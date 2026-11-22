/**
 * Momentum by domain: who is growing faster or slower than the companies
 * they compete with. Pure data, no labels: each row is a certified SEC
 * filer's latest year-over-year revenue growth, the change from the quarter
 * before in percentage points, and the domain median as the benchmark.
 *
 * Growth comes only from certified suppliers (certification.ts). Companies
 * without certified figures are listed with their own sourced facts and
 * events, and the page says that financials are not available for them.
 */
import health from '../generated/healthFacts.json' with { type: 'json' }
import { isCertifiedSupplier } from './certification'
import { formatOwnershipCompact, suppliersForDomain } from './derive'
import { trackerDomains } from './domains'
import type { TrackerDomain } from './domains'
import { joinNames, shortSupplierName } from './names'
import { ageInDays, quarterlyGrowth, revenueGrowthRows, yearChanges } from './presentation'
import type { ChangeItem } from './presentation'
import type { TrackerSupplier } from './suppliers'

export interface HealthFigure { value: number; periodEnd: string; sourceUrl: string; form: string }
export interface BalanceFigure { cash: number; debt: number | null; asOf: string; sourceUrl: string; form: string }
export interface SupplierHealth {
  /** Operating income over revenue, trailing four quarters. */
  operatingMargin: HealthFigure | null
  /** (Operating cash flow minus capital expenditure) over revenue, trailing four quarters. */
  fcfMargin: HealthFigure | null
  /** Cash plus short-term investments, and carrying value of debt, at the latest balance sheet. */
  balance: BalanceFigure | null
}
interface HealthFile { generatedAt: string; method: Record<string, string>; suppliers: Record<string, SupplierHealth>; gaps: Record<string, string[]> }
export const healthFacts = health as unknown as HealthFile

export interface MomentumRow {
  supplier: TrackerSupplier
  /** Latest year-over-year revenue growth, percent. */
  latest: number
  /** Change from the prior quarter's year-over-year growth, percentage points; null with no prior figure. */
  change: number | null
  /** Latest growth minus the domain median, percentage points; null with no median. */
  vsMedian: number | null
  health: SupplierHealth | null
  /** Year-over-year growth for each quarter the SEC series can compare, oldest first. */
  trend: { periodEnd: string; growth: number }[]
  /** Revenue for the latest quarter in US dollars, from the SEC series. */
  revenue: number | null
  /** Tracked companies it bought between the year-ago quarter and the latest one. */
  bought: Bought[]
}

/** A tracked company a filer acquired, with the date the deal closed. */
export interface Bought { supplierId: string; name: string; closed: string }

/**
 * A public company whose growth comes from its own results release, not re-derived from SEC
 * filings (no `edgarId`, or a foreign filer). Drawn beside the certified rows with its own mark
 * and kept out of every median.
 */
export interface ReportedRow {
  supplier: TrackerSupplier
  /** Year-over-year revenue growth as the company reports it, percent. */
  latest: number
  /** Quarterly revenue in US dollars as the company reports it; null when the text does not parse. */
  revenue: number | null
  periodEnd: string
  /** The basis the company reports on, where it differs from US dollars. */
  basis: string | null
  bought: Bought[]
}

export interface OtherCompany {
  supplier: TrackerSupplier
  /** The company's own compact fact: last round, ownership, or a company-stated metric. */
  fact: string
  /** Its newest tracked event in the trailing 12 months, if any. */
  latestEvent: ChangeItem | null
  eventCount: number
  /** The date of the newest dated public fact on file: an event, a round, an ownership change or a dated company figure. */
  signalDate: string | null
}

export interface OtherGroup {
  /** Sub-area id and name; null for a domain without sub-areas. */
  id: string | null
  name: string | null
  scope: string | null
  companies: OtherCompany[]
}

export interface DomainMomentum {
  id: string
  name: string
  rows: MomentumRow[]
  /** Company-reported growth of public companies outside the SEC check, highest first. Not in `median`. */
  reported: ReportedRow[]
  median: number | null
  /** False when the domain shows no revenue bars (domains.ts `revenueBars`). */
  revenueBars: boolean
  others: OtherCompany[]
  /** The same companies as `others`, grouped by sub-area when the domain has them. */
  otherGroups: OtherGroup[]
}

const median = (values: number[], min = 2): number | null => {
  if (values.length < min) return null
  const s = values.slice().sort((a, b) => a - b)
  const mid = Math.floor(s.length / 2)
  return s.length % 2 ? s[mid] : (s[mid - 1] + s[mid]) / 2
}
const round1 = (n: number) => Math.round(n * 10) / 10

/** Certified growth rows: public SEC filers only, never a company release or a segment. */
export const certifiedGrowth = revenueGrowthRows().filter(r => isCertifiedSupplier(r.supplier.id))
export const marketMedian = median(certifiedGrowth.map(r => r.latest))

