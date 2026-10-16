// SEC-MARKET-AUTO-002-P0: certified-tier contract and independent verifier.
import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { edgarRegistry } from '../src/data/edgarRegistry.ts'
import { trackerSuppliers } from '../src/data/tracker/suppliers.ts'
import { selectRevenueFacts } from '../src/data/edgarLogic.ts'
import { verifyRevenuePeriod, verifyNotStale, verifyIdentity, verifySecEvents, verifyPriorAdjacent, verifyHistory, accessionFromUrl, normalizeName } from '../scripts/sec-verify/independent.mjs'

const contract = JSON.parse(readFileSync(new URL('../src/data/tracker/certifiedContract.json', import.meta.url), 'utf8'))

test('certified supplier set is derived from the SEC registry, never hand-set', () => {
  const registry = new Set(edgarRegistry.map(r => r.id))
  const derived = trackerSuppliers.filter(s => s.edgarId && registry.has(s.edgarId)).map(s => s.id).sort()
  assert.deepEqual([...contract.supplierIds].sort(), derived)
  assert.deepEqual(contract.exclusions, {})
  assert.deepEqual(contract.undisclosedAnswers, {})
})

// Fixture: fiscal year = calendar year. Q1-Q3 filed in 10-Qs, Q4 derived from the 10-K.
const fact = (start, end, val, form, filed, accn) => ({ start, end, val, form, filed, accn })
const facts = (rows, concept = 'Revenues') => ({ facts: { 'us-gaap': { [concept]: { units: { USD: rows } } } } })
const rows = [
  fact('2025-01-01', '2025-03-31', 100, '10-Q', '2025-05-01', 'a1'),
  fact('2025-04-01', '2025-06-30', 110, '10-Q', '2025-08-01', 'a2'),
  fact('2025-07-01', '2025-09-30', 120, '10-Q', '2025-11-01', 'a3'),
  fact('2025-01-01', '2025-12-31', 460, '10-K', '2026-02-20', 'a4'),
  fact('2026-01-01', '2026-03-31', 125, '10-Q', '2026-05-01', 'a5'),
]
const latest = { value: '$125', priorYearValue: '$100', yoyGrowth: '+25.0%', period: 'Quarter ended 2026-03-31', periodEnd: '2026-03-31', releaseDate: '2026-05-01' }
const subs = (forms = [], extra = {}) => ({ cik: '1', name: 'Example Security, Inc.', tickers: ['EXS'], ...extra,
  filings: { recent: { form: forms.map(f => f.form), filingDate: forms.map(f => f.date), reportDate: forms.map(f => f.report ?? f.date), accessionNumber: forms.map(f => f.accn), items: forms.map(f => f.items ?? ''), primaryDocument: forms.map(() => 'x.htm') } } })

test('a displayed quarter that matches SEC passes, including a derived Q4', () => {
  assert.equal(verifyRevenuePeriod(facts(rows), ['Revenues'], latest, { requireReleaseDate: true }).ok, true)
  const q4 = { value: '$130', period: 'Quarter ended 2025-12-31 (derived from annual less preceding quarters)', periodEnd: '2025-12-31', yoyGrowth: '' }
  assert.equal(verifyRevenuePeriod(facts(rows), ['Revenues'], q4, { requireReleaseDate: false }).ok, true)
})

test('a changed value, wrong growth, wrong period text or wrong release date fails', () => {
  for (const bad of [{ value: '$126' }, { yoyGrowth: '+26.0%' }, { period: 'Quarter ended 2026-03-31 (derived)' }, { releaseDate: '2026-04-30' }]) {
    assert.equal(verifyRevenuePeriod(facts(rows), ['Revenues'], { ...latest, ...bad }, { requireReleaseDate: true }).ok, false, JSON.stringify(bad))
  }
})

test('a newer quarter under another concept or a newer 10-Q filing makes the latest quarter stale', () => {
  const both = { facts: { 'us-gaap': { ...facts(rows).facts['us-gaap'], RevenueFromContractWithCustomerExcludingAssessedTax: { units: { USD: [fact('2026-04-01', '2026-06-30', 140, '10-Q', '2026-08-01', 'b1')] } } } } }
  assert.equal(verifyNotStale(both, subs(), ['Revenues', 'RevenueFromContractWithCustomerExcludingAssessedTax'], latest).ok, false)
  assert.equal(verifyNotStale(facts(rows), subs([{ form: '10-Q', date: '2026-08-01', accn: 'z' }]), ['Revenues'], latest).ok, false)
  assert.equal(verifyNotStale(facts(rows), subs([{ form: '10-Q', date: '2026-05-01', accn: 'a5' }]), ['Revenues'], latest).ok, true)
})

test('the producer now picks the concept with the newest period, not the first listed', () => {
  const both = { facts: { 'us-gaap': { Revenues: { units: { USD: rows } }, RevenueFromContractWithCustomerExcludingAssessedTax: { units: { USD: [fact('2026-04-01', '2026-06-30', 140, '10-Q', '2026-08-01', 'b1')] } } } } }
  assert.equal(selectRevenueFacts(both, ['Revenues', 'RevenueFromContractWithCustomerExcludingAssessedTax']).concept, 'RevenueFromContractWithCustomerExcludingAssessedTax')
})

