from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProductBase(BaseModel):
    codigo: str = Field(..., max_length=20)
    nome: str = Field(..., max_length=200)
    categoria: str = Field(..., pattern="^(chope|carvao|transporte)$")
    unidade_medida: str = Field(..., pattern="^(L|KG|UN|PCT|SACO)$")
    preco_venda: Decimal = Field(..., gt=0)
    familia_id: UUID | None = None
    ncm: str | None = Field(None, max_length=8)
    ativo: bool = True


class ProductCreate(ProductBase):
    preco_custo: Decimal | None = None
    codigo_barras: str | None = Field(None, max_length=20)
    estoque_minimo: Decimal = Decimal("0")
    lote_obrigatorio: bool = False


class ProductUpdate(BaseModel):
    nome: str | None = Field(None, max_length=200)
    preco_venda: Decimal | None = Field(None, gt=0)
    preco_custo: Decimal | None = None
    ativo: bool | None = None
    familia_id: UUID | None = None
    ncm: str | None = Field(None, max_length=8)


class ProductResponse(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    preco_custo: Decimal | None = None
    codigo_barras: str | None = None
    estoque_minimo: Decimal = Decimal("0")
    lote_obrigatorio: bool = False
    created_at: datetime
    updated_at: datetime


class ProductListResponse(BaseModel):
    items: list[ProductResponse]
    total: int
    skip: int
    limit: int
