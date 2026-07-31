from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class OrderItemCreate(BaseModel):
    produto_id: UUID
    quantidade: Decimal = Field(gt=0)
    preco_unitario: Decimal = Field(gt=0)
    desconto_percentual: Decimal = Decimal("0")


class OrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    produto_id: UUID
    quantidade: Decimal
    preco_unitario: Decimal
    desconto_percentual: Decimal
    desconto_valor: Decimal
    subtotal: Decimal
    ordem: int


class OrderCreate(BaseModel):
    cliente_id: UUID
    data_entrega_prevista: date | None = None
    condicao_pagamento_id: UUID | None = None
    observacao: str | None = None
    items: list[OrderItemCreate] = Field(..., min_length=1)


class OrderUpdateStatus(BaseModel):
    status: str = Field(pattern="^(rascunho|aguardando_aprovacao|aprovado|cancelado)$")


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    numero: str
    cliente_id: UUID
    data_emissao: date
    data_entrega_prevista: date | None
    status: str
    subtotal: Decimal
    desconto: Decimal
    frete: Decimal
    total: Decimal
    observacao: str | None
    created_at: datetime
    updated_at: datetime
    itens: list[OrderItemResponse] = []


class OrderListResponse(BaseModel):
    items: list[OrderResponse]
    total: int
    skip: int
    limit: int
