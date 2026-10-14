import assert from 'node:assert/strict'
import { test } from 'node:test'
import { requiredFieldGroups, supportedFieldStatus, validateSupplierChecks, verifyClaimSources } from '../src/data/tracker/coverage'
import type { SupplierCheck, SourceCheck } from '../src/data/tracker/coverage'
import { assessCoverage } from '../../scripts/refresh-health.mjs'
import { verifyDataFile } from '../scripts/verify-collector-edits'

const now = new Date('2026-10-14T18:00:00Z')
const sources: SourceCheck[] = ['https://example.com/release', 'https://example.com/news'].map(url => ({ url, checkedAt: now.toISOString(), status: 'ok', sha256: 'a'.repeat(64) }))
const field: SupplierCheck['fields'][number] = { field: 'headlineMetric', status: 'checked-no-change', sourceUrls: [sources[0].url], discoverySourceUrls: [sources[1].url], reason: 'Release checked and no newer disclosure on newsroom.' }
test('a successful old release without current discovery cannot establish currentness', () => {
  assert.equal(verifyClaimSources({ ...field, discoverySourceUrls: [] }, sources, [sources[0].url]), 'No hashed current company or parent discovery check; retained claim is not verified current.')
  assert.equal(verifyClaimSources(field, sources, [sources[0].url]), null)
})
test('a filings index alone cannot verify the primary document supporting a displayed claim', () => {
  assert.match(verifyClaimSources({ ...field, sourceUrls: [sources[1].url] }, sources, [sources[0].url])!, /primary document/)
  assert.equal(supportedFieldStatus(field, sources.map(s => ({ ...s, sha256: undefined }))), 'not-checked')
})
test('duplicate suppliers and missing field groups are rejected', () => {
  const check: SupplierCheck = { supplierId: 'example', checkedAt: now.toISOString(), sourceChecks: sources, fields: requiredFieldGroups.map(name => ({ ...field, field: name })) }
  assert.doesNotThrow(() => validateSupplierChecks([check], ['example'], now.getTime()))
  assert.throws(() => validateSupplierChecks([check, check], ['example'], now.getTime()), /duplicated/)
  assert.throws(() => validateSupplierChecks([{ ...check, fields: check.fields.slice(1) }], ['example'], now.getTime()), /seven field/)
  assert.throws(() => validateSupplierChecks([{ ...check, checkedAt: '2026-10-12T00:00:00Z' }], ['example'], now.getTime()), /stale/)
})
test('monitor distinguishes current complete, incomplete and overdue source receipts', () => {
  const coverage = { checkedAt: now.toISOString(), allSuppliersAttempted: true, supplierChecksReceived: 74, supplierCount: 74, state: 'complete', summary: { failed: 0, 'not-checked': 0 } }
  assert.equal(assessCoverage(coverage, now).healthy, false)
  assert.equal(assessCoverage({ ...coverage, state: 'incomplete', summary: { failed: 3, 'not-checked': 2 } }, now).healthy, false)
  assert.match(assessCoverage(coverage, new Date('2026-10-16T18:00:00Z')).reason, /overdue/)
  assert.equal(assessCoverage({ ...coverage, allSuppliersAttempted: false }, now).healthy, false)
})
test('collector guard permits literal facts while rejecting executable data or outside edits', () => {
  const before = 'export const records = [{ value: "retained" }]\nexport const reviewedCode = 1\n'
  assert.doesNotThrow(() => verifyDataFile(before, before.replace('retained', 'new sourced fact'), 'records'))
  assert.throws(() => verifyDataFile(before, before.replace('"retained"', 'fetch("https://example.com")'), 'records'), /data literals/)
  assert.throws(() => verifyDataFile(before, before.replace('reviewedCode = 1', 'reviewedCode = 2'), 'records'), /outside/)
})
