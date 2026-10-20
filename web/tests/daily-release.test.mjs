import { test } from 'node:test'
import assert from 'node:assert/strict'
import { createHash } from 'node:crypto'
import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { verifyDaily } from '../scripts/verify-daily.mjs'

const canonical = x => Array.isArray(x) ? '[' + x.map(canonical).join(',') + ']' : x && typeof x === 'object' ? '{' + Object.keys(x).sort().map(k => JSON.stringify(k) + ':' + canonical(x[k])).join(',') + '}' : JSON.stringify(x)
const hash = x => createHash('sha256').update(typeof x === 'string' ? x : canonical(x)).digest('hex')

function fixture(t, change = () => {}) {
  const root = mkdtempSync(join(tmpdir(), 'smp-daily-gate-'))
  t.after(() => rmSync(root, { recursive: true, force: true }))
  mkdirSync(join(root, 'web/src/data/generated'), { recursive: true })
  mkdirSync(join(root, 'contracts'))
  const contract = { suppliers: [{ id: 'one', requiredFamilies: ['official_announcements'] }], sources: [{ supplierId: 'one', required: true, family: 'official_announcements' }], schedule: { overdueHours: 30 } }
  writeFileSync(join(root, 'contracts/market.json'), JSON.stringify(contract))
  const policy = hash(contract), runId = 'a'.repeat(64)
  const data = { schemaVersion: 1, enabled: true, contractSha256: policy, runId, events: [], evidence: [], supplierUpdates: {},
    coverage: { contractSha256: policy, runId, supplierCount: 1, requiredTasks: 1, successfulTasks: 1, gapTaskIds: [], complete: true,
      checkedAt: '2026-10-20T12:00:00Z', lastCollectionAt: '2026-10-20T12:00:00Z', overdueHours: 30,
      sources: [{ taskId: 'task-one', required: true, outcome: 'checked_no_change', registration: 'verified' }] } }
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
