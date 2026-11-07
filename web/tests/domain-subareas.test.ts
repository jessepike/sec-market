import assert from 'node:assert/strict'
import { describe, it } from 'node:test'
import { trackerDomains } from '../src/data/tracker/domains.ts'
import { domainMomentum } from '../src/data/tracker/momentum.ts'
import { onboardingSuppliers } from '../src/data/tracker/onboarding.ts'
import { trackerSuppliers } from '../src/data/tracker/suppliers.ts'

// AI security is split into named parts and shows no revenue bars (owner, 2026-11-07).
describe('domain sub-areas', () => {
  const all = [...trackerSuppliers, ...onboardingSuppliers]
  for (const domain of trackerDomains.filter(d => d.subareas)) {
    it(`${domain.id}: every listed company is in the domain, once`, () => {
      const ids = domain.subareas!.flatMap(a => a.supplierIds)
      assert.equal(new Set(ids).size, ids.length)
      for (const id of ids) {
        const s = all.find(x => x.id === id)
        assert.ok(s, `${id} is not a tracker or onboarding supplier`)
        assert.ok(s.domainIds.includes(domain.id), `${id} is not in ${domain.id}`)
      }
    })
    it(`${domain.id}: every tracker company in the domain has a sub-area`, () => {
      const placed = new Set(domain.subareas!.flatMap(a => a.supplierIds))
      for (const s of all.filter(x => x.domainIds.includes(domain.id))) assert.ok(placed.has(s.id), `${s.id} has no sub-area`)
    })
  }
  it('AI security shows no revenue bars and lists Palo Alto Networks by what it bought', () => {
    const ai = domainMomentum().find(d => d.id === 'ai-security')!
    assert.equal(ai.revenueBars, false)
    assert.equal(ai.rows.length, 0)
    const panw = ai.others.find(o => o.supplier.id === 'panw')
    assert.equal(panw?.fact, 'Public company. Bought Protect AI')
    assert.deepEqual(ai.otherGroups.map(g => g.id), ['ai-usage', 'ai-apps-models', 'ai-agents'])
  })
})
