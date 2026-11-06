import type { EvidenceRecord } from '../types'
import type { RunStatus } from '../runStatus'
import type { TrackerDomain } from './domains'
import type { SupplierKind, TrackerSupplier } from './suppliers'
import { isCertifiedSupplier, receiptComplete } from './certification'
import { DATA_LICENSE, DATA_LICENSE_URL, SITE_URL } from '../meta'

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
  /** Publication date of each cited source, in the same order as sourceUrls. */
  sourceDates: string[]
  /**
   * True only for SEC revenue that the certification gate re-derived from the
   * company's own filings (D-100). Every other figure keeps its own source and
   * date and is not re-checked automatically.
   */
  certified: boolean
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
  about: string
  license: string
  licenseUrl: string
  documentation: string
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

/** Publication dates of the same evidence records sourceUrlsFor resolves, in the same order. */
function sourceDatesFor(evidenceIds: string[], evidenceByIdMap: Record<string, EvidenceRecord>): string[] {
  const seen = new Set<string>()
  const dates: string[] = []
  for (const id of evidenceIds) {
    const record = evidenceByIdMap[id]
    const url = record?.canonicalUrl
    if (url && !seen.has(url)) {
      seen.add(url)
      dates.push(record.publicationDate)
    }
  }
  return dates
}

const CERTIFIED_TYPES: ReadonlySet<TrackerFigureType> = new Set(['revenue-latest', 'revenue-prior'])

/** Whether a figure of this type for this supplier is part of the certified claim set. */
export function isCertifiedFigure(supplierId: string, type: TrackerFigureType): boolean {
  return receiptComplete && CERTIFIED_TYPES.has(type) && isCertifiedSupplier(supplierId)
}

function figuresForSupplier(
  supplier: TrackerSupplier,
  evidenceByIdMap: Record<string, EvidenceRecord>,
): TrackerFigure[] {
  const figures: Omit<TrackerFigure, 'certified'>[] = []

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
      sourceDates: sourceDatesFor(metric.evidenceIds, evidenceByIdMap),
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
      sourceDates: sourceDatesFor(latest.evidenceIds, evidenceByIdMap),
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
      sourceDates: sourceDatesFor(prior.evidenceIds, evidenceByIdMap),
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
      sourceDates: sourceDatesFor(round.evidenceIds, evidenceByIdMap),
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
      sourceDates: sourceDatesFor(ownership.evidenceIds, evidenceByIdMap),
    })
  }

  return figures.map((figure) => ({ ...figure, certified: isCertifiedFigure(supplier.id, figure.type) }))
}

export function trackerJsonPayload(
  suppliers: TrackerSupplier[],
  domains: TrackerDomain[],
  evidenceByIdMap: Record<string, EvidenceRecord>,
  status: RunStatus,
): TrackerJsonPayload {
  return {
    about:
      'Security Market Pulse: dated, sourced facts about the business of security suppliers. Every figure carries ' +
      'its reporting period and the source it is cited to. Facts only, no rankings or forecasts.',
    license: DATA_LICENSE,
    licenseUrl: DATA_LICENSE_URL,
    documentation: `${SITE_URL}/data/`,
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
