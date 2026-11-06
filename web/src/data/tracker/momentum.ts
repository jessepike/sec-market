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

export interface DomainMomentum {
  id: string
  name: string
  rows: MomentumRow[]
  median: number | null
  others: OtherCompany[]
}

const median = (values: number[]): number | null => {
  if (values.length < 2) return null
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
  return suppliersForDomain(domainId).filter(s => !ranked.has(s.id)).map(supplier => {
    const own = yearItems.filter(item => item.supplierId === supplier.id)
    const fact = supplier.revenue && !isCertifiedSupplier(supplier.id)
      ? `${supplier.revenue.latest.yoyGrowth} revenue growth, company-reported`
      : supplier.headlineMetric && !supplier.lastRound ? `${supplier.headlineMetric.label} ${supplier.headlineMetric.value}` : formatOwnershipCompact(supplier)
    return { supplier, fact, latestEvent: own[0] ?? null, eventCount: own.length }
  })
}

/** One block per domain, in the site's domain order. Rows are ranked by latest growth, highest first. */
export function domainMomentum(): DomainMomentum[] {
  return trackerDomains.map(domain => {
    const members = new Set(suppliersForDomain(domain.id).map(s => s.id))
    const growth = certifiedGrowth.filter(r => members.has(r.supplier.id))
    const med = median(growth.map(r => r.latest))
    const rows = growth.map(r => ({
      supplier: r.supplier,
      latest: r.latest,
      change: r.prior === null ? null : round1(r.latest - r.prior),
      vsMedian: med === null ? null : round1(r.latest - med),
      health: healthFacts.suppliers[r.supplier.id] ?? null,
    })).sort((a, b) => b.latest - a.latest || a.supplier.name.localeCompare(b.supplier.name))
    return { id: domain.id, name: domain.name, rows, median: med, others: others(domain.id, new Set(rows.map(r => r.supplier.id))) }
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
