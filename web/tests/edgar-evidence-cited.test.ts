import assert from 'node:assert/strict'
import test from 'node:test'
import { edgarRevenueEvidence } from '../src/data/tracker/edgarRevenue.ts'
import { trackerSuppliers } from '../src/data/tracker/suppliers.ts'

// The EDGAR collection can hold filers the page does not read SEC revenue for (D-138).
// Their figures must not become evidence records, or the release integrity check counts them as orphans.
test('every SEC revenue evidence record belongs to a filer a listed supplier points at', () => {
  const cited = new Set(trackerSuppliers.map((s) => s.edgarId).filter(Boolean))
  assert.ok(edgarRevenueEvidence.length > 0)
  for (const record of edgarRevenueEvidence) {
    const owner = [...cited].find((id) => record.id.startsWith(`TR-edgar-revenue-${id}-`))
    assert.ok(owner, `${record.id} has no listed supplier`)
  }
})
