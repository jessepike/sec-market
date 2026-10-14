import { test } from 'node:test'
import assert from 'node:assert/strict'
import { mkdtempSync, mkdirSync, writeFileSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { createHash } from 'node:crypto'
import { verifyFrozenData, appOnlyDecision, publicAttempt, diagnosticPreview } from '../scripts/app-release.mjs'

test('code-only release permits unchanged published data and does not advance completion date', () => {
  const snapshot = { unchanged: true, sourceRevision: 'accepted', lastCompleteRefreshAt: null }
  const publication = { publishedSourceRevision: 'accepted', lastCompleteRefreshAt: null }
  assert.deepEqual(appOnlyDecision(snapshot, publication), { allowed: true, releaseKind: 'app-only', dataUpdated: false, snapshotRevision: 'accepted', lastCompleteRefreshAt: null })
  assert.throws(() => appOnlyDecision(snapshot, { ...publication, lastCompleteRefreshAt: '2026-10-14' }), /cannot change/)
  assert.throws(() => appOnlyDecision({ ...snapshot, unchanged: false }, publication), /cannot change/)
})

test('baseline hash gate rejects changed, dropped and newly added published facts', () => {
  const root = mkdtempSync(join(tmpdir(), 'smp-frozen-'))
  try {
    mkdirSync(join(root, 'src/data'), { recursive: true })
    const file = 'src/data/facts.json', bytes = '{"value":12,"period":"2026-06-30"}'
    writeFileSync(join(root, file), bytes)
    const manifest = { sourceRevision: 'accepted', lastCompleteRefreshAt: null, dataFiles: { [file]: createHash('sha256').update(bytes).digest('hex') } }
    assert.equal(verifyFrozenData(root, manifest).unchanged, true)
    writeFileSync(join(root, file), bytes.replace('12', '13'))
    assert.throws(() => verifyFrozenData(root, manifest), /Published data changed/)
    writeFileSync(join(root, file), bytes)
    writeFileSync(join(root, 'src/data/extra.json'), '{}')
    assert.throws(() => verifyFrozenData(root, manifest), /inventory changed/)
    rmSync(join(root, 'src/data/extra.json'));rmSync(join(root, file))
    assert.throws(() => verifyFrozenData(root, manifest), /inventory changed/)
  } finally { rmSync(root, { recursive: true, force: true }) }
})

test('failed attempt receipt is independent of published data and omits candidate financial values', () => {
  const coverage = { supplierChecksReceived: 74, supplierCount: 74, summary: { failed: 248 }, fields: [{ supplierId: 'one', field: 'revenue.latest.value', value: '$NEW', status: 'failed' }] }
  const receipt = publicAttempt(coverage, { lastAttemptAt: '2026-10-14T19:30:00Z', lastAttemptState: 'blocked', lastCompleteRefreshAt: null, publishedSourceRevision: 'accepted' })
  assert.equal(receipt.published, false);assert.equal(receipt.lastCompleteRefreshAt, null)
  assert.equal(receipt.lastAttemptAt, '2026-10-14T19:30:00Z');assert.deepEqual(receipt.failedSupplierIds, ['one'])
  assert.doesNotMatch(JSON.stringify(receipt), /\$NEW/)
})

test('production can never acquire diagnostic data through the local preview flag', () => {
  assert.equal(diagnosticPreview({ VERCEL_ENV: 'production', VERCEL: '1', SMP_APP_PREVIEW: '1' }), false)
  assert.equal(diagnosticPreview({ VERCEL: '1', SMP_APP_PREVIEW: '1' }), false)
  assert.equal(diagnosticPreview({ VERCEL_ENV: 'preview', VERCEL: '1' }), true)
  assert.equal(diagnosticPreview({ SMP_APP_PREVIEW: '1' }), true)
  assert.equal(diagnosticPreview({}), false)
})
