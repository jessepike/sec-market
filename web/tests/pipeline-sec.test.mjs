// Fictional SEC payloads exercise the real bridge and existing independent verifier.
import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { execFileSync } from 'node:child_process'
import { verifySecEvents } from '../scripts/sec-verify/independent.mjs'
const bridge = input => JSON.parse(execFileSync(process.execPath, ['--import', 'tsx', 'scripts/pipeline/sec-adapter.mjs'], { input: JSON.stringify(input), encoding: 'utf8', stdio: ['pipe', 'pipe', 'pipe'] }))
test('SEC bridge re-derives fixture revenue and returns stable identities', () => {
  const facts = JSON.parse(readFileSync('tests/fixtures/edgar-companyfacts-fixture.json', 'utf8'))
  facts.cik = 1535527 // Test-only identity, never a claim about CrowdStrike's revenue.
  const input = { kind: 'sec_facts', supplierId: 'crwd', documents: [facts], windowEnd: '2026-10-19' }
  const first = bridge(input), second = bridge(input)
  assert(first.checks.every(c => c.ok))
  assert.equal(first.facts[0].value.quarters.length, 8)
  assert.equal(first.facts[0].value.latest.quarter.value, 134000000)
  assert.equal(first.facts[0].factId, second.facts[0].factId)
  assert.equal(first.facts[0].assurance, 'sec_rederived')
})
test('SEC bridge rejects a payload for a different CIK', () => {
  const facts = JSON.parse(readFileSync('tests/fixtures/edgar-companyfacts-fixture.json', 'utf8'))
  assert.throws(() => bridge({ kind: 'sec_facts', supplierId: 'crwd', documents: [facts], windowEnd: '2026-10-19' }))
})
test('SEC submissions bridge preserves every tracked item and archived late notice', () => {
  const recent = { accessionNumber: ['0001535527-26-000001'], form: ['8-K'], filingDate: ['2026-10-19'], reportDate: ['2026-10-18'], items: ['5.02,2.03'], primaryDocument: ['fixture.htm'] }
  const archive = { accessionNumber: ['0001535527-26-000002'], form: ['NT 10-Q'], filingDate: ['2026-09-19'], reportDate: ['2026-09-18'], items: [''], primaryDocument: ['late.htm'] }
  const submissions = { cik: 1535527, name: 'CrowdStrike', tickers: ['CRWD'], filings: { recent } }
  const result = bridge({ kind: 'sec_submissions', supplierId: 'crwd', documents: [submissions, archive], windowEnd: '2026-10-19' })
  assert(result.checks.every(c => c.ok))
  assert.deepEqual(result.facts[1].value.map(e => e.type).sort(), ['debt', 'exec-change', 'late-filing'])
})
test('a late notice is anchored to its filing date and cannot borrow a report date', () => {
  const source = { filings: { recent: { accessionNumber: ['notice'], form: ['NT 10-Q'], filingDate: ['2026-10-19'], reportDate: ['2026-10-18'], items: [''] } } }
  const event = { id: 'notice', date: '2026-10-19', accessions: ['notice'], evidenceDates: ['2026-10-19'], type: 'late-filing' }
  assert.equal(verifySecEvents(source, [event], [event], '2026-10-01', '2026-10-19', '2026-10-19').ok, true)
  assert.equal(verifySecEvents(source, [{ ...event, date: '2026-10-18' }], [event], '2026-10-01', '2026-10-19', '2026-10-19').ok, false)
})
