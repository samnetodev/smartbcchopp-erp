from dataclasses import dataclass

from database.models.pedido import ItemPedidoModel, PedidoModel, PedidoStatus
from database.repositories.cliente_repository_impl import ClienteRepositoryImpl
from database.repositories.pedido_repository_impl import PedidoRepositoryImpl
from database.repositories.produto_repository_impl import ProdutoRepositoryImpl
from database.unit_of_work import AsyncUnitOfWork


@dataclass
class OrderItemInput:
    produto_id: str
    quantidade: float
    preco_unitario: float
    desconto_percentual: float = 0


@dataclass
class CreateOrderInput:
    cliente_id: str
    items: list[OrderItemInput]
    data_entrega_prevista: str | None = None
    condicao_pagamento_id: str | None = None
    observacao: str | None = None


class CreateOrderUseCase:
    def __init__(self, uow: AsyncUnitOfWork) -> None:
        self._uow = uow

    async def execute(self, input_data: CreateOrderInput) -> PedidoModel:
        from uuid import UUID

        pedido_repo = PedidoRepositoryImpl(self._uow.session)
        cliente_repo = ClienteRepositoryImpl(self._uow.session)
        produto_repo = ProdutoRepositoryImpl(self._uow.session)

        cliente = await cliente_repo.find_by_id(UUID(input_data.cliente_id))
        if not cliente:
            raise ValueError("Cliente não encontrado")

        if not input_data.items:
            raise ValueError("Pedido deve ter pelo menos 1 item")

        numero = await pedido_repo.next_numero()

        order = PedidoModel(
            numero=numero,
            cliente_id=UUID(input_data.cliente_id),
            status=PedidoStatus.RASCUNHO,
            observacao=input_data.observacao,
        )

        subtotal = 0.0
        for i, item in enumerate(input_data.items):
            produto = await produto_repo.find_by_id(UUID(item.produto_id))
            if not produto:
                raise ValueError(f"Produto {item.produto_id} não encontrado")

            item_subtotal = item.quantidade * item.preco_unitario
            item_desconto_valor = item_subtotal * (item.desconto_percentual / 100)
            item_total = item_subtotal - item_desconto_valor

            order_item = ItemPedidoModel(
                quantidade=item.quantidade,
                preco_unitario=item.preco_unitario,
                desconto_percentual=item.desconto_percentual,
                desconto_valor=item_desconto_valor,
                subtotal=item_total,
                ordem=i + 1,
                produto_id=UUID(item.produto_id),
            )
            order.itens.append(order_item)
            subtotal += item_total

        order.subtotal = subtotal
        order.total = subtotal

        await pedido_repo.save(order)
        await self._uow.commit()

        return order
