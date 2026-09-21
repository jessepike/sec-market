import assert from 'node:assert/strict'
import { describe, it } from 'node:test'
import { renderToString } from 'react-dom/server'
import { createElement } from 'react'
import {
  claimId,
  collectJudgedClaimRefs,
  effectiveDate,
  effectiveJudgment,
  isStaleAsOf,
  newestPublishedSignedOn,
  unknownClaimIds,
  validateReconfirmations,
} from '../src/data/reconfirmationHelpers.ts'
import { buildStaleReportJson } from '../src/data/staleReport.ts'
import { JudgedStamp, JudgedStampSpaced, JudgedStampStacked } from '../src/components/JudgedStamp.tsx'
import { computeReconfirmations } from '../scripts/reconfirmLogic.ts'
import { renderReconfirmationsModule } from '../scripts/reconfirmRender.ts'
import type { EvidenceRecord, Hypothesis, Issue, PressureRow, Reconfirmation, SecurityDomain } from '../src/data/types.ts'

function domain(overrides: Partial<SecurityDomain> & Pick<SecurityDomain, 'id' | 'asOf'>): SecurityDomain {
  return {
    name: 'Fixture Domain',
    coverage: 'PASS_WITH_LIMITATION',
    posture: 'INVESTIGATE',
    tag: 'WATCH',
    horizon: 'This quarter',
    momentum: 'stable-positive',
    evidenceStrength: 'medium',
    print: '',
    why: 'A fixture reason.',
    summary: '',
    watchItems: [],
    supportingEvidenceIds: [],
    counterEvidenceIds: [],
    ...overrides,
  }
}

function hypothesis(overrides: Partial<Hypothesis> & Pick<Hypothesis, 'id'>): Hypothesis {
  return {
    claim: 'A fixture claim',
    state: 'TRACKING',
    note: '',
    firstTest: null,
    evidenceIds: [],
    provenance: { layer: 'judged', judgedOn: '2026-01-01', confidence: 'medium', evidenceIds: [] },
    ...overrides,
  }
}

function pressureRow(overrides: Partial<PressureRow> & Pick<PressureRow, 'id'>): PressureRow {
  return {
    vendors: ['Fixture'],
    position: 'incumbent',
    print: '',
    read: 'A fixture read.',
    provenance: {
      print: { layer: 'tracked', evidenceIds: ['fx-1'], observedOn: '2026-01-01' },
      read: { layer: 'judged', judgedOn: '2026-01-01', confidence: 'medium', evidenceIds: [] },
    },
    ...overrides,
  }
}

function reconfirmation(overrides: Partial<Reconfirmation> & Pick<Reconfirmation, 'claimId'>): Reconfirmation {
  return { reconfirmedOn: '2026-09-01', by: 'Jesse Pike', via: '2026-w36', ...overrides }
}

describe('claimId / collectJudgedClaimRefs', () => {
  it('prefixes the claim id with its kind', () => {
    assert.equal(claimId('domain', 'network-sase'), 'domain:network-sase')
    assert.equal(claimId('hypothesis', 'hyp-infra-lag'), 'hypothesis:hyp-infra-lag')
    assert.equal(claimId('platform-pressure', 'a--b'), 'platform-pressure:a--b')
  })

  it('collects domains, hypotheses, and only judged pressure rows', () => {
    const refs = collectJudgedClaimRefs({
      domains: [domain({ id: 'd1', asOf: '2026-08-01' })],
      hypotheses: [hypothesis({ id: 'h1' })],
      pressureRows: [
        pressureRow({ id: 'row-judged' }),
        pressureRow({
          id: 'row-tracked',
          provenance: {
            print: { layer: 'tracked', evidenceIds: ['fx-1'], observedOn: '2026-01-01' },
            read: { layer: 'tracked', evidenceIds: ['fx-1'], observedOn: '2026-01-01' },
          },
        }),
      ],
    })
    assert.deepEqual(
      refs.map((r) => r.claimId),
      ['domain:d1', 'hypothesis:h1', 'platform-pressure:row-judged'],
    )
  })
})

