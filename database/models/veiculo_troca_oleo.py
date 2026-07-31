import uuid
from datetime import date

from sqlalchemy import DECIMAL, Date, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base


class TrocaOleoModel(Base):
    __tablename__ = "veiculo_troca_oleo"

    data: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    km_atual: Mapped[int] = mapped_column(Integer, nullable=False)
    tipo_oleo: Mapped[str] = mapped_column(String(50), nullable=False)
    quantidade_l: Mapped[float] = mapped_column(DECIMAL(6, 2), nullable=False)
    valor_oleo: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    valor_filtro: Mapped[float] = mapped_column(DECIMAL(10, 2), default=0)
    valor_servico: Mapped[float] = mapped_column(DECIMAL(10, 2), default=0)
    valor_total: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    oficina_nome: Mapped[str | None] = mapped_column(String(100))
    km_proxima_troca: Mapped[int | None] = mapped_column(Integer)
    observacao: Mapped[str | None] = mapped_column(Text)

    veiculo_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("veiculo.id"), nullable=False, index=True
    )

    veiculo = relationship("VeiculoModel", back_populates="trocas_oleo")
