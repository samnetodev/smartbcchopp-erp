from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

# ─── Chopeira ──────────────────────────────────────────────────────────────────


class ChopeiraCreate(BaseModel):
    codigo_identificacao: str = Field(max_length=50)
    numero_serie: str | None = Field(None, max_length=50)
    marca: str = Field(max_length=50)
    modelo: str = Field(max_length=50)
    tipo: str
    capacidade_l: Decimal | None = None
    local_instalacao: str | None = Field(None, max_length=200)
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    observacao: str | None = None


class ChopeiraUpdate(BaseModel):
    codigo_identificacao: str | None = Field(None, max_length=50)
    numero_serie: str | None = Field(None, max_length=50)
    marca: str | None = Field(None, max_length=50)
    modelo: str | None = Field(None, max_length=50)
    tipo: str | None = None
    capacidade_l: Decimal | None = None
    status: str | None = None
    local_instalacao: str | None = Field(None, max_length=200)
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    observacao: str | None = None


class ChopeiraResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    codigo_identificacao: str
    numero_serie: str | None
    marca: str
    modelo: str
    tipo: str
    capacidade_l: Decimal | None
    status: str
    ativo: bool
    data_instalacao: date | None
    data_ultima_manutencao: date | None
    data_proxima_manutencao: date | None
    local_instalacao: str | None
    latitude: Decimal | None
    longitude: Decimal | None
    observacao: str | None
    cliente_id: UUID | None


class ChopeiraListResponse(BaseModel):
    items: list[ChopeiraResponse]
    total: int


class InstallChopeiraInput(BaseModel):
    cliente_id: UUID
    data_instalacao: date | None = None
    local_instalacao: str | None = Field(None, max_length=200)
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    observacao: str | None = None


# ─── Manutenção ────────────────────────────────────────────────────────────────


class ManutencaoCreate(BaseModel):
    tipo: str
    data_solicitacao: date
    data_inicio: date | None = None
    data_fim: date | None = None
    descricao_problema: str | None = None
    descricao_servico: str | None = None
    tecnico_responsavel: str | None = Field(None, max_length=100)
    custo_pecas: Decimal = Field(default=Decimal("0"), ge=0)
    custo_servico: Decimal = Field(default=Decimal("0"), ge=0)


class ManutencaoUpdate(BaseModel):
    tipo: str | None = None
    status: str | None = None
    data_inicio: date | None = None
    data_fim: date | None = None
    descricao_problema: str | None = None
    descricao_servico: str | None = None
    tecnico_responsavel: str | None = Field(None, max_length=100)
    custo_pecas: Decimal | None = Field(None, ge=0)
    custo_servico: Decimal | None = Field(None, ge=0)


class ManutencaoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tipo: str
    status: str
    data_solicitacao: date
    data_inicio: date | None
    data_fim: date | None
    descricao_problema: str | None
    descricao_servico: str | None
    tecnico_responsavel: str | None
    custo_pecas: Decimal
    custo_servico: Decimal
    custo_total: Decimal
    chopeira_id: UUID


class ManutencaoListResponse(BaseModel):
    items: list[ManutencaoResponse]
    total: int


# ─── Histórico ─────────────────────────────────────────────────────────────────


class HistoricoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    evento: str
    data_evento: date
    descricao: str | None
    detalhes: str | None
    chopeira_id: UUID
    cliente_id: UUID | None
    usuario_id: UUID | None


class HistoricoListResponse(BaseModel):
    items: list[HistoricoResponse]
    total: int


# ─── Disponibilidade / Relatórios ──────────────────────────────────────────────


class StatusCount(BaseModel):
    status: str
    total: int


class ChopeiraMaintenanceDueItem(BaseModel):
    id: UUID
    codigo_identificacao: str
    marca: str
    modelo: str
    data_proxima_manutencao: date
    cliente_nome: str | None
    dias_para_vencer: int


class ChopeiraMaintenanceDueList(BaseModel):
    items: list[ChopeiraMaintenanceDueItem]