describe('effectiveJudgment / effectiveDate', () => {
  it('returns the original judgment when there is no reconfirmation', () => {
    const effective = effectiveJudgment('domain:d1', '2026-08-01', [])
    assert.equal(effective.reconfirmedOn, null)
    assert.equal(effectiveDate(effective), '2026-08-01')
  })

  it('returns the newest reconfirmation for that claim, ignoring others', () => {
    const list: Reconfirmation[] = [
      reconfirmation({ claimId: 'domain:other', reconfirmedOn: '2026-09-15' }),
      reconfirmation({ claimId: 'domain:d1', reconfirmedOn: '2026-08-20' }),
      reconfirmation({ claimId: 'domain:d1', reconfirmedOn: '2026-09-05' }),
    ]
    const effective = effectiveJudgment('domain:d1', '2026-08-01', list)
    assert.equal(effective.reconfirmedOn, '2026-09-05')
    assert.equal(effective.reconfirmedBy, 'Jesse Pike')
    assert.equal(effective.reconfirmedVia, '2026-w36')
    assert.equal(effectiveDate(effective), '2026-09-05')
  })
})

describe('isStaleAsOf', () => {
  it('is false at exactly the threshold (boundary is exclusive)', () => {
    assert.equal(isStaleAsOf(effectiveJudgment('domain:d1', '2026-08-07', []), '2026-09-21', 45), false)
  })

  it('is true one day past the threshold', () => {
    assert.equal(isStaleAsOf(effectiveJudgment('domain:d1', '2026-08-06', []), '2026-09-21', 45), true)
  })

  it('uses the reconfirmed date, not the original, once reconfirmed', () => {
    const list = [reconfirmation({ claimId: 'domain:d1', reconfirmedOn: '2026-09-01' })]
    assert.equal(isStaleAsOf(effectiveJudgment('domain:d1', '2026-01-01', list), '2026-09-21', 45), false)
  })
})

describe('unknownClaimIds', () => {
  const claims = collectJudgedClaimRefs({
    domains: [domain({ id: 'd1', asOf: '2026-08-01' })],
    hypotheses: [],
    pressureRows: [],
  })

  it('is empty when every id names a real claim', () => {
    assert.deepEqual(unknownClaimIds(['domain:d1'], claims), [])
  })

  it('names every id that does not', () => {
    assert.deepEqual(unknownClaimIds(['domain:d1', 'domain:ghost', 'hypothesis:ghost2'], claims), [
      'domain:ghost',
      'hypothesis:ghost2',
    ])
  })
})

