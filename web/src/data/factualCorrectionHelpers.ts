import { correctionsJsonPayload } from './correctionHelpers'
import type { Correction, EvidenceRecord } from './types'
import type { FactualCorrectionGroup, FactualCorrectionTarget } from './tracker/factualCorrections'

export interface CorrectionHistorySources {
  evidence: Readonly<Record<string, EvidenceRecord>>
  suppliers: readonly { id: string; name: string }[]
  groupEvidenceIds?: Readonly<Record<string, readonly string[]>>
}

export const emptyCorrectionHistorySources: CorrectionHistorySources = { evidence: {}, suppliers: [] }

export interface FactualCorrectionHistoryEntry extends FactualCorrectionGroup {
  kind: 'source_verified_factual_correction' | 'publisher_disclosure_correction'
  supplierName: string
  url: string
  sources: Array<{ id: string; title: string; url: string }>
  changes: Array<{ targetId: string; label: string; operation: FactualCorrectionTarget['operation']; before: string; after: string }>
}

/** These summaries describe the complete before/after records preserved in targets. */
function reading(target: FactualCorrectionTarget, side: 'original' | 'proposedValue'): string {
  const value = target[side]
  if (value === null) return 'Withdrawn from the standing reference.'
  if (target.targetId.startsWith('event:')) {
    const event = value as { date: string; text: string }
    return `${event.date}: ${event.text}`
  }
  const labels: Record<string, string> = {
    date: 'Date', stage: 'Stage', amount: 'Amount', lead: 'Lead investor', valuation: 'Valuation',
    label: 'Metric', value: 'Value', period: 'Period', status: 'Status', acquirer: 'Acquirer',
    announced: 'Announced', closed: 'Closed', price: 'Price', relationship: 'Relationship',
    title: 'Title', publicationDate: 'Publication date', economicPeriod: 'Period', excerpt: 'Source excerpt', limitations: 'Limitations',
    organization: 'Publisher', sourceClass: 'Source class',
  }
  const fields = target.operation === 'reclassify_publisher_disclosure' ? ['organization', 'sourceClass', 'limitations'] : target.targetId.startsWith('evidence:')
    ? ['title', 'publicationDate', 'economicPeriod', 'excerpt', 'limitations']
    : Object.keys(value)
  return fields.filter((key) => labels[key] && Object.hasOwn(value, key))
    .map((key) => `${labels[key]}: ${String((value as unknown as Record<string, unknown>)[key])}`).join('; ')
}

/** Pure presentation only. The independent gate authenticates admission and source bytes. */
export function factualCorrectionHistory(
  groups: readonly FactualCorrectionGroup[],
  sources: CorrectionHistorySources,
  siteUrl: string,
): FactualCorrectionHistoryEntry[] {
  return [...groups].sort((a, b) => b.date.localeCompare(a.date)).map((group) => {
    const links = new Map<string, { id: string; title: string; url: string }>()
    for (const id of sources.groupEvidenceIds?.[group.id] ?? []) {
      const record = sources.evidence[id]
      if (!record) throw new Error(`Factual correction ${group.id} has unresolved bound source ${id}`)
      links.set(id, { id, title: record.title, url: record.canonicalUrl })
    }
    for (const target of group.targets) {
      for (const value of [target.original, target.proposedValue]) {
        if (value === null) continue
        if ('canonicalUrl' in value) {
          links.set(value.id, { id: value.id, title: value.title, url: value.canonicalUrl })
        } else {
          for (const id of value.evidenceIds) {
            const record = sources.evidence[id]
            if (!record) throw new Error(`Factual correction ${group.id} has unresolved source ${id}`)
            links.set(id, { id, title: record.title, url: record.canonicalUrl })
          }
        }
      }
    }
    return {
      ...group,
      kind: group.reviewScope === 'publisher_disclosure_only' ? 'publisher_disclosure_correction' : 'source_verified_factual_correction',
      supplierName: sources.suppliers.find((supplier) => supplier.id === group.supplierId)?.name ?? group.supplierId,
      url: `${siteUrl}/corrections/#${group.id}`,
      sources: [...links.values()],
      changes: group.targets.map((target) => ({
        targetId: target.targetId,
        label: target.targetId.startsWith('event:') ? 'Event'
          : target.operation === 'reclassify_publisher_disclosure' ? 'Publisher disclosure and source class'
          : target.targetId.startsWith('evidence:') ? 'Source metadata'
          : target.targetId.endsWith(':lastRound') ? 'Funding round'
          : target.targetId.endsWith(':ownership') ? 'Ownership' : 'Headline metric',
        operation: target.operation, before: reading(target, 'original'), after: reading(target, 'proposedValue'),
      })),
    }
  })
}

export function publicCorrectionsJsonPayload(
  corrections: Correction[],
  groups: readonly FactualCorrectionGroup[],
  sources: CorrectionHistorySources,
  siteUrl: string,
) {
  const legacy = correctionsJsonPayload(corrections, siteUrl)
  if (!groups.length) return legacy
  return [...legacy, ...factualCorrectionHistory(groups, sources, siteUrl)].sort((a, b) => b.date.localeCompare(a.date))
}

/** Feed character data; the feed writer escapes this once as XML. */
export function factualCorrectionFeedText(entry: FactualCorrectionHistoryEntry): string {
  return [
    entry.note,
    entry.reviewScope === 'publisher_disclosure_only'
      ? 'Publisher disclosure correction. Verification covers publication role only and does not verify financial, funding or operating figures.'
      : 'Source-verified factual correction.',
    ...entry.changes.map((change) => `${change.label} (${change.targetId}). Before: ${change.before} After: ${change.after}`),
    ...entry.sources.map((source) => `Source: ${source.title} (${source.url})`),
    `Admitted: ${entry.admission.admittedAt}.`,
    `Candidate SHA-256: ${entry.admission.candidateSha256}. Evidence set SHA-256: ${entry.admission.evidenceSetSha256}. Policy SHA-256: ${entry.admission.policySha256}. Review SHA-256: ${entry.admission.reviewSha256}.`,
  ].join('\n')
}
