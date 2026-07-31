import { useCallback, useEffect, useState } from 'react'
import { listAlertas, marcarAlertaLido, Alerta } from '../api/client'
import { Button, Badge, Spinner, EmptyState, PageHeader, Card, ErrorNotice } from '../components/ui'

const nivelTone: Record<string, 'red' | 'amber' | 'blue'> = {
  critico: 'red',
  aviso: 'amber',
  info: 'blue',
}

export default function Alertas() {
  const [items, setItems] = useState<Alerta[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      setItems(await listAlertas())
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao carregar alertas')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    load()
  }, [load])

  const markRead = async (a: Alerta) => {
    try {
      await marcarAlertaLido(a.id)
      load()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao marcar alerta')
    }
  }

  const pendentes = items.filter((a) => !a.lido).length

  return (
    <div>
      <PageHeader title="Alertas" subtitle={pendentes > 0 ? `${pendentes} alertas não lidos` : 'Tudo em dia'} />

      {error && <div className="mb-4"><ErrorNotice message={error} /></div>}

      <Card>
        {loading ? (
          <Spinner />
        ) : items.length === 0 ? (
          <EmptyState message="Nenhum alerta gerado" />
        ) : (
          <ul className="divide-y divide-gray-50">
            {items.map((a) => (
              <li key={a.id} className={`flex items-start gap-3 px-4 py-3 ${a.lido ? 'opacity-60' : ''}`}>
                <div className="mt-1">
                  <Badge tone={nivelTone[a.nivel] ?? 'gray'}>{a.nivel}</Badge>
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <p className={`text-sm font-medium ${a.lido ? 'text-gray-500' : 'text-gray-900'}`}>{a.titulo}</p>
                    <span className="text-xs text-gray-400">{a.tipo}</span>
                  </div>
                  {a.mensagem && <p className="text-sm text-gray-500 truncate">{a.mensagem}</p>}
                  <p className="text-xs text-gray-400 mt-0.5">
                    {a.created_at ? new Date(a.created_at).toLocaleString('pt-BR') : ''}
                  </p>
                </div>
                {!a.lido && (
                  <Button variant="outline" className="shrink-0" onClick={() => markRead(a)}>
                    Marcar lido
                  </Button>
                )}
              </li>
            ))}
          </ul>
        )}
      </Card>
    </div>
  )
}
