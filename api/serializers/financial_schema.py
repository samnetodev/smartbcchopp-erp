from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

# ─── Dashboard ─────────────────────────────────────────────────────────────────


class FinancialDashboardResponse(BaseModel):
    total_a_receber: float
    total_a_pagar: float
    saldo_previsto: float
    contas_receber_vencidas: float
    contas_pagar_vencidas: float
    total_recebido_mes: float
    total_pago_mes: float
    saldo_disponivel: float


# ─── Conta a Receber ──────────────────────────────────────────────────────────


class ContaReceberCreate(BaseModel):
    cliente_id: UUID
    pedido_id: UUID | None = None
    numero_documento: str = Field(default="", max_length=50)
    data_emissao: date = Field(default_factory=date.today)
    data_vencimento: date
    valor_original: Decimal = Field(gt=0)
    parcela: int = 1
    observacao: str | None = None


class ContaReceberUpdate(BaseModel):
    data_vencimento: date | None = None
    valor_original: Decimal | None = Field(None, gt=0)
    status: str | None = Field(None, pattern="^(aberto|parcial|pago|atrasado|cancelado)$")
    observacao: str | None = None


class ContaReceberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    parcela: int
    numero_documento: str
    data_emissao: date
    data_vencimento: date
    data_pagamento: date | None = None
    valor_original: Decimal
    valor_pago: Decimal
    desconto: Decimal
    juros: Decimal
    multa: Decimal
    saldo: Decimal
    status: str
    forma_pagamento: str | None = None
    nosso_numero: str | None = None
    pix_charge_id: str | None = None
    cliente_id: UUID
    pedido_id: UUID | None = None
    created_at: datetime
    updated_at: datetime


class ContaReceberListResponse(BaseModel):
    items: list[ContaReceberResponse]
    total: int


# ─── Baixa / Recebimento ──────────────────────────────────────────────────────


class ReceberBaixaInput(BaseModel):
    data_pagamento: date = Field(default_factory=date.today)
    valor_pago: Decimal = Field(gt=0)
    desconto: Decimal = Decimal("0")
    juros: Decimal = Decimal("0")
    multa: Decimal = Decimal("0")
    forma_pagamento: str | None = Field(
        None, pattern="^(boleto|pix|credito|debito|dinheiro|cheque)$"
    )
    observacao: str | None = None


class PagarBaixaInput(BaseModel):
    data_pagamento: date = Field(default_factory=date.today)
    valor_pago: Decimal = Field(gt=0)
    desconto: Decimal = Decimal("0")
    juros: Decimal = Decimal("0")
    multa: Decimal = Decimal("0")
    observacao: str | None = None


class BaixaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tipo: str
    data_baixa: date
    valor: Decimal
    forma_pagamento: str | None = None
    observacao: str | None = None
    conta_receber_id: UUID | None = None
    conta_pagar_id: UUID | None = None


# ─── Conta a Pagar ────────────────────────────────────────────────────────────


class ContaPagarCreate(BaseModel):
    fornecedor_id: UUID | None = None
    pedido_compra_id: UUID | None = None
    numero_documento: str = Field(default="", max_length=50)
    data_emissao: date = Field(default_factory=date.today)
    data_vencimento: date
    valor_original: Decimal = Field(gt=0)
    parcela: int = 1
    categoria: str | None = Field(None, max_length=50)
    observacao: str | None = None


class ContaPagarUpdate(BaseModel):
    data_vencimento: date | None = None
    valor_original: Decimal | None = Field(None, gt=0)
    status: str | None = Field(None, pattern="^(aberto|parcial|pago|atrasado|cancelado)$")
    categoria: str | None = None
    observacao: str | None = None


class ContaPagarResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    parcela: int
    numero_documento: str
    data_emissao: date
    data_vencimento: date
    data_pagamento: date | None = None
    valor_original: Decimal
    valor_pago: Decimal
    desconto: Decimal
    juros: Decimal
    multa: Decimal
    saldo: Decimal
    status: str
    categoria: str | None = None
    fornecedor_id: UUID | None = None
    pedido_compra_id: UUID | None = None
    created_at: datetime
    updated_at: datetime


class ContaPagarListResponse(BaseModel):
    items: list[ContaPagarResponse]
    total: int


