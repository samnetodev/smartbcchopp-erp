import uuid
from datetime import date

from sqlalchemy import DECIMAL, Date, Enum, ForeignKey, SmallInteger, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base
from database.models.conta_receber import ContaStatus as ContaStatus


class ContaPagarModel(Base):
    __tablename__ = "conta_pagar"

    parcela: Mapped[int] = mapped_column(SmallInteger, default=1)
    numero_documento: Mapped[str] = mapped_column(String(50), nullable=False)
    data_emissao: Mapped[date] = mapped_column(Date, nullable=False)
    data_vencimento: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    data_pagamento: Mapped[date | None] = mapped_column(Date)
    valor_original: Mapped[float] = mapped_column(DECIMAL(12, 2), nullable=False)
    valor_pago: Mapped[float] = mapped_column(DECIMAL(12, 2), default=0)
    desconto: Mapped[float] = mapped_column(DECIMAL(10, 2), default=0)
    juros: Mapped[float] = mapped_column(DECIMAL(10, 2), default=0)
    multa: Mapped[float] = mapped_column(DECIMAL(10, 2), default=0)
    categoria: Mapped[str | None] = mapped_column(String(50), index=True)
    status: Mapped[ContaStatus] = mapped_column(
        Enum(ContaStatus, values_callable=lambda x: [e.value for e in x]),
        default=ContaStatus.ABERTO, nullable=False, index=True
    )

    fornecedor_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fornecedor.id")
    )
    pedido_compra_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pedido_compra.id")
    )

    fornecedor = relationship("FornecedorModel")
    pedido_compra = relationship("PedidoCompraModel")
