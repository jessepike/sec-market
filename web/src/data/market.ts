import type { MarketCall, MarketLayerSeries, SummaryCard } from './types'

export const marketCall: MarketCall = {
  headline: 'Infrastructure is accelerating. A stable security-spending lag is not measurable.',
  subhead:
    'Use infrastructure activation as an account qualification trigger — not as proof of a broad cybersecurity boom.',
  meaning:
    'The infrastructure build is real and still accelerating. Security evidence is mixed across refresh, recovery, platformization, intent, and selected organic growth. Prepare bounded, domain-specific readiness only where a client has relevant exposure.',
  confidenceNote:
    'High confidence on infrastructure acceleration; high confidence that broad security-budget response through 2025 was absent or weakened; medium confidence on selected domain strengthening in 2025–2026.',
  noCallBoundaries: [
    'Stable 0–8-quarter infrastructure-to-security lag: NO-CALL',
    'Domain-specific infrastructure lag: NO-CALL',
    'AI compression of the lag: NO-CALL',
    'Broad cybersecurity-boom motion: not supported',
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
      'Only one mature broad infrastructure impulse is observable; the second impulse is right-censored. Fourteen quarters at most — insufficient for a stable lag estimate.',
    disposition: 'NO-CALL',
    evidenceIds: ['LAG-NO-CALL', 'D1'],
  },
  {
    id: 'confidence',
    label: 'Decision confidence',
    headline: 'Qualification trigger — high readiness',
    detail:
      'Using infrastructure activation as a reversible account question is high-readiness. Scaling a broad GTM campaign or vendor selection is not authorized by this episode.',
    disposition: 'Action readiness: high for conversation; low for broad GTM',
    evidenceIds: ['LAG-NO-CALL', 'D1', 'D2'],
  },
]

/** Indexed to 2023-Q1 = 100. Layers are within-company direction checks, not additive. */
export const marketLayerSeries: MarketLayerSeries[] = [
  { quarter: '2023-Q1', infrastructure: 100, hyperscaler: 100, security: 100, buyerBudget: 6 },
  { quarter: '2023-Q2', infrastructure: 241, hyperscaler: 128, security: 106, buyerBudget: null },
  { quarter: '2023-Q3', infrastructure: 339, hyperscaler: 138, security: 113, buyerBudget: null },
  { quarter: '2023-Q4', infrastructure: 430, hyperscaler: 147, security: 121, buyerBudget: null },
  { quarter: '2024-Q1', infrastructure: 527, hyperscaler: 166, security: 131, buyerBudget: 8 },
  { quarter: '2024-Q2', infrastructure: 613, hyperscaler: 201, security: 138, buyerBudget: null },
  { quarter: '2024-Q3', infrastructure: 718, hyperscaler: 228, security: 145, buyerBudget: null },
  { quarter: '2024-Q4', infrastructure: 831, hyperscaler: 268, security: 153, buyerBudget: null },
  { quarter: '2025-Q1', infrastructure: 914, hyperscaler: 284, security: 158, buyerBudget: 4 },
  { quarter: '2025-Q2', infrastructure: 960, hyperscaler: 339, security: 167, buyerBudget: null },
  { quarter: '2025-Q3', infrastructure: 1197, hyperscaler: 370, security: null, buyerBudget: null },
  { quarter: '2025-Q4', infrastructure: 1456, hyperscaler: 421, security: 176, buyerBudget: null },
  { quarter: '2026-Q1', infrastructure: 1758, hyperscaler: 467, security: 200, buyerBudget: null },
]

export const chartEvidenceIds = ['A1a', 'A1b', 'B1', 'B2', 'B3', 'C1', 'D1']

export const chartMetricNote =
  'Infrastructure: NVIDIA Data Center revenue indexed to 2023-Q1. Hyperscaler: median of Microsoft, Amazon, and Alphabet quarterly cash capex indexed to 2023-Q1 (not additive). Security: median indexed revenue of CrowdStrike, Okta, Fortinet, Zscaler, and Check Point where reported. Buyer: IANS average annual security-budget growth (%).'
