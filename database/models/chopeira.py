import enum
import uuid
from datetime import date

from sqlalchemy import DECIMAL, Boolean, Date, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base


class ChopeiraStatus(str, enum.Enum):  # noqa: UP042
    DISPONIVEL = "disponivel"
    INSTALADA = "instalada"
    MANUTENCAO = "manutencao"
    BAIXADA = "baixada"


class ChopeiraTipo(str, enum.Enum):  # noqa: UP042
    CHOPEIRA = "chopeira"
    TORRE = "torre"
    COOLER = "cooler"
    TORNEIRA = "torneira"


class ChopeiraModel(Base):
    __tablename__ = "chopeira"

    codigo_identificacao: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    numero_serie: Mapped[str | None] = mapped_column(String(50))
    marca: Mapped[str] = mapped_column(String(50), nullable=False)
    modelo: Mapped[str] = mapped_column(String(50), nullable=False)
    tipo: Mapped[ChopeiraTipo] = mapped_column(
        Enum(ChopeiraTipo, values_callable=lambda x: [e.value for e in x]),
        nullable=False
    )
    capacidade_l: Mapped[float | None] = mapped_column(DECIMAL(6, 2))
    status: Mapped[ChopeiraStatus] = mapped_column(
        Enum(ChopeiraStatus, values_callable=lambda x: [e.value for e in x]),
        default=ChopeiraStatus.DISPONIVEL, nullable=False, index=True
    )
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)

    data_instalacao: Mapped[date | None] = mapped_column(Date)
    data_ultima_manutencao: Mapped[date | None] = mapped_column(Date)
    data_proxima_manutencao: Mapped[date | None] = mapped_column(Date, index=True)

    local_instalacao: Mapped[str | None] = mapped_column(String(200))
    latitude: Mapped[float | None] = mapped_column(DECIMAL(10, 7))
    longitude: Mapped[float | None] = mapped_column(DECIMAL(10, 7))

    observacao: Mapped[str | None] = mapped_column(Text)

    cliente_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cliente.id"), index=True
    )

    cliente = relationship("ClienteModel")
    manutencoes = relationship(
        "ChopeiraManutencaoModel", back_populates="chopeira", cascade="all, delete-orphan"
    )
    historico = relationship(
        "ChopeiraHistoricoModel", back_populates="chopeira", cascade="all, delete-orphan"
    )
