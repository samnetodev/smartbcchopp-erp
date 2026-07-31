import { useCallback, useEffect, useState } from 'react'
import { listAuditoria, AuditoriaEvento } from '../api/client'
import { Badge, Spinner, EmptyState, PageHeader, Card, Th, Td, ErrorNotice } from '../components/ui'

const acaoTone: Record<string, 'green' | 'red' | 'amber' | 'gray'> = {
  C: 'green',
  U: 'amber',
  D: 'red',
}

export default function Auditoria() {
  const [items, setItems] = useState<AuditoriaEvento[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await listAuditoria()
      setItems(res.items)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao carregar auditoria')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    load()
  }, [load])

  return (
    <div>
      <PageHeader title="Auditoria" subtitle={`${items.length} eventos`} />

      {error && <div className="mb-4"><ErrorNotice message={error} /></div>}

      <Card>
        {loading ? (
          <Spinner />
        ) : items.length === 0 ? (
          <EmptyState message="Nenhum evento de auditoria registrado" />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-100">
                <tr>
                  <Th>Data</Th>
                  <Th>Ação</Th>
                  <Th>Entidade</Th>
                  <Th>Usuário</Th>
                  <Th>Alterações</Th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {items.map((e) => (
                  <tr key={e.id} className="hover:bg-gray-50/50 align-top">
                    <Td>{new Date(e.created_at).toLocaleString('pt-BR')}</Td>
                    <Td><Badge tone={acaoTone[e.acao]}>{e.acao}</Badge></Td>
                    <Td>
                      <p className="font-medium text-gray-900">{e.entidade_tipo}</p>
                      <p className="text-xs text-gray-400">{e.entidade_id}</p>
                    </Td>
                    <Td>{e.usuario_id ? e.usuario_id.slice(0, 8) : '—'}</Td>
                    <Td>
                      {e.dados_novos ? (
                        <details>
                          <summary className="cursor-pointer text-xs text-gray-500">ver alterações</summary>
                          <pre className="mt-1 text-xs bg-gray-50 p-2 rounded overflow-x-auto max-w-md whitespace-pre-wrap">
                            {JSON.stringify({ anteriores: e.dados_anteriores, novos: e.dados_novos }, null, 2)}
                          </pre>
                        </details>
                      ) : '—'}
                    </Td>
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
