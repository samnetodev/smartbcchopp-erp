from dataclasses import dataclass
from uuid import UUID

from core.shared.domain_event import DomainEvent


@dataclass(frozen=True, kw_only=True)
class OrderPlaced(DomainEvent):
    order_id: UUID
    customer_id: UUID
    total: float
