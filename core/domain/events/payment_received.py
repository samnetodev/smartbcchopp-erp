from dataclasses import dataclass
from uuid import UUID

from core.shared.domain_event import DomainEvent


@dataclass(frozen=True, kw_only=True)
class PaymentReceived(DomainEvent):
    conta_receber_id: UUID
    order_id: UUID
    valor_pago: float
