import enum
import uuid
from datetime import date

from sqlalchemy import Date, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base
from database.models.conta_receber import FormaPagamento


class BaixaTipo(str, enum.Enum):  # noqa: UP042
    RECEBIMENTO = "recebimento"
    PAGAMENTO = "pagamento"


class BaixaModel(Base):
    __tablename__ = "financeiro_baixa"

    tipo: Mapped[BaixaTipo] = mapped_column(
        Enum(BaixaTipo, values_callable=lambda x: [e.value for e in x]),
        nullable=False, index=True
    )
    data_baixa: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    valor: Mapped[float] = mapped_column(nullable=False)
    forma_pagamento: Mapped[FormaPagamento | None] = mapped_column(
        Enum(FormaPagamento, values_callable=lambda x: [e.value for e in x]),
    )
    observacao: Mapped[str | None] = mapped_column(String(200))

    conta_receber_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("conta_receber.id"), index=True
    )
    conta_pagar_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("conta_pagar.id"), index=True
    )

    conta_receber = relationship("ContaReceberModel")
    conta_pagar = relationship("ContaPagarModel")
