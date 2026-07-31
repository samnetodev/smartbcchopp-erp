import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base


class PixStatus(str, enum.Enum):  # noqa: UP042
    ATIVO = "ativo"
    CONCLUIDO = "concluido"
    EXPIRADO = "expirado"
    CANCELADO = "cancelado"


class PixCobrancaModel(Base):
    __tablename__ = "pix_cobranca"

    txid: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    charge_id: Mapped[str | None] = mapped_column(String(100))
    payload_base64: Mapped[str | None] = mapped_column(Text)
    qr_code_url: Mapped[str | None] = mapped_column(String(500))
    pix_copia_cola: Mapped[str | None] = mapped_column(Text)
    valor: Mapped[float] = mapped_column(nullable=False)
    status: Mapped[PixStatus] = mapped_column(
        Enum(PixStatus, values_callable=lambda x: [e.value for e in x]),
        default=PixStatus.ATIVO, nullable=False, index=True
    )
    data_expiracao: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    data_pagamento: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    end_to_end_id: Mapped[str | None] = mapped_column(String(50))
    observacao: Mapped[str | None] = mapped_column(Text)

    conta_receber_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("conta_receber.id"), nullable=False, index=True
    )

    conta_receber = relationship("ContaReceberModel")
