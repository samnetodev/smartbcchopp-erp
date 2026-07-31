import enum
import uuid
from datetime import date

from sqlalchemy import DECIMAL, Date, Enum, ForeignKey, SmallInteger, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base


class ContaStatus(str, enum.Enum):  # noqa: UP042
    ABERTO = "aberto"
    PARCIAL = "parcial"
    PAGO = "pago"
    ATRASADO = "atrasado"
    CANCELADO = "cancelado"


class FormaPagamento(str, enum.Enum):  # noqa: UP042
    BOLETO = "boleto"
    PIX = "pix"
    CREDITO = "credito"
    DEBITO = "debito"
    DINHEIRO = "dinheiro"
    CHEQUE = "cheque"


class ContaReceberModel(Base):
    __tablename__ = "conta_receber"

    parcela: Mapped[int] = mapped_column(SmallInteger, default=1, nullable=False)
    numero_documento: Mapped[str] = mapped_column(String(50), nullable=False)
    data_emissao: Mapped[date] = mapped_column(Date, nullable=False)
    data_vencimento: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    data_pagamento: Mapped[date | None] = mapped_column(Date)
    valor_original: Mapped[float] = mapped_column(DECIMAL(12, 2), nullable=False)
    valor_pago: Mapped[float] = mapped_column(DECIMAL(12, 2), default=0)
    desconto: Mapped[float] = mapped_column(DECIMAL(10, 2), default=0)
    juros: Mapped[float] = mapped_column(DECIMAL(10, 2), default=0)
    multa: Mapped[float] = mapped_column(DECIMAL(10, 2), default=0)
    status: Mapped[ContaStatus] = mapped_column(
        Enum(ContaStatus, values_callable=lambda x: [e.value for e in x]),
        default=ContaStatus.ABERTO, nullable=False, index=True
    )
    forma_pagamento: Mapped[FormaPagamento | None] = mapped_column(
        Enum(FormaPagamento, values_callable=lambda x: [e.value for e in x]),
    )
    nosso_numero: Mapped[str | None] = mapped_column(String(50))
    pix_charge_id: Mapped[str | None] = mapped_column(String(100))

    pedido_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("pedido.id"))
    cliente_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cliente.id"), nullable=False, index=True
    )

    pedido = relationship("PedidoModel")
    cliente = relationship("ClienteModel")
