import { Bell, RefreshCw } from 'lucide-react'

interface TopBarProps {
  title: string
  alertasPendentes: number
  onRefresh: () => void
  lastUpdate: Date | null
  username: string
  email: string
}

export default function TopBar({
  title,
  alertasPendentes,
  onRefresh,
  lastUpdate,
  username,
  email,
}: TopBarProps) {
  const initials = username.slice(0, 2).toUpperCase()

  return (
    <header className="sticky top-0 z-30 bg-white/80 backdrop-blur border-b border-gray-100">
      <div className="flex items-center justify-between h-16 px-6">
        <div className="flex items-center gap-3">
          <h1 className="text-lg font-semibold text-gray-900">{title}</h1>
          {lastUpdate && (
            <span className="text-xs text-gray-400">
              Atualizado {lastUpdate.toLocaleTimeString('pt-BR')}
            </span>
          )}
        </div>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1.5 text-xs text-emerald-600">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
            </span>
            Tempo real
          </div>

          <button
            onClick={onRefresh}
            className="p-2 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors"
            title="Atualizar"
          >
            <RefreshCw className="w-4 h-4" />
          </button>

          <button className="relative p-2 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors">
            <Bell className="w-4 h-4" />
            {alertasPendentes > 0 && (
              <span className="absolute -top-0.5 -right-0.5 w-4 h-4 rounded-full bg-rose-500 text-white text-[10px] font-bold flex items-center justify-center">
                {alertasPendentes > 9 ? '9+' : alertasPendentes}
              </span>
            )}
          </button>

          <div className="flex items-center gap-2 pl-4 border-l border-gray-200">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-brand-400 to-brand-600 flex items-center justify-center text-white text-xs font-bold">
              {initials}
            </div>
            <div className="text-sm">
              <p className="font-medium text-gray-900">{username}</p>
              {email && <p className="text-xs text-gray-400">{email}</p>}
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}
