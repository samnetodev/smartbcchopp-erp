import enum
import uuid
from datetime import date

from sqlalchemy import Boolean, Date, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base


class MotoristaStatus(str, enum.Enum):  # noqa: UP042
    DISPONIVEL = "disponivel"
    EM_VIAGEM = "em_viagem"
    FOLGA = "folga"
    AFASTADO = "afastado"
    INATIVO = "inativo"


class CategoriaCNH(str, enum.Enum):  # noqa: UP042
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    AB = "AB"
    AC = "AC"
    AD = "AD"
    AE = "AE"


class MotoristaModel(Base):
    __tablename__ = "motorista"

    numero_cnh: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    categoria_cnh: Mapped[CategoriaCNH] = mapped_column(
        Enum(CategoriaCNH, values_callable=lambda x: [e.value for e in x]),
        nullable=False
    )
    data_validade_cnh: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    data_primeira_cnh: Mapped[date | None] = mapped_column(Date)
    orgao_emissor_cnh: Mapped[str | None] = mapped_column(String(50))
    cnh_observacao: Mapped[str | None] = mapped_column(String(200))
    data_ultimo_exame_medico: Mapped[date | None] = mapped_column(Date)
    data_validade_exame_medico: Mapped[date | None] = mapped_column(Date)
    certificacoes: Mapped[str | None] = mapped_column()  # JSON string
    telefone: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[MotoristaStatus] = mapped_column(
        Enum(MotoristaStatus, values_callable=lambda x: [e.value for e in x]),
        default=MotoristaStatus.DISPONIVEL, nullable=False, index=True
    )
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)

    funcionario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("funcionario.id"), unique=True, nullable=False
    )

    funcionario = relationship("FuncionarioModel")
