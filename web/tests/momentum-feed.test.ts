import assert from 'node:assert/strict'
import { test } from 'node:test'
import { certifiedGrowth, domainMomentum, formatPoints } from '../src/data/tracker/momentum'
import { entriesInGroup, feedEntries, resultFact, statedAmount, tileSnapshot } from '../src/data/tracker/feed'
import { eventFact, filingStep, isFilingNotice, shortUsd } from '../src/data/tracker/eventFacts'
import { countedUnits, dealParent, eventGroups, quarterlyGrowth } from '../src/data/tracker/presentation'
import type { ChangeItem } from '../src/data/tracker/presentation'
import { signalAge, signalDate } from '../src/data/tracker/momentum'
import { trackerSuppliers } from '../src/data/tracker/suppliers'
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

const item = (over: Partial<ChangeItem>): ChangeItem => ({ id: 'x', supplierId: 'varonis', date: '2026-10-15', type: 'acquisition', text: '', evidenceIds: [], filings: [], ...over })

test('a filing notice is told apart from a sourced fact, and names the step it adds', () => {
  const notice = 'Form PREM14A reporting a preliminary proxy statement for a proposed merger, filed 2026-11-06.'
  assert.ok(isFilingNotice(notice))
  assert.ok(isFilingNotice('Form 8-K (Item 5.02) reporting a change in directors or certain officers, filed 2026-10-15.'))
  assert.ok(!isFilingNotice('Form 8-K (Item 2.03) reporting the creation of a direct financial obligation, filed 2026-10-16. The filing describes it as: “notes”'))
  assert.ok(!isFilingNotice('Varonis and Proofpoint announced a definitive agreement.'))
  assert.equal(filingStep(notice), 'Preliminary merger proxy filed')
})

test('a later merger proxy joins the deal it belongs to and is counted once', () => {
  const deal = item({ id: 'a', text: 'Varonis and Proofpoint announced a definitive agreement for Proofpoint to acquire Varonis in an all-cash transaction valued at approximately $6.3 billion.' })
  const proxy = item({ id: 'b', date: '2026-11-06', text: 'Form PREM14A reporting a preliminary proxy statement for a proposed merger, filed 2026-11-06.' })
  const other = item({ id: 'c', supplierId: 'okta', date: '2026-11-06', text: 'Form PREM14A reporting a preliminary proxy statement for a proposed merger, filed 2026-11-06.' })
  assert.equal(dealParent(proxy, [deal, proxy])?.id, 'a')
  assert.equal(dealParent(deal, [deal, proxy]), null)
  assert.equal(dealParent(other, [deal, proxy, other]), null)
  assert.equal(countedUnits([deal, proxy]).length, 1)
  assert.equal(countedUnits([deal, proxy, other]).length, 2)
})

test('leadership and funding lines name the person or investor only when the text does', () => {
  const cro = eventFact({ type: 'exec-change', text: 'appointed industry veteran Robert Ruelas as Chief Revenue Officer (CRO)' })
  assert.equal(cro.line, 'CRO appointed'); assert.equal(cro.detail, 'Robert Ruelas')
  assert.equal(eventFact({ type: 'exec-change', text: 'Axonius named Joe Diamond permanent CEO; co-founder Dean Sysman moved to executive chairman.' }).detail, undefined)
  assert.equal(eventFact({ type: 'exec-change', text: 'promoted Sterling Parker to Chief Customer Officer (CCO)' }).line, 'Promoted Sterling Parker to Chief Customer Officer (CCO)')
  assert.equal(eventFact({ type: 'funding', text: 'Ontario Teachers’ Pension Plan has also agreed to make an investment into Proofpoint in connection with the transaction.' }).line, 'Investment from Ontario Teachers’ Pension Plan')
})

test('a result states revenue and growth from the SEC series', () => {
  const supplier = trackerSuppliers.find(s => s.edgarId && quarterlyGrowth(s.edgarId).length > 1)!
  const series = quarterlyGrowth(supplier.edgarId!)
  const last = series.at(-1)!
  const fact = resultFact(item({ supplierId: supplier.id, type: 'filing', filings: [{ supplierId: supplier.id, periodEnd: last.periodEnd, filedDate: '2026-01-01', form: '10-Q', value: last.value, sourceUrl: 'https://www.sec.gov/' }] }))!
  assert.match(fact.line, /^Revenue \$[\d.]+[MB]$/)
  assert.equal(fact.amount?.label, 'year over year'); assert.equal(fact.amount?.value, last.growth)
  assert.match(fact.detail!, new RegExp(`the quarter before · quarter ended ${last.periodEnd}$`))
  assert.equal(resultFact(item({ supplierId: supplier.id, type: 'results' })), null)
})

test('the front feed is newest first, never leads with a filing notice, and the tiles count its entries', () => {
  const dates = feedEntries.map(e => e.date)
  assert.deepEqual(dates, dates.slice().sort().reverse())
  assert.ok(feedEntries.every(e => !isFilingNotice(e.primary.text) || e.groupId === 'results'))
  assert.equal(eventGroups.reduce((n, g) => n + entriesInGroup(g.id).length, 0), feedEntries.length)
  assert.equal(tileSnapshot('no-such-group'), '')
})

test('signal age is in whole months or years, and a month-only date counts from its first day', () => {
  assert.equal(signalAge('2026-10-20', '2026-11-09'), 'this month')
  assert.equal(signalAge('2026-07-01', '2026-11-09'), '4 months ago')
  assert.equal(signalAge('2021-07-13', '2026-11-09'), '5 years ago')
  const s = { lastRound: { date: '2024-03', stage: 'Growth', amount: '$60M', evidenceIds: [] } } as unknown as (typeof trackerSuppliers)[number]
  assert.equal(signalDate(s), '2024-03-01'); assert.equal(signalDate(s, '2026-02-01'), '2026-02-01')
})
