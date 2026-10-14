import assert from 'node:assert/strict'
import { test } from 'node:test'
import edgarFacts from '../src/data/generated/edgarFacts.json' with { type: 'json' }
import { runStatus } from '../src/data/runStatus'
import { edgarFilingsInLast30Days } from '../src/data/tracker/derive'
import { trackerSuppliers } from '../src/data/tracker/suppliers'
import { eventGroups, monthEvents, recentChanges, revenueGrowthRows, secCollectedCount, secFilerCount, yearEvents } from '../src/data/tracker/presentation'

test('SEC coverage includes every corrected filer and counts failures independently', () => {
  assert.equal(secFilerCount, 16)
  assert.equal(secCollectedCount, 16)
  assert.equal(secFilerCount, edgarFacts.suppliers.length)
  assert.ok(edgarFacts.suppliers.some(s => s.id === 'netskope'))
  assert.ok(edgarFacts.suppliers.some(s => s.id === 'sailpoint'))
})

test('change log retains every recent event and latest filing once after grouping', () => {
  const changes = recentChanges()
  for (const event of monthEvents) assert.equal(changes.filter(item => item.id === event.id).length, 1)
  const filings = changes.flatMap(item => item.filings)
  const expected = edgarFilingsInLast30Days(runStatus.lastChecked, edgarFacts)
  assert.equal(filings.length, expected.length)
  assert.equal(new Set(filings.map(f => `${f.supplierId}:${f.periodEnd}`)).size, expected.length)
  for (const filing of expected) assert.ok(filings.some(f => f.sourceUrl === filing.sourceUrl && f.filedDate === filing.filedDate))
})

test('growth comparison excludes company metrics and segments, retaining exact signed reported percentages', () => {
  const rows = revenueGrowthRows()
  assert.equal(rows.length, 18)
  assert.ok(rows.some(r => r.latest < 0))
  for (const row of rows) {
    assert.equal(row.supplier.kind, 'public')
    assert.equal(row.latest, Number(row.supplier.revenue!.latest.yoyGrowth.replace('%', '')))
    assert.ok(row.supplier.revenue!.latest.evidenceIds.length > 0)
    assert.ok(row.supplier.revenue!.latest.periodEnd)
  }
  assert.ok(!rows.some(r => r.supplier.id === 'msft-entra' || r.supplier.id === 'crwd-cloud'))
  assert.ok(trackerSuppliers.some(s => /over|>|approximately/i.test(s.headlineMetric?.value ?? '')))
})

test('all generated and collected events belong to exactly one timeline lane', () => {
  for (const event of yearEvents) assert.equal(eventGroups.filter(g => g.types.includes(event.type)).length, 1)
  assert.equal(eventGroups.reduce((sum, g) => sum + yearEvents.filter(e => g.types.includes(e.type)).length, 0), yearEvents.length)
})
