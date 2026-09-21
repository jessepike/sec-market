import assert from 'node:assert/strict'
import { describe, it } from 'node:test'
import { checkPrintCompany, checkPrintMetric, checkPrintValueAndUnits, verifyPrint } from '../src/data/printChecks.ts'
import { checkPrintPeriod, classifyCardPeriod, classifyEvidencePeriod, derivePeriodEndDate } from '../src/data/printPeriod.ts'
import type { EvidenceRecord, VendorPrint } from '../src/data/types.ts'

function evidence(overrides: Partial<EvidenceRecord> & Pick<EvidenceRecord, 'id'>): EvidenceRecord {
  return {
    title: 'Fixture Corp Results',
    organization: 'Fixture Corp',
    publicationDate: '2026-06-15',
    economicPeriod: 'Quarter ended 2026-06-30',
    canonicalUrl: 'https://example.com',
    excerpt: 'Revenue grew 20%.',
    sourceClass: 'IR',
    interpretation: '',
    limitations: '',
    conflictingEvidenceIds: [],
    artifactLabel: 'fixture',
    tags: [],
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
    evidenceIds: ['fx-1'],
    ...overrides,
  }
}

describe('classifyCardPeriod', () => {
  it('parses a month-year tag with a curly apostrophe', () => {
    assert.deepEqual(classifyCardPeriod('JUN ’26'), { kind: 'month-year', month: 6, year: 2026 })
  })

  it('parses a month-year tag with a straight apostrophe', () => {
    assert.deepEqual(classifyCardPeriod("APR '25"), { kind: 'month-year', month: 4, year: 2025 })
  })

  it('parses a bare fiscal year', () => {
    assert.deepEqual(classifyCardPeriod('FY26'), { kind: 'fiscal-year', year: 2026 })
  })

  it('parses a bare calendar year', () => {
    assert.deepEqual(classifyCardPeriod('2025'), { kind: 'calendar-year', year: 2025 })
  })

  it('parses an explicit fiscal quarter', () => {
    assert.deepEqual(classifyCardPeriod('Q3 FY26'), { kind: 'quarter', year: 2026 })
  })

  it('treats "Closed" and "No series" as non-comparable', () => {
    assert.equal(classifyCardPeriod('Closed').kind, 'non-comparable')
    assert.equal(classifyCardPeriod('No series').kind, 'non-comparable')
  })

  it('falls back to unknown for text it does not recognise', () => {
    assert.equal(classifyCardPeriod('sometime soon').kind, 'unknown')
  })
})

describe('classifyEvidencePeriod', () => {
  it('reads a bare quarter', () => {
    const info = classifyEvidencePeriod('Quarter ended 2026-06-30')
    assert.equal(info.kind, 'quarter')
    assert.equal(info.endDate, '2026-06-30')
  })

  it('reads a combined fiscal-year-and-quarter record', () => {
    const info = classifyEvidencePeriod('FY2026 and quarter ended 2026-07-25')
    assert.equal(info.kind, 'combined')
    assert.ok(info.years.includes(2026), `expected 2026 among years, got ${JSON.stringify(info.years)}`)
  })

  it('reads a fiscal year', () => {
    const info = classifyEvidencePeriod('Fiscal year ended 2026-01-31')
    assert.equal(info.kind, 'fiscal-year')
    assert.equal(info.endDate, '2026-01-31')
  })

  it('reads a point-in-time funding event', () => {
    assert.equal(classifyEvidencePeriod('Series G close').kind, 'point')
    assert.equal(classifyEvidencePeriod('Transaction announcement').kind, 'point')
  })
})

