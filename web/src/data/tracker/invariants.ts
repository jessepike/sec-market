/**
 * Site invariants: checks that the numbers a reader sees agree with each other.
 *
 * Every figure comes from the same functions the page uses (presentation.ts, derive.ts,
 * deals.ts), so a rule can only fail when the page itself would show something inconsistent.
 * `checkSiteInvariants` reads the live data. `checkInvariants` takes the data as an argument so
 * tests can feed it a crafted bad case and prove each rule fires.
 *
 * Rules the data model cannot express: none are skipped. Two are limited by what the data
 * holds, noted in place: rule 3 can only judge growth whose basis text names a currency, and
 * rule 5 checks that a source link exists in the data, not that the URL still loads.
 */
import edgarFacts from '../generated/edgarFacts.json' with { type: 'json' }
import { evidenceById } from '../evidence'
import { runStatus } from '../runStatus'
import { dealIds } from './deals'
import { shortSupplierName } from './derive'
import { countedUnits, eventGroups, recentChanges, revenueGrowthRows, secFilingsInLastYear, yearChanges } from './presentation'
import type { ChangeItem, CountedUnit, GrowthRow } from './presentation'
import { trackerSuppliers } from './suppliers'

export interface Violation { rule: string; detail: string }

export interface SiteData {
  /** The date the page's windows end on (runStatus.lastChecked). */
  asOf: string
  monthChanges: ChangeItem[]
  yearChanges: ChangeItem[]
  monthUnits: CountedUnit[]
  yearUnits: CountedUnit[]
  growthRows: GrowthRow[]
  dealLinks: Record<string, string>
  /** Supplier id -> names the page recognises in event text. */
  supplierNames: Record<string, string[]>
  sourceUrl: (evidenceId: string) => string | undefined
  /** Every SEC filing date the data holds. */
  filingDates: { supplierId: string; filedDate: string }[]
}

const R1 = 'tile-count-matches-list'
const R2 = 'one-deal-counts-once'
const R3 = 'non-usd-growth-has-currency'
const R4 = 'no-future-dates'
const R5 = 'every-event-has-source'

export function liveSiteData(): SiteData {
  const monthChanges = recentChanges()
  const yearItems = yearChanges()
  return {
    asOf: runStatus.lastChecked,
    monthChanges, yearChanges: yearItems,
    monthUnits: countedUnits(monthChanges), yearUnits: countedUnits(yearItems),
    growthRows: revenueGrowthRows(),
    dealLinks: dealIds,
    supplierNames: Object.fromEntries(trackerSuppliers.map(s => [s.id, [...new Set([s.name, shortSupplierName(s.name)])]])),
    sourceUrl: id => evidenceById[id]?.canonicalUrl,
    filingDates: [
      ...edgarFacts.suppliers.flatMap(s => s.quarters.map(q => ({ supplierId: s.id, filedDate: q.filedDate }))),
      ...secFilingsInLastYear().map(f => ({ supplierId: f.supplierId, filedDate: f.filedDate })),
    ],
  }
}

export function checkSiteInvariants(now: string = new Date().toISOString().slice(0, 10)): Violation[] {
  return checkInvariants(liveSiteData(), now)
}

const escapeRe = (s: string) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
const isHttp = (url: string | undefined) => !!url && /^https?:\/\/\S+$/.test(url)
const label = (item: ChangeItem) => `${item.id} (${item.supplierId}, ${item.date}, ${item.type})`

