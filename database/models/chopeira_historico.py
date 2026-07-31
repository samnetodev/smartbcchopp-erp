import enum
import uuid
from datetime import date

from sqlalchemy import Date, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base


class HistoricoEvento(str, enum.Enum):  # noqa: UP042
    INSTALACAO = "instalacao"
    DESINSTALACAO = "desinstalacao"
    TRANSFERENCIA = "transferencia"
    MANUTENCAO = "manutencao"
    STATUS_CHANGE = "status_change"
    OBSERVACAO = "observacao"


class ChopeiraHistoricoModel(Base):
    __tablename__ = "chopeira_historico"

    evento: Mapped[HistoricoEvento] = mapped_column(
        Enum(HistoricoEvento, values_callable=lambda x: [e.value for e in x]),
        nullable=False, index=True
    )
    data_evento: Mapped[date] = mapped_column(Date, nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text)
    detalhes: Mapped[str | None] = mapped_column(String(500))

    chopeira_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chopeira.id"), nullable=False, index=True
    )
    cliente_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cliente.id")
    )
    usuario_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuario.id")
    )

    chopeira = relationship("ChopeiraModel", back_populates="historico")
    cliente = relationship("ClienteModel")
