from decimal import Decimal
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_session
from api.middlewares.auth import requer_permissao
from api.serializers.product_schema import (
    ProductCreate,
    ProductListResponse,
    ProductResponse,
    ProductUpdate,
)
from core.domain.auth.papeis import Acao, Modulo
from database.repositories.produto_repository_impl import ProdutoRepositoryImpl
from database.unit_of_work import AsyncUnitOfWork

router = APIRouter()


@router.get("/", response_model=ProductListResponse)
async def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    categoria: str | None = None,
    search: str | None = None,
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.PRODUTOS, Acao.LER)),
) -> ProductListResponse:
    repo = ProdutoRepositoryImpl(session)

    if search:
        items = await repo.search(search, skip=skip, limit=limit)
    elif categoria:
        items = await repo.find_by_categoria(categoria, skip=skip, limit=limit)
    else:
        items = await repo.find_all(skip=skip, limit=limit)

    total = await repo.count()

    return ProductListResponse(
        items=[ProductResponse.model_validate(p) for p in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: UUID,
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.PRODUTOS, Acao.LER)),
) -> ProductResponse:
    repo = ProdutoRepositoryImpl(session)
    product = await repo.find_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return ProductResponse.model_validate(product)


@router.post("/", response_model=ProductResponse, status_code=201)
async def create_product(
    body: ProductCreate,
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.PRODUTOS, Acao.CRIAR)),
) -> ProductResponse:
    repo = ProdutoRepositoryImpl(session)

    existing = await repo.find_by_codigo(body.codigo)
    if existing:
        raise HTTPException(status_code=400, detail=f"Produto com código '{body.codigo}' já existe")

    if body.codigo_barras:
        existing_barcode = await repo.find_by_codigo_barras(body.codigo_barras)
        if existing_barcode:
            msg = f"Código de barras '{body.codigo_barras}' já cadastrado"
            raise HTTPException(status_code=400, detail=msg)

    from database.models.produto import ProdutoModel

    product = ProdutoModel(
        codigo=body.codigo,
        nome=body.nome,
        categoria=body.categoria,
        unidade_medida=body.unidade_medida,
        preco_venda=float(body.preco_venda),
        preco_custo=float(body.preco_custo) if body.preco_custo else 0,
        familia_id=body.familia_id,
        ncm=body.ncm,
        codigo_barras=body.codigo_barras,
        estoque_minimo=float(body.estoque_minimo),
        lote_obrigatorio=body.lote_obrigatorio,
    )

    await repo.save(product)
    uow = AsyncUnitOfWork(session)
    await uow.commit()

    return ProductResponse.model_validate(product)


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: UUID,
    body: ProductUpdate,
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.PRODUTOS, Acao.ATUALIZAR)),
) -> ProductResponse:
    repo = ProdutoRepositoryImpl(session)
    product = await repo.find_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(product, field, float(value) if isinstance(value, Decimal) else value)

    uow = AsyncUnitOfWork(session)
    await uow.commit()

    return ProductResponse.model_validate(product)


@router.delete("/{product_id}", status_code=204)
async def delete_product(
    product_id: UUID,
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.PRODUTOS, Acao.DELETAR)),
) -> None:
    repo = ProdutoRepositoryImpl(session)
    product = await repo.find_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    product.ativo = False
    uow = AsyncUnitOfWork(session)
    await uow.commit()
