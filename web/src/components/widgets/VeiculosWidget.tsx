import { Truck, Wrench, Droplet } from 'lucide-react'

interface Props {
  total: number
  ativos: number
  em_manutencao: number
  proxima_troca_oleo: number
}

export default function VeiculosWidget({ total, ativos, em_manutencao, proxima_troca_oleo }: Props) {
  return (
    <div className="card p-5">
      <h3 className="text-sm font-semibold text-gray-900 mb-4 flex items-center gap-2">
        <Truck className="w-4 h-4 text-sky-500" />
        Veículos
      </h3>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <p className="text-2xl font-bold text-gray-900">{total}</p>
          <p className="text-xs text-gray-500">Total</p>
        </div>
        <div>
          <p className="text-2xl font-bold text-emerald-600">{ativos}</p>
          <p className="text-xs text-gray-500 flex items-center gap-1">
            <Truck className="w-3 h-3" /> Em circulação
          </p>
        </div>
        <div>
          <p className="text-2xl font-bold text-amber-600">{em_manutencao}</p>
          <p className="text-xs text-gray-500 flex items-center gap-1">
            <Wrench className="w-3 h-3" /> Em manutenção
          </p>
        </div>
        <div>
          <p className="text-2xl font-bold text-rose-600">{proxima_troca_oleo}</p>
          <p className="text-xs text-gray-500 flex items-center gap-1">
            <Droplet className="w-3 h-3" /> Troca óleo (30d)
          </p>
        </div>
      </div>
    </div>
  )
}
