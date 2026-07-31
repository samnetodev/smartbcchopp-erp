import { useCallback, useEffect, useState } from 'react'
import { listFornecedores, createFornecedor, updateFornecedor, deleteFornecedor, Fornecedor } from '../api/client'
import { Modal, Field, Button, Badge, Spinner, EmptyState, PageHeader, Card, Th, Td, inputCls, ErrorNotice } from '../components/ui'

type FormState = {
  nome_razao_social: string
  cpf_cnpj: string
  categoria: string
  tipo_pessoa: 'PF' | 'PJ'
  nome_fantasia: string
  email: string
  telefone: string
  contato_nome: string
}

const emptyForm: FormState = {
  nome_razao_social: '',
  cpf_cnpj: '',
  categoria: 'chope',
  tipo_pessoa: 'PJ',
  nome_fantasia: '',
  email: '',
  telefone: '',
  contato_nome: '',
}

const statusTone: Record<string, 'green' | 'red' | 'amber' | 'gray'> = {
  ativo: 'green',
  inativo: 'gray',
  bloqueado: 'red',
}

const categorias = ['chope', 'carvao', 'transporte', 'insumos', 'servicos', 'outros']

export default function Fornecedores() {
  const [items, setItems] = useState<Fornecedor[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState<Fornecedor | null>(null)
  const [form, setForm] = useState<FormState>(emptyForm)
  const [saving, setSaving] = useState(false)
  const [formError, setFormError] = useState<string | null>(null)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await listFornecedores()
      setItems(res.items)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao carregar fornecedores')
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

  const openEdit = (f: Fornecedor) => {
    setEditing(f)
    setForm({
      nome_razao_social: f.nome_razao_social,
      cpf_cnpj: f.cpf_cnpj,
      categoria: f.categoria,
      tipo_pessoa: f.tipo_pessoa === 'PJ' ? 'PJ' : 'PF',
      nome_fantasia: f.nome_fantasia ?? '',
      email: f.email ?? '',
      telefone: f.telefone ?? '',
      contato_nome: f.contato_nome ?? '',
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
        await updateFornecedor(editing.id, {
          nome_razao_social: form.nome_razao_social,
          email: form.email || null,
          telefone: form.telefone || null,
          contato_nome: form.contato_nome || null,
        })
      } else {
        await createFornecedor({
          nome_razao_social: form.nome_razao_social,
          cpf_cnpj: form.cpf_cnpj.replace(/\D/g, ''),
          categoria: form.categoria,
          tipo_pessoa: form.tipo_pessoa,
          nome_fantasia: form.nome_fantasia || null,
          email: form.email || null,
          telefone: form.telefone || null,
          contato_nome: form.contato_nome || null,
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

  const handleDelete = async (f: Fornecedor) => {
    if (!confirm(`Inativar fornecedor "${f.nome_razao_social}"?`)) return
    try {
      await deleteFornecedor(f.id)
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
        title="Fornecedores"
        subtitle={`${items.length} registros`}
        action={<Button onClick={openNew}>+ Novo fornecedor</Button>}
      />

      {error && <div className="mb-4"><ErrorNotice message={error} /></div>}

      <Card>
        {loading ? (
          <Spinner />
        ) : items.length === 0 ? (
          <EmptyState message="Nenhum fornecedor cadastrado" />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-100">
                <tr>
                  <Th>Nome</Th>
                  <Th>Documento</Th>
                  <Th>Categoria</Th>
                  <Th>Contato</Th>
                  <Th>Status</Th>
                  <Th />
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {items.map((f) => (
                  <tr key={f.id} className="hover:bg-gray-50/50">
                    <Td className="font-medium text-gray-900">{f.nome_razao_social}</Td>
                    <Td>{f.cpf_cnpj}</Td>
                    <Td><Badge tone="blue">{f.categoria}</Badge></Td>
                    <Td>
                      {f.contato_nome && <p>{f.contato_nome}</p>}
                      {f.telefone && <p className="text-xs text-gray-400">{f.telefone}</p>}
                    </Td>
                    <Td><Badge tone={statusTone[f.status]}>{f.status}</Badge></Td>
                    <Td>
                      <div className="flex justify-end gap-1">
                        <Button variant="ghost" onClick={() => openEdit(f)}>Editar</Button>
                        <Button variant="danger" onClick={() => handleDelete(f)}>Inativar</Button>
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
        <Modal title={editing ? 'Editar fornecedor' : 'Novo fornecedor'} onClose={() => setModalOpen(false)}>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <Field label="Tipo" required>
                <select value={form.tipo_pessoa} onChange={set('tipo_pessoa')} className={inputCls} disabled={!!editing}>
                  <option value="PJ">Pessoa Jurídica</option>
                  <option value="PF">Pessoa Física</option>
                </select>
              </Field>
              <Field label={editing ? 'Documento (fixo)' : 'CPF/CNPJ'} required>
                <input
                  value={form.cpf_cnpj}
                  onChange={set('cpf_cnpj')}
                  disabled={!!editing}
                  placeholder="00.000.000/0000-00"
                  className={inputCls}
                  required
                />
              </Field>
            </div>
            <Field label="Nome / Razão Social" required>
              <input value={form.nome_razao_social} onChange={set('nome_razao_social')} className={inputCls} required />
            </Field>
            <div className="grid grid-cols-2 gap-3">
              <Field label="Categoria" required>
                <select value={form.categoria} onChange={set('categoria')} className={inputCls}>
                  {categorias.map((c) => (
                    <option key={c} value={c}>{c}</option>
                  ))}
                </select>
              </Field>
              <Field label="Nome fantasia">
                <input value={form.nome_fantasia} onChange={set('nome_fantasia')} className={inputCls} />
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
            <Field label="Contato">
              <input value={form.contato_nome} onChange={set('contato_nome')} className={inputCls} />
            </Field>
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
