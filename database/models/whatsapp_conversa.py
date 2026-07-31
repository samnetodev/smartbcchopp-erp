import enum
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Boolean, DateTime, Enum, ForeignKey, String, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base


class WhatsappConversaStatus(str, enum.Enum):
    ATIVA = "ativa"
    PENDENTE = "pendente"
    ENCERRADA = "encerrada"


class WhatsappMensagemModel(Base):
    __tablename__ = "whatsapp_mensagem"

    remetente: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    conteudo: Mapped[str] = mapped_column(Text, nullable=False)
    tipo: Mapped[str] = mapped_column(String(20), nullable=False, default="texto")
    direcao: Mapped[str] = mapped_column(String(10), nullable=False)
    lida: Mapped[bool] = mapped_column(Boolean, default=False)
    data_recebida: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )
    meta_dados: Mapped[dict[str, Any] | None] = mapped_column(JSON)

    conversa_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("whatsapp_conversa.id"), nullable=False, index=True
    )

    conversa = relationship("WhatsappConversaModel", back_populates="mensagens")


class WhatsappConversaModel(Base):
    __tablename__ = "whatsapp_conversa"

    telefone: Mapped[str] = mapped_column(String(20), nullable=False, unique=True, index=True)
    nome_contato: Mapped[str | None] = mapped_column(String(200))
    status: Mapped[WhatsappConversaStatus] = mapped_column(
        Enum(WhatsappConversaStatus, values_callable=lambda x: [e.value for e in x]),
        default=WhatsappConversaStatus.ATIVA, nullable=False
    )
    ultima_mensagem: Mapped[str | None] = mapped_column(Text)
    ultima_data: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))
    contexto: Mapped[dict[str, Any] | None] = mapped_column(JSON, default=dict)
    agente_ativo: Mapped[str | None] = mapped_column(String(30))
    cliente_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cliente.id")
    )
    pedido_ctx: Mapped[dict[str, Any] | None] = mapped_column(JSON, default=dict)

    cliente = relationship("ClienteModel")
    mensagens = relationship(
        "WhatsappMensagemModel", back_populates="conversa", cascade="all, delete-orphan",
        order_by="WhatsappMensagemModel.data_recebida",
    )
