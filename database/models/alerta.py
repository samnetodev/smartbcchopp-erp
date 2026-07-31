import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base


class AlertaNivel(str, enum.Enum):  # noqa: UP042
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertaModel(Base):
    __tablename__ = "alerta"

    tipo: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    entidade_tipo: Mapped[str | None] = mapped_column(String(30), index=True)
    entidade_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    nivel: Mapped[AlertaNivel] = mapped_column(
        Enum(AlertaNivel, values_callable=lambda x: [e.value for e in x]),
        default=AlertaNivel.WARNING, nullable=False
    )
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    mensagem: Mapped[str | None] = mapped_column(Text)
    lido: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    data_lido: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    data_resolvido: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    usuario_responsavel_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("funcionario.id")
    )

    usuario_responsavel = relationship("FuncionarioModel")
