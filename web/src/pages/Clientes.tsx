import { useCallback, useEffect, useState } from 'react'
import { listClientes, createCliente, updateCliente, deleteCliente, Cliente } from '../api/client'
import { Modal, Field, Button, Badge, Spinner, EmptyState, PageHeader, Card, Th, Td, inputCls, ErrorNotice } from '../components/ui'
import { fmtBRL } from '../lib/format'

type FormState = {
  tipo_pessoa: 'PF' | 'PJ'
  nome_razao_social: string
  cpf_cnpj: string
  nome_fantasia: string
  rg_ie: string
  email: string
  telefone: string
  celular: string
  limite_credito: string
  status: 'ativo' | 'inativo' | 'bloqueado'
}

const emptyForm: FormState = {
  tipo_pessoa: 'PF',
  nome_razao_social: '',
  cpf_cnpj: '',
  nome_fantasia: '',
  rg_ie: '',
  email: '',
  telefone: '',
  celular: '',
  limite_credito: '0',
  status: 'ativo',
}

const statusTone: Record<string, 'green' | 'red' | 'amber' | 'gray'> = {
  ativo: 'green',
  inativo: 'gray',
  bloqueado: 'red',
}

export default function Clientes() {
  const [items, setItems] = useState<Cliente[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [search, setSearch] = useState('')
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState<Cliente | null>(null)
  const [form, setForm] = useState<FormState>(emptyForm)
  const [saving, setSaving] = useState(false)
  const [formError, setFormError] = useState<string | null>(null)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await listClientes(search || undefined)
      setItems(res.items)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao carregar clientes')
    } finally {
      setLoading(false)
    }
  }, [search])

  useEffect(() => {
    load()
  }, [load])

  const openNew = () => {
    setEditing(null)
    setForm(emptyForm)
    setFormError(null)
    setModalOpen(true)
  }

  const openEdit = (c: Cliente) => {
    setEditing(c)
    setForm({
      tipo_pessoa: c.tipo_pessoa,
      nome_razao_social: c.nome_razao_social,
      cpf_cnpj: c.cpf_cnpj,
      nome_fantasia: c.nome_fantasia ?? '',
      rg_ie: c.rg_ie ?? '',
      email: c.email ?? '',
      telefone: c.telefone ?? '',
      celular: c.celular ?? '',
      limite_credito: String(c.limite_credito),
      status: c.status,
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
        await updateCliente(editing.id, {
          nome_razao_social: form.nome_razao_social,
          nome_fantasia: form.nome_fantasia || null,
          rg_ie: form.rg_ie || null,
          email: form.email || null,
          telefone: form.telefone || null,
          celular: form.celular || null,
          limite_credito: Number(form.limite_credito) || 0,
          status: form.status,
        })
      } else {
        await createCliente({
          tipo_pessoa: form.tipo_pessoa,
          nome_razao_social: form.nome_razao_social,
          cpf_cnpj: form.cpf_cnpj.replace(/\D/g, ''),
          nome_fantasia: form.nome_fantasia || null,
          rg_ie: form.rg_ie || null,
          email: form.email || null,
          telefone: form.telefone || null,
          celular: form.celular || null,
          limite_credito: Number(form.limite_credito) || 0,
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

  const handleDelete = async (c: Cliente) => {
    if (!confirm(`Excluir cliente "${c.nome_razao_social}"?`)) return
    try {
      await deleteCliente(c.id)
      load()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao excluir')
    }
  }

  const set = (k: keyof FormState) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
    setForm((f) => ({ ...f, [k]: e.target.value }))

  return (
    <div>
      <PageHeader
        title="Clientes"
        subtitle={`${items.length} registros`}
        action={<Button onClick={openNew}>+ Novo cliente</Button>}
      />

      <div className="mb-4">
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Buscar por nome ou documento..."
          className={inputCls + ' max-w-sm'}
        />
      </div>

      {error && <div className="mb-4"><ErrorNotice message={error} /></div>}

      <Card>
        {loading ? (
          <Spinner />
        ) : items.length === 0 ? (
          <EmptyState message="Nenhum cliente cadastrado" />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-100">
                <tr>
                  <Th>Nome</Th>
                  <Th>Documento</Th>
                  <Th>Tipo</Th>
                  <Th>Contato</Th>
                  <Th>Limite de crédito</Th>
                  <Th>Status</Th>
                  <Th />
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {items.map((c) => (
                  <tr key={c.id} className="hover:bg-gray-50/50">
                    <Td className="font-medium text-gray-900">{c.nome_razao_social}</Td>
                    <Td>{c.cpf_cnpj}</Td>
                    <Td>
                      <Badge tone={c.tipo_pessoa === 'PJ' ? 'blue' : 'purple'}>{c.tipo_pessoa}</Badge>
                    </Td>
                    <Td>
                      {c.email && <p>{c.email}</p>}
                      {c.celular && <p className="text-xs text-gray-400">{c.celular}</p>}
                    </Td>
                    <Td>{fmtBRL(c.limite_credito)}</Td>
                    <Td>
                      <Badge tone={statusTone[c.status]}>{c.status}</Badge>
                    </Td>
                    <Td>
                      <div className="flex justify-end gap-1">
                        <Button variant="ghost" onClick={() => openEdit(c)}>Editar</Button>
                        <Button variant="danger" onClick={() => handleDelete(c)}>Excluir</Button>
                      </div>
                    </Td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      {modalOpen && (
        <Modal title={editing ? 'Editar cliente' : 'Novo cliente'} onClose={() => setModalOpen(false)}>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <Field label="Tipo" required>
                <select value={form.tipo_pessoa} onChange={set('tipo_pessoa')} className={inputCls} disabled={!!editing}>
                  <option value="PF">Pessoa Física</option>
                  <option value="PJ">Pessoa Jurídica</option>
                </select>
              </Field>
              <Field label={editing ? 'Documento (fixo)' : 'CPF/CNPJ'} required>
                <input
                  value={form.cpf_cnpj}
                  onChange={set('cpf_cnpj')}
                  disabled={!!editing}
                  placeholder="000.000.000-00"
                  className={inputCls}
                  required
                />
              </Field>
            </div>
            <Field label="Nome / Razão Social" required>
              <input value={form.nome_razao_social} onChange={set('nome_razao_social')} className={inputCls} required />
            </Field>
            <div className="grid grid-cols-2 gap-3">
              <Field label="Nome fantasia">
                <input value={form.nome_fantasia} onChange={set('nome_fantasia')} className={inputCls} />
              </Field>
              <Field label="RG / Inscrição Estadual">
                <input value={form.rg_ie} onChange={set('rg_ie')} className={inputCls} />
              </Field>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <Field label="E-mail">
                <input type="email" value={form.email} onChange={set('email')} className={inputCls} />
              </Field>
              <Field label="Telefone">
                <input value={form.telefone} onChange={set('telefone')} className={inputCls} />
              </Field>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <Field label="Celular">
                <input value={form.celular} onChange={set('celular')} className={inputCls} />
              </Field>
              <Field label="Limite de crédito (R$)">
                <input type="number" step="0.01" min="0" value={form.limite_credito} onChange={set('limite_credito')} className={inputCls} />
              </Field>
            </div>
            {editing && (
              <Field label="Status">
                <select value={form.status} onChange={set('status')} className={inputCls}>
                  <option value="ativo">Ativo</option>
                  <option value="inativo">Inativo</option>
                  <option value="bloqueado">Bloqueado</option>
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
