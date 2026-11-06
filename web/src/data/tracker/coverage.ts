/**
 * Supplier coverage page (`/coverage/`). How much the site can say about a
 * supplier depends on what that supplier discloses: a US-listed company files
 * quarterly results with the SEC, a venture-backed startup announces funding
 * rounds, and a company owned by private equity or inside a larger company
 * usually publishes no financials of its own.
 *
 * Every tier below is derived from the data the page already carries for that
 * supplier, never hand-set: certification for tier 1, a revenue record for
 * tier 2, a funding round or a company-stated figure for tier 3, and nothing
 * financial for tier 4. A supplier moves tier on its own when its data changes.
 */
import { displayDomainIds } from './domains'
import edgarFacts from '../generated/edgarFacts.json' with { type: 'json' }
import { trackerDomains } from './domains'
import { retainedTrackerEvents } from './events'
import { isCertifiedSupplier } from './certification'
import { eventSummaryForSupplier, formatMonthYear, shortSupplierName } from './derive'
import { trackerSuppliers } from './suppliers'
import type { SupplierKind, TrackerSupplier } from './suppliers'

export type CoverageTierId = 'sec' | 'reported' | 'funding' | 'ownership'

export interface CoverageTier {
  id: CoverageTierId
  number: 1 | 2 | 3 | 4
  name: string
  /** Who lands in this tier, in one sentence. */
  who: string
  /** What the site shows for a supplier in this tier. */
  includes: string[]
  /** How the data stays current. */
  freshness: string
}

export const coverageTiers: CoverageTier[] = [
  {
    id: 'sec',
    number: 1,
    name: 'Revenue checked against SEC filings',
    who: 'Public companies that file quarterly reports with the US Securities and Exchange Commission.',
    includes: [
      'Quarterly revenue and the same quarter a year earlier',
      'Up to eight quarters of filed revenue',
      'The metric the company itself leads with, such as ARR',
      'Events filed with the SEC, plus acquisitions, layoffs, debt and leadership changes',
    ],
    freshness: 'Revenue figures are re-derived from SEC filings every day. New quarters appear once the company files.',
  },
  {
    id: 'reported',
    number: 2,
    name: 'Company-reported results',
    who: 'Public companies whose results are not in SEC structured data, such as foreign listings.',
    includes: [
      'Quarterly revenue and growth from the company’s own results releases',
      'The metric the company itself leads with',
      'Acquisitions, layoffs, debt and leadership changes',
    ],
    freshness: 'Each figure keeps its own source and date. It is not re-checked against a filing automatically.',
  },
  {
    id: 'funding',
    number: 3,
    name: 'Funding and company statements',
    who: 'Private companies that announce funding rounds or figures of their own. Private companies do not publish audited revenue.',
    includes: [
      'Latest funding round: date, stage, amount, lead investor and valuation when disclosed',
      'Figures the company states itself, such as ARR or growth, labelled as company-stated',
      'Acquisitions, layoffs, debt and leadership changes',
    ],
    freshness: 'Updated when the company or its investors announce something. Each fact keeps its own source and date.',
  },
  {
    id: 'ownership',
    number: 4,
    name: 'Ownership and events only',
    who: 'Companies owned by private equity, product lines inside a larger company, acquired companies, and private companies with no recent disclosure.',
    includes: [
      'Who owns it, and the deal terms when they were disclosed',
      'Dated events: acquisitions, debt and credit ratings, layoffs and leadership changes',
      'No revenue, because none is published for the company on its own',
    ],
    freshness: 'Updated when an owner, lender, rating agency or the company publishes something. Long gaps are normal.',
  },
]

export const supplierKindLabel: Record<SupplierKind, string> = {
  public: 'Public company',
  private: 'Venture-backed',
  'pe-owned': 'Private equity-owned',
  segment: 'Part of a larger company',
  acquired: 'Acquired',
}

export function coverageTierFor(supplier: TrackerSupplier): CoverageTierId {
  if (isCertifiedSupplier(supplier.id)) return 'sec'
  if (supplier.revenue) return 'reported'
  if (supplier.lastRound || supplier.headlineMetric) return 'funding'
  return 'ownership'
}

