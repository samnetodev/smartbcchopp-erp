import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    SmallInteger,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base


class EntregaStatus(str, enum.Enum):  # noqa: UP042
    PENDENTE = "pendente"
    EM_ROTA = "em_rota"
    ENTREGUE = "entregue"
    PARCIAL = "parcial"
    ATRASADO = "atrasado"
    CANCELADA = "cancelada"


class EntregaModel(Base):
    __tablename__ = "entrega"

    rota: Mapped[str | None] = mapped_column(String(100))
    sequencia: Mapped[int | None] = mapped_column(SmallInteger)
    data_saida: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    data_chegada: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    data_entrega: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    km_saida: Mapped[int | None] = mapped_column(Integer)
    km_chegada: Mapped[int | None] = mapped_column(Integer)
    km_rota: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[EntregaStatus] = mapped_column(
        Enum(EntregaStatus, values_callable=lambda x: [e.value for e in x]),
        default=EntregaStatus.PENDENTE, nullable=False, index=True
    )
    assinatura_recebedor: Mapped[str | None] = mapped_column(String(100))
    observacao: Mapped[str | None] = mapped_column(Text)

    pedido_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pedido.id"), nullable=False, index=True
    )
    veiculo_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("veiculo.id"), nullable=False
    )
    motorista_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("motorista.id"), nullable=False
    )

    pedido = relationship("PedidoModel")
    veiculo = relationship("VeiculoModel")
    motorista = relationship("MotoristaModel")
