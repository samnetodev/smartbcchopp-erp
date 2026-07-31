import enum
import uuid
from datetime import datetime

from sqlalchemy import DECIMAL, Boolean, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base


class TipoCombustivel(str, enum.Enum):  # noqa: UP042
    DIESEL_S10 = "diesel_s10"
    DIESEL_S500 = "diesel_s500"
    GASOLINA_ADITIVADA = "gasolina_aditivada"
    GASOLINA_COMUM = "gasolina_comum"
    ETANOL = "etanol"
    GNV = "gnv"


class AbastecimentoModel(Base):
    __tablename__ = "abastecimento"

    data: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.now, index=True
    )
    km_atual: Mapped[int] = mapped_column(Integer, nullable=False)
    tipo_combustivel: Mapped[TipoCombustivel] = mapped_column(
        Enum(TipoCombustivel, values_callable=lambda x: [e.value for e in x]),
        nullable=False
    )
    litros: Mapped[float] = mapped_column(DECIMAL(8, 3), nullable=False)
    valor_litro: Mapped[float] = mapped_column(DECIMAL(8, 4), nullable=False)
    valor_total: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    posto_nome: Mapped[str | None] = mapped_column(String(100))
    posto_cnpj: Mapped[str | None] = mapped_column(String(14))
    completo: Mapped[bool] = mapped_column(Boolean, default=True)
    nota_fiscal: Mapped[str | None] = mapped_column(String(50))

    veiculo_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("veiculo.id"), nullable=False, index=True
    )
    motorista_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("motorista.id")
    )

    veiculo = relationship("VeiculoModel")
    motorista = relationship("MotoristaModel")
