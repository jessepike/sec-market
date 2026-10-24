import { test } from 'node:test'
import assert from 'node:assert/strict'
import { createHash } from 'node:crypto'
import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { verifyDaily } from '../scripts/verify-daily.mjs'

const canonical = x => Array.isArray(x) ? '[' + x.map(canonical).join(',') + ']' : x && typeof x === 'object' ? '{' + Object.keys(x).sort().map(k => JSON.stringify(k) + ':' + canonical(x[k])).join(',') + '}' : JSON.stringify(x)
const hash = x => createHash('sha256').update(typeof x === 'string' ? x : canonical(x)).digest('hex')

function fixture(t, change = () => {}, v2 = false) {
  const root = mkdtempSync(join(tmpdir(), 'smp-daily-gate-'))
  t.after(() => rmSync(root, { recursive: true, force: true }))
  mkdirSync(join(root, 'web/src/data/generated'), { recursive: true })
  mkdirSync(join(root, 'contracts'))
  const contract = { suppliers: [{ id: 'one', requiredFamilies: ['official_announcements'] }], sources: [{ supplierId: 'one', required: true, family: 'official_announcements' }], schedule: { overdueHours: 30 } }
  if (v2) {
    contract.version = 'market-daily-v2'
    contract.collection = { mode: 'daily_intake_with_separate_history' }
    Object.assign(contract.sources[0], { id: 'one:official', registration: 'verified' })
  }
  writeFileSync(join(root, 'contracts/market.json'), JSON.stringify(contract))
  const policy = hash(contract), runId = 'a'.repeat(64)
  const data = { schemaVersion: 1, enabled: true, contractSha256: policy, runId, events: [], evidence: [], supplierUpdates: {},
    coverage: { contractSha256: policy, runId, supplierCount: 1, requiredTasks: 1, successfulTasks: 1, gapTaskIds: [], complete: true,
      checkedAt: '2026-10-20T12:00:00Z', lastCollectionAt: '2026-10-20T12:00:00Z', overdueHours: 30,
      sources: [{ taskId: 'task-one', required: true, outcome: 'checked_no_change', registration: 'verified' }] } }
  if (v2) {
    const processing = { complete: false, inventoryDocuments: 10, reviewedDocuments: 2, pendingDocuments: 8,
      heldDocuments: 1, changedDocuments: 3, unknownDateDocuments: 2 }
    const historicalReview = { complete: false, inventoryDocuments: 100, reviewedDocuments: 10,
      pendingDocuments: 90, heldDocuments: 2 }
    Object.assign(data.coverage, { schemaVersion: 2, measure: 'daily_source_intake_v2',
      intake: { measure: 'daily_source_intake_v2', evaluated: true, status: 'collected',
        requiredTasks: 1, successfulTasks: 1, gapTaskIds: [], complete: true }, processing, historicalReview })
    Object.assign(data.coverage.sources[0], { measure: 'daily_source_intake_v2', sourceId: 'one:official',
      supplierId: 'one', family: 'official_announcements', outcome: 'checked', intakeOutcome: 'checked',
      processing: structuredClone(processing), historicalReview: structuredClone(historicalReview) })
  }
  change(data)
  data.snapshotSha256 = hash(data)
  const raw = JSON.stringify(data)
  writeFileSync(join(root, 'web/src/data/generated/dailyMarket.json'), raw)
  writeFileSync(join(root, 'web/src/data/generated/dailyMarket.seal.json'), JSON.stringify({ fileSha256: hash(raw), runId, contractSha256: policy }))
  return { root, web: join(root, 'web'), data }
}

test('a quiet source check can pass the envelope without inventing market events', t => {
  const f = fixture(t)
  assert.equal(verifyDaily(f.web).coverageComplete, true)
})
test('a completion flag cannot replace a missing source check', t => {
  const f = fixture(t, data => { data.coverage.sources[0].outcome = 'not_checked' })
  assert.throws(() => verifyDaily(f.web), /completion differs/)
})
test('a snapshot cannot silently shrink its supplier denominator', t => {
  const f = fixture(t, data => { data.coverage.supplierCount = 0 })
  assert.throws(() => verifyDaily(f.web), /denominator/)
})
test('editing data after validation invalidates its exact seal', t => {
  const f = fixture(t)
  writeFileSync(join(f.web, 'src/data/generated/dailyMarket.json'), JSON.stringify({ ...f.data, runId: 'b'.repeat(64) }))
  assert.throws(() => verifyDaily(f.web), /seal/)
})
test('a published statement must remain verbatim in its supporting excerpt', t => {
  const f = fixture(t, data => {
    data.events.push({ id: 'event', supplierId: 'one', rung: 1, text: 'Unsupported new statement', evidenceIds: ['proof'] })
    data.evidence.push({ id: 'proof', excerpt: 'The source says something different.' })
  })
  assert.throws(() => verifyDaily(f.web), /differs from supported source/)
})

