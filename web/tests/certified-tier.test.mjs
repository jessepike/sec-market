// SEC-MARKET-AUTO-002-P0: certified-tier contract and independent verifier.
import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { edgarRegistry } from '../src/data/edgarRegistry.ts'
import { trackerSuppliers } from '../src/data/tracker/suppliers.ts'
import { selectRevenueFacts } from '../src/data/edgarLogic.ts'
import { verifyRevenuePeriod, verifyNotStale, verifyIdentity, verifySecEvents, accessionFromUrl, normalizeName } from '../scripts/sec-verify/independent.mjs'

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
  filings: { recent: { form: forms.map(f => f.form), filingDate: forms.map(f => f.date), accessionNumber: forms.map(f => f.accn), items: forms.map(f => f.items ?? ''), primaryDocument: forms.map(() => 'x.htm') } } })

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

test('SEC events must cite filings that exist and cover every tracked filing in the window', () => {
  const index = subs([{ form: '8-K', date: '2026-06-01', accn: '0000000001-26-000001', items: '5.02,9.01' }, { form: '8-K', date: '2026-07-01', accn: '0000000001-26-000002', items: '2.02' }])
  const ev = [{ date: '2026-06-01', accessions: ['0000000001-26-000001'] }]
  assert.equal(verifySecEvents(index, ev, ['2026-06-01'], '2025-10-15', '2026-10-15', '2026-10-15').ok, true)
  assert.equal(verifySecEvents(index, [], [], '2025-10-15', '2026-10-15', '2026-10-15').ok, false, 'missing 5.02 event')
  assert.equal(verifySecEvents(index, [{ date: '2026-06-02', accessions: ['0000000001-26-000001'] }], ['2026-06-01', '2026-06-02'], '2025-10-15', '2026-10-15', '2026-10-15').ok, false, 'event after its filing')
  assert.equal(verifySecEvents(index, [{ date: '2026-06-01', accessions: ['9999999999-26-000009'] }], ['2026-06-01'], '2025-10-15', '2026-10-15', '2026-10-15').ok, false, 'unknown accession')
  const late = subs([{ form: '8-K', date: '2026-10-15', accn: '0000000001-26-000003', items: '5.02' }])
  assert.equal(verifySecEvents(late, [], [], '2025-10-14', '2026-10-14', '2026-10-15').ok, false, 'filing after window end')
  assert.equal(accessionFromUrl('https://www.sec.gov/Archives/edgar/data/1660280/000166028026000046/tenb-20261013.htm'), '0001660280-26-000046')
})
