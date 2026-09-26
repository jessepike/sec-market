import assert from 'node:assert/strict'
import { describe, it } from 'node:test'
import { evidenceById } from '../src/data/evidence.ts'
import { notCoveredByTracker, trackerDomainIds, trackerDomains } from '../src/data/tracker/domains.ts'
import {
  abbreviateDollar,
  edgarFilingsInLast30Days,
  eventSummaryForSupplier,
  eventsInLast30Days,
  formatHeadlineCompact,
  formatMonthYear,
  formatOwnershipCompact,
  formatShortDate,
  formatShortQuarter,
  formatYear,
  medianRevenueGrowthForDomain,
  parseGrowthPercent,
  shortSupplierName,
  suppliersForDomain,
} from '../src/data/tracker/derive.ts'
import { trackerEvents } from '../src/data/tracker/events.ts'
import { trackerSuppliers } from '../src/data/tracker/suppliers.ts'

const BANNED_WORDS = [
  'leading',
  'strong',
  'weak',
  'solid',
  'healthy',
  'concerning',
  'accelerating',
  'struggling',
  'winning',
  'fading',
]

function bannedWordsIn(text: string): string[] {
  return BANNED_WORDS.filter((word) => new RegExp(`\\b${word}\\b`, 'i').test(text))
}

describe('tracker domains and suppliers', () => {
  it('declares exactly twelve domains with unique ids', () => {
    assert.equal(trackerDomains.length, 12)
    assert.equal(new Set(trackerDomainIds).size, 12)
  })

  it('gives every domain at least three suppliers', () => {
    for (const domain of trackerDomains) {
      const suppliers = suppliersForDomain(domain.id)
      assert.ok(suppliers.length >= 3, `${domain.id} has only ${suppliers.length} supplier(s)`)
    }
  })

  it('gives every supplier at least one known domain', () => {
    for (const supplier of trackerSuppliers) {
      assert.ok(supplier.domainIds.length > 0, `${supplier.id} names no domain`)
      for (const domainId of supplier.domainIds) {
        assert.ok(trackerDomainIds.includes(domainId), `${supplier.id} names unknown domain ${domainId}`)
      }
    }
  })

  it('keeps supplier and event ids unique', () => {
    const supplierIds = trackerSuppliers.map((s) => s.id)
    assert.equal(new Set(supplierIds).size, supplierIds.length, 'duplicate supplier id')
    const eventIds = trackerEvents.map((e) => e.id)
    assert.equal(new Set(eventIds).size, eventIds.length, 'duplicate event id')
  })

  it('resolves every evidence id a supplier or event cites, each with a source URL and a retrieval date', () => {
    const ids = new Set<string>()
    for (const supplier of trackerSuppliers) {
      for (const id of supplier.headlineMetric?.evidenceIds ?? []) ids.add(id)
      for (const id of supplier.revenue?.latest.evidenceIds ?? []) ids.add(id)
      for (const id of supplier.revenue?.prior?.evidenceIds ?? []) ids.add(id)
      for (const id of supplier.lastRound?.evidenceIds ?? []) ids.add(id)
      for (const id of supplier.ownership?.evidenceIds ?? []) ids.add(id)
    }
    for (const event of trackerEvents) {
      for (const id of event.evidenceIds) ids.add(id)
    }
    assert.ok(ids.size > 0, 'expected the tracker to cite evidence')
    for (const id of ids) {
      const record = evidenceById[id]
      assert.ok(record, `evidence id "${id}" does not resolve`)
      assert.ok(record.canonicalUrl && record.canonicalUrl.length > 0, `evidence "${id}" has no URL`)
      assert.ok(record.retrievedAt || record.publicationDate, `evidence "${id}" has no retrieval date`)
    }
  })

  it('never publishes a rung-5-only event', () => {
    for (const event of trackerEvents) {
      assert.notEqual(event.rung, 5, `event "${event.id}" is rung 5 — must not publish alone`)
      assert.ok(event.rung >= 1 && event.rung <= 4, `event "${event.id}" has rung ${event.rung}`)
    }
  })

  it('keeps every event within the trailing 12-month window', () => {
    for (const event of trackerEvents) {
      assert.ok(event.date >= '2025-09-25' && event.date <= '2026-09-25', `event "${event.id}" dated ${event.date} is outside the window`)
    }
  })

  it('carries no banned judgment word in the tracker’s own authored strings', () => {
    for (const domain of trackerDomains) {
      assert.deepEqual(bannedWordsIn(domain.scope), [], `domain ${domain.id} scope`)
    }
    for (const line of notCoveredByTracker) {
      assert.deepEqual(bannedWordsIn(line), [], `not-covered line "${line}"`)
    }
    for (const supplier of trackerSuppliers) {
      if (supplier.headlineMetric) assert.deepEqual(bannedWordsIn(supplier.headlineMetric.label), [], supplier.id)
      if (supplier.ownership) assert.deepEqual(bannedWordsIn(supplier.ownership.status), [], supplier.id)
      if (supplier.lastRound) assert.deepEqual(bannedWordsIn(supplier.lastRound.stage), [], supplier.id)
    }
    for (const event of trackerEvents) {
      assert.deepEqual(bannedWordsIn(event.text), [], `event ${event.id}`)
    }
  })
})

