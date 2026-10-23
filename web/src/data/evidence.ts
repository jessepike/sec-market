import { effectiveHandWrittenEvidenceRecords } from './tracker/correctionData'
import { edgarRevenueEvidence } from './tracker/edgarRevenue'
import type { EvidenceRecord } from './types'
import { dailyEvidence } from './tracker/daily'
import generatedFilingEvidence from './generated/filingEvidence.json' with { type: 'json' }

export { originalHandWrittenEvidenceRecords as handWrittenEvidenceRecords } from './tracker/correctionData'


export const evidenceRecords: EvidenceRecord[] = [
  ...effectiveHandWrittenEvidenceRecords,
  ...edgarRevenueEvidence,
  ...(generatedFilingEvidence as EvidenceRecord[]),
  ...dailyEvidence,
]

export const evidenceById = Object.fromEntries(
  evidenceRecords.map((record) => [record.id, record]),
) as Record<string, EvidenceRecord>

export function getEvidence(ids: string | string[]): EvidenceRecord[] {
  const list = Array.isArray(ids) ? ids : [ids]
  return list.map((id) => evidenceById[id]).filter(Boolean)
}
