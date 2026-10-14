import assert from 'node:assert/strict'
import { describe, it } from 'node:test'
import {
  DOMAIN_PRINT_GROUP,
  MAX_VISIBLE_VENDORS_PER_DOMAIN,
  OLDER_FIGURE_THRESHOLD_DAYS,
  SEGMENT_PRINT_IDS,
  marketPictureVendorEntries,
} from '../src/data/marketPicture.ts'
import { securityDomains } from '../src/data/domains.ts'
import { vendorPrints } from '../src/data/prints.ts'
import type { EvidenceRecord, VendorPrint } from '../src/data/types.ts'

function makePrint(overrides: Partial<VendorPrint> & Pick<VendorPrint, 'id' | 'name'>): VendorPrint {
  return {
    id: overrides.id,
    group: overrides.group ?? 'Network & edge',
    name: overrides.name,
    period: overrides.period ?? 'JAN ’26',
    value: overrides.value ?? '+10%',
    metric: overrides.metric ?? 'revenue',
    note: overrides.note ?? '',
    tone: overrides.tone ?? 'up',
    surface: overrides.surface,
    position: overrides.position,
    evidenceIds: overrides.evidenceIds ?? [],
    secondaryGroup: overrides.secondaryGroup,
    vendorSlug: overrides.vendorSlug,
  }
}

function makeEvidence(id: string, publicationDate: string): EvidenceRecord {
  return {
    id,
    title: `Fixture ${id}`,
    organization: 'Fixture Org',
    publicationDate,
    economicPeriod: 'Fixture period',
    canonicalUrl: `https://example.test/${id}`,
    excerpt: 'Fixture excerpt.',
    sourceClass: 'INDEPENDENT',
    interpretation: 'Fixture interpretation.',
    limitations: 'Fixture limitation.',
    conflictingEvidenceIds: [],
    artifactLabel: `FIXTURE / ${id}`,
    tags: ['fixture'],
  }
}

const TODAY = '2026-09-19' // matches meta.ts's LAST_UPDATED_ISO

