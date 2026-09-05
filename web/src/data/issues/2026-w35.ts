import type { Issue } from '../types'

/**
 * Dry-run draft (SEC-MARKET-GATHER-001 first run, per gather-job-spec.md §7).
 * Every source in the fixed manifest (docs/active/gather-brief.md §2) was
 * unreachable: this environment's outbound network policy rejected the
 * CONNECT to every host tried — Return on Security, Cybersecurity Ventures,
 * the specialist VC pages, SecurityWeek, and SEC.gov/EDGAR alike — with a 403
 * at the egress proxy, confirmed on three attempts each against the two
 * primary sources and once against every other manifest source, plus a
 * control fetch to a host outside the manifest. Zero documents were fetched,
 * so zero evidence records exist to cite and no item enters the draft.
 * `id`/`weekEnding`/`windowStart` are fixed by the dry-run instruction, not
 * computed from today's date, and deliberately overlap the existing
 * `2026-w36` issue's window — an expected `verify:issue` failure this draft
 * does not attempt to fix.
 */
export const issue2026w35: Issue = {
  id: '2026-w35',
  weekEnding: '2026-08-30',
  windowStart: '2026-08-24',
  published: null,
  status: 'draft',
  read: "Dry run: this environment's network policy blocked every outbound fetch — zero sources reachable.",
  quiet: true,
  sections: [
    { lane: 'formation', items: [] },
    { lane: 'absorption', items: [] },
    { lane: 'prints', items: [] },
    { lane: 'capital', items: [] },
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
    read: "Dry run: this environment's network policy blocked every outbound fetch — zero sources reachable.",
    thesis: {
      thesis: 'episode-002',
      verdict: 'no-call',
      basis:
        'No document in the fixed source manifest could be fetched this run: every outbound HTTPS request was rejected at the egress proxy with a 403 on CONNECT, confirmed against Return on Security, Cybersecurity Ventures, the specialist VC pages, SecurityWeek and SEC.gov/EDGAR, and against a control host outside the manifest. With zero evidence gathered, there is nothing to test the infrastructure-to-security lag call against this week; this is a no-call about this run, not a claim about the market.',
      confidence: 'low',
      evidenceIds: [],
    },
    noCalls: [
      'Everything this week is a no-call: zero sources were readable, so there is no evidence to weigh for or against any standing thesis or posture.',
    ],
    postureDeltas:
      'None proposed. No source was readable this run, so there is no evidence to support any posture change for any domain.',
    summary:
      "This was a dry run of the Tuesday gather with the id, weekEnding and windowStart fixed by the operator rather than computed, to test the pipeline before the schedule is armed. Every fetch attempt failed with a 403 from this environment's egress proxy, so no evidence was gathered and every lane is empty; the schedule should not be armed until the environment's network policy allows the sources named in docs/active/gather-brief.md §2.",
  },
  sources: {
    readable: 0,
    unreadable: [
      'https://www.returnonsecurity.com/',
      'https://cybersecurityventures.com/cybersecurity-venture-capital-vc-deals/',
      'https://www.synventures.com/portfolio',
      'https://forgepointcap.com/companies',
      'https://team8.vc/portfolio/',
      'https://www.ballisticventures.com/portfolio',
      'https://www.cyberstarts.com/portfolio',
      'https://www.ylventures.com/news',
      'https://www.evolutionequity.com/companies',
      'https://paladincapgroup.com/portfolio/',
      'https://www.securityweek.com/feed/',
      'https://efts.sec.gov/LATEST/search-index (EDGAR full-text search, all issuer queries)',
      'https://www.sec.gov/ (EDGAR filing pages)',
    ],
  },
}