export function checkInvariants(data: SiteData, now: string): Violation[] {
  const out: Violation[] = []
  const add = (rule: string, detail: string) => out.push({ rule, detail })
  const inGroup = (units: CountedUnit[], groupId: string) => units.filter(u => u.groupId === groupId)

  // Rule 1: tile counts agree with the change log and the 12-month grid.
  // The log, filtered to a type, lists every row of the units in that type. A deal reported by
  // several rows is several log rows but one count, so the log is compared by distinct deal.
  const unitOfRow = new Map<string, CountedUnit>()
  for (const unit of data.monthUnits) for (const item of unit.items) unitOfRow.set(item.id, unit)
  let loggedRows = 0
  for (const group of eventGroups) {
    const units = inGroup(data.monthUnits, group.id)
    const logRows = units.flatMap(u => u.items)
    loggedRows += logRows.length
    const logDeals = new Set(logRows.map(item => unitOfRow.get(item.id)!.key)).size
    if (logDeals !== units.length) add(R1, `${group.label}: 30-day tile shows ${units.length} but the filtered change log lists ${logDeals} distinct entries`)
    for (const item of logRows) {
      if (data.monthChanges.filter(c => c.id === item.id).length !== 1) add(R1, `${group.label}: log row ${label(item)} is not in the 30-day change log exactly once`)
    }
  }
  if (loggedRows !== data.monthChanges.length) {
    add(R1, `30-day change log has ${data.monthChanges.length} rows but the type filters together show ${loggedRows}`)
  }

  const start = new Date(Date.parse(data.asOf) - 365 * 86_400_000)
  const months: string[] = []
  for (const d = new Date(Date.UTC(start.getUTCFullYear(), start.getUTCMonth(), 1)); d.toISOString().slice(0, 7) <= data.asOf.slice(0, 7); d.setUTCMonth(d.getUTCMonth() + 1)) {
    months.push(d.toISOString().slice(0, 7))
  }
  for (const group of eventGroups) {
    const units = inGroup(data.yearUnits, group.id)
    const gridTotal = months.reduce((sum, month) => sum + units.filter(u => u.date.startsWith(month)).length, 0)
    if (gridTotal !== units.length) add(R1, `${group.label}: 12-month tile shows ${units.length} but the grid row sums to ${gridTotal}`)
  }

  // Rule 2: a transaction counts once. No two separately counted deal units may be the same deal.
  const dealTypes = new Set(['acquisition', 'divestiture', 'funding'])
  const mentions = (item: ChangeItem, supplierId: string) =>
    (data.supplierNames[supplierId] ?? []).some(n => new RegExp(`\\b${escapeRe(n)}\\b`, 'i').test(item.text))
  for (const units of [data.monthUnits, data.yearUnits]) {
    const dealUnits = units.filter(u => u.items.some(i => dealTypes.has(i.type)))
    for (let i = 0; i < dealUnits.length; i++) for (let j = i + 1; j < dealUnits.length; j++) {
      const a = dealUnits[i], b = dealUnits[j]
      for (const x of a.items.filter(it => dealTypes.has(it.type))) for (const y of b.items.filter(it => dealTypes.has(it.type))) {
        const linked = data.dealLinks[x.id] !== undefined && data.dealLinks[x.id] === data.dealLinks[y.id]
        const sameDay = x.date === y.date && (x.type !== 'funding' || y.type !== 'funding')
          && (x.supplierId === y.supplierId || mentions(x, y.supplierId) || mentions(y, x.supplierId))
        if (linked || sameDay) add(R2, `${label(x)} and ${label(y)} describe one deal but are counted as two`)
      }
    }
  }

  // Rule 3: growth in a non-USD currency carries its code. Only growth whose basis text names a
  // currency can be judged; a basis that says nothing is treated as the company's own currency
  // being unstated, which the data cannot tell apart from USD.
  for (const row of data.growthRows) {
    const basis = row.supplier.revenue?.latest.growthBasis
    const named = basis?.match(/^([A-Z]{3})\b/)?.[1]
    if (named && named !== 'USD' && row.currency !== named) {
      add(R3, `${row.supplier.name}: growth basis says ${named} but the chart value carries ${row.currency ?? 'no currency code'}`)
    }
    if (row.currency && row.currency === 'USD') add(R3, `${row.supplier.name}: USD growth should not carry a currency tag`)
  }

  // Rule 4: nothing is dated after today.
  const future = (date: string) => date > now
  for (const item of data.yearChanges) {
    if (future(item.date)) add(R4, `${label(item)} is dated after ${now}`)
    for (const f of item.filings) if (future(f.filedDate)) add(R4, `${item.supplierId} filing ${f.sourceUrl} filed ${f.filedDate}, after ${now}`)
  }
  for (const f of data.filingDates) if (future(f.filedDate)) add(R4, `${f.supplierId} SEC filing dated ${f.filedDate}, after ${now}`)

  // Rule 5: every displayed event has a source link (an evidence record with an http(s) URL, or an SEC filing URL).
  // This checks the link exists in the data, not that the page behind it still loads.
  for (const item of data.yearChanges) {
    const urls = [...item.evidenceIds.map(data.sourceUrl), ...item.filings.map(f => f.sourceUrl)]
    if (!urls.some(isHttp)) add(R5, `${label(item)} has no source URL`)
    for (const id of item.evidenceIds) if (!isHttp(data.sourceUrl(id))) add(R5, `${label(item)} cites evidence ${id} that has no usable URL`)
  }
  return out
}
