import { evidenceById } from './evidence'

export function evidenceSourceLabel(ids: string | string[]): string {
  const list = Array.isArray(ids) ? ids : [ids]
  const names = list
    .map((id) => {
      const record = evidenceById[id]
      if (!record) return id
      return record.organization
    })
    .filter(Boolean)

  const unique = [...new Set(names)]
  if (unique.length === 0) return 'View sources'
  if (unique.length === 1) return unique[0]
  if (unique.length === 2) return unique.join(' & ')
  if (unique.length === 3) return unique.join(', ')
  return `${unique.slice(0, 2).join(', ')} +${unique.length - 2}`
}

export function evidenceAriaLabel(ids: string | string[], context?: string): string {
  const label = evidenceSourceLabel(ids)
  return context ? `${context}: ${label}` : `View evidence: ${label}`
}
