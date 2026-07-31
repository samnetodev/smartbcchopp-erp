import enum
import uuid
from typing import Any

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base


class AuditoriaAcao(str, enum.Enum):  # noqa: UP042
    C = "C"
    U = "U"
    D = "D"


class AuditoriaModel(Base):
    __tablename__ = "auditoria"

    entidade_tipo: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    entidade_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    acao: Mapped[AuditoriaAcao] = mapped_column(
        Enum(AuditoriaAcao, values_callable=lambda x: [e.value for e in x]), nullable=False
    )
    dados_anteriores: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    dados_novos: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    ip_origem: Mapped[str | None] = mapped_column(String(45))
    user_agent: Mapped[str | None] = mapped_column(String(255))

    usuario_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuario.id")
    )

    usuario = relationship("UsuarioModel")