# ─── Fluxo de Caixa / Lançamentos ─────────────────────────────────────────────


class LancamentoCreate(BaseModel):
    data: date = Field(default_factory=date.today)
    tipo: str = Field(pattern="^(entrada|saida)$")
    valor: Decimal = Field(gt=0)
    categoria: str = Field(max_length=50)
    descricao: str = Field(max_length=200)
    conciliado: bool = False


class LancamentoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    data: date
    tipo: str
    valor: Decimal
    categoria: str
    descricao: str
    conciliado: bool
    data_conciliacao: date | None = None
    created_at: datetime


class LancamentoListResponse(BaseModel):
    items: list[LancamentoResponse]
    total: int
    saldo_periodo: float


class FluxoCaixaProjecaoItem(BaseModel):
    periodo: str
    data_inicio: date
    data_fim: date
    entradas_previstas: float
    saidas_previstas: float
    saldo_previsto: float


class FluxoCaixaProjecaoResponse(BaseModel):
    items: list[FluxoCaixaProjecaoItem]
    saldo_atual: float


# ─── Boleto ───────────────────────────────────────────────────────────────────


class BoletoGerarInput(BaseModel):
    data_vencimento: date
    valor: Decimal | None = None


class BoletoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    nosso_numero: str
    linha_digitavel: str | None = None
    codigo_barras: str | None = None
    qr_code: str | None = None
    data_emissao: date
    data_vencimento: date
    data_pagamento: date | None = None
    valor_nominal: Decimal
    valor_pago: Decimal | None = None
    status: str
    arquivo_pdf: str | None = None
    conta_receber_id: UUID


class BoletoListResponse(BaseModel):
    items: list[BoletoResponse]
    total: int


# ─── PIX ──────────────────────────────────────────────────────────────────────


class PixGerarInput(BaseModel):
    valor: Decimal | None = None


class PixResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    txid: str
    charge_id: str | None = None
    payload_base64: str | None = None
    qr_code_url: str | None = None
    pix_copia_cola: str | None = None
    valor: Decimal
    status: str
    data_expiracao: datetime | None = None
    data_pagamento: datetime | None = None
    end_to_end_id: str | None = None
    conta_receber_id: UUID


class PixListResponse(BaseModel):
    items: list[PixResponse]
    total: int


# ─── Inadimplência ─────────────────────────────────────────────────────────────


class InadimplenciaItem(BaseModel):
    conta_id: UUID
    cliente_id: UUID
    cliente_nome: str
    documento: str
    data_vencimento: date
    dias_atraso: int
    faixa: str
    valor_original: Decimal
    saldo: Decimal


class InadimplenciaPorCliente(BaseModel):
    cliente_id: UUID
    cliente_nome: str
    total_vencido: Decimal
    quantidade: int
    dias_maior_atraso: int


class InadimplenciaResponse(BaseModel):
    items: list[InadimplenciaItem]
    total_geral: float
    quantidade_total: int


class InadimplenciaClientesResponse(BaseModel):
    items: list[InadimplenciaPorCliente]


# ─── Relatórios ───────────────────────────────────────────────────────────────


class RelatorioFluxoCaixaItem(BaseModel):
    data: date
    entradas: float
    saidas: float
    saldo_dia: float
    saldo_acumulado: float


class RelatorioFluxoCaixaResponse(BaseModel):
    items: list[RelatorioFluxoCaixaItem]
    total_entradas: float
    total_saidas: float
    saldo_final: float
    data_inicio: date
    data_fim: date


class RelatorioContasReceberResponse(BaseModel):
    items: list[ContaReceberResponse]
    total_previsto: float
    total_recebido: float
    total_vencido: float
    data_inicio: date
    data_fim: date


class RelatorioContasPagarResponse(BaseModel):
    items: list[ContaPagarResponse]
    total_previsto: float
    total_pago: float
    total_vencido: float
    data_inicio: date
    data_fim: date


class DreCategoriaItem(BaseModel):
    categoria: str
    receitas: float
    despesas: float
    saldo: float


class DreResponse(BaseModel):
    items: list[DreCategoriaItem]
    total_receitas: float
    total_despesas: float
    resultado: float
    data_inicio: date
    data_fim: date
