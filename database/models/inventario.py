import enum
import uuid
from datetime import date as date_type

from sqlalchemy import DECIMAL, Date, Enum, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base


class InventarioStatus(str, enum.Enum):  # noqa: UP042
    ABERTO = "aberto"
    FECHADO = "fechado"


class InventarioModel(Base):
    __tablename__ = "inventario"

    status: Mapped[InventarioStatus] = mapped_column(
        Enum(InventarioStatus, values_callable=lambda x: [e.value for e in x]),
        nullable=False, default=InventarioStatus.ABERTO, index=True
    )
    data_contagem: Mapped[date_type] = mapped_column(
        Date, nullable=False, server_default=func.current_date()
    )
    quantidade_sistema: Mapped[float] = mapped_column(DECIMAL(10, 3), nullable=False)
    quantidade_contada: Mapped[float] = mapped_column(DECIMAL(10, 3), nullable=False)
    diferenca: Mapped[float] = mapped_column(DECIMAL(10, 3), nullable=False, default=0)
    observacao: Mapped[str | None] = mapped_column(Text)

    produto_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("produto.id"), nullable=False, index=True
    )
    deposito_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("deposito.id"), nullable=False, index=True
    )
    lote_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("lote.id"))
    usuario_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuario.id")
    )

    produto = relationship("ProdutoModel")
    deposito = relationship("DepositoModel")
