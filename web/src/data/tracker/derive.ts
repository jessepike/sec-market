/**
 * Pure helpers over the tracker data (domains.ts, suppliers.ts, events.ts).
 * Kept separate from the components so the logic can be unit-tested without
 * rendering React — see tests/tracker-data.test.ts.
 */
import { trackerEvents } from './events'
import { trackerSuppliers } from './suppliers'
import type { TrackerEvent } from './events'
import type { TrackerSupplier } from './suppliers'

/** Suppliers assigned to a domain, alphabetical by name — the front page's default order. */
export function suppliersForDomain(domainId: string): TrackerSupplier[] {
  return trackerSuppliers
    .filter((supplier) => supplier.domainIds.includes(domainId))
    .slice()
    .sort((a, b) => a.name.localeCompare(b.name))
}

/** Parses a leading "+26%" / "-5.2%" / "26%" style string into a signed number, or null if unparseable. */
export function parseGrowthPercent(value: string | undefined): number | null {
  if (!value) return null
  const match = value.match(/(-?\+?\d+(\.\d+)?)\s*%/)
  if (!match) return null
  const num = Number(match[1].replace('+', ''))
  return Number.isFinite(num) ? num : null
}

/** Median of the latest reported YoY revenue growth across a domain's public suppliers, or null with fewer than 2. */
export function medianRevenueGrowthForDomain(domainId: string): number | null {
  const values = suppliersForDomain(domainId)
    .filter((supplier) => supplier.kind === 'public' || supplier.kind === 'segment')
    .map((supplier) => parseGrowthPercent(supplier.revenue?.latest.yoyGrowth))
    .filter((value): value is number => value !== null)
  if (values.length < 2) return null
  const sorted = values.slice().sort((a, b) => a - b)
  const mid = Math.floor(sorted.length / 2)
  return sorted.length % 2 === 0 ? (sorted[mid - 1] + sorted[mid]) / 2 : sorted[mid]
}

/** Events for one supplier, newest first. */
export function eventsForSupplier(supplierId: string): TrackerEvent[] {
  return trackerEvents
    .filter((event) => event.supplierId === supplierId)
    .slice()
    .sort((a, b) => (a.date < b.date ? 1 : a.date > b.date ? -1 : 0))
}

/** Count of events in the trailing 12 months for one supplier, and the newest one if any. */
export function eventSummaryForSupplier(supplierId: string): { count: number; latest: TrackerEvent | null } {
  const events = eventsForSupplier(supplierId)
  return { count: events.length, latest: events[0] ?? null }
}

function daysBetween(earlier: string, later: string): number {
  const [ey, em, ed] = earlier.split('-').map(Number)
  const [ly, lm, ld] = later.split('-').map(Number)
  const earlierMs = Date.UTC(ey, em - 1, ed)
  const laterMs = Date.UTC(ly, lm - 1, ld)
  return Math.round((laterMs - earlierMs) / 86_400_000)
}

/** Tracker events dated within the 30 days ending on `today` (inclusive), newest first. */
export function eventsInLast30Days(today: string): TrackerEvent[] {
  return trackerEvents
    .filter((event) => {
      const age = daysBetween(event.date, today)
      return age >= 0 && age <= 30
    })
    .slice()
    .sort((a, b) => (a.date < b.date ? 1 : a.date > b.date ? -1 : 0))
}

export interface EdgarFiling {
  supplierId: string
  periodEnd: string
  filedDate: string
  form: string
  value: number
  sourceUrl: string
}

interface EdgarFactsFile {
  generatedAt: string
  suppliers: Array<{
    id: string
    name: string
    cik: string
    quarters: Array<{
      periodEnd: string
      filedDate: string
      form: string
      value: number
      sourceUrl: string
    }>
  }>
}

/** EDGAR-filed quarters (from generated/edgarFacts.json) with a filing date within 30 days of `today`. */
export function edgarFilingsInLast30Days(today: string, facts: EdgarFactsFile): EdgarFiling[] {
  const out: EdgarFiling[] = []
  for (const supplier of facts.suppliers) {
    for (const quarter of supplier.quarters) {
      const age = daysBetween(quarter.filedDate, today)
      if (age >= 0 && age <= 30) {
        out.push({
          supplierId: supplier.id,
          periodEnd: quarter.periodEnd,
          filedDate: quarter.filedDate,
          form: quarter.form,
          value: quarter.value,
          sourceUrl: quarter.sourceUrl,
        })
      }
    }
  }
  return out.sort((a, b) => (a.filedDate < b.filedDate ? 1 : a.filedDate > b.filedDate ? -1 : 0))
}
