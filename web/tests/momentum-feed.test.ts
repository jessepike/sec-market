import assert from 'node:assert/strict'
import { test } from 'node:test'
import { certifiedGrowth, domainMomentum, formatPoints } from '../src/data/tracker/momentum'
import { feedChanges, isLedgerItem, statedAmount, tileSnapshot } from '../src/data/tracker/feed'
import { isCertifiedSupplier } from '../src/data/tracker/certification'

test('momentum ranks only certified SEC filers, highest growth first, with a median from two or more', () => {
  for (const d of domainMomentum()) {
    assert.ok(d.rows.every(r => isCertifiedSupplier(r.supplier.id)))
    assert.deepEqual(d.rows.map(r => r.latest), d.rows.map(r => r.latest).slice().sort((a, b) => b - a))
    assert.equal(d.median === null, d.rows.length < 2)
    assert.ok(d.others.every(o => !d.rows.some(r => r.supplier.id === o.supplier.id)))
  }
  assert.equal(certifiedGrowth.length, 16)
})

test('points format keeps the sign', () => {
  assert.equal(formatPoints(3.4), '+3.4 pts'); assert.equal(formatPoints(-0.2), '−0.2 pts'); assert.equal(formatPoints(0), '0.0 pts')
})

test('stated amounts read millions, billions and full figures, not per-share prices', () => {
  assert.equal(statedAmount('valued at approximately $6.3 billion, or $49.75 per share'), 6.3e9)
  assert.equal(statedAmount('a facility of $400.0 million'), 400e6)
  assert.equal(statedAmount('aggregate principal amount of $1,250,000,000 of notes'), 1.25e9)
  assert.equal(statedAmount('$49.75 per share'), null)
  assert.equal(statedAmount('$200,000 of letters of credit'), null)
})

test('the front feed holds no routine filings or results and is sorted by stated amount', () => {
  assert.ok(feedChanges.every(item => !isLedgerItem(item)))
  const amounts = feedChanges.map(i => statedAmount(i.text) ?? 0)
  assert.deepEqual(amounts, amounts.slice().sort((a, b) => b - a))
  assert.equal(tileSnapshot('no-such-group'), '')
})
