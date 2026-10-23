// Build consistency checks. Semantic admission is replayed by the independent
// Python gate against the immutable archive; a JSON seal alone is not that proof.
import { readFileSync, existsSync } from 'node:fs'
import { resolve } from 'node:path'
import { createHash } from 'node:crypto'

const canonical = value => Array.isArray(value) ? '[' + value.map(canonical).join(',') + ']' : value && typeof value === 'object' ? '{' + Object.keys(value).sort().map(k => JSON.stringify(k) + ':' + canonical(value[k])).join(',') + '}' : JSON.stringify(value)
const digest = value => createHash('sha256').update(Buffer.isBuffer(value) ? value : canonical(value)).digest('hex')
const equal = (a, b) => canonical(a) === canonical(b)
const requireThat = (condition, reason) => { if (!condition) throw new Error(`Factual correction build refused: ${reason}`) }

export function verifyFactualCorrections(web) {
  const file = resolve(web, 'src/data/generated/factualCorrections.json')
  const contractPath = resolve(web, '../contracts/factual-corrections.json')
  // Older isolated release fixtures predate this feature. Actual builds must
  // include both policy and projection, including the disabled development view.
  if (!existsSync(file) && !existsSync(contractPath)) return { enabled: false }
  const read = path => JSON.parse(readFileSync(path, 'utf8'))
  const requests = read(contractPath)
  requireThat(requests.baseline?.path === 'contracts/factual-baseline.json', 'unexpected baseline path')
  const baselineBytes = readFileSync(resolve(web, '..', requests.baseline.path))
  requireThat(digest(baselineBytes) === requests.baseline.sha256, 'baseline bytes changed')
  const baseline = JSON.parse(baselineBytes)
  const originals = read(resolve(web, 'src/data/tracker/originals.json'))
  requireThat(baseline.schemaVersion === 1 && equal(Object.keys(originals).sort(), ['events', 'evidence', 'suppliers']), 'original inventory schema differs')
  for (const [kind, records] of Object.entries(originals)) {
    requireThat(Array.isArray(records) && new Set(records.map(r => r.id)).size === records.length, 'duplicate original identity')
    requireThat(equal(Object.fromEntries(records.map(record => [record.id, digest(record)])), baseline.inventories[kind]), `unreviewed ${kind} original edit`)
  }
  const market = read(resolve(web, '../contracts/market.json'))
  const policySha256 = digest({ marketSha256: digest(market), requestsSha256: digest(requests), baselineSha256: requests.baseline.sha256 })
  const groupIds = requests.groups.map(group => group.id)
  const targetIds = requests.groups.flatMap(group => group.targets.map(target => target.targetId))
  requireThat(new Set(groupIds).size === groupIds.length && new Set(targetIds).size === targetIds.length, 'duplicate requested group or target')
  const expected = read(resolve(web, 'src/data/tracker/factualCorrectionPolicy.json'))
  const sourceEvidenceIds = Object.fromEntries(requests.groups.map(group => [group.id, group.sources.map(source => source.evidenceId)]))
  requireThat(equal(expected, { schemaVersion: 1, policySha256, groupIds, targetIds, sourceEvidenceIds }), 'policy stamp differs')
  const bytes = readFileSync(file), bundle = JSON.parse(bytes)
  requireThat(bundle.schemaVersion === 1 && typeof bundle.enabled === 'boolean', 'projection schema differs')
  if (!bundle.enabled) {
    requireThat(equal(bundle, { schemaVersion: 1, enabled: false, policySha256: null, checkedAt: null, groups: [] }), 'disabled projection contains corrections')
    return { enabled: false, policySha256, fileSha256: digest(bytes) }
  }
  requireThat(bundle.policySha256 === policySha256 && equal(bundle.groups.map(group => group.id), groupIds), 'stale policy or incomplete groups')
  requireThat(Number.isFinite(Date.parse(bundle.checkedAt)) && bundle.checkedAt.endsWith('Z'), 'invalid check time')
  for (const [index, group] of bundle.groups.entries()) {
    const request = requests.groups[index]
    requireThat(group.supplierId === request.supplierId && group.reasonCode === request.reasonCode && equal(group.targets, request.targets), 'target before/after policy differs')
    requireThat(/^\d{4}-\d{2}-\d{2}$/.test(group.date) && new Date(group.date).toISOString().slice(0, 10) === group.date && group.date <= bundle.checkedAt.slice(0, 10), 'invalid publication date')
    requireThat(group.note === request.noteTemplate.replace('{date}', group.date), 'correction note differs from reviewed template')
    const admission = group.admission
    requireThat(admission?.result === 'accepted' && admission.policySha256 === policySha256 && admission.candidateSha256 === digest(request) && admission.evidenceSetSha256 === digest(request.sources) && /^[a-f0-9]{64}$/.test(admission.reviewSha256 ?? ''), 'unbound admission metadata')
    requireThat(Number.isFinite(Date.parse(admission.admittedAt)) && admission.admittedAt.endsWith('Z') && Date.parse(admission.admittedAt) <= Date.parse(bundle.checkedAt) && admission.admittedAt.slice(0, 10) <= group.date, 'future admission')
    for (const target of group.targets) requireThat(digest(target.original) === target.originalSha256, 'wrong original hash')
  }
  const seal = read(file.replace(/\.json$/, '.seal.json'))
  requireThat(seal.schemaVersion === 1 && seal.fileSha256 === digest(bytes) && seal.policySha256 === policySha256 && equal(seal.groupIds, groupIds) && equal(seal.targetIds, targetIds), 'projection differs from gate seal')
  requireThat(Array.isArray(seal.newGroupIds) && new Set(seal.newGroupIds).size === seal.newGroupIds.length && seal.newGroupIds.every(id => groupIds.includes(id)), 'invalid new correction inventory')
  requireThat(/^\d{4}-\d{2}-\d{2}$/.test(seal.publicationDate) && seal.publicationDate === bundle.checkedAt.slice(0, 10) && bundle.groups.filter(group => seal.newGroupIds.includes(group.id)).every(group => group.date === seal.publicationDate), 'new correction date differs')
  return { enabled: true, policySha256, fileSha256: digest(bytes), groupIds, targetIds, newGroupIds: seal.newGroupIds, publicationDate: seal.publicationDate }
}
