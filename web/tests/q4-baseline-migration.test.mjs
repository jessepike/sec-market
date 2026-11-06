import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { createHash } from 'node:crypto'
import { gunzipSync } from 'node:zlib'
import { verifyQ4BaselineMigration, verifyQ4PolicyTransition, Q4_J } from '../scripts/pipeline/daily_q4_baseline_migration.mjs'
import { repoBaseContract } from '../scripts/pipeline/roster_transition.mjs'

const read = path => JSON.parse(readFileSync(fileURLToPath(new URL(path, import.meta.url))))
const original = read('../scripts/migration-proofs/q4-h-original/market.json')
// Under J's additive roster successor (D-138) the J these proofs pin is its exact inverse.
const current = repoBaseContract(fileURLToPath(new URL('..', import.meta.url)))
const registry = read('../scripts/migration-proofs/q4-h-original/authority.json')
const transition = read('../scripts/migration-proofs/q4-h-original/transition.json')
// Accepted prospective J baseline, frozen from immutable Git blob 3794b800ffc9d691604d77ed1d06a3a8daebf517.
// Fresh gate data is a different snapshot and must never replace this historical fixture.
const packed = readFileSync(fileURLToPath(new URL('./fixtures/q4-prospective-j-baseline-2026-10-25.json.gz', import.meta.url)))
const sha256 = raw => createHash('sha256').update(raw).digest('hex')
assert.equal(packed.length, 555404)
assert.equal(sha256(packed), '643cfc12299d2841d37ca7589fe76de56b9ba40266b1643c7e67d3213e71c051')
const frozen = gunzipSync(packed)
assert.equal(frozen.length, 7696749)
assert.equal(sha256(frozen), '7120790449e8a4427446e2a62d69889cf651692153e6624359c50daa0379197f')
const snapshot = JSON.parse(frozen.toString('utf8'))

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
