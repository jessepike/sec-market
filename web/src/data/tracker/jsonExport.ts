import type { EvidenceRecord } from '../types'
import type { RunStatus } from '../runStatus'
import type { TrackerDomain } from './domains'
import type { SupplierKind, TrackerSupplier } from './suppliers'

/**
 * The machine-readable `/tracker.json` export (AUTO-001 fix pass 4, item
 * 10). Every figure on the live tracker table — a headline metric, a
 * revenue reading, a last funding round, an ownership fact — gets one row
 * here with a stable id, its value, its period/as-of date, and the source
 * URL(s) it is cited to. A program that wants the tracker's facts reads this
 * file; it never has to parse the rendered HTML.
 *
 * Pure builder, no file I/O — mirrors correctionsJsonPayload
 * (correctionHelpers.ts): a payload function here, a thin writer in
 * generate-feed.ts, and a matching identity check in verify-dist.ts, so the
 * writer and its checker cannot compute the shape two different ways.
 */

export type TrackerFigureType = 'headline-metric' | 'revenue-latest' | 'revenue-prior' | 'last-round' | 'ownership'

export interface TrackerFigure {
  id: string
  supplierId: string
  type: TrackerFigureType
  label: string
  value: string
  /** The reporting period or as-of date this value is true for — never the run date. */
  period: string
  sourceUrls: string[]
}

export interface TrackerJsonDomain {
  id: string
  name: string
  scope: string
}

export interface TrackerJsonSupplier {
  id: string
  name: string
  domainIds: string[]
  kind: SupplierKind
}

export interface TrackerJsonPayload {
  generatedAt: string
  runStatus: {
    lastChecked: string
    state: RunStatus['state']
    detail?: string
  }
  domains: TrackerJsonDomain[]
  suppliers: TrackerJsonSupplier[]
  figures: TrackerFigure[]
}

/** Evidence ids resolved to their canonical source URLs, duplicates and blanks dropped, in citation order. */
function sourceUrlsFor(evidenceIds: string[], evidenceByIdMap: Record<string, EvidenceRecord>): string[] {
  const seen = new Set<string>()
  const urls: string[] = []
  for (const id of evidenceIds) {
    const url = evidenceByIdMap[id]?.canonicalUrl
    if (url && !seen.has(url)) {
      seen.add(url)
      urls.push(url)
    }
  }
  return urls
}

function figuresForSupplier(
  supplier: TrackerSupplier,
  evidenceByIdMap: Record<string, EvidenceRecord>,
): TrackerFigure[] {
  const figures: TrackerFigure[] = []

  if (supplier.headlineMetric) {
    const metric = supplier.headlineMetric
    figures.push({
      id: `${supplier.id}-headline`,
      supplierId: supplier.id,
      type: 'headline-metric',
      label: metric.label,
      value: metric.value,
      period: metric.period,
      sourceUrls: sourceUrlsFor(metric.evidenceIds, evidenceByIdMap),
    })
  }

  if (supplier.revenue?.latest) {
    const latest = supplier.revenue.latest
    figures.push({
      id: `${supplier.id}-revenue-latest`,
      supplierId: supplier.id,
      type: 'revenue-latest',
      label: 'Revenue',
      value: latest.value,
      period: latest.period,
      sourceUrls: sourceUrlsFor(latest.evidenceIds, evidenceByIdMap),
    })
  }

  if (supplier.revenue?.prior) {
    const prior = supplier.revenue.prior
    figures.push({
      id: `${supplier.id}-revenue-prior`,
      supplierId: supplier.id,
      type: 'revenue-prior',
      label: 'Revenue (prior quarter)',
      value: prior.value,
      period: prior.period,
      sourceUrls: sourceUrlsFor(prior.evidenceIds, evidenceByIdMap),
    })
  }

  if (supplier.lastRound) {
    const round = supplier.lastRound
    figures.push({
      id: `${supplier.id}-last-round`,
      supplierId: supplier.id,
      type: 'last-round',
      label: `Last funding round (${round.stage})`,
      value: round.amount,
      period: round.date,
      sourceUrls: sourceUrlsFor(round.evidenceIds, evidenceByIdMap),
    })
  }

  if (supplier.ownership) {
    const ownership = supplier.ownership
    figures.push({
      id: `${supplier.id}-ownership`,
      supplierId: supplier.id,
      type: 'ownership',
      label: 'Ownership',
      value: ownership.relationship ?? ownership.status,
      period: ownership.closed ?? ownership.announced ?? '',
      sourceUrls: sourceUrlsFor(ownership.evidenceIds, evidenceByIdMap),
    })
  }

  return figures
}

export function trackerJsonPayload(
  suppliers: TrackerSupplier[],
  domains: TrackerDomain[],
  evidenceByIdMap: Record<string, EvidenceRecord>,
  status: RunStatus,
): TrackerJsonPayload {
  return {
    generatedAt: status.lastChecked,
    runStatus: {
      lastChecked: status.lastChecked,
      state: status.state,
      ...(status.detail ? { detail: status.detail } : {}),
    },
    domains: domains.map((domain) => ({ id: domain.id, name: domain.name, scope: domain.scope })),
    suppliers: suppliers.map((supplier) => ({
      id: supplier.id,
      name: supplier.name,
      domainIds: supplier.domainIds,
      kind: supplier.kind,
    })),
    figures: suppliers.flatMap((supplier) => figuresForSupplier(supplier, evidenceByIdMap)),
  }
}
