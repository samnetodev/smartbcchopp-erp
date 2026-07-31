import { Users, Truck, Beer, DollarSign, Receipt, Bell } from 'lucide-react'
import StatCard from '../components/StatCard'
import RevenueChart from '../components/RevenueChart'
import AlertsPanel from '../components/AlertsPanel'
import ClientesWidget from '../components/widgets/ClientesWidget'
import VeiculosWidget from '../components/widgets/VeiculosWidget'
import ChopeirasWidget from '../components/widgets/ChopeirasWidget'
import FinanceiroWidget from '../components/widgets/FinanceiroWidget'
import EstoqueWidget from '../components/widgets/EstoqueWidget'
import { DashboardData } from '../api/client'

interface DashboardProps {
  data: DashboardData | null
  loading: boolean
  error: string | null
  refetch: () => void
}

export default function Dashboard({ data, loading, error, refetch }: DashboardProps) {
  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="flex flex-col items-center gap-3">
          <div className="w-10 h-10 border-4 border-brand-500 border-t-transparent rounded-full animate-spin" />
          <p className="text-sm text-gray-500">Carregando dashboard...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <p className="text-rose-600 font-medium">Erro ao carregar dados</p>
          <p className="text-sm text-gray-500 mt-1">{error}</p>
          <button
            onClick={refetch}
            className="mt-4 px-4 py-2 bg-brand-500 text-white rounded-lg text-sm hover:bg-brand-600 transition-colors"
          >
            Tentar novamente
          </button>
        </div>
      </div>
    )
  }

  if (!data) return null

  const { cards, clientes, veiculos, chopeiras, financeiro, estoque, alertas, faturamento_mensal } = data

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        <StatCard
          title="Clientes Ativos"
          value={cards.clientes_ativos}
          icon={<Users className="w-5 h-5" />}
          color="indigo"
          subtitle={`${clientes.novos_mes} novos este mês`}
        />
        <StatCard
          title="Veículos em Circulação"
          value={cards.veiculos_ativos}
          icon={<Truck className="w-5 h-5" />}
          color="sky"
          subtitle={`${veiculos.em_manutencao} em manutenção`}
        />
        <StatCard
          title="Chopeiras Instaladas"
          value={cards.chopeiras_instaladas}
          icon={<Beer className="w-5 h-5" />}
          color="amber"
          subtitle={`${chopeiras.disponiveis} disponíveis`}
        />
        <StatCard
          title="Faturamento (Mês)"
          value={cards.faturamento_mes.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
          icon={<DollarSign className="w-5 h-5" />}
          color="emerald"
        />
        <StatCard
          title="Ticket Médio"
          value={cards.ticket_medio.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
          icon={<Receipt className="w-5 h-5" />}
          color="violet"
        />
        <StatCard
          title="Alertas Pendentes"
          value={cards.alertas_pendentes}
          icon={<Bell className="w-5 h-5" />}
          color="rose"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <RevenueChart data={faturamento_mensal} />
        </div>
        <div>
          <AlertsPanel alerts={alertas} />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
        <ClientesWidget {...clientes} />
        <VeiculosWidget {...veiculos} />
        <ChopeirasWidget {...chopeiras} />
        <FinanceiroWidget {...financeiro} />
        <EstoqueWidget {...estoque} />
      </div>
    </div>
  )
}
