import uuid
from datetime import date

from sqlalchemy import DECIMAL, Date, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base


class LoteModel(Base):
    __tablename__ = "lote"

    codigo_lote: Mapped[str] = mapped_column(String(50), nullable=False)
    data_fabricacao: Mapped[date | None] = mapped_column(Date)
    data_validade: Mapped[date] = mapped_column(Date, nullable=False)
    quantidade_inicial: Mapped[float] = mapped_column(DECIMAL(10, 3), nullable=False)

    produto_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("produto.id"), nullable=False
    )

    produto = relationship("ProdutoModel")
