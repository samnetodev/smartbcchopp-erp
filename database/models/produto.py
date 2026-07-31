import enum
import uuid

from sqlalchemy import DECIMAL, Boolean, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base


class ProdutoCategoria(str, enum.Enum):  # noqa: UP042
    CHOPE = "chope"
    CARVAO = "carvao"
    TRANSPORTE = "transporte"


class UnidadeMedida(str, enum.Enum):  # noqa: UP042
    L = "L"
    KG = "KG"
    UN = "UN"
    PCT = "PCT"
    SACO = "SACO"


class ProdutoModel(Base):
    __tablename__ = "produto"

    codigo: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    codigo_barras: Mapped[str | None] = mapped_column(String(20), unique=True)
    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text)
    categoria: Mapped[ProdutoCategoria] = mapped_column(
        Enum(ProdutoCategoria, values_callable=lambda x: [e.value for e in x]),
        nullable=False, index=True
    )
    unidade_medida: Mapped[UnidadeMedida] = mapped_column(
        Enum(UnidadeMedida, values_callable=lambda x: [e.value for e in x]),
        nullable=False
    )
    tipo_embalagem: Mapped[str | None] = mapped_column(String(50))
    peso_kg: Mapped[float | None] = mapped_column(DECIMAL(10, 3))
    volume_l: Mapped[float | None] = mapped_column(DECIMAL(10, 3))
    preco_custo: Mapped[float | None] = mapped_column(DECIMAL(12, 4))
    preco_venda: Mapped[float] = mapped_column(DECIMAL(12, 2), nullable=False)
    ncm: Mapped[str | None] = mapped_column(String(8))
    cest: Mapped[str | None] = mapped_column(String(7))
    icms_aliquota: Mapped[float | None] = mapped_column(DECIMAL(5, 2))
    icms_cst: Mapped[str | None] = mapped_column(String(3))
    ipi_aliquota: Mapped[float] = mapped_column(DECIMAL(5, 2), default=0)
    pis_cofins_cst: Mapped[str | None] = mapped_column(String(3))
    estoque_minimo: Mapped[float] = mapped_column(DECIMAL(10, 3), default=0)
    estoque_maximo: Mapped[float | None] = mapped_column(DECIMAL(10, 3))
    lote_obrigatorio: Mapped[bool] = mapped_column(Boolean, default=False)
    dias_validade: Mapped[int | None] = mapped_column()
    controla_temperatura: Mapped[bool] = mapped_column(Boolean, default=False)
    temperatura_min: Mapped[float | None] = mapped_column(DECIMAL(5, 2))
    temperatura_max: Mapped[float | None] = mapped_column(DECIMAL(5, 2))
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)

    familia_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("familia_produto.id")
    )

    familia = relationship("FamiliaProdutoModel")
