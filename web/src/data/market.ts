import type { ContextStat, SummaryCard } from './types'
import { chartLayerPoints } from './derivePanel'
import { BUYER_BUDGET_GROWTH_ANNUAL, BUYER_SECURITY_SHARE_IT } from './panelRaw'

export interface MarketActions {
  doItems: string[]
  avoidItems: string[]
}

export interface MarketCall {
  headline: string
  subhead: string
  whatChanged: string[]
  actions: MarketActions
  meaning: string
  confidenceNote: string
  noCallBoundaries: string[]
  changeTriggers: string[]
  evidenceIds: string[]
}

export const contextStats: ContextStat[] = [
  { value: '+92%', label: 'NVIDIA Data Center', tone: 'up', evidenceIds: ['A1b'] },
  { value: '+4%', label: '2025 security budgets', tone: 'down', evidenceIds: ['D1'] },
  { value: 'NO-CALL', label: 'Infra → security lag', tone: 'hold', evidenceIds: ['LAG-NO-CALL'] },
]

export const marketCall: MarketCall = {
  headline: 'Infrastructure is running ahead. Security is splitting, not booming.',
  subhead:
    'Use infrastructure activation as an account qualification trigger — not as proof of a broad cybersecurity boom. A stable lag is still not measurable.',
  whatChanged: [
    'Cisco Q4 networking orders +40% and NVIDIA Data Center at $75.25B. The build is still on.',
    'Fortinet product +52% while Zscaler organic ARR is +21% and Cisco FY security is +2%. Network iron is hot; the category is not.',
    'Rubrik and Varonis are accelerating. Okta decelerated. CrowdStrike recovered. That is a split, not a wave.',
  ],
  actions: {
    doItems: [
      'Prepare the observed network refresh motion where it is already in flight. Do not rebrand it as infrastructure-lag capture.',
      'Ask when cloud/AI capacity, sensitive data, and machine identities go live.',
      'Prepare data/AI only for accounts putting sensitive data into new workloads.',
    ],
    avoidItems: [
      'Claiming a market-wide cybersecurity boom or a stable 0–8 quarter lag.',
      'Reading headline security growth without stripping acquisitions.',
      'Treating 2025 Wiz or CyberArk deals as this month’s demand signal.',
    ],
  },
  meaning:
    'Infrastructure is leading by a wide margin. Security’s useful movement is underneath the composite: appliance-led network is live, selected data vendors are up, identity and cloud lack a clean spend series, and buyer budgets did not follow in 2025. Prepare only where a client has matching exposure.',
  confidenceNote:
    'High on infrastructure acceleration. High that 2025 security budgets did not follow. Medium on the 2026 domain split. No-call on a stable lag.',
  noCallBoundaries: [
    'Stable 0–8-quarter infrastructure-to-security lag',
    'Domain-specific infrastructure lag',
    'AI compression of the lag',
    'Broad cybersecurity-boom motion',
  ],
  changeTriggers: [
    'Realized security-budget growth and rebound in security share of IT',
    'Organic acceleration across a majority of comparable security vendors',
    'Expansion from AI pilots into consequential production workloads',
    'A registered infrastructure impulse followed by a registered security response under fixed cohort rules',
  ],
  evidenceIds: ['A1b', 'D1', 'LAG-NO-CALL', 'C3', 'C6b'],
}

export const summaryCards: SummaryCard[] = [
  {
    id: 'infrastructure',
    label: 'Infrastructure cycle',
    headline: 'Accelerating',
    detail:
      'NVIDIA Data Center revenue reached $75.25B (+92% YoY). Hyperscaler capex and supplier orders/backlog remain broadly up.',
    disposition: 'High confidence',
    evidenceIds: ['A1b', 'B1', 'B2', 'A4', 'A5'],
  },
  {
    id: 'security-response',
    label: 'Security response',
    headline: 'Absent / mixed',
    detail:
      '2025 security-budget growth fell to 4% and security share of IT dropped to 10.9%. Selected vendors strengthened; Check Point, Cisco FY, and Okta remain weak or decelerating.',
    disposition: 'High confidence on budgets; mixed vendor breadth',
    evidenceIds: ['D1', 'C3', 'C6a', 'C6b', 'C7'],
  },
  {
    id: 'lag',
    label: 'Infrastructure-to-security lag',
    headline: 'NO-CALL',
    detail:
      'Only one mature broad infrastructure impulse is observable; a later wave is still deploying. Fourteen quarters at most — not enough for a stable lag estimate.',
    disposition: 'Sequence described; lag band not called',
    evidenceIds: ['LAG-NO-CALL', 'D1'],
  },
  {
    id: 'confidence',
    label: 'How to use this',
    headline: 'Good for account questions',
    detail:
      'Safe to use infrastructure activation as a reversible qualification question. Not safe to launch broad campaigns or pick vendors from this evidence alone.',
    disposition: 'High readiness for conversation; low for broad GTM',
    evidenceIds: ['LAG-NO-CALL', 'D1', 'D2'],
  },
]

export { chartLayerPoints }

export const chartEvidenceIds = [
  'A1a',
  'A1b',
  'B1',
  'B2',
  'B3',
  'C1',
  'C3',
  'C4',
  'C6a',
  'C6b',
  'C7',
]

export const chartMetricNote =
  'Panel window is calendar 2023-Q1 through 2026-Q1. Later JUL ’26 scorecard prints are not on these charts. Company fiscal quarters are mapped into those calendar buckets — NVIDIA FY27 Q1 (ended 2026-04-26) sits in 2026-Q1. All three charts share the same log-scale index axis (50–1800; 2023-Q1 = 100). Infrastructure: NVIDIA Data Center revenue. Hyperscaler: median indexed Microsoft, Amazon, and Alphabet quarterly cash capex (not additive). Security: median indexed CrowdStrike, Okta, Fortinet, Zscaler, and Check Point revenue where reported. Gaps remain null — no interpolation.'

export const buyerBudgetAnnual = [2023, 2024, 2025].map((year) => ({
  year,
  budgetGrowth: BUYER_BUDGET_GROWTH_ANNUAL[year],
  securityShareIt: BUYER_SECURITY_SHARE_IT[year],
}))
