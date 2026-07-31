from decimal import Decimal

from core.domain.entities.order import Order, OrderItem
from core.shared.domain_event import DomainEvent


class OrderAggregate:
    def __init__(self, order: Order) -> None:
        self.order = order
        self._events: list[DomainEvent] = []

    def add_item(self, item: OrderItem) -> None:
        self.order.items.append(item)
        self._recalculate_totals()

    def remove_item(self, produto_id: str) -> None:
        self.order.items = [i for i in self.order.items if str(i.produto_id) != produto_id]
        self._recalculate_totals()

    def _recalculate_totals(self) -> None:
        self.order.subtotal = sum(
            (
                (i.quantidade * i.preco_unitario) - i.desconto_percentual
                for i in self.order.items
            ),
            start=Decimal("0"),
        )
        self.order.total = self.order.subtotal - self.order.desconto + self.order.frete

    @property
    def events(self) -> list[DomainEvent]:
        return self._events
