import { readFileSync } from 'node:fs'
import { createHash } from 'node:crypto'
import { fileURLToPath } from 'node:url'
import { verifyProspectiveV2Migration } from './daily_baseline_migration.mjs'

export const Q4_J = '47b9f22636f0e6ea79cf830ae90aab844d8f554d44110a5bb08f29f00266593a'
const H = '8b44bcbec679c178836408c4d98c7230a85572784b0257ef21d21d3b03b445db'
const root = new URL('../migration-proofs/q4-h-original/', import.meta.url)
const canonical = value => Array.isArray(value) ? '[' + value.map(canonical).join(',') + ']'
  : value && typeof value === 'object' ? '{' + Object.keys(value).sort().map(k => JSON.stringify(k) + ':' + canonical(value[k])).join(',') + '}' : JSON.stringify(value)
const rawHash = raw => createHash('sha256').update(raw).digest('hex')
const hash = value => rawHash(canonical(value))
const same = (a, b) => canonical(a) === canonical(b)
const demand = (value, message) => { if (!value) throw new Error('Q4 baseline ' + message) }
const unsigned = value => { const copy = { ...value }; delete copy.snapshotSha256; return copy }

function asset(name, pin) {
  const raw = readFileSync(fileURLToPath(new URL(name, root)))
  demand(rawHash(raw) === pin.sha256 && raw.length === pin.bytes, 'immutable asset differs')
  return JSON.parse(raw.toString('utf8'))
}

export function verifyQ4PolicyTransition(original, current, transition, registry) {
  demand(hash(original) === H && hash(current) === Q4_J &&
    hash(transition) === registry.authority.transition.sha256 &&
    same(transition, { schemaVersion: 1, kind: 'two_q4_press_source_qualification',
      originalContract: registry.authority.originalContract, activatedContractSha256: Q4_J,
      changes: ['jfrog:official:1', 'rapid7:official:1'].map(id => registry.authority.sources[id].change) }),
  'exact policy pair or transition differs')
  const forward = structuredClone(original), inverse = structuredClone(current)
  demand(Array.isArray(original.sources) && original.sources.length === current.sources.length, 'source count differs')
  for (const id of ['jfrog:official:1', 'rapid7:official:1']) {
    const row = registry.authority.sources[id], index = row.sourceIndex
    const old = original.sources[index], next = current.sources[index]
    const adapter = { ...old, kind: 'q4_press_list', url: registry.urls[id], registration: 'verified' }
    demand(old.id === id && next.id === id && hash(old) === row.change.originalSourceSha256 &&
      hash(adapter) === row.change.adapterSha256 && hash(next) === row.sourceSha256 &&
      hash(row.origin) === row.change.qualificationOriginSha256 &&
      same(next, { ...adapter, qualificationOrigin: row.origin }), 'source patch or position differs')
    forward.sources[index] = structuredClone(next)
    inverse.sources[index] = structuredClone(old)
  }
  demand(same(forward, current) && same(inverse, original), 'whole forward or inverse policy differs')
  return inverse
}

export function verifyQ4BaselineMigration(data, contract, required) {
  const registry = asset('authority.json', { sha256: '3fcc1a016f0e76e00257645fb8756786811035c3cf8ab4919c39220d23ef129a', bytes: 5825 })
  const original = asset('market.json', registry.baselinePins['market.json'])
  const snapshot = asset('dailyMarket.json', registry.baselinePins['dailyMarket.json'])
  const seal = asset('dailyMarket.seal.json', registry.baselinePins['dailyMarket.seal.json'])
  const transition = asset('transition.json', registry.authority.transition)
  verifyQ4PolicyTransition(original, contract, transition, registry)
  // The older positive pair and its entire nested history keep their original verifier.
  verifyProspectiveV2Migration(snapshot, original, required)
  demand(required === 557 && snapshot.contractSha256 === H && hash(unsigned(snapshot)) === snapshot.snapshotSha256 &&
    seal.fileSha256 === registry.baselinePins['dailyMarket.json'].sha256 && seal.runId === snapshot.runId &&
    seal.contractSha256 === H, 'original baseline identity differs')
  const expected = structuredClone(snapshot)
  expected.contractSha256 = Q4_J
  expected.coverage.contractSha256 = Q4_J
  for (const row of expected.coverage.sources) {
    if (['jfrog:official:1', 'rapid7:official:1'].includes(row.sourceId)) {
      demand(row.registration === 'candidate', 'original registration differs')
      row.registration = 'verified'
    }
  }
  const pointer = Buffer.from(canonical(registry.authority.transition))
  expected.prospectiveMigration = { schemaVersion: 1, kind: 'prospective_h_to_j_q4', transitionReference: {
    key: `source-qualification-transitions/${Q4_J}.json`, sha256: rawHash(pointer), bytes: pointer.length } }
  expected.supersededPolicy = { schemaVersion: 1, kind: 'daily_v2_baseline', contractSha256: H,
    contract: original, snapshotSha256: snapshot.snapshotSha256,
    snapshotFileSha256: registry.baselinePins['dailyMarket.json'].sha256,
    snapshotFileBytes: registry.baselinePins['dailyMarket.json'].bytes, snapshot,
    sealSha256: registry.baselinePins['dailyMarket.seal.json'].sha256,
    sealFileBytes: registry.baselinePins['dailyMarket.seal.json'].bytes, seal }
  expected.snapshotSha256 = hash(unsigned(expected))
  demand(same(data, expected), 'projection changed historical facts, dates, obligations or zero-credit state')
  return { migration: 'prospective_h_to_j_q4', coverageCredit: false }
}
