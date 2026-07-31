import { useCallback, useEffect, useState } from 'react'
import {
  listContasReceber, createContaReceber, baixarContaReceber, cancelarContaReceber,
  listContasPagar, createContaPagar, baixarContaPagar, cancelarContaPagar,
  listLancamentos, createLancamento, listClientes, Cliente,
  ContaReceber, ContaPagar, Lancamento,
} from '../api/client'
import { Modal, Field, Button, Badge, Spinner, EmptyState, PageHeader, Card, Th, Td, inputCls, ErrorNotice } from '../components/ui'
import { fmtBRL, fmtDate } from '../lib/format'

type Tab = 'receber' | 'pagar' | 'lancamentos'

const contaStatusTone: Record<string, 'green' | 'red' | 'amber' | 'blue' | 'gray'> = {
  aberto: 'blue',
  parcial: 'amber',
  pago: 'green',
  atrasado: 'red',
  cancelado: 'gray',
}

export default function Financeiro() {
  const [tab, setTab] = useState<Tab>('receber')
  const [clientes, setClientes] = useState<Cliente[]>([])

  const [receber, setReceber] = useState<ContaReceber[]>([])
  const [pagar, setPagar] = useState<ContaPagar[]>([])
  const [lancamentos, setLancamentos] = useState<Lancamento[]>([])
  const [saldoPeriodo, setSaldoPeriodo] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [createOpen, setCreateOpen] = useState(false)
  const [form, setForm] = useState({ cliente_id: '', data_vencimento: '', valor_original: '', numero_documento: '', parcela: '1', categoria: '', descricao: '', tipo_lancamento: 'entrada' })
  const [createError, setCreateError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)

  const [baixaTarget, setBaixaTarget] = useState<ContaReceber | ContaPagar | null>(null)
  const [baixaForm, setBaixaForm] = useState({ valor_pago: '', data_pagamento: '', forma_pagamento: 'dinheiro' })

  const loadAll = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const [rec, pag, lanc, cli] = await Promise.all([listContasReceber(), listContasPagar(), listLancamentos(), listClientes()])
      setReceber(rec.items)
      setPagar(pag.items)
      setLancamentos(lanc.items)
      setSaldoPeriodo(lanc.saldo_periodo)
      setClientes(cli.items.filter((c) => c.status === 'ativo'))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao carregar financeiro')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadAll()
  }, [loadAll])

  const openNew = () => {
    setForm({ cliente_id: '', data_vencimento: '', valor_original: '', numero_documento: '', parcela: '1', categoria: '', descricao: '', tipo_lancamento: 'entrada' })
    setCreateError(null)
    setCreateOpen(true)
  }

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setCreateError(null)
    try {
      const valor = Number(form.valor_original) || 0
      if (tab === 'receber') {
        await createContaReceber({
          cliente_id: form.cliente_id,
          data_vencimento: form.data_vencimento,
          valor_original: valor,
          numero_documento: form.numero_documento || undefined,
          parcela: Number(form.parcela) || 1,
        })
      } else if (tab === 'pagar') {
        await createContaPagar({
          data_vencimento: form.data_vencimento,
          valor_original: valor,
          numero_documento: form.numero_documento || undefined,
          parcela: Number(form.parcela) || 1,
          categoria: form.categoria || undefined,
        })
      } else {
        await createLancamento({
          tipo: form.tipo_lancamento as 'entrada' | 'saida',
          valor,
          categoria: form.categoria,
          descricao: form.descricao,
        })
      }
      setCreateOpen(false)
      loadAll()
    } catch (err) {
      setCreateError(err instanceof Error ? err.message : 'Erro ao salvar')
    } finally {
      setSaving(false)
    }
  }

  const openBaixa = (c: ContaReceber | ContaPagar) => {
    setBaixaTarget(c)
    setBaixaForm({ valor_pago: String(c.saldo), data_pagamento: new Date().toISOString().slice(0, 10), forma_pagamento: 'dinheiro' })
  }

  const handleBaixa = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!baixaTarget) return
    setSaving(true)
    setError(null)
    try {
      const body = { valor_pago: Number(baixaForm.valor_pago) || 0, data_pagamento: baixaForm.data_pagamento || undefined }
      if ('cliente_id' in baixaTarget) {
        await baixarContaReceber(baixaTarget.id, { ...body, forma_pagamento: baixaForm.forma_pagamento })
      } else {
        await baixarContaPagar(baixaTarget.id, body)
      }
      setBaixaTarget(null)
      loadAll()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao registrar pagamento')
    } finally {
      setSaving(false)
    }
  }

  const handleCancel = async (c: ContaReceber | ContaPagar) => {
    if (!confirm('Cancelar esta conta?')) return
    try {
      if ('cliente_id' in c) await cancelarContaReceber(c.id)
      else await cancelarContaPagar(c.id)
      loadAll()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao cancelar')
    }
  }

  const tabs: Array<{ id: Tab; label: string }> = [
    { id: 'receber', label: 'A Receber' },
    { id: 'pagar', label: 'A Pagar' },
    { id: 'lancamentos', label: 'Lançamentos' },
  ]

  return (
    <div>
      <PageHeader
        title="Financeiro"
        action={<Button onClick={openNew}>+ Novo registro</Button>}
      />

      <div className="flex gap-1 mb-4 bg-gray-100 p-1 rounded-lg w-fit">
        {tabs.map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`px-4 py-1.5 rounded-md text-sm font-medium transition-colors cursor-pointer ${
              tab === t.id ? 'bg-white shadow-sm text-gray-900' : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {error && <div className="mb-4"><ErrorNotice message={error} /></div>}

      <Card>
        {loading ? (
          <Spinner />
        ) : tab === 'receber' ? (
          receber.length === 0 ? (
            <EmptyState message="Nenhuma conta a receber" />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-100">
                  <tr>
                    <Th>Doc</Th>
                    <Th>Vencimento</Th>
                    <Th>Valor</Th>
                    <Th>Pago</Th>
                    <Th>Saldo</Th>
                    <Th>Status</Th>
                    <Th />
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-50">
                  {receber.map((c) => (
                    <tr key={c.id} className="hover:bg-gray-50/50">
                      <Td>{c.numero_documento || '—'}</Td>
                      <Td>{fmtDate(c.data_vencimento)}</Td>
                      <Td>{fmtBRL(c.valor_original)}</Td>
                      <Td>{fmtBRL(c.valor_pago)}</Td>
                      <Td className="font-medium">{fmtBRL(c.saldo)}</Td>
                      <Td><Badge tone={contaStatusTone[c.status]}>{c.status}</Badge></Td>
                      <Td>
                        <div className="flex justify-end gap-1">
                          {c.status !== 'pago' && c.status !== 'cancelado' && (
                            <Button variant="outline" onClick={() => openBaixa(c)}>Receber</Button>
                          )}
                          <Button variant="danger" onClick={() => handleCancel(c)}>Cancelar</Button>
                        </div>
                      </Td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )
        ) : tab === 'pagar' ? (
          pagar.length === 0 ? (
            <EmptyState message="Nenhuma conta a pagar" />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-100">
                  <tr>
                    <Th>Doc</Th>
                    <Th>Vencimento</Th>
                    <Th>Categoria</Th>
                    <Th>Valor</Th>
                    <Th>Saldo</Th>
                    <Th>Status</Th>
                    <Th />
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-50">
                  {pagar.map((c) => (
                    <tr key={c.id} className="hover:bg-gray-50/50">
                      <Td>{c.numero_documento || '—'}</Td>
                      <Td>{fmtDate(c.data_vencimento)}</Td>
                      <Td>{c.categoria ?? '—'}</Td>
                      <Td>{fmtBRL(c.valor_original)}</Td>
                      <Td className="font-medium">{fmtBRL(c.saldo)}</Td>
                      <Td><Badge tone={contaStatusTone[c.status]}>{c.status}</Badge></Td>
                      <Td>
                        <div className="flex justify-end gap-1">
                          {c.status !== 'pago' && c.status !== 'cancelado' && (
                            <Button variant="outline" onClick={() => openBaixa(c)}>Pagar</Button>
                          )}
                          <Button variant="danger" onClick={() => handleCancel(c)}>Cancelar</Button>
                        </div>
                      </Td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )
        ) : lancamentos.length === 0 ? (
          <EmptyState message="Nenhum lançamento no período" />
        ) : (
          <div className="overflow-x-auto">
            <div className="flex justify-between items-center px-4 py-3 border-b border-gray-100 bg-gray-50/50">
              <p className="text-sm text-gray-600">Saldo do período</p>
              <p className={`text-sm font-semibold ${saldoPeriodo >= 0 ? 'text-emerald-600' : 'text-rose-600'}`}>
                {fmtBRL(saldoPeriodo)}
              </p>
            </div>
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-100">
                <tr>
                  <Th>Data</Th>
                  <Th>Descrição</Th>
                  <Th>Categoria</Th>
                  <Th>Tipo</Th>
                  <Th>Valor</Th>
                  <Th>Status</Th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {lancamentos.map((l) => (
                  <tr key={l.id} className="hover:bg-gray-50/50">
                    <Td>{fmtDate(l.data)}</Td>
                    <Td className="font-medium text-gray-900">{l.descricao}</Td>
                    <Td>{l.categoria}</Td>
                    <Td>
                      <Badge tone={l.tipo === 'entrada' ? 'green' : 'red'}>{l.tipo}</Badge>
                    </Td>
                    <Td className={l.tipo === 'entrada' ? 'text-emerald-600' : 'text-rose-600'}>
                      {l.tipo === 'entrada' ? '+' : '-'}{fmtBRL(l.valor)}
                    </Td>
                    <Td>
                      {l.conciliado ? <Badge tone="green">conciliado</Badge> : <Badge tone="gray">pendente</Badge>}
                    </Td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      {createOpen && (
        <Modal title={`Novo registro — ${tabs.find((t) => t.id === tab)?.label}`} onClose={() => setCreateOpen(false)}>
          <form onSubmit={handleCreate} className="space-y-4">
            {tab === 'receber' && (
              <Field label="Cliente" required>
                <select value={form.cliente_id} onChange={(e) => setForm((f) => ({ ...f, cliente_id: e.target.value }))} className={inputCls} required>
                  <option value="">Selecione...</option>
                  {clientes.map((c) => (
                    <option key={c.id} value={c.id}>{c.nome_razao_social}</option>
                  ))}
                </select>
              </Field>
            )}
            <div className="grid grid-cols-2 gap-3">
              <Field label="Vencimento" required>
                <input type="date" value={form.data_vencimento} onChange={(e) => setForm((f) => ({ ...f, data_vencimento: e.target.value }))} className={inputCls} required />
              </Field>
              <Field label="Valor (R$)" required>
                <input type="number" step="0.01" min="0" value={form.valor_original} onChange={(e) => setForm((f) => ({ ...f, valor_original: e.target.value }))} className={inputCls} required />
              </Field>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <Field label="Nº documento">
                <input value={form.numero_documento} onChange={(e) => setForm((f) => ({ ...f, numero_documento: e.target.value }))} className={inputCls} />
              </Field>
              {tab === 'receber' ? (
                <Field label="Parcela">
                  <input type="number" min="1" value={form.parcela} onChange={(e) => setForm((f) => ({ ...f, parcela: e.target.value }))} className={inputCls} />
                </Field>
              ) : (
                <Field label="Categoria">
                  <input value={form.categoria} onChange={(e) => setForm((f) => ({ ...f, categoria: e.target.value }))} className={inputCls} placeholder="ex.: combustível" />
                </Field>
              )}
            </div>
            {tab === 'lancamentos' && (
              <>
                <Field label="Descrição" required>
                  <input value={form.descricao} onChange={(e) => setForm((f) => ({ ...f, descricao: e.target.value }))} className={inputCls} required />
                </Field>
                <div className="grid grid-cols-2 gap-3">
                  <Field label="Tipo" required>
                    <select value={form.tipo_lancamento} onChange={(e) => setForm((f) => ({ ...f, tipo_lancamento: e.target.value }))} className={inputCls}>
                      <option value="entrada">Entrada</option>
                      <option value="saida">Saída</option>
                    </select>
                  </Field>
                  <Field label="Categoria" required>
                    <input value={form.categoria} onChange={(e) => setForm((f) => ({ ...f, categoria: e.target.value }))} className={inputCls} required />
                  </Field>
                </div>
              </>
            )}
            {createError && <ErrorNotice message={createError} />}
            <div className="flex justify-end gap-2 pt-2">
              <Button variant="outline" onClick={() => setCreateOpen(false)}>Cancelar</Button>
              <Button type="submit" disabled={saving}>{saving ? 'Salvando...' : 'Salvar'}</Button>
            </div>
          </form>
        </Modal>
      )}

      {baixaTarget && (
        <Modal title="Registrar pagamento" onClose={() => setBaixaTarget(null)}>
          <form onSubmit={handleBaixa} className="space-y-4">
            <p className="text-sm text-gray-500">
              Saldo atual: <span className="font-semibold text-gray-900">{fmtBRL(baixaTarget.saldo)}</span>
            </p>
            <div className="grid grid-cols-2 gap-3">
              <Field label="Valor pago" required>
                <input type="number" step="0.01" min="0" value={baixaForm.valor_pago} onChange={(e) => setBaixaForm((f) => ({ ...f, valor_pago: e.target.value }))} className={inputCls} required />
              </Field>
              <Field label="Data do pagamento">
                <input type="date" value={baixaForm.data_pagamento} onChange={(e) => setBaixaForm((f) => ({ ...f, data_pagamento: e.target.value }))} className={inputCls} />
              </Field>
            </div>
            {'cliente_id' in baixaTarget && (
              <Field label="Forma de pagamento">
                <select value={baixaForm.forma_pagamento} onChange={(e) => setBaixaForm((f) => ({ ...f, forma_pagamento: e.target.value }))} className={inputCls}>
                  <option value="dinheiro">Dinheiro</option>
                  <option value="pix">PIX</option>
                  <option value="credito">Crédito</option>
                  <option value="debito">Débito</option>
                  <option value="boleto">Boleto</option>
                  <option value="cheque">Cheque</option>
                </select>
              </Field>
            )}
            <div className="flex justify-end gap-2 pt-2">
              <Button variant="outline" onClick={() => setBaixaTarget(null)}>Cancelar</Button>
              <Button type="submit" disabled={saving}>{saving ? 'Salvando...' : 'Confirmar'}</Button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  )
}
