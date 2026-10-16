import edgarFacts from '../generated/edgarFacts.json' with { type: 'json' }
import { runStatus } from '../runStatus'
import { edgarFilingsInLast30Days, eventsInLast30Days, parseGrowthPercent } from './derive'
import type { EdgarFiling } from './derive'
import { trackerEvents } from './events'
import type { TrackerEventType } from './events'
import { trackerSuppliers } from './suppliers'
import type { TrackerSupplier } from './suppliers'

export const eventGroups: { id: string; label: string; types: TrackerEventType[] }[] = [
  { id: 'ownership', label: 'Acquisitions & divestitures', types: ['acquisition', 'divestiture'] },
  { id: 'funding', label: 'Funding rounds', types: ['funding'] },
  { id: 'results', label: 'Results reported', types: ['results'] },
  { id: 'restructuring', label: 'Restructuring & layoffs', types: ['restructuring', 'layoff', 'shutdown', 'going-concern', 'late-filing'] },
  { id: 'debt', label: 'Debt & credit ratings', types: ['debt', 'rating'] },
  { id: 'leadership', label: 'Leadership changes', types: ['exec-change'] },
]

export function ageInDays(date: string, asOf = runStatus.lastChecked): number {
  return (Date.parse(asOf) - Date.parse(date)) / 86_400_000
}

export const yearEvents = trackerEvents.filter(event => ageInDays(event.date) >= 0 && ageInDays(event.date) <= 365)
export const monthEvents = eventsInLast30Days(runStatus.lastChecked)

export interface ChangeItem {
  id: string
  supplierId: string
  date: string
  type: TrackerEventType | 'filing'
  text: string
  evidenceIds: string[]
  filings: EdgarFiling[]
}

/** Attach a latest-quarter filing to the corresponding results announcement, preserving both sources. */
export function recentChanges(): ChangeItem[] {
  const changes: ChangeItem[] = monthEvents.map(event => ({ ...event, filings: [] }))
  for (const filing of edgarFilingsInLast30Days(runStatus.lastChecked, edgarFacts)) {
    const matchingResult = changes.find(item => item.supplierId === filing.supplierId && item.type === 'results'
      && ageInDays(item.date, filing.filedDate) >= 0 && ageInDays(item.date, filing.filedDate) <= 30
      && trackerSuppliers.find(s => s.id === item.supplierId)?.revenue?.latest.periodEnd === filing.periodEnd)
    if (matchingResult) matchingResult.filings.push(filing)
    else changes.push({ id: `filing-${filing.supplierId}-${filing.periodEnd}`, supplierId: filing.supplierId,
      date: filing.filedDate, type: 'filing', text: `Filed ${filing.form} for the quarter ended ${filing.periodEnd}.`, evidenceIds: [], filings: [filing] })
  }
  return changes.sort((a, b) => b.date.localeCompare(a.date) || a.id.localeCompare(b.id))
}

export interface GrowthRow {
  supplier: TrackerSupplier
  latest: number
  prior: number | null
}

/** Public companies only. Segments, ARR and other own metrics are never mixed into this comparison. */
export function revenueGrowthRows(): GrowthRow[] {
  return trackerSuppliers.flatMap(supplier => {
    const latest = parseGrowthPercent(supplier.revenue?.latest.yoyGrowth)
    // Qualified strings describe bounds, not exact chart coordinates.
    if (supplier.kind !== 'public' || latest === null || !/^[+-]?\d+(?:\.\d+)?%$/.test(supplier.revenue!.latest.yoyGrowth)) return []
    const priorText = supplier.revenue?.prior?.yoyGrowth
    const prior = priorText && /^[+-]?\d+(?:\.\d+)?%$/.test(priorText) ? parseGrowthPercent(priorText) : null
    return [{ supplier, latest, prior }]
  }).sort((a, b) => a.supplier.name.localeCompare(b.supplier.name))
}

export const secFilerCount = trackerSuppliers.filter(s => s.kind === 'public' && s.edgarId).length
export const secCollectedCount = edgarFacts.suppliers.filter(s => trackerSuppliers.some(t => t.kind === 'public' && t.edgarId === s.id)
  && !(edgarFacts.failures as { id: string }[]).some(f => f.id === s.id)).length
export const filingSeries = edgarFacts.suppliers
