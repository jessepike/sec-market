import assert from 'node:assert/strict'
import { test } from 'node:test'
import { readFileSync, writeFileSync, mkdirSync, mkdtempSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { resolve } from 'node:path'
import { createHash } from 'node:crypto'
import { verifyFactualCorrections } from '../scripts/verify-factual-corrections.mjs'

const canonical = value => Array.isArray(value) ? '[' + value.map(canonical).join(',') + ']' : value && typeof value === 'object' ? '{' + Object.keys(value).sort().map(k => JSON.stringify(k) + ':' + canonical(value[k])).join(',') + '}' : JSON.stringify(value)
const digest = value => createHash('sha256').update(typeof value === 'string' || Buffer.isBuffer(value) ? value : canonical(value)).digest('hex')

function fixture(t, enabled = true) {
  const root = mkdtempSync(resolve(tmpdir(), 'smp-correction-build-'))
  t.after(() => rmSync(root, { recursive: true, force: true }))
  const web = resolve(root, 'web')
  const files = ['contracts/market.json', 'contracts/factual-corrections.json', 'contracts/factual-baseline.json', 'web/src/data/tracker/originals.json', 'web/src/data/tracker/factualCorrectionPolicy.json', 'web/src/data/generated/factualCorrections.json']
  for (const file of files) {
    mkdirSync(resolve(root, file, '..'), { recursive: true })
    writeFileSync(resolve(root, file), readFileSync(new URL('../../' + file, import.meta.url)))
  }
  const read = file => JSON.parse(readFileSync(resolve(root, file)))
  const write = (file, value) => writeFileSync(resolve(root, file), JSON.stringify(value, null, 2) + '\n')
  const requests = read('contracts/factual-corrections.json')
  const policy = read('web/src/data/tracker/factualCorrectionPolicy.json')
  const path = 'web/src/data/generated/factualCorrections.json'
  const bundle = enabled ? {
    schemaVersion: 1, enabled: true, policySha256: policy.policySha256, checkedAt: '2026-10-24T06:23:00Z',
    groups: requests.groups.map(group => ({
      id: group.id, supplierId: group.supplierId, reasonCode: group.reasonCode, date: '2026-10-24',
      note: group.noteTemplate.replace('{date}', '2026-10-24'), targets: group.targets,
      admission: { result: 'accepted', policySha256: policy.policySha256, candidateSha256: digest(group), evidenceSetSha256: digest(group.sources), admittedAt: '2026-10-24T06:00:00Z', reviewSha256: 'a'.repeat(64) },
    })),
  } : { schemaVersion: 1, enabled: false, policySha256: null, checkedAt: null, groups: [] }
  // Synthetic seal proves file consistency only; these fixtures are never used as admission.
  function seal() {
    write(path, bundle)
    write(path.replace('.json', '.seal.json'), { schemaVersion: 1, fileSha256: digest(readFileSync(resolve(root, path))), policySha256: policy.policySha256, groupIds: policy.groupIds, targetIds: policy.targetIds, newGroupIds: policy.groupIds, publicationDate: '2026-10-24' })
  }
  seal()
  return { root, web, bundle, seal, read, write }
}

test('build binds every requested before/after and policy without certifying synthetic admission', t => {
  const f = fixture(t)
  const result = verifyFactualCorrections(f.web)
  assert.equal(result.enabled, true)
  assert.equal(result.groupIds.length, 5)
  assert.equal(result.targetIds.length, 11)
})
test('disabled build preserves original inventory checks', t => {
  const f = fixture(t, false)
  assert.equal(verifyFactualCorrections(f.web).enabled, false)
  const raw = f.read('web/src/data/tracker/originals.json')
  raw.events[0].text += ' unreviewed edit'
  f.write('web/src/data/tracker/originals.json', raw)
  assert.throws(() => verifyFactualCorrections(f.web), /unreviewed events original edit/)
})
test('build rejects missing groups despite a new file seal', t => {
  const f = fixture(t)
  f.bundle.groups.pop(); f.seal()
  assert.throws(() => verifyFactualCorrections(f.web), /incomplete groups/)
})
test('build rejects a changed target even if its JSON seal is recalculated', t => {
  const f = fixture(t)
  f.bundle.groups[1].targets[0].proposedValue.text += ' forged claim'; f.seal()
  assert.throws(() => verifyFactualCorrections(f.web), /before\/after policy differs/)
})
test('build rejects wrong review metadata and source-set binding', t => {
  for (const field of ['candidateSha256', 'evidenceSetSha256', 'policySha256', 'reviewSha256']) {
    const f = fixture(t)
    f.bundle.groups[0].admission[field] = field === 'reviewSha256' ? 'wrong' : '0'.repeat(64); f.seal()
    assert.throws(() => verifyFactualCorrections(f.web), /unbound admission metadata/)
  }
})
test('build refuses note changes and fresh date relabeling', t => {
  const f = fixture(t)
  f.bundle.groups[0].note += ' extra'; f.seal()
  assert.throws(() => verifyFactualCorrections(f.web), /reviewed template/)
  f.bundle.groups[0].note = f.bundle.groups[0].note.replace(' extra', '')
  f.bundle.groups[0].date = '2026-10-23'; f.seal()
  assert.throws(() => verifyFactualCorrections(f.web), /template|future admission/)
})
test('build refuses stale baseline pin or policy stamp', t => {
  const f = fixture(t, false)
  const stamp = f.read('web/src/data/tracker/factualCorrectionPolicy.json')
  stamp.targetIds.pop(); f.write('web/src/data/tracker/factualCorrectionPolicy.json', stamp)
  assert.throws(() => verifyFactualCorrections(f.web), /stamp differs/)
  f.write('contracts/factual-baseline.json', {})
  assert.throws(() => verifyFactualCorrections(f.web), /baseline bytes changed/)
})
