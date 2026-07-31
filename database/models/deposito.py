import enum
import uuid

from sqlalchemy import Boolean, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base


class DepositoTipo(str, enum.Enum):  # noqa: UP042
    MATRIZ = "matriz"
    FILIAL = "filial"
    DEPOSITO = "deposito"


class DepositoModel(Base):
    __tablename__ = "deposito"

    codigo: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    tipo: Mapped[DepositoTipo] = mapped_column(
        Enum(DepositoTipo, values_callable=lambda x: [e.value for e in x]),
        nullable=False
    )
    telefone: Mapped[str | None] = mapped_column(String(20))
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)

    endereco_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("endereco.id"), nullable=False
    )

    endereco = relationship("EnderecoModel")
