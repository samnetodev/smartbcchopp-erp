from sqlalchemy import DECIMAL, Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from database.models.base import Base


class CondicaoPagamentoModel(Base):
    __tablename__ = "condicao_pagamento"

    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    numero_parcelas: Mapped[int] = mapped_column(Integer, nullable=False)
    intervalo_dias: Mapped[int] = mapped_column(Integer, nullable=False)
    entrada_percentual: Mapped[float] = mapped_column(DECIMAL(5, 2), default=0)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
