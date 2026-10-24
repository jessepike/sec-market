import { createHash } from 'node:crypto'
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, join } from 'node:path'

const proofRoot = join(dirname(fileURLToPath(import.meta.url)), '../migration-proofs/daily-v2-original')
const SOURCE_IDS = Object.freeze([
  'ping-identity:official:1',
  'delinea:official:1',
  'sonatype:official:1',
])
const HASH = /^[a-f0-9]{64}$/
const TRANSITION_KEY = /^source-qualification-transitions\/[a-f0-9]{64}\.json$/
const MIGRATION_KIND = 'prospective_v2_to_v2'
const SUPERSEDED_KIND = 'daily_v2_baseline'

// Exact reviewed V5 activation only. Unknown migrations remain rejected.
// Original baseline bytes and the entire superseded history stay pinned below.
export const PROSPECTIVE_V2_MIGRATION_AUTHORITIES = Object.freeze([
  {
    "activatedContractSha256": "8b44bcbec679c178836408c4d98c7230a85572784b0257ef21d21d3b03b445db",
    "originalContractSha256": "79cdd19b962ee3adbb5d9e1a43cbc389b3c9196a6c0a2105ea455c8bd70f9f60",
    "transitionReference": {
      "key": "source-qualification-transitions/8b44bcbec679c178836408c4d98c7230a85572784b0257ef21d21d3b03b445db.json",
      "sha256": "269606aefb5407e08e9d00c8a05281f702bd44059c6d157899033608d157ac21",
      "bytes": 171
    },
    "originalSnapshotSha256": "e797841d93674b223c75397cd979b61586eb8648358f9791b6b361824785e231",
    "originalSnapshotFileSha256": "e339c9157c0e4daffcd85705d894a4ac4dfb19ca252d1c581a604ea359d27fd1",
    "originalSnapshotFileBytes": 2755864,
    "originalSealSha256": "3d97adde1b0655077636f31a8e82b5c03e6eb0268cc75efcbf1798335dbd9c26",
    "originalSealFileBytes": 276,
    "originalContractFileSha256": "5b2b52dc2d17709f562b64ad6cb435086971ff8a6ccb9ce2fe95296a1ce1a7ff",
    "originalContractFileBytes": 279420
  }
])

export const ORIGINAL_V2_PROOF_PINS = Object.freeze({
  originalContractSha256: '79cdd19b962ee3adbb5d9e1a43cbc389b3c9196a6c0a2105ea455c8bd70f9f60',
  originalContractFileSha256: '5b2b52dc2d17709f562b64ad6cb435086971ff8a6ccb9ce2fe95296a1ce1a7ff',
  originalContractFileBytes: 279420,
  originalSnapshotSha256: 'e797841d93674b223c75397cd979b61586eb8648358f9791b6b361824785e231',
  originalSnapshotFileSha256: 'e339c9157c0e4daffcd85705d894a4ac4dfb19ca252d1c581a604ea359d27fd1',
  originalSnapshotFileBytes: 2755864,
  originalSealSha256: '3d97adde1b0655077636f31a8e82b5c03e6eb0268cc75efcbf1798335dbd9c26',
  originalSealFileBytes: 276,
})

const canonical = value => Array.isArray(value)
  ? '[' + value.map(canonical).join(',') + ']'
  : value && typeof value === 'object'
    ? '{' + Object.keys(value).sort().map(key => JSON.stringify(key) + ':' + canonical(value[key])).join(',') + '}'
    : JSON.stringify(value)
const rawHash = bytes => createHash('sha256').update(bytes).digest('hex')
const valueHash = value => rawHash(canonical(value))
const isObject = value => value !== null && typeof value === 'object' && !Array.isArray(value)
const same = (a, b) => canonical(a) === canonical(b)
const sameIds = (a, b) => Array.isArray(a) && Array.isArray(b) && a.length === b.length &&
  new Set(a).size === a.length && new Set(b).size === b.length && a.every(id => b.includes(id))
const demand = (condition, message) => {
  if (!condition) throw new Error('Daily v2 migration ' + message)
}

