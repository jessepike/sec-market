import assert from 'node:assert/strict'
import { describe, it } from 'node:test'
import { searchCompanies } from '../src/data/tracker/search.ts'
import { trackerSuppliers } from '../src/data/tracker/suppliers.ts'
import type { TrackerSupplier } from '../src/data/tracker/suppliers.ts'

describe('company search', () => {
  it('finds company names and tickers regardless of case and surrounding spaces', () => {
    assert.deepEqual(searchCompanies(trackerSuppliers, '  vArOnIs  ').map(company => company.id), ['varonis'])
    assert.deepEqual(searchCompanies(trackerSuppliers, 'VRNS').map(company => company.id), ['varonis'])
    assert.deepEqual(searchCompanies(trackerSuppliers, 'pAnW').map(company => company.id).sort(), ['panw', 'panw-xsiam'])
  })

  it('matches multiple words with punctuation without duplicating companies across domains', () => {
    assert.deepEqual(searchCompanies(trackerSuppliers, 'Palo-Alto   Networks').map(company => company.id).sort(), ['panw', 'panw-xsiam'])
    const ids = searchCompanies(trackerSuppliers, 'security').map(company => company.id)
    assert.ok(ids.length > 1)
    assert.equal(new Set(ids).size, ids.length)
    assert.deepEqual(searchCompanies(trackerSuppliers, 'Varonis Palo'), [])
  })

  it('uses aliases already registered against the same company id', () => {
    const fixture: TrackerSupplier = { id: 'arctic-wolf', name: 'Fixture legal name', domainIds: [], kind: 'private' }
    assert.deepEqual(searchCompanies([fixture], 'Arctic Wolf Networks'), [fixture])
    assert.deepEqual(searchCompanies([{ ...fixture, id: 'unregistered' }], 'Arctic Wolf Networks'), [])
  })

  it('keeps empty and unknown queries empty and does not mutate source order', () => {
    const before = trackerSuppliers.map(company => company.id)
    for (const query of ['', '   ', '!!!', 'not-a-tracked-company-123']) assert.deepEqual(searchCompanies(trackerSuppliers, query), [])
    searchCompanies(trackerSuppliers, 'security')
    assert.deepEqual(trackerSuppliers.map(company => company.id), before)
  })
})
