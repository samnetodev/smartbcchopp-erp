from uuid import UUID

from core.shared.result import Failure, Success
from database.models.pedido import PedidoModel, PedidoStatus
from database.repositories.pedido_repository_impl import PedidoRepositoryImpl
from database.unit_of_work import AsyncUnitOfWork


class ApproveOrderUseCase:
    def __init__(self, uow: AsyncUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, order_id: UUID) -> Success[PedidoModel] | Failure[str]:
        repo = PedidoRepositoryImpl(self._uow.session)
        order = await repo.find_by_id(order_id)

        if not order:
            return Failure("Pedido não encontrado")

        if order.status != PedidoStatus.AGUARDANDO_APROVACAO:
            return Failure(f"Status inválido para aprovação: {order.status}")

        order.status = PedidoStatus.APROVADO
        await self._uow.commit()

        return Success(order)


class CancelOrderUseCase:
    def __init__(self, uow: AsyncUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, order_id: UUID) -> Success[PedidoModel] | Failure[str]:
        repo = PedidoRepositoryImpl(self._uow.session)
        order = await repo.find_by_id(order_id)

        if not order:
            return Failure("Pedido não encontrado")

        if order.status in (PedidoStatus.ENTREGUE, PedidoStatus.CANCELADO):
            return Failure(f"Não é possível cancelar pedido {order.status}")

        order.status = PedidoStatus.CANCELADO
        await self._uow.commit()

        return Success(order)