describe('marketPictureVendorEntries', () => {
  it('orders entries alphabetically by vendor name regardless of figure size', () => {
    const prints = [
      makePrint({ id: 'p-zeta', name: 'Zeta Security', value: '+90%', evidenceIds: ['E1'] }),
      makePrint({ id: 'p-alpha', name: 'Alpha Security', value: '+5%', evidenceIds: ['E2'] }),
      makePrint({ id: 'p-mid', name: 'Mid Security', value: '+40%', evidenceIds: ['E3'] }),
    ]
    const evidenceById = {
      E1: makeEvidence('E1', '2026-09-01'),
      E2: makeEvidence('E2', '2026-09-01'),
      E3: makeEvidence('E3', '2026-09-01'),
    }
    const entries = marketPictureVendorEntries(prints, TODAY, evidenceById)
    assert.deepEqual(
      entries.map((entry) => entry.print.name),
      ['Alpha Security', 'Mid Security', 'Zeta Security'],
    )
  })

  it('never includes a record whose surface is not a real print', () => {
    const prints = [
      makePrint({ id: 'p-coverage', name: 'Coverage Co', value: '+99%', surface: 'coverage', evidenceIds: ['E1'] }),
      makePrint({ id: 'p-print', name: 'Print Co', value: '+10%', evidenceIds: ['E2'] }),
    ]
    const evidenceById = {
      E1: makeEvidence('E1', '2026-09-01'),
      E2: makeEvidence('E2', '2026-09-01'),
    }
    const entries = marketPictureVendorEntries(prints, TODAY, evidenceById)
    assert.deepEqual(
      entries.map((entry) => entry.print.id),
      ['p-print'],
    )
  })

  it('excludes a record with no percent figure at all (a valuation, a count, a close)', () => {
    const prints = [
      makePrint({ id: 'p-valuation', name: 'Valuation Co', value: '$1.5B', evidenceIds: ['E1'] }),
      makePrint({ id: 'p-count', name: 'Count Co', value: '300+', evidenceIds: ['E2'] }),
    ]
    const evidenceById = {
      E1: makeEvidence('E1', '2026-09-01'),
      E2: makeEvidence('E2', '2026-09-01'),
    }
    assert.deepEqual(marketPictureVendorEntries(prints, TODAY, evidenceById), [])
  })

  it('attaches a "previous" value only when the vendor name AND the metric label both match exactly', () => {
    const sameMetric = [
      makePrint({ id: 'p-old', name: 'Acme', metric: 'ARR', value: '+20%', period: 'JAN ’26', evidenceIds: ['E1'] }),
      makePrint({ id: 'p-new', name: 'Acme', metric: 'ARR', value: '+25%', period: 'JUL ’26', evidenceIds: ['E2'] }),
    ]
    const evidenceById = {
      E1: makeEvidence('E1', '2026-02-01'),
      E2: makeEvidence('E2', '2026-08-01'),
    }
    const entries = marketPictureVendorEntries(sameMetric, TODAY, evidenceById)
    assert.equal(entries.length, 1, 'same vendor + same metric collapses to one row')
    assert.equal(entries[0].print.id, 'p-new')
    assert.deepEqual(entries[0].previous, { value: '+20%', period: 'JAN ’26' })

    const differentMetric = [
      makePrint({ id: 'p-arr', name: 'Acme', metric: 'ARR', value: '+20%', period: 'JAN ’26', evidenceIds: ['E1'] }),
      makePrint({
        id: 'p-revenue',
        name: 'Acme',
        metric: 'total revenue',
        value: '+25%',
        period: 'JUL ’26',
        evidenceIds: ['E2'],
      }),
    ]
    const entriesDifferent = marketPictureVendorEntries(differentMetric, TODAY, evidenceById)
    assert.equal(entriesDifferent.length, 2, 'different metrics are two separate rows, never merged')
    for (const entry of entriesDifferent) {
      assert.equal(entry.previous, null, `"${entry.print.metric}" must not carry a previous value`)
    }
  })

  it('marks a figure "older" only once its evidence predates today by more than the threshold', () => {
    const justUnderThreshold = daysBefore(TODAY, OLDER_FIGURE_THRESHOLD_DAYS)
    const justOverThreshold = daysBefore(TODAY, OLDER_FIGURE_THRESHOLD_DAYS + 1)
    const prints = [
      makePrint({ id: 'p-fresh', name: 'Fresh Co', evidenceIds: ['E1'] }),
      makePrint({ id: 'p-boundary', name: 'Boundary Co', evidenceIds: ['E2'] }),
      makePrint({ id: 'p-stale', name: 'Stale Co', evidenceIds: ['E3'] }),
    ]
    const evidenceById = {
      E1: makeEvidence('E1', TODAY),
      E2: makeEvidence('E2', justUnderThreshold),
      E3: makeEvidence('E3', justOverThreshold),
    }
    const entries = marketPictureVendorEntries(prints, TODAY, evidenceById)
    const byId = Object.fromEntries(entries.map((entry) => [entry.print.id, entry]))
    assert.equal(byId['p-fresh'].isOlderFigure, false)
    assert.equal(byId['p-boundary'].isOlderFigure, false, 'exactly at the threshold is not yet "older"')
    assert.equal(byId['p-stale'].isOlderFigure, true)
  })

  it('flags a print id in SEGMENT_PRINT_IDS as a segment, and nothing else', () => {
    const [someSegmentId] = [...SEGMENT_PRINT_IDS]
    assert.ok(someSegmentId, 'expected at least one curated segment print id to test against')
    const prints = [
      makePrint({ id: someSegmentId, name: 'Segment Co', evidenceIds: ['E1'] }),
      makePrint({ id: 'not-a-segment', name: 'Whole Co', evidenceIds: ['E2'] }),
    ]
    const evidenceById = { E1: makeEvidence('E1', '2026-09-01'), E2: makeEvidence('E2', '2026-09-01') }
    const entries = marketPictureVendorEntries(prints, TODAY, evidenceById)
    const byId = Object.fromEntries(entries.map((entry) => [entry.print.id, entry]))
    assert.equal(byId[someSegmentId].isSegment, true)
    assert.equal(byId['not-a-segment'].isSegment, false)
  })
})

/** `n` days before `iso`, as an ISO date string — a small fixture-only helper, never used at render time. */
function daysBefore(iso: string, n: number): string {
  const date = new Date(`${iso}T00:00:00Z`)
  date.setUTCDate(date.getUTCDate() - n)
  return date.toISOString().slice(0, 10)
}

describe('marketPictureVendorEntries against real site data', () => {
  it('every domain resolves to a print group, and no domain silently loses its group mapping', () => {
    for (const domain of securityDomains) {
      assert.ok(DOMAIN_PRINT_GROUP[domain.id], `domain "${domain.id}" has no entry in DOMAIN_PRINT_GROUP`)
    }
  })

  it('no domain today shows more vendors than the site actually has to show (sanity bound)', () => {
    for (const domain of securityDomains) {
      const group = DOMAIN_PRINT_GROUP[domain.id]
      const groupPrints = vendorPrints.filter((print) => print.group === group)
      const entries = marketPictureVendorEntries(groupPrints, TODAY)
      assert.ok(
        entries.length <= groupPrints.length,
        `domain "${domain.id}" produced more market-picture entries than prints exist for its group`,
      )
    }
  })

  it('MAX_VISIBLE_VENDORS_PER_DOMAIN is a positive number the component can slice by', () => {
    assert.ok(MAX_VISIBLE_VENDORS_PER_DOMAIN > 0)
  })
})
