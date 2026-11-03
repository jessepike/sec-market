import assert from 'node:assert/strict'
import { test } from 'node:test'
import { checkInvariants, checkSiteInvariants, liveSiteData } from '../src/data/tracker/invariants'
import type { SiteData } from '../src/data/tracker/invariants'
import type { ChangeItem, CountedUnit, GrowthRow } from '../src/data/tracker/presentation'

test('the live site data passes every invariant', () => {
  assert.deepEqual(checkSiteInvariants(), [])
})

const item = (id: string, supplierId: string, date: string, type: string, text = 'text', evidenceIds: string[] = ['e1']) =>
  ({ id, supplierId, date, type, text, evidenceIds, filings: [] }) as unknown as ChangeItem
const unit = (groupId: string, items: ChangeItem[]): CountedUnit => ({ key: items[0].id, groupId, date: items[0].date, items })

function clean(): SiteData {
  const a = item('a', 'alpha', '2026-10-20', 'results')
  const b = item('b', 'beta', '2026-06-10', 'results')
  return {
    asOf: '2026-11-03', monthChanges: [a], yearChanges: [a, b],
    monthUnits: [unit('results', [a])], yearUnits: [unit('results', [a]), unit('results', [b])],
    growthRows: [], dealLinks: {}, supplierNames: { alpha: ['Alpha'], beta: ['Beta'] },
    sourceUrl: id => (id === 'e1' ? 'https://example.com/x' : undefined), filingDates: [],
  }
}
const rules = (data: SiteData, now = '2026-11-03') => checkInvariants(data, now).map(v => v.rule)

test('a clean crafted data set passes', () => assert.deepEqual(rules(clean()), []))

test('rule 1 fires when a tile count disagrees with the change log', () => {
  const data = clean()
  const extra = item('c', 'alpha', '2026-10-21', 'results')
  data.monthChanges = [...data.monthChanges, extra] // a row the type filters never show
  assert.ok(rules(data).includes('tile-count-matches-list'))
})

test('rule 1 fires when a 12-month event falls outside the grid', () => {
  const data = clean()
  const old = item('old', 'alpha', '2025-01-05', 'results')
  data.yearUnits = [...data.yearUnits, unit('results', [old])]
  assert.ok(rules(data).includes('tile-count-matches-list'))
})

test('rule 2 fires when one deal is counted twice', () => {
  const data = clean()
  const x = item('x', 'alpha', '2026-10-20', 'acquisition', 'Alpha to acquire Beta')
  const y = item('y', 'beta', '2026-10-20', 'acquisition', 'Beta agrees to be acquired by Alpha')
  data.yearChanges = [x, y]; data.yearUnits = [unit('ownership', [x]), unit('ownership', [y])]
  assert.ok(rules(data).includes('one-deal-counts-once'))
})

test('rule 2 fires for two stages linked in deals.ts but counted separately', () => {
  const data = clean()
  const x = item('x', 'alpha', '2026-01-15', 'acquisition')
  const y = item('y', 'alpha', '2026-03-15', 'acquisition')
  data.dealLinks = { x: 'd', y: 'd' }
  data.yearChanges = [x, y]; data.yearUnits = [unit('ownership', [x]), unit('ownership', [y])]
  assert.ok(rules(data).includes('one-deal-counts-once'))
})

test('rule 3 fires when yen growth has no currency code', () => {
  const data = clean()
  const supplier = { id: 'trend', name: 'Trend', revenue: { latest: { growthBasis: 'JPY net sales; year over year' } } }
  data.growthRows = [{ supplier, latest: 5, prior: null, currency: null } as unknown as GrowthRow]
  assert.ok(rules(data).includes('non-usd-growth-has-currency'))
})

test('rule 4 fires for a future event date and a future filing date', () => {
  const data = clean()
  data.yearChanges = [item('f', 'alpha', '2026-12-01', 'results')]
  data.filingDates = [{ supplierId: 'alpha', filedDate: '2027-01-01' }]
  const found = rules(data).filter(r => r === 'no-future-dates')
  assert.equal(found.length, 2)
})

test('rule 5 fires for an event with no source URL', () => {
  const data = clean()
  data.yearChanges = [item('n', 'alpha', '2026-10-01', 'results', 'text', [])]
  assert.ok(rules(data).includes('every-event-has-source'))
})

test('live data builder returns the page windows', () => {
  const data = liveSiteData()
  assert.ok(data.yearChanges.length >= data.monthChanges.length)
})
