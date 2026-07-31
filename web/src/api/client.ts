const BASE_URL = '/api/v1'
const TOKEN_KEY = 'smartbcchopp_access_token'

export interface LoginResponse {
  access_token: string
  refresh_token: string
  username: string
  email: string
  papel: string
}

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token)
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY)
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken()
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> | undefined),
  }
  if (token) headers['Authorization'] = `Bearer ${token}`

  const res = await fetch(`${BASE_URL}${path}`, { ...options, headers })

  if (res.status === 401) {
    clearToken()
    throw new Error('Sessão expirada. Faça login novamente.')
  }
  if (!res.ok) {
    let detail = `Erro ${res.status}`
    try {
      const body = await res.json()
      if (body?.detail) detail = body.detail
    } catch {
      /* resposta sem JSON */
    }
    throw new Error(detail)
  }
  return res.json() as Promise<T>
}

export async function login(username: string, password: string): Promise<LoginResponse> {
  return request<LoginResponse>('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  })
}

export async function logout(): Promise<void> {
  try {
    await request('/auth/logout', { method: 'POST' })
  } finally {
    clearToken()
  }
}

export interface DashboardData {
  cards: {
    clientes_ativos: number
    veiculos_ativos: number
    chopeiras_instaladas: number
    faturamento_mes: number
    ticket_medio: number
    alertas_pendentes: number
  }
  clientes: {
    total: number
    ativos: number
    inativos: number
    novos_mes: number
  }
  veiculos: {
    total: number
    ativos: number
    em_manutencao: number
    proxima_troca_oleo: number
  }
  chopeiras: {
    total: number
    instaladas: number
    disponiveis: number
    em_manutencao: number
    manutencao_pendente: number
  }
  financeiro: {
    total_a_receber: number
    total_a_pagar: number
    saldo_previsto: number
    contas_receber_vencidas: number
    contas_pagar_vencidas: number
    recebido_mes: number
    pago_mes: number
  }
  estoque: {
    total_produtos: number
    total_itens_estoque: number
    estoque_baixo: number
  }
  alertas: Array<{
    id: string
    tipo: string
    nivel: string
    titulo: string
    mensagem: string | null
    lido: boolean
    created_at: string | null
  }>
  faturamento_mensal: Array<{
    mes: string
    receita: number
    qtd_pedidos: number
  }>
  pedidos_por_status: Record<string, number>
}

export function fetchDashboard(): Promise<DashboardData> {
  return request<DashboardData>('/dashboard/master')
}

export function toNumber(v: unknown): number {
  return typeof v === 'number' ? v : Number(v ?? 0)
}

// ── Clientes ────────────────────────────────────────────────

export interface Cliente {
  id: string
  tipo_pessoa: 'PF' | 'PJ'
  nome_razao_social: string
  nome_fantasia: string | null
  cpf_cnpj: string
  rg_ie: string | null
  email: string | null
  telefone: string | null
  celular: string | null
  limite_credito: number
  saldo_disponivel: number
  status: 'ativo' | 'inativo' | 'bloqueado'
  created_at: string
  updated_at: string
}

export interface ListResponse<T> {
  items: T[]
  total: number
}

export function listClientes(search?: string): Promise<ListResponse<Cliente>> {
  const q = search ? `?search=${encodeURIComponent(search)}` : ''
  return request(`/customers/${q}`)
}

export function createCliente(body: Partial<Cliente>): Promise<Cliente> {
  return request('/customers/', { method: 'POST', body: JSON.stringify(body) })
}

export function updateCliente(id: string, body: Partial<Cliente>): Promise<Cliente> {
  return request(`/customers/${id}`, { method: 'PUT', body: JSON.stringify(body) })
}

export function deleteCliente(id: string): Promise<void> {
  return request(`/customers/${id}`, { method: 'DELETE' })
}

// ── Produtos ────────────────────────────────────────────────

export interface Produto {
  id: string
  codigo: string
  nome: string
  categoria: 'chope' | 'carvao' | 'transporte'
  unidade_medida: 'L' | 'KG' | 'UN' | 'PCT' | 'SACO'
  preco_venda: number
  preco_custo: number | null
  codigo_barras: string | null
  estoque_minimo: number
  lote_obrigatorio: boolean
  ncm: string | null
  familia_id: string | null
  ativo: boolean
  created_at: string
  updated_at: string
}

export function listProducts(categoria?: string, search?: string): Promise<ListResponse<Produto>> {
  const params = new URLSearchParams()
  if (categoria) params.set('categoria', categoria)
  if (search) params.set('search', search)
  const qs = params.toString()
  return request(`/products/${qs ? `?${qs}` : ''}`)
}

export function createProduct(body: Partial<Produto>): Promise<Produto> {
  return request('/products/', { method: 'POST', body: JSON.stringify(body) })
}

export function updateProduct(id: string, body: Partial<Produto>): Promise<Produto> {
  return request(`/products/${id}`, { method: 'PUT', body: JSON.stringify(body) })
}

export function deleteProduct(id: string): Promise<void> {
  return request(`/products/${id}`, { method: 'DELETE' })
}

// ── Veículos (Fleet) ────────────────────────────────────────

export interface Veiculo {
  id: string
  placa: string
  marca: string
  modelo: string
  tipo: 'caminhao' | 'van' | 'carro' | 'utilitario'
  proprietario: 'proprio' | 'terceiro'
  renavam: string | null
  chassi: string | null
  ano_fabricacao: number | null
  ano_modelo: number | null
  cor: string | null
  categoria: 'leve' | 'medio' | 'pesado' | null
  capacidade_carga_kg: number | null
  capacidade_volume_m3: number | null
  consumo_medio_km_l: number | null
  tanque_capacidade_l: number | null
  tipo_carroceria: 'bau' | 'graneleiro' | 'tanque' | 'sider' | 'aberta' | null
  km_atual: number
  km_proxima_troca_oleo: number | null
  status: 'disponivel' | 'em_rota' | 'manutencao' | 'inativo'
  terceiro_nome: string | null
  terceiro_cpf_cnpj: string | null
  data_aquisicao: string | null
  data_vencimento_seguro: string | null
  ativo: boolean
  created_at: string
  updated_at: string
}

export function listVeiculos(search?: string): Promise<ListResponse<Veiculo>> {
  const q = search ? `?search=${encodeURIComponent(search)}` : ''
  return request(`/fleet/vehicles${q}`)
}

export function createVeiculo(body: Partial<Veiculo>): Promise<Veiculo> {
  return request('/fleet/vehicles', { method: 'POST', body: JSON.stringify(body) })
}

export function updateVeiculo(id: string, body: Partial<Veiculo>): Promise<Veiculo> {
  return request(`/fleet/vehicles/${id}`, { method: 'PUT', body: JSON.stringify(body) })
}

export function deleteVeiculo(id: string): Promise<void> {
  return request(`/fleet/vehicles/${id}`, { method: 'DELETE' })
}

// ── Chopeiras ───────────────────────────────────────────────

export interface Chopeira {
  id: string
  codigo_identificacao: string
  numero_serie: string | null
  marca: string
  modelo: string
  tipo: string
  capacidade_l: number | null
  status: 'disponivel' | 'instalada' | 'manutencao' | 'baixada'
  ativo: boolean
  data_instalacao: string | null
  data_ultima_manutencao: string | null
  data_proxima_manutencao: string | null
  local_instalacao: string | null
  latitude: number | null
  longitude: number | null
  observacao: string | null
  cliente_id: string | null
}

export function listChopeiras(search?: string): Promise<ListResponse<Chopeira>> {
  const q = search ? `?search=${encodeURIComponent(search)}` : ''
  return request(`/chopeiras/${q}`)
}

export function createChopeira(body: Partial<Chopeira>): Promise<Chopeira> {
  return request('/chopeiras/', { method: 'POST', body: JSON.stringify(body) })
}

export function updateChopeira(id: string, body: Partial<Chopeira>): Promise<Chopeira> {
  return request(`/chopeiras/${id}`, { method: 'PUT', body: JSON.stringify(body) })
}

export function deleteChopeira(id: string): Promise<void> {
  return request(`/chopeiras/${id}`, { method: 'DELETE' })
}

export function instalarChopeira(
  id: string,
  body: { cliente_id: string; data_instalacao?: string; local_instalacao?: string; observacao?: string },
): Promise<Chopeira> {
  return request(`/chopeiras/${id}/install`, { method: 'POST', body: JSON.stringify(body) })
}

export function desinstalarChopeira(id: string): Promise<Chopeira> {
  return request(`/chopeiras/${id}/uninstall`, { method: 'POST' })
}

// ── Financeiro ──────────────────────────────────────────────

export interface ContaReceber {
  id: string
  parcela: number
  numero_documento: string
  data_emissao: string
  data_vencimento: string
  data_pagamento: string | null
  valor_original: number
  valor_pago: number
  desconto: number
  juros: number
  multa: number
  saldo: number
  status: 'aberto' | 'parcial' | 'pago' | 'atrasado' | 'cancelado'
  forma_pagamento: string | null
  cliente_id: string
  pedido_id: string | null
  created_at: string
  updated_at: string
}

export interface ContaPagar {
  id: string
  parcela: number
  numero_documento: string
  data_emissao: string
  data_vencimento: string
  data_pagamento: string | null
  valor_original: number
  valor_pago: number
  desconto: number
  juros: number
  multa: number
  saldo: number
  status: 'aberto' | 'parcial' | 'pago' | 'atrasado' | 'cancelado'
  categoria: string | null
  fornecedor_id: string | null
  pedido_compra_id: string | null
  created_at: string
  updated_at: string
}

export interface Lancamento {
  id: string
  data: string
  tipo: 'entrada' | 'saida'
  valor: number
  categoria: string
  descricao: string
  conciliado: boolean
  data_conciliacao: string | null
  created_at: string
}

export function listContasReceber(status?: string): Promise<ListResponse<ContaReceber>> {
  const q = status ? `?status=${encodeURIComponent(status)}` : ''
  return request(`/financial/receber${q}`)
}

export function createContaReceber(body: {
  cliente_id: string
  data_vencimento: string
  valor_original: number
  numero_documento?: string
  data_emissao?: string
  parcela?: number
}): Promise<ContaReceber> {
  return request('/financial/receber', { method: 'POST', body: JSON.stringify(body) })
}

export function baixarContaReceber(
  id: string,
  body: { valor_pago: number; data_pagamento?: string; forma_pagamento?: string; observacao?: string },
): Promise<ContaReceber> {
  return request(`/financial/receber/${id}/receber`, { method: 'POST', body: JSON.stringify(body) })
}

export function cancelarContaReceber(id: string): Promise<void> {
  return request(`/financial/receber/${id}`, { method: 'DELETE' })
}

export function listContasPagar(status?: string): Promise<ListResponse<ContaPagar>> {
  const q = status ? `?status=${encodeURIComponent(status)}` : ''
  return request(`/financial/pagar${q}`)
}

export function createContaPagar(body: {
  fornecedor_id?: string
  data_vencimento: string
  valor_original: number
  numero_documento?: string
  data_emissao?: string
  parcela?: number
  categoria?: string
}): Promise<ContaPagar> {
  return request('/financial/pagar', { method: 'POST', body: JSON.stringify(body) })
}

export function baixarContaPagar(
  id: string,
  body: { valor_pago: number; data_pagamento?: string; observacao?: string },
): Promise<ContaPagar> {
  return request(`/financial/pagar/${id}/pagar`, { method: 'POST', body: JSON.stringify(body) })
}

export function cancelarContaPagar(id: string): Promise<void> {
  return request(`/financial/pagar/${id}`, { method: 'DELETE' })
}

export function listLancamentos(): Promise<{ items: Lancamento[]; total: number; saldo_periodo: number }> {
  return request('/financial/fluxo-caixa')
}

export function createLancamento(body: {
  tipo: 'entrada' | 'saida'
  valor: number
  categoria: string
  descricao: string
  data?: string
}): Promise<Lancamento> {
  return request('/financial/fluxo-caixa', { method: 'POST', body: JSON.stringify(body) })
}

// ── Estoque ─────────────────────────────────────────────────

export interface Deposito {
  id: string
  codigo: string
  nome: string
  tipo: string | null
  ativo: boolean
}

export interface ItemEstoque {
  id: string
  produto_id: string
  deposito_id: string
  lote_id: string | null
  quantidade_atual: number
  quantidade_reservada: number
  localizacao: string | null
}

export interface Movimentacao {
  id: string
  tipo: 'entrada' | 'saida' | 'transferencia' | 'perda' | 'ajuste'
  quantidade: number
  observacao: string | null
  produto_id: string
  deposito_id_origem: string
  deposito_id_destino: string | null
  lote_id: string | null
  created_at: string
}

export function listStock(): Promise<ListResponse<ItemEstoque>> {
  return request('/inventory/stock')
}

export function listDepositos(): Promise<Deposito[]> {
  return request('/inventory/depositos')
}

export function listMovements(): Promise<ListResponse<Movimentacao>> {
  return request('/inventory/movements')
}

export function createEntry(body: {
  produto_id: string
  deposito_id: string
  quantidade: number
  observacao?: string
}): Promise<Movimentacao> {
  return request('/inventory/entries', { method: 'POST', body: JSON.stringify(body) })
}

export function createExit(body: {
  produto_id: string
  deposito_id: string
  quantidade: number
  observacao?: string
}): Promise<Movimentacao> {
  return request('/inventory/exits', { method: 'POST', body: JSON.stringify(body) })
}

export function createAdjustment(body: {
  produto_id: string
  deposito_id: string
  quantidade_nova: number
  observacao?: string
}): Promise<Movimentacao> {
  return request('/inventory/adjustments', { method: 'POST', body: JSON.stringify(body) })
}

export function createTransfer(body: {
  produto_id: string
  deposito_id_origem: string
  deposito_id_destino: string
  quantidade: number
  observacao?: string
}): Promise<Movimentacao> {
  return request('/inventory/transfers', { method: 'POST', body: JSON.stringify(body) })
}

export interface InventarioContagem {
  id: string
  status: string
  data_contagem: string
  produto_id: string
  deposito_id: string
  quantidade_sistema: number
  quantidade_contada: number
  diferenca: number
  observacao: string | null
  created_at: string
}

export function listInventoryCounts(): Promise<ListResponse<InventarioContagem>> {
  return request('/inventory/inventory-count')
}

export function createInventoryCount(body: {
  produto_id: string
  deposito_id: string
  quantidade_contada: number
  observacao?: string
}): Promise<InventarioContagem> {
  return request('/inventory/inventory-count', { method: 'POST', body: JSON.stringify(body) })
}

export function closeInventoryCount(id: string): Promise<InventarioContagem> {
  return request(`/inventory/inventory-count/${id}/close`, { method: 'POST' })
}

export function listLowStock(): Promise<
  Array<{
    produto_id: string
    produto_codigo: string
    produto_nome: string
    deposito_nome: string
    quantidade_atual: number
    estoque_minimo: number
  }>
> {
  return request('/inventory/reports/low-stock')
}

// ── Comercial ───────────────────────────────────────────────

export interface Meta {
  id: string
  descricao: string
  periodo_inicio: string
  periodo_fim: string
  valor_meta: number
  valor_realizado: number
  comissao_percentual: number
  status: 'aberta' | 'atingida' | 'nao_atingida' | 'cancelada'
  vendedor_id: string | null
  created_at: string
  updated_at: string
}

export function listMetas(): Promise<ListResponse<Meta>> {
  return request('/commercial/metas')
}

export function createMeta(body: {
  descricao: string
  periodo_inicio: string
  periodo_fim: string
  valor_meta: number
  comissao_percentual?: number
  vendedor_id?: string
}): Promise<Meta> {
  return request('/commercial/metas', { method: 'POST', body: JSON.stringify(body) })
}

export function updateMeta(id: string, body: Partial<Meta>): Promise<Meta> {
  return request(`/commercial/metas/${id}`, { method: 'PUT', body: JSON.stringify(body) })
}

export function deleteMeta(id: string): Promise<void> {
  return request(`/commercial/metas/${id}`, { method: 'DELETE' })
}

// ── Alertas ─────────────────────────────────────────────────

export interface Alerta {
  id: string
  tipo: string
  nivel: 'info' | 'aviso' | 'critico'
  titulo: string
  mensagem: string | null
  lido: boolean
  created_at: string | null
}

export function listAlertas(): Promise<Alerta[]> {
  return request('/automation/alertas')
}

export function marcarAlertaLido(id: string): Promise<{ status: string }> {
  return request(`/automation/alertas/${id}/ler`, { method: 'PATCH' })
}

// ── Relatórios ──────────────────────────────────────────────

export interface DocumentoVencendo {
  veiculo_id: string
  placa: string
  tipo_documento: string
  data_vencimento: string
  dias_para_vencer: number
}

export function listDocumentosVencendo(dias = 30): Promise<DocumentoVencendo[]> {
  return request(`/fleet/reports/expiring-documents?dias=${dias}`)
}

export function relatorioFluxoCaixa(
  data_inicio: string,
  data_fim: string,
): Promise<{
  items: Array<{ data: string; entradas: number; saidas: number; saldo_dia: number; saldo_acumulado: number }>
  total_entradas: number
  total_saidas: number
  saldo_final: number
}> {
  return request(`/financial/relatorios/fluxo-caixa?data_inicio=${data_inicio}&data_fim=${data_fim}`)
}

export interface ItemInadimplencia {
  conta_id: string
  cliente_nome: string
  documento: string
  data_vencimento: string
  dias_atraso: number
  faixa: string
  saldo: number
}

export function listInadimplencia(): Promise<{ items: ItemInadimplencia[]; total_geral: number; quantidade_total: number }> {
  return request('/financial/inadimplencia')
}

// ── Fornecedores ─────────────────────────────────────────────

export interface Fornecedor {
  id: string
  nome_razao_social: string
  cpf_cnpj: string
  categoria: string
  tipo_pessoa: string
  nome_fantasia: string | null
  email: string | null
  telefone: string | null
  contato_nome: string | null
  status: string
  created_at: string
  updated_at: string
}

export function listFornecedores(categoria?: string): Promise<ListResponse<Fornecedor>> {
  const q = categoria ? `?categoria=${encodeURIComponent(categoria)}` : ''
  return request(`/suppliers/${q}`)
}

export function createFornecedor(body: {
  nome_razao_social: string
  cpf_cnpj: string
  categoria: string
  tipo_pessoa: string
  nome_fantasia?: string | null
  email?: string | null
  telefone?: string | null
  contato_nome?: string | null
}): Promise<Fornecedor> {
  return request('/suppliers/', { method: 'POST', body: JSON.stringify(body) })
}

export function updateFornecedor(id: string, body: {
  nome_razao_social?: string
  email?: string | null
  telefone?: string | null
  contato_nome?: string | null
  status?: string
}): Promise<Fornecedor> {
  return request(`/suppliers/${id}`, { method: 'PUT', body: JSON.stringify(body) })
}

export function deleteFornecedor(id: string): Promise<void> {
  return request(`/suppliers/${id}`, { method: 'DELETE' })
}

// ── Auditoria ────────────────────────────────────────────────

export interface AuditoriaEvento {
  id: string
  usuario_id: string | null
  acao: string
  entidade_tipo: string
  entidade_id: string | null
  dados_anteriores: Record<string, unknown> | null
  dados_novos: Record<string, unknown> | null
  created_at: string
}

export function listAuditoria(entidadeTipo?: string): Promise<ListResponse<AuditoriaEvento>> {
  const q = entidadeTipo ? `?entidade_tipo=${encodeURIComponent(entidadeTipo)}` : ''
  return request(`/auditoria/${q}`)
}