function packagedAssets() {
  const contractBytes = readFileSync(join(proofRoot, 'market.json'))
  const snapshotBytes = readFileSync(join(proofRoot, 'dailyMarket.json'))
  const sealBytes = readFileSync(join(proofRoot, 'dailyMarket.seal.json'))
  return {
    contractBytes,
    snapshotBytes,
    sealBytes,
    contract: JSON.parse(contractBytes.toString('utf8')),
    snapshot: JSON.parse(snapshotBytes.toString('utf8')),
    seal: JSON.parse(sealBytes.toString('utf8')),
  }
}

function requiredTaskCount(contract) {
  const sources = Array.isArray(contract.sources) ? contract.sources : []
  const suppliers = Array.isArray(contract.suppliers) ? contract.suppliers : []
  return sources.filter(source => source.required === true).length + suppliers.reduce((total, supplier) => {
    const bound = new Set(sources.filter(source => source.supplierId === supplier.id && source.required === true)
      .map(source => source.family))
    return total + (Array.isArray(supplier.requiredFamilies)
      ? supplier.requiredFamilies.filter(family => !bound.has(family)).length
      : 0)
  }, 0)
}

function validateAssetPins(assets, pins) {
  demand(assets && Buffer.isBuffer(assets.contractBytes) && Buffer.isBuffer(assets.snapshotBytes) &&
    Buffer.isBuffer(assets.sealBytes), 'immutable original proof bytes are missing')
  demand(rawHash(assets.contractBytes) === pins.originalContractFileSha256 &&
    assets.contractBytes.length === pins.originalContractFileBytes &&
    rawHash(assets.snapshotBytes) === pins.originalSnapshotFileSha256 &&
    assets.snapshotBytes.length === pins.originalSnapshotFileBytes &&
    rawHash(assets.sealBytes) === pins.originalSealSha256 &&
    assets.sealBytes.length === pins.originalSealFileBytes, 'immutable original proof bytes differ')
  const contract = JSON.parse(assets.contractBytes.toString('utf8'))
  const snapshot = JSON.parse(assets.snapshotBytes.toString('utf8'))
  const seal = JSON.parse(assets.sealBytes.toString('utf8'))
  demand(valueHash(contract) === pins.originalContractSha256 &&
    valueHash(snapshotWithoutAddress(snapshot)) === pins.originalSnapshotSha256 &&
    snapshot.snapshotSha256 === pins.originalSnapshotSha256 &&
    snapshot.contractSha256 === pins.originalContractSha256 &&
    seal.fileSha256 === pins.originalSnapshotFileSha256 &&
    seal.runId === snapshot.runId && seal.contractSha256 === pins.originalContractSha256,
  'immutable original fixture is internally inconsistent')
  return { contract, snapshot, seal }
}

function snapshotWithoutAddress(snapshot) {
  const result = { ...snapshot }
  delete result.snapshotSha256
  return result
}

function validateAuthorityRow(row, pins, contractSha256) {
  const expected = new Set([
    'activatedContractSha256', 'originalContractSha256', 'transitionReference',
    'originalSnapshotSha256', 'originalSnapshotFileSha256', 'originalSnapshotFileBytes',
    'originalSealSha256', 'originalSealFileBytes', 'originalContractFileSha256',
    'originalContractFileBytes',
  ])
  demand(isObject(row) && Object.keys(row).length === expected.size &&
    Object.keys(row).every(key => expected.has(key)), 'authority row has unknown or missing fields')
  demand(row.activatedContractSha256 === contractSha256 && HASH.test(row.activatedContractSha256) &&
    row.originalContractSha256 === pins.originalContractSha256 &&
    row.originalSnapshotSha256 === pins.originalSnapshotSha256 &&
    row.originalSnapshotFileSha256 === pins.originalSnapshotFileSha256 &&
    row.originalSnapshotFileBytes === pins.originalSnapshotFileBytes &&
    row.originalSealSha256 === pins.originalSealSha256 &&
    row.originalSealFileBytes === pins.originalSealFileBytes &&
    row.originalContractFileSha256 === pins.originalContractFileSha256 &&
    row.originalContractFileBytes === pins.originalContractFileBytes,
  'authority row does not pin the packaged original baseline')
  const transition = row.transitionReference
  demand(isObject(transition) && Object.keys(transition).sort().join(',') === 'bytes,key,sha256' &&
    transition.key === `source-qualification-transitions/${contractSha256}.json` &&
    TRANSITION_KEY.test(transition.key) && typeof transition.sha256 === 'string' && HASH.test(transition.sha256) &&
    Number.isSafeInteger(transition.bytes) && transition.bytes > 0 && transition.bytes <= 32_000_000,
  'authority transition reference is invalid')
  return transition
}

