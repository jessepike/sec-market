import type { Issue } from '../types'

/**
 * Second issue. Drafted 2026-09-20 from Return on Security #261 as a lead list,
 * then rebuilt so that every item carries its own primary document with a date
 * confirmed inside the window. Machine-authored: `read`, the four lane sections,
 * `sources` and `proposed`. `weThink` stays empty/null until a named person
 * signs it.
 */
export const issue2026w37: Issue = {
  id: '2026-w37',
  weekEnding: '2026-09-13',
  windowStart: '2026-09-07',
  published: null,
  status: 'draft',
  read: 'Oracle books a backlog of $664 billion while security capital scatters into small rounds and priceless acquisitions.',
  sections: [
    {
      lane: 'formation',
      intro:
        'Four rounds carry a confirmed date and a primary source this week. One is very large and the rest are small.',
      items: [
        {
          id: '2026-w37-formation-1',
          lane: 'formation',
          headline: 'Cylake raises $245 million through a convertible note for a sovereign security platform',
          why: 'The largest security round of the week funds a platform whose beta is not expected until the end of the year.',
          date: '2026-09-08',
          evidenceIds: ['W37-01'],
          vendors: ['cylake'],
          domainId: 'secops',
        },
        {
          id: '2026-w37-formation-2',
          lane: 'formation',
          headline: 'Quantinuum finalizes $100 million in federal funding under the CHIPS and Science Act',
          why: 'Public money rather than venture money, funding cryptographic hardware capability.',
          date: '2026-09-08',
          evidenceIds: ['W37-02'],
          vendors: ['quantinuum'],
        },
        {
          id: '2026-w37-formation-3',
          lane: 'formation',
          headline: 'ZeroRisk raises $10 million in Series A funding for merchant cyber risk management',
          why: 'A narrow vertical play, selling risk visibility to payment providers rather than to enterprises.',
          date: '2026-09-09',
          evidenceIds: ['W37-03'],
          vendors: ['zerorisk'],
        },
        {
          id: '2026-w37-formation-4',
          lane: 'formation',
          headline: 'HelmGuard raises a seed round to replace compliance paperwork with AI agents',
          why: 'Governance tooling for agents is now raising on its own, separately from agent runtime security.',
          date: '2026-09-09',
          evidenceIds: ['W37-04'],
          vendors: ['helmguard-ai'],
          domainId: 'ai-runtime',
        },
      ],
    },
    {
      lane: 'absorption',
      intro:
        'Five acquisitions with a confirmed date, and not one of them disclosed a price. Two of the five buyers are financial sponsors rather than security companies.',
      items: [
        {
          id: '2026-w37-absorption-1',
          lane: 'absorption',
          headline: 'Surfshark acquires Optery, a data removal company, for an undisclosed amount',
          why: 'Consumer privacy tooling consolidating into a consumer VPN brand.',
          date: '2026-09-07',
          evidenceIds: ['W37-05'],
          vendors: ['surfshark', 'optery'],
        },
        {
          id: '2026-w37-absorption-2',
          lane: 'absorption',
          headline: 'Kiteworks acquires Bonfy.AI, an AI data security company, for an undisclosed amount',
          why: 'Another AI data security asset absorbed with no price and no materiality statement.',
          date: '2026-09-08',
          evidenceIds: ['W37-06'],
          vendors: ['kiteworks', 'bonfy-ai'],
          domainId: 'data-ai-security',
        },
        {
          id: '2026-w37-absorption-3',
          lane: 'absorption',
          headline: 'Apax completes the acquisition of NextGen Security from Dunes Point Capital',
          why: 'A financial sponsor buying security integration services rather than product.',
          date: '2026-09-09',
          evidenceIds: ['W37-07'],
          vendors: ['apax-partners', 'nextgen-security'],
        },
        {
          id: '2026-w37-absorption-4',
          lane: 'absorption',
          headline: 'InfraVia takes a majority stake in Nexis, a German identity governance vendor',
          why: 'Identity governance changing hands between sponsors rather than being bought by a security platform.',
          date: '2026-09-09',
          evidenceIds: ['W37-08'],
          vendors: ['infravia', 'nexis'],
          domainId: 'identity',
        },
        {
          id: '2026-w37-absorption-5',
          lane: 'absorption',
          headline: 'SecureSky acquires Soveren, adding data security posture management to its platform',
          why: 'Posture management folding into managed detection and response, again with no price.',
          date: '2026-09-09',
          evidenceIds: ['W37-09'],
          vendors: ['securesky', 'soveren'],
          domainId: 'data-ai-security',
        },
      ],
    },
    {
      lane: 'prints',
      intro: 'One pure-play security issuer reported inside the window.',
      items: [
        {
          id: '2026-w37-prints-1',
          lane: 'prints',
          headline: 'SailPoint grows ARR 25% to $1.231 billion; SaaS ARR up 36% to $847 million',
          why: 'Identity is compounding, and this is the first print here to attach a disclosed figure to AI-driven security revenue.',
          date: '2026-09-09',
          evidenceIds: ['W37-10'],
          vendors: ['sailpoint'],
          domainId: 'identity',
        },
      ],
    },
    {
      lane: 'capital',
      intro: 'The infrastructure impulse got materially larger inside this window.',
      items: [
        {
          id: '2026-w37-capital-1',
          lane: 'capital',
          headline: 'Oracle books Remaining Performance Obligations up $209 billion to $664 billion',
          why: 'The largest contracted-backlog figure this project has recorded, and it is signed capacity rather than a forecast.',
          date: '2026-09-10',
          evidenceIds: ['W37-11'],
          vendors: ['oracle'],
        },
      ],
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
    read: 'Oracle books a backlog of $664 billion while security capital scatters into small rounds and priceless acquisitions.',
    thesis: {
      thesis: 'episode-002',
      verdict: 'holds',
      basis:
        'This window widens the gap the call is about rather than closing it. Oracle added $209 billion of Remaining Performance Obligations year over year to reach $664 billion, which is the largest contracted-backlog figure recorded here and a very large infrastructure impulse inside a single week. Against it the security side produced four datable rounds, the largest of which funds a product that has not shipped, five acquisitions with no disclosed price between them, and one public print. Security demand is not absent, and SailPoint grew ARR 25% to $1.231 billion, but nothing in this window is the registered security response the fixed-lag question needs.',
      confidence: 'medium',
      evidenceIds: ['W37-11', 'W37-10', 'W37-01', 'W37-06'],
    },
    noCalls: [
      'Stable 0–8-quarter infrastructure-to-security lag: a second consecutive window pairs a large infrastructure impulse with scattered, small security formation, which is consistent with the no-call rather than resolving it into a measured number of quarters.',
    ],
    postureDeltas:
      'None proposed, with one flagged for a human look. SailPoint is the first print in this data set to put a disclosed figure on AI-driven revenue inside a security business, and that is a different kind of evidence from the acquisition-led AI activity recorded so far, where acquirers stated the acquired revenue was immaterial. One print is not a posture change and Identity should not move on it alone, but if a second identity or platform issuer prints a comparable figure, Identity is the card to revisit. Nothing else this window argues for a change to any domain posture.',
    summary:
      'A scattered week for security capital sat beside a very loud one for infrastructure: four datable rounds, five acquisitions with no disclosed price between them, and one public print, against Oracle booking a contracted backlog of $664 billion. The signal worth keeping is SailPoint, which put a disclosed AI revenue figure on the board in identity rather than promising one.',
  },
  sources: {
    readable: 11,
    unreadable: [
      'https://www.tipranks.com/news/company-announcements/cy4gate-takes-full-control-of-french-cyber-firm-diateam-to-boost-european-growth',
      'https://www.securityweek.com/feed/',
      'https://cybersecurityventures.com/cybersecurity-venture-capital-vc-deals/',
    ],
  },
}