/** "+6.4%" -> 6.4, "-1.1%" -> -1.1; null for anything else. */
export function parseGrowth(text: string): number | null {
  const m = /^([+\-−]?)(\d+(?:\.\d+)?)%$/.exec(text.trim())
  return m ? (m[1] === '-' || m[1] === '−' ? -1 : 1) * Number(m[2]) : null
}
/** "$1,122.0 million" -> 1_122_000_000, "$2.1 billion" -> 2_100_000_000; null for anything else. */
export function parseUsd(text: string): number | null {
  const m = /^\$([\d,]+(?:\.\d+)?)\s*(million|billion)$/i.exec(text.trim())
  return m ? Number(m[1].replace(/,/g, '')) * (m[2].toLowerCase() === 'billion' ? 1e9 : 1e6) : null
}

/** Public companies with whole-company revenue growth from their own release and no certified figures. */
export function reportedGrowth(domainId: string): ReportedRow[] {
  return suppliersForDomain(domainId).flatMap(supplier => {
    const rev = supplier.revenue
    if (supplier.kind !== 'public' || !rev || rev.scope === 'segment' || isCertifiedSupplier(supplier.id)) return []
    const latest = parseGrowth(rev.latest.yoyGrowth)
    if (latest === null) return []
    return [{ supplier, latest, revenue: parseUsd(rev.latest.value), periodEnd: rev.latest.periodEnd, basis: rev.latest.growthBasis ?? null, bought: boughtWithin(supplier, rev.latest.periodEnd) }]
  }).sort((a, b) => b.latest - a.latest || a.supplier.name.localeCompare(b.supplier.name))
}

const roster = trackerDomains.flatMap(d => suppliersForDomain(d.id)).filter((s, i, all) => all.findIndex(o => o.id === s.id) === i)
const yearBefore = (date: string) => `${Number(date.slice(0, 4)) - 1}${date.slice(4)}`
/**
 * Tracked companies the supplier acquired whose deal closed after the year-ago quarter ended and on
 * or before the latest quarter end: the latest quarter holds their revenue and the year-ago quarter
 * does not. Matched on the acquirer named in each company's own ownership record.
 */
export function boughtWithin(supplier: TrackerSupplier, periodEnd: string | undefined): Bought[] {
  if (!periodEnd || !/^\d{4}-\d{2}-\d{2}$/.test(periodEnd)) return []
  const buyer = shortSupplierName(supplier.name)
  const from = yearBefore(periodEnd)
  return roster.filter(m => m.id !== supplier.id && m.ownership?.acquirer && shortSupplierName(m.ownership.acquirer) === buyer
    && !!m.ownership.closed && /^\d{4}-\d{2}-\d{2}$/.test(m.ownership.closed) && m.ownership.closed > from && m.ownership.closed <= periodEnd)
    .map(m => ({ supplierId: m.id, name: shortSupplierName(m.name), closed: m.ownership!.closed! }))
    .sort((a, b) => a.closed.localeCompare(b.closed) || a.name.localeCompare(b.name))
}

const yearItems = yearChanges().filter(item => item.type !== 'filing')

function others(domainId: string, ranked: Set<string>): OtherCompany[] {
  const members = suppliersForDomain(domainId)
  return members.filter(s => !ranked.has(s.id)).map(supplier => {
    const own = yearItems.filter(item => item.supplierId === supplier.id)
    // A public filer listed without a bar: name the companies in this domain it bought, from their own ownership records.
    const bought = supplier.kind === 'public'
      ? members.filter(m => m.id !== supplier.id && m.ownership?.status.startsWith(`Acquired by ${shortSupplierName(supplier.name)}`)).map(m => shortSupplierName(m.name))
      : []
    const fact = bought.length > 0
      ? `Public company. Bought ${joinNames(bought)}`
      : supplier.revenue && !isCertifiedSupplier(supplier.id)
        ? `${supplier.revenue.latest.yoyGrowth} revenue growth, company-reported`
        : supplier.headlineMetric && !supplier.lastRound ? `${supplier.headlineMetric.label} ${supplier.headlineMetric.value}`
          // A short company-stated figure rides beside the last round; a long one stays on the company page.
          : supplier.headlineMetric && supplier.headlineMetric.value.length <= 40 ? `${formatOwnershipCompact(supplier)} · ${supplier.headlineMetric.label.replace(/ \(company-stated[^)]*\)/, '')} ${supplier.headlineMetric.value}, company-stated`
            : formatOwnershipCompact(supplier)
    return { supplier, fact, latestEvent: own[0] ?? null, eventCount: own.length, signalDate: signalDate(supplier, own[0]?.date) }
  }).sort((a, b) => (b.signalDate ?? '').localeCompare(a.signalDate ?? '') || a.supplier.name.localeCompare(b.supplier.name))
}