const secQuarterCount = new Map<string, number>(
  (edgarFacts.suppliers as Array<{ id: string; quarters: unknown[] }>).map((s) => [s.id, s.quarters.length]),
)

export interface CoverageRow {
  supplier: TrackerSupplier
  displayName: string
  tier: CoverageTierId
  typeLabel: string
  domains: string[]
  /** Short facts this supplier has on the site, in plain words. */
  holdings: string[]
  /** Newest dated fact the site holds for this supplier (YYYY-MM-DD or YYYY-MM), if any. */
  latestFact: string | null
  events12m: number
}

function holdingsFor(supplier: TrackerSupplier, tier: CoverageTierId, events12m: number): string[] {
  const out: string[] = []
  if (tier === 'sec') {
    const quarters = secQuarterCount.get(supplier.id) ?? 0
    out.push(`${quarters} quarters of SEC-filed revenue`)
  } else if (supplier.revenue) {
    out.push(`Quarterly revenue (${supplier.revenue.latest.period})`)
  }
  const metric = supplier.headlineMetric?.label
  if (metric && !/^(total )?revenue$/i.test(metric)) {
    out.push(tier === 'funding' && !/company-stated/i.test(metric) ? `${metric} (company-stated)` : metric)
  }
  if (supplier.lastRound) out.push(`Funding: ${supplier.lastRound.stage}, ${formatMonthYear(supplier.lastRound.date)}`)
  if (supplier.ownership && supplier.kind !== 'public' && supplier.kind !== 'private') out.push('Ownership record')
  out.push(events12m === 1 ? '1 event in 12 months' : `${events12m} events in 12 months`)
  return out
}

function latestFactFor(supplier: TrackerSupplier): string | null {
  const dates: string[] = []
  for (const event of retainedTrackerEvents) if (event.supplierId === supplier.id) dates.push(event.date)
  if (supplier.revenue) dates.push(supplier.revenue.latest.releaseDate || supplier.revenue.latest.periodEnd)
  if (supplier.lastRound) dates.push(supplier.lastRound.date)
  const valid = dates.filter((d) => /^\d{4}-\d{2}(-\d{2})?$/.test(d))
  return valid.length ? valid.sort().at(-1)! : null
}

const domainName = new Map(trackerDomains.map((d) => [d.id, d.name]))
const tierOrder: CoverageTierId[] = coverageTiers.map((t) => t.id)

export const coverageRows: CoverageRow[] = trackerSuppliers
  .map((supplier) => {
    const tier = coverageTierFor(supplier)
    const events12m = eventSummaryForSupplier(supplier.id).count
    return {
      supplier,
      displayName: shortSupplierName(supplier.name),
      tier,
      typeLabel: supplierKindLabel[supplier.kind],
      domains: displayDomainIds(supplier).map((id) => domainName.get(id) ?? id),
      holdings: holdingsFor(supplier, tier, events12m),
      latestFact: latestFactFor(supplier),
      events12m,
    }
  })
  .sort((a, b) => tierOrder.indexOf(a.tier) - tierOrder.indexOf(b.tier) || a.displayName.localeCompare(b.displayName))

export function rowsForTier(tier: CoverageTierId): CoverageRow[] {
  return coverageRows.filter((row) => row.tier === tier)
}

/** Count of suppliers of each company type in each tier, for the summary grid. */
export function typeTierCounts(): { kind: SupplierKind; label: string; counts: Record<CoverageTierId, number>; total: number }[] {
  const kinds: SupplierKind[] = ['public', 'private', 'pe-owned', 'segment', 'acquired']
  return kinds.map((kind) => {
    const rows = coverageRows.filter((row) => row.supplier.kind === kind)
    const counts = { sec: 0, reported: 0, funding: 0, ownership: 0 } as Record<CoverageTierId, number>
    for (const row of rows) counts[row.tier] += 1
    return { kind, label: supplierKindLabel[kind], counts, total: rows.length }
  })
}
