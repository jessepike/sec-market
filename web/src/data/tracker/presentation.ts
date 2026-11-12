import { listedEdgarFacts as edgarFacts } from './listedEdgar'
import { runStatus } from '../runStatus'
import { edgarFilingsInLast30Days, eventsInLast30Days, parseGrowthPercent, shortSupplierName } from './derive'
import { dealIds } from './deals'
import { isFilingNotice } from './eventFacts'
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

/**
 * SEC quarterly filings in the trailing 12 months, one per filing. A filing also restates the
 * same quarter a year earlier, and edgarFacts stamps that comparative with the newer filing's
 * date, so each filing keeps only the latest quarter it reports.
 */
export function secFilingsInLastYear(asOf = runStatus.lastChecked): EdgarFiling[] {
  const out: EdgarFiling[] = []
  for (const supplier of edgarFacts.suppliers) {
    const byFiling = new Map<string, EdgarFiling>()
    for (const q of supplier.quarters) {
      const current = byFiling.get(q.sourceUrl)
      if (!current || q.periodEnd > current.periodEnd) {
        byFiling.set(q.sourceUrl, { supplierId: supplier.id, periodEnd: q.periodEnd, filedDate: q.filedDate, form: q.form, value: q.value, sourceUrl: q.sourceUrl })
      }
    }
    for (const filing of byFiling.values()) {
      const age = ageInDays(filing.filedDate, asOf)
      if (age >= 0 && age <= 365) out.push(filing)
    }
  }
  return out
}

/**
 * Year view: every tracked event plus each SEC filing that has no matching results announcement.
 * Filings from the last 30 days attach exactly as in `recentChanges`, so both views agree.
 */
export function yearChanges(): ChangeItem[] {
  const items: ChangeItem[] = yearEvents.map(event => ({ ...event, filings: [] }))
  const recentByFiling = new Map(recentChanges().flatMap(item => item.filings.map(f => [f.sourceUrl, item] as const)))
  for (const filing of secFilingsInLastYear()) {
    const recent = recentByFiling.get(filing.sourceUrl)
    const matchingResult = recent
      ? (recent.type === 'filing' ? undefined : items.find(item => item.id === recent.id))
      : items.find(item => item.supplierId === filing.supplierId && item.type === 'results' && item.filings.length === 0
        && ageInDays(item.date, filing.filedDate) >= 0 && ageInDays(item.date, filing.filedDate) <= 30)
    if (matchingResult) matchingResult.filings.push(filing)
    else items.push({ id: `filing-${filing.supplierId}-${filing.periodEnd}`, supplierId: filing.supplierId,
      date: filing.filedDate, type: 'filing', text: `Filed ${filing.form} for the quarter ended ${filing.periodEnd}.`, evidenceIds: [], filings: [filing] })
  }
  return items.sort((a, b) => b.date.localeCompare(a.date) || a.id.localeCompare(b.id))
}

export function groupIdFor(type: ChangeItem['type']): string {
  return type === 'filing' ? 'results' : eventGroups.find(g => g.types.includes(type))!.id
}

/** A counted event: one row, or several rows that report the same transaction. */
export interface CountedUnit {
  key: string
  groupId: string
  date: string
  items: ChangeItem[]
}

const dealTypes: ReadonlySet<string> = new Set(['acquisition', 'divestiture', 'funding'])
const ownershipTypes: ReadonlySet<string> = new Set(['acquisition', 'divestiture'])
const supplierNamePatterns = trackerSuppliers.map(s => ({ id: s.id,
  pattern: new RegExp(`\\b(${[...new Set([s.name, shortSupplierName(s.name)])].map(n => n.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|')})\\b`, 'i') }))
const mentions = (item: ChangeItem, supplierId: string) => supplierNamePatterns.find(p => p.id === supplierId)?.pattern.test(item.text) ?? false

/**
 * Groups rows that report one transaction so the counts show deals, not rows. Rows join when
 * `dealIds` links them, or when they share a date and a deal type and are about the same supplier
 * or name each other's supplier, with at least one ownership row among them. Every row stays in
 * the change log and the supplier's own history.
 */
/**
 * The deal a bare filing notice belongs to: the newest earlier acquisition or divestiture entry,
 * within nine months, that is about the same company or names it. A merger proxy filed weeks
 * after the announcement is a step in that deal, not a second deal.
 */
export function dealParent(item: ChangeItem, pool: ChangeItem[]): ChangeItem | null {
  if (!ownershipTypes.has(item.type) || !isFilingNotice(item.text)) return null
  return pool.filter(other => other.id !== item.id && ownershipTypes.has(other.type) && !isFilingNotice(other.text)
    && other.date <= item.date && ageInDays(other.date, item.date) <= 270
    && (other.supplierId === item.supplierId || mentions(other, item.supplierId)))
    .sort((a, b) => b.date.localeCompare(a.date) || a.id.localeCompare(b.id))[0] ?? null
}