const fullDate = (d: string | undefined) => !d ? null : /^\d{4}-\d{2}$/.test(d) ? `${d}-01` : /^\d{4}-\d{2}-\d{2}$/.test(d) ? d : null
/** The newest dated public fact held for a company. A company figure counts only when its period carries a full date. */
export function signalDate(supplier: TrackerSupplier, latestEvent?: string): string | null {
  const dates = [latestEvent, supplier.lastRound?.date, supplier.ownership?.closed, supplier.ownership?.announced,
    supplier.headlineMetric?.period.match(/\d{4}-\d{2}-\d{2}/)?.[0], supplier.revenue?.latest.releaseDate].map(fullDate).filter((d): d is string => d !== null)
  return dates.sort().at(-1) ?? null
}

/** "this month", "4 months ago", "1 year ago", "5 years ago": whole units, rounded down. */
export function signalAge(date: string, asOf?: string): string {
  const months = Math.floor(ageInDays(date, asOf) / 30.44)
  if (months < 1) return 'this month'
  if (months < 12) return `${months} ${months === 1 ? 'month' : 'months'} ago`
  const years = Math.floor(months / 12)
  return `${years} ${years === 1 ? 'year' : 'years'} ago`
}

function groups(domain: TrackerDomain, list: OtherCompany[]): OtherGroup[] {
  if (!domain.subareas) return list.length ? [{ id: null, name: null, scope: null, companies: list }] : []
  const byId = new Map(list.map(o => [o.supplier.id, o]))
  const out: OtherGroup[] = domain.subareas.map(a => ({ id: a.id, name: a.name, scope: a.scope, companies: a.supplierIds.flatMap(id => byId.get(id) ?? []) }))
  const placed = new Set(domain.subareas.flatMap(a => a.supplierIds))
  const rest = list.filter(o => !placed.has(o.supplier.id))
  if (rest.length) out.push({ id: 'other', name: 'Other', scope: null, companies: rest })
  return out.filter(g => g.companies.length > 0)
}

function series(supplier: TrackerSupplier): Pick<MomentumRow, 'trend' | 'revenue'> {
  const quarters = supplier.edgarId ? quarterlyGrowth(supplier.edgarId) : []
  const latest = quarters.find(q => q.periodEnd === supplier.revenue?.latest.periodEnd)
  return { trend: quarters.slice(-8).map(({ periodEnd, growth }) => ({ periodEnd, growth })), revenue: latest?.value ?? null }
}

/** One block per domain, in the site's domain order. Rows are ranked by latest growth, highest first. */
export function domainMomentum(): DomainMomentum[] {
  return trackerDomains.map(domain => {
    const members = new Set(suppliersForDomain(domain.id).map(s => s.id))
    const revenueBars = domain.revenueBars !== false
    const growth = revenueBars ? certifiedGrowth.filter(r => members.has(r.supplier.id)) : []
    // A median of two filers reads as a domain signal it is not; shown from three.
    const med = median(growth.map(r => r.latest), 3)
    const rows = growth.map(r => ({
      supplier: r.supplier,
      latest: r.latest,
      change: r.prior === null ? null : round1(r.latest - r.prior),
      vsMedian: med === null ? null : round1(r.latest - med),
      health: healthFacts.suppliers[r.supplier.id] ?? null,
      ...series(r.supplier),
      bought: boughtWithin(r.supplier, r.supplier.revenue?.latest.periodEnd),
    })).sort((a, b) => b.latest - a.latest || a.supplier.name.localeCompare(b.supplier.name))
    // Company-reported rows sit beside certified ones only where the domain draws bars and has a filer to compare with.
    const reported = revenueBars && rows.length > 0 ? reportedGrowth(domain.id) : []
    const list = others(domain.id, new Set([...rows, ...reported].map(r => r.supplier.id)))
    return { id: domain.id, name: domain.name, rows, reported, median: med, revenueBars, others: list, otherGroups: groups(domain, list) }
  })
}

/** "+3.4 pts", "-0.2 pts", "0.0 pts". */
export const formatPoints = (n: number) => `${n > 0 ? '+' : n < 0 ? '−' : ''}${Math.abs(n).toFixed(1)} pts`
/** "+25.8%", "−1.5%". */
export const formatPercent = (n: number) => `${n > 0 ? '+' : n < 0 ? '−' : ''}${Math.abs(n).toFixed(1)}%`
/** 4_210_000_000 -> "$4.2B", 640_000_000 -> "$640M". */
export function formatUsd(n: number): string {
  const a = Math.abs(n)
  const text = a >= 1e9 ? `$${(a / 1e9).toFixed(1)}B` : a >= 1e6 ? `$${Math.round(a / 1e6)}M` : `$${Math.round(a).toLocaleString('en-US')}`
  return n < 0 ? `−${text}` : text
}

/** Cash minus debt, signed: "+$3.2B", "−$1.1B". */
export const formatNetCash = (cash: number, debt: number) => `${cash - debt >= 0 ? '+' : ''}${formatUsd(cash - debt)}`
