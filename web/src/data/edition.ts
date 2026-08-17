import { securityDomains } from './domains'
import type { DomainEditionNote, Edition, EditionChangeKind } from './types'

const domainNotes: DomainEditionNote[] = [
  {
    domainId: 'network-sase',
    kind: 'held',
    note: 'Opening dated posture. Refresh still live this quarter.',
  },
  {
    domainId: 'data-ai-security',
    kind: 'held',
    note: 'Opening dated posture. Prepare only where sensitive data is entering new workloads.',
  },
  {
    domainId: 'cloud-security',
    kind: 'held',
    note: 'Opening dated posture. Qualify residual gaps when capacity goes live.',
  },
  {
    domainId: 'identity',
    kind: 'held',
    note: 'Opening dated posture. IGA is up; agentic identity is still capital, not spend.',
  },
  {
    domainId: 'secops',
    kind: 'held',
    note: 'Opening dated posture. Share shift and platformization, not a new cycle.',
  },
  {
    domainId: 'ai-runtime',
    kind: 'held',
    note: 'Opening dated posture. Capital heat is not a specialist-platform motion.',
  },
]

for (const domain of securityDomains) {
  if (!domainNotes.some((note) => note.domainId === domain.id)) {
    throw new Error(`Missing edition note for domain ${domain.id}`)
  }
}

for (const note of domainNotes) {
  if (!securityDomains.some((domain) => domain.id === note.domainId)) {
    throw new Error(`Edition note references missing domain ${note.domainId}`)
  }
}

export const currentEdition: Edition = {
  id: '2026-08-17',
  date: '2026-08-17',
  dateDisplay: '17 August 2026',
  priorId: '2026-08-16',
  priorDateDisplay: '16 August 2026',
  summary:
    'Domain postures are now dated, with a horizon and the evidence that produced each one. The market call did not move.',
  surfaces: [
    {
      id: 'call',
      label: 'Market call',
      kind: 'held',
      detail: 'Infrastructure ahead. Security split. Lag NO-CALL.',
    },
    {
      id: 'prints',
      label: 'Prints',
      kind: 'held',
      detail: 'Same comparable vendor window.',
    },
    {
      id: 'activity',
      label: 'Activity',
      kind: 'held',
      detail: '6 Jul – 10 Aug 2026 / RoS #252–#256.',
    },
  ],
  domainNotes,
}

export interface EditionDomainRow {
  id: string
  name: string
  tag: string
  horizon: string
  asOf: string
  kind: EditionChangeKind
  note: string
}

export function editionDomainRows(): EditionDomainRow[] {
  return currentEdition.domainNotes.map((note) => {
    const domain = securityDomains.find((item) => item.id === note.domainId)
    if (!domain) {
      throw new Error(`Edition note references missing domain ${note.domainId}`)
    }
    return {
      id: domain.id,
      name: domain.name,
      tag: domain.tag,
      horizon: domain.horizon,
      asOf: domain.asOf,
      kind: note.kind,
      note: note.note,
    }
  })
}
