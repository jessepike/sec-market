import assert from 'node:assert/strict'
import { test } from 'node:test'
import rawEdgarFacts from '../src/data/generated/edgarFacts.json' with { type: 'json' }
import { listedEdgarFacts as edgarFacts } from '../src/data/tracker/listedEdgar'
import { runStatus } from '../src/data/runStatus'
import { edgarFilingsInLast30Days } from '../src/data/tracker/derive'
import { trackerSuppliers } from '../src/data/tracker/suppliers'
import { countedUnits, eventGroups, monthEvents, recentChanges, revenueGrowthRows, secCollectedCount, secFilerCount, secFilingsInLastYear, yearChanges, yearEvents } from '../src/data/tracker/presentation'
import type { ChangeItem } from '../src/data/tracker/presentation'

test('SEC coverage includes every corrected filer and counts failures independently', () => {
  assert.equal(secFilerCount, 16)
  assert.equal(secCollectedCount, 16)
  assert.equal(secFilerCount, edgarFacts.suppliers.length)
  assert.ok(edgarFacts.suppliers.some(s => s.id === 'netskope'))
  assert.ok(edgarFacts.suppliers.some(s => s.id === 'sailpoint'))
})

test('SEC companies still in onboarding never reach the page through the EDGAR collection', () => {
  const listed = new Set(trackerSuppliers.filter(s => s.kind === 'public' && s.edgarId).map(s => s.edgarId))
  for (const s of edgarFacts.suppliers) assert.ok(listed.has(s.id), s.id)
  for (const s of rawEdgarFacts.suppliers) if (!listed.has(s.id)) assert.ok(!secFilingsInLastYear().some(f => f.supplierId === s.id), s.id)
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
  // 18 before onboarding graduations (D-138); a graduated SEC filer adds a row.
  assert.ok(rows.length >= 18)
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

const row = (id: string, supplierId: string, date: string, type: string, text: string) =>
  ({ id, supplierId, date, type, text, evidenceIds: [], filings: [] }) as unknown as ChangeItem

test('every recent SEC filing is counted under results, once', () => {
  const units = countedUnits(recentChanges())
  const filings = edgarFilingsInLast30Days(runStatus.lastChecked, edgarFacts)
  const results = units.filter(u => u.groupId === 'results')
  for (const filing of filings) {
    assert.equal(results.filter(u => u.items.some(i => i.filings.some(f => f.sourceUrl === filing.sourceUrl))).length, 1)
  }
})

test('the year view keeps one event per SEC filing, never a comparative quarter', () => {
  const filings = secFilingsInLastYear()
  assert.equal(new Set(filings.map(f => f.sourceUrl)).size, filings.length)
  const crwd = filings.filter(f => f.supplierId === 'crwd' && f.filedDate === '2026-08-27').map(f => f.periodEnd)
  assert.deepEqual(crwd, ['2026-07-31'])
  const items = yearChanges()
  for (const filing of filings) assert.equal(items.filter(i => i.filings.some(f => f.sourceUrl === filing.sourceUrl)).length, 1)
  for (const event of yearEvents) assert.equal(items.filter(i => i.id === event.id).length, 1)
})

test('one deal reported by both companies, with a co-investment, counts as one acquisition', () => {
  const units = countedUnits([
    row('a', 'varonis', '2026-10-15', 'acquisition', 'Varonis and Proofpoint announced a definitive agreement for Proofpoint to acquire Varonis'),
    row('b', 'proofpoint', '2026-10-15', 'acquisition', 'Varonis will be acquired by Proofpoint'),
    row('c', 'proofpoint', '2026-10-15', 'funding', 'Ontario Teachers’ Pension Plan has also agreed to make an investment into Proofpoint'),
    row('d', 'cyera', '2026-10-15', 'funding', 'Cyera raised a round'),
    row('e', 'varonis', '2026-10-15', 'exec-change', 'Form 8-K (Item 5.02)'),
  ])
  assert.deepEqual(units.map(u => [u.groupId, u.items.length]).sort(), [['funding', 1], ['leadership', 1], ['ownership', 3]])
})

test('a deal announced and completed on different dates counts once, at its first date', () => {
  const units = countedUnits(yearChanges()).filter(u => u.items.some(i => i.id === 'EV-delinea-2'))
  assert.equal(units.length, 1)
  assert.deepEqual(units[0].items.map(i => i.id), ['EV-delinea-2', 'EV-delinea-3'])
  assert.equal(units[0].date, '2026-01-15')
})

test('growth measured in another currency is marked', () => {
  const rows = revenueGrowthRows()
  assert.equal(rows.find(r => r.supplier.id === 'trend-micro')!.currency, 'JPY')
  assert.ok(rows.filter(r => r.supplier.id !== 'trend-micro').every(r => r.currency === null))
})
