import { useCallback, useEffect, useState } from 'react'
import {
  listProducts, createProduct, updateProduct, deleteProduct,
  listStock, listMovements, listDepositos, createEntry, createExit, createAdjustment,
  createTransfer, listInventoryCounts, createInventoryCount, closeInventoryCount,
  Produto, ItemEstoque, Movimentacao, Deposito, InventarioContagem,
} from '../api/client'
import { Modal, Field, Button, Badge, Spinner, EmptyState, PageHeader, Card, Th, Td, inputCls, ErrorNotice } from '../components/ui'
import { fmtBRL } from '../lib/format'

type Tab = 'produtos' | 'estoque' | 'movimentacoes' | 'contagens'

const productFormEmpty = {
  codigo: '',
  nome: '',
  categoria: 'chope',
  unidade_medida: 'L',
  preco_venda: '',
  preco_custo: '',
  estoque_minimo: '0',
  codigo_barras: '',
  ncm: '',
  ativo: true,
}

const productStatusTone: Record<string, 'green' | 'gray'> = { true: 'green', false: 'gray' }

export default function Estoque() {
  const [tab, setTab] = useState<Tab>('produtos')

  const [produtos, setProdutos] = useState<Produto[]>([])
  const [stock, setStock] = useState<ItemEstoque[]>([])
  const [movements, setMovements] = useState<Movimentacao[]>([])
  const [depositos, setDepositos] = useState<Deposito[]>([])
  const [contagens, setContagens] = useState<InventarioContagem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [prodOpen, setProdOpen] = useState(false)
  const [editingProd, setEditingProd] = useState<Produto | null>(null)
  const [prodForm, setProdForm] = useState(productFormEmpty)
  const [prodError, setProdError] = useState<string | null>(null)

  const [moveType, setMoveType] = useState<'entrada' | 'saida' | 'ajuste'>('entrada')
  const [moveOpen, setMoveOpen] = useState(false)
  const [moveForm, setMoveForm] = useState({ produto_id: '', deposito_id: '', quantidade: '', observacao: '' })
  const [moveError, setMoveError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)

  const [transferOpen, setTransferOpen] = useState(false)
  const [transferForm, setTransferForm] = useState({ produto_id: '', deposito_id_origem: '', deposito_id_destino: '', quantidade: '', observacao: '' })
  const [transferError, setTransferError] = useState<string | null>(null)

  const [countOpen, setCountOpen] = useState(false)
  const [countForm, setCountForm] = useState({ produto_id: '', deposito_id: '', quantidade_contada: '', observacao: '' })
  const [countError, setCountError] = useState<string | null>(null)

  const loadAll = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const [p, s, m, d, c] = await Promise.all([listProducts(), listStock(), listMovements(), listDepositos(), listInventoryCounts()])
      setProdutos(p.items)
      setStock(s.items)
      setMovements(m.items)
      setDepositos(d)
      setContagens(c.items)
      setMoveForm((prev) => ({ ...prev, deposito_id: prev.deposito_id || d[0]?.id || '' }))
      setTransferForm((prev) => ({ ...prev, deposito_id_origem: prev.deposito_id_origem || d[0]?.id || '', deposito_id_destino: prev.deposito_id_destino || d[1]?.id || d[0]?.id || '' }))
      setCountForm((prev) => ({ ...prev, deposito_id: prev.deposito_id || d[0]?.id || '' }))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao carregar estoque')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadAll()
  }, [loadAll])

  const openNewProduct = () => {
    setEditingProd(null)
    setProdForm(productFormEmpty)
    setProdError(null)
    setProdOpen(true)
  }

  const openEditProduct = (p: Produto) => {
    setEditingProd(p)
    setProdForm({
      codigo: p.codigo,
      nome: p.nome,
      categoria: p.categoria,
      unidade_medida: p.unidade_medida,
      preco_venda: String(p.preco_venda),
      preco_custo: p.preco_custo ? String(p.preco_custo) : '',
      estoque_minimo: String(p.estoque_minimo),
      codigo_barras: p.codigo_barras ?? '',
      ncm: p.ncm ?? '',
      ativo: p.ativo,
    })
    setProdError(null)
    setProdOpen(true)
  }

  const handleProductSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setProdError(null)
    try {
      if (editingProd) {
        await updateProduct(editingProd.id, {
          nome: prodForm.nome,
          preco_venda: Number(prodForm.preco_venda) || 0,
          preco_custo: prodForm.preco_custo ? Number(prodForm.preco_custo) : null,
          ncm: prodForm.ncm || null,
          ativo: prodForm.ativo,
        })
      } else {
        await createProduct({
          codigo: prodForm.codigo,
          nome: prodForm.nome,
          categoria: prodForm.categoria as Produto['categoria'],
          unidade_medida: prodForm.unidade_medida as Produto['unidade_medida'],
          preco_venda: Number(prodForm.preco_venda) || 0,
          preco_custo: prodForm.preco_custo ? Number(prodForm.preco_custo) : null,
          estoque_minimo: Number(prodForm.estoque_minimo) || 0,
          codigo_barras: prodForm.codigo_barras || null,
          ncm: prodForm.ncm || null,
        })
      }
      setProdOpen(false)
      loadAll()
    } catch (err) {
      setProdError(err instanceof Error ? err.message : 'Erro ao salvar')
    } finally {
      setSaving(false)
    }
  }

  const handleProductDelete = async (p: Produto) => {
    if (!confirm(`Excluir produto "${p.nome}"?`)) return
    try {
      await deleteProduct(p.id)
      loadAll()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao excluir')
    }
  }

  const openMove = (type: typeof moveType) => {
    setMoveType(type)
    setMoveForm({ produto_id: '', deposito_id: depositos[0]?.id || '', quantidade: '', observacao: '' })
    setMoveError(null)
    setMoveOpen(true)
  }

  const handleMoveSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setMoveError(null)
    try {
      const qtd = Number(moveForm.quantidade) || 0
      const body = { produto_id: moveForm.produto_id, deposito_id: moveForm.deposito_id, quantidade: qtd, observacao: moveForm.observacao || undefined }
      if (moveType === 'entrada') await createEntry(body)
      else if (moveType === 'saida') await createExit(body)
      else await createAdjustment({ produto_id: body.produto_id, deposito_id: body.deposito_id, quantidade_nova: qtd, observacao: moveForm.observacao || undefined })
      setMoveOpen(false)
      loadAll()
    } catch (err) {
      setMoveError(err instanceof Error ? err.message : 'Erro ao registrar')
    } finally {
      setSaving(false)
    }
  }

  const openTransfer = () => {
    setTransferForm({ produto_id: '', deposito_id_origem: depositos[0]?.id || '', deposito_id_destino: depositos[1]?.id || depositos[0]?.id || '', quantidade: '', observacao: '' })
    setTransferError(null)
    setTransferOpen(true)
  }

  const handleTransferSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setTransferError(null)
    try {
      await createTransfer({
        produto_id: transferForm.produto_id,
        deposito_id_origem: transferForm.deposito_id_origem,
        deposito_id_destino: transferForm.deposito_id_destino,
        quantidade: Number(transferForm.quantidade) || 0,
        observacao: transferForm.observacao || undefined,
      })
      setTransferOpen(false)
      loadAll()
    } catch (err) {
      setTransferError(err instanceof Error ? err.message : 'Erro ao transferir')
    } finally {
      setSaving(false)
    }
  }

  const openCount = () => {
    setCountForm({ produto_id: '', deposito_id: depositos[0]?.id || '', quantidade_contada: '', observacao: '' })
    setCountError(null)
    setCountOpen(true)
  }

  const handleCountSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setCountError(null)
    try {
      await createInventoryCount({
        produto_id: countForm.produto_id,
        deposito_id: countForm.deposito_id,
        quantidade_contada: Number(countForm.quantidade_contada) || 0,
        observacao: countForm.observacao || undefined,
      })
      setCountOpen(false)
      loadAll()
    } catch (err) {
      setCountError(err instanceof Error ? err.message : 'Erro ao registrar contagem')
    } finally {
      setSaving(false)
    }
  }

  const handleCloseCount = async (c: InventarioContagem) => {
    if (!confirm('Fechar esta contagem e aplicar a diferença ao estoque?')) return
    setSaving(true)
    try {
      await closeInventoryCount(c.id)
      loadAll()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao fechar contagem')
    } finally {
      setSaving(false)
    }
  }

  const tabs: Array<{ id: Tab; label: string }> = [
    { id: 'produtos', label: 'Produtos' },
    { id: 'estoque', label: 'Estoque' },
    { id: 'movimentacoes', label: 'Movimentações' },
    { id: 'contagens', label: 'Contagens' },
  ]

  return (
    <div>
      <PageHeader
        title="Estoque"
        action={
          <div className="flex gap-2">
            {tab === 'produtos' && <Button onClick={openNewProduct}>+ Novo produto</Button>}
            {tab === 'estoque' && (
              <>
                <Button variant="outline" onClick={() => openMove('entrada')}>Entrada</Button>
                <Button variant="outline" onClick={() => openMove('saida')}>Saída</Button>
                <Button variant="outline" onClick={() => openMove('ajuste')}>Ajuste</Button>
                <Button variant="outline" onClick={openTransfer}>Transferência</Button>
              </>
            )}
            {tab === 'contagens' && (
              <Button variant="outline" onClick={openCount}>+ Nova contagem</Button>
            )}
          </div>
        }
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
        ) : tab === 'produtos' ? (
          produtos.length === 0 ? (
            <EmptyState message="Nenhum produto cadastrado" />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-100">
                  <tr>
                    <Th>Código</Th>
                    <Th>Produto</Th>
                    <Th>Categoria</Th>
                    <Th>Un.</Th>
                    <Th>Custo</Th>
                    <Th>Venda</Th>
                    <Th>Est. mín.</Th>
                    <Th>Status</Th>
                    <Th />
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-50">
                  {produtos.map((p) => (
                    <tr key={p.id} className="hover:bg-gray-50/50">
                      <Td className="font-medium text-gray-900">{p.codigo}</Td>
                      <Td>{p.nome}</Td>
                      <Td><Badge tone="blue">{p.categoria}</Badge></Td>
                      <Td>{p.unidade_medida}</Td>
                      <Td>{p.preco_custo ? fmtBRL(p.preco_custo) : '—'}</Td>
                      <Td>{fmtBRL(p.preco_venda)}</Td>
                      <Td>{Number(p.estoque_minimo).toLocaleString('pt-BR', { maximumFractionDigits: 0 })}</Td>
                      <Td><Badge tone={productStatusTone[String(p.ativo)]}>{p.ativo ? 'ativo' : 'inativo'}</Badge></Td>
                      <Td>
                        <div className="flex justify-end gap-1">
                          <Button variant="ghost" onClick={() => openEditProduct(p)}>Editar</Button>
                          <Button variant="danger" onClick={() => handleProductDelete(p)}>Excluir</Button>
                        </div>
                      </Td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )
        ) : tab === 'estoque' ? (
          stock.length === 0 ? (
            <EmptyState message="Sem itens em estoque. Use Entrada para registrar o primeiro item." />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-100">
                  <tr>
                    <Th>Produto</Th>
                    <Th>Qtd. atual</Th>
                    <Th>Reservada</Th>
                    <Th>Localização</Th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-50">
                  {stock.map((s) => {
                    const prod = produtos.find((p) => p.id === s.produto_id)
                    return (
                      <tr key={s.id} className="hover:bg-gray-50/50">
                        <Td className="font-medium text-gray-900">{prod?.nome ?? s.produto_id}</Td>
                        <Td>{Number(s.quantidade_atual).toLocaleString('pt-BR')}</Td>
                        <Td>{Number(s.quantidade_reservada).toLocaleString('pt-BR')}</Td>
                        <Td>{s.localizacao ?? '—'}</Td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          )
        ) : tab === 'contagens' ? (
          contagens.length === 0 ? (
            <EmptyState message={'Nenhuma contagem registrada. Use "Nova contagem" para iniciar.'} />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-100">
                  <tr>
                    <Th>Data</Th>
                    <Th>Produto</Th>
                    <Th>Status</Th>
                    <Th>Sistema</Th>
                    <Th>Contada</Th>
                    <Th>Diferença</Th>
                    <Th />
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-50">
                  {contagens.map((c) => {
                    const prod = produtos.find((p) => p.id === c.produto_id)
                    const diff = Number(c.diferenca)
                    return (
                      <tr key={c.id} className="hover:bg-gray-50/50">
                        <Td>{new Date(c.data_contagem).toLocaleDateString('pt-BR')}</Td>
                        <Td className="font-medium text-gray-900">{prod?.nome ?? c.produto_id}</Td>
                        <Td><Badge tone={c.status === 'fechado' ? 'green' : 'amber'}>{c.status}</Badge></Td>
                        <Td>{Number(c.quantidade_sistema).toLocaleString('pt-BR')}</Td>
                        <Td>{Number(c.quantidade_contada).toLocaleString('pt-BR')}</Td>
                        <Td className={diff !== 0 ? 'text-red-600 font-medium' : ''}>{diff > 0 ? `+${diff.toLocaleString('pt-BR')}` : diff.toLocaleString('pt-BR')}</Td>
                        <Td>
                          <div className="flex justify-end gap-1">
                            {c.status === 'aberto' && (
                              <Button variant="ghost" disabled={saving} onClick={() => handleCloseCount(c)}>Fechar</Button>
                            )}
                          </div>
                        </Td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          )
        ) : movements.length === 0 ? (
          <EmptyState message="Nenhuma movimentação registrada" />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-100">
                <tr>
                  <Th>Data</Th>
                  <Th>Tipo</Th>
                  <Th>Produto</Th>
                  <Th>Qtd.</Th>
                  <Th>Observação</Th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {movements.map((m) => {
                  const prod = produtos.find((p) => p.id === m.produto_id)
                  const tone = m.tipo === 'entrada' ? 'green' : m.tipo === 'saida' ? 'red' : m.tipo === 'ajuste' ? 'amber' : 'gray'
                  return (
                    <tr key={m.id} className="hover:bg-gray-50/50">
                      <Td>{new Date(m.created_at).toLocaleDateString('pt-BR')}</Td>
                      <Td><Badge tone={tone}>{m.tipo}</Badge></Td>
                      <Td className="font-medium text-gray-900">{prod?.nome ?? m.produto_id}</Td>
                      <Td>{Number(m.quantidade).toLocaleString('pt-BR')}</Td>
                      <Td>{m.observacao ?? '—'}</Td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      {prodOpen && (
        <Modal title={editingProd ? 'Editar produto' : 'Novo produto'} onClose={() => setProdOpen(false)}>
          <form onSubmit={handleProductSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <Field label="Código" required>
                <input value={prodForm.codigo} onChange={(e) => setProdForm((f) => ({ ...f, codigo: e.target.value }))} disabled={!!editingProd} className={inputCls} required />
              </Field>
              <Field label="Nome" required>
                <input value={prodForm.nome} onChange={(e) => setProdForm((f) => ({ ...f, nome: e.target.value }))} className={inputCls} required />
              </Field>
            </div>
            <div className="grid grid-cols-3 gap-3">
              <Field label="Categoria" required>
                <select value={prodForm.categoria} onChange={(e) => setProdForm((f) => ({ ...f, categoria: e.target.value }))} className={inputCls}>
                  <option value="chope">Chope</option>
                  <option value="carvao">Carvão</option>
                  <option value="transporte">Transporte</option>
                </select>
              </Field>
              <Field label="Unidade" required>
                <select value={prodForm.unidade_medida} onChange={(e) => setProdForm((f) => ({ ...f, unidade_medida: e.target.value }))} className={inputCls}>
                  <option value="L">L</option>
                  <option value="KG">KG</option>
                  <option value="UN">UN</option>
                  <option value="PCT">PCT</option>
                  <option value="SACO">SACO</option>
                </select>
              </Field>
              <Field label="Estoque mínimo">
                <input type="number" step="0.001" min="0" value={prodForm.estoque_minimo} onChange={(e) => setProdForm((f) => ({ ...f, estoque_minimo: e.target.value }))} className={inputCls} />
              </Field>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <Field label="Preço de venda (R$)" required>
                <input type="number" step="0.01" min="0" value={prodForm.preco_venda} onChange={(e) => setProdForm((f) => ({ ...f, preco_venda: e.target.value }))} className={inputCls} required />
              </Field>
              <Field label="Preço de custo (R$)">
                <input type="number" step="0.01" min="0" value={prodForm.preco_custo} onChange={(e) => setProdForm((f) => ({ ...f, preco_custo: e.target.value }))} className={inputCls} />
              </Field>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <Field label="Código de barras">
                <input value={prodForm.codigo_barras} onChange={(e) => setProdForm((f) => ({ ...f, codigo_barras: e.target.value }))} className={inputCls} />
              </Field>
              <Field label="NCM">
                <input value={prodForm.ncm} onChange={(e) => setProdForm((f) => ({ ...f, ncm: e.target.value }))} className={inputCls} />
              </Field>
            </div>
            {editingProd && (
              <Field label="Status">
                <select value={String(prodForm.ativo)} onChange={(e) => setProdForm((f) => ({ ...f, ativo: e.target.value === 'true' }))} className={inputCls}>
                  <option value="true">Ativo</option>
                  <option value="false">Inativo</option>
                </select>
              </Field>
            )}
            {prodError && <ErrorNotice message={prodError} />}
            <div className="flex justify-end gap-2 pt-2">
              <Button variant="outline" onClick={() => setProdOpen(false)}>Cancelar</Button>
              <Button type="submit" disabled={saving}>{saving ? 'Salvando...' : 'Salvar'}</Button>
            </div>
          </form>
        </Modal>
      )}

      {moveOpen && (
        <Modal title={`${moveType === 'entrada' ? 'Entrada' : moveType === 'saida' ? 'Saída' : 'Ajuste'} de estoque`} onClose={() => setMoveOpen(false)}>
          <form onSubmit={handleMoveSubmit} className="space-y-4">
            <Field label="Produto" required>
              <select value={moveForm.produto_id} onChange={(e) => setMoveForm((f) => ({ ...f, produto_id: e.target.value }))} className={inputCls} required>
                <option value="">Selecione...</option>
                {produtos.map((p) => (
                  <option key={p.id} value={p.id}>{p.codigo} — {p.nome}</option>
                ))}
              </select>
            </Field>
            <div className="grid grid-cols-2 gap-3">
              <Field label="Depósito" required>
                <select value={moveForm.deposito_id} onChange={(e) => setMoveForm((f) => ({ ...f, deposito_id: e.target.value }))} className={inputCls} required>
                  {depositos.map((d) => (
                    <option key={d.id} value={d.id}>{d.nome}</option>
                  ))}
                </select>
              </Field>
              <Field label={moveType === 'ajuste' ? 'Nova quantidade' : 'Quantidade'} required>
                <input type="number" step="0.001" min="0" value={moveForm.quantidade} onChange={(e) => setMoveForm((f) => ({ ...f, quantidade: e.target.value }))} className={inputCls} required />
              </Field>
              <Field label="Observação">
                <input value={moveForm.observacao} onChange={(e) => setMoveForm((f) => ({ ...f, observacao: e.target.value }))} className={inputCls} />
              </Field>
            </div>
            {moveError && <ErrorNotice message={moveError} />}
            <div className="flex justify-end gap-2 pt-2">
              <Button variant="outline" onClick={() => setMoveOpen(false)}>Cancelar</Button>
              <Button type="submit" disabled={saving || !moveForm.produto_id}>{saving ? 'Salvando...' : 'Confirmar'}</Button>
            </div>
          </form>
        </Modal>
      )}

      {transferOpen && (
        <Modal title="Transferência entre depósitos" onClose={() => setTransferOpen(false)}>
          <form onSubmit={handleTransferSubmit} className="space-y-4">
            <Field label="Produto" required>
              <select value={transferForm.produto_id} onChange={(e) => setTransferForm((f) => ({ ...f, produto_id: e.target.value }))} className={inputCls} required>
                <option value="">Selecione...</option>
                {produtos.map((p) => (
                  <option key={p.id} value={p.id}>{p.codigo} — {p.nome}</option>
                ))}
              </select>
            </Field>
            <div className="grid grid-cols-2 gap-3">
              <Field label="Depósito origem" required>
                <select value={transferForm.deposito_id_origem} onChange={(e) => setTransferForm((f) => ({ ...f, deposito_id_origem: e.target.value }))} className={inputCls} required>
                  {depositos.map((d) => (
                    <option key={d.id} value={d.id}>{d.nome}</option>
                  ))}
                </select>
              </Field>
              <Field label="Depósito destino" required>
                <select value={transferForm.deposito_id_destino} onChange={(e) => setTransferForm((f) => ({ ...f, deposito_id_destino: e.target.value }))} className={inputCls} required>
                  {depositos.map((d) => (
                    <option key={d.id} value={d.id}>{d.nome}</option>
                  ))}
                </select>
              </Field>
            </div>
            <Field label="Quantidade" required>
              <input type="number" step="0.001" min="0" value={transferForm.quantidade} onChange={(e) => setTransferForm((f) => ({ ...f, quantidade: e.target.value }))} className={inputCls} required />
            </Field>
            <Field label="Observação">
              <input value={transferForm.observacao} onChange={(e) => setTransferForm((f) => ({ ...f, observacao: e.target.value }))} className={inputCls} />
            </Field>
            {transferError && <ErrorNotice message={transferError} />}
            <div className="flex justify-end gap-2 pt-2">
              <Button variant="outline" onClick={() => setTransferOpen(false)}>Cancelar</Button>
              <Button type="submit" disabled={saving || !transferForm.produto_id}>{saving ? 'Salvando...' : 'Transferir'}</Button>
            </div>
          </form>
        </Modal>
      )}

      {countOpen && (
        <Modal title="Nova contagem de inventário" onClose={() => setCountOpen(false)}>
          <form onSubmit={handleCountSubmit} className="space-y-4">
            <Field label="Produto" required>
              <select value={countForm.produto_id} onChange={(e) => setCountForm((f) => ({ ...f, produto_id: e.target.value }))} className={inputCls} required>
                <option value="">Selecione...</option>
                {produtos.map((p) => (
                  <option key={p.id} value={p.id}>{p.codigo} — {p.nome}</option>
                ))}
              </select>
            </Field>
            <div className="grid grid-cols-2 gap-3">
              <Field label="Depósito" required>
                <select value={countForm.deposito_id} onChange={(e) => setCountForm((f) => ({ ...f, deposito_id: e.target.value }))} className={inputCls} required>
                  {depositos.map((d) => (
                    <option key={d.id} value={d.id}>{d.nome}</option>
                  ))}
                </select>
              </Field>
              <Field label="Quantidade contada" required>
                <input type="number" step="0.001" min="0" value={countForm.quantidade_contada} onChange={(e) => setCountForm((f) => ({ ...f, quantidade_contada: e.target.value }))} className={inputCls} required />
              </Field>
            </div>
            <Field label="Observação">
              <input value={countForm.observacao} onChange={(e) => setCountForm((f) => ({ ...f, observacao: e.target.value }))} className={inputCls} />
            </Field>
            {countError && <ErrorNotice message={countError} />}
            <div className="flex justify-end gap-2 pt-2">
              <Button variant="outline" onClick={() => setCountOpen(false)}>Cancelar</Button>
              <Button type="submit" disabled={saving || !countForm.produto_id}>{saving ? 'Salvando...' : 'Registrar'}</Button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  )
}
