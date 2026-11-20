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
import { PENDING_DOMAIN_MIN_LIVE, pendingDomains } from './pendingDomains'

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
      // Vendor partner tags (D-153) are preview-only, so their evidence does not go live with the company.
      if (key === 'partners') continue
      if (key === 'evidenceIds' && Array.isArray(v)) v.forEach((id) => out.add(String(id)))
      else evidenceIdsIn(v, out)
    }
  }
  return out
}

/** Pure split of onboarding.json into held and graduated parts. verify-current-facts uses it on fresh bytes. */
export function splitOnboarding<S extends { id: string; domainIds?: readonly string[] }, V extends { id: string }, E extends { supplierId: string }>(
  file: { suppliers: S[]; evidence: V[]; events: E[]; graduated?: Record<string, unknown> },
) {
  const marked = new Set(Object.keys(file.graduated ?? {}))
  // A company in a pending domain (D-153) stays held until enough of that domain's companies have
  // passed, so the domain and its companies go live together.
  const pendingIds = new Set(pendingDomains.map((d) => d.id))
  const readyIn = (domainId: string) => file.suppliers.filter((s) => marked.has(s.id) && (s.domainIds ?? []).includes(domainId)).length
  const held = (s: S) => (s.domainIds ?? []).some((d) => pendingIds.has(d) && readyIn(d) < PENDING_DOMAIN_MIN_LIVE)
  const graduatedIds = new Set([...marked].filter((id) => !file.suppliers.some((s) => s.id === id && held(s))))
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
