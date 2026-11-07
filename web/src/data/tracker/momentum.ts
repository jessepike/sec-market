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
import { revenueGrowthRows, yearChanges } from './presentation'
import type { ChangeItem } from './presentation'
import type { TrackerSupplier } from './suppliers'

export interface HealthFigure { value: number; periodEnd: string; sourceUrl: string; form: string }
export interface BalanceFigure { cash: number; debt: number; asOf: string; sourceUrl: string; form: string }
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
}

export interface OtherCompany {
  supplier: TrackerSupplier
  /** The company's own compact fact: last round, ownership, or a company-stated metric. */
  fact: string
  /** Its newest tracked event in the trailing 12 months, if any. */
  latestEvent: ChangeItem | null
  eventCount: number
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
        : supplier.headlineMetric && !supplier.lastRound ? `${supplier.headlineMetric.label} ${supplier.headlineMetric.value}` : formatOwnershipCompact(supplier)
    return { supplier, fact, latestEvent: own[0] ?? null, eventCount: own.length }
  })
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
    })).sort((a, b) => b.latest - a.latest || a.supplier.name.localeCompare(b.supplier.name))
    const list = others(domain.id, new Set(rows.map(r => r.supplier.id)))
    return { id: domain.id, name: domain.name, rows, median: med, revenueBars, others: list, otherGroups: groups(domain, list) }
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