function validateThreeSourceContract(original, current) {
  demand(isObject(original) && isObject(current) && Array.isArray(original.sources) &&
    Array.isArray(current.sources) && original.sources.length === current.sources.length,
  'original/current contract source arrays differ')
  const originalIds = original.sources.map(source => source.id)
  const currentIds = current.sources.map(source => source.id)
  demand(same(originalIds, currentIds), 'source order or identities changed')
  const changed = []
  for (let index = 0; index < original.sources.length; index += 1) {
    const oldSource = original.sources[index]
    const newSource = current.sources[index]
    if (!same(oldSource, newSource)) changed.push({ oldSource, newSource })
  }
  demand(changed.length === SOURCE_IDS.length &&
    same(changed.map(item => item.oldSource.id).sort(), [...SOURCE_IDS].sort()),
  'source change set is not the closed three-source transition')
  for (const { oldSource, newSource } of changed) {
    demand(oldSource.registration === 'candidate' && !Object.hasOwn(oldSource, 'qualificationOrigin') &&
      newSource.registration === 'verified' && isObject(newSource.qualificationOrigin),
    'source transition does not match candidate-to-verified activation shape')
  }
  const currentWithoutSources = { ...current, sources: original.sources }
  demand(same(currentWithoutSources, original), 'contract changed outside the three source rows')
}

function validateZeroCreditBaseline(data, contract, originalSnapshot, required) {
  const coverage = data.coverage
  demand(data.schemaVersion === 1 && data.enabled === true &&
    coverage?.schemaVersion === 2 && coverage.measure === 'daily_source_intake_v2' &&
    coverage.intake?.evaluated === false && coverage.intake.status === 'uncollected' &&
    coverage.successfulTasks === 0 && coverage.requiredTasks === required && required === 557 &&
    coverage.complete === false && coverage.validUntil === null &&
    coverage.intake.successfulTasks === 0 && coverage.intake.requiredTasks === required &&
    coverage.intake.complete === false,
  'new snapshot is not an uncollected 0/557 baseline')
  demand(Array.isArray(coverage.sources) && coverage.sources.length === required &&
    new Set(coverage.sources.map(row => row.taskId)).size === required &&
    coverage.sources.filter(row => row.required === true).length === required &&
    Array.isArray(coverage.gapTaskIds) && coverage.gapTaskIds.length === required &&
    sameIds(coverage.gapTaskIds, coverage.sources.map(row => row.taskId)) &&
    coverage.sources.every(row => row.outcome === 'not_checked' && row.intakeOutcome === 'not_checked'),
  'new snapshot contains current-policy intake credit')
  for (const kind of ['processing', 'historicalReview']) {
    const summary = coverage[kind]
    const fields = kind === 'processing'
      ? ['inventoryDocuments', 'reviewedDocuments', 'pendingDocuments', 'heldDocuments', 'changedDocuments', 'unknownDateDocuments']
      : ['inventoryDocuments', 'reviewedDocuments', 'pendingDocuments', 'heldDocuments']
    demand(summary?.evaluated === false && summary.status === 'uncollected' && summary.complete === false &&
      fields.every(field => summary[field] === 0), `new ${kind} summary claims measured work`)
    demand(coverage.sources.every(row => {
      const rowSummary = row[kind]
      return rowSummary?.evaluated === false && rowSummary.status === 'uncollected' &&
        rowSummary.complete === false && fields.every(field => rowSummary[field] === 0)
    }), `a source row claims measured ${kind} work`)
  }
  demand(valueHash(data.events) === valueHash(originalSnapshot.events) &&
    valueHash(data.evidence) === valueHash(originalSnapshot.evidence) &&
    valueHash(data.supplierUpdates) === valueHash(originalSnapshot.supplierUpdates),
  'static public facts changed')
  demand(data.checkedAt === originalSnapshot.checkedAt && data.runId === originalSnapshot.runId &&
    coverage.checkedAt === originalSnapshot.coverage.checkedAt &&
    coverage.lastCollectionAt === originalSnapshot.coverage.lastCollectionAt,
  'original collection dates or run identity changed')
  const oldRows = originalSnapshot.coverage.sources
  demand(Array.isArray(oldRows) && oldRows.length === required && coverage.sources.every((row, index) => {
    const old = oldRows[index]
    const restored = { ...row, registration: old.registration }
    return same(restored, old) && row.outcome === 'not_checked'
  }), 'current snapshot changed the original obligation rows')
}

