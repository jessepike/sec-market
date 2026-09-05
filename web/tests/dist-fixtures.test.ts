import assert from 'node:assert/strict'
import { mkdtempSync, readFileSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { describe, it } from 'node:test'
import {
  archiveEntriesNewestFirst,
  feedIssuesNewestFirst,
  issueEvidenceIds,
  issueJsonCopy,
} from '../src/data/issueHelpers.ts'
import type { EvidenceRecord, Issue } from '../src/data/types.ts'
import {
  writeFeedXml,
  writeIssueJsonCopies,
  writeIssuesIndexJson,
  writeLockManifestCopy,
} from '../scripts/generate-feed.ts'
import {
  checkEveryIssueJsonExists,
  checkFeedXmlExistsAndParses,
  checkIssuesIndexJsonExists,
  checkLockJsonMatchesSource,
} from '../scripts/verify-dist.ts'

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

/**
 * Runs the REAL generate-feed.ts writers against this file's two-published-
 * plus-one-draft fixture into a temp directory, then runs the REAL
 * verify-dist.ts checks against that directory — not a re-implementation of
 * either. This is what catches the writer and its own checker silently
 * agreeing on the wrong thing (Codex whole-diff review finding 3): the old
 * version of this file exercised only the pure helpers underneath, never the
 * writer or the checker that call them.
 *
 * Route/sitemap/description checks (11a, 11e, 11g) are not run here — they
 * need prerendered route HTML, which is prerender.ts + generate-seo.ts's
 * job, not generate-feed.ts's; see that file's own header comment.
 */
describe('dist pipeline (real writers + real checks, fixture data)', () => {
  const tmpDir = mkdtempSync(join(tmpdir(), 'smp-dist-fixture-'))
  const lockSourcePath = join(tmpDir, 'source-issues.lock.json')
  const fixtureLockManifest = {
    '2026-w10': 'a'.repeat(64),
    '2026-w11': 'b'.repeat(64),
  }

  it('writes feed.xml, issue JSON copies, index.json and lock.json, and every real check passes', () => {
    writeFeedXml(fixtureIssues, tmpDir)
    writeIssueJsonCopies(fixtureIssues, evidenceById, tmpDir)
    writeIssuesIndexJson(fixtureIssues, tmpDir)
    writeFileSync(lockSourcePath, `${JSON.stringify(fixtureLockManifest, null, 2)}\n`)
    writeLockManifestCopy(tmpDir, lockSourcePath)

    const results = [
      checkEveryIssueJsonExists(tmpDir, fixtureIssues),
      checkIssuesIndexJsonExists(tmpDir, fixtureIssues),
      checkFeedXmlExistsAndParses(tmpDir, fixtureIssues),
      checkLockJsonMatchesSource(tmpDir, lockSourcePath),
    ]
    for (const result of results) {
      assert.equal(result.pass, true, `${result.name} unexpectedly failed: ${result.detail}`)
    }
  })

  it('perturbation: an issue JSON copy that disagrees with the source issue fails 11b, and restoring it passes again', () => {
    const path = join(tmpDir, 'issues', '2026-w10.json')
    const original = readFileSync(path, 'utf8')
    const perturbed = JSON.parse(original)
    perturbed.issue.read = 'Perturbed for the test — this must not deep-equal the source issue.'
    writeFileSync(path, JSON.stringify(perturbed, null, 2))

    const failed = checkEveryIssueJsonExists(tmpDir, fixtureIssues)
    assert.equal(failed.pass, false)
    assert.match(failed.detail ?? '', /does not deep-equal the source issue/)

    writeFileSync(path, original)
    const restored = checkEveryIssueJsonExists(tmpDir, fixtureIssues)
    assert.equal(restored.pass, true, `expected 11b to pass after restoring: ${restored.detail}`)
  })

  it('perturbation: an archive row missing a field fails 11c, and restoring it passes again', () => {
    const path = join(tmpDir, 'issues/index.json')
    const original = readFileSync(path, 'utf8')
    const parsed = JSON.parse(original)
    delete parsed[0].url
    writeFileSync(path, JSON.stringify(parsed, null, 2))

    const failed = checkIssuesIndexJsonExists(tmpDir, fixtureIssues)
    assert.equal(failed.pass, false)
    assert.match(failed.detail ?? '', /does not deep-equal the expected row/)

    writeFileSync(path, original)
    const restored = checkIssuesIndexJsonExists(tmpDir, fixtureIssues)
    assert.equal(restored.pass, true, `expected 11c to pass after restoring: ${restored.detail}`)
  })

  it('perturbation: a feed item pubDate that disagrees with its issue fails 11d, and restoring it passes again', () => {
    const path = join(tmpDir, 'feed.xml')
    const original = readFileSync(path, 'utf8')
    const perturbed = original.replace(
      /<pubDate>[^<]*<\/pubDate>/,
      '<pubDate>Mon, 01 Jan 2001 00:00:00 GMT</pubDate>',
    )
    assert.notEqual(perturbed, original, 'the test fixture setup did not find a pubDate to perturb')
    writeFileSync(path, perturbed)

    const failed = checkFeedXmlExistsAndParses(tmpDir, fixtureIssues)
    assert.equal(failed.pass, false)
    assert.match(failed.detail ?? '', /pubDate is/)

    writeFileSync(path, original)
    const restored = checkFeedXmlExistsAndParses(tmpDir, fixtureIssues)
    assert.equal(restored.pass, true, `expected 11d to pass after restoring: ${restored.detail}`)
  })

  it('perturbation: a nested <item> in feed.xml is rejected rather than silently truncated, and restoring it passes again', () => {
    const path = join(tmpDir, 'feed.xml')
    const original = readFileSync(path, 'utf8')
    const nested = original.replace('<item>', '<item><item>')
    assert.notEqual(nested, original, 'the test fixture setup did not find an <item> to nest inside')
    writeFileSync(path, nested)

    const failed = checkFeedXmlExistsAndParses(tmpDir, fixtureIssues)
    assert.equal(failed.pass, false)
    assert.match(failed.detail ?? '', /nested <item>/)

    writeFileSync(path, original)
    const restored = checkFeedXmlExistsAndParses(tmpDir, fixtureIssues)
    assert.equal(restored.pass, true, `expected 11d to pass after restoring: ${restored.detail}`)
  })

  it('perturbation: dist/issues/lock.json disagreeing with the source manifest fails 11f, and restoring it passes again', () => {
    const path = join(tmpDir, 'issues/lock.json')
    const original = readFileSync(path, 'utf8')
    writeFileSync(path, `${JSON.stringify({ '2026-w10': 'c'.repeat(64) }, null, 2)}\n`)

    const failed = checkLockJsonMatchesSource(tmpDir, lockSourcePath)
    assert.equal(failed.pass, false)

    writeFileSync(path, original)
    const restored = checkLockJsonMatchesSource(tmpDir, lockSourcePath)
    assert.equal(restored.pass, true, `expected 11f to pass after restoring: ${restored.detail}`)
  })
})
