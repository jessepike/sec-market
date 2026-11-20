import assert from 'node:assert/strict'
import { describe, it } from 'node:test'
import onboarding from '../src/data/tracker/onboarding.json' with { type: 'json' }
import { knownDomains, pendingDomains, trackerDomains } from '../src/data/tracker/domains.ts'
import { splitOnboarding } from '../src/data/tracker/graduation.ts'
import { knownVendorNames, partnerLine, type VendorPartner } from '../src/data/tracker/partners.ts'

const suppliers = onboarding.suppliers as Array<{ id: string; domainIds: string[]; partners?: VendorPartner[] }>
const evidence = new Map((onboarding.evidence as Array<{ id: string; canonicalUrl: string; excerpt: string; publicationDate: string }>).map(e => [e.id, e]))

// D-153 vendor pairing v1: each tag is a dated vendor statement, cited, about a vendor on the site.
describe('vendor partner tags', () => {
  const tags = suppliers.flatMap(s => (s.partners ?? []).map(p => ({ supplier: s.id, ...p })))

  it('exist for the providers that vendors named', () => {
    assert.ok(tags.length >= 8)
  })

  for (const tag of tags) {
    it(`${tag.supplier} / ${tag.vendorId}: known vendor, dated, with evidence that names the provider`, () => {
      assert.ok(knownVendorNames.has(tag.vendorId), `${tag.vendorId} is not a supplier on the site`)
      assert.match(tag.date, /^\d{4}-\d{2}-\d{2}$/)
      assert.ok(tag.program.trim().length > 0 && /\b20\d\d\b/.test(tag.program), 'program names its year')
      assert.ok(tag.evidenceIds.length > 0, 'no evidence')
      for (const id of tag.evidenceIds) {
        const record = evidence.get(id)
        assert.ok(record, `missing evidence ${id}`)
        assert.match(record.canonicalUrl, /^https:\/\/[^/]+\/.+/)
        assert.equal(record.publicationDate, tag.date)
        assert.ok(record.excerpt.trim().length > 10)
      }
    })
  }

  it('render as one plain line with a source link', () => {
    const line = partnerLine('bitsio')
    assert.equal(line?.text, 'Named partner of: Splunk (2026 Services Partner of the Year, AMER)')
    assert.equal(line?.sources.length, 1)
    assert.equal(partnerLine('insight'), null)
  })

  it('never come from ePlus partner data', () => {
    for (const tag of tags) for (const id of tag.evidenceIds) assert.ok(!/eplus\.com/.test(evidence.get(id)!.canonicalUrl), id)
  })
})

describe('security solution providers domain', () => {
  it('stays pending, so production shows no new domain, while its companies are onboarding', () => {
    assert.ok(pendingDomains.some(d => d.id === 'solution-providers'))
    assert.ok(!trackerDomains.some(d => d.id === 'solution-providers'))
    assert.ok(knownDomains.some(d => d.id === 'solution-providers'))
  })

  it('releases its companies only when three of them have graduated', () => {
    const marked = (ids: string[]) => Object.fromEntries(ids.map(id => [id, { date: '2026-11-21', runIds: [] }]))
    const file = onboarding as unknown as Parameters<typeof splitOnboarding>[0]
    const two = splitOnboarding({ ...file, graduated: { ...(file.graduated ?? {}), ...marked(['cdw', 'insight']) } })
    assert.ok(!two.graduatedIds.has('cdw') && two.heldIds.includes('cdw'))
    const three = splitOnboarding({ ...file, graduated: { ...(file.graduated ?? {}), ...marked(['cdw', 'insight', 'eplus']) } })
    assert.ok(three.graduatedIds.has('cdw') && three.graduatedIds.has('eplus'))
  })
})
