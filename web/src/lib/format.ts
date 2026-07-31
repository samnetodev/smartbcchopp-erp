import { toNumber } from '../api/client'

export function fmtBRL(v: unknown): string {
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(toNumber(v))
}

export function fmtDate(v: string | null | undefined): string {
  if (!v) return '—'
  const [y, m, d] = v.slice(0, 10).split('-')
  if (!y || !m || !d) return v
  return `${d}/${m}/${y}`
}

export function fmtDateInput(v: string | null | undefined): string {
  if (!v) return ''
  return v.slice(0, 10)
}
