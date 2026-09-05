import assert from 'node:assert/strict'
import { describe, it } from 'node:test'
import { issues } from '../src/data/issues/index.ts'
import {
  extractNumericTokens,
  isoWeekId,
  isoWeekSunday,
  issueEvidenceIds,
  parseVendorsParam,
  serializeVendorsParam,
  thesisRunningScore,
  vendorSlug,
  windowOf,
} from '../src/data/issueHelpers.ts'
import type { Issue } from '../src/data/types.ts'

function makeIssue(overrides: Partial<Issue> & Pick<Issue, 'id'>): Issue {
  return {
    id: overrides.id,
    weekEnding: overrides.weekEnding ?? isoWeekSunday(overrides.id),
    windowStart: overrides.windowStart ?? isoWeekSunday(overrides.id),
    published: overrides.published ?? null,
    status: overrides.status ?? 'draft',
    read: overrides.read ?? 'Test issue.',
    sections: overrides.sections ?? [
      { lane: 'formation', items: [] },
      { lane: 'absorption', items: [] },
      { lane: 'prints', items: [] },
      { lane: 'capital', items: [] },
    ],
    weThink: overrides.weThink ?? {
      summary: '',
      postureDeltas: [],
      thesis: null,
      noCalls: [],
      signedBy: null,
      signedOn: null,
    },
    proposed: overrides.proposed ?? null,
    sources: overrides.sources ?? { readable: 0, unreadable: [] },
  }
}

describe('isoWeekId / isoWeekSunday', () => {
  it('round-trips a known ISO week', () => {
    assert.equal(isoWeekId('2026-09-06'), '2026-w36')
    assert.equal(isoWeekSunday('2026-w36'), '2026-09-06')
    assert.equal(isoWeekSunday(isoWeekId('2026-09-06')), '2026-09-06')
  })

  it('agrees with every issue in the data set', () => {
    for (const issue of issues) {
      assert.equal(
        isoWeekSunday(issue.id),
        issue.weekEnding,
        `issue "${issue.id}" weekEnding does not match its id's ISO week Sunday`,
      )
      assert.equal(isoWeekId(issue.weekEnding), issue.id)
    }
  })

  it('rejects a malformed week id', () => {
    assert.throws(() => isoWeekSunday('2026-week-36'))
  })
})

describe('windowOf', () => {
  it('returns the issue window bounds', () => {
    const issue = makeIssue({ id: '2026-w36', windowStart: '2026-08-24', weekEnding: '2026-09-06' })
    assert.deepEqual(windowOf(issue), { start: '2026-08-24', end: '2026-09-06' })
  })
})

describe('thesisRunningScore', () => {
  it('is empty when there are no published issues', () => {
    const score = thesisRunningScore(issues)
    assert.deepEqual(score, { holds: 0, total: 0, since: null })
  })

  it('counts holds and strengthens but not no-call, and ignores drafts', () => {
    const published1 = makeIssue({
      id: '2026-w36',
      status: 'published',
      published: '2026-09-06',
      weThink: {
        summary: '',
        postureDeltas: [],
        thesis: { thesis: 'episode-002', verdict: 'holds', basis: '', confidence: 'high', evidenceIds: [] },
        noCalls: [],
        signedBy: 'Jesse Pike',
        signedOn: '2026-09-06',
      },
    })
    const published2 = makeIssue({
      id: '2026-w37',
      status: 'published',
      published: '2026-09-13',
      weThink: {
        summary: '',
        postureDeltas: [],
        thesis: {
          thesis: 'episode-002',
          verdict: 'strengthens',
          basis: '',
          confidence: 'medium',
          evidenceIds: [],
        },
        noCalls: [],
        signedBy: 'Jesse Pike',
        signedOn: '2026-09-13',
      },
    })
    const publishedNoCall = makeIssue({
      id: '2026-w38',
      status: 'published',
      published: '2026-09-20',
      weThink: {
        summary: '',
        postureDeltas: [],
        thesis: {
          thesis: 'episode-002',
          verdict: 'no-call',
          basis: '',
          confidence: 'low',
          evidenceIds: [],
        },
        noCalls: [],
        signedBy: 'Jesse Pike',
        signedOn: '2026-09-20',
      },
    })
    const draft = makeIssue({ id: '2026-w39', status: 'draft' })

    const score = thesisRunningScore([published1, published2, publishedNoCall, draft])
    assert.deepEqual(score, { holds: 2, total: 2, since: '2026-09-06' })
  })

  it('counts a weakens verdict toward the total but not toward holds', () => {
    const weakens = makeIssue({
      id: '2026-w36',
      status: 'published',
      published: '2026-09-06',
      weThink: {
        summary: '',
        postureDeltas: [],
        thesis: {
          thesis: 'episode-002',
          verdict: 'weakens',
          basis: '',
          confidence: 'medium',
          evidenceIds: [],
        },
        noCalls: [],
        signedBy: 'Jesse Pike',
        signedOn: '2026-09-06',
      },
    })
    assert.deepEqual(thesisRunningScore([weakens]), { holds: 0, total: 1, since: '2026-09-06' })
  })
})

