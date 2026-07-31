import enum
import uuid
from datetime import date

from sqlalchemy import DECIMAL, Date, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base


class ManutencaoTipo(str, enum.Enum):  # noqa: UP042
    PREVENTIVA = "preventiva"
    CORRETIVA = "corretiva"


class ManutencaoStatus(str, enum.Enum):  # noqa: UP042
    AGENDADA = "agendada"
    ANDAMENTO = "andamento"
    CONCLUIDA = "concluida"
    CANCELADA = "cancelada"


class ChopeiraManutencaoModel(Base):
    __tablename__ = "chopeira_manutencao"

    tipo: Mapped[ManutencaoTipo] = mapped_column(
        Enum(ManutencaoTipo, values_callable=lambda x: [e.value for e in x]),
        nullable=False
    )
    status: Mapped[ManutencaoStatus] = mapped_column(
        Enum(ManutencaoStatus, values_callable=lambda x: [e.value for e in x]),
        default=ManutencaoStatus.AGENDADA, nullable=False, index=True
    )
    data_solicitacao: Mapped[date] = mapped_column(Date, nullable=False)
    data_inicio: Mapped[date | None] = mapped_column(Date)
    data_fim: Mapped[date | None] = mapped_column(Date)
    descricao_problema: Mapped[str | None] = mapped_column(Text)
    descricao_servico: Mapped[str | None] = mapped_column(Text)
    tecnico_responsavel: Mapped[str | None] = mapped_column(String(100))
    custo_pecas: Mapped[float] = mapped_column(DECIMAL(10, 2), default=0)
    custo_servico: Mapped[float] = mapped_column(DECIMAL(10, 2), default=0)

    chopeira_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chopeira.id"), nullable=False, index=True
    )

    chopeira = relationship("ChopeiraModel", back_populates="manutencoes")

    @property
    def custo_total(self) -> float:
        return self.custo_pecas + self.custo_servico
