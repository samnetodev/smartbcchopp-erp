import { Beer, CheckCircle, Check, Wrench, Clock } from 'lucide-react'

interface Props {
  total: number
  instaladas: number
  disponiveis: number
  em_manutencao: number
  manutencao_pendente: number
}

export default function ChopeirasWidget({
  total, instaladas, disponiveis, em_manutencao, manutencao_pendente,
}: Props) {
  return (
    <div className="card p-5">
      <h3 className="text-sm font-semibold text-gray-900 mb-4 flex items-center gap-2">
        <Beer className="w-4 h-4 text-amber-500" />
        Chopeiras
      </h3>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <p className="text-2xl font-bold text-gray-900">{total}</p>
          <p className="text-xs text-gray-500">Total</p>
        </div>
        <div>
          <p className="text-2xl font-bold text-emerald-600">{instaladas}</p>
          <p className="text-xs text-gray-500 flex items-center gap-1">
            <CheckCircle className="w-3 h-3" /> Instaladas
          </p>
        </div>
        <div>
          <p className="text-2xl font-bold text-sky-600">{disponiveis}</p>
          <p className="text-xs text-gray-500 flex items-center gap-1">
            <Check className="w-3 h-3" /> Disponíveis
          </p>
        </div>
        <div>
          <p className="text-2xl font-bold text-amber-600">{em_manutencao}</p>
          <p className="text-xs text-gray-500 flex items-center gap-1">
            <Wrench className="w-3 h-3" /> Em manutenção
          </p>
        </div>
        <div className="col-span-2">
          <p className="text-lg font-bold text-rose-600">{manutencao_pendente}</p>
          <p className="text-xs text-gray-500 flex items-center gap-1">
            <Clock className="w-3 h-3" /> Manutenção preventiva pendente (15d)
          </p>
        </div>
      </div>
    </div>
  )
}
