import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { describe, it } from 'node:test'
import {
  buildFilingIndexUrl,
  buildQuarterSeries,
  buildSupplierRecord,
  computeYoy,
  daysBetween,
  expectedFiscalQuarter,
  findPriorYearQuarter,
  isAnnualDuration,
  isQuarterlyDuration,
  selectRevenueFacts,
  type CompanyFacts,
  type QuarterFact,
  type XbrlFact,
} from '../src/data/edgarLogic.ts'

// No network anywhere in this file. The one integration-shaped test reads a
// saved companyfacts fixture off disk (tests/fixtures/edgar-companyfacts-fixture.json)
// standing in for what SEC EDGAR's companyfacts API returns for one filer —
// same pattern as tests/dist-fixtures.test.ts. Everything else exercises
// the pure functions directly with hand-built facts, which is the same
// "no fixture file needed for every case" approach dist-fixtures.test.ts
// uses for its own hand-built Issue objects.

const fixturePath = join(dirname(fileURLToPath(import.meta.url)), 'fixtures/edgar-companyfacts-fixture.json')
const fixtureCompanyFacts: CompanyFacts = JSON.parse(readFileSync(fixturePath, 'utf8'))

function fact(overrides: Partial<XbrlFact> & Pick<XbrlFact, 'end' | 'val'>): XbrlFact {
  return {
    start: undefined,
    accn: '0000000001-26-000001',
    fy: 2026,
    fp: undefined,
    form: '10-Q',
    filed: '2026-01-01',
    ...overrides,
  }
}

describe('daysBetween / duration classification', () => {
  it('counts calendar days between two ISO dates', () => {
    assert.equal(daysBetween('2026-01-01', '2026-03-31'), 89)
    assert.equal(daysBetween('2026-01-01', '2027-01-01'), 365)
  })

  it('treats 80-100 days as quarterly and 340-386 as annual', () => {
    assert.equal(isQuarterlyDuration(89), true)
    assert.equal(isQuarterlyDuration(79), false)
    assert.equal(isQuarterlyDuration(101), false)
    assert.equal(isAnnualDuration(365), true)
    assert.equal(isAnnualDuration(180), false)
  })
})

describe('buildFilingIndexUrl', () => {
  it('builds the sec.gov Archives index URL for an accession', () => {
    assert.equal(
      buildFilingIndexUrl(1535527, '0001535527-26-000123'),
      'https://www.sec.gov/Archives/edgar/data/1535527/000153552726000123/0001535527-26-000123-index.htm',
    )
  })
})

describe('selectRevenueFacts', () => {
  it('picks the first concept in priority order that has 10-Q/10-K USD facts', () => {
    const selected = selectRevenueFacts(fixtureCompanyFacts, [
      'Revenues',
      'RevenueFromContractWithCustomerExcludingAssessedTax',
    ])
    assert.ok(selected)
    assert.equal(selected.concept, 'RevenueFromContractWithCustomerExcludingAssessedTax')
    assert.equal(selected.facts.length, 9)
  })

  it('returns null when none of the candidate concepts exist', () => {
    const selected = selectRevenueFacts(fixtureCompanyFacts, ['Revenues', 'SalesRevenueNet'])
    assert.equal(selected, null)
  })
})

describe('buildQuarterSeries — Q4 derivation and restatement de-dup', () => {
  const selected = selectRevenueFacts(fixtureCompanyFacts, [
    'RevenueFromContractWithCustomerExcludingAssessedTax',
  ])
  assert.ok(selected)
  const { quarters, notes } = buildQuarterSeries(selected.facts, 9999999)

  it('extracts 8 quarters: 3 reported + 1 derived Q4, for each of two fiscal years', () => {
    assert.equal(quarters.length, 8)
    assert.equal(notes.length, 0)
  })

  it('derives Q4 2024 as the annual total minus the three reported quarters', () => {
    const q4 = quarters.find((q) => q.periodEnd === '2024-12-31')
    assert.ok(q4)
    assert.equal(q4.value, 130000000) // 460M - (100M + 110M + 120M)
    assert.equal(q4.derived, true)
    assert.equal(q4.periodStart, '2024-10-01')
    assert.equal(q4.fiscalQuarter, 'Q4')
  })

  it('derives Q4 2025 the same way', () => {
    const q4 = quarters.find((q) => q.periodEnd === '2025-12-31')
    assert.ok(q4)
    assert.equal(q4.value, 134000000) // 500M - (115M + 121M + 130M)
    assert.equal(q4.derived, true)
  })

  it('de-dupes the restated Q1 2025 figure by keeping the later-filed value', () => {
    const q1_2025 = quarters.find((q) => q.periodEnd === '2025-03-31')
    assert.ok(q1_2025)
    assert.equal(q1_2025.value, 115000000) // not the original 110M
    assert.equal(q1_2025.filedDate, '2025-07-25')
    assert.equal(q1_2025.derived, false)
  })

  it('leaves reported quarters undisturbed', () => {
    const q2_2024 = quarters.find((q) => q.periodEnd === '2024-06-30')
    assert.ok(q2_2024)
    assert.equal(q2_2024.value, 110000000)
    assert.equal(q2_2024.derived, false)
    assert.equal(q2_2024.sourceUrl, buildFilingIndexUrl(9999999, '0000000001-24-000020'))
  })
})