describe('validateReconfirmations', () => {
  const claims = collectJudgedClaimRefs({
    domains: [domain({ id: 'd1', asOf: '2026-08-01' })],
    hypotheses: [],
    pressureRows: [],
  })
  const publishedIssueIds = new Set(['2026-w36'])

  it('passes a well-formed entry', () => {
    const violations = validateReconfirmations(
      [reconfirmation({ claimId: 'domain:d1', reconfirmedOn: '2026-09-01' })],
      claims,
      'Jesse Pike',
      publishedIssueIds,
      '2026-09-01',
    )
    assert.deepEqual(violations, [])
  })

  it('flags an unknown claimId', () => {
    const violations = validateReconfirmations(
      [reconfirmation({ claimId: 'domain:ghost' })],
      claims,
      'Jesse Pike',
      publishedIssueIds,
      '2026-09-01',
    )
    assert.equal(violations.length, 1)
    assert.match(violations[0].reason, /no judged claim/)
  })

  it('flags "by" not equal to AUTHOR_NAME', () => {
    const violations = validateReconfirmations(
      [reconfirmation({ claimId: 'domain:d1', by: 'Someone Else' })],
      claims,
      'Jesse Pike',
      publishedIssueIds,
      '2026-09-01',
    )
    assert.ok(violations.some((v) => /AUTHOR_NAME/.test(v.reason)))
  })

  it('flags a reconfirmedOn earlier than the claim\'s own judgedOn', () => {
    const violations = validateReconfirmations(
      [reconfirmation({ claimId: 'domain:d1', reconfirmedOn: '2026-07-01' })],
      claims,
      'Jesse Pike',
      publishedIssueIds,
      '2026-09-01',
    )
    assert.ok(violations.some((v) => /earlier than the claim's judgedOn/.test(v.reason)))
  })

  it('flags a reconfirmedOn more than one day after the newest published signedOn', () => {
    const violations = validateReconfirmations(
      [reconfirmation({ claimId: 'domain:d1', reconfirmedOn: '2026-09-05' })],
      claims,
      'Jesse Pike',
      publishedIssueIds,
      '2026-09-01',
    )
    assert.ok(violations.some((v) => /more than one day after/.test(v.reason)))
  })

  it('allows exactly one day after the newest published signedOn', () => {
    const violations = validateReconfirmations(
      [reconfirmation({ claimId: 'domain:d1', reconfirmedOn: '2026-09-02' })],
      claims,
      'Jesse Pike',
      publishedIssueIds,
      '2026-09-01',
    )
    assert.deepEqual(violations, [])
  })

  it('flags a via that does not name a published issue', () => {
    const violations = validateReconfirmations(
      [reconfirmation({ claimId: 'domain:d1', via: '2026-w99' })],
      claims,
      'Jesse Pike',
      publishedIssueIds,
      '2026-09-01',
    )
    assert.ok(violations.some((v) => /is not a published issue id/.test(v.reason)))
  })

  it('flags every entry when no published issue exists yet', () => {
    const violations = validateReconfirmations(
      [reconfirmation({ claimId: 'domain:d1' })],
      claims,
      'Jesse Pike',
      new Set(),
      null,
    )
    assert.ok(violations.some((v) => /no published issue exists yet/.test(v.reason)))
  })
})

describe('newestPublishedSignedOn', () => {
  function issue(overrides: Partial<Issue> & Pick<Issue, 'id'>): Issue {
    return {
      weekEnding: '2026-01-04',
      windowStart: '2026-01-01',
      published: null,
      status: 'draft',
      read: '',
      sections: [
        { lane: 'formation', items: [] },
        { lane: 'absorption', items: [] },
        { lane: 'prints', items: [] },
        { lane: 'capital', items: [] },
      ],
      weThink: { summary: '', postureDeltas: [], thesis: null, noCalls: [], signedBy: null, signedOn: null },
      proposed: null,
      sources: { readable: 0, unreadable: [] },
      ...overrides,
    }
  }

  it('is null with no published issues', () => {
    assert.equal(newestPublishedSignedOn([issue({ id: '2026-w36' })]), null)
  })

  it('picks the latest signedOn among published issues', () => {
    const issues = [
      issue({
        id: '2026-w36',
        status: 'published',
        weThink: { summary: 'x', postureDeltas: [], thesis: null, noCalls: [], signedBy: 'Jesse Pike', signedOn: '2026-09-06' },
      }),
      issue({
        id: '2026-w37',
        status: 'published',
        weThink: { summary: 'x', postureDeltas: [], thesis: null, noCalls: [], signedBy: 'Jesse Pike', signedOn: '2026-09-13' },
      }),
      issue({ id: '2026-w38' }),
    ]
    assert.equal(newestPublishedSignedOn(issues), '2026-09-13')
  })
})

describe('computeReconfirmations', () => {
  const base = {
    reconfirm: true,
    signedOn: '2026-09-21',
    issueId: '2026-w38',
    authorName: 'Jesse Pike',
    challengedClaimIds: [] as string[],
    staleClaimIds: [] as string[],
    existingReconfirmations: [] as Reconfirmation[],
  }

  it('reconfirms a stale, unchallenged claim', () => {
    const result = computeReconfirmations({ ...base, staleClaimIds: ['domain:d1'] })
    assert.equal(result.added.length, 1)
    assert.deepEqual(result.added[0], { claimId: 'domain:d1', reconfirmedOn: '2026-09-21', by: 'Jesse Pike', via: '2026-w38' })
    assert.deepEqual(result.challengedLeftStale, [])
    assert.deepEqual(result.reconfirmations, result.added)
  })

  it('leaves a stale, challenged claim un-reconfirmed', () => {
    const result = computeReconfirmations({
      ...base,
      staleClaimIds: ['domain:d1'],
      challengedClaimIds: ['domain:d1'],
    })
    assert.deepEqual(result.added, [])
    assert.deepEqual(result.challengedLeftStale, ['domain:d1'])
  })

  it('does not touch a fresh (not-stale) claim, challenged or not', () => {
    const result = computeReconfirmations({ ...base, staleClaimIds: [], challengedClaimIds: ['domain:d1'] })
    assert.deepEqual(result.added, [])
    assert.deepEqual(result.challengedLeftStale, [])
  })

  it('does nothing at all when reconfirm is false, even with stale unchallenged claims', () => {
    const result = computeReconfirmations({ ...base, reconfirm: false, staleClaimIds: ['domain:d1'] })
    assert.deepEqual(result.added, [])
    assert.deepEqual(result.challengedLeftStale, [])
    assert.deepEqual(result.reconfirmations, base.existingReconfirmations)
  })

  it('never re-adds a claim already reconfirmed recently (it is simply absent from staleClaimIds)', () => {
    // staleClaimIds is computed upstream via effective date, so a recently
    // reconfirmed claim is never passed in here at all — this test proves
    // computeReconfirmations does not need its own "already reconfirmed"
    // special case to get the right answer.
    const existing = [reconfirmation({ claimId: 'domain:d1', reconfirmedOn: '2026-09-01', via: '2026-w37' })]
    const result = computeReconfirmations({ ...base, staleClaimIds: [], existingReconfirmations: existing })
    assert.deepEqual(result.added, [])
    assert.deepEqual(result.reconfirmations, existing)
  })

  it('is additive: existing entries are carried forward untouched', () => {
    const existing = [reconfirmation({ claimId: 'domain:other', reconfirmedOn: '2026-08-01', via: '2026-w30' })]
    const result = computeReconfirmations({ ...base, staleClaimIds: ['domain:d1'], existingReconfirmations: existing })
    assert.deepEqual(result.reconfirmations, [...existing, ...result.added])
  })
})

describe('buildStaleReportJson integration: a recent reconfirmation removes a claim from staleClaimIds', () => {
  const emptyInputs = {
    domains: [] as SecurityDomain[],
    hypotheses: [] as Hypothesis[],
    pressureRows: [] as PressureRow[],
    prints: [],
    evidenceById: {} as Record<string, EvidenceRecord>,
  }

  it('a long-ago-judged, recently-reconfirmed domain is not stale', () => {
    const json = buildStaleReportJson('2026-09-21', {
      ...emptyInputs,
      domains: [domain({ id: 'd1', asOf: '2026-01-01' })],
      reconfirmations: [reconfirmation({ claimId: 'domain:d1', reconfirmedOn: '2026-09-10' })],
    })
    assert.deepEqual(json.staleClaimIds, [])
  })

  it('the same domain with no reconfirmation is stale', () => {
    const json = buildStaleReportJson('2026-09-21', {
      ...emptyInputs,
      domains: [domain({ id: 'd1', asOf: '2026-01-01' })],
    })
    assert.deepEqual(json.staleClaimIds, ['domain:d1'])
  })
})

describe('renderReconfirmationsModule', () => {
  it('round-trips through a real module to the exact original array', async () => {
    const { mkdtempSync, writeFileSync, rmSync } = await import('node:fs')
    const { tmpdir } = await import('node:os')
    const { join } = await import('node:path')
    const { pathToFileURL } = await import('node:url')

    const list: Reconfirmation[] = [reconfirmation({ claimId: 'domain:d1' })]
    const source = renderReconfirmationsModule(list)
    assert.match(source, /export const reconfirmations: Reconfirmation\[\] = /)

    const dir = mkdtempSync(join(tmpdir(), 'reconfirm-render-test-'))
    try {
      writeFileSync(join(dir, 'types.ts'), 'export type Reconfirmation = unknown\n')
      const modulePath = join(dir, 'reconfirmations.ts')
      writeFileSync(modulePath, source)
      const imported = (await import(pathToFileURL(modulePath).href)) as { reconfirmations: unknown }
      assert.deepEqual(imported.reconfirmations, list)
    } finally {
      rmSync(dir, { recursive: true, force: true })
    }
  })

  it('renders an empty list as []', () => {
    const source = renderReconfirmationsModule([])
    assert.match(source, /export const reconfirmations: Reconfirmation\[\] = \[\]/)
  })
})

describe('JudgedStamp', () => {
  // The real page is server-rendered with `renderToString` (src/entry-server.tsx), which
  // inserts `<!-- -->` hydration boundary comments between adjacent children that both
  // render as plain text — `renderToStaticMarkup` never does this, so it cannot prove
  // byte-identical output against what actually ships. `renderToString` under this test
  // runner's own esbuild-based JSX transform was checked, exact byte for byte, against the
  // real `vite build` + prerender output for all three shapes (T7-4 evidence step, diffing
  // `dist/index.html` between `preview` and this branch down to zero lines); it agreed on
  // every one, so the strings below are the real ground truth, not a guess from reading the
  // JSX. If a future change to the toolchain makes this test disagree with a real dist
  // build again, trust the dist build and update this test, not the other way round.
  it('renders byte-identical markup to the pre-reconfirmation form when there is no reconfirmation (market-picture shape)', () => {
    const markup = renderToString(createElement(JudgedStamp, { judgedOn: '2026-08-16', reconfirmedOn: null }))
    assert.equal(
      markup,
      '<p class="stamp-label">JUDGED <time dateTime="2026-08-16">16 Aug 2026</time> · <!-- -->Jesse Pike</p>',
    )
  })

  it('renders byte-identical markup to the pre-reconfirmation form when there is no reconfirmation (domain-stance shape)', () => {
    const markup = renderToString(
      createElement(JudgedStampSpaced, { judgedOn: '2026-08-16', reconfirmedOn: null }),
    )
    assert.equal(
      markup,
      '<p class="stamp-label">JUDGED <time dateTime="2026-08-16">16 Aug 2026</time> ·<!-- --> <!-- -->Jesse Pike</p>',
    )
  })

  it('renders byte-identical markup to the pre-reconfirmation form when there is no reconfirmation (hypothesis / Platform-pressure shape)', () => {
    const markup = renderToString(
      createElement(JudgedStampStacked, { judgedOn: '2026-08-16', reconfirmedOn: null }),
    )
    assert.equal(
      markup,
      '<p class="stamp-label">JUDGED<!-- --> <time dateTime="2026-08-16">16 Aug 2026</time> <!-- -->· <!-- -->Jesse Pike</p>',
    )
  })

  it('shows both dates, honestly, when reconfirmed (fixture only — no real data touched)', () => {
    for (const Component of [JudgedStamp, JudgedStampSpaced, JudgedStampStacked]) {
      const markup = renderToString(
        createElement(Component, { judgedOn: '2026-08-16', reconfirmedOn: '2026-11-02' }),
      )
      assert.match(markup, /JUDGED/)
      assert.match(markup, /16 Aug 2026/)
      assert.match(markup, /RECONFIRMED/)
      assert.match(markup, /2 Nov 2026/)
      assert.match(markup, /Jesse Pike/)
      assert.match(markup, /<time dateTime="2026-08-16">/)
      assert.match(markup, /<time dateTime="2026-11-02">/)
    }
  })

  it('wraps each reconfirmed segment in .stamp-segment (nowrap) so a phone width breaks between segments, not inside a name or date', () => {
    for (const Component of [JudgedStamp, JudgedStampSpaced, JudgedStampStacked]) {
      const markup = renderToString(
        createElement(Component, { judgedOn: '2026-08-16', reconfirmedOn: '2026-11-02' }),
      )
      const segments = [...markup.matchAll(/<span class="stamp-segment">(.*?)<\/span>/g)].map((m) => m[1])
      assert.equal(segments.length, 3)
      assert.match(segments[0], /^JUDGED/)
      assert.match(segments[1], /^RECONFIRMED/)
      assert.equal(segments[2], 'Jesse Pike')
    }
  })

  it('never wraps a segment span around the no-reconfirmation form', () => {
    for (const Component of [JudgedStamp, JudgedStampSpaced, JudgedStampStacked]) {
      const markup = renderToString(createElement(Component, { judgedOn: '2026-08-16', reconfirmedOn: null }))
      assert.doesNotMatch(markup, /stamp-segment/)
    }
  })
})
