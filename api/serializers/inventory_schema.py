from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class EntryCreate(BaseModel):
    produto_id: UUID
    deposito_id: UUID
    quantidade: Decimal = Field(gt=0)
    lote_id: UUID | None = None
    documento_tipo: str | None = None
    documento_numero: str | None = None
    documento_id: UUID | None = None
    observacao: str | None = None


class ExitCreate(BaseModel):
    produto_id: UUID
    deposito_id: UUID
    quantidade: Decimal = Field(gt=0)
    lote_id: UUID | None = None
    documento_tipo: str | None = None
    documento_numero: str | None = None
    documento_id: UUID | None = None
    observacao: str | None = None


class TransferCreate(BaseModel):
    produto_id: UUID
    deposito_id_origem: UUID
    deposito_id_destino: UUID
    quantidade: Decimal = Field(gt=0)
    lote_id: UUID | None = None
    observacao: str | None = None


class LossCreate(BaseModel):
    produto_id: UUID
    deposito_id: UUID
    quantidade: Decimal = Field(gt=0)
    motivo: str
    lote_id: UUID | None = None
    observacao: str | None = None


class AdjustmentCreate(BaseModel):
    produto_id: UUID
    deposito_id: UUID
    quantidade_nova: Decimal = Field(ge=0)
    lote_id: UUID | None = None
    observacao: str | None = None


class MovementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tipo: str
    quantidade: Decimal
    motivo_perda: str | None
    documento_tipo: str | None
    documento_numero: str | None
    documento_id: UUID | None
    observacao: str | None

    produto_id: UUID
    deposito_id_origem: UUID
    deposito_id_destino: UUID | None
    lote_id: UUID | None
    pedido_id: UUID | None
    pedido_compra_id: UUID | None
    usuario_id: UUID | None

    created_at: datetime


class MovementListResponse(BaseModel):
    items: list[MovementResponse]
    total: int


class StockResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    produto_id: UUID
    deposito_id: UUID
    lote_id: UUID | None
    quantidade_atual: Decimal
    quantidade_reservada: Decimal
    localizacao: str | None
    versao: int

    created_at: datetime
    updated_at: datetime


class StockListResponse(BaseModel):
    items: list[StockResponse]
    total: int


class DepositoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    codigo: str
    nome: str
    tipo: str | None = None
    ativo: bool = True


class InventoryCountCreate(BaseModel):
    produto_id: UUID
    deposito_id: UUID
    quantidade_contada: Decimal = Field(ge=0)
    lote_id: UUID | None = None
    observacao: str | None = None


class InventoryCountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: str
    data_contagem: date
    produto_id: UUID
    deposito_id: UUID
    quantidade_sistema: Decimal
    quantidade_contada: Decimal
    diferenca: Decimal
    observacao: str | None
    lote_id: UUID | None
    usuario_id: UUID | None

    created_at: datetime
    updated_at: datetime


class InventoryCountListResponse(BaseModel):
    items: list[InventoryCountResponse]
    total: int


class LowStockReportItem(BaseModel):
    produto_id: UUID
    produto_codigo: str
    produto_nome: str
    deposito_id: UUID
    deposito_nome: str
    quantidade_atual: Decimal
    estoque_minimo: Decimal


class StockValueReportItem(BaseModel):
    produto_id: UUID
    produto_codigo: str
    produto_nome: str
    quantidade_total: Decimal
    preco_custo_medio: Decimal
    valor_total: Decimal
