/**
 * Graduation from onboarding (D-138). onboarding.json lists every supplier that
 * entered through the onboarding gate. `graduated` names the ones that passed
 * a clean daily run and every build check (ops/onboarding/graduate.py). A graduated
 * supplier's seed record, its evidence and its events join the live tracker;
 * the rest stay held on preview builds only.
 *
 * Graduated records live here, not in originals.json, so the reviewed
 * correction baseline (contracts/factual-baseline.json) is untouched.
 */
import onboarding from './onboarding.json' with { type: 'json' }
import type { TrackerSupplier } from './suppliers'
import type { TrackerEvent } from './events'
import type { EvidenceRecord } from '../types'

export interface OnboardingFile {
  suppliers: Array<{ id: string }>
  evidence: Array<{ id: string }>
  events: Array<{ supplierId: string }>
  graduated?: Record<string, { date: string; runIds: string[] }>
}

function evidenceIdsIn(value: unknown, out: Set<string>): Set<string> {
  if (Array.isArray(value)) value.forEach((v) => evidenceIdsIn(v, out))
  else if (value && typeof value === 'object') {
    for (const [key, v] of Object.entries(value)) {
      if (key === 'evidenceIds' && Array.isArray(v)) v.forEach((id) => out.add(String(id)))
      else evidenceIdsIn(v, out)
    }
  }
  return out
}

/** Pure split of onboarding.json into held and graduated parts. verify-current-facts uses it on fresh bytes. */
export function splitOnboarding<S extends { id: string }, V extends { id: string }, E extends { supplierId: string }>(
  file: { suppliers: S[]; evidence: V[]; events: E[]; graduated?: Record<string, unknown> },
) {
  const graduatedIds = new Set(Object.keys(file.graduated ?? {}))
  const suppliers = file.suppliers.filter((s) => graduatedIds.has(s.id))
  const events = file.events.filter((e) => graduatedIds.has(e.supplierId))
  const used = evidenceIdsIn([suppliers, events], new Set())
  return {
    graduatedIds,
    heldIds: file.suppliers.filter((s) => !graduatedIds.has(s.id)).map((s) => s.id),
    suppliers,
    events,
    evidence: file.evidence.filter((e) => used.has(e.id)),
  }
}

const split = splitOnboarding(onboarding as unknown as { suppliers: TrackerSupplier[]; evidence: EvidenceRecord[]; events: TrackerEvent[]; graduated?: Record<string, unknown> })
export const graduatedSupplierIds: ReadonlySet<string> = split.graduatedIds
export const heldOnboardingIds: readonly string[] = split.heldIds
export const graduatedSuppliers: TrackerSupplier[] = split.suppliers
export const graduatedEvidence: EvidenceRecord[] = split.evidence
export const graduatedEvents: TrackerEvent[] = split.events
