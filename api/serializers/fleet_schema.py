from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

# ─── Veículo ──────────────────────────────────────────────────────────────────


class VehicleBase(BaseModel):
    placa: str = Field(max_length=7)
    marca: str = Field(max_length=50)
    modelo: str = Field(max_length=50)
    tipo: str
    proprietario: str


class VehicleCreate(VehicleBase):
    renavam: str | None = Field(None, max_length=20)
    chassi: str | None = Field(None, max_length=20)
    ano_fabricacao: int | None = None
    ano_modelo: int | None = None
    cor: str | None = Field(None, max_length=30)
    categoria: str | None = None
    capacidade_carga_kg: Decimal | None = None
    capacidade_volume_m3: Decimal | None = None
    tipo_carroceria: str | None = None
    consumo_medio_km_l: Decimal | None = None
    tanque_capacidade_l: Decimal | None = None
    km_atual: int = 0
    km_proxima_troca_oleo: int | None = None
    terceiro_nome: str | None = Field(None, max_length=200)
    terceiro_cpf_cnpj: str | None = Field(None, max_length=14)
    data_aquisicao: date | None = None
    data_vencimento_seguro: date | None = None


class VehicleUpdate(BaseModel):
    placa: str | None = Field(None, max_length=7)
    marca: str | None = Field(None, max_length=50)
    modelo: str | None = Field(None, max_length=50)
    tipo: str | None = None
    proprietario: str | None = None
    status: str | None = None
    renavam: str | None = Field(None, max_length=20)
    chassi: str | None = Field(None, max_length=20)
    ano_fabricacao: int | None = None
    ano_modelo: int | None = None
    cor: str | None = Field(None, max_length=30)
    categoria: str | None = None
    capacidade_carga_kg: Decimal | None = None
    capacidade_volume_m3: Decimal | None = None
    tipo_carroceria: str | None = None
    consumo_medio_km_l: Decimal | None = None
    tanque_capacidade_l: Decimal | None = None
    km_atual: int | None = None
    km_proxima_troca_oleo: int | None = None
    terceiro_nome: str | None = Field(None, max_length=200)
    terceiro_cpf_cnpj: str | None = Field(None, max_length=14)
    data_aquisicao: date | None = None
    data_vencimento_seguro: date | None = None


