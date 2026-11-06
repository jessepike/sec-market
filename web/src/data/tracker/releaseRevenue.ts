import rawReleases from '../generated/companyReleases.json' with { type: 'json' }
import type { ReleaseQuarter, ReleaseRecord } from '../sixKLogic'
import { releaseRegistry } from '../releaseRegistry'
import type { EvidenceRecord } from '../types'
import type { RevenuePeriod, SupplierRevenue, TrackerSupplier } from './suppliers'

const releases = rawReleases as unknown as { generatedAt: string; suppliers: ReleaseRecord[] }

export const releaseEvidenceId = (id: string, q: ReleaseQuarter) => `TR-6k-revenue-${id}-${q.periodEnd}-${q.filedDate}`
const millions = (usd: number) => `$${(usd / 1e6).toLocaleString('en-US', { minimumFractionDigits: 1, maximumFractionDigits: 1 })} million`
const growth = (q: ReleaseQuarter) => {
  const g = q.value / q.priorYearValue - 1
  return `${g >= 0 ? '+' : ''}${(g * 100).toFixed(1)}%`
}

function period(id: string, q: ReleaseQuarter): RevenuePeriod {
  return { value: millions(q.value), priorYearValue: millions(q.priorYearValue), yoyGrowth: growth(q),
    period: `Quarter ended ${q.periodEnd}`, periodEnd: q.periodEnd, evidenceIds: [releaseEvidenceId(id, q)] }
}

/**
 * Advances a 6-K filer's revenue only when its own results release covers a
 * later quarter than the hand-collected record. Never touches a certified
 * (edgarId) supplier, and never moves a period backwards.
 */
export function withReleaseRevenue(supplier: TrackerSupplier): TrackerSupplier {
  if (supplier.edgarId) return supplier
  const reg = releaseRegistry.find(r => r.supplierId === supplier.id)
  const record = reg && releases.suppliers.find(s => s.id === reg.id)
  if (!reg || !record?.latest) return supplier
  if (supplier.revenue && record.latest.periodEnd <= supplier.revenue.latest.periodEnd) return supplier
  const latest = { ...period(record.id, record.latest), releaseDate: record.latest.filedDate }
  const revenue: SupplierRevenue = { scope: 'company', latest, prior: record.prior ? period(record.id, record.prior) : undefined }
  const headlineMetric = supplier.headlineMetric
    ? { label: 'Total revenue', value: latest.value, period: latest.period, evidenceIds: latest.evidenceIds }
    : undefined
  return { ...supplier, revenue, ...(headlineMetric ? { headlineMetric } : {}) }
}

export const releaseRevenueEvidence: EvidenceRecord[] = releases.suppliers.flatMap(record => [record.latest, record.prior]
  .filter((q): q is ReleaseQuarter => !!q)
  .map(q => ({ id: releaseEvidenceId(record.id, q), title: `${record.name} Form 6-K: quarterly results release`,
    organization: record.name, publicationDate: q.filedDate, economicPeriod: `Quarter ended ${q.periodEnd}`,
    canonicalUrl: q.sourceUrl,
    excerpt: `Total revenues: USD ${(q.value / 1e6).toFixed(1)} million for the three months ended ${q.periodEnd}; USD ${(q.priorYearValue / 1e6).toFixed(1)} million a year earlier.`,
    sourceClass: 'FILING' as const, interpretation: '',
    limitations: 'Company-reported figure from the results release furnished on Form 6-K. Read by a fixed parser, not re-derived from XBRL, and not part of the certified SEC figures.',
    conflictingEvidenceIds: [], artifactLabel: 'SEC-MARKET-REFRESH / 6-K results release', tags: ['tracker', 'release-revenue'],
    retrievedAt: q.checkedAt.slice(0, 10),
    retrieval: { finalUrl: q.sourceUrl, sha256: q.sha256, fetchedAt: q.checkedAt, locator: `Total revenues; three months ended ${q.periodEnd}; ${q.scale}` } })))
