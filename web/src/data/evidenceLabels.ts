import { evidenceById } from './evidence'

export function evidenceSourceLabel(ids: string | string[]): string {
  const list = Array.isArray(ids) ? ids : [ids]
  const names = list
    .flatMap((id) => {
      const record = evidenceById[id]
      if (!record) return [id]
      if (record.sourceAttributions?.length) {
        return record.sourceAttributions.map((source) => source.organization)
      }
      return record.organization.split(/\s*\/\s*/)
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

/** The most recent date attached to a set of evidence records — retrieval date if present, else publication date. */
function evidenceDateLabel(ids: string | string[]): string {
  const list = Array.isArray(ids) ? ids : [ids]
  const dates = list
    .map((id) => evidenceById[id])
    .filter((record): record is NonNullable<typeof record> => Boolean(record))
    .map((record) => record.retrievedAt ?? record.publicationDate)
    .filter(Boolean)
  const unique = [...new Set(dates)]
  if (unique.length === 0) return ''
  if (unique.length === 1) return unique[0]
  return `${unique[0]} & ${unique.length - 1} more`
}

/**
 * Density pass — the accessible label for a compact "src" evidence link,
 * which carries no visible source name or date of its own. Names the
 * source and date so the link is still self-describing to a screen reader.
 */
export function evidenceCompactAriaLabel(ids: string | string[], context?: string): string {
  const source = evidenceSourceLabel(ids)
  const date = evidenceDateLabel(ids)
  const label = date ? `${source}, ${date}` : source
  return context ? `${context} — source: ${label}` : `Source: ${label}`
}