class VehicleResponse(VehicleBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    renavam: str | None = None
    chassi: str | None = None
    ano_fabricacao: int | None = None
    ano_modelo: int | None = None
    cor: str | None = None
    categoria: str | None = None
    capacidade_carga_kg: Decimal | None = None
    capacidade_volume_m3: Decimal | None = None
    tipo_carroceria: str | None = None
    consumo_medio_km_l: Decimal | None = None
    tanque_capacidade_l: Decimal | None = None
    km_atual: int = 0
    km_proxima_troca_oleo: int | None = None
    status: str = "disponivel"
    terceiro_nome: str | None = None
    terceiro_cpf_cnpj: str | None = None
    data_aquisicao: date | None = None
    data_vencimento_seguro: date | None = None
    ativo: bool = True
    created_at: datetime
    updated_at: datetime


class VehicleListResponse(BaseModel):
    items: list[VehicleResponse]
    total: int


class VehicleKmUpdate(BaseModel):
    km: int = Field(ge=0)
    data: date | None = None
    observacao: str | None = None


# ─── Motorista ────────────────────────────────────────────────────────────────


class DriverBase(BaseModel):
    numero_cnh: str = Field(max_length=20)
    categoria_cnh: str = Field(max_length=5)
    data_validade_cnh: date


class DriverCreate(DriverBase):
    funcionario_id: UUID
    data_primeira_cnh: date | None = None
    orgao_emissor_cnh: str | None = Field(None, max_length=50)
    cnh_observacao: str | None = Field(None, max_length=200)
    data_ultimo_exame_medico: date | None = None
    data_validade_exame_medico: date | None = None
    certificacoes: str | None = None
    telefone: str | None = Field(None, max_length=20)
    email: str | None = Field(None, max_length=255)


class DriverUpdate(BaseModel):
    numero_cnh: str | None = Field(None, max_length=20)
    categoria_cnh: str | None = Field(None, max_length=5)
    data_validade_cnh: date | None = None
    data_primeira_cnh: date | None = None
    orgao_emissor_cnh: str | None = Field(None, max_length=50)
    cnh_observacao: str | None = Field(None, max_length=200)
    data_ultimo_exame_medico: date | None = None
    data_validade_exame_medico: date | None = None
    certificacoes: str | None = None
    telefone: str | None = Field(None, max_length=20)
    email: str | None = Field(None, max_length=255)
    status: str | None = None


class DriverResponse(DriverBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    data_primeira_cnh: date | None = None
    orgao_emissor_cnh: str | None = None
    cnh_observacao: str | None = None
    data_ultimo_exame_medico: date | None = None
    data_validade_exame_medico: date | None = None
    certificacoes: str | None = None
    telefone: str | None = None
    email: str | None = None
    status: str = "disponivel"
    ativo: bool = True
    funcionario_id: UUID
    created_at: datetime
    updated_at: datetime


class DriverListResponse(BaseModel):
    items: list[DriverResponse]
    total: int


# ─── Seguro ───────────────────────────────────────────────────────────────────


class SeguroCreate(BaseModel):
    apolice: str = Field(max_length=30)
    seguradora: str
    data_inicio_vigencia: date
    data_fim_vigencia: date
    data_contratacao: date | None = None
    premio_total: Decimal = Field(ge=0)
    premio_parcela: Decimal | None = Field(None, ge=0)
    numero_parcelas: int | None = None
    coberturas: str | None = None
    valor_cobertura_terceiros: Decimal | None = Field(None, ge=0)
    valor_franquia: Decimal | None = Field(None, ge=0)
    observacao: str | None = None


class SeguroUpdate(BaseModel):
    apolice: str | None = Field(None, max_length=30)
    seguradora: str | None = None
    data_inicio_vigencia: date | None = None
    data_fim_vigencia: date | None = None
    premio_total: Decimal | None = Field(None, ge=0)
    premio_parcela: Decimal | None = Field(None, ge=0)
    numero_parcelas: int | None = None
    status: str | None = None
    coberturas: str | None = None
    valor_cobertura_terceiros: Decimal | None = Field(None, ge=0)
    valor_franquia: Decimal | None = Field(None, ge=0)
    observacao: str | None = None


class SeguroResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    apolice: str
    seguradora: str
    data_inicio_vigencia: date
    data_fim_vigencia: date
    data_contratacao: date | None = None
    premio_total: Decimal
    premio_parcela: Decimal | None = None
    numero_parcelas: int | None = None
    coberturas: str | None = None
    valor_cobertura_terceiros: Decimal | None = None
    valor_franquia: Decimal | None = None
    status: str
    ativo: bool = True
    observacao: str | None = None
    veiculo_id: UUID


class SeguroListResponse(BaseModel):
    items: list[SeguroResponse]
    total: int


# ─── Pneu ──────────────────────────────────────────────────────────────────────


class PneuCreate(BaseModel):
    posicao: str
    marca: str
    modelo: str = Field(max_length=50)
    medida: str = Field(max_length=20)
    numero_fogo: str | None = Field(None, max_length=30)
    km_instalacao: int = Field(ge=0)
    data_instalacao: date
    vida_util_km: int | None = None
    valor_unitario: Decimal | None = Field(None, ge=0)
    observacao: str | None = None


class PneuUpdate(BaseModel):
    posicao: str | None = None
    marca: str | None = None
    modelo: str | None = Field(None, max_length=50)
    km_troca: int | None = Field(None, ge=0)
    data_troca: date | None = None
    status: str | None = None
    vida_util_km: int | None = None
    observacao: str | None = None


class PneuResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    posicao: str
    marca: str
    modelo: str
    medida: str
    numero_fogo: str | None = None
    km_instalacao: int
    km_troca: int | None = None
    data_instalacao: date
    data_troca: date | None = None
    vida_util_km: int | None = None
    valor_unitario: Decimal | None = None
    status: str
    observacao: str | None = None
    veiculo_id: UUID


class PneuListResponse(BaseModel):
    items: list[PneuResponse]
    total: int


# ─── Troca de Óleo ────────────────────────────────────────────────────────────


class TrocaOleoCreate(BaseModel):
    data: date
    km_atual: int = Field(ge=0)
    tipo_oleo: str = Field(max_length=50)
    quantidade_l: Decimal = Field(gt=0)
    valor_oleo: Decimal = Field(ge=0)
    valor_filtro: Decimal = Field(default=Decimal("0"), ge=0)
    valor_servico: Decimal = Field(default=Decimal("0"), ge=0)
    valor_total: Decimal = Field(ge=0)
    oficina_nome: str | None = Field(None, max_length=100)
    km_proxima_troca: int | None = None
    observacao: str | None = None


class TrocaOleoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    data: date
    km_atual: int
    tipo_oleo: str
    quantidade_l: Decimal
    valor_oleo: Decimal
    valor_filtro: Decimal
    valor_servico: Decimal
    valor_total: Decimal
    oficina_nome: str | None = None
    km_proxima_troca: int | None = None
    observacao: str | None = None
    veiculo_id: UUID


class TrocaOleoListResponse(BaseModel):
    items: list[TrocaOleoResponse]
    total: int


# ─── KM Registro ──────────────────────────────────────────────────────────────


class KmRegistroCreate(BaseModel):
    data: date
    km: int = Field(ge=0)
    tipo: str = Field(default="leitura_manual", max_length=20)
    origem: str | None = Field(None, max_length=100)
    observacao: str | None = None


class KmRegistroResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    data: date
    km: int
    tipo: str
    origem: str | None = None
    observacao: str | None = None
    veiculo_id: UUID


class KmRegistroListResponse(BaseModel):
    items: list[KmRegistroResponse]
    total: int


# ─── Histórico ────────────────────────────────────────────────────────────────


class HistoricoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    evento: str
    data_evento: date
    descricao: str
    detalhes: str | None = None
    veiculo_id: UUID
    usuario_id: UUID | None = None


class HistoricoListResponse(BaseModel):
    items: list[HistoricoResponse]
    total: int


# ─── Custos (aggregated report) ──────────────────────────────────────────────


class CustoPeriodo(BaseModel):
    data_inicio: date
    data_fim: date


class CustoPorCategoria(BaseModel):
    categoria: str
    valor_total: Decimal
    quantidade: int


class CustoReportItem(BaseModel):
    veiculo_id: UUID
    placa: str
    total_combustivel: Decimal
    total_manutencao: Decimal
    total_multas: Decimal
    total_seguros: Decimal
    total_troca_oleo: Decimal
    total_geral: Decimal


class CustoReportResponse(BaseModel):
    items: list[CustoReportItem]
    total_geral: Decimal
    data_inicio: date
    data_fim: date


# ─── Expiring Documents Report ──────────────────────────────────────────────


class DocumentoVencendoItem(BaseModel):
    tipo: str
    descricao: str
    veiculo_id: UUID | None = None
    placa: str | None = None
    motorista_id: UUID | None = None
    motorista_nome: str | None = None
    data_vencimento: date
    dias_para_vencer: int
    status: str


class DocumentoVencendoList(BaseModel):
    items: list[DocumentoVencendoItem]
