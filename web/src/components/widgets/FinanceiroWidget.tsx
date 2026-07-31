import { Wallet, ArrowUpRight, ArrowDownRight, AlertTriangle } from 'lucide-react'

interface Props {
  total_a_receber: number
  total_a_pagar: number
  saldo_previsto: number
  contas_receber_vencidas: number
  contas_pagar_vencidas: number
  recebido_mes: number
  pago_mes: number
}

function fmt(v: number) {
  return v.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

export default function FinanceiroWidget(props: Props) {
  return (
    <div className="card p-5">
      <h3 className="text-sm font-semibold text-gray-900 mb-4 flex items-center gap-2">
        <Wallet className="w-4 h-4 text-emerald-500" />
        Financeiro
      </h3>
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-xs text-gray-500">Saldo previsto</span>
          <span className={`text-sm font-bold ${props.saldo_previsto >= 0 ? 'text-emerald-600' : 'text-rose-600'}`}>
            {fmt(props.saldo_previsto)}
          </span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-xs text-gray-500 flex items-center gap-1">
            <ArrowUpRight className="w-3 h-3 text-emerald-500" /> A receber
          </span>
          <span className="text-sm font-medium text-gray-900">{fmt(props.total_a_receber)}</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-xs text-gray-500 flex items-center gap-1">
            <ArrowDownRight className="w-3 h-3 text-rose-500" /> A pagar
          </span>
          <span className="text-sm font-medium text-gray-900">{fmt(props.total_a_pagar)}</span>
        </div>
        <div className="border-t border-gray-100 pt-3">
          <div className="flex items-center justify-between">
            <span className="text-xs text-gray-500">Recebido no mês</span>
            <span className="text-sm font-medium text-emerald-600">{fmt(props.recebido_mes)}</span>
          </div>
          <div className="flex items-center justify-between mt-1">
            <span className="text-xs text-gray-500">Pago no mês</span>
            <span className="text-sm font-medium text-rose-600">{fmt(props.pago_mes)}</span>
          </div>
        </div>
        {(props.contas_receber_vencidas > 0 || props.contas_pagar_vencidas > 0) && (
          <div className="border-t border-gray-100 pt-3 space-y-1">
            {props.contas_receber_vencidas > 0 && (
              <div className="flex items-center gap-1 text-xs text-rose-600">
                <AlertTriangle className="w-3 h-3" />
                {fmt(props.contas_receber_vencidas)} em recebimentos vencidos
              </div>
            )}
            {props.contas_pagar_vencidas > 0 && (
              <div className="flex items-center gap-1 text-xs text-amber-600">
                <AlertTriangle className="w-3 h-3" />
                {fmt(props.contas_pagar_vencidas)} em contas vencidas
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
