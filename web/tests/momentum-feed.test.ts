import assert from 'node:assert/strict'
import { test } from 'node:test'
import { certifiedGrowth, domainMomentum, formatPoints } from '../src/data/tracker/momentum'
import { feedChanges, isLedgerItem, statedAmount, tileSnapshot } from '../src/data/tracker/feed'
import { eventFact, shortUsd } from '../src/data/tracker/eventFacts'
import { isCertifiedSupplier } from '../src/data/tracker/certification'

test('momentum ranks only certified SEC filers, highest growth first, with a median from three or more', () => {
  for (const d of domainMomentum()) {
    assert.ok(d.rows.every(r => isCertifiedSupplier(r.supplier.id)))
    assert.deepEqual(d.rows.map(r => r.latest), d.rows.map(r => r.latest).slice().sort((a, b) => b - a))
    assert.equal(d.median === null, d.rows.length < 3)
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
  assert.equal(shortUsd(6.3e9), '$6.3B'); assert.equal(shortUsd(5.5e6), '$5.5M'); assert.equal(shortUsd(1.725e9), '$1.73B'); assert.equal(shortUsd(2e9), '$2B')
})

test('one-line facts name the deal, its status and what each dollar figure measures', () => {
  const v = eventFact({ type: 'acquisition', text: 'Varonis and Proofpoint announced a definitive agreement for Proofpoint to acquire Varonis in an all-cash transaction valued at approximately $6.3 billion, or $49.75 per share.' })
  assert.equal(v.line, 'Proofpoint acquiring Varonis'); assert.equal(v.status, 'Announced'); assert.deepEqual(v.amount && [v.amount.text, v.amount.label], ['$6.3B', 'deal value'])
  const c = eventFact({ type: 'acquisition', text: 'Cyera completed its acquisition of Oasis Security.' })
  assert.equal(c.line, 'Cyera acquired Oasis Security'); assert.equal(c.status, 'Closed')
  const t = eventFact({ type: 'debt', text: 'Tenable entered into a credit agreement for a senior secured revolving credit facility of $400.0 million; the company had no outstanding revolving loans.' })
  assert.equal(t.line, 'Revolving credit line, none drawn'); assert.equal(t.amount?.label, 'available')
  const f = eventFact({ type: 'funding', text: 'HiddenLayer raised a $100 million Series B round led by Delta-v Capital, with participation from others.' })
  assert.equal(f.line, 'Series B · led by Delta-v Capital'); assert.equal(f.amount?.label, 'raised')
  assert.equal(eventFact({ type: 'exec-change', text: 'Timothy Regan appointed Chief Financial Officer of Delinea.' }).line, 'CFO appointed')
  assert.equal(eventFact({ type: 'exec-change', text: 'Form 8-K (Item 5.02) reporting a change in directors or certain officers, filed 2026-10-15.' }).line, 'Officer or director change (8-K)')
})

test('the front feed holds no routine filings or results, newest first', () => {
  assert.ok(feedChanges.every(item => !isLedgerItem(item)))
  const dates = feedChanges.map(i => i.date)
  assert.deepEqual(dates, dates.slice().sort().reverse())
  assert.equal(tileSnapshot('no-such-group'), '')
})
