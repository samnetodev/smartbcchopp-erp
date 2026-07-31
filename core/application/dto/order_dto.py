from dataclasses import dataclass
from typing import Any
from uuid import UUID


@dataclass
class CreateOrderDTO:
    cliente_id: UUID
    items: list[dict[str, Any]]
    data_entrega_prevista: str | None = None


@dataclass
class OrderResponseDTO:
    id: UUID
    numero: str
    cliente_id: UUID
    status: str
    total: float
