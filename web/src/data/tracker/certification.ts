/**
 * AUTO-002 Phase 2: what the page may call certified. Everything here is read
 * from the committed certification receipt and contract, never hand-set.
 *
 * Certified means: re-derived from the company's own SEC filings by a check
 * that shares no code with the producer, at 100% for every certified claim
 * (identity, latest and prior quarter revenue, the 8-quarter table, and the
 * filing and date of SEC-filed events). It does not mean a second method; see
 * the contract policy (D-100). Fields outside that list keep their own source
 * and date and are not re-checked automatically.
 */
import coverage from '../generated/certifiedCoverage.json' with { type: 'json' }
import contract from './certifiedContract.json' with { type: 'json' }
import { evidenceById } from '../evidence'
import type { TrackerEvent } from './events'

interface CoverageFile { checkedAt: string; windowEnd: string; state: string; fields: { supplierId: string; field: string; status: string }[] }
const receipt = coverage as unknown as CoverageFile

/** Time of the certification run that produced the committed data (ISO). */
export const certifiedAt: string = receipt.checkedAt
export const certifiedDateDisplay = `${certifiedAt.slice(0, 10)} ${certifiedAt.slice(11, 16)} UTC`
export const secWindowEnd: string = receipt.windowEnd
export const certifiedSupplierIds: ReadonlySet<string> = new Set(contract.supplierIds)
export const certifiedCount = contract.supplierIds.length
export const certifiedClaimCount = contract.supplierIds.length * Object.keys(contract.groups).length
export const receiptComplete = receipt.state === 'complete' && receipt.fields.every(f => f.status !== 'failed')
export const checkInterval = 'every 4 hours'
export const notCertified: Record<string, string> = contract.notCertified

export function isCertifiedSupplier(id: string): boolean {
  return certifiedSupplierIds.has(id)
}

const isSec = (url: string | undefined) => !!url && /(^|\/\/)(www\.)?sec\.gov\//.test(url)

/** An event whose filing and date are part of the certified claim. Its written summary is not. */
export function isCertifiedEvent(event: Pick<TrackerEvent, 'supplierId' | 'evidenceIds' | 'date'>): boolean {
  if (!isCertifiedSupplier(event.supplierId)) return false
  const start = new Date(Date.parse(secWindowEnd + 'T00:00:00Z') - 365 * 86_400_000).toISOString().slice(0, 10)
  if (event.date < start || event.date > secWindowEnd) return false
  return event.evidenceIds.some(id => isSec(evidenceById[id]?.canonicalUrl))
}
