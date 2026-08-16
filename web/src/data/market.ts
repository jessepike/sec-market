import type { SummaryCard } from './types'
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

export const marketCall: MarketCall = {
  headline: 'Infrastructure is accelerating. A stable security-spending lag is not measurable.',
  subhead:
    'Use infrastructure activation as an account qualification trigger — not as proof of a broad cybersecurity boom.',
  whatChanged: [
    'Infrastructure spend is still rising — NVIDIA Data Center revenue went from $4.28B to $75.25B across the frozen window.',
    'Broad security budgets did not keep pace: IANS reports 4% average growth in 2025 and security fell to 10.9% of IT spend.',
    'Some security categories strengthened later (network/SASE, selected data vendors, AI-protection intent) — for different reasons, not one uniform wave.',
  ],
  actions: {
    doItems: [
      'Ask when cloud/AI capacity, sensitive data, and machine identities go live.',
      'Refresh cloud, identity, and data qualification views for exposed accounts.',
      'Tie network/SASE talk to observed refresh — not assumed lag capture.',
    ],
    avoidItems: [
      'Claiming a market-wide cybersecurity boom or a stable 0–8 quarter lag.',
      'Scaling broad GTM without realized buyer spend and organic vendor breadth.',
      'Treating Wiz or CyberArk acquisitions as proof of customer spend.',
    ],
  },
  meaning:
    'The infrastructure build is real and still accelerating. Security evidence is mixed across refresh, recovery, platformization, intent, and selected organic growth. Prepare bounded, domain-specific readiness only where a client has relevant exposure.',
  confidenceNote:
    'High confidence on infrastructure acceleration; high confidence that broad security-budget response through 2025 was absent or weakened; medium confidence on selected domain strengthening in 2025–2026.',
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
  evidenceIds: ['A1b', 'D1', 'LAG-NO-CALL', 'C3', 'C6'],
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
    evidenceIds: ['D1', 'C3', 'C6', 'C7'],
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
  'C6',
  'C7',
]

export const chartMetricNote =
  'All three charts share the same log-scale index axis (50–1800; 2023-Q1 = 100) so an 18× move and a 2× move look proportionally different. Infrastructure: NVIDIA Data Center revenue. Hyperscaler: median indexed Microsoft, Amazon, and Alphabet quarterly cash capex (not additive). Security: median indexed CrowdStrike, Okta, Fortinet, Zscaler, and Check Point revenue where reported. Gaps remain null — no interpolation.'

export const buyerBudgetAnnual = [2023, 2024, 2025].map((year) => ({
  year,
  budgetGrowth: BUYER_BUDGET_GROWTH_ANNUAL[year],
  securityShareIt: BUYER_SECURITY_SHARE_IT[year],
}))