export function countedUnits(items: ChangeItem[]): CountedUnit[] {
  const parent = new Map(items.map(item => [item.id, item.id]))
  const find = (id: string): string => { const p = parent.get(id)!; return p === id ? id : find(p) }
  const join = (a: string, b: string) => { parent.set(find(a), find(b)) }
  const deals = items.filter(item => dealTypes.has(item.type))
  for (const a of deals) for (const b of deals) {
    if (a.id >= b.id) continue
    const linked = dealIds[a.id] !== undefined && dealIds[a.id] === dealIds[b.id]
    const sameDay = a.date === b.date && (a.type !== 'funding' || b.type !== 'funding')
      && (a.supplierId === b.supplierId || mentions(a, b.supplierId) || mentions(b, a.supplierId))
    if (linked || sameDay) join(a.id, b.id)
  }
  for (const item of deals) { const earlier = dealParent(item, deals); if (earlier) join(item.id, earlier.id) }
  const clusters = new Map<string, ChangeItem[]>()
  for (const item of items) clusters.set(find(item.id), [...(clusters.get(find(item.id)) ?? []), item])
  return [...clusters.values()].map(members => {
    const sorted = members.slice().sort((a, b) => a.date.localeCompare(b.date) || a.id.localeCompare(b.id))
    const ownership = sorted.find(item => item.type === 'acquisition' || item.type === 'divestiture')
    return { key: sorted[0].id, groupId: groupIdFor((ownership ?? sorted[0]).type), date: sorted[0].date, items: sorted }
  })
}

export interface GrowthRow {
  supplier: TrackerSupplier
  latest: number
  prior: number | null
  /** ISO code when growth is measured in a currency other than US dollars, e.g. 'JPY'. */
  currency: string | null
}

const currencyNames: Record<string, string> = { JPY: 'Japanese yen', EUR: 'euros', GBP: 'British pounds', ILS: 'Israeli shekels', CAD: 'Canadian dollars' }
export const currencyName = (code: string) => currencyNames[code] ?? code

/** Reads the reporting currency from a growth basis such as "JPY net sales; ...". */
export function growthCurrency(basis: string | undefined): string | null {
  const code = basis?.match(/^([A-Z]{3})\b/)?.[1]
  return code && code !== 'USD' ? code : null
}

/** Public companies only. Segments, ARR and other own metrics are never mixed into this comparison. */
export function revenueGrowthRows(): GrowthRow[] {
  return trackerSuppliers.flatMap(supplier => {
    const latest = parseGrowthPercent(supplier.revenue?.latest.yoyGrowth)
    // Qualified strings describe bounds, not exact chart coordinates.
    if (supplier.kind !== 'public' || latest === null || !/^[+-]?\d+(?:\.\d+)?%$/.test(supplier.revenue!.latest.yoyGrowth)) return []
    const priorText = supplier.revenue?.prior?.yoyGrowth
    const prior = priorText && /^[+-]?\d+(?:\.\d+)?%$/.test(priorText) ? parseGrowthPercent(priorText) : null
    return [{ supplier, latest, prior, currency: growthCurrency(supplier.revenue!.latest.growthBasis) }]
  }).sort((a, b) => a.supplier.name.localeCompare(b.supplier.name))
}

export const secFilerCount = trackerSuppliers.filter(s => s.kind === 'public' && s.edgarId).length
export const secCollectedCount = edgarFacts.suppliers.filter(s => trackerSuppliers.some(t => t.kind === 'public' && t.edgarId === s.id)
  && !(edgarFacts.failures as { id: string }[]).some(f => f.id === s.id)).length
export const filingSeries = edgarFacts.suppliers

/** Year-over-year growth for each quarter that has the same quarter a year earlier in the SEC series, oldest first. */
export function quarterlyGrowth(edgarId: string): { periodEnd: string; growth: number; value: number }[] {
  const quarters = (filingSeries.find(s => s.id === edgarId)?.quarters ?? []).slice().sort((a, b) => a.periodEnd.localeCompare(b.periodEnd))
  return quarters.flatMap(q => {
    const end = Date.parse(q.periodEnd)
    const prior = quarters.find(p => Math.abs(Date.parse(p.periodEnd) - (end - 365 * 86_400_000)) <= 7 * 86_400_000)
    return prior ? [{ periodEnd: q.periodEnd, growth: Math.round((q.value / prior.value - 1) * 1000) / 10, value: q.value }] : []
  })
}
