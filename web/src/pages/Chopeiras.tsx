import { useCallback, useEffect, useState } from 'react'
import {
  listChopeiras, createChopeira, deleteChopeira, instalarChopeira,
  desinstalarChopeira, listClientes, Cliente, Chopeira,
} from '../api/client'
import { Modal, Field, Button, Badge, Spinner, EmptyState, PageHeader, Card, Th, Td, inputCls, ErrorNotice } from '../components/ui'
import { fmtDate } from '../lib/format'

const statusTone: Record<string, 'green' | 'red' | 'amber' | 'blue' | 'gray'> = {
  disponivel: 'green',
  instalada: 'blue',
  manutencao: 'amber',
  baixada: 'gray',
}

export default function Chopeiras() {
  const [items, setItems] = useState<Chopeira[]>([])
  const [clientes, setClientes] = useState<Cliente[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [search, setSearch] = useState('')

  const [createOpen, setCreateOpen] = useState(false)
  const [createForm, setCreateForm] = useState({ codigo_identificacao: '', numero_serie: '', marca: '', modelo: '', tipo: 'chopeira', capacidade_l: '' })
  const [createError, setCreateError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)

  const [installTarget, setInstallTarget] = useState<Chopeira | null>(null)
  const [installForm, setInstallForm] = useState({ cliente_id: '', local_instalacao: '', observacao: '' })

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const [chopeiras, cli] = await Promise.all([listChopeiras(search || undefined), listClientes()])
      setItems(chopeiras.items)
      setClientes(cli.items.filter((c) => c.status === 'ativo'))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao carregar chopeiras')
    } finally {
      setLoading(false)
    }
  }, [search])

  useEffect(() => {
    load()
  }, [load])

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setCreateError(null)
    try {
      await createChopeira({
        codigo_identificacao: createForm.codigo_identificacao,
        numero_serie: createForm.numero_serie || null,
        marca: createForm.marca,
        modelo: createForm.modelo,
        tipo: createForm.tipo,
        capacidade_l: createForm.capacidade_l ? Number(createForm.capacidade_l) : null,
      })
      setCreateOpen(false)
      setCreateForm({ codigo_identificacao: '', numero_serie: '', marca: '', modelo: '', tipo: 'chopeira', capacidade_l: '' })
      load()
    } catch (err) {
      setCreateError(err instanceof Error ? err.message : 'Erro ao salvar')
    } finally {
      setSaving(false)
    }
  }

  const handleInstall = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!installTarget) return
    setSaving(true)
    setError(null)
    try {
      await instalarChopeira(installTarget.id, { cliente_id: installForm.cliente_id, local_instalacao: installForm.local_instalacao || undefined, observacao: installForm.observacao || undefined })
      setInstallTarget(null)
      load()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao instalar')
    } finally {
      setSaving(false)
    }
  }

  const handleUninstall = async (c: Chopeira) => {
    if (!confirm(`Desinstalar chopeira ${c.codigo_identificacao}?`)) return
    try {
      await desinstalarChopeira(c.id)
      load()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao desinstalar')
    }
  }

  const handleDelete = async (c: Chopeira) => {
    if (!confirm(`Excluir chopeira ${c.codigo_identificacao}?`)) return
    try {
      await deleteChopeira(c.id)
      load()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao excluir')
    }
  }

  return (
    <div>
      <PageHeader
        title="Chopeiras"
        subtitle={`${items.length} equipamentos`}
        action={<Button onClick={() => setCreateOpen(true)}>+ Nova chopeira</Button>}
      />

      <div className="mb-4">
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Buscar por código, marca ou modelo..."
          className={inputCls + ' max-w-sm'}
        />
      </div>

      {error && <div className="mb-4"><ErrorNotice message={error} /></div>}

      <Card>
        {loading ? (
          <Spinner />
        ) : items.length === 0 ? (
          <EmptyState message="Nenhuma chopeira cadastrada" />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-100">
                <tr>
                  <Th>Código</Th>
                  <Th>Equipamento</Th>
                  <Th>Tipo</Th>
                  <Th>Capacidade</Th>
                  <Th>Instalada em</Th>
                  <Th>Última manutenção</Th>
                  <Th>Status</Th>
                  <Th />
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {items.map((c) => (
                  <tr key={c.id} className="hover:bg-gray-50/50">
                    <Td className="font-medium text-gray-900">{c.codigo_identificacao}</Td>
                    <Td>
                      <p>{c.marca} {c.modelo}</p>
                      {c.numero_serie && <p className="text-xs text-gray-400">S/N {c.numero_serie}</p>}
                    </Td>
                    <Td>{c.tipo}</Td>
                    <Td>{c.capacidade_l ? `${c.capacidade_l} L` : '—'}</Td>
                    <Td>{fmtDate(c.data_instalacao)}</Td>
                    <Td>{fmtDate(c.data_ultima_manutencao)}</Td>
                    <Td>
                      <Badge tone={statusTone[c.status]}>{c.status}</Badge>
                    </Td>
                    <Td>
                      <div className="flex justify-end gap-1">
                        {c.status === 'disponivel' && (
                          <Button variant="outline" onClick={() => { setInstallTarget(c); setInstallForm({ cliente_id: '', local_instalacao: '', observacao: '' }) }}>
                            Instalar
                          </Button>
                        )}
                        {c.status === 'instalada' && (
                          <Button variant="outline" onClick={() => handleUninstall(c)}>Desinstalar</Button>
                        )}
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

      {createOpen && (
        <Modal title="Nova chopeira" onClose={() => setCreateOpen(false)}>
          <form onSubmit={handleCreate} className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <Field label="Código de identificação" required>
                <input value={createForm.codigo_identificacao} onChange={(e) => setCreateForm((f) => ({ ...f, codigo_identificacao: e.target.value }))} className={inputCls} required />
              </Field>
              <Field label="Número de série">
                <input value={createForm.numero_serie} onChange={(e) => setCreateForm((f) => ({ ...f, numero_serie: e.target.value }))} className={inputCls} />
              </Field>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <Field label="Marca" required>
                <input value={createForm.marca} onChange={(e) => setCreateForm((f) => ({ ...f, marca: e.target.value }))} className={inputCls} required />
              </Field>
              <Field label="Modelo" required>
                <input value={createForm.modelo} onChange={(e) => setCreateForm((f) => ({ ...f, modelo: e.target.value }))} className={inputCls} required />
              </Field>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <Field label="Tipo">
                <select value={createForm.tipo} onChange={(e) => setCreateForm((f) => ({ ...f, tipo: e.target.value }))} className={inputCls}>
                  <option value="chopeira">Chopeira</option>
                  <option value="torre">Torre</option>
                  <option value="cooler">Cooler</option>
                  <option value="torneira">Torneira</option>
                </select>
              </Field>
              <Field label="Capacidade (L)">
                <input type="number" min="0" value={createForm.capacidade_l} onChange={(e) => setCreateForm((f) => ({ ...f, capacidade_l: e.target.value }))} className={inputCls} />
              </Field>
            </div>
            {createError && <ErrorNotice message={createError} />}
            <div className="flex justify-end gap-2 pt-2">
              <Button variant="outline" onClick={() => setCreateOpen(false)}>Cancelar</Button>
              <Button type="submit" disabled={saving}>{saving ? 'Salvando...' : 'Salvar'}</Button>
            </div>
          </form>
        </Modal>
      )}

      {installTarget && (
        <Modal title={`Instalar ${installTarget.codigo_identificacao}`} onClose={() => setInstallTarget(null)}>
          <form onSubmit={handleInstall} className="space-y-4">
            <Field label="Cliente" required>
              <select value={installForm.cliente_id} onChange={(e) => setInstallForm((f) => ({ ...f, cliente_id: e.target.value }))} className={inputCls} required>
                <option value="">Selecione...</option>
                {clientes.map((c) => (
                  <option key={c.id} value={c.id}>{c.nome_razao_social}</option>
                ))}
              </select>
            </Field>
            <Field label="Local de instalação">
              <input value={installForm.local_instalacao} onChange={(e) => setInstallForm((f) => ({ ...f, local_instalacao: e.target.value }))} className={inputCls} />
            </Field>
            <Field label="Observação">
              <input value={installForm.observacao} onChange={(e) => setInstallForm((f) => ({ ...f, observacao: e.target.value }))} className={inputCls} />
            </Field>
            <div className="flex justify-end gap-2 pt-2">
              <Button variant="outline" onClick={() => setInstallTarget(null)}>Cancelar</Button>
              <Button type="submit" disabled={saving || !installForm.cliente_id}>{saving ? 'Instalando...' : 'Instalar'}</Button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  )
}
