import assert from 'node:assert/strict'
import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { describe, it } from 'node:test'
import { pathToFileURL } from 'node:url'
import {
  computeSignedIssue,
  findDraftToSign,
  isProposedEmpty,
  isValidIsoDate,
  postureDeltasDroppedCount,
} from '../scripts/signIssueLogic.ts'
import { issueExportName, renderIssueModule, tsLiteral } from '../scripts/signIssueRender.ts'
import type { Issue } from '../src/data/types.ts'

function draftIssue(overrides: Partial<Issue> = {}): Issue {
  return {
    id: '2026-w37',
    weekEnding: '2026-09-13',
    windowStart: '2026-09-07',
    published: null,
    status: 'draft',
    read: 'Test read.',
    sections: [
      { lane: 'formation', items: [] },
      { lane: 'absorption', items: [] },
      { lane: 'prints', items: [] },
      { lane: 'capital', items: [] },
    ],
    weThink: { summary: '', postureDeltas: [], thesis: null, noCalls: [], signedBy: null, signedOn: null },
    proposed: {
      read: 'Test read.',
      noCalls: ['A no-call.'],
      postureDeltas: 'None proposed.',
      summary: 'A test summary.',
    },
    sources: { readable: 1, unreadable: [] },
    ...overrides,
  }
}

function publishedIssue(overrides: Partial<Issue> = {}): Issue {
  return draftIssue({
    status: 'published',
    published: '2026-09-06',
    weThink: {
      summary: 'Signed.',
      postureDeltas: [],
      thesis: null,
      noCalls: [],
      signedBy: 'Jesse Pike',
      signedOn: '2026-09-06',
    },
    proposed: null,
    ...overrides,
  })
}

describe('isValidIsoDate', () => {
  it('accepts a real calendar date', () => {
    assert.equal(isValidIsoDate('2026-09-20'), true)
  })

  it('rejects a malformed or non-existent date', () => {
    assert.equal(isValidIsoDate('2026-09-31'), false) // September has 30 days
    assert.equal(isValidIsoDate('09-20-2026'), false)
    assert.equal(isValidIsoDate('2026-9-20'), false)
    assert.equal(isValidIsoDate('not-a-date'), false)
    assert.equal(isValidIsoDate(''), false)
  })
})

describe('isProposedEmpty', () => {
  it('is true for null', () => {
    assert.equal(isProposedEmpty(null), true)
  })

  it('is true when read or summary is blank', () => {
    assert.equal(isProposedEmpty({ read: '', noCalls: [], postureDeltas: '', summary: 'x' }), true)
    assert.equal(isProposedEmpty({ read: '  ', noCalls: [], postureDeltas: '', summary: 'x' }), true)
    assert.equal(isProposedEmpty({ read: 'x', noCalls: [], postureDeltas: '', summary: '' }), true)
  })

  it('is false for a substantive proposal', () => {
    assert.equal(isProposedEmpty({ read: 'x', noCalls: [], postureDeltas: '', summary: 'y' }), false)
  })
})

describe('postureDeltasDroppedCount', () => {
  it('is 0 for a blank string', () => {
    assert.equal(postureDeltasDroppedCount({ read: 'x', noCalls: [], postureDeltas: '', summary: 'y' }), 0)
    assert.equal(postureDeltasDroppedCount({ read: 'x', noCalls: [], postureDeltas: '   ', summary: 'y' }), 0)
  })

  it('is 0 for the gather-brief.md "nothing to propose" convention, case-insensitively', () => {
    assert.equal(
      postureDeltasDroppedCount({ read: 'x', noCalls: [], postureDeltas: 'None proposed.', summary: 'y' }),
      0,
    )
    assert.equal(
      postureDeltasDroppedCount({ read: 'x', noCalls: [], postureDeltas: 'none proposed', summary: 'y' }),
      0,
    )
  })

  it('is 1 for a real proposed note, even one that leads with "none proposed"', () => {
    assert.equal(
      postureDeltasDroppedCount({
        read: 'x',
        noCalls: [],
        postureDeltas: 'None proposed, with one flagged for a human look at the CrowdStrike stance.',
        summary: 'y',
      }),
      1,
    )
    assert.equal(
      postureDeltasDroppedCount({
        read: 'x',
        noCalls: [],
        postureDeltas: 'Consider softening the cloud-security stance given two weak prints.',
        summary: 'y',
      }),
      1,
    )
  })
})

