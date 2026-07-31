import enum
import uuid
from datetime import date

from sqlalchemy import DECIMAL, Date, Enum, ForeignKey, SmallInteger, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base


class MultaStatus(str, enum.Enum):  # noqa: UP042
    PENDENTE = "pendente"
    PAGO = "pago"
    RECORRENDO = "recorrendo"
    CANCELADO = "cancelado"


class MultaResponsavel(str, enum.Enum):  # noqa: UP042
    MOTORISTA = "motorista"
    EMPRESA = "empresa"


class MultaModel(Base):
    __tablename__ = "multa"

    data_infracao: Mapped[date] = mapped_column(Date, nullable=False)
    data_notificacao: Mapped[date | None] = mapped_column(Date)
    data_vencimento: Mapped[date | None] = mapped_column(Date)
    data_pagamento: Mapped[date | None] = mapped_column(Date)
    orgao_autuador: Mapped[str] = mapped_column(String(50), nullable=False)
    descricao: Mapped[str] = mapped_column(String(300), nullable=False)
    artigo_ctb: Mapped[str | None] = mapped_column(String(20))
    pontuacao: Mapped[int | None] = mapped_column(SmallInteger)
    valor_original: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    valor_pago: Mapped[float | None] = mapped_column(DECIMAL(10, 2))
    desconto: Mapped[float] = mapped_column(DECIMAL(10, 2), default=0)
    status: Mapped[MultaStatus] = mapped_column(
        Enum(MultaStatus, values_callable=lambda x: [e.value for e in x]),
        default=MultaStatus.PENDENTE, nullable=False, index=True
    )
    responsavel: Mapped[MultaResponsavel] = mapped_column(
        Enum(MultaResponsavel, values_callable=lambda x: [e.value for e in x]),
        nullable=False
    )

    veiculo_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("veiculo.id"), nullable=False, index=True
    )
    motorista_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("motorista.id")
    )

    veiculo = relationship("VeiculoModel")
    motorista = relationship("MotoristaModel")
