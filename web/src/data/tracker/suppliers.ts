import { effectiveManualTrackerSuppliers } from './correctionData'
import { withEdgarRevenue } from './edgarRevenue'
import { withReleaseRevenue } from './releaseRevenue'
import { withDailyData } from './daily'
/**
 * Tracked suppliers — step 5 of the autonomy plan
 * (docs/archive/2026-10-refresh-gate/autonomy-coverage-plan.md §4–5, D-76/D-77). One record per
 * declared supplier, sourced from docs/archive/2026-10-refresh-gate/auto-001/step5/research/coverage-g{1,2,3}.md
 * (~80 suppliers across the twelve domains in domains.ts). `id` reuses an
 * existing print id (prints.ts, stripped of "print-") or EDGAR registry id
 * (edgarRegistry.ts) where one already exists, so the data sets join without
 * a remapping table. Every fact-bearing field cites evidence in evidence.ts
 * with a real source URL — see web/scripts/verify-tracker.ts, the build
 * gate that enforces this.
 */

export interface HeadlineMetric {
  label: string
  value: string
  period: string
  evidenceIds: string[]
}

export interface RevenuePeriod {
  value: string
  /** Same quarter, one year earlier — the figure `yoyGrowth` is computed from. AUTO-001 fix pass 4, item 6. */
  priorYearValue?: string
  yoyGrowth: string
  /** Company's reporting currency/basis where it differs from the displayed equivalent. */
  growthBasis?: string
  period: string
  periodEnd: string
  evidenceIds: string[]
}

export interface RevenuePeriodLatest extends RevenuePeriod {
  releaseDate: string
}

export interface SupplierRevenue {
  /** Separate segment figures require explicit source-backed scope. */
  scope?: 'company' | 'segment'
  latest: RevenuePeriodLatest
  /** Absent when the research found no comparable prior-quarter figure (e.g. an unbroken-out segment). */
  prior?: RevenuePeriod
}

export interface FundingRound {
  /** Full "YYYY-MM-DD", or "YYYY-MM" when the sourced evidence only gave a month. */
  date: string
  stage: string
  amount: string
  /** Absent when no lead investor was disclosed in the sourced evidence. */
  lead?: string
  valuation?: string
  evidenceIds: string[]
}

export interface Ownership {
  status: string
  acquirer?: string
  announced?: string
  closed?: string
  price?: string
  /**
   * Overrides the kind-derived compact label ("Acquired by X", "PE-owned ·
   * X") with the primary source's own wording, for a relationship the
   * generic template would misstate — e.g. a majority investment that is
   * not a full acquisition (Dragos/Accenture, AUTO-001 fix pass 4, item 3).
   * Plain text, no judgment words; `formatOwnershipCompact` (derive.ts)
   * appends the date the same way it would for the generic template.
   */
  relationship?: string
  evidenceIds: string[]
}

export type SupplierKind = 'public' | 'private' | 'pe-owned' | 'segment' | 'acquired'

export interface TrackerSupplier {
  id: string
  name: string
  domainIds: string[]
  kind: SupplierKind
  ticker?: string
  cik?: string
  edgarId?: string
  headlineMetric?: HeadlineMetric
  revenue?: SupplierRevenue
  lastRound?: FundingRound
  ownership?: Ownership
}

export { originalManualTrackerSuppliers as manualTrackerSuppliers } from './correctionData'


// Displayed SEC revenue follows checked structured facts; collector-owned claims stay manual.
export const trackerSuppliers = effectiveManualTrackerSuppliers.map(withDailyData).map(withEdgarRevenue).map(withReleaseRevenue)
