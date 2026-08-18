import { securityDomains } from './domains'
import type {
  DecisionHorizon,
  Edition,
  EditionChangeKind,
  EditionRecord,
  PostureSnapshot,
} from './types'

/**
 * Append-only edition history.
 *
 * Every published edition freezes the postures it published. A past entry is a
 * historical record, not a working copy: once an edition ships, its snapshot is
 * never edited. To publish a new edition, append a new record at the end.
 *
 * The edition-to-edition delta is DERIVED from these snapshots (see
 * `editionDomainRows`). It is never hand-written, so the page cannot claim a
 * posture held when it moved, or moved when it held.
 *
 * The 2026-08-16 snapshot is transcribed from the domain data actually
 * published in that edition (`web/src/data/domains.ts` at commit ab8a6fd).
 * That edition carried a posture and a tag but no decision horizon, so its
 * horizons are recorded as null rather than backfilled.
 */
export const editions: EditionRecord[] = [
  {
    id: '2026-08-16',
    date: '2026-08-16',
    dateDisplay: '16 August 2026',
    summary: 'First published edition. Postures carried a tag but no stated horizon.',
    surfaces: [],
    postures: [
      { domainId: 'network-sase', posture: 'PREPARE', tag: 'PREPARE', horizon: null },
      { domainId: 'data-ai-security', posture: 'PREPARE', tag: 'PREPARE', horizon: null },
      { domainId: 'cloud-security', posture: 'INVESTIGATE', tag: 'WATCH', horizon: null },
      { domainId: 'identity', posture: 'INVESTIGATE', tag: 'WATCH', horizon: null },
      { domainId: 'secops', posture: 'INVESTIGATE', tag: 'WATCH', horizon: null },
      { domainId: 'ai-runtime', posture: 'INVESTIGATE', tag: 'WATCH', horizon: null },
    ],
    notes: {},
  },
  {
    id: '2026-08-17',
    date: '2026-08-17',
    dateDisplay: '17 August 2026',
    summary:
      'Domain postures are now dated, with the decision horizon each one governs and the evidence that produced it. No posture moved.',
    surfaces: [
      {
        id: 'call',
        label: 'Market call',
        kind: 'held',
        detail: 'Infrastructure ahead. Security split. Lag NO-CALL.',
      },
      { id: 'prints', label: 'Prints', kind: 'held', detail: 'Same comparable vendor window.' },
      {
        id: 'activity',
        label: 'Activity',
        kind: 'held',
        detail: '6 Jul – 10 Aug 2026 / RoS #252–#256.',
      },
    ],
    postures: [
      { domainId: 'network-sase', posture: 'PREPARE', tag: 'PREPARE', horizon: 'This quarter' },
      {
        domainId: 'data-ai-security',
        posture: 'PREPARE',
        tag: 'PREPARE',
        horizon: 'This planning cycle',
      },
      {
        domainId: 'cloud-security',
        posture: 'INVESTIGATE',
        tag: 'WATCH',
        horizon: 'Next 1–4 quarters',
      },
      { domainId: 'identity', posture: 'INVESTIGATE', tag: 'WATCH', horizon: 'Next 1–4 quarters' },
      { domainId: 'secops', posture: 'INVESTIGATE', tag: 'WATCH', horizon: 'Next 1–4 quarters' },
      {
        domainId: 'ai-runtime',
        posture: 'INVESTIGATE',
        tag: 'WATCH',
        horizon: 'Next 1–4 quarters',
      },
    ],
    notes: {
      'network-sase': 'Refresh still live this quarter.',
      'data-ai-security': 'Prepare only where sensitive data is entering new workloads.',
      'cloud-security': 'Qualify residual gaps when capacity goes live.',
      identity: 'IGA is up; agentic identity is still capital, not spend.',
      secops: 'Share shift and platformization, not a new cycle.',
      'ai-runtime': 'Capital heat is not a specialist-platform motion.',
    },
  },
]

if (editions.length === 0) {
  throw new Error('Edition history is empty')
}

export const currentEditionRecord: EditionRecord = editions[editions.length - 1]
export const priorEditionRecord: EditionRecord | null =
  editions.length > 1 ? editions[editions.length - 2] : null

/**
 * The published page and the current edition's frozen snapshot must agree.
 * If they drift, the delta on the page would describe postures the page is not
 * actually showing, so this fails the build rather than publishing a false one.
 */
for (const domain of securityDomains) {
  const snapshot = currentEditionRecord.postures.find((item) => item.domainId === domain.id)
  if (!snapshot) {
    throw new Error(
      `Edition ${currentEditionRecord.id} has no posture snapshot for domain ${domain.id}`,
    )
  }
  if (snapshot.posture !== domain.posture || snapshot.tag !== domain.tag) {
    throw new Error(
      `Edition ${currentEditionRecord.id} snapshot for ${domain.id} disagrees with the published posture`,
    )
  }
  if (snapshot.horizon !== domain.horizon) {
    throw new Error(
      `Edition ${currentEditionRecord.id} snapshot for ${domain.id} disagrees with the published horizon`,
    )
  }
}

for (const snapshot of currentEditionRecord.postures) {
  if (!securityDomains.some((domain) => domain.id === snapshot.domainId)) {
    throw new Error(
      `Edition ${currentEditionRecord.id} snapshots a domain that is not published: ${snapshot.domainId}`,
    )
  }
}

export interface EditionDomainRow {
  id: string
  name: string
  tag: string
  horizon: DecisionHorizon
  asOf: string
  kind: EditionChangeKind
  /** Derived description of what moved, or what was stated for the first time. */
  change: string
  /** Human judgment about the posture. Optional. */
  note: string | null
}

function describeChange(
  current: PostureSnapshot,
  prior: PostureSnapshot | undefined,
): { kind: EditionChangeKind; change: string } {
  if (!prior) {
    return { kind: 'new', change: 'First published posture.' }
  }

  if (prior.posture !== current.posture || prior.tag !== current.tag) {
    return {
      kind: 'revised',
      change: `Moved from ${prior.tag} to ${current.tag}.`,
    }
  }

  if (prior.horizon === null && current.horizon !== null) {
    return { kind: 'held', change: `Horizon stated for the first time: ${current.horizon}.` }
  }

  if (prior.horizon !== current.horizon) {
    return {
      kind: 'held',
      change: `Posture held. Horizon moved from ${prior.horizon} to ${current.horizon}.`,
    }
  }

  return { kind: 'held', change: 'Unchanged.' }
}

export function editionDomainRows(): EditionDomainRow[] {
  return securityDomains.map((domain) => {
    const current = currentEditionRecord.postures.find((item) => item.domainId === domain.id)
    if (!current) {
      throw new Error(`No posture snapshot for domain ${domain.id}`)
    }
    const prior = priorEditionRecord?.postures.find((item) => item.domainId === domain.id)
    const { kind, change } = describeChange(current, prior)

    return {
      id: domain.id,
      name: domain.name,
      tag: domain.tag,
      horizon: domain.horizon,
      asOf: domain.asOf,
      kind,
      change,
      note: currentEditionRecord.notes[domain.id] ?? null,
    }
  })
}

/** Shape the rest of the app reads. Prior identity is derived, not typed by hand. */
export const currentEdition: Edition = {
  id: currentEditionRecord.id,
  date: currentEditionRecord.date,
  dateDisplay: currentEditionRecord.dateDisplay,
  priorId: priorEditionRecord?.id ?? null,
  priorDateDisplay: priorEditionRecord?.dateDisplay ?? null,
  summary: currentEditionRecord.summary,
  surfaces: currentEditionRecord.surfaces,
}
