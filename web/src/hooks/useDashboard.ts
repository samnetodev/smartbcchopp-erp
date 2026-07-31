import { useState, useEffect, useCallback } from 'react'
import { fetchDashboard, DashboardData } from '../api/client'

const POLL_INTERVAL = 30_000

export function useDashboard(enabled = true) {
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(async () => {
    if (!enabled) return
    try {
      const result = await fetchDashboard()
      setData(result)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao carregar dashboard')
    } finally {
      setLoading(false)
    }
  }, [enabled])

  useEffect(() => {
    setLoading(true)
    load()
    if (!enabled) return
    const interval = setInterval(load, POLL_INTERVAL)
    return () => clearInterval(interval)
  }, [load, enabled])

  return { data, loading, error, refetch: load }
}
