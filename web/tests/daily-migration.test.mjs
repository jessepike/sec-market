import { test } from 'node:test'
import assert from 'node:assert/strict'
import { createHash } from 'node:crypto'
import { mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { verifyDaily } from '../scripts/verify-daily.mjs'
import {
  ORIGINAL_V2_PROOF_PINS,
  PROSPECTIVE_V2_MIGRATION_AUTHORITIES,
  dailyMigrationRequiredTaskCount,
  verifyProspectiveV2MigrationFixture,
} from '../scripts/pipeline/daily_baseline_migration.mjs'

const canonical = value => Array.isArray(value)
  ? '[' + value.map(canonical).join(',') + ']'
  : value && typeof value === 'object'
    ? '{' + Object.keys(value).sort().map(key => JSON.stringify(key) + ':' + canonical(value[key])).join(',') + '}'
    : JSON.stringify(value)
const rawHash = value => createHash('sha256').update(value).digest('hex')
const valueHash = value => rawHash(canonical(value))
const proofDir = fileURLToPath(new URL('../scripts/migration-proofs/daily-v2-original/', import.meta.url))

function originalAssets() {
  const contractBytes = readFileSync(join(proofDir, 'market.json'))
  const snapshotBytes = readFileSync(join(proofDir, 'dailyMarket.json'))
  const sealBytes = readFileSync(join(proofDir, 'dailyMarket.seal.json'))
  return { contractBytes, snapshotBytes, sealBytes }
}

function migrationFixture() {
  const assets = originalAssets()
  const originalContract = JSON.parse(assets.contractBytes.toString('utf8'))
  const originalSnapshot = JSON.parse(assets.snapshotBytes.toString('utf8'))
  const originalSeal = JSON.parse(assets.sealBytes.toString('utf8'))
  const contract = structuredClone(originalContract)
  const migratedIds = ['ping-identity:official:1', 'delinea:official:1', 'sonatype:official:1']
  for (const sourceId of migratedIds) {
    const source = contract.sources.find(item => item.id === sourceId)
    assert.ok(source, `fixture source ${sourceId} exists`)
    source.registration = 'verified'
    source.qualificationOrigin = { schemaVersion: 1, kind: 'bounded_html_qualification', fixture: true }
  }
  const activatedContractSha256 = valueHash(contract)
  const transitionReference = {
    key: `source-qualification-transitions/${activatedContractSha256}.json`,
    sha256: 'f'.repeat(64),
    bytes: 123,
  }
  const pins = {
    ...ORIGINAL_V2_PROOF_PINS,
    originalSealFileSha256: rawHash(assets.sealBytes),
  }
  const authority = {
    activatedContractSha256,
    originalContractSha256: valueHash(originalContract),
    transitionReference,
    originalSnapshotSha256: originalSnapshot.snapshotSha256,
    originalSnapshotFileSha256: rawHash(assets.snapshotBytes),
    originalSnapshotFileBytes: assets.snapshotBytes.length,
    originalSealSha256: rawHash(assets.sealBytes),
    originalSealFileBytes: assets.sealBytes.length,
    originalContractFileSha256: rawHash(assets.contractBytes),
    originalContractFileBytes: assets.contractBytes.length,
  }
  const data = structuredClone(originalSnapshot)
  data.contractSha256 = activatedContractSha256
  data.coverage.contractSha256 = activatedContractSha256
  for (const row of data.coverage.sources) {
    if (migratedIds.includes(row.sourceId)) row.registration = 'verified'
  }
  data.prospectiveMigration = {
    schemaVersion: 1,
    kind: 'prospective_v2_to_v2',
    transitionReference: structuredClone(transitionReference),
  }
  data.supersededPolicy = {
    schemaVersion: 1,
    kind: 'daily_v2_baseline',
    contract: originalContract,
    contractSha256: valueHash(originalContract),
    snapshot: originalSnapshot,
    snapshotSha256: originalSnapshot.snapshotSha256,
    snapshotFileSha256: rawHash(assets.snapshotBytes),
    snapshotFileBytes: assets.snapshotBytes.length,
    seal: originalSeal,
    sealSha256: rawHash(assets.sealBytes),
    sealFileBytes: assets.sealBytes.length,
  }
  delete data.snapshotSha256
  data.snapshotSha256 = valueHash(data)
  return { data, contract, authority, assets, pins, required: dailyMigrationRequiredTaskCount(contract) }
}

function verifyFixture(f, overrides = {}) {
  return verifyProspectiveV2MigrationFixture(f.data, f.contract, f.required, {
    authorities: overrides.authorities ?? [f.authority],
    assets: overrides.assets ?? f.assets,
    pins: overrides.pins ?? f.pins,
  })
}

test('original v2 proof stays byte-pinned and only the reviewed actual migration is authorized', () => {
  const assets = originalAssets()
  assert.equal(assets.contractBytes.length, ORIGINAL_V2_PROOF_PINS.originalContractFileBytes)
  assert.equal(rawHash(assets.contractBytes), ORIGINAL_V2_PROOF_PINS.originalContractFileSha256)
  assert.equal(assets.snapshotBytes.length, ORIGINAL_V2_PROOF_PINS.originalSnapshotFileBytes)
  assert.equal(rawHash(assets.snapshotBytes), ORIGINAL_V2_PROOF_PINS.originalSnapshotFileSha256)
  assert.equal(assets.sealBytes.length, ORIGINAL_V2_PROOF_PINS.originalSealFileBytes)
  assert.equal(rawHash(assets.sealBytes), ORIGINAL_V2_PROOF_PINS.originalSealSha256)
  assert.equal(PROSPECTIVE_V2_MIGRATION_AUTHORITIES.length, 1)
  const authority = PROSPECTIVE_V2_MIGRATION_AUTHORITIES[0]
  assert.equal(authority.activatedContractSha256,
    '8b44bcbec679c178836408c4d98c7230a85572784b0257ef21d21d3b03b445db')
  assert.deepEqual(authority.transitionReference, {
    key: `source-qualification-transitions/${authority.activatedContractSha256}.json`,
    sha256: '269606aefb5407e08e9d00c8a05281f702bd44059c6d157899033608d157ac21',
    bytes: 171,
  })
})

test('synthetic positive authority accepts only a zero-credit v2-to-v2 preservation wrapper', () => {
  const f = migrationFixture()
  assert.equal(f.required, 557)
  assert.equal(f.data.coverage.successfulTasks, 0)
  assert.equal(f.data.coverage.complete, false)
  assert.equal(f.data.coverage.intake.evaluated, false)
  assert.deepEqual(verifyFixture(f), {
    migration: 'prospective_v2_to_v2',
    transitionReference: f.authority.transitionReference.key,
  })
})

test('build verifier rejects a valid-looking baseline outside the reviewed static authority', t => {
  const f = migrationFixture()
  const root = mkdtempSync(join(tmpdir(), 'smp-daily-v2-migration-'))
  t.after(() => rmSync(root, { recursive: true, force: true }))
  const web = join(root, 'web')
  mkdirSync(join(web, 'src/data/generated'), { recursive: true })
  mkdirSync(join(root, 'contracts'), { recursive: true })
  const contractBytes = Buffer.from(JSON.stringify(f.contract))
  const snapshotBytes = Buffer.from(JSON.stringify(f.data))
  writeFileSync(join(root, 'contracts/market.json'), contractBytes)
  writeFileSync(join(web, 'src/data/generated/dailyMarket.json'), snapshotBytes)
  writeFileSync(join(web, 'src/data/generated/dailyMarket.seal.json'), JSON.stringify({
    fileSha256: rawHash(snapshotBytes), runId: f.data.runId, contractSha256: f.data.contractSha256,
  }))
  assert.throws(() => verifyDaily(web), /not statically authorized/)
})

test('migration rejects altered original bytes, seals, nested chain and transition binding', () => {
  const cases = [
    f => { f.data.supersededPolicy.snapshot.events.push({ invented: true }) },
    f => { f.data.supersededPolicy.snapshot.supersededPolicy.snapshot.checkedAt = '2026-10-24T00:00:00Z' },
    f => { f.data.supersededPolicy.seal.fileSha256 = '0'.repeat(64) },
    f => { f.data.prospectiveMigration.transitionReference.sha256 = '0'.repeat(64) },
    f => { f.authority.unreviewed = true },
    f => { f.assets = { ...f.assets, snapshotBytes: Buffer.from('changed original snapshot') } },
  ]
  for (const [index, mutate] of cases.entries()) {
    const f = migrationFixture()
    mutate(f)
    assert.throws(() => verifyFixture(f), /Daily v2 migration/, `tamper case ${index}`)
  }
})

test('migration rejects changed original dates, public facts, nonzero current totals and source edits', () => {
  const cases = [
    f => { f.data.checkedAt = '2026-10-24T12:00:00Z' },
    f => { f.data.coverage.lastCollectionAt = '2026-10-24T12:00:00Z' },
    f => { f.data.secRecords.invented = true },
    f => { f.data.coverage.successfulTasks = 1 },
    f => { f.data.coverage.historicalReview.evaluated = true },
    f => { f.data.coverage.sources[0].processing.pendingDocuments = 1 },
    f => { f.data.coverage.sources[0].processingOutcome = 'reviewed' },
    f => {
      const extra = f.contract.sources.find(source => ![
        'ping-identity:official:1', 'delinea:official:1', 'sonatype:official:1',
      ].includes(source.id))
      extra.registration = extra.registration === 'verified' ? 'candidate' : 'verified'
      f.authority.activatedContractSha256 = valueHash(f.contract)
      f.data.contractSha256 = f.authority.activatedContractSha256
      f.data.coverage.contractSha256 = f.authority.activatedContractSha256
      f.authority.transitionReference.key = `source-qualification-transitions/${f.authority.activatedContractSha256}.json`
      f.data.prospectiveMigration.transitionReference = structuredClone(f.authority.transitionReference)
    },
  ]
  for (const mutate of cases) {
    const f = migrationFixture()
    mutate(f)
    assert.throws(() => verifyFixture(f), /Daily v2 migration/)
  }
})