describe('vendorSlug', () => {
  it('lower-cases and hyphenates', () => {
    assert.equal(vendorSlug('Fortinet'), 'fortinet')
    assert.equal(vendorSlug('Palo Alto Networks'), 'palo-alto-networks')
  })

  it('strips diacritics and non-ASCII punctuation', () => {
    assert.equal(vendorSlug('Crédit Vendor'), 'credit-vendor')
    assert.equal(vendorSlug("O'Reilly & Co."), 'o-reilly-co')
  })

  it('trims leading and trailing hyphens', () => {
    assert.equal(vendorSlug('  Zscaler  '), 'zscaler')
  })
})

describe('parseVendorsParam / serializeVendorsParam', () => {
  it('returns null when the vendors parameter is absent', () => {
    assert.equal(parseVendorsParam(''), null)
    assert.equal(parseVendorsParam('?other=1'), null)
  })

  it('splits, trims, and drops empty entries', () => {
    assert.deepEqual(parseVendorsParam('?vendors=crowdstrike,zscaler'), ['crowdstrike', 'zscaler'])
    assert.deepEqual(parseVendorsParam('?vendors= crowdstrike , zscaler '), ['crowdstrike', 'zscaler'])
    assert.deepEqual(parseVendorsParam('?vendors=crowdstrike,,zscaler'), ['crowdstrike', 'zscaler'])
  })

  it('returns null (same as absent) for a present but empty parameter — a cleared lens and a bare "?vendors=" render identically', () => {
    assert.equal(parseVendorsParam('?vendors='), null)
  })

  it('returns null for a parameter holding only commas/whitespace, since it names no real slug', () => {
    assert.equal(parseVendorsParam('?vendors=,,,'), null)
    assert.equal(parseVendorsParam('?vendors=  ,  '), null)
  })

  it('preserves an unrecognised slug rather than erroring', () => {
    assert.deepEqual(parseVendorsParam('?vendors=not-a-real-vendor'), ['not-a-real-vendor'])
  })

  it('serializes a slug list back into a comma-joined value', () => {
    assert.equal(serializeVendorsParam(['crowdstrike', 'zscaler']), 'crowdstrike,zscaler')
  })

  it('serializes null or an empty list to null, signalling "drop the parameter"', () => {
    assert.equal(serializeVendorsParam(null), null)
    assert.equal(serializeVendorsParam([]), null)
  })

  it('round-trips a slug list through parse and serialize', () => {
    const slugs = ['crowdstrike', 'zscaler']
    assert.deepEqual(parseVendorsParam(`?vendors=${serializeVendorsParam(slugs)}`), slugs)
  })
})