describe('checkPrintPeriod — the deliberately wrong case', () => {
  it('fails a card labelling a full fiscal year when the only evidence is a single quarter', () => {
    const result = checkPrintPeriod('FY26', [
      evidence({ id: 'fx-1', economicPeriod: 'Quarter ended 2026-01-31' }),
    ])
    assert.equal(result.status, 'fail')
    assert.match(result.reason, /single quarter/)
  })

  it('mirrors the real print-crwd-cloud defect exactly', () => {
    const result = checkPrintPeriod('FY26', [
      evidence({
        id: 'C13',
        title: 'CrowdStrike Q4 FY2026 Results — Falcon Cloud segment',
        economicPeriod: 'Quarter ended 2026-01-31',
        excerpt: 'For the first time, our cloud business exceeded $800 million in ending ARR… grew more than 35% year over year.',
      }),
    ])
    assert.equal(result.status, 'fail')
  })

  it('passes a month-year card against a matching quarter', () => {
    const result = checkPrintPeriod('JUN ’26', [evidence({ id: 'fx-1', economicPeriod: 'Quarter ended 2026-06-30' })])
    assert.equal(result.status, 'pass')
  })

  it('passes a fiscal-year card against a matching fiscal-year record', () => {
    const result = checkPrintPeriod('FY26', [evidence({ id: 'fx-1', economicPeriod: 'Fiscal year ended 2026-01-31' })])
    assert.equal(result.status, 'pass')
  })

  it('passes a bare year against a point-in-time record dated that year', () => {
    const result = checkPrintPeriod('2023', [
      evidence({ id: 'fx-1', economicPeriod: 'Last disclosed raise', publicationDate: '2023-03-10' }),
    ])
    assert.equal(result.status, 'pass')
  })

  it('passes a month-year card via a later date named only in the excerpt text', () => {
    // Mirrors print-veza / evidence C23: publicationDate is the announcement,
    // the card's period names the later close date, which only the excerpt states.
    const result = checkPrintPeriod('MAR ’26', [
      evidence({
        id: 'fx-1',
        economicPeriod: 'Acquisition announcement',
        publicationDate: '2025-12-02',
        excerpt: 'Announced intent to acquire Fixture Target… The acquisition closed on March 2, 2026.',
      }),
    ])
    assert.equal(result.status, 'pass')
  })

  it('is not-checkable for a non-comparable card period', () => {
    assert.equal(checkPrintPeriod('Closed', [evidence({ id: 'fx-1' })]).status, 'not-checkable')
  })

  it('fails a bare year that matches nothing in the cited evidence', () => {
    const result = checkPrintPeriod('2019', [evidence({ id: 'fx-1', economicPeriod: 'Calendar year 2025', publicationDate: '2026-01-01' })])
    assert.equal(result.status, 'fail')
  })
})

describe('derivePeriodEndDate', () => {
  it('derives the last day of a month-year tag with no evidence needed', () => {
    assert.equal(derivePeriodEndDate('JUN ’26', []), '2026-06-30')
    assert.equal(derivePeriodEndDate('FEB ’24', []), '2024-02-29') // leap year
    assert.equal(derivePeriodEndDate('FEB ’25', []), '2025-02-28')
  })

  it('derives December 31 for a bare year', () => {
    assert.equal(derivePeriodEndDate('2025', []), '2025-12-31')
  })

  it('falls back to the newest cited evidence publicationDate for FY / quarter / non-comparable tags', () => {
    assert.equal(
      derivePeriodEndDate('FY26', [evidence({ id: 'fx-1', publicationDate: '2026-03-01' }), evidence({ id: 'fx-2', publicationDate: '2026-05-01' })]),
      '2026-05-01',
    )
  })

  it('is unparseable when no evidence resolves and the card names no dated period', () => {
    assert.equal(derivePeriodEndDate('Closed', []), null)
  })
})

describe('checkPrintCompany', () => {
  it('matches directly on organization', () => {
    const result = checkPrintCompany(print({ id: 'p1', name: 'Fixture Corp' }), [evidence({ id: 'fx-1' })])
    assert.equal(result.status, 'pass')
  })

  it('falls back to title/excerpt when a small company is bylined under its acquirer', () => {
    const result = checkPrintCompany(print({ id: 'p1', name: 'Veza' }), [
      evidence({ id: 'fx-1', organization: 'ServiceNow', title: 'ServiceNow acquisition of Veza', excerpt: 'ServiceNow announced its intent to acquire Veza.' }),
    ])
    assert.equal(result.status, 'pass')
  })

  it('fails when no cited evidence names the company at all', () => {
    const result = checkPrintCompany(print({ id: 'p1', name: 'Nonexistent Vendor' }), [evidence({ id: 'fx-1', organization: 'Somebody Else', title: 'Unrelated', excerpt: 'Nothing to do with it.' })])
    assert.equal(result.status, 'fail')
  })

  it('passes a multi-part name if any part is corroborated', () => {
    const result = checkPrintCompany(print({ id: 'p1', name: 'Entra / Ping / PE PAM' }), [
      evidence({ id: 'fx-1', organization: 'Ping Identity / BeyondTrust / Delinea' }),
    ])
    assert.equal(result.status, 'pass')
  })
})

