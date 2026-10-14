import assert from 'node:assert/strict'
import { describe, it } from 'node:test'
import { buildStaleReport } from '../src/data/staleReport.ts'
import type { EvidenceRecord, Hypothesis, PressureRow, SecurityDomain, VendorPrint } from '../src/data/types.ts'

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

function print(overrides: Partial<VendorPrint> & Pick<VendorPrint, 'id'>): VendorPrint {
  return {
    group: 'SecOps',
    name: 'Fixture Corp',
    period: 'JUN ’26',
    value: '+20%',
    metric: 'revenue',
    note: '',
    tone: 'up',
    evidenceIds: [],
    ...overrides,
  }
}

const emptyInputs = { domains: [], hypotheses: [], pressureRows: [], prints: [], evidenceById: {} as Record<string, EvidenceRecord> }

describe('buildStaleReport', () => {
  it('reports no judged claims and no scorecard entries when nothing is old', () => {
    const report = buildStaleReport('2026-09-21', {
      ...emptyInputs,
      domains: [domain({ id: 'd1', asOf: '2026-09-01' })], // 20 days old
      hypotheses: [hypothesis({ id: 'h1', provenance: { layer: 'judged', judgedOn: '2026-09-01', confidence: 'medium', evidenceIds: [] } })],
    })
    assert.match(report, /0 judged claim\(s\)/)
    assert.match(report, /None found\./)
  })

  it('flags a domain stance judged more than 45 days before the as-of date', () => {
    const report = buildStaleReport('2026-09-21', {
      ...emptyInputs,
      domains: [domain({ id: 'd1', asOf: '2026-06-01' })], // > 45 days before 2026-09-21
    })
    assert.match(report, /1 judged claim\(s\)/)
    assert.match(report, /`d1`/)
  })

  it('does not flag a domain stance judged exactly 45 days ago (boundary is exclusive of the threshold)', () => {
    const report = buildStaleReport('2026-09-21', {
      ...emptyInputs,
      domains: [domain({ id: 'd1', asOf: '2026-08-07' })], // exactly 45 days before 2026-09-21
    })
    assert.match(report, /0 judged claim\(s\)/)
  })

  it('flags a stale hypothesis and a stale platform-pressure row, oldest first', () => {
    const report = buildStaleReport('2026-09-21', {
      ...emptyInputs,
      hypotheses: [
        hypothesis({ id: 'h-newer', provenance: { layer: 'judged', judgedOn: '2026-07-01', confidence: 'medium', evidenceIds: [] } }),
        hypothesis({ id: 'h-older', provenance: { layer: 'judged', judgedOn: '2026-05-01', confidence: 'medium', evidenceIds: [] } }),
      ],
      pressureRows: [pressureRow({ id: 'row-1', provenance: { print: { layer: 'tracked', evidenceIds: ['fx-1'], observedOn: '2026-01-01' }, read: { layer: 'judged', judgedOn: '2026-06-01', confidence: 'medium', evidenceIds: [] } } })],
    })
    const olderIndex = report.indexOf('`h-older`')
    const newerIndex = report.indexOf('`h-newer`')
    const rowIndex = report.indexOf('`row-1`')
    assert.ok(olderIndex !== -1 && newerIndex !== -1 && rowIndex !== -1)
    assert.ok(olderIndex < newerIndex, 'the older hypothesis should be listed first (oldest first)')
  })

  it('flags a scorecard print whose period ended more than 150 days before the as-of date', () => {
    const report = buildStaleReport('2026-09-21', {
      ...emptyInputs,
      prints: [print({ id: 'p-stale', period: 'JAN ’26' })], // ends 2026-01-31, well over 150 days before Sep 21
    })
    assert.match(report, /1 scorecard print\(s\)/)
    assert.match(report, /`p-stale`/)
  })

  it('does not flag a recent scorecard print', () => {
    const report = buildStaleReport('2026-09-21', {
      ...emptyInputs,
      prints: [print({ id: 'p-fresh', period: 'AUG ’26' })], // ends 2026-08-31, 21 days before as-of
    })
    assert.match(report, /0 scorecard print\(s\)/)
  })

  it('lists an unparseable period separately, never dropping it', () => {
    const report = buildStaleReport('2026-09-21', {
      ...emptyInputs,
      prints: [print({ id: 'p-mystery', period: 'Closed', evidenceIds: [] })],
    })
    assert.match(report, /1 print\(s\) with a period not understood/)
    assert.match(report, /Period not understood/)
    assert.match(report, /`p-mystery`/)
  })
})
