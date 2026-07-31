import {
  LayoutDashboard, Users, Truck, Beer, Wallet, Package,
  Bell, TrendingUp, BarChart3, Settings, LogOut, Store, ScrollText,
} from 'lucide-react'

export type SectionId =
  | 'dashboard' | 'clientes' | 'veiculos' | 'chopeiras'
  | 'financeiro' | 'estoque' | 'comercial' | 'fornecedores'
  | 'relatorios' | 'alertas' | 'auditoria'

const navItems: Array<{ label: string; icon: typeof LayoutDashboard; id: SectionId }> = [
  { label: 'Dashboard', icon: LayoutDashboard, id: 'dashboard' },
  { label: 'Clientes', icon: Users, id: 'clientes' },
  { label: 'Veículos', icon: Truck, id: 'veiculos' },
  { label: 'Chopeiras', icon: Beer, id: 'chopeiras' },
  { label: 'Financeiro', icon: Wallet, id: 'financeiro' },
  { label: 'Estoque', icon: Package, id: 'estoque' },
  { label: 'Comercial', icon: TrendingUp, id: 'comercial' },
  { label: 'Fornecedores', icon: Store, id: 'fornecedores' },
  { label: 'Relatórios', icon: BarChart3, id: 'relatorios' },
  { label: 'Alertas', icon: Bell, id: 'alertas' },
  { label: 'Auditoria', icon: ScrollText, id: 'auditoria' },
]

interface SidebarProps {
  active: SectionId
  onNavigate: (id: SectionId) => void
  onLogout: () => void
}

export default function Sidebar({ active, onNavigate, onLogout }: SidebarProps) {
  return (
    <aside className="fixed left-0 top-0 z-40 h-screen w-64 bg-gray-950 text-white flex flex-col">
      <div className="flex items-center gap-3 px-6 h-16 border-b border-gray-800">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-brand-400 to-brand-600 flex items-center justify-center text-white font-bold text-sm">
          SC
        </div>
        <div>
          <p className="text-sm font-semibold">SmartBcChopp</p>
          <p className="text-xs text-gray-400">ERP Dashboard</p>
        </div>
      </div>

      <nav className="flex-1 overflow-y-auto p-4 space-y-1">
        {navItems.map((item) => (
          <button
            key={item.id}
            type="button"
            onClick={() => onNavigate(item.id)}
            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors cursor-pointer ${
              active === item.id
                ? 'bg-brand-600/20 text-brand-300'
                : 'text-gray-400 hover:text-white hover:bg-gray-800'
            }`}
          >
            <item.icon className="w-5 h-5" />
            {item.label}
          </button>
        ))}
      </nav>

      <div className="p-4 border-t border-gray-800 space-y-1">
        <button
          type="button"
          onClick={() => onNavigate('dashboard')}
          className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-gray-400 hover:text-white hover:bg-gray-800 transition-colors cursor-pointer"
        >
          <Settings className="w-5 h-5" />
          Configurações
        </button>
        <button
          type="button"
          onClick={onLogout}
          className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-gray-400 hover:text-rose-300 hover:bg-rose-950/40 transition-colors cursor-pointer"
        >
          <LogOut className="w-5 h-5" />
          Sair
        </button>
      </div>
    </aside>
  )
}