describe('findDraftToSign', () => {
  it('refuses when there is no draft', () => {
    assert.throws(() => findDraftToSign([publishedIssue()], null), /no draft issue found/)
  })

  it('refuses when more than one draft exists, even with --id given', () => {
    const a = draftIssue({ id: '2026-w37' })
    const b = draftIssue({ id: '2026-w38', weekEnding: '2026-09-20', windowStart: '2026-09-14' })
    assert.throws(() => findDraftToSign([a, b], null), /2 draft issues found/)
    assert.throws(() => findDraftToSign([a, b], '2026-w37'), /2 draft issues found/)
  })

  it('refuses when proposed is null or empty', () => {
    assert.throws(() => findDraftToSign([draftIssue({ proposed: null })], null), /no proposed content/)
    assert.throws(
      () =>
        findDraftToSign(
          [draftIssue({ proposed: { read: '', noCalls: [], postureDeltas: '', summary: '' } })],
          null,
        ),
      /no proposed content/,
    )
  })

  it('refuses an issue that is already signed', () => {
    assert.throws(() => findDraftToSign([publishedIssue()], '2026-w37'), /already signed/)
  })

  it('refuses when --id names no known issue', () => {
    assert.throws(() => findDraftToSign([draftIssue()], '2026-w99'), /no issue with id/)
  })

  it('refuses an inconsistently-marked draft that already carries signed fields', () => {
    const corrupt = draftIssue({
      weThink: { summary: '', postureDeltas: [], thesis: null, noCalls: [], signedBy: 'Jesse Pike', signedOn: null },
    })
    assert.throws(() => findDraftToSign([corrupt], null), /already carries signed fields/)
  })

  it('returns the one valid draft, with or without a matching --id', () => {
    const draft = draftIssue()
    assert.equal(findDraftToSign([draft], null), draft)
    assert.equal(findDraftToSign([draft], '2026-w37'), draft)
  })
})

describe('computeSignedIssue', () => {
  it('publishes the draft: signedBy/signedOn/published set, proposed nulled, thesis null, postureDeltas empty', () => {
    const draft = draftIssue()
    const signed = computeSignedIssue(draft, { signedOn: '2026-09-20', authorName: 'Jesse Pike' })

    assert.equal(signed.status, 'published')
    assert.equal(signed.published, '2026-09-20')
    assert.equal(signed.proposed, null)
    assert.equal(signed.weThink.signedBy, 'Jesse Pike')
    assert.equal(signed.weThink.signedOn, '2026-09-20')
    assert.equal(signed.weThink.summary, draft.proposed?.summary)
    assert.deepEqual(signed.weThink.noCalls, draft.proposed?.noCalls)
    assert.equal(signed.weThink.thesis, null)
    assert.deepEqual(signed.weThink.postureDeltas, [])
    assert.equal(signed.read, draft.read) // untouched — already equals proposed.read
  })

  it("ignores an older draft's proposed.thesis rather than carrying it forward", () => {
    const draft = draftIssue({
      proposed: {
        read: 'Test read.',
        thesis: { thesis: 'episode-002', verdict: 'holds', basis: 'b', confidence: 'high', evidenceIds: ['E1'] },
        noCalls: [],
        postureDeltas: '',
        summary: 'summary',
      },
    })
    const signed = computeSignedIssue(draft, { signedOn: '2026-09-20', authorName: 'Jesse Pike' })
    assert.equal(signed.weThink.thesis, null)
  })

  it('refuses to sign an issue with no proposed content', () => {
    const draft = draftIssue({ proposed: null })
    assert.throws(() => computeSignedIssue(draft, { signedOn: '2026-09-20', authorName: 'Jesse Pike' }))
  })
})

describe('tsLiteral / renderIssueModule', () => {
  it('issueExportName follows the issue<id-without-dash> convention', () => {
    assert.equal(issueExportName('2026-w37'), 'issue2026w37')
  })

  it('quotes strings with single quotes by default, double quotes only to avoid escaping an apostrophe', () => {
    assert.equal(tsLiteral('plain text'), "'plain text'")
    assert.equal(tsLiteral("O'Reilly"), '"O\'Reilly"')
    assert.equal(tsLiteral('says "hi"'), "'says \"hi\"'")
  })

  it('drops undefined-valued keys, matching JSON.stringify', () => {
    const rendered = tsLiteral({ a: 1, b: undefined, c: 'x' })
    assert.ok(!rendered.includes('b:'))
    assert.ok(rendered.includes('a: 1'))
    assert.ok(rendered.includes("c: 'x'"))
  })

  it('serializes a signed issue to a TS module that re-imports to a deep-equal object', async () => {
    const draft = draftIssue()
    const signed = computeSignedIssue(draft, { signedOn: '2026-09-20', authorName: 'Jesse Pike' })
    const source = renderIssueModule(signed, 'Jesse Pike')

    assert.match(source, /^import type \{ Issue \} from '\.\.\/types'$/m)
    assert.match(source, /export const issue2026w37: Issue = /)

    const dir = mkdtempSync(join(tmpdir(), 'sign-issue-test-'))
    try {
      // The rendered module's `import type { Issue } from '../types'` is
      // type-only and erased at transpile time, but write a stand-in file
      // beside where a real issue module resolves it, so this test proves
      // the relative import path is well-formed even if a future loader
      // stops erasing type-only imports before resolving them.
      writeFileSync(join(dir, 'types.ts'), 'export type Issue = unknown\n')
      const issuesDir = join(dir, 'issues')
      mkdirSync(issuesDir)
      const modulePath = join(issuesDir, `${signed.id}.ts`)
      writeFileSync(modulePath, source)

      const imported = (await import(pathToFileURL(modulePath).href)) as Record<string, unknown>
      assert.deepEqual(imported.issue2026w37, signed)
    } finally {
      rmSync(dir, { recursive: true, force: true })
    }
  })
})
