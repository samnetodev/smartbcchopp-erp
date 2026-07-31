import uuid

from sqlalchemy import DECIMAL, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base


class TabelaPrecoModel(Base):
    __tablename__ = "tabela_preco"

    nome: Mapped[str] = mapped_column(String(100), nullable=False)

    itens = relationship(
        "ItemTabelaPrecoModel", back_populates="tabela", cascade="all, delete-orphan"
    )


class ItemTabelaPrecoModel(Base):
    __tablename__ = "item_tabela_preco"

    preco: Mapped[float] = mapped_column(DECIMAL(12, 2), nullable=False)

    tabela_preco_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tabela_preco.id"), nullable=False
    )
    produto_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("produto.id"), nullable=False
    )

    tabela = relationship("TabelaPrecoModel", back_populates="itens")
    produto = relationship("ProdutoModel")

    __table_args__ = (UniqueConstraint("tabela_preco_id", "produto_id", name="uq_tabela_produto"),)
