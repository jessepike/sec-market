import assert from 'node:assert/strict'
import { describe, it } from 'node:test'
import {
  archiveEntriesNewestFirst,
  feedIssuesNewestFirst,
  issueEvidenceIds,
  issueJsonCopy,
} from '../src/data/issueHelpers.ts'
import type { EvidenceRecord, Issue } from '../src/data/types.ts'

/**
 * A small fixture standing in for the dist-generation pipeline
 * (generate-feed.ts / verify-dist.ts) without touching src/data: two
 * published issues (older, newer) and one newest draft — exactly the shape
 * a real `issues` array carries once an issue is signed off, but built by
 * hand so this test never drifts with real content.
 */
function makeEvidence(id: string, excerpt: string): EvidenceRecord {
  return {
    id,
    title: `Fixture evidence ${id}`,
    organization: 'Fixture Org',
    publicationDate: '2026-08-01',
    economicPeriod: 'Fixture period',
    canonicalUrl: `https://example.test/${id}`,
    excerpt,
    sourceClass: 'INDEPENDENT',
    interpretation: 'Fixture interpretation.',
    limitations: 'Fixture limitation.',
    conflictingEvidenceIds: [],
    artifactLabel: `FIXTURE / ${id}`,
    tags: ['fixture'],
  }
}

function makeIssue(overrides: Partial<Issue> & Pick<Issue, 'id' | 'weekEnding'>): Issue {
  return {
    id: overrides.id,
    weekEnding: overrides.weekEnding,
    windowStart: overrides.windowStart ?? overrides.weekEnding,
    published: overrides.published ?? null,
    status: overrides.status ?? 'draft',
    read: overrides.read ?? `Test issue ${overrides.id}.`,
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

const evidenceById: Record<string, EvidenceRecord> = {
  'FX-01': makeEvidence('FX-01', 'The older published issue cites this record verbatim.'),
  'FX-02': makeEvidence('FX-02', 'The newer published issue cites this record verbatim.'),
}

const olderPublished = makeIssue({
  id: '2026-w10',
  weekEnding: '2026-03-08',
  published: '2026-03-09',
  status: 'published',
  sections: [
    {
      lane: 'formation',
      items: [
        {
          id: '2026-w10-formation-1',
          lane: 'formation',
          headline: 'Older issue formation item',
          why: 'Fixture why.',
          date: '2026-03-05',
          evidenceIds: ['FX-01'],
        },
      ],
    },
    { lane: 'absorption', items: [] },
    { lane: 'prints', items: [] },
    { lane: 'capital', items: [] },
  ],
})

const newerPublished = makeIssue({
  id: '2026-w11',
  weekEnding: '2026-03-15',
  published: '2026-03-16',
  status: 'published',
  sections: [
    {
      lane: 'formation',
      items: [
        {
          id: '2026-w11-formation-1',
          lane: 'formation',
          headline: 'Newer issue formation item',
          why: 'Fixture why.',
          date: '2026-03-12',
          evidenceIds: ['FX-02'],
        },
      ],
    },
    { lane: 'absorption', items: [] },
    { lane: 'prints', items: [] },
    { lane: 'capital', items: [] },
  ],
})

const newestDraft = makeIssue({
  id: '2026-w12',
  weekEnding: '2026-03-22',
  status: 'draft',
  published: null,
})

const fixtureIssues: Issue[] = [olderPublished, newerPublished, newestDraft]

describe('archiveEntriesNewestFirst', () => {
  it('reverses the array order (newest first) and carries only the archive fields', () => {
    const entries = archiveEntriesNewestFirst(fixtureIssues)
    assert.deepEqual(
      entries.map((entry) => entry.id),
      ['2026-w12', '2026-w11', '2026-w10'],
    )
    assert.deepEqual(entries[0], {
      id: '2026-w12',
      weekEnding: '2026-03-22',
      published: null,
      status: 'draft',
      read: newestDraft.read,
    })
  })

  it('preserves the exact length — one entry per issue, draft included', () => {
    assert.equal(archiveEntriesNewestFirst(fixtureIssues).length, fixtureIssues.length)
  })
})

describe('feedIssuesNewestFirst', () => {
  it('excludes the draft and orders the two published issues newest-published-first', () => {
    const feedIssues = feedIssuesNewestFirst(fixtureIssues)
    assert.deepEqual(
      feedIssues.map((issue) => issue.id),
      ['2026-w11', '2026-w10'],
    )
  })

  it('excludes a "published" issue whose published date is still null', () => {
    const draftLikePublished = makeIssue({
      id: '2026-w09',
      weekEnding: '2026-03-01',
      status: 'published',
      published: null,
    })
    const feedIssues = feedIssuesNewestFirst([...fixtureIssues, draftLikePublished])
    assert.ok(!feedIssues.some((issue) => issue.id === '2026-w09'))
  })
})

describe('issueJsonCopy', () => {
  it('resolves the { issue, evidence } shape via issueEvidenceIds', () => {
    const copy = issueJsonCopy(olderPublished, evidenceById)
    assert.equal(copy.issue.id, '2026-w10')
    assert.deepEqual(
      copy.evidence.map((record) => record.id),
      issueEvidenceIds(olderPublished),
    )
    assert.deepEqual(
      copy.evidence.map((record) => record.id),
      ['FX-01'],
    )
  })

  it('throws, naming the issue and the unresolved id, when a cited evidence id does not resolve', () => {
    assert.throws(
      () => issueJsonCopy(olderPublished, {}),
      /issue "2026-w10" cites evidence id "FX-01" which does not resolve/,
    )
  })
})
