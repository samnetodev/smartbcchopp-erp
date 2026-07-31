import enum
import uuid
from datetime import date

from sqlalchemy import DECIMAL, Date, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base


class MetaStatus(str, enum.Enum):
    ABERTA = "aberta"
    ATINGIDA = "atingida"
    NAO_ATINGIDA = "nao_atingida"
    CANCELADA = "cancelada"


class MetaModel(Base):
    __tablename__ = "meta_comercial"

    descricao: Mapped[str] = mapped_column(String(300), nullable=False)
    periodo_inicio: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    periodo_fim: Mapped[date] = mapped_column(Date, nullable=False)
    valor_meta: Mapped[float] = mapped_column(DECIMAL(12, 2), nullable=False)
    valor_realizado: Mapped[float] = mapped_column(DECIMAL(12, 2), default=0)
    comissao_percentual: Mapped[float] = mapped_column(DECIMAL(5, 2), default=0)
    status: Mapped[MetaStatus] = mapped_column(
        Enum(MetaStatus, values_callable=lambda x: [e.value for e in x]),
        default=MetaStatus.ABERTA, nullable=False, index=True
    )

    vendedor_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("funcionario.id"), index=True
    )

    vendedor = relationship("FuncionarioModel")
