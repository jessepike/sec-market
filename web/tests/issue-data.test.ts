import assert from 'node:assert/strict'
import { describe, it } from 'node:test'
import { issues } from '../src/data/issues/index.ts'
import {
  isoWeekId,
  isoWeekSunday,
  issueEvidenceIds,
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
