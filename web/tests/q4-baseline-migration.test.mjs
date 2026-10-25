import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { verifyQ4BaselineMigration, verifyQ4PolicyTransition, Q4_J } from '../scripts/pipeline/daily_q4_baseline_migration.mjs'

const read = path => JSON.parse(readFileSync(fileURLToPath(new URL(path, import.meta.url))))
const original = read('../scripts/migration-proofs/q4-h-original/market.json')
const current = read('../../contracts/market.json')
const registry = read('../scripts/migration-proofs/q4-h-original/authority.json')
const transition = read('../scripts/migration-proofs/q4-h-original/transition.json')
const snapshot = read('../src/data/generated/dailyMarket.json')

test('exact H/J policies invert independently and preserve all other sources and types', () => {
  assert.deepEqual(verifyQ4PolicyTransition(original, current, transition, registry), original)
  assert.equal(registry.authority.activatedContractSha256, Q4_J)
  const mutations = [
    value => value.sources.reverse(),
    value => { value.sources[0].extra = true },
    value => { value.model.maxCallsPerRun = 81 },
    value => { value.sources[34].qualificationOrigin.sourceResultIndex = false },
    value => { value.sources[52].url += '&year=2026' },
  ]
  for (const mutate of mutations) {
    const changed = structuredClone(current); mutate(changed)
    assert.throws(() => verifyQ4PolicyTransition(original, changed, transition, registry))
  }
  const reversed = structuredClone(transition); reversed.changes.reverse()
  assert.throws(() => verifyQ4PolicyTransition(original, current, reversed, registry))
})

test('J baseline preserves full H history and all dates while granting zero credit', () => {
  assert.deepEqual(verifyQ4BaselineMigration(snapshot, current, 557), {
    migration: 'prospective_h_to_j_q4', coverageCredit: false,
  })
  assert.equal(snapshot.coverage.intake.evaluated, false)
  assert.equal(snapshot.coverage.validUntil, null)
  assert.equal(snapshot.coverage.requiredTasks, 557)
  assert.equal(snapshot.checkedAt, snapshot.supersededPolicy.snapshot.checkedAt)
  const mutations = [
    value => { value.checkedAt = '2026-10-25T12:30:00Z' },
    value => { value.coverage.successfulTasks = 2 },
    value => { value.coverage.sources[0].processing.pendingDocuments = 1 },
    value => { value.supersededPolicy.snapshot.checkedAt = '2026-10-25T12:30:00Z' },
    value => { value.coverage.sources.reverse() },
    value => { value.prospectiveMigration.transitionReference.bytes = true },
  ]
  for (const mutate of mutations) {
    const changed = structuredClone(snapshot); mutate(changed)
    assert.throws(() => verifyQ4BaselineMigration(changed, current, 557))
  }
})
