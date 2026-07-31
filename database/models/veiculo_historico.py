import enum
import uuid
from datetime import date

from sqlalchemy import Date, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base


class VeiculoHistoricoEvento(str, enum.Enum):  # noqa: UP042
    CRIACAO = "criacao"
    ALTERACAO_STATUS = "alteracao_status"
    MANUTENCAO = "manutencao"
    TROCA_OLEO = "troca_oleo"
    TROCA_PNEU = "troca_pneu"
    SEGURO = "seguro"
    ABASTECIMENTO = "abastecimento"
    MULTA = "multa"
    KM_ATUALIZADO = "km_atualizado"
    DOCUMENTO = "documento"
    OBSERVACAO = "observacao"


class VeiculoHistoricoModel(Base):
    __tablename__ = "veiculo_historico"

    evento: Mapped[VeiculoHistoricoEvento] = mapped_column(
        Enum(VeiculoHistoricoEvento, values_callable=lambda x: [e.value for e in x]),
        nullable=False, index=True
    )
    data_evento: Mapped[date] = mapped_column(Date, nullable=False)
    descricao: Mapped[str] = mapped_column(Text, nullable=False)
    detalhes: Mapped[str | None] = mapped_column(String(500))

    veiculo_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("veiculo.id"), nullable=False, index=True
    )
    usuario_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuario.id")
    )

    veiculo = relationship("VeiculoModel", back_populates="historico")
