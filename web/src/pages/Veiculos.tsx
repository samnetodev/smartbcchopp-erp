import { useCallback, useEffect, useState } from 'react'
import { listVeiculos, createVeiculo, updateVeiculo, deleteVeiculo, Veiculo } from '../api/client'
import { Modal, Field, Button, Badge, Spinner, EmptyState, PageHeader, Card, Th, Td, inputCls, ErrorNotice } from '../components/ui'
import { fmtDate } from '../lib/format'

type FormState = {
  placa: string
  marca: string
  modelo: string
  tipo: string
  proprietario: string
  categoria: string
  cor: string
  renavam: string
  chassi: string
  ano_fabricacao: string
  ano_modelo: string
  capacidade_carga_kg: string
  km_atual: string
  km_proxima_troca_oleo: string
  data_aquisicao: string
  data_vencimento_seguro: string
  terceiro_nome: string
  terceiro_cpf_cnpj: string
  status: string
}

const emptyForm: FormState = {
  placa: '',
  marca: '',
  modelo: '',
  tipo: 'caminhao',
  proprietario: 'proprio',
  categoria: 'pesado',
  cor: '',
  renavam: '',
  chassi: '',
  ano_fabricacao: '',
  ano_modelo: '',
  capacidade_carga_kg: '',
  km_atual: '0',
  km_proxima_troca_oleo: '',
  data_aquisicao: '',
  data_vencimento_seguro: '',
  terceiro_nome: '',
  terceiro_cpf_cnpj: '',
  status: 'disponivel',
}

const statusTone: Record<string, 'green' | 'red' | 'amber' | 'blue' | 'gray'> = {
  disponivel: 'green',
  em_rota: 'blue',
  manutencao: 'amber',
  inativo: 'gray',
}

