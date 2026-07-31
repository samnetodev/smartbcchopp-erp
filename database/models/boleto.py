import enum
import uuid
from datetime import date

from sqlalchemy import Date, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base


class BoletoStatus(str, enum.Enum):  # noqa: UP042
    GERADO = "gerado"
    REGISTRADO = "registrado"
    VENCIDO = "vencido"
    PAGO = "pago"
    CANCELADO = "cancelado"


class BoletoModel(Base):
    __tablename__ = "boleto"

    nosso_numero: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    linha_digitavel: Mapped[str | None] = mapped_column(String(100))
    codigo_barras: Mapped[str | None] = mapped_column(String(60))
    qr_code: Mapped[str | None] = mapped_column(Text)
    data_emissao: Mapped[date] = mapped_column(Date, nullable=False)
    data_vencimento: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    data_pagamento: Mapped[date | None] = mapped_column(Date)
    valor_nominal: Mapped[float] = mapped_column(nullable=False)
    valor_pago: Mapped[float | None] = mapped_column()
    status: Mapped[BoletoStatus] = mapped_column(
        Enum(BoletoStatus, values_callable=lambda x: [e.value for e in x]),
        default=BoletoStatus.GERADO, nullable=False, index=True
    )
    arquivo_pdf: Mapped[str | None] = mapped_column(String(500))
    arquivo_remessa: Mapped[str | None] = mapped_column(String(500))
    observacao: Mapped[str | None] = mapped_column(Text)

    conta_receber_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("conta_receber.id"), nullable=False, index=True
    )

    conta_receber = relationship("ContaReceberModel")
