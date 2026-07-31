import enum
import uuid

from sqlalchemy import Enum, ForeignKey, SmallInteger, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base


class FornecedorCategoria(str, enum.Enum):  # noqa: UP042
    CHOPE = "chope"
    CARVAO = "carvao"
    TRANSPORTE = "transporte"
    INSUMOS = "insumos"
    SERVICOS = "servicos"
    OUTROS = "outros"


class FornecedorStatus(str, enum.Enum):  # noqa: UP042
    ATIVO = "ativo"
    INATIVO = "inativo"
    BLOQUEADO = "bloqueado"


class FornecedorModel(Base):
    __tablename__ = "fornecedor"

    tipo_pessoa: Mapped[str] = mapped_column(String(2), nullable=False)
    nome_razao_social: Mapped[str] = mapped_column(String(200), nullable=False)
    nome_fantasia: Mapped[str | None] = mapped_column(String(200))
    cpf_cnpj: Mapped[str] = mapped_column(String(14), unique=True, nullable=False)
    inscricao_estadual: Mapped[str | None] = mapped_column(String(20))
    inscricao_municipal: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(255))
    telefone: Mapped[str | None] = mapped_column(String(20))
    contato_nome: Mapped[str | None] = mapped_column(String(100))
    categoria: Mapped[FornecedorCategoria] = mapped_column(
        Enum(FornecedorCategoria, values_callable=lambda x: [e.value for e in x]),
        nullable=False, index=True
    )
    prazo_medio_entrega_dias: Mapped[int | None] = mapped_column(SmallInteger)
    avaliacao: Mapped[int | None] = mapped_column(SmallInteger)
    status: Mapped[FornecedorStatus] = mapped_column(
        Enum(FornecedorStatus, values_callable=lambda x: [e.value for e in x]),
        default=FornecedorStatus.ATIVO, nullable=False, index=True
    )
    observacao: Mapped[str | None] = mapped_column(Text)

    endereco_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("endereco.id")
    )

    endereco = relationship("EnderecoModel")