describe('findPriorYearQuarter / computeYoy', () => {
  const selected = selectRevenueFacts(fixtureCompanyFacts, [
    'RevenueFromContractWithCustomerExcludingAssessedTax',
  ])
  assert.ok(selected)
  const { quarters } = buildQuarterSeries(selected.facts, 9999999)

  it('matches a quarter to the same fiscal quarter one year earlier', () => {
    const q3_2025 = quarters.find((q) => q.periodEnd === '2025-09-30')
    assert.ok(q3_2025)
    const priorYear = findPriorYearQuarter(q3_2025, quarters)
    assert.ok(priorYear)
    assert.equal(priorYear.periodEnd, '2024-09-30')
  })

  it('computes YoY growth for the latest quarter and flags nothing when the match is clean', () => {
    const latest = quarters[0]
    assert.equal(latest.periodEnd, '2025-12-31')
    const yoy = computeYoy(latest, quarters)
    assert.ok(yoy.priorYearQuarter)
    assert.equal(yoy.priorYearQuarter.periodEnd, '2024-12-31')
    assert.ok(yoy.growth !== null)
    assert.ok(Math.abs(yoy.growth! - 4000000 / 130000000) < 1e-9)
    assert.deepEqual(yoy.flags, [])
  })

  it('computes YoY for the quarter before the latest one too', () => {
    const priorQuarter = quarters[1]
    assert.equal(priorQuarter.periodEnd, '2025-09-30')
    const yoy = computeYoy(priorQuarter, quarters)
    assert.ok(yoy.growth !== null)
    assert.ok(Math.abs(yoy.growth! - 10000000 / 120000000) < 1e-9)
    assert.deepEqual(yoy.flags, [])
  })

  it('flags a quarter with no same-quarter-prior-year match instead of throwing', () => {
    const lonely: QuarterFact = {
      periodStart: '2026-01-01',
      periodEnd: '2026-03-31',
      value: 999,
      form: '10-Q',
      accessionNumber: '0000000001-26-000099',
      filedDate: '2026-04-20',
      sourceUrl: 'https://example.test/lonely',
      derived: false,
      fiscalYear: 2026,
      fiscalQuarter: 'Q1',
    }
    const yoy = computeYoy(lonely, [lonely])
    assert.equal(yoy.priorYearQuarter, null)
    assert.equal(yoy.growth, null)
    assert.ok(yoy.flags.includes('no-prior-year-match'))
  })

  it('flags growth beyond the +-80% sane band without dropping the figure', () => {
    const base = fact({ start: '2024-01-01', end: '2024-03-31', val: 10000000, fp: 'Q1', form: '10-Q' })
    const spike = fact({ start: '2025-01-01', end: '2025-03-31', val: 30000000, fp: 'Q1', form: '10-Q' })
    const { quarters } = buildQuarterSeries([base, spike], 1)
    const latest = quarters[0]
    const yoy = computeYoy(latest, quarters)
    assert.equal(yoy.growth, 2) // +200%
    assert.ok(yoy.flags.includes('growth-out-of-band'))
    assert.equal(yoy.quarter.value, 30000000) // figure kept, not dropped
  })
})

describe('buildSupplierRecord', () => {
  it('builds the full record end to end from the fixture', () => {
    const record = buildSupplierRecord('fixture', 'FixtureCorp', '0009999999', fixtureCompanyFacts, [
      'Revenues',
      'RevenueFromContractWithCustomerExcludingAssessedTax',
    ])
    assert.equal(record.id, 'fixture')
    assert.equal(record.concept, 'RevenueFromContractWithCustomerExcludingAssessedTax')
    assert.equal(record.quarters.length, 8)
    assert.ok(record.latest)
    assert.equal(record.latest.quarter.periodEnd, '2025-12-31')
    assert.ok(record.prior)
    assert.equal(record.prior.quarter.periodEnd, '2025-09-30')
  })

  it('records a failure (via throw) rather than silently producing an empty record when no concept matches', () => {
    assert.throws(
      () => buildSupplierRecord('fixture', 'FixtureCorp', '0009999999', fixtureCompanyFacts, ['Revenues']),
      /no usable revenue concept found/,
    )
  })
})

describe('expectedFiscalQuarter', () => {
  // AUTO-001 fix pass (2026-09-26), item 2: regression cases from the two
  // blind scores — SailPoint and Okta (both FYE 0131) had their Q2 FY2027
  // periodEnd (2026-07-31) hand-labelled "Q4 FY2027", and their Q1 FY2027
  // periodEnd (2026-04-30) hand-labelled "Q3 FY2027".
  it('places a 0131-FYE filer\'s 2026-07-31 period in Q2 FY2027, not Q4', () => {
    assert.deepEqual(expectedFiscalQuarter('2026-07-31', '0131'), { quarter: 2, fiscalYear: 2027 })
  })

  it('places a 0131-FYE filer\'s 2026-04-30 period in Q1 FY2027, not Q3', () => {
    assert.deepEqual(expectedFiscalQuarter('2026-04-30', '0131'), { quarter: 1, fiscalYear: 2027 })
  })

  it('places a 0731-FYE filer\'s 2026-07-31 period in Q4 FY2026 (fiscal year end itself)', () => {
    assert.deepEqual(expectedFiscalQuarter('2026-07-31', '0731'), { quarter: 4, fiscalYear: 2026 })
  })

  it('places a 1231-FYE (calendar-year) filer\'s 2026-06-30 period in Q2 FY2026', () => {
    assert.deepEqual(expectedFiscalQuarter('2026-06-30', '1231'), { quarter: 2, fiscalYear: 2026 })
  })

  it('places a 0131-FYE filer\'s own fiscal year end (2026-01-31) in Q4 FY2026', () => {
    assert.deepEqual(expectedFiscalQuarter('2026-01-31', '0131'), { quarter: 4, fiscalYear: 2026 })
  })
})
