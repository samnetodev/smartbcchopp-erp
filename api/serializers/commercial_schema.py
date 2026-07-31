from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MetaCreate(BaseModel):
    descricao: str = Field(..., max_length=300)
    periodo_inicio: date
    periodo_fim: date
    valor_meta: Decimal = Field(gt=0)
    comissao_percentual: Decimal = Decimal("0")
    vendedor_id: UUID | None = None


class MetaUpdate(BaseModel):
    descricao: str | None = Field(None, max_length=300)
    periodo_inicio: date | None = None
    periodo_fim: date | None = None
    valor_meta: Decimal | None = Field(None, gt=0)
    valor_realizado: Decimal | None = None
    comissao_percentual: Decimal | None = None
    status: str | None = Field(None, pattern="^(aberta|atingida|nao_atingida|cancelada)$")


class MetaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    descricao: str
    periodo_inicio: date
    periodo_fim: date
    valor_meta: Decimal
    valor_realizado: Decimal
    comissao_percentual: Decimal
    status: str
    vendedor_id: UUID | None = None
    created_at: datetime
    updated_at: datetime


class MetaListResponse(BaseModel):
    items: list[MetaResponse]
    total: int
    skip: int
    limit: int


class ClienteInativoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    nome_razao_social: str
    nome_fantasia: str | None = None
    cpf_cnpj: str
    email: str | None = None
    celular: str | None = None
    status: str
    ultima_compra: date | None = None


class ClienteRankingItem(BaseModel):
    cliente_id: UUID
    cliente_nome: str
    total_vendas: float
    qtd_pedidos: int


class FaturamentoItem(BaseModel):
    periodo: str
    receita: float
    qtd_pedidos: int


class IndicadoresResponse(BaseModel):
    total_pedidos: int
    pedidos_finalizados: int
    pedidos_cancelados: int
    taxa_conversao: float
    taxa_cancelamento: float
    receita_total: float
    ticket_medio: float


class DashboardComercialResponse(BaseModel):
    indicadores: IndicadoresResponse
    faturamento_periodo: list[FaturamentoItem]
    ranking_clientes: list[ClienteRankingItem]
    ticket_medio: float
    total_clientes_ativos: int
