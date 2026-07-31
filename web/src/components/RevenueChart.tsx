import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend,
} from 'recharts'

interface RevenueChartProps {
  data: Array<{ mes: string; receita: number; qtd_pedidos: number }>
}

function formatMes(mes: string) {
  const d = new Date(mes)
  return d.toLocaleDateString('pt-BR', { month: 'short', year: '2-digit' })
}

export default function RevenueChart({ data }: RevenueChartProps) {
  const chartData = data.map((d) => ({
    ...d,
    mes: formatMes(d.mes),
    receita_k: Math.round(d.receita / 1000),
  }))

  if (chartData.length === 0) {
    return (
      <div className="card p-6">
        <div className="card-header -mx-6 -mt-6 mb-4">
          <h3 className="text-sm font-semibold text-gray-900">Faturamento Mensal</h3>
        </div>
        <p className="text-sm text-gray-400 py-8 text-center">Nenhum dado disponível</p>
      </div>
    )
  }

  return (
    <div className="card p-6">
      <div className="card-header -mx-6 -mt-6 mb-4">
        <h3 className="text-sm font-semibold text-gray-900">Faturamento Mensal</h3>
      </div>
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis dataKey="mes" tick={{ fontSize: 12 }} stroke="#9ca3af" />
          <YAxis tick={{ fontSize: 12 }} stroke="#9ca3af" tickFormatter={(v) => `${v}k`} />
          <Tooltip
            contentStyle={{
              background: '#fff',
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
              boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
            }}
            formatter={(value: number) => [`R$ ${value.toLocaleString('pt-BR')}`, 'Receita']}
          />
          <Legend />
          <Bar
            dataKey="receita_k"
            fill="#6366f1"
            radius={[4, 4, 0, 0]}
            name="Receita (R$)"
            maxBarSize={40}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
