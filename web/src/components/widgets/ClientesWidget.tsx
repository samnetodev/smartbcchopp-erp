import { Users, UserPlus, UserX, UserCheck } from 'lucide-react'

interface Props {
  total: number
  ativos: number
  inativos: number
  novos_mes: number
}

export default function ClientesWidget({ total, ativos, inativos, novos_mes }: Props) {
  return (
    <div className="card p-5">
      <h3 className="text-sm font-semibold text-gray-900 mb-4 flex items-center gap-2">
        <Users className="w-4 h-4 text-brand-500" />
        Clientes
      </h3>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <p className="text-2xl font-bold text-gray-900">{total}</p>
          <p className="text-xs text-gray-500">Total</p>
        </div>
        <div>
          <p className="text-2xl font-bold text-emerald-600">{ativos}</p>
          <p className="text-xs text-gray-500 flex items-center gap-1">
            <UserCheck className="w-3 h-3" /> Ativos
          </p>
        </div>
        <div>
          <p className="text-2xl font-bold text-amber-600">{inativos}</p>
          <p className="text-xs text-gray-500 flex items-center gap-1">
            <UserX className="w-3 h-3" /> Inativos
          </p>
        </div>
        <div>
          <p className="text-2xl font-bold text-brand-600">{novos_mes}</p>
          <p className="text-xs text-gray-500 flex items-center gap-1">
            <UserPlus className="w-3 h-3" /> Novos (mês)
          </p>
        </div>
      </div>
    </div>
  )
}
