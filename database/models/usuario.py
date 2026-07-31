import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base


class PapelUsuario(str, enum.Enum):  # noqa: UP042
    ADMIN = "admin"
    FINANCEIRO = "financeiro"
    COMERCIAL = "comercial"
    MOTORISTA = "motorista"
    ESTOQUE = "estoque"


class UsuarioModel(Base):
    __tablename__ = "usuario"

    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    papel: Mapped[PapelUsuario] = mapped_column(
        SAEnum(PapelUsuario, values_callable=lambda x: [e.value for e in x]),
        default=PapelUsuario.COMERCIAL, nullable=False
    )
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    ultimo_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    refresh_token: Mapped[str | None] = mapped_column(String(500))

    funcionario_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("funcionario.id"), unique=True
    )

    funcionario = relationship("FuncionarioModel")
