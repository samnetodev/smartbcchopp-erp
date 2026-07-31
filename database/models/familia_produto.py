from sqlalchemy import DECIMAL, Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from database.models.base import Base


class FamiliaProdutoModel(Base):
    __tablename__ = "familia_produto"

    codigo: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    margem_padrao: Mapped[float | None] = mapped_column(DECIMAL(5, 2))
    ativa: Mapped[bool] = mapped_column(Boolean, default=True)
