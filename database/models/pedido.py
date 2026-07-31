import enum
import uuid
from datetime import date

from sqlalchemy import DECIMAL, Date, Enum, ForeignKey, SmallInteger, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base


class PedidoStatus(str, enum.Enum):  # noqa: UP042
    RASCUNHO = "rascunho"
    AGUARDANDO_APROVACAO = "aguardando_aprovacao"
    APROVADO = "aprovado"
    EM_SEPARACAO = "em_separacao"
    FATURADO = "faturado"
    ENTREGUE = "entregue"
    CANCELADO = "cancelado"


class TipoFrete(str, enum.Enum):  # noqa: UP042
    CIF = "CIF"
    FOB = "FOB"


class PedidoModel(Base):
    __tablename__ = "pedido"

    numero: Mapped[str] = mapped_column(String(15), unique=True, nullable=False, index=True)
    data_emissao: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)
    data_entrega_prevista: Mapped[date | None] = mapped_column(Date, index=True)
    data_entrega_real: Mapped[date | None] = mapped_column(Date)
    tipo_frete: Mapped[TipoFrete | None] = mapped_column(
        Enum(TipoFrete, values_callable=lambda x: [e.value for e in x]),
    )
    status: Mapped[PedidoStatus] = mapped_column(
        Enum(PedidoStatus, values_callable=lambda x: [e.value for e in x]),
        default=PedidoStatus.RASCUNHO, nullable=False, index=True
    )
    subtotal: Mapped[float] = mapped_column(DECIMAL(12, 2), default=0, nullable=False)
    desconto: Mapped[float] = mapped_column(DECIMAL(12, 2), default=0)
    frete: Mapped[float] = mapped_column(DECIMAL(12, 2), default=0)
    total: Mapped[float] = mapped_column(DECIMAL(12, 2), default=0, nullable=False)
    observacao: Mapped[str | None] = mapped_column(Text)

    cliente_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cliente.id"), nullable=False, index=True
    )
    vendedor_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("funcionario.id")
    )
    condicao_pagamento_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("condicao_pagamento.id")
    )

    cliente = relationship("ClienteModel")
    vendedor = relationship("FuncionarioModel")
    condicao_pagamento = relationship("CondicaoPagamentoModel")
    itens = relationship("ItemPedidoModel", back_populates="pedido", cascade="all, delete-orphan")


class ItemPedidoModel(Base):
    __tablename__ = "item_pedido"

    quantidade: Mapped[float] = mapped_column(DECIMAL(10, 3), nullable=False)
    preco_unitario: Mapped[float] = mapped_column(DECIMAL(12, 4), nullable=False)
    desconto_percentual: Mapped[float] = mapped_column(DECIMAL(5, 2), default=0)
    desconto_valor: Mapped[float] = mapped_column(DECIMAL(12, 2), default=0)
    subtotal: Mapped[float] = mapped_column(DECIMAL(12, 2), nullable=False)
    ordem: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    pedido_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pedido.id"), nullable=False, index=True
    )
    produto_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("produto.id"), nullable=False
    )
    lote_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("lote.id"))

    pedido = relationship("PedidoModel", back_populates="itens")
    produto = relationship("ProdutoModel")
