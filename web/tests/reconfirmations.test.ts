import assert from 'node:assert/strict'
import { describe, it } from 'node:test'
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
import type { Hypothesis, Issue, PressureRow, Reconfirmation, SecurityDomain } from '../src/data/types.ts'

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
