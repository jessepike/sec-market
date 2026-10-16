// Builds the certified-tier candidate claims from the site's build inputs
// (trackerSuppliers, events, evidence, edgarFacts). Used by certify-sec.ts to
// create proofs and by certify-gate.ts to re-derive the same claims at gate
// time, so a value changed after certification is caught (AUTO-002 P0 audit fix 1).
import { edgarRegistry } from '../../src/data/edgarRegistry'
import { trackerSuppliers } from '../../src/data/tracker/suppliers'
import { retainedTrackerEvents } from '../../src/data/tracker/events'
import { evidenceById } from '../../src/data/evidence'
import edgarFacts from '../../src/data/generated/edgarFacts.json' with { type: 'json' }
import { accessionFromUrl } from './independent.mjs'

export type Leaf = [string, unknown]

/** The certified set is derived, never hand-set: tracker suppliers with structured SEC revenue. */
export function derivedCertifiedIds(): string[] {
  const registry = new Set(edgarRegistry.map(r => r.id))
  return trackerSuppliers.filter(s => s.edgarId && registry.has(s.edgarId)).map(s => s.id).sort()
}

export function eventWindow(windowEnd: string): { windowStart: string; windowEnd: string } {
  return { windowStart: new Date(Date.parse(windowEnd + 'T00:00:00Z') - 365 * 86400000).toISOString().slice(0, 10), windowEnd }
}

const isSec = (url: string) => /(^|\/\/)(www\.)?sec\.gov\//.test(url)

export function windowEvents(supplierId: string, windowStart: string, windowEnd: string) {
  return retainedTrackerEvents.filter(e => e.supplierId === supplierId && e.date >= windowStart && e.date <= windowEnd).map(e => {
    const urls = e.evidenceIds.map(id => evidenceById[id]?.canonicalUrl ?? '')
    return { e, secEvidence: e.evidenceIds.filter((_id, k) => isSec(urls[k])), accessions: urls.filter(isSec).map(accessionFromUrl) }
  })
}

export function candidateFor(supplierId: string, windowStart: string, windowEnd: string): Record<string, unknown> {
  const supplier = trackerSuppliers.find(s => s.id === supplierId)!
  const record = (edgarFacts as unknown as { suppliers: Array<{ id: string; quarters: Array<{ periodEnd: string; value: number; filedDate: string; accessionNumber: string; derived: boolean }> }> })
    .suppliers.find(s => s.id === supplier.edgarId)
  const secEvents = windowEvents(supplierId, windowStart, windowEnd).filter(x => x.secEvidence.length).map(({ e, secEvidence, accessions }) => ({
    id: e.id, date: e.date, type: e.type, accessions, evidenceDates: secEvidence.map(id => evidenceById[id]?.publicationDate ?? null),
  })).sort((a, b) => a.id.localeCompare(b.id))
  return {
    identity: { name: supplier.name, ticker: supplier.ticker ?? null, kind: supplier.kind },
    'revenue.latest': supplier.revenue?.latest ?? null,
    'revenue.prior': supplier.revenue?.prior ?? null,
    'revenue.history': record ? record.quarters.map(q => ({ periodEnd: q.periodEnd, value: q.value, filedDate: q.filedDate, accessionNumber: q.accessionNumber, derived: q.derived })) : null,
    secEvents,
  }
}

export const leaves = (group: string, value: unknown): Leaf[] => value && typeof value === 'object' && !Array.isArray(value)
  ? Object.entries(value as Record<string, unknown>).filter(([k, v]) => k !== 'evidenceIds' && v !== undefined).map(([k, v]) => [`${group}.${k}`, v] as Leaf)
  : [[group, value]]

/** Every certified leaf for every certified supplier, as the gate should see it. */
export function allCandidateLeaves(groups: string[], windowEnd: string): Array<{ supplierId: string; field: string; value: unknown }> {
  const { windowStart } = eventWindow(windowEnd)
  return derivedCertifiedIds().flatMap(id => {
    const candidate = candidateFor(id, windowStart, windowEnd)
    return groups.flatMap(g => leaves(g, candidate[g]).map(([field, value]) => ({ supplierId: id, field, value })))
  })
}
