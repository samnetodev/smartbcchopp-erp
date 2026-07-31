from sqlalchemy import DECIMAL, String
from sqlalchemy.orm import Mapped, mapped_column

from database.models.base import Base


class EnderecoModel(Base):
    __tablename__ = "endereco"

    logradouro: Mapped[str] = mapped_column(String(200), nullable=False)
    numero: Mapped[str] = mapped_column(String(20), nullable=False)
    complemento: Mapped[str | None] = mapped_column(String(100))
    bairro: Mapped[str] = mapped_column(String(100), nullable=False)
    cidade: Mapped[str] = mapped_column(String(100), nullable=False)
    estado: Mapped[str] = mapped_column(String(2), nullable=False)
    cep: Mapped[str] = mapped_column(String(8), nullable=False, index=True)
    latitude: Mapped[float | None] = mapped_column(DECIMAL(10, 7))
    longitude: Mapped[float | None] = mapped_column(DECIMAL(10, 7))
