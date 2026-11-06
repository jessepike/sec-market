import assert from 'node:assert/strict'
import { describe, it } from 'node:test'
import originals from '../src/data/tracker/originals.json' with { type: 'json' }
import market from '../../contracts/market.json' with { type: 'json' }
import { trackerDomainIds } from '../src/data/tracker/domains.ts'
import { trackerSuppliers } from '../src/data/tracker/suppliers.ts'
import { onboardingEvidence, onboardingRows, onboardingSuppliers, showOnboarding } from '../src/data/tracker/onboarding.ts'

// D-138: onboarding suppliers carry sourced seed records, render on preview
// builds only, and never join the tracker, the contract or any count.
describe('onboarding suppliers', () => {
  it('stay hidden outside a Vercel preview build', () => {
    assert.equal(showOnboarding, process.env.VERCEL_ENV === 'preview')
  })

  it('are collected under the contract but not yet in the tracker or the originals', () => {
    const registered = new Set(market.suppliers.map(s => s.id))
    for (const supplier of onboardingSuppliers) assert.ok(registered.has(supplier.id), `${supplier.id} is not in the contract`)
    const live = new Set([...trackerSuppliers.map(s => s.id), ...originals.suppliers.map(s => s.id)])
    for (const supplier of onboardingSuppliers) assert.ok(!live.has(supplier.id), `${supplier.id} is already live`)
    const liveEvidence = new Set(originals.evidence.map(e => e.id))
    for (const record of onboardingEvidence) assert.ok(!liveEvidence.has(record.id), `${record.id} collides with live evidence`)
    assert.equal(new Set(onboardingSuppliers.map(s => s.id)).size, onboardingSuppliers.length)
  })

  it('cite a specific, dated source for every fact', () => {
    const evidence = new Map(onboardingEvidence.map(e => [e.id, e]))
    for (const supplier of onboardingSuppliers) {
      assert.ok(supplier.domainIds.length > 0 && supplier.domainIds.every(id => trackerDomainIds.includes(id)), `${supplier.id} domain`)
      const fields = [supplier.revenue?.latest, supplier.headlineMetric, supplier.lastRound, supplier.ownership].filter(Boolean)
      assert.ok(fields.length > 0, `${supplier.id} has no facts`)
      for (const field of fields) {
        assert.ok(field!.evidenceIds.length > 0, `${supplier.id} fact without evidence`)
        for (const id of field!.evidenceIds) {
          const record = evidence.get(id)
          assert.ok(record, `${supplier.id} cites missing ${id}`)
          assert.match(record.canonicalUrl, /^https:\/\/[^/]+\/.+/, `${id} must link a specific document`)
          assert.ok(record.excerpt.trim().length > 20, `${id} needs a verbatim excerpt`)
          assert.match(record.publicationDate, /^\d{4}-\d{2}-\d{2}$/)
          assert.match(record.retrievedAt, /^\d{4}-\d{2}-\d{2}$/)
        }
      }
    }
  })

  it('target tier 1 only for SEC filers', () => {
    for (const row of onboardingRows) assert.equal(row.targetTier === 1, Boolean(row.supplier.cik), row.supplier.id)
  })

  it('keep machine text free of em dashes', () => {
    for (const row of onboardingRows) for (const fact of row.facts) assert.ok(!fact.includes('—'), fact)
  })
})

describe('onboarding hold on daily data', () => {
  it('keeps an onboarding supplier event and its evidence out of the expected public views', async () => {
    const { expectedCurrentFacts, loadCurrentFactInputs } = await import('../scripts/verify-current-facts.ts')
    const inputs = loadCurrentFactInputs()
    const evidence = { id: 'EV-synthetic-onboarding', title: 'Synthetic', organization: 'F5, Inc.', publicationDate: '2026-11-01',
      economicPeriod: 'N/A', canonicalUrl: 'https://www.f5.com/company/news/press-releases/synthetic', excerpt: 'Synthetic event text for the hold test.',
      sourceClass: 'IR', interpretation: '', limitations: '', conflictingEvidenceIds: [], artifactLabel: 'test', tags: [] }
    const event = { id: 'EV-daily-synthetic', supplierId: 'f5', date: '2026-11-01', type: 'results' as const,
      text: 'Synthetic event text for the hold test.', evidenceIds: [evidence.id], rung: 1 as const }
    const daily = { ...inputs.daily, enabled: true, events: [...(inputs.daily.enabled ? inputs.daily.events : []), event],
      evidence: [...(inputs.daily.enabled ? inputs.daily.evidence : []), evidence], supplierUpdates: inputs.daily.enabled ? inputs.daily.supplierUpdates : {} }
    const views = expectedCurrentFacts({ ...inputs, daily })
    assert.ok(!views.retainedTrackerEvents.some(e => e.id === event.id))
    assert.ok(!views.evidenceRecords.some(e => e.id === evidence.id))
    const open = expectedCurrentFacts({ ...inputs, daily, onboardingSupplierIds: [] })
    assert.ok(open.retainedTrackerEvents.some(e => e.id === event.id))
  })
})
