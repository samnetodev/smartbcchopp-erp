import enum
import uuid
from datetime import date

from sqlalchemy import DECIMAL, Boolean, Date, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.models.base import Base


class LancamentoTipo(str, enum.Enum):  # noqa: UP042
    ENTRADA = "entrada"
    SAIDA = "saida"


class LancamentoModel(Base):
    __tablename__ = "lancamento"

    data: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    tipo: Mapped[LancamentoTipo] = mapped_column(
        Enum(LancamentoTipo, values_callable=lambda x: [e.value for e in x]),
        nullable=False
    )
    valor: Mapped[float] = mapped_column(DECIMAL(12, 2), nullable=False)
    categoria: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    descricao: Mapped[str] = mapped_column(String(200), nullable=False)
    conciliado: Mapped[bool] = mapped_column(Boolean, default=False)
    data_conciliacao: Mapped[date | None] = mapped_column(Date)

    conta_receber_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("conta_receber.id")
    )
    conta_pagar_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("conta_pagar.id")
    )
