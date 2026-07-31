import { useCallback, useEffect, useState } from 'react'
import {
  relatorioFluxoCaixa, listInadimplencia, listLowStock, listDocumentosVencendo,
  ItemInadimplencia, DocumentoVencendo,
} from '../api/client'
import { Button, Spinner, EmptyState, PageHeader, Card, Th, Td, inputCls, ErrorNotice } from '../components/ui'
import { fmtBRL, fmtDate } from '../lib/format'

type Relatorio = 'fluxo-caixa' | 'inadimplencia' | 'estoque-baixo' | 'documentos'

export default function Relatorios() {
  const [tipo, setTipo] = useState<Relatorio>('fluxo-caixa')
  const today = new Date()
  const firstOfMonth = new Date(today.getFullYear(), today.getMonth(), 1)
  const [dataInicio, setDataInicio] = useState(firstOfMonth.toISOString().slice(0, 10))
  const [dataFim, setDataFim] = useState(today.toISOString().slice(0, 10))

  const [fluxo, setFluxo] = useState<{ items: Array<{ data: string; entradas: number; saidas: number; saldo_dia: number; saldo_acumulado: number }>; total_entradas: number; total_saidas: number; saldo_final: number } | null>(null)
  const [inadimplencia, setInadimplencia] = useState<{ items: ItemInadimplencia[]; total_geral: number } | null>(null)
  const [lowStock, setLowStock] = useState<Array<{ produto_codigo: string; produto_nome: string; deposito_nome: string; quantidade_atual: number; estoque_minimo: number }>>([])
  const [documentos, setDocumentos] = useState<DocumentoVencendo[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      if (tipo === 'fluxo-caixa') setFluxo(await relatorioFluxoCaixa(dataInicio, dataFim))
      else if (tipo === 'inadimplencia') setInadimplencia(await listInadimplencia())
      else if (tipo === 'estoque-baixo') setLowStock(await listLowStock())
      else setDocumentos(await listDocumentosVencendo(30))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao carregar relatório')
    } finally {
      setLoading(false)
    }
  }, [tipo, dataInicio, dataFim])

  useEffect(() => {
    load()
  }, [load])

  const tabs: Array<{ id: Relatorio; label: string }> = [
    { id: 'fluxo-caixa', label: 'Fluxo de Caixa' },
    { id: 'inadimplencia', label: 'Inadimplência' },
    { id: 'estoque-baixo', label: 'Estoque Baixo' },
    { id: 'documentos', label: 'Documentos Vencendo' },
  ]

  return (
    <div>
      <PageHeader title="Relatórios" />

      <div className="flex flex-wrap items-center gap-3 mb-4">
        <div className="flex gap-1 bg-gray-100 p-1 rounded-lg">
          {tabs.map((t) => (
            <button
              key={t.id}
              onClick={() => setTipo(t.id)}
              className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors cursor-pointer ${
                tipo === t.id ? 'bg-white shadow-sm text-gray-900' : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>

        {tipo === 'fluxo-caixa' && (
          <div className="flex items-center gap-2 ml-auto">
            <input type="date" value={dataInicio} onChange={(e) => setDataInicio(e.target.value)} className={inputCls + ' w-auto'} />
            <span className="text-sm text-gray-400">até</span>
            <input type="date" value={dataFim} onChange={(e) => setDataFim(e.target.value)} className={inputCls + ' w-auto'} />
            <Button onClick={load}>Gerar</Button>
          </div>
        )}
      </div>

      {error && <div className="mb-4"><ErrorNotice message={error} /></div>}

      <Card>
        {loading ? (
          <Spinner />
        ) : tipo === 'fluxo-caixa' ? (
          !fluxo || fluxo.items.length === 0 ? (
            <EmptyState message="Sem movimentações no período" />
          ) : (
            <div>
              <div className="flex flex-wrap gap-4 px-4 py-3 border-b border-gray-100 bg-gray-50/50 text-sm">
                <p>Entradas: <span className="font-semibold text-emerald-600">{fmtBRL(fluxo.total_entradas)}</span></p>
                <p>Saídas: <span className="font-semibold text-rose-600">{fmtBRL(fluxo.total_saidas)}</span></p>
                <p>Saldo final: <span className={`font-semibold ${fluxo.saldo_final >= 0 ? 'text-emerald-600' : 'text-rose-600'}`}>{fmtBRL(fluxo.saldo_final)}</span></p>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50 border-b border-gray-100">
                    <tr>
                      <Th>Data</Th>
                      <Th>Entradas</Th>
                      <Th>Saídas</Th>
                      <Th>Saldo do dia</Th>
                      <Th>Saldo acumulado</Th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-50">
                    {fluxo.items.map((i) => (
                      <tr key={i.data} className="hover:bg-gray-50/50">
                        <Td>{fmtDate(i.data)}</Td>
                        <Td className="text-emerald-600">{fmtBRL(i.entradas)}</Td>
                        <Td className="text-rose-600">{fmtBRL(i.saidas)}</Td>
                        <Td>{fmtBRL(i.saldo_dia)}</Td>
                        <Td className="font-medium">{fmtBRL(i.saldo_acumulado)}</Td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )
        ) : tipo === 'inadimplencia' ? (
          !inadimplencia || inadimplencia.items.length === 0 ? (
            <EmptyState message="Nenhuma conta vencida" />
          ) : (
            <div>
              <div className="px-4 py-3 border-b border-gray-100 bg-gray-50/50 text-sm">
                Total vencido: <span className="font-semibold text-rose-600">{fmtBRL(inadimplencia.total_geral)}</span>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50 border-b border-gray-100">
                    <tr>
                      <Th>Cliente</Th>
                      <Th>Documento</Th>
                      <Th>Vencimento</Th>
                      <Th>Dias em atraso</Th>
                      <Th>Faixa</Th>
                      <Th>Saldo</Th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-50">
                    {inadimplencia.items.map((i) => (
                      <tr key={i.conta_id} className="hover:bg-gray-50/50">
                        <Td className="font-medium text-gray-900">{i.cliente_nome}</Td>
                        <Td>{i.documento}</Td>
                        <Td>{fmtDate(i.data_vencimento)}</Td>
                        <Td>{i.dias_atraso} dias</Td>
                        <Td>{i.faixa}</Td>
                        <Td className="font-medium text-rose-600">{fmtBRL(i.saldo)}</Td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )
        ) : tipo === 'estoque-baixo' ? (
          lowStock.length === 0 ? (
            <EmptyState message="Nenhum item abaixo do estoque mínimo" />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-100">
                  <tr>
                    <Th>Código</Th>
                    <Th>Produto</Th>
                    <Th>Depósito</Th>
                    <Th>Qtd. atual</Th>
                    <Th>Mínimo</Th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-50">
                  {lowStock.map((i) => (
                    <tr key={i.produto_codigo} className="hover:bg-gray-50/50">
                      <Td>{i.produto_codigo}</Td>
                      <Td className="font-medium text-gray-900">{i.produto_nome}</Td>
                      <Td>{i.deposito_nome}</Td>
                      <Td>{Number(i.quantidade_atual).toLocaleString('pt-BR')}</Td>
                      <Td>{Number(i.estoque_minimo).toLocaleString('pt-BR')}</Td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )
        ) : documentos.length === 0 ? (
          <EmptyState message="Nenhum documento vencendo nos próximos 30 dias" />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-100">
                <tr>
                  <Th>Veículo</Th>
                  <Th>Documento</Th>
                  <Th>Vencimento</Th>
                  <Th>Dias restantes</Th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {documentos.map((d) => (
                  <tr key={d.veiculo_id + d.tipo_documento} className="hover:bg-gray-50/50">
                    <Td className="font-medium text-gray-900">{d.placa}</Td>
                    <Td>{d.tipo_documento}</Td>
                    <Td>{fmtDate(d.data_vencimento)}</Td>
                    <Td>{d.dias_para_vencer} dias</Td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  )
}