export default function Veiculos() {
  const [items, setItems] = useState<Veiculo[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [search, setSearch] = useState('')
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState<Veiculo | null>(null)
  const [form, setForm] = useState<FormState>(emptyForm)
  const [saving, setSaving] = useState(false)
  const [formError, setFormError] = useState<string | null>(null)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await listVeiculos(search || undefined)
      setItems(res.items)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao carregar veículos')
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

  const openEdit = (v: Veiculo) => {
    setEditing(v)
    setForm({
      placa: v.placa,
      marca: v.marca,
      modelo: v.modelo,
      tipo: v.tipo,
      proprietario: v.proprietario,
      categoria: v.categoria ?? '',
      cor: v.cor ?? '',
      renavam: v.renavam ?? '',
      chassi: v.chassi ?? '',
      ano_fabricacao: v.ano_fabricacao ? String(v.ano_fabricacao) : '',
      ano_modelo: v.ano_modelo ? String(v.ano_modelo) : '',
      capacidade_carga_kg: v.capacidade_carga_kg ? String(v.capacidade_carga_kg) : '',
      km_atual: String(v.km_atual ?? 0),
      km_proxima_troca_oleo: v.km_proxima_troca_oleo ? String(v.km_proxima_troca_oleo) : '',
      data_aquisicao: v.data_aquisicao ?? '',
      data_vencimento_seguro: v.data_vencimento_seguro ?? '',
      terceiro_nome: v.terceiro_nome ?? '',
      terceiro_cpf_cnpj: v.terceiro_cpf_cnpj ?? '',
      status: v.status,
    })
    setFormError(null)
    setModalOpen(true)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setFormError(null)
    const base = {
      marca: form.marca,
      modelo: form.modelo,
      cor: form.cor || null,
      renavam: form.renavam || null,
      chassi: form.chassi || null,
      ano_fabricacao: form.ano_fabricacao ? Number(form.ano_fabricacao) : null,
      ano_modelo: form.ano_modelo ? Number(form.ano_modelo) : null,
      categoria: (form.categoria || null) as Veiculo['categoria'],
      capacidade_carga_kg: form.capacidade_carga_kg ? Number(form.capacidade_carga_kg) : null,
      km_atual: Number(form.km_atual) || 0,
      km_proxima_troca_oleo: form.km_proxima_troca_oleo ? Number(form.km_proxima_troca_oleo) : null,
      data_aquisicao: form.data_aquisicao || null,
      data_vencimento_seguro: form.data_vencimento_seguro || null,
      terceiro_nome: form.terceiro_nome || null,
      terceiro_cpf_cnpj: form.terceiro_cpf_cnpj || null,
    }
    try {
      if (editing) {
        await updateVeiculo(editing.id, { ...base, status: form.status as Veiculo['status'] })
      } else {
        await createVeiculo({
          ...base,
          placa: form.placa.toUpperCase(),
          tipo: form.tipo as Veiculo['tipo'],
          proprietario: form.proprietario as Veiculo['proprietario'],
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

  const handleDelete = async (v: Veiculo) => {
    if (!confirm(`Excluir veículo placa ${v.placa}?`)) return
    try {
      await deleteVeiculo(v.id)
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
        title="Veículos"
        subtitle={`${items.length} veículos cadastrados`}
        action={<Button onClick={openNew}>+ Novo veículo</Button>}
      />

      <div className="mb-4">
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Buscar por placa, marca ou modelo..."
          className={inputCls + ' max-w-sm'}
        />
      </div>

      {error && <div className="mb-4"><ErrorNotice message={error} /></div>}

      <Card>
        {loading ? (
          <Spinner />
        ) : items.length === 0 ? (
          <EmptyState message="Nenhum veículo cadastrado" />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-100">
                <tr>
                  <Th>Placa</Th>
                  <Th>Veículo</Th>
                  <Th>Tipo</Th>
                  <Th>KM atual</Th>
                  <Th>Próx. troca óleo</Th>
                  <Th>Seguro vence</Th>
                  <Th>Status</Th>
                  <Th />
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {items.map((v) => (
                  <tr key={v.id} className="hover:bg-gray-50/50">
                    <Td className="font-medium text-gray-900">{v.placa}</Td>
                    <Td>
                      <p>{v.marca} {v.modelo}</p>
                      {v.cor && <p className="text-xs text-gray-400">{v.cor}{v.ano_modelo ? ` · ${v.ano_modelo}` : ''}</p>}
                    </Td>
                    <Td>{v.tipo}</Td>
                    <Td>{v.km_atual.toLocaleString('pt-BR')} km</Td>
                    <Td>{v.km_proxima_troca_oleo ? `${v.km_proxima_troca_oleo.toLocaleString('pt-BR')} km` : '—'}</Td>
                    <Td>{fmtDate(v.data_vencimento_seguro)}</Td>
                    <Td>
                      <Badge tone={statusTone[v.status]}>{v.status}</Badge>
                    </Td>
                    <Td>
                      <div className="flex justify-end gap-1">
                        <Button variant="ghost" onClick={() => openEdit(v)}>Editar</Button>
                        <Button variant="danger" onClick={() => handleDelete(v)}>Excluir</Button>
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
        <Modal title={editing ? 'Editar veículo' : 'Novo veículo'} onClose={() => setModalOpen(false)}>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-3 gap-3">
              <Field label="Placa" required>
                <input value={form.placa} onChange={set('placa')} disabled={!!editing} className={inputCls} required maxLength={7} placeholder="ABC1D23" />
              </Field>
              <Field label="Marca" required>
                <input value={form.marca} onChange={set('marca')} className={inputCls} required />
              </Field>
              <Field label="Modelo" required>
                <input value={form.modelo} onChange={set('modelo')} className={inputCls} required />
              </Field>
            </div>
            <div className="grid grid-cols-3 gap-3">
              <Field label="Tipo" required>
                <select value={form.tipo} onChange={set('tipo')} className={inputCls}>
                  <option value="caminhao">Caminhão</option>
                  <option value="van">Van</option>
                  <option value="carro">Carro</option>
                  <option value="utilitario">Utilitário</option>
                </select>
              </Field>
              <Field label="Proprietário" required>
                <select value={form.proprietario} onChange={set('proprietario')} className={inputCls}>
                  <option value="proprio">Próprio</option>
                  <option value="terceiro">Terceiro</option>
                </select>
              </Field>
              <Field label="Categoria">
                <select value={form.categoria} onChange={set('categoria')} className={inputCls}>
                  <option value="">—</option>
                  <option value="leve">Leve</option>
                  <option value="medio">Médio</option>
                  <option value="pesado">Pesado</option>
                </select>
              </Field>
            </div>
            <div className="grid grid-cols-3 gap-3">
              <Field label="Renavam">
                <input value={form.renavam} onChange={set('renavam')} className={inputCls} />
              </Field>
              <Field label="Chassi">
                <input value={form.chassi} onChange={set('chassi')} className={inputCls} />
              </Field>
              <Field label="Cor">
                <input value={form.cor} onChange={set('cor')} className={inputCls} />
              </Field>
            </div>
            <div className="grid grid-cols-3 gap-3">
              <Field label="Ano fabricação">
                <input type="number" value={form.ano_fabricacao} onChange={set('ano_fabricacao')} className={inputCls} />
              </Field>
              <Field label="Ano modelo">
                <input type="number" value={form.ano_modelo} onChange={set('ano_modelo')} className={inputCls} />
              </Field>
              <Field label="Capacidade (kg)">
                <input type="number" value={form.capacidade_carga_kg} onChange={set('capacidade_carga_kg')} className={inputCls} />
              </Field>
            </div>
            <div className="grid grid-cols-3 gap-3">
              <Field label="KM atual" required>
                <input type="number" min="0" value={form.km_atual} onChange={set('km_atual')} className={inputCls} required />
              </Field>
              <Field label="KM próx. troca óleo">
                <input type="number" min="0" value={form.km_proxima_troca_oleo} onChange={set('km_proxima_troca_oleo')} className={inputCls} />
              </Field>
              <Field label="Status">
                <select value={form.status} onChange={set('status')} className={inputCls}>
                  <option value="disponivel">Disponível</option>
                  <option value="em_rota">Em rota</option>
                  <option value="manutencao">Manutenção</option>
                  <option value="inativo">Inativo</option>
                </select>
              </Field>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <Field label="Data aquisição">
                <input type="date" value={form.data_aquisicao} onChange={set('data_aquisicao')} className={inputCls} />
              </Field>
              <Field label="Vencimento seguro">
                <input type="date" value={form.data_vencimento_seguro} onChange={set('data_vencimento_seguro')} className={inputCls} />
              </Field>
            </div>
            {form.proprietario === 'terceiro' && (
              <div className="grid grid-cols-2 gap-3">
                <Field label="Nome do terceiro">
                  <input value={form.terceiro_nome} onChange={set('terceiro_nome')} className={inputCls} />
                </Field>
                <Field label="CPF/CNPJ do terceiro">
                  <input value={form.terceiro_cpf_cnpj} onChange={set('terceiro_cpf_cnpj')} className={inputCls} />
                </Field>
              </div>
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
