import { activityItems } from './activity'
import { securityDomains } from './domains'
import { JUDGED_AS_OF_ISO } from './meta'
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

const judgedOn = JUDGED_AS_OF_ISO

function judged(
  evidenceIds: string[],
  confidence: JudgedClaim['confidence'] = 'medium',
  judgedOnOverride: string = judgedOn,
): JudgedClaim {
  return { layer: 'judged', judgedOn: judgedOnOverride, confidence, evidenceIds }
}

/**
 * Acquirers whose purchase of a security company counts as absorption into
 * the cloud itself, not into a security platform (D-75, BACKLOG SEC-054).
 * Kept here, explicit and small, so the sentence a "buying in" row gets
 * never depends on guessing a name inside a component. Palo Alto Networks
 * and F5 buy and absorb security companies too, but neither belongs on this
 * list — they are platform vendors, not hyperscalers.
 */
const HYPERSCALER_ACQUIRERS = ['Alphabet', 'Google', 'Microsoft', 'Amazon', 'AWS']

function isHyperscaler(actor: string): boolean {
  return HYPERSCALER_ACQUIRERS.includes(actor.trim())
}

/** The two `VendorPrint.group` values D-75's wording turns on. */
const AI_SECURITY_GROUP = 'AI runtime'
const CLOUD_SECURITY_GROUP = 'Cloud security'

const CLOUD_INTO_HYPERSCALER_SENTENCE =
  'Cloud security absorbed into a hyperscaler. Watch what it does to the specialist gap.'
const AI_SECURITY_INTO_PLATFORM_SENTENCE =
  'AI security absorbed into a platform vendor. Watch whether it survives as a product or becomes a feature.'
const CLOUD_INTO_PLATFORM_SENTENCE =
  'Cloud security absorbed into a platform vendor. Watch whether it survives as a product or becomes a feature.'

/** The date the owner approved the reworded sentences below (D-75, 2026-09-21). */
const WORDING_JUDGED_ON = '2026-09-21'

export interface BuyingInWording {
  text: string
  /** True when `text` is D-75's new wording — the row's judged date moves to WORDING_JUDGED_ON. */
  reworded: boolean
  /**
   * False when the acquirer/target combination is none of D-75's three
   * approved cases. `text` is then the row's original (imprecise) sentence,
   * left alone rather than guessed at — see SEC-054 and the T7-9 report.
   */
  approved: boolean
}

/**
 * D-75: the sentence a non-Identity "buying in" row gets, chosen by who
 * bought the company and what kind of company it was.
 *   - hyperscaler acquirer, cloud security target: the original sentence, unchanged.
 *   - platform-vendor acquirer, AI security target: the AI-security sentence.
 *   - platform-vendor acquirer, cloud security target: the same sentence, said of cloud security.
 * Anything else — a hyperscaler buying something that is not cloud
 * security, or a platform vendor buying a target that is neither AI
 * security nor cloud security — is outside the three cases the owner
 * approved. This never invents wording for that case; it returns the
 * original sentence with `approved: false` so the caller can flag it.
 */
export function buyingInWording(actor: string, targetGroup: string): BuyingInWording {
  const hyperscaler = isHyperscaler(actor)
  if (hyperscaler && targetGroup === CLOUD_SECURITY_GROUP) {
    return { text: CLOUD_INTO_HYPERSCALER_SENTENCE, reworded: false, approved: true }
  }
  if (!hyperscaler && targetGroup === AI_SECURITY_GROUP) {
    return { text: AI_SECURITY_INTO_PLATFORM_SENTENCE, reworded: true, approved: true }
  }
  if (!hyperscaler && targetGroup === CLOUD_SECURITY_GROUP) {
    return { text: CLOUD_INTO_PLATFORM_SENTENCE, reworded: true, approved: true }
  }
  return { text: CLOUD_INTO_HYPERSCALER_SENTENCE, reworded: false, approved: false }
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
      const combined = [...print.evidenceIds, ...item.evidenceIds]
      const evidenceIds = combined.filter((id, index) => combined.indexOf(id) === index)
      let read: string
      let readJudgedOn = judgedOn
      if (print.group === 'Identity') {
        read = identityAbsorbedRead(item.actor)
      } else {
        const wording = buyingInWording(item.actor, print.group)
        read = wording.text
        if (wording.reworded) readJudgedOn = WORDING_JUDGED_ON
      }
      return [
        {
          id: item.id,
          vendors: [print.name],
          position: print.position,
          print: rendered,
          read,
          provenance: {
            print: trackedFrom(evidenceIds),
            read: judged(evidenceIds, 'medium', readJudgedOn),
          },
        },
      ]
    })
}

export interface BuyingInWordingDecision {
  id: string
  actor: string
  target: string
  targetGroup: string
  approved: boolean
  reworded: boolean
  read: string
}

/**
 * Every non-Identity "buying in" row's acquirer, target, and the sentence
 * `buyingInRows` gave it, for tests and for reporting which rows, if any,
 * fall outside D-75's three approved cases (SEC-054).
 */
export function buyingInWordingDecisions(): BuyingInWordingDecision[] {
  const absorbed = positioned('absorbed')
  return activityItems
    .filter((item) => item.kind === 'ma')
    .flatMap((item) => {
      const print = absorbed.find((row) => row.name === item.target)
      if (!print || !print.position || print.group === 'Identity') return []
      const wording = buyingInWording(item.actor, print.group)
      return [
        {
          id: item.id,
          actor: item.actor,
          target: item.target,
          targetGroup: print.group,
          approved: wording.approved,
          reworded: wording.reworded,
          read: wording.text,
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
