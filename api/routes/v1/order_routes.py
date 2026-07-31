from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_session
from api.middlewares.auth import requer_permissao
from api.serializers.order_schema import (
    OrderCreate,
    OrderListResponse,
    OrderResponse,
    OrderUpdateStatus,
)
from core.application.use_cases.order.approve_order_usecase import (
    ApproveOrderUseCase,
    CancelOrderUseCase,
)
from core.application.use_cases.order.create_order_usecase import (
    CreateOrderInput,
    CreateOrderUseCase,
    OrderItemInput,
)
from core.domain.auth.papeis import Acao, Modulo
from core.shared.result import Failure
from database.models.pedido import PedidoStatus
from database.repositories.pedido_repository_impl import PedidoRepositoryImpl
from database.unit_of_work import AsyncUnitOfWork

router = APIRouter()


@router.get("/", response_model=OrderListResponse)
async def list_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: str | None = None,
    cliente_id: UUID | None = None,
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.PEDIDOS, Acao.LER)),
) -> OrderListResponse:
    repo = PedidoRepositoryImpl(session)

    if status:
        items = await repo.find_by_status(status, skip=skip, limit=limit)
        total = await repo.count_by_status(status)
    elif cliente_id:
        items = await repo.find_by_cliente(cliente_id, skip=skip, limit=limit)
        total = len(items)
    else:
        items = await repo.find_all(skip=skip, limit=limit)
        total = await repo.count()

    return OrderListResponse(
        items=[OrderResponse.model_validate(o) for o in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: UUID,
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.PEDIDOS, Acao.LER)),
) -> OrderResponse:
    repo = PedidoRepositoryImpl(session)
    order = await repo.find_by_id_with_items(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    return OrderResponse.model_validate(order)


@router.post("/", response_model=OrderResponse, status_code=201)
async def create_order(
    body: OrderCreate,
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.PEDIDOS, Acao.CRIAR)),
) -> OrderResponse:
    uow = AsyncUnitOfWork(session)
    use_case = CreateOrderUseCase(uow)

    try:
        order = await use_case.execute(
            CreateOrderInput(
                cliente_id=str(body.cliente_id),
                items=[
                    OrderItemInput(
                        produto_id=str(i.produto_id),
                        quantidade=float(i.quantidade),
                        preco_unitario=float(i.preco_unitario),
                        desconto_percentual=float(i.desconto_percentual),
                    )
                    for i in body.items
                ],
                condicao_pagamento_id=(
                    str(body.condicao_pagamento_id) if body.condicao_pagamento_id else None
                ),
                observacao=body.observacao,
            )
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return OrderResponse.model_validate(order)


@router.patch("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: UUID,
    body: OrderUpdateStatus,
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.PEDIDOS, Acao.ATUALIZAR)),
) -> OrderResponse:
    repo = PedidoRepositoryImpl(session)
    order = await repo.find_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    order.status = PedidoStatus(body.status)
    uow = AsyncUnitOfWork(session)
    await uow.commit()

    return OrderResponse.model_validate(order)


@router.post("/{order_id}/submit")
async def submit_order(
    order_id: UUID,
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.PEDIDOS, Acao.ATUALIZAR)),
) -> dict[str, Any]:
    repo = PedidoRepositoryImpl(session)
    order = await repo.find_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    status_val = order.status.value if hasattr(order.status, "value") else order.status
    if status_val != "rascunho":
        raise HTTPException(status_code=400, detail=f"Status inválido: {status_val}")

    order.status = PedidoStatus.AGUARDANDO_APROVACAO
    uow = AsyncUnitOfWork(session)
    await uow.commit()

    return {"message": "Pedido enviado para aprovação", "order_id": str(order_id)}


@router.post("/{order_id}/approve")
async def approve_order(
    order_id: UUID,
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.PEDIDOS, Acao.APROVAR)),
) -> dict[str, Any]:
    uow = AsyncUnitOfWork(session)
    use_case = ApproveOrderUseCase(uow)

    result = await use_case.execute(order_id)
    if isinstance(result, Failure):
        raise HTTPException(status_code=400, detail=result.error)

    return {"message": "Pedido aprovado", "order_id": str(order_id)}


@router.post("/{order_id}/cancel")
async def cancel_order(
    order_id: UUID,
    session: AsyncSession = Depends(get_session),
    _: dict[str, Any] = Depends(requer_permissao(Modulo.PEDIDOS, Acao.CANCELAR)),
) -> dict[str, Any]:
    uow = AsyncUnitOfWork(session)
    use_case = CancelOrderUseCase(uow)

    result = await use_case.execute(order_id)
    if isinstance(result, Failure):
        raise HTTPException(status_code=400, detail=result.error)

    return {"message": "Pedido cancelado", "order_id": str(order_id)}
