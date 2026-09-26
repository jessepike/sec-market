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

export interface SourcingRung {
  rung: number
  label: string
  description: string
  /** Whether a fact resting on this rung alone may publish. */
  publishesAlone: boolean
}

/**
 * The five-rung sourcing ladder the supplier tracker follows (step 5,
 * autonomy-coverage-plan.md §5; docs/active/fable-run/research/
 * 11-distress-signal-sources.md §5). Strongest evidence first. A fact
 * resting only on rung 5 — a single trade-press report with no primary
 * document behind it — does not publish on this site; it stays a lead until
 * a rung 1-4 source confirms it. web/scripts/verify-tracker.ts enforces this
 * on every tracker event at build time.
 */
export const sourcingLadder: SourcingRung[] = [
  {
    rung: 1,
    label: "Company's own SEC filing",
    description: 'An 8-K, 10-Q or 10-K filed with the SEC and readable on EDGAR.',
    publishesAlone: true,
  },
  {
    rung: 2,
    label: 'Rating agency action, republished',
    description:
      "A Moody's, S&P or Fitch rating action, most reliably read on the rated company's own newsroom.",
    publishesAlone: true,
  },
  {
    rung: 3,
    label: 'State WARN Act notice',
    description: 'A mass-layoff or closure notice filed with a state workforce agency.',
    publishesAlone: true,
  },
  {
    rung: 4,
    label: 'Confirmed primary corporate action',
    description: "An acquirer's own press release, or a company or parent's own wind-down statement.",
    publishesAlone: true,
  },
  {
    rung: 5,
    label: 'Trade press report',
    description: 'A news report, including one citing unnamed sources, with no primary document behind it.',
    publishesAlone: false,
  },
]

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
