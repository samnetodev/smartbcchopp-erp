import uuid

from sqlalchemy import DECIMAL, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base


class EstoqueModel(Base):
    __tablename__ = "estoque"

    quantidade_atual: Mapped[float] = mapped_column(DECIMAL(10, 3), default=0, nullable=False)
    quantidade_reservada: Mapped[float] = mapped_column(DECIMAL(10, 3), default=0, nullable=False)
    localizacao: Mapped[str | None] = mapped_column(String(50))
    versao: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    produto_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("produto.id"), nullable=False, index=True
    )
    deposito_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("deposito.id"), nullable=False, index=True
    )
    lote_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("lote.id"))

    produto = relationship("ProdutoModel")
    deposito = relationship("DepositoModel")
    lote = relationship("LoteModel")

    __table_args__ = (
        UniqueConstraint(
            "produto_id",
            "deposito_id",
            "lote_id",
            name="uq_estoque_produto_deposito_lote",
        ),
        {"extend_existing": True},
    )
