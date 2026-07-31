import enum
import uuid
from datetime import date

from sqlalchemy import DECIMAL, Date, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base


class PneuPosicao(str, enum.Enum):  # noqa: UP042
    DIANTEIRO_E = "dianteiro_e"
    DIANTEIRO_D = "dianteiro_d"
    TRASEIRO_E = "traseiro_e"
    TRASEIRO_D = "traseiro_d"
    TAP_E = "tap_e"
    TAP_D = "tap_d"
    RESERVA = "reserva"


class PneuMarca(str, enum.Enum):  # noqa: UP042
    PIRELLI = "pirelli"
    GOODYEAR = "goodyear"
    BRIDGESTONE = "bridgestone"
    MICHELIN = "michelin"
    CONTINENTAL = "continental"
    DUNLOP = "dunlop"
    OUTRA = "outra"


class PneuStatus(str, enum.Enum):  # noqa: UP042
    ATIVO = "ativo"
    TROCADO = "trocado"
    DESCARTADO = "descartado"


class PneuModel(Base):
    __tablename__ = "veiculo_pneu"

    posicao: Mapped[PneuPosicao] = mapped_column(
        Enum(PneuPosicao, values_callable=lambda x: [e.value for e in x]),
        nullable=False
    )
    marca: Mapped[PneuMarca] = mapped_column(
        Enum(PneuMarca, values_callable=lambda x: [e.value for e in x]),
        nullable=False
    )
    modelo: Mapped[str] = mapped_column(String(50), nullable=False)
    medida: Mapped[str] = mapped_column(String(20), nullable=False)
    numero_fogo: Mapped[str | None] = mapped_column(String(30))
    km_instalacao: Mapped[int] = mapped_column(Integer, nullable=False)
    km_troca: Mapped[int | None] = mapped_column(Integer)
    data_instalacao: Mapped[date] = mapped_column(Date, nullable=False)
    data_troca: Mapped[date | None] = mapped_column(Date)
    vida_util_km: Mapped[int | None] = mapped_column(Integer)
    valor_unitario: Mapped[float | None] = mapped_column(DECIMAL(10, 2))
    status: Mapped[PneuStatus] = mapped_column(
        Enum(PneuStatus, values_callable=lambda x: [e.value for e in x]),
        default=PneuStatus.ATIVO, nullable=False, index=True
    )
    observacao: Mapped[str | None] = mapped_column(Text)

    veiculo_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("veiculo.id"), nullable=False, index=True
    )

    veiculo = relationship("VeiculoModel", back_populates="pneus")
