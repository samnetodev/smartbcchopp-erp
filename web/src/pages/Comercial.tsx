import { useCallback, useEffect, useState } from 'react'
import { listMetas, createMeta, updateMeta, deleteMeta, Meta } from '../api/client'
import { Modal, Field, Button, Badge, Spinner, EmptyState, PageHeader, Card, Th, Td, inputCls, ErrorNotice } from '../components/ui'
import { fmtBRL, fmtDate } from '../lib/format'

const statusTone: Record<string, 'green' | 'red' | 'amber' | 'blue' | 'gray'> = {
  aberta: 'blue',
  atingida: 'green',
  nao_atingida: 'red',
  cancelada: 'gray',
}

const emptyForm = {
  descricao: '',
  periodo_inicio: '',
  periodo_fim: '',
  valor_meta: '',
  comissao_percentual: '0',
  status: 'aberta',
}

export default function Comercial() {
  const [items, setItems] = useState<Meta[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState<Meta | null>(null)
  const [form, setForm] = useState(emptyForm)
  const [saving, setSaving] = useState(false)
  const [formError, setFormError] = useState<string | null>(null)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await listMetas()
      setItems(res.items)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao carregar metas')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    load()
  }, [load])

  const openNew = () => {
    setEditing(null)
    setForm(emptyForm)
    setFormError(null)
    setModalOpen(true)
  }

  const openEdit = (m: Meta) => {
    setEditing(m)
    setForm({
      descricao: m.descricao,
      periodo_inicio: m.periodo_inicio,
      periodo_fim: m.periodo_fim,
      valor_meta: String(m.valor_meta),
      comissao_percentual: String(m.comissao_percentual),
      status: m.status,
    })
    setFormError(null)
    setModalOpen(true)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setFormError(null)
    try {
      if (editing) {
        await updateMeta(editing.id, {
          descricao: form.descricao,
          periodo_inicio: form.periodo_inicio,
          periodo_fim: form.periodo_fim,
          valor_meta: Number(form.valor_meta) || 0,
          comissao_percentual: Number(form.comissao_percentual) || 0,
          status: form.status as Meta['status'],
        })
      } else {
        await createMeta({
          descricao: form.descricao,
          periodo_inicio: form.periodo_inicio,
          periodo_fim: form.periodo_fim,
          valor_meta: Number(form.valor_meta) || 0,
          comissao_percentual: Number(form.comissao_percentual) || 0,
        })
      }
      setModalOpen(false)
      load()
    } catch (err) {
      setFormError(err instanceof Error ? err.message : 'Erro ao salvar')
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (m: Meta) => {
    if (!confirm(`Excluir meta "${m.descricao}"?`)) return
    try {
      await deleteMeta(m.id)
      load()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao excluir')
    }
  }

  return (
    <div>
      <PageHeader
        title="Comercial"
        subtitle="Metas de vendas"
        action={<Button onClick={openNew}>+ Nova meta</Button>}
      />

      {error && <div className="mb-4"><ErrorNotice message={error} /></div>}

      <Card>
        {loading ? (
          <Spinner />
        ) : items.length === 0 ? (
          <EmptyState message="Nenhuma meta cadastrada" />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-100">
                <tr>
                  <Th>Descrição</Th>
                  <Th>Período</Th>
                  <Th>Meta</Th>
                  <Th>Realizado</Th>
                  <Th>% realizado</Th>
                  <Th>Comissão</Th>
                  <Th>Status</Th>
                  <Th />
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {items.map((m) => {
                  const pct = Number(m.valor_meta) > 0 ? Math.round((Number(m.valor_realizado) / Number(m.valor_meta)) * 100) : 0
                  return (
                    <tr key={m.id} className="hover:bg-gray-50/50">
                      <Td className="font-medium text-gray-900">{m.descricao}</Td>
                      <Td>{fmtDate(m.periodo_inicio)} → {fmtDate(m.periodo_fim)}</Td>
                      <Td>{fmtBRL(m.valor_meta)}</Td>
                      <Td>{fmtBRL(m.valor_realizado)}</Td>
                      <Td>{pct}%</Td>
                      <Td>{m.comissao_percentual}%</Td>
                      <Td><Badge tone={statusTone[m.status]}>{m.status}</Badge></Td>
                      <Td>
                        <div className="flex justify-end gap-1">
                          <Button variant="ghost" onClick={() => openEdit(m)}>Editar</Button>
                          <Button variant="danger" onClick={() => handleDelete(m)}>Excluir</Button>
                        </div>
                      </Td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      {modalOpen && (
        <Modal title={editing ? 'Editar meta' : 'Nova meta'} onClose={() => setModalOpen(false)}>
          <form onSubmit={handleSubmit} className="space-y-4">
            <Field label="Descrição" required>
              <input value={form.descricao} onChange={(e) => setForm((f) => ({ ...f, descricao: e.target.value }))} className={inputCls} required />
            </Field>
            <div className="grid grid-cols-2 gap-3">
              <Field label="Período início" required>
                <input type="date" value={form.periodo_inicio} onChange={(e) => setForm((f) => ({ ...f, periodo_inicio: e.target.value }))} className={inputCls} required />
              </Field>
              <Field label="Período fim" required>
                <input type="date" value={form.periodo_fim} onChange={(e) => setForm((f) => ({ ...f, periodo_fim: e.target.value }))} className={inputCls} required />
              </Field>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <Field label="Valor da meta (R$)" required>
                <input type="number" step="0.01" min="0" value={form.valor_meta} onChange={(e) => setForm((f) => ({ ...f, valor_meta: e.target.value }))} className={inputCls} required />
              </Field>
              <Field label="Comissão (%)">
                <input type="number" step="0.01" min="0" value={form.comissao_percentual} onChange={(e) => setForm((f) => ({ ...f, comissao_percentual: e.target.value }))} className={inputCls} />
              </Field>
            </div>
            {editing && (
              <Field label="Status">
                <select value={form.status} onChange={(e) => setForm((f) => ({ ...f, status: e.target.value }))} className={inputCls}>
                  <option value="aberta">Aberta</option>
                  <option value="atingida">Atingida</option>
                  <option value="nao_atingida">Não atingida</option>
                  <option value="cancelada">Cancelada</option>
                </select>
              </Field>
            )}
            {formError && <ErrorNotice message={formError} />}
            <div className="flex justify-end gap-2 pt-2">
              <Button variant="outline" onClick={() => setModalOpen(false)}>Cancelar</Button>
              <Button type="submit" disabled={saving}>{saving ? 'Salvando...' : 'Salvar'}</Button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  )
}
