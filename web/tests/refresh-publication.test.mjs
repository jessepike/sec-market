import { test } from 'node:test'
import assert from 'node:assert/strict'
import { digest, evaluateRefresh, publicationDecision } from '../scripts/refresh-publication-gate.mjs'

const now = Date.parse('2026-10-14T20:00:00Z')
const at = new Date(now).toISOString()
const contract = { version: 'test-v1', supplierIds: ['one'], groups: { identity: 720, events: 24 }, exclusions: {}, undisclosedAnswers: {} }
const fields = Object.keys(contract.groups).map(group => ({ supplierId: 'one', field: group, value: group === 'events' ? [] : 'One', status: 'checked-no-change' }))
const coverage = { allSuppliersAttempted: true, supplierCount: 1, supplierChecksReceived: 1, fields }
const source = { url: 'https://example.com/primary', sha256: 'a'.repeat(64), checkedAt: at }
const verification = { contractVersion: 'test-v1', verifiedClaims: fields.map(f => ({ key: `one.${f.field}`, verifiedAt: at, result: 'verified-value', valueSha256: digest([[f.field, f.value]]), discovery: { ...source, scope: 'company-or-parent', coveredThrough: at }, evidence: [{ ...source, method: 'primary-content-match', locator: 'Dated release paragraph 1', excerpt: 'Specific substantive claim checked against the primary content.' }] })) }
const evaluate = (c = coverage, v = verification, policy = contract, time = now) => evaluateRefresh(policy, c, v, time)

test('verified no-change counts; fixed inventory is independent of candidate leaf count', () => {
  assert.deepEqual({ complete: evaluate().complete, required: evaluate().required, verified: evaluate().verified }, { complete: true, required: 2, verified: 2 })
  assert.equal(evaluate({ ...coverage, fields: fields.slice(1) }).complete, false)
  assert.equal(evaluate({ ...coverage, supplierCount: 0, supplierChecksReceived: 0 }).complete, false)
})
test('HTTP retrieval, missing proof and a completion label cannot certify refreshed claims', () => {
  assert.equal(evaluate({ ...coverage, state: 'complete' }, { ...verification, verifiedClaims: [] }).complete, false)
  const httpOnly = structuredClone(verification);httpOnly.verifiedClaims[0].evidence[0].method = 'http-success'
  assert.equal(evaluate(coverage, httpOnly).complete, false)
})
test('deleting a required qualifier fails even with a new value hash and verification label', () => {
  const policy = { ...contract, pinnedFields: { 'one.identity': ['identity.qualifier'] } }
  assert.equal(evaluate(coverage, verification, policy).complete, false)
})
test('failed, unchecked and undisclosed required claims block without changing denominator', () => {
  for (const status of ['failed', 'not-checked', 'unavailable', 'not-applicable']) {
    const result = evaluate({ ...coverage, fields: fields.map((f, i) => i ? f : { ...f, status }) })
    assert.equal(result.complete, false);assert.equal(result.required, 2)
  }
})
test('an explicit reviewed undisclosed-answer policy still requires substantive disclosure proof', () => {
  const c = { ...coverage, fields: fields.map((f, i) => i ? f : { ...f, status: 'unavailable' }) }
  const policy = { ...contract, undisclosedAnswers: { 'one.identity': { reason: 'Fixture disclosure-status question permits this answer.', reviewedAt: at } } }
  assert.equal(evaluate(c, verification, policy).complete, false)
  const v = structuredClone(verification);v.verifiedClaims[0].result = 'verified-undisclosed'
  assert.equal(evaluate(c, v, policy).complete, true)
})
test('retries do not renew stale verification, discovery or exact-value proof', () => {
  assert.equal(evaluate(coverage, verification, contract, now + 25 * 3600000).complete, false)
  const retry = { ...coverage, checkedAt: new Date(now + 25 * 3600000).toISOString() }
  assert.equal(evaluate(retry, verification, contract, now + 25 * 3600000).complete, false)
  const v = structuredClone(verification);v.verifiedClaims[1].discovery.coveredThrough = '2026-10-10T20:00:00Z'
  assert.equal(evaluate(coverage, v).complete, false)
  assert.equal(evaluate({ ...coverage, fields: fields.map((f, i) => i ? { ...f, value: ['new'] } : f) }).complete, false)
})
test('unchanged legacy snapshot retains unestablished date; incomplete candidate is blocked', () => {
  const baseline = { files: { 'facts.json': 'old' }, lastCompleteRefreshAt: null }
  const failed = { complete: false }
  assert.equal(publicationDecision(baseline, { 'facts.json': 'old' }, failed).allowed, true)
  const held = publicationDecision(baseline, { 'facts.json': 'new' }, failed)
  assert.equal(held.allowed, false);assert.equal(held.lastCompleteRefreshAt, null)
  assert.equal(publicationDecision(baseline, { 'facts.json': 'new' }, evaluate()).refreshed, true)
})