describe('checkPrintMetric', () => {
  it('is always not-checkable', () => {
    assert.equal(checkPrintMetric(print({ id: 'p1' })).status, 'not-checkable')
  })
})

describe('checkPrintValueAndUnits — the deliberately absent case', () => {
  it('fails a value that does not appear in any cited evidence', () => {
    const { value } = checkPrintValueAndUnits(print({ id: 'p1', value: '$999M' }), [
      evidence({ id: 'fx-1', excerpt: 'Revenue grew 20% to $50 million.' }),
    ])
    assert.equal(value.status, 'fail')
  })

  it('passes an exact percentage match', () => {
    const { value, units } = checkPrintValueAndUnits(print({ id: 'p1', value: '+52%' }), [
      evidence({ id: 'fx-1', excerpt: 'Product revenue grew 52%.' }),
    ])
    assert.equal(value.status, 'pass')
    assert.equal(units.status, 'pass')
  })

  it('passes a spelled-out billion figure against a compact card value', () => {
    const { value } = checkPrintValueAndUnits(print({ id: 'p1', value: '$12B' }), [
      evidence({ id: 'fx-1', excerpt: 'Latest funding round of $600 million, taking the valuation to $12 billion.' }),
    ])
    assert.equal(value.status, 'pass')
  })

  it('passes a rounded percentage within tolerance (the Arista case)', () => {
    const { value } = checkPrintValueAndUnits(print({ id: 'p1', value: '+38%' }), [
      evidence({ id: 'fx-1', excerpt: 'Revenue rose to $3.036 billion; latest YoY growth 37.7 percent.' }),
    ])
    assert.equal(value.status, 'pass')
    assert.match(value.reason, /tolerance/)
  })

  it('fails units when the same number appears under a different unit', () => {
    const { units } = checkPrintValueAndUnits(print({ id: 'p1', value: '$300M' }), [
      evidence({ id: 'fx-1', excerpt: 'We now have over 300 customers.' }),
    ])
    assert.equal(units.status, 'fail')
  })

  it('is not-checkable for a categorical, non-numeric value', () => {
    const { value, units } = checkPrintValueAndUnits(print({ id: 'p1', value: 'Closed' }), [evidence({ id: 'fx-1' })])
    assert.equal(value.status, 'not-checkable')
    assert.equal(units.status, 'not-checkable')
  })
})

describe('verifyPrint — overall pass/fail', () => {
  it('passes a print that is correct on every checkable dimension', () => {
    const result = verifyPrint(
      print({ id: 'p1', name: 'Fixture Corp', period: 'JUN ’26', value: '+20%' }),
      { 'fx-1': evidence({ id: 'fx-1', economicPeriod: 'Quarter ended 2026-06-30', excerpt: 'Revenue grew 20%.' }) },
    )
    assert.equal(result.overall, 'pass')
    assert.equal(result.metric.status, 'not-checkable')
  })

  it('fails overall when only the period is wrong, mirroring print-crwd-cloud', () => {
    const result = verifyPrint(
      print({ id: 'print-crwd-cloud', name: 'CrowdStrike Falcon Cloud', period: 'FY26', value: '>35%', evidenceIds: ['C13'] }),
      {
        C13: evidence({
          id: 'C13',
          title: 'CrowdStrike Q4 FY2026 Results — Falcon Cloud segment',
          organization: 'CrowdStrike',
          economicPeriod: 'Quarter ended 2026-01-31',
          excerpt: 'For the first time, our cloud business exceeded $800 million in ending ARR… grew more than 35% year over year.',
        }),
      },
    )
    assert.equal(result.overall, 'fail')
    assert.equal(result.period.status, 'fail')
    assert.equal(result.value.status, 'pass')
  })

  it('fails overall when the value is absent from evidence', () => {
    const result = verifyPrint(
      print({ id: 'p2', name: 'Fixture Corp', period: 'JUN ’26', value: '$999M' }),
      { 'fx-1': evidence({ id: 'fx-1', economicPeriod: 'Quarter ended 2026-06-30', excerpt: 'Revenue grew 20% to $50 million.' }) },
    )
    assert.equal(result.overall, 'fail')
    assert.equal(result.value.status, 'fail')
  })
})