test('v2 checked intake passes separately while processing and history remain unfinished', t => {
  const f = fixture(t, () => {}, true)
  const result = verifyDaily(f.web)
  assert.equal(result.coverageMeasure, 'daily_source_intake_v2')
  assert.equal(result.intakeComplete, true)
  assert.equal(result.processingComplete, false)
  assert.equal(result.historicalReviewComplete, false)
})

test('v2 rejects old outcome aliases, missing measures and contradictory review counts', t => {
  const mutations = [
    data => { data.coverage.sources[0].outcome = 'checked_no_change' },
    data => { data.coverage.intake.successfulTasks = 0 },
    data => { delete data.coverage.measure }, data => { delete data.coverage.processing },
    data => { data.coverage.schemaVersion = 1 }, data => { delete data.coverage.intake },
    data => { data.coverage.processing.complete = true },
    data => { data.coverage.processing.pendingDocuments = 7 },
    data => { data.coverage.sources[0].processing.pendingDocuments = 7 },
    data => { data.coverage.processing.heldDocuments = true },
    data => { data.coverage.sources[0].registration = 'candidate' },
    data => { data.coverage.sources[0].sourceId = 'other' },
    data => { data.coverage.intake.evaluated = false; data.coverage.intake.status = 'uncollected' },
  ]
  for (const mutate of mutations) assert.throws(() => verifyDaily(fixture(t, mutate, true).web), /Daily v2 coverage/)
})

function uncollected(data) {
  // Retain an independently sealed historical snapshot, never restamp it as a new check.
  const oldContract = { version: 'market-daily-v1' }
  const old = { schemaVersion: 1, enabled: true, contractSha256: hash(oldContract), runId: data.runId,
    events: [], evidence: [], supplierUpdates: {}, checkedAt: '2026-10-20T12:00:00Z',
    coverage: { schemaVersion: 1, checkedAt: '2026-10-20T12:00:00Z', lastCollectionAt: '2026-10-20T12:00:00Z' } }
  old.snapshotSha256 = hash(old)
  data.supersededPolicy = { contract: oldContract, contractSha256: hash(oldContract), snapshot: old, snapshotSha256: old.snapshotSha256 }
  data.checkedAt = old.checkedAt
  Object.assign(data.coverage, { complete: false, successfulTasks: 0, gapTaskIds: ['task-one'], validUntil: null })
  Object.assign(data.coverage.intake, { evaluated: false, status: 'uncollected', complete: false,
    successfulTasks: 0, gapTaskIds: ['task-one'] })
  for (const target of [data.coverage, data.coverage.sources[0]]) {
    target.processing = { complete: false, evaluated: false, status: 'uncollected', inventoryDocuments: 0,
      reviewedDocuments: 0, pendingDocuments: 0, heldDocuments: 0, changedDocuments: 0, unknownDateDocuments: 0 }
    target.historicalReview = { complete: false, evaluated: false, status: 'uncollected', inventoryDocuments: 0,
      reviewedDocuments: 0, pendingDocuments: 0, heldDocuments: 0 }
  }
  Object.assign(data.coverage.sources[0], { outcome: 'not_checked', intakeOutcome: 'not_checked' })
}

test('explicit uncollected v2 fixture preserves historical pins and times without intake credit', t => {
  const result = verifyDaily(fixture(t, uncollected, true).web)
  assert.equal(result.intakeComplete, false)
  assert.equal(result.processingComplete, false)
  assert.equal(result.historicalReviewComplete, false)
})

test('uncollected v2 cannot claim reviewed history, move old dates or change inherited facts', t => {
  const mutations = [
    data => { data.coverage.processing.evaluated = true },
    data => { data.coverage.historicalReview.complete = true },
    data => { data.coverage.validUntil = '2026-10-25T12:00:00Z' },
    data => { data.coverage.lastCollectionAt = '2026-10-24T12:00:00Z' },
    data => { data.supersededPolicy.contract.version = 'rewritten' },
    data => { data.supersededPolicy.snapshot.checkedAt = '2026-10-24T12:00:00Z' },
    data => { data.events.push({ id: 'invented' }) },
  ]
  for (const mutate of mutations) {
    const f = fixture(t, data => { uncollected(data); mutate(data) }, true)
    assert.throws(() => verifyDaily(f.web), /Daily v2 coverage/)
  }
})
