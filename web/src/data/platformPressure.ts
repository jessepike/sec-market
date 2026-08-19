import { activityItems } from './activity'
import { securityDomains } from './domains'
import { LAST_UPDATED_ISO } from './meta'
import {
  fasterPeerRead,
  fasterThanOrganicRead,
  growthPoints,
  groupPositionKey,
  identityAbsorbedRead,
  identityHoldingRead,
  infraCarriedRead,
  isCurrentPrint,
  renderClosePrint,
  renderMetricPrint,
  trackedFrom,
} from './printValue'
import { vendorPrints } from './prints'
import type { JudgedClaim, PressureGroup, PressureRow, VendorPosition, VendorPrint } from './types'

const judgedOn = LAST_UPDATED_ISO

function judged(evidenceIds: string[], confidence: JudgedClaim['confidence'] = 'medium'): JudgedClaim {
  return { layer: 'judged', judgedOn, confidence, evidenceIds }
}

function positioned(position: VendorPosition): VendorPrint[] {
  return vendorPrints.filter((print) => print.position === position)
}

function challengersInGroup(group: string): VendorPrint[] {
  return vendorPrints.filter(
    (print) => print.group === group && (print.position === 'challenger' || print.position === 'early'),
  )
}

function outrunByChallenger(print: VendorPrint): boolean {
  const own = growthPoints(print.value)
  if (own === null) return false
  return challengersInGroup(print.group).some((challenger) => {
    const other = growthPoints(challenger.value)
    return other !== null && own < other
  })
}

function siblingInfraPrint(securityPrint: VendorPrint): VendorPrint | undefined {
  const platformRow = vendorPrints.find(
    (print) =>
      print.group === 'Platform' && securityPrint.evidenceIds.some((id) => print.evidenceIds.includes(id)),
  )
  if (!platformRow) return undefined
  return vendorPrints.find((print) => print.group === 'Infrastructure' && print.name === platformRow.name)
}

function pairRows(prints: VendorPrint[], readFor: (members: VendorPrint[]) => string): PressureRow[] {
  const byKey = new Map<string, VendorPrint[]>()
  for (const print of prints) {
    const key = groupPositionKey(print.group, print.position ?? '')
    const list = byKey.get(key) ?? []
    list.push(print)
    byKey.set(key, list)
  }

  return [...byKey.values()].map((members) => {
    const [lead] = members
    if (!lead || !lead.position) {
      throw new Error('challenger group is missing a lead print')
    }
    const evidenceIds = members.flatMap((print) => print.evidenceIds)
    const read = readFor(members)
    return {
      id: members.map((print) => print.id).join('--'),
      vendors: members.map((print) => print.name),
      position: lead.position,
      print: members.map((print) => print.value).join(' · '),
      read,
      provenance: {
        print: trackedFrom(evidenceIds),
        read: judged(evidenceIds),
      },
    }
  })
}

function buyingInRows(): PressureRow[] {
  const absorbed = positioned('absorbed')
  return activityItems
    .slice()
    .sort((left, right) => left.date.localeCompare(right.date))
    .flatMap((item) => {
      if (item.kind !== 'ma') return []
      const print = absorbed.find((row) => row.name === item.target)
      if (!print || !print.position) return []
      const rendered = renderClosePrint(item.actor, item.value, item.date)
      const evidenceIds = [...print.evidenceIds, ...item.evidenceIds]
      const read =
        print.group === 'Identity'
          ? identityAbsorbedRead(item.actor)
          : 'Cloud security absorbed into a hyperscaler. Watch what it does to the specialist gap.'
      return [
        {
          id: item.id,
          vendors: [print.name],
          position: print.position,
          print: rendered,
          read,
          provenance: {
            print: trackedFrom(evidenceIds),
            read: judged(evidenceIds),
          },
        },
      ]
    })
}

function outrunRows(): PressureRow[] {
  const candidates = vendorPrints.filter((print) => {
    if (print.position !== 'platform' && print.position !== 'incumbent') return false
    return outrunByChallenger(print) || print.tone === 'down'
  })

  return candidates.map((print) => {
    const peers = challengersInGroup(print.group).filter((peer) => growthPoints(peer.value) !== null)
    const infra = siblingInfraPrint(print)
    const peerClause =
      peers.length > 0
        ? fasterPeerRead(peers)
        : infra
          ? infraCarriedRead(infra.value)
          : 'No clean re-acceleration inside this window.'
    const evidenceIds = [
      ...print.evidenceIds,
      ...peers.flatMap((peer) => peer.evidenceIds),
      ...(infra?.evidenceIds ?? []),
    ]
    return {
      id: print.id,
      vendors: [print.name],
      position: print.position ?? 'platform',
      print: renderMetricPrint(print),
      read: peerClause,
      provenance: {
        print: trackedFrom(print.evidenceIds),
        read: judged(evidenceIds),
      },
    }
  })
}

function challengerRows(): PressureRow[] {
  const organic = vendorPrints.find((print) => print.position === 'platform' && print.metric.includes('organic'))
  return pairRows(positioned('challenger').concat(positioned('early')), (members) => {
    const [lead] = members
    if (lead?.position === 'early') {
      return 'Agentic identity. Capital, not customers. Too early to place a bet on.'
    }
    if (lead && organic && lead.group === organic.group) {
      return fasterThanOrganicRead(organic.name)
    }
    return 'Both accelerating on public numbers. The cleanest data-side signal here.'
  })
}

function holdingRows(already: Set<string>): PressureRow[] {
  return vendorPrints
    .filter((print) => {
      if (!print.position) return false
      if (print.position === 'challenger' || print.position === 'early' || print.position === 'absorbed') {
        return false
      }
      if (!isCurrentPrint(print)) return false
      if (already.has(print.id)) return false
      return true
    })
    .map((print) => {
      const identity = securityDomains.find((domain) => domain.id === 'identity')
      const read =
        print.position === 'incumbent' && identity && print.group === identity.name
          ? identityHoldingRead(identity.name, identity.momentum)
          : print.position === 'incumbent'
            ? 'Refresh spike. Not yet proven as a lasting rotation.'
            : 'Recovered. The cloud segment is real revenue, not a category series.'
      return {
        id: print.id,
        vendors: [print.name],
        position: print.position ?? 'incumbent',
        print: renderMetricPrint(print),
        read,
        provenance: {
          print: trackedFrom(print.evidenceIds),
          read: judged(print.evidenceIds),
        },
      }
    })
}

const buyingIn = buyingInRows()
const outrun = outrunRows()
const challengers = challengerRows()
const placed = new Set([...outrun, ...buyingIn].flatMap((row) => [row.id]))
const holding = holdingRows(placed)

export const platformPressure: Record<PressureGroup, PressureRow[]> = {
  holding,
  'buying-in': buyingIn,
  outrun,
  challengers,
}

export function allPressureRows(): PressureRow[] {
  return [...holding, ...buyingIn, ...outrun, ...challengers]
}
