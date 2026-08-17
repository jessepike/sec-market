export interface SignalFamily {
  name: string
  examples: string
  weTreatAs: string
  weDoNot: string
}

export interface ReasoningStep {
  step: string
  rule: string
}

export const signalFamilies: SignalFamily[] = [
  {
    name: 'Infrastructure prints',
    examples: 'NVIDIA Data Center, Cisco orders, Arista, Dell, Vertiv',
    weTreatAs: 'Supply and buildout. The lead layer.',
    weDoNot: 'Proof that security budgets will follow.',
  },
  {
    name: 'Hyperscaler capex',
    examples: 'Microsoft, Amazon, Alphabet cash investment',
    weTreatAs: 'Demand for capacity. Market condition, not a vendor score.',
    weDoNot: 'A security-spending forecast.',
  },
  {
    name: 'Security vendor prints',
    examples: 'Fortinet, SentinelOne, CrowdStrike, Rubrik, Varonis, SailPoint, Okta, Palo Alto, Cisco',
    weTreatAs: 'Realized category motion — after stripping acquisitions.',
    weDoNot: 'A boom from one headline growth rate.',
  },
  {
    name: 'Buyer budgets',
    examples: 'IANS security-budget growth and share of IT',
    weTreatAs: 'The best check on whether customers actually spent.',
    weDoNot: 'Vendor guidance dressed up as demand.',
  },
  {
    name: 'Buyer intent',
    examples: 'ETR planned increases, McKinsey AI-use surveys',
    weTreatAs: 'Direction of attention. Useful, early, weak.',
    weDoNot: 'Bookings or a category call.',
  },
  {
    name: 'Capital and M&A',
    examples: 'Wiz, CyberArk, Portkey, Astrix, Symmetry, Cyera, Onyx, Lumos',
    weTreatAs: 'Where incumbents are placing bets.',
    weDoNot: 'Customer spend. A $32B deal is not a demand series.',
  },
  {
    name: 'Forcing events',
    examples: 'DORA, SEC cyber rule, incidents, insurance hygiene',
    weTreatAs: 'Reasons spend can move on a different clock than infra.',
    weDoNot: 'A product-revenue print.',
  },
]

export const reasoningSteps: ReasoningStep[] = [
  {
    step: 'Separate the fact from the story',
    rule: 'Keep the excerpt, date, period, and metric definition. Interpretation sits next to it, not on top of it.',
  },
  {
    step: 'Do not collapse signal types',
    rule: 'Realized revenue, organic growth, guidance, intent, funding, and acquisitions stay in different buckets.',
  },
  {
    step: 'Need breadth before a domain call',
    rule: 'One strong print is a card. A domain posture needs more than one company and a reason the motion is not just share shift or M&A.',
  },
  {
    step: 'Refuse the lag if the window cannot support it',
    rule: 'A stable infra-to-security lag needs two mature buildout impulses and a comparable security response. This window has one mature impulse. That is a no-call, not a guessed number of quarters.',
  },
  {
    step: 'Action follows exposure, not the composite',
    rule: 'PREPARE only where the account has a matching live motion. A split market is not a license for a broad campaign, and this episode does not authorize RUN.',
  },
  {
    step: 'Age the edition; do not pretend it is live',
    rule: 'Keep the latest comparable print on the card. Demote still-true context. Leave superseded prints in evidence. Freeze acquired entities. Refresh on earnings, material capital events, and falsifiers — not on a news clock.',
  },
  {
    step: 'Date the posture; show the delta',
    rule: 'Every domain posture carries the date it was set, the horizon it governs, and the evidence that produced it. Each edition states what held or moved versus the prior edition. Do not overwrite the last state.',
  },
]