describe('extractNumericTokens', () => {
  it('excludes a digit run immediately preceded by a letter — a name/label, not a figure', () => {
    assert.deepEqual(extractNumericTokens('M12 led the round'), [])
    assert.deepEqual(extractNumericTokens('guidance holds into FY2027'), [])
    assert.deepEqual(extractNumericTokens('a Q2 update'), [])
  })

  it('keeps a currency amount with an M/B suffix', () => {
    assert.deepEqual(extractNumericTokens('HiddenLayer raises $100M Series B'), ['100M'])
    assert.deepEqual(extractNumericTokens('ARR crossed $1.47B this quarter'), ['1.47B'])
  })

  it('keeps a plain percentage, including a leading sign', () => {
    assert.deepEqual(extractNumericTokens('revenue grew 26%'), ['26%'])
    assert.deepEqual(extractNumericTokens('billings were +51% year over year'), ['51%'])
  })

  it('keeps a plain number with no letter attached', () => {
    assert.deepEqual(extractNumericTokens('the round brought in 1,200 new seats'), ['1200'])
  })

  it('does not truncate a name+digits token into a spurious remainder', () => {
    // "M12" must vanish entirely — not degrade into a stray "2" from the tail
    // of the digit run.
    assert.deepEqual(extractNumericTokens('backed by M12'), [])
  })

  it('still matches a genuine figure that happens to follow a name+digits token', () => {
    assert.deepEqual(extractNumericTokens('M12 joined the $100M round'), ['100M'])
  })

  it('excludes a digit run immediately followed by a non-magnitude letter — a name, not a figure', () => {
    assert.deepEqual(extractNumericTokens('1Password rolled out passkeys'), [])
  })

  it('keeps a bare figure with a legitimate M/B/K magnitude suffix', () => {
    assert.deepEqual(extractNumericTokens('$100M'), ['100M'])
    assert.deepEqual(extractNumericTokens('3M'), ['3M'])
  })

  it('keeps a bare percentage and a bare integer with no surrounding context', () => {
    assert.deepEqual(extractNumericTokens('26%'), ['26%'])
    assert.deepEqual(extractNumericTokens('+51%'), ['51%'])
    assert.deepEqual(extractNumericTokens('12'), ['12'])
  })
})

describe('issueEvidenceIds', () => {
  it('collects ids from items, posture deltas, and the thesis, deduplicated', () => {
    const issue = makeIssue({
      id: '2026-w36',
      sections: [
        {
          lane: 'formation',
          items: [
            {
              id: '2026-w36-formation-1',
              lane: 'formation',
              headline: 'Test headline',
              why: 'Because.',
              date: '2026-09-01',
              evidenceIds: ['E1', 'E2'],
            },
          ],
        },
        { lane: 'absorption', items: [] },
        { lane: 'prints', items: [] },
        { lane: 'capital', items: [] },
      ],
      weThink: {
        summary: '',
        postureDeltas: [
          {
            domainId: 'network-sase',
            from: 'INVESTIGATE',
            to: 'PREPARE',
            basis: 'Test basis.',
            confidence: 'medium',
            evidenceIds: ['E2', 'E3'],
          },
        ],
        thesis: {
          thesis: 'episode-002',
          verdict: 'holds',
          basis: '',
          confidence: 'high',
          evidenceIds: ['E4'],
        },
        noCalls: [],
        signedBy: null,
        signedOn: null,
      },
    })
    assert.deepEqual(new Set(issueEvidenceIds(issue)), new Set(['E1', 'E2', 'E3', 'E4']))
  })

  it('includes the machine proposal thesis evidence on a draft', () => {
    const issue = makeIssue({
      id: '2026-w37',
      proposed: {
        read: '',
        thesis: { thesis: 'episode-002', verdict: 'holds', basis: '', confidence: 'high', evidenceIds: ['E5'] },
        noCalls: [],
        postureDeltas: '',
        summary: '',
      },
    })
    assert.deepEqual(issueEvidenceIds(issue), ['E5'])
  })

  it('returns an empty array for the empty-lane skeleton', () => {
    for (const issue of issues) {
      if (issue.sections.every((section) => section.items.length === 0)) {
        assert.deepEqual(issueEvidenceIds(issue), [])
      }
    }
  })
})
