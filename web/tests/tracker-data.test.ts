import assert from 'node:assert/strict'
import { describe, it } from 'node:test'
import { evidenceById } from '../src/data/evidence.ts'
import { notCoveredByTracker, trackerDomainIds, trackerDomains } from '../src/data/tracker/domains.ts'
import {
  edgarFilingsInLast30Days,
  eventSummaryForSupplier,
  eventsInLast30Days,
  medianRevenueGrowthForDomain,
  parseGrowthPercent,
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
})
