import type { Issue } from '../types'

/**
 * Gathered 2026-09-21 from the fixed source manifest in
 * `docs/active/gather-brief.md`. Machine-authored: `read`, the four lane
 * sections and `sources`. Unsigned draft — `proposed` is the gather's
 * proposal, not a judgment.
 */
export const issue2026w38: Issue = {
  id: '2026-w38',
  weekEnding: '2026-09-20',
  windowStart: '2026-09-14',
  published: null,
  status: 'draft',
  read: "Eight AI-security funding rounds land, led by Exein's $270 million raise, as S&P Global agrees to acquire OpenZeppelin.",
  sections: [
    {
      lane: 'formation',
      items: [
        {
          id: '2026-w38-formation-1',
          lane: 'formation',
          headline: 'AIUC raises $40 million Series A led by Ribbit Capital for frontier-AI confidence infrastructure',
          why: "The round adds to AIUC's $15 million seed, bringing total funding to $55 million.",
          date: '2026-09-15',
          evidenceIds: ['W38-02'],
          vendors: ['aiuc'],
        },
        {
          id: '2026-w38-formation-2',
          lane: 'formation',
          headline: 'Eve Security extends seed round to $7.5 million to police rogue AI agent behavior at runtime',
          why: 'The extension adds $4.5 million led by Run Ventures, with Dreamit Ventures, Blu Ventures and LiveOak Ventures also participating.',
          date: '2026-09-15',
          evidenceIds: ['W38-03'],
          vendors: ['eve-security'],
          domainId: 'ai-runtime',
        },
        {
          id: '2026-w38-formation-3',
          lane: 'formation',
          headline: 'Exein raises $270 million at a $1.7 billion valuation to secure physical AI',
          why: 'Headline led the round, joined by Sofina, Goldman Sachs and EIB Group, funding security for robots, drones and vehicles.',
          date: '2026-09-15',
          evidenceIds: ['W38-06'],
          vendors: ['exein'],
        },
        {
          id: '2026-w38-formation-4',
          lane: 'formation',
          headline: "StrikeReady lands Aramco-backed investment, lifting total funding to $29M",
          why: "Wa'ed Ventures, Aramco's domestic venture arm, backs the Composite AI platform for security operations.",
          date: '2026-09-16',
          evidenceIds: ['W38-05'],
          vendors: ['strikeready'],
          domainId: 'secops',
        },
        {
          id: '2026-w38-formation-5',
          lane: 'formation',
          headline: 'MIND raises $72M Series B for AI-era data loss prevention, lifting total funding to $112M',
          why: "Crosspoint Capital led the round with YL Ventures and Paladin Capital returning, a year after the company's $30M Series A.",
          date: '2026-09-17',
          evidenceIds: ['W38-01'],
          vendors: ['mind'],
          domainId: 'data-ai-security',
        },
        {
          id: '2026-w38-formation-6',
          lane: 'formation',
          headline: 'Comp AI raises $34 million Series A led by Roo Capital and Grand Ventures for agentic compliance',
          why: 'The startup positions continuous, agentic compliance automation against traditional GRC tooling.',
          date: '2026-09-17',
          evidenceIds: ['W38-04'],
          vendors: ['comp-ai'],
        },
        {
          id: '2026-w38-formation-7',
          lane: 'formation',
          headline: 'QueryLift raises a seed round from JAFCO and Z Venture Capital for GEO brand protection',
          why: 'The Tokyo-based startup defends brand identity in generative-engine search results, a category adjacent to core security.',
          date: '2026-09-17',
          evidenceIds: ['W38-08'],
          vendors: ['querylift'],
        },
        {
          id: '2026-w38-formation-8',
          lane: 'formation',
          headline: 'TigerByte Cyber emerges from stealth with $3 million seed led by Hale Capital Partners',
          why: 'Tenon VC also joined the round backing cyber hardening for AI and edge devices.',
          date: '2026-09-19',
          evidenceIds: ['W38-07'],
          vendors: ['tigerbyte-cyber'],
        },
      ],
    },
    {
      lane: 'absorption',
      items: [
        {
          id: '2026-w38-absorption-1',
          lane: 'absorption',
          headline: 'S&P Global agrees to acquire OpenZeppelin, the security standard for onchain finance',
          why: "The deal extends S&P Global's risk-assessment capabilities into onchain security standards and benchmarks.",
          date: '2026-09-17',
          evidenceIds: ['W38-09'],
          vendors: ['openzeppelin', 'sp-global'],
        },
      ],
    },
    {
      lane: 'prints',
      intro: 'None found this week.',
      items: [],
    },
    {
      lane: 'capital',
      intro: 'None found this week.',
      items: [],
    },
  ],
  weThink: {
    summary: '',
    postureDeltas: [],
    thesis: null,
    noCalls: [],
    signedBy: null,
    signedOn: null,
  },
  proposed: {
    read: "Eight AI-security funding rounds land, led by Exein's $270 million raise, as S&P Global agrees to acquire OpenZeppelin.",
    noCalls: [
      'No comparable earnings prints or capital-spend evidence landed in-window, so the standing infrastructure-to-security lag call is unchanged by this window — no-call stands.',
    ],
    postureDeltas:
      'None proposed. No prints or capital evidence entered this window to move any domain posture, and eight early-stage formation rounds are not by themselves grounds to move one.',
    summary:
      'This window was formation-heavy and otherwise quiet: eight venture rounds across AI-agent runtime security, AI-risk underwriting, data-security-for-AI, and physical-AI security, plus one disclosed acquisition of a smart-contract security standard-setter by a public financial-data incumbent. No public-issuer earnings print or capital-spend disclosure fell inside the window.',
  },
  sources: {
    readable: 20,
    unreadable: [
      'http://www.businesswire.com/news/home/20260916319331/en/Hackuity-Raises-%2419-Million-to-Help-Enterprises-Prepare-for-the-AI-Driven-Vulnerability-Explosion',
      'https://www.hackuity.io/',
    ],
  },
}
