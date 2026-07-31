from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_session
from api.middlewares.auth import requer_permissao
from api.serializers.customer_schema import (
    CustomerCreate,
    CustomerListResponse,
    CustomerResponse,
    CustomerUpdate,
)
from core.domain.auth.papeis import Acao, Modulo
from database.repositories.cliente_repository_impl import ClienteRepositoryImpl
from database.unit_of_work import AsyncUnitOfWork

router = APIRouter()


@router.get("/", response_model=CustomerListResponse)
async def list_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: str | None = None,
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.CLIENTES, Acao.LER)),
) -> CustomerListResponse:
    repo = ClienteRepositoryImpl(session)

    if search:
        items = await repo.search(search, skip=skip, limit=limit)
    else:
        items = await repo.find_all_active(skip=skip, limit=limit)

    total = await repo.count_active()

    return CustomerListResponse(
        items=[CustomerResponse.model_validate(c) for c in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: UUID,
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.CLIENTES, Acao.LER)),
) -> CustomerResponse:
    repo = ClienteRepositoryImpl(session)
    customer = await repo.find_by_id(customer_id)
    if not customer or customer.deleted_at:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return CustomerResponse.model_validate(customer)


@router.post("/", response_model=CustomerResponse, status_code=201)
async def create_customer(
    body: CustomerCreate,
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.CLIENTES, Acao.CRIAR)),
) -> CustomerResponse:
    repo = ClienteRepositoryImpl(session)

    existing = await repo.find_by_cpf_cnpj(body.cpf_cnpj)
    if existing:
        raise HTTPException(status_code=400, detail="CPF/CNPJ já cadastrado")

    from database.models.cliente import ClienteModel

    customer = ClienteModel(
        tipo_pessoa=body.tipo_pessoa,
        nome_razao_social=body.nome_razao_social,
        nome_fantasia=body.nome_fantasia,
        cpf_cnpj=body.cpf_cnpj,
        rg_ie=body.rg_ie,
        email=body.email,
        telefone=body.telefone,
        celular=body.celular,
        limite_credito=float(body.limite_credito),
    )

    await repo.save(customer)
    uow = AsyncUnitOfWork(session)
    await uow.commit()

    return CustomerResponse.model_validate(customer)


@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: UUID,
    body: CustomerUpdate,
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.CLIENTES, Acao.ATUALIZAR)),
) -> CustomerResponse:
    repo = ClienteRepositoryImpl(session)
    customer = await repo.find_by_id(customer_id)
    if not customer or customer.deleted_at:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            if field == "limite_credito":
                value = float(value)
            setattr(customer, field, value)

    uow = AsyncUnitOfWork(session)
    await uow.commit()

    return CustomerResponse.model_validate(customer)


@router.delete("/{customer_id}", status_code=204)
async def delete_customer(
    customer_id: UUID,
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.CLIENTES, Acao.DELETAR)),
) -> None:
    repo = ClienteRepositoryImpl(session)
    customer = await repo.find_by_id(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    customer.deleted_at = datetime.now(timezone.utc)
    uow = AsyncUnitOfWork(session)
    await uow.commit()
