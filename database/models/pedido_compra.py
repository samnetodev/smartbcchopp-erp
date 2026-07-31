import enum
import uuid
from datetime import date

from sqlalchemy import DECIMAL, Date, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base


class PedidoCompraStatus(str, enum.Enum):  # noqa: UP042
    RASCUNHO = "rascunho"
    COTACAO = "cotacao"
    AGUARDANDO_APROVACAO = "aguardando_aprovacao"
    APROVADO = "aprovado"
    ENVIADO = "enviado"
    RECEBIDO_PARCIAL = "recebido_parcial"
    RECEBIDO = "recebido"
    CANCELADO = "cancelado"


class PedidoCompraModel(Base):
    __tablename__ = "pedido_compra"

    numero: Mapped[str] = mapped_column(String(15), unique=True, nullable=False)
    data_emissao: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)
    data_previsao_entrega: Mapped[date | None] = mapped_column(Date)
    data_entrega: Mapped[date | None] = mapped_column(Date)
    status: Mapped[PedidoCompraStatus] = mapped_column(
        Enum(PedidoCompraStatus, values_callable=lambda x: [e.value for e in x]),
        default=PedidoCompraStatus.RASCUNHO, nullable=False, index=True
    )
    subtotal: Mapped[float | None] = mapped_column(DECIMAL(12, 2))
    frete: Mapped[float] = mapped_column(DECIMAL(10, 2), default=0)
    desconto: Mapped[float] = mapped_column(DECIMAL(10, 2), default=0)
    total: Mapped[float | None] = mapped_column(DECIMAL(12, 2))
    observacao: Mapped[str | None] = mapped_column(Text)

    fornecedor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fornecedor.id"), nullable=False
    )
    usuario_solicitante_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("funcionario.id")
    )
    usuario_aprovador_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("funcionario.id")
    )
    condicao_pagamento_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("condicao_pagamento.id")
    )

    fornecedor = relationship("FornecedorModel")
    itens = relationship(
        "ItemPedidoCompraModel", back_populates="pedido_compra", cascade="all, delete-orphan"
    )


class ItemPedidoCompraModel(Base):
    __tablename__ = "item_pedido_compra"

    quantidade: Mapped[float] = mapped_column(DECIMAL(10, 3), nullable=False)
    quantidade_recebida: Mapped[float] = mapped_column(DECIMAL(10, 3), default=0)
    preco_unitario: Mapped[float] = mapped_column(DECIMAL(12, 4), nullable=False)
    subtotal: Mapped[float] = mapped_column(DECIMAL(12, 2), nullable=False)

    pedido_compra_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pedido_compra.id"), nullable=False
    )
    produto_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("produto.id"), nullable=False
    )

    pedido_compra = relationship("PedidoCompraModel", back_populates="itens")
    produto = relationship("ProdutoModel")
