import { useState } from 'react'
import Sidebar, { SectionId } from './components/Sidebar'
import TopBar from './components/TopBar'
import Dashboard from './pages/Dashboard'
import Login from './pages/Login'
import Clientes from './pages/Clientes'
import Veiculos from './pages/Veiculos'
import Chopeiras from './pages/Chopeiras'
import Financeiro from './pages/Financeiro'
import Estoque from './pages/Estoque'
import Comercial from './pages/Comercial'
import Relatorios from './pages/Relatorios'
import Alertas from './pages/Alertas'
import Fornecedores from './pages/Fornecedores'
import Auditoria from './pages/Auditoria'
import { useDashboard } from './hooks/useDashboard'
import { setToken, clearToken, getToken, LoginResponse } from './api/client'

const sectionTitles: Record<SectionId, string> = {
  dashboard: 'Dashboard',
  clientes: 'Clientes',
  veiculos: 'Veículos',
  chopeiras: 'Chopeiras',
  financeiro: 'Financeiro',
  estoque: 'Estoque',
  comercial: 'Comercial',
  fornecedores: 'Fornecedores',
  relatorios: 'Relatórios',
  alertas: 'Alertas',
  auditoria: 'Auditoria',
}

export default function App() {
  const [token, setTokenState] = useState<string | null>(() => getToken())
  const [user, setUser] = useState<LoginResponse | null>(null)
  const [activeSection, setActiveSection] = useState<SectionId>('dashboard')
  const { data, loading, error, refetch } = useDashboard(token !== null)
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null)

  const handleRefresh = () => {
    refetch()
    setLastUpdate(new Date())
  }

  const handleLoginSuccess = (data: LoginResponse) => {
    setToken(data.access_token)
    setTokenState(data.access_token)
    setUser(data)
    setActiveSection('dashboard')
  }

  const handleLogout = () => {
    clearToken()
    setTokenState(null)
    setUser(null)
  }

  if (!token) {
    return <Login onSuccess={handleLoginSuccess} />
  }

  const username = user?.username ?? 'Admin'
  const email = user?.email ?? ''

  return (
    <div className="min-h-screen bg-gray-50">
      <Sidebar
        active={activeSection}
        onNavigate={setActiveSection}
        onLogout={handleLogout}
      />
      <div className="ml-64">
        <TopBar
          title={sectionTitles[activeSection]}
          alertasPendentes={data?.cards.alertas_pendentes ?? 0}
          onRefresh={handleRefresh}
          lastUpdate={lastUpdate}
          username={username}
          email={email}
        />
        <main className="p-6">
          {activeSection === 'dashboard' && (
            <Dashboard data={data} loading={loading} error={error} refetch={handleRefresh} />
          )}
          {activeSection === 'clientes' && <Clientes />}
          {activeSection === 'veiculos' && <Veiculos />}
          {activeSection === 'chopeiras' && <Chopeiras />}
          {activeSection === 'financeiro' && <Financeiro />}
          {activeSection === 'estoque' && <Estoque />}
          {activeSection === 'comercial' && <Comercial />}
          {activeSection === 'fornecedores' && <Fornecedores />}
          {activeSection === 'relatorios' && <Relatorios />}
          {activeSection === 'alertas' && <Alertas />}
          {activeSection === 'auditoria' && <Auditoria />}
        </main>
      </div>
    </div>
  )
}
