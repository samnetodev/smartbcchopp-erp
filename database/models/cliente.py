import enum
import uuid
from datetime import datetime

from sqlalchemy import DECIMAL, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base


class ClienteTipoPessoa(str, enum.Enum):  # noqa: UP042
    PF = "PF"
    PJ = "PJ"


class ClienteStatus(str, enum.Enum):  # noqa: UP042
    ATIVO = "ativo"
    INATIVO = "inativo"
    BLOQUEADO = "bloqueado"


class ClienteModel(Base):
    __tablename__ = "cliente"

    tipo_pessoa: Mapped[ClienteTipoPessoa] = mapped_column(
        Enum(ClienteTipoPessoa, values_callable=lambda x: [e.value for e in x]),
        nullable=False
    )
    nome_razao_social: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    nome_fantasia: Mapped[str | None] = mapped_column(String(200))
    cpf_cnpj: Mapped[str] = mapped_column(String(14), unique=True, nullable=False)
    rg_ie: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(255))
    telefone: Mapped[str | None] = mapped_column(String(20))
    celular: Mapped[str | None] = mapped_column(String(20))
    limite_credito: Mapped[float] = mapped_column(DECIMAL(12, 2), default=0)
    saldo_disponivel: Mapped[float] = mapped_column(DECIMAL(12, 2), default=0)
    status: Mapped[ClienteStatus] = mapped_column(
        Enum(ClienteStatus, values_callable=lambda x: [e.value for e in x]),
        default=ClienteStatus.ATIVO, nullable=False, index=True
    )
    observacao: Mapped[str | None] = mapped_column(Text)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    endereco_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("endereco.id")
    )
    tabela_preco_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tabela_preco.id")
    )

    endereco = relationship("EnderecoModel")