function validateMigration(data, contract, required, dependencies) {
  const { authorities, assets, pins } = dependencies
  const contractSha256 = valueHash(contract)
  const matches = authorities.filter(row => row?.activatedContractSha256 === contractSha256)
  demand(matches.length === 1, 'prospective v2-to-v2 migration is not statically authorized')
  const authority = matches[0]
  const original = validateAssetPins(assets, pins)
  const transition = validateAuthorityRow(authority, pins, contractSha256)
  demand(valueHash(original.contract) === authority.originalContractSha256 &&
    requiredTaskCount(original.contract) === requiredTaskCount(contract) &&
    requiredTaskCount(contract) === required, 'required obligation denominator changed')
  validateThreeSourceContract(original.contract, contract)
  demand(isObject(data.prospectiveMigration) &&
    Object.keys(data.prospectiveMigration).sort().join(',') === 'kind,schemaVersion,transitionReference' &&
    data.prospectiveMigration.schemaVersion === 1 &&
    data.prospectiveMigration.kind === MIGRATION_KIND &&
    same(data.prospectiveMigration.transitionReference, transition),
  'migration descriptor does not match static transition authority')

  const previous = data.supersededPolicy
  demand(isObject(previous) && Object.keys(previous).sort().join(',') === [
    'contract', 'contractSha256', 'kind', 'schemaVersion', 'seal', 'sealFileBytes', 'sealSha256',
    'snapshot', 'snapshotFileBytes', 'snapshotFileSha256', 'snapshotSha256',
  ].sort().join(',') && previous.schemaVersion === 1 && previous.kind === SUPERSEDED_KIND,
  'superseded baseline wrapper schema differs')
  demand(same(previous.contract, original.contract) && previous.contractSha256 === pins.originalContractSha256 &&
    same(previous.snapshot, original.snapshot) && previous.snapshotSha256 === pins.originalSnapshotSha256 &&
    previous.snapshotFileSha256 === pins.originalSnapshotFileSha256 &&
    previous.snapshotFileBytes === pins.originalSnapshotFileBytes &&
    same(previous.seal, original.seal) && previous.sealSha256 === pins.originalSealSha256 &&
    previous.sealFileBytes === pins.originalSealFileBytes,
  'embedded original baseline or full superseded chain differs from immutable bytes')
  const preservedTopLevel = new Set(['contractSha256', 'coverage', 'prospectiveMigration', 'snapshotSha256', 'supersededPolicy'])
  const oldKeys = Object.keys(original.snapshot).filter(key => !preservedTopLevel.has(key)).sort()
  const newKeys = Object.keys(data).filter(key => !preservedTopLevel.has(key)).sort()
  demand(same(oldKeys, newKeys) && oldKeys.every(key => same(data[key], original.snapshot[key])),
    'original public snapshot fields or historical reports changed')
  validateZeroCreditBaseline(data, contract, original.snapshot, required)
  return { migration: MIGRATION_KIND, transitionReference: transition.key }
}

export function verifyProspectiveV2Migration(data, contract, required) {
  return validateMigration(data, contract, required, {
    authorities: PROSPECTIVE_V2_MIGRATION_AUTHORITIES,
    assets: packagedAssets(),
    pins: ORIGINAL_V2_PROOF_PINS,
  })
}

// Dependency injection is limited to this pure validator for synthetic unit
// fixtures. The build-facing verifier above always supplies the fixed package
// assets and the static authority list.
export function verifyProspectiveV2MigrationFixture(data, contract, required, dependencies) {
  return validateMigration(data, contract, required, dependencies)
}

export { requiredTaskCount as dailyMigrationRequiredTaskCount }
