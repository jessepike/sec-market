import { activityItems } from './activity'
import { LAST_UPDATED_ISO, RESEARCH_FREEZE } from './meta'
import { vendorPrints } from './prints'
import type { Hypothesis, JudgedClaim } from './types'

const freezeDate = RESEARCH_FREEZE.slice(0, 10)
const trackingDate = LAST_UPDATED_ISO

function judged(evidenceIds: string[], judgedOn: string, confidence: JudgedClaim['confidence']): JudgedClaim {
  return { layer: 'judged', judgedOn, confidence, evidenceIds }
}

/** Renders a list as "A, B, C, D and E" instead of chaining " and " for every item. */
function formatList(items: string[]): string {
  if (items.length <= 1) return items.join('')
  if (items.length === 2) return items.join(' and ')
  return `${items.slice(0, -1).join(', ')} and ${items[items.length - 1]}`
}

const absorbedCloses = activityItems.filter(
  (item) =>
    item.kind === 'ma' && vendorPrints.some((print) => print.position === 'absorbed' && print.name === item.target),
)

const organic = vendorPrints.find((print) => print.position === 'platform' && print.metric.includes('organic'))
const organicPeers = organic
  ? vendorPrints.filter(
      (print) => print.group === organic.group && (print.position === 'challenger' || print.position === 'early'),
    )
  : []

export const hypotheses: Hypothesis[] = [
  {
    id: 'hyp-infra-lag',
    claim: 'Infrastructure spend leads security spend by a stable 0 to 8 quarters',
    state: 'NO-CALL',
    note: 'Needs two mature buildout impulses. This window has one.',
    firstTest: 'A second mature infrastructure impulse with a registered security response under fixed cohort rules',
    evidenceIds: ['LAG-NO-CALL', 'A1b', 'D1'],
    provenance: judged(['LAG-NO-CALL', 'A1b', 'D1'], freezeDate, 'high'),
  },
  {
    id: 'hyp-ai-compression',
    claim: 'AI adoption compresses that lag',
    state: 'NO-CALL',
    note: 'No series exists to test it against yet.',
    firstTest: 'A registered infrastructure impulse followed by a registered security response that can be attributed to AI adoption',
    evidenceIds: ['LAG-NO-CALL'],
    provenance: judged(['LAG-NO-CALL'], freezeDate, 'high'),
  },
  {
    id: 'hyp-platform-absorb',
    claim: 'Platforms absorb adjacent security categories rather than compete with them',
    state: 'TRACKING',
    note: formatList(absorbedCloses.map((item) => `${item.target} in ${item.domain}`)),
    firstTest: formatList(absorbedCloses.map((item) => `${item.target} in ${item.domain}`)),
    evidenceIds: absorbedCloses.flatMap((item) => item.evidenceIds),
    provenance: judged(
      absorbedCloses.flatMap((item) => item.evidenceIds),
      trackingDate,
      'medium',
    ),
  },
  {
    id: 'hyp-incumbent-outrun',
    claim: 'Incumbents that cannot pivot lose ground to challengers inside their own motion',
    state: 'TRACKING',
    note:
      organic && organicPeers.length > 0
        ? `${organicPeers.map((print) => print.name).join(' and ')} against ${organic.name} organic is the first test.`
        : 'No organic platform print is positioned for this test yet.',
    firstTest:
      organic && organicPeers.length > 0
        ? `${organicPeers.map((print) => print.name).join(' and ')} against ${organic.name} organic`
        : null,
    evidenceIds: [organic, ...organicPeers].flatMap((print) => print?.evidenceIds ?? []),
    provenance: judged(
      [organic, ...organicPeers].flatMap((print) => print?.evidenceIds ?? []),
      trackingDate,
      'medium',
    ),
  },
]
