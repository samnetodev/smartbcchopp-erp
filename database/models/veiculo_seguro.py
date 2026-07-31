import enum
import uuid
from datetime import date

from sqlalchemy import DECIMAL, Boolean, Date, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base


class SeguroSeguradora(str, enum.Enum):  # noqa: UP042
    PORTO_SEGURO = "porto_seguro"
    SULAMERICA = "sulamerica"
    ALLIANZ = "allianz"
    MAPFRE = "mapfre"
    TOKIO_MARINE = "tokio_marine"
    LIBERTY = "liberty"
    HDI = "hdi"
    OUTRA = "outra"


class SeguroStatus(str, enum.Enum):  # noqa: UP042
    ATIVO = "ativo"
    VENCIDO = "vencido"
    CANCELADO = "cancelado"


class SeguroModel(Base):
    __tablename__ = "veiculo_seguro"

    apolice: Mapped[str] = mapped_column(String(30), nullable=False)
    seguradora: Mapped[SeguroSeguradora] = mapped_column(
        Enum(SeguroSeguradora, values_callable=lambda x: [e.value for e in x]),
        nullable=False
    )
    data_inicio_vigencia: Mapped[date] = mapped_column(Date, nullable=False)
    data_fim_vigencia: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    data_contratacao: Mapped[date | None] = mapped_column(Date)
    premio_total: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    premio_parcela: Mapped[float | None] = mapped_column(DECIMAL(10, 2))
    numero_parcelas: Mapped[int | None] = mapped_column()
    coberturas: Mapped[str | None] = mapped_column(Text)  # JSON string
    valor_cobertura_terceiros: Mapped[float | None] = mapped_column(DECIMAL(12, 2))
    valor_franquia: Mapped[float | None] = mapped_column(DECIMAL(10, 2))
    status: Mapped[SeguroStatus] = mapped_column(
        Enum(SeguroStatus, values_callable=lambda x: [e.value for e in x]),
        default=SeguroStatus.ATIVO, nullable=False, index=True
    )
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    observacao: Mapped[str | None] = mapped_column(Text)

    veiculo_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("veiculo.id"), nullable=False, index=True
    )

    veiculo = relationship("VeiculoModel", back_populates="seguros")
