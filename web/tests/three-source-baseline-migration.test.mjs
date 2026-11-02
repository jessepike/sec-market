import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { verifyThreeBaselineMigration, verifyThreePolicyTransition, THREE_K } from '../scripts/pipeline/daily_three_source_baseline_migration.mjs'

const read = path => JSON.parse(readFileSync(fileURLToPath(new URL(path, import.meta.url))))
const original = read('../scripts/migration-proofs/three-source-j-original/market.json')
const current = read('../../contracts/market.json')
const registry = read('../scripts/migration-proofs/three-source-j-original/authority.json')
const transition = read('../scripts/migration-proofs/three-source-j-original/transition.json')
const data = read('../src/data/generated/dailyMarket.json')

test('exact J/K three rows invert and preserve every other field', () => {
  assert.deepEqual(verifyThreePolicyTransition(original, current, transition, registry), original)
  assert.equal(registry.authority.activatedContractSha256, THREE_K)
  for (const mutate of [x => { x.sources.reverse() }, x => { x.sources[0].extra = true },
    x => { x.sources[7].family = 'official_announcements' }, x => { x.sources[19].maxPages = 8 },
    x => { x.sources[8].qualificationOrigin.sourceResultIndex = false }]) {
    const changed = structuredClone(current); mutate(changed)
    assert.throws(() => verifyThreePolicyTransition(original, changed, transition, registry))
  }
  const reversed = structuredClone(transition); reversed.changes.reverse()
  assert.throws(() => verifyThreePolicyTransition(original, current, reversed, registry))
})

test('Python-generated K baseline preserves all J history and has zero intake credit', () => {
  assert.deepEqual(verifyThreeBaselineMigration(data, current, 557), {
    migration: 'prospective_j_to_k_three_source', coverageCredit: false,
  })
  assert.equal(data.coverage.intake.evaluated, false)
  assert.equal(data.coverage.validUntil, null)
  assert.equal(data.coverage.requiredTasks, 557)
  assert.equal(data.checkedAt, data.supersededPolicy.snapshot.checkedAt)
  for (const mutate of [x => { x.checkedAt = '2026-10-27T16:00:00Z' },
    x => { x.coverage.successfulTasks = 3 }, x => { x.coverage.sources[0].processing.pendingDocuments = 1 },
    x => { x.supersededPolicy.snapshot.checkedAt = '2026-10-27T16:00:00Z' },
    x => { x.prospectiveMigration.transitionReference.bytes = true }]) {
    const changed = structuredClone(data); mutate(changed)
    assert.throws(() => verifyThreeBaselineMigration(changed, current, 557))
  }
})