test('identity passes on name and ticker match and fails on mismatch or a delisting form', () => {
  const now = Date.parse('2026-10-15T00:00:00Z')
  assert.equal(normalizeName('CrowdStrike Holdings, Inc.'), normalizeName('CrowdStrike'))
  assert.equal(verifyIdentity(subs(), { name: 'Example Security', ticker: 'EXS', kind: 'public' }, now).ok, true)
  assert.equal(verifyIdentity(subs(), { name: 'Other Co', ticker: 'EXS', kind: 'public' }, now).ok, false)
  assert.equal(verifyIdentity(subs(), { name: 'Example Security', ticker: 'XXX', kind: 'public' }, now).ok, false)
  assert.equal(verifyIdentity(subs([{ form: '25-NSE', date: '2026-09-01', accn: 'd' }]), { name: 'Example Security', ticker: 'EXS', kind: 'public' }, now).ok, false)
})

test('the prior quarter must be the one immediately before latest, and every table row must match SEC', () => {
  assert.equal(verifyPriorAdjacent(facts(rows), ['Revenues'], '2026-03-31', '2025-12-31').ok, true)
  assert.equal(verifyPriorAdjacent(facts(rows), ['Revenues'], '2026-03-31', '2025-09-30').ok, false, 'stale prior quarter')
  const table = [{ periodEnd: '2026-03-31', value: 125, filedDate: '2026-05-01', accessionNumber: 'a5', derived: false }, { periodEnd: '2025-12-31', value: 130, filedDate: '2026-02-20', accessionNumber: 'a4', derived: true }]
  assert.equal(verifyHistory(facts(rows), ['Revenues'], table).ok, true)
  assert.equal(verifyHistory(facts(rows), ['Revenues'], [{ ...table[0], value: 126 }]).ok, false)
  assert.equal(verifyHistory(facts(rows), ['Revenues'], [{ ...table[1], derived: false }]).ok, false)
})

test('SEC events are anchored to filings and every tracked item is represented by type', () => {
  const W = ['2025-10-15', '2026-10-15', '2026-10-15']
  const index = subs([{ form: '8-K', date: '2026-06-03', report: '2026-06-01', accn: '0000000001-26-000001', items: '5.02,9.01' },
    { form: '8-K', date: '2026-07-01', accn: '0000000001-26-000002', items: '2.02' }])
  const ev = { id: 'EV-1', date: '2026-06-01', type: 'exec-change', accessions: ['0000000001-26-000001'], evidenceDates: ['2026-06-03'] }
  assert.equal(verifySecEvents(index, [ev], [ev], ...W).ok, true, 'event on report date')
  assert.equal(verifySecEvents(index, [], [], ...W).ok, false, 'missing 5.02 event')
  assert.equal(verifySecEvents(index, [{ ...ev, date: '2026-04-01' }], [{ ...ev, date: '2026-04-01' }], ...W).ok, false, 'event far before its 8-K')
  assert.equal(verifySecEvents(index, [{ ...ev, date: '2026-06-04' }], [{ ...ev, date: '2026-06-04' }], ...W).ok, false, 'event after its filing')
  assert.equal(verifySecEvents(index, [{ ...ev, evidenceDates: ['2026-06-01'] }], [ev], ...W).ok, false, 'evidence date not the filing date')
  assert.equal(verifySecEvents(index, [{ ...ev, accessions: ['9999999999-26-000009'] }], [ev], ...W).ok, false, 'unknown accession')
  const sameDayOtherType = { date: '2026-06-03', type: 'acquisition', accessions: [] }
  assert.equal(verifySecEvents(index, [], [sameDayOtherType], ...W).ok, false, 'same-day event of another type does not cover Item 5.02')
  const earnings = { date: '2026-06-01', type: 'results', accessions: ['0000000001-26-000001'] }
  assert.equal(verifySecEvents(index, [], [earnings], ...W).ok, false, 'event citing the 8-K with another type does not cover Item 5.02')
  const tenQ = subs([{ form: '10-Q', date: '2026-08-10', report: '2026-06-30', accn: '0000000001-26-000004' }])
  const inPeriod = { id: 'EV-2', date: '2026-05-15', type: 'acquisition', accessions: ['0000000001-26-000004'], evidenceDates: ['2026-08-10'] }
  assert.equal(verifySecEvents(tenQ, [inPeriod], [inPeriod], ...W).ok, true, 'event inside the 10-Q period')
  assert.equal(verifySecEvents(tenQ, [{ ...inPeriod, date: '2026-03-20' }], [], ...W).ok, false, 'event before the 10-Q period')
  const late = subs([{ form: '8-K', date: '2026-10-15', accn: '0000000001-26-000003', items: '5.02' }])
  assert.equal(verifySecEvents(late, [], [], '2025-10-14', '2026-10-14', '2026-10-15').ok, false, 'filing after window end')
  assert.equal(accessionFromUrl('https://www.sec.gov/Archives/edgar/data/1660280/000166028026000046/tenb-20261013.htm'), '0001660280-26-000046')
})
