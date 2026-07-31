import enum
import uuid
from datetime import date

from sqlalchemy import DECIMAL, Date, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base


class FuncionarioStatus(str, enum.Enum):  # noqa: UP042
    ATIVO = "ativo"
    INATIVO = "inativo"
    AFASTADO = "afastado"


class FuncionarioModel(Base):
    __tablename__ = "funcionario"

    matricula: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    cpf: Mapped[str] = mapped_column(String(11), unique=True, nullable=False)
    rg: Mapped[str | None] = mapped_column(String(20))
    data_nascimento: Mapped[date] = mapped_column(Date, nullable=False)
    cargo: Mapped[str] = mapped_column(String(100), nullable=False)
    departamento: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    data_admissao: Mapped[date] = mapped_column(Date, nullable=False)
    data_demissao: Mapped[date | None] = mapped_column(Date)
    salario: Mapped[float | None] = mapped_column(DECIMAL(12, 2))
    telefone: Mapped[str | None] = mapped_column(String(20))
    email_corporativo: Mapped[str | None] = mapped_column(String(255), unique=True)
    tipo_sanguineo: Mapped[str | None] = mapped_column(String(5))
    status: Mapped[FuncionarioStatus] = mapped_column(
        Enum(FuncionarioStatus, values_callable=lambda x: [e.value for e in x]),
        default=FuncionarioStatus.ATIVO, nullable=False, index=True
    )

    endereco_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("endereco.id")
    )

    endereco = relationship("EnderecoModel")