describe('tracker derive helpers (fixtures)', () => {
  it('parses a signed percent string', () => {
    assert.equal(parseGrowthPercent('+26%'), 26)
    assert.equal(parseGrowthPercent('-5.2%'), -5.2)
    assert.equal(parseGrowthPercent('26%'), 26)
    assert.equal(parseGrowthPercent(undefined), null)
    assert.equal(parseGrowthPercent('no comparable figure'), null)
  })

  it('computes a median only with two or more comparable public/segment suppliers', () => {
    for (const domain of trackerDomains) {
      const value = medianRevenueGrowthForDomain(domain.id)
      const publicCount = suppliersForDomain(domain.id).filter(
        (s) => (s.kind === 'public' || s.kind === 'segment') && parseGrowthPercent(s.revenue?.latest.yoyGrowth) !== null,
      ).length
      if (publicCount < 2) {
        assert.equal(value, null, `${domain.id} should have no median with <2 comparable public suppliers`)
      } else {
        assert.ok(typeof value === 'number', `${domain.id} should compute a median`)
      }
    }
  })

  it('summarizes an unknown supplier as zero events', () => {
    const summary = eventSummaryForSupplier('not-a-real-supplier-id')
    assert.deepEqual(summary, { count: 0, latest: null })
  })

  it('filters events to a 30-day trailing window, inclusive, newest first', () => {
    const inWindow = eventsInLast30Days('2026-09-25')
    for (const event of inWindow) {
      assert.ok(event.date >= '2026-08-26' && event.date <= '2026-09-25', event.id)
    }
    for (let i = 1; i < inWindow.length; i++) {
      assert.ok(inWindow[i - 1].date >= inWindow[i].date, 'not sorted newest-first')
    }
  })

  it('filters EDGAR filings to a 30-day trailing window from a fixture facts file', () => {
    const facts = {
      generatedAt: '2026-09-25T00:00:00Z',
      suppliers: [
        {
          id: 'fixture',
          name: 'Fixture Co',
          cik: '0000000000',
          quarters: [
            {
              periodEnd: '2026-07-31',
              filedDate: '2026-09-01',
              form: '10-Q',
              value: 100,
              sourceUrl: 'https://example.test/fixture-1',
            },
            {
              periodEnd: '2026-04-30',
              filedDate: '2026-06-01',
              form: '10-Q',
              value: 90,
              sourceUrl: 'https://example.test/fixture-2',
            },
          ],
        },
      ],
    }
    const filings = edgarFilingsInLast30Days('2026-09-25', facts)
    assert.equal(filings.length, 1)
    assert.equal(filings[0].filedDate, '2026-09-01')
  })

  it('never reports a restated prior-year comparative as a new filing (AUTO-001 fix pass, item 1)', () => {
    // Mirrors the real edgarFacts.json shape: dedupeByPeriodEnd keeps
    // whichever fact for a given periodEnd was filed most recently, so a
    // 10-Q that reports 2026-07-31 also restates the 2025-07-31
    // comparative under the SAME filedDate. Only the true latest quarter
    // (max periodEnd) may appear in the 30-day window, never the
    // comparative — see the regression this fixed:
    // "SailPoint filed its 10-Q for the quarter ended 2025-07-31".
    const facts = {
      generatedAt: '2026-09-26T00:00:00Z',
      suppliers: [
        {
          id: 'fixture',
          name: 'Fixture Co',
          cik: '0000000000',
          quarters: [
            {
              periodEnd: '2026-07-31',
              filedDate: '2026-09-10',
              form: '10-Q',
              value: 100,
              sourceUrl: 'https://example.test/fixture-current',
            },
            {
              periodEnd: '2025-07-31',
              filedDate: '2026-09-10',
              form: '10-Q',
              value: 85,
              sourceUrl: 'https://example.test/fixture-comparative',
            },
          ],
        },
      ],
    }
    const filings = edgarFilingsInLast30Days('2026-09-26', facts)
    assert.equal(filings.length, 1)
    assert.equal(filings[0].periodEnd, '2026-07-31')
  })
})

