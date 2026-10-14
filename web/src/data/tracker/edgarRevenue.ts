import rawFacts from '../generated/edgarFacts.json' with { type: 'json' }
import type { SupplierRecord, YoyFigure } from '../edgarLogic'
import type { EvidenceRecord } from '../types'
import type { RevenuePeriod, SupplierRevenue, TrackerSupplier } from './suppliers'

interface CheckedSupplierRecord extends SupplierRecord { sourceCheck?: { checkedAt: string; url: string; sha256: string } }
const facts = rawFacts as unknown as { generatedAt: string; suppliers: CheckedSupplierRecord[]; failures: { id: string }[]; checks?: { supplierId: string; checkedAt: string; url: string; status: string; sha256?: string }[] }
export const revenueEvidenceId = (id: string, figure: YoyFigure) => `TR-edgar-revenue-${id}-${figure.quarter.periodEnd}-${figure.quarter.filedDate}`
const dollars = (value: number) => `$${value.toLocaleString('en-US')}`

export function revenuePeriod(id: string, figure: YoyFigure): RevenuePeriod {
  const q = figure.quarter
  return { value: dollars(q.value), priorYearValue: figure.priorYearQuarter ? dollars(figure.priorYearQuarter.value) : undefined,
    yoyGrowth: figure.growth !== null && figure.flags.length === 0 ? `${figure.growth >= 0 ? '+' : ''}${(figure.growth * 100).toFixed(1)}%` : '',
    period: `Quarter ended ${q.periodEnd}${q.derived ? ' (derived from annual less preceding quarters)' : ''}`,
    periodEnd: q.periodEnd, evidenceIds: [revenueEvidenceId(id, figure)] }
}

/** A failed check never replaces the last retained supplier claim or advances its period. */
export function withEdgarRevenue(supplier: TrackerSupplier): TrackerSupplier {
  if (!supplier.edgarId) return supplier
  const record = facts.suppliers.find(s => s.id === supplier.edgarId)
  if (!record?.latest) return supplier
  const revenue: SupplierRevenue = { scope: 'company', latest: { ...revenuePeriod(record.id, record.latest), releaseDate: record.latest.quarter.filedDate },
    prior: record.prior ? revenuePeriod(record.id, record.prior) : undefined }
  return { ...supplier, revenue }
}

export const edgarRevenueEvidence: EvidenceRecord[] = facts.suppliers.flatMap(record => [record.latest, record.prior]
  .filter((figure): figure is YoyFigure => figure !== null)
  .map(figure => ({ id: revenueEvidenceId(record.id, figure), title: `${record.name} ${figure.quarter.form}: quarterly revenue`,
    organization: record.name, publicationDate: figure.quarter.filedDate, economicPeriod: `Quarter ended ${figure.quarter.periodEnd}`,
    canonicalUrl: figure.quarter.sourceUrl, excerpt: `SEC XBRL ${record.concept}: USD ${figure.quarter.value.toLocaleString('en-US')} for ${figure.quarter.periodStart} to ${figure.quarter.periodEnd}.${figure.priorYearQuarter ? ` Same-quarter prior-year revenue: USD ${figure.priorYearQuarter.value.toLocaleString('en-US')}.` : ''}`,
    sourceClass: 'FILING' as const, interpretation: '', limitations: `${figure.quarter.derived ? 'Quarter derived from annual total minus the preceding three quarters. ' : ''}Year-over-year growth is computed from comparable filed quarter values; no growth is plotted without a matching prior year and clean validation. ${figure.flags.join('; ')}`,
    conflictingEvidenceIds: [], artifactLabel: 'SEC-MARKET-REFRESH / structured revenue', tags: ['tracker', 'edgar-revenue'],
    ...sourceReceipt(record, figure) })))

function sourceReceipt(record: CheckedSupplierRecord, figure: YoyFigure): Pick<EvidenceRecord, 'retrievedAt' | 'retrieval'> {
  const current = facts.checks?.find(c => c.supplierId === record.id && c.status === 'checked' && c.sha256)
  const check = current ?? record.sourceCheck
  if (!check?.sha256) return {}
  return { retrievedAt: check.checkedAt.slice(0, 10), retrieval: { finalUrl: check.url, sha256: check.sha256, fetchedAt: check.checkedAt,
    locator: `${record.concept}; USD; ${figure.quarter.periodStart} through ${figure.quarter.periodEnd}; filed ${figure.quarter.filedDate}${figure.quarter.derived ? '; derived annual less preceding three quarters' : ''}` } }
}
