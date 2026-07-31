import enum
import uuid

from sqlalchemy import DECIMAL, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base


class MovimentacaoTipo(str, enum.Enum):  # noqa: UP042
    ENTRADA = "entrada"
    SAIDA = "saida"
    AJUSTE = "ajuste"
    TRANSFERENCIA = "transferencia"
    DEVOLUCAO = "devolucao"
    PERDA = "perda"
    RESERVA = "reserva"
    CANCELAMENTO_RESERVA = "cancelamento_reserva"


class MovimentacaoModel(Base):
    __tablename__ = "movimentacao"

    tipo: Mapped[MovimentacaoTipo] = mapped_column(
        Enum(MovimentacaoTipo, values_callable=lambda x: [e.value for e in x]),
        nullable=False, index=True
    )
    quantidade: Mapped[float] = mapped_column(DECIMAL(10, 3), nullable=False)
    documento_tipo: Mapped[str | None] = mapped_column(String(20))
    documento_numero: Mapped[str | None] = mapped_column(String(50))
    documento_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    observacao: Mapped[str | None] = mapped_column(Text)
    motivo_perda: Mapped[str | None] = mapped_column(String(100))

    produto_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("produto.id"), nullable=False, index=True
    )
    deposito_id_origem: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("deposito.id"), nullable=False
    )
    deposito_id_destino: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("deposito.id")
    )
    lote_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("lote.id"))
    pedido_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("pedido.id"))
    pedido_compra_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pedido_compra.id")
    )
    usuario_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuario.id")
    )

    produto = relationship("ProdutoModel")
    deposito_origem = relationship("DepositoModel", foreign_keys=[deposito_id_origem])
    deposito_destino = relationship("DepositoModel", foreign_keys=[deposito_id_destino])
