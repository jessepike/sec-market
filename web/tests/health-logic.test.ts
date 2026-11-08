import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { test } from 'node:test'
import { computeHealth } from '../src/data/healthLogic.ts'
import edgar from '../src/data/generated/edgarFacts.json' with { type: 'json' }
import health from '../src/data/generated/healthFacts.json' with { type: 'json' }

const fixture = JSON.parse(readFileSync(new URL('./fixtures/health/synthetic.json', import.meta.url), 'utf8'))

test('margins match the Python snapshot method on a year-to-date filer with a capex tag rename', () => {
  // Expected values come from web/scripts/health/compute.py run on the same facts.
  const { health: h, gaps, notes } = computeHealth(fixture.cik, fixture.quarters, fixture.companyFacts)
  assert.equal(h.operatingMargin?.value, -1.9)
  assert.equal(h.fcfMargin?.value, 23.9)
  assert.equal(h.operatingMargin?.periodEnd, '2026-07-31')
  assert.match(h.operatingMargin!.sourceUrl, /000000000126000031\/0000000001-26-000031-index\.htm$/)
  assert.deepEqual(gaps, [])
  assert.equal(notes.length, 1)
})

test('cash adds short-term investments and debt reads the filer\'s own tag on the quarter end', () => {
  const { health: h } = computeHealth(fixture.cik, fixture.quarters, fixture.companyFacts)
  assert.deepEqual([h.balance?.cash, h.balance?.debt, h.balance?.asOf], [2000, 1500, '2026-07-31'])
})

test('no borrowing tag on the quarter end keeps cash and marks debt as not tagged', () => {
  const facts = structuredClone(fixture.companyFacts)
  delete facts.facts['us-gaap'].ConvertibleNotesPayable
  const { health: h, notes } = computeHealth(fixture.cik, fixture.quarters, facts)
  assert.deepEqual([h.balance?.cash, h.balance?.debt], [2000, null])
  assert.ok(notes.includes('no borrowing tagged at the latest quarter end'))
})

test('every committed margin covers the same quarter as the revenue beside it', () => {
  for (const s of edgar.suppliers) {
    const h = (health.suppliers as Record<string, { operatingMargin: { periodEnd: string } | null }>)[s.id]
    if (!h?.operatingMargin) continue
    assert.equal(h.operatingMargin.periodEnd, s.quarters[0].periodEnd, s.id)
  }
})

test('a filer with old PP&E facts but current capex only under ProductiveAssets falls back to it', () => {
  const facts = structuredClone(fixture.companyFacts)
  const g = facts.facts['us-gaap']
  g.PaymentsToAcquireProductiveAssets.units.USD.push(...g.PaymentsToAcquirePropertyPlantAndEquipment.units.USD)
  g.PaymentsToAcquirePropertyPlantAndEquipment = { units: { USD: [{ start: '2021-02-01', end: '2022-01-31', val: 1, accn: 'x', form: '10-K', filed: '2022-03-01' }] } }
  const { health: h } = computeHealth(fixture.cik, fixture.quarters, facts)
  assert.ok(h.fcfMargin, 'falls back to PaymentsToAcquireProductiveAssets')
})

test('debt read from DebtInstrumentCarryingAmount when the usual tags are absent', () => {
  const facts = structuredClone(fixture.companyFacts)
  const g = facts.facts['us-gaap']
  delete g.ConvertibleNotesPayable
  g.DebtInstrumentCarryingAmount = { units: { USD: [{ end: '2026-07-31', val: 358, accn: '0000000001-26-000031', form: '10-Q', filed: '2026-08-27' }] } }
  assert.equal(computeHealth(fixture.cik, fixture.quarters, facts).health.balance?.debt, 358)
})
