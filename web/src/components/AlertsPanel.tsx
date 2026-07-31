import { AlertTriangle, Info, AlertCircle, XCircle } from 'lucide-react'

interface Alert {
  id: string
  tipo: string
  nivel: string
  titulo: string
  mensagem: string | null
  lido: boolean
  created_at: string | null
}

interface AlertsPanelProps {
  alerts: Alert[]
}

const nivelConfig = {
  critical: { icon: XCircle, color: 'text-rose-600', bg: 'bg-rose-50' },
  warning: { icon: AlertTriangle, color: 'text-amber-600', bg: 'bg-amber-50' },
  info: { icon: Info, color: 'text-sky-600', bg: 'bg-sky-50' },
}

export default function AlertsPanel({ alerts }: AlertsPanelProps) {
  const active = alerts.filter((a) => !a.lido)

  if (active.length === 0) {
    return (
      <div className="card p-6">
        <div className="card-header -mx-6 -mt-6 mb-4">
          <h3 className="text-sm font-semibold text-gray-900">Alertas Recentes</h3>
        </div>
        <p className="text-sm text-gray-400 py-8 text-center">Nenhum alerta pendente</p>
      </div>
    )
  }

  return (
    <div className="card p-6">
      <div className="card-header -mx-6 -mt-6 mb-4 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-gray-900">Alertas Recentes</h3>
        <span className="text-xs text-gray-400">{active.length} pendentes</span>
      </div>
      <div className="space-y-2">
        {active.slice(0, 5).map((alert) => {
          const cfg = nivelConfig[alert.nivel as keyof typeof nivelConfig] || nivelConfig.info
          const Icon = cfg.icon
          return (
            <div key={alert.id} className={`flex items-start gap-3 p-3 rounded-lg ${cfg.bg}`}>
              <Icon className={`w-5 h-5 mt-0.5 ${cfg.color}`} />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900">{alert.titulo}</p>
                {alert.mensagem && (
                  <p className="text-xs text-gray-500 mt-0.5 line-clamp-2">{alert.mensagem}</p>
                )}
              </div>
              {alert.created_at && (
                <span className="text-xs text-gray-400 whitespace-nowrap">
                  {new Date(alert.created_at).toLocaleDateString('pt-BR')}
                </span>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
