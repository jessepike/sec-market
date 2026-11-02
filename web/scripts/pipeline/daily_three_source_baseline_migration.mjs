import { readFileSync } from 'node:fs'
import { createHash } from 'node:crypto'
import { fileURLToPath } from 'node:url'
import { Q4_J, verifyQ4BaselineMigration } from './daily_q4_baseline_migration.mjs'

export const THREE_K = '6cb053a5954a52f2dddf7773caeca1db436dbe5966e085ea421d911691774a68'
const root = new URL('../migration-proofs/three-source-j-original/', import.meta.url)
const canonical = value => Array.isArray(value) ? '[' + value.map(canonical).join(',') + ']'
  : value && typeof value === 'object' ? '{' + Object.keys(value).sort().map(k => JSON.stringify(k) + ':' + canonical(value[k])).join(',') + '}' : JSON.stringify(value)
const rawHash = raw => createHash('sha256').update(raw).digest('hex')
const hash = value => rawHash(canonical(value))
const same = (a, b) => canonical(a) === canonical(b)
const demand = (value, message) => { if (!value) throw new Error('Three-source baseline ' + message) }
const unsigned = value => { const copy = { ...value }; delete copy.snapshotSha256; return copy }
const ids = ['cato:official:1', 'chainguard:official:1', 'cyera:official:1']

function asset(name, pin) {
  const raw = readFileSync(fileURLToPath(new URL(name, root)))
  demand(rawHash(raw) === pin.sha256 && raw.length === pin.bytes, 'immutable asset differs')
  return JSON.parse(raw.toString('utf8'))
}

export function verifyThreePolicyTransition(original, current, transition, registry) {
  const authority = registry.authority
  demand(hash(original) === Q4_J && hash(current) === THREE_K &&
    hash(transition) === authority.transition.sha256 &&
    same(transition, { schemaVersion: 1, kind: 'three_existing_source_qualification',
      originalContract: authority.originalContract, activatedContractSha256: THREE_K,
      changes: ids.map(id => authority.sources[id].change) }), 'exact policy pair or transition differs')
  const forward = structuredClone(original), inverse = structuredClone(current)
  demand(Array.isArray(original.sources) && original.sources.length === current.sources.length, 'source count differs')
  for (const id of ids) {
    const row = authority.sources[id], index = row.sourceIndex
    const old = original.sources[index], next = current.sources[index]
    const adapter = { ...old, kind: 'html_index', registration: 'verified', url: row.url,
      htmlCompleteness: id === 'cyera:official:1' ? 'cyera-press-list-finite-html-v1' : 'prnewswire-issuer-calendar-window-v1' }
    demand(old.id === id && next.id === id && hash(old) === row.originalSourceSha256 &&
      hash(adapter) === row.adapterSha256 && hash(next) === row.sourceSha256 &&
      same(next, { ...adapter, qualificationOrigin: row.origin }), 'source patch or position differs')
    forward.sources[index] = structuredClone(next)
    inverse.sources[index] = structuredClone(old)
  }
  demand(same(forward, current) && same(inverse, original), 'whole forward or inverse policy differs')
  return inverse
}

export function verifyThreeBaselineMigration(data, contract, required) {
  const registry = asset('authority.json', {"sha256": "fe0e7c05593d38b93bc4c267ceabb147f3335c772727092b635504070e3713cf", "bytes": 6063})
  const original = asset('market.json', registry.baselinePins['market.json'])
  const snapshot = asset('dailyMarket.json', registry.baselinePins['dailyMarket.json'])
  const seal = asset('dailyMarket.seal.json', registry.baselinePins['dailyMarket.seal.json'])
  const transition = asset('transition.json', registry.authority.transition)
  verifyThreePolicyTransition(original, contract, transition, registry)
  verifyQ4BaselineMigration(snapshot, original, required)
  demand(required === 557 && snapshot.contractSha256 === Q4_J && hash(unsigned(snapshot)) === snapshot.snapshotSha256 &&
    seal.fileSha256 === registry.baselinePins['dailyMarket.json'].sha256 && seal.runId === snapshot.runId &&
    seal.contractSha256 === Q4_J, 'original baseline identity differs')
  const expected = structuredClone(snapshot)
  expected.contractSha256 = THREE_K
  expected.coverage.contractSha256 = THREE_K
  for (const row of expected.coverage.sources) {
    if (ids.includes(row.sourceId)) {
      demand(row.registration === 'candidate', 'original registration differs')
      row.registration = 'verified'
    }
  }
  const pointer = Buffer.from(canonical(registry.authority.transition))
  expected.prospectiveMigration = { schemaVersion: 1, kind: 'prospective_j_to_k_three_source', transitionReference: {
    key: `source-qualification-transitions/${THREE_K}.json`, sha256: rawHash(pointer), bytes: pointer.length } }
  expected.supersededPolicy = { schemaVersion: 1, kind: 'daily_v2_baseline', contractSha256: Q4_J,
    contract: original, snapshotSha256: snapshot.snapshotSha256,
    snapshotFileSha256: registry.baselinePins['dailyMarket.json'].sha256,
    snapshotFileBytes: registry.baselinePins['dailyMarket.json'].bytes, snapshot,
    sealSha256: registry.baselinePins['dailyMarket.seal.json'].sha256,
    sealFileBytes: registry.baselinePins['dailyMarket.seal.json'].bytes, seal }
  expected.snapshotSha256 = hash(unsigned(expected))
  demand(same(data, expected), 'projection changed historical facts, dates, obligations or zero-credit state')
  return { migration: 'prospective_j_to_k_three_source', coverageCredit: false }
}
