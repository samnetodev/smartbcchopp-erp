from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Any
from uuid import UUID

from core.shared.base_entity import BaseEntity


@dataclass
class OrderItem:
    produto_id: UUID
    quantidade: Decimal
    preco_unitario: Decimal
    desconto_percentual: Decimal = Decimal("0")


class Order(BaseEntity):
    def __init__(
        self,
        numero: str,
        cliente_id: UUID,
        status: str = "rascunho",
        items: list[OrderItem] | None = None,
        subtotal: Decimal = Decimal("0"),
        desconto: Decimal = Decimal("0"),
        frete: Decimal = Decimal("0"),
        total: Decimal = Decimal("0"),
        data_entrega_prevista: date | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.numero = numero
        self.cliente_id = cliente_id
        self.status = status
        self.items = items or []
        self.subtotal = subtotal
        self.desconto = desconto
        self.frete = frete
        self.total = total
        self.data_entrega_prevista = data_entrega_prevista
