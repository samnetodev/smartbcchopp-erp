from dataclasses import dataclass
from uuid import UUID

from core.shared.domain_event import DomainEvent


@dataclass(frozen=True, kw_only=True)
class WhatsappMessageReceived(DomainEvent):
    conversa_id: UUID
    telefone: str
    mensagem: str
    mensagem_id: UUID