describe('density-pass display helpers (fixtures)', () => {
  it('strips a legal-entity suffix but leaves a genuine brand word alone', () => {
    assert.equal(shortSupplierName('CrowdStrike Holdings, Inc.'), 'CrowdStrike')
    assert.equal(shortSupplierName('Tenable Holdings, Inc.'), 'Tenable')
    assert.equal(shortSupplierName('Forescout Technologies, Inc.'), 'Forescout')
    assert.equal(shortSupplierName('Veeam Software'), 'Veeam')
    assert.equal(shortSupplierName('Trend Micro Incorporated'), 'Trend Micro')
    assert.equal(shortSupplierName('Sophos Group (Sophos Ltd)'), 'Sophos')
    assert.equal(shortSupplierName('Rapid7, Inc.'), 'Rapid7')
    // brand words that are not legal-entity suffixes survive untouched
    assert.equal(shortSupplierName('Zscaler'), 'Zscaler')
    assert.equal(shortSupplierName('Microsoft Defender for Endpoint'), 'Microsoft Defender for Endpoint')
    assert.equal(shortSupplierName('Palo Alto Networks, Inc.'), 'Palo Alto Networks')
    assert.equal(shortSupplierName('Cato Networks'), 'Cato Networks')
  })

  it('formats compact quarter, event, month-year, and year labels', () => {
    assert.equal(formatShortQuarter('2026-07-31'), 'Q Jul 26')
    assert.equal(formatShortDate('2026-08-12'), '12 Aug 26')
    assert.equal(formatMonthYear('2026-04-20'), 'Apr 2026')
    assert.equal(formatMonthYear('2024-01'), 'Jan 2024')
    assert.equal(formatYear('2020-03-01'), '2020')
    assert.equal(formatShortQuarter(undefined), '')
  })

  it('abbreviates a dollar figure to one letter, keeping any leading qualifier', () => {
    assert.equal(abbreviateDollar('$5.84 billion'), '$5.84B')
    assert.equal(abbreviateDollar('$651.4 million'), '$651.4M')
    assert.equal(abbreviateDollar('>$1.7 billion'), '>$1.7B')
    assert.equal(abbreviateDollar('$250 million'), '$250M')
    assert.equal(abbreviateDollar('over $200 million'), 'over $200M')
    assert.equal(abbreviateDollar(undefined), '')
  })

  it('formats the own-metric cell as "label value · Q mon yy"', () => {
    const withEndedDate = formatHeadlineCompact({
      id: 'x',
      name: 'X',
      domainIds: [],
      kind: 'public',
      headlineMetric: {
        label: 'ARR',
        value: '$5.84 billion',
        period: 'Q2 FY2027, ended 2026-07-31',
        evidenceIds: ['e1'],
      },
    })
    assert.equal(withEndedDate, 'ARR $5.84B · Q Jul 26')

    const withoutMetric = formatHeadlineCompact({ id: 'y', name: 'Y', domainIds: [], kind: 'private' })
    assert.equal(withoutMetric, '')
  })

  it('formats the ownership-or-last-round cell for every supplier kind', () => {
    assert.equal(
      formatOwnershipCompact({
        id: 'crwd',
        name: 'CrowdStrike Holdings, Inc.',
        domainIds: [],
        kind: 'public',
        ticker: 'CRWD',
        ownership: { status: 'Independent, publicly traded (Nasdaq: CRWD).', evidenceIds: ['e1'] },
      }),
      'Public · CRWD',
    )

    assert.equal(
      formatOwnershipCompact({
        id: 'msft-defender',
        name: 'Microsoft Defender for Office 365',
        domainIds: [],
        kind: 'segment',
        ownership: {
          status: 'Segment of Microsoft Corporation (publicly traded, Nasdaq: MSFT). No separate revenue disclosed.',
          evidenceIds: ['e1'],
        },
      }),
      'Segment of Microsoft',
    )

    assert.equal(
      formatOwnershipCompact({
        id: 'sophos',
        name: 'Sophos Group (Sophos Ltd)',
        domainIds: [],
        kind: 'pe-owned',
        ownership: {
          status: 'Owned by Thoma Bravo since March 2020.',
          acquirer: 'Thoma Bravo',
          announced: '2020-03-01',
          evidenceIds: ['e1'],
        },
      }),
      'PE-owned · Thoma Bravo (2020)',
    )

    assert.equal(
      formatOwnershipCompact({
        id: 'armis',
        name: 'Armis Security Ltd.',
        domainIds: [],
        kind: 'acquired',
        ownership: {
          status: "Acquired; ServiceNow closed its acquisition of Armis on April 20, 2026.",
          acquirer: 'ServiceNow, Inc. (NYSE: NOW)',
          closed: '2026-04-20',
          evidenceIds: ['e1'],
        },
      }),
      'Acquired by ServiceNow · Apr 2026',
    )

    assert.equal(
      formatOwnershipCompact({
        id: 'abnormal-security',
        name: 'Abnormal Security',
        domainIds: [],
        kind: 'private',
        lastRound: {
          date: '2024-08-06',
          stage: 'Series D',
          amount: '$250 million',
          evidenceIds: ['e1'],
        },
      }),
      'Series D $250M · Aug 2024',
    )

    assert.equal(
      formatOwnershipCompact({ id: 'nothing', name: 'Nothing Co', domainIds: [], kind: 'private' }),
      '–',
    )
  })
})
