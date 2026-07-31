from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_session
from api.middlewares.auth import requer_permissao
from api.serializers.supplier_schema import (
    SupplierCreate,
    SupplierListResponse,
    SupplierResponse,
    SupplierUpdate,
)
from core.domain.auth.papeis import Acao, Modulo
from database.models.fornecedor import FornecedorCategoria, FornecedorModel, FornecedorStatus
from database.repositories.fornecedor_repository_impl import FornecedorRepositoryImpl
from database.unit_of_work import AsyncUnitOfWork

router = APIRouter()


@router.get("/", response_model=SupplierListResponse)
async def list_suppliers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    categoria: str | None = None,
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.FORNECEDORES, Acao.LER)),
) -> SupplierListResponse:
    repo = FornecedorRepositoryImpl(session)

    if categoria:
        items = await repo.find_by_categoria(categoria)
        total = len(items)
    else:
        items = await repo.find_all(skip=skip, limit=limit)
        total = await repo.count()

    return SupplierListResponse(
        items=[SupplierResponse.model_validate(f) for f in items],
        total=total,
    )


@router.get("/{supplier_id}", response_model=SupplierResponse)
async def get_supplier(
    supplier_id: UUID,
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.FORNECEDORES, Acao.LER)),
) -> SupplierResponse:
    repo = FornecedorRepositoryImpl(session)
    supplier = await repo.find_by_id(supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado")
    return SupplierResponse.model_validate(supplier)


@router.post("/", response_model=SupplierResponse, status_code=201)
async def create_supplier(
    body: SupplierCreate,
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.FORNECEDORES, Acao.CRIAR)),
) -> SupplierResponse:
    repo = FornecedorRepositoryImpl(session)

    existing = await repo.find_by_cpf_cnpj(body.cpf_cnpj)
    if existing:
        raise HTTPException(status_code=400, detail="CPF/CNPJ já cadastrado")

    supplier = FornecedorModel(
        tipo_pessoa=body.tipo_pessoa,
        nome_razao_social=body.nome_razao_social,
        nome_fantasia=body.nome_fantasia,
        cpf_cnpj=body.cpf_cnpj,
        inscricao_estadual=body.inscricao_estadual,
        email=body.email,
        telefone=body.telefone,
        contato_nome=body.contato_nome,
        categoria=FornecedorCategoria(body.categoria),
    )

    await repo.save(supplier)
    uow = AsyncUnitOfWork(session)
    await uow.commit()

    return SupplierResponse.model_validate(supplier)


@router.put("/{supplier_id}", response_model=SupplierResponse)
async def update_supplier(
    supplier_id: UUID,
    body: SupplierUpdate,
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.FORNECEDORES, Acao.ATUALIZAR)),
) -> SupplierResponse:
    repo = FornecedorRepositoryImpl(session)
    supplier = await repo.find_by_id(supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado")

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            if field == "status":
                value = FornecedorStatus(value)
            setattr(supplier, field, value)

    uow = AsyncUnitOfWork(session)
    await uow.commit()

    return SupplierResponse.model_validate(supplier)


@router.delete("/{supplier_id}", status_code=204)
async def delete_supplier(
    supplier_id: UUID,
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.FORNECEDORES, Acao.DELETAR)),
) -> None:
    repo = FornecedorRepositoryImpl(session)
    supplier = await repo.find_by_id(supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado")

    supplier.status = FornecedorStatus.INATIVO
    uow = AsyncUnitOfWork(session)
    await uow.commit()
