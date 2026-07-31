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


class ManutencaoCategoria(str, enum.Enum):  # noqa: UP042
    OLEO = "oleo"
    PNEUS = "pneus"
    FREIOS = "freios"
    MOTOR = "motor"
    SUSPENSAO = "suspensao"
    ELETRICA = "eletrica"
    ARREFECIMENTO = "arrefecimento"
    GERAL = "geral"
    OUTROS = "outros"


class ManutencaoStatus(str, enum.Enum):  # noqa: UP042
    AGENDADA = "agendada"
    ANDAMENTO = "andamento"
    CONCLUIDA = "concluida"
    CANCELADA = "cancelada"


class ManutencaoModel(Base):
    __tablename__ = "manutencao"

    tipo: Mapped[ManutencaoTipo] = mapped_column(
        Enum(ManutencaoTipo, values_callable=lambda x: [e.value for e in x]),
        nullable=False
    )
    categoria: Mapped[ManutencaoCategoria] = mapped_column(
        Enum(ManutencaoCategoria, values_callable=lambda x: [e.value for e in x]), nullable=False
    )
    data_agendamento: Mapped[date | None] = mapped_column(Date)
    data_inicio: Mapped[date | None] = mapped_column(Date, index=True)
    data_fim: Mapped[date | None] = mapped_column(Date)
    km_na_manutencao: Mapped[int | None] = mapped_column()
    oficina_nome: Mapped[str | None] = mapped_column(String(150))
    oficina_cnpj: Mapped[str | None] = mapped_column(String(14))
    descricao: Mapped[str] = mapped_column(Text, nullable=False)
    observacao: Mapped[str | None] = mapped_column(Text)
    status: Mapped[ManutencaoStatus] = mapped_column(
        Enum(ManutencaoStatus, values_callable=lambda x: [e.value for e in x]),
        default=ManutencaoStatus.AGENDADA, nullable=False, index=True
    )
    valor_pecas: Mapped[float] = mapped_column(DECIMAL(10, 2), default=0)
    valor_servico: Mapped[float] = mapped_column(DECIMAL(10, 2), default=0)
    valor_total: Mapped[float] = mapped_column(DECIMAL(10, 2), default=0)
    nota_fiscal: Mapped[str | None] = mapped_column(String(50))

    veiculo_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("veiculo.id"), nullable=False, index=True
    )

    veiculo = relationship("VeiculoModel")
    itens = relationship(
        "ManutencaoItemModel", back_populates="manutencao", cascade="all, delete-orphan"
    )


class ManutencaoItemModel(Base):
    __tablename__ = "manutencao_item"

    descricao: Mapped[str] = mapped_column(String(200), nullable=False)
    tipo: Mapped[str] = mapped_column(String(10), nullable=False)  # peca | servico
    quantidade: Mapped[float] = mapped_column(DECIMAL(8, 2), default=1)
    valor_unitario: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    valor_total: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)

    manutencao_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("manutencao.id"), nullable=False
    )

    manutencao = relationship("ManutencaoModel", back_populates="itens")
