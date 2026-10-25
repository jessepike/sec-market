import assert from 'node:assert/strict'
import { test } from 'node:test'
import { readFileSync, writeFileSync, mkdirSync, mkdtempSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { resolve } from 'node:path'
import { createHash } from 'node:crypto'
import { verifyFactualCorrections } from '../scripts/verify-factual-corrections.mjs'

const canonical = value => Array.isArray(value) ? '[' + value.map(canonical).join(',') + ']' : value && typeof value === 'object' ? '{' + Object.keys(value).sort().map(k => JSON.stringify(k) + ':' + canonical(value[k])).join(',') + '}' : JSON.stringify(value)
const digest = value => createHash('sha256').update(typeof value === 'string' || Buffer.isBuffer(value) ? value : canonical(value)).digest('hex')
const historicalRequests = readFileSync(new URL('../../ops/ci/fixtures/accepted-six-correction-requests-2026-10-25.json', import.meta.url))
const historicalStamp = readFileSync(new URL('../../ops/ci/fixtures/accepted-six-correction-stamp-J-2026-10-25.json', import.meta.url))
assert.equal(digest(historicalRequests), '9c9fbe0d3d40ece11e1407ce9460086c732f62da88d3b0f220ab9d6f8757da00')
assert.equal(digest(historicalStamp), '365058911a182610cde401307fb30cc1855930b7940969440a618441cbbef9b2')
const design = JSON.parse(readFileSync(new URL('../../docs/active/daily-pipeline/accuracy/source-classification-admission-design-2026-10-23.json', import.meta.url)))
const reviewPolicy = (group, market, baselineSha256) => digest({
  schemaVersion: 1, rulesVersion: 'dated-factual-correction-review-1', baselineSha256,
  candidateSha256: digest(group),
  supplier: Object.fromEntries(['id', 'name', 'aliases', 'kind'].map(key => [key, market.suppliers.find(supplier => supplier.id === group.supplierId)[key]])),
  sources: group.sources.map(source => market.sources.find(configured => configured.id === source.sourceId)),
  model: Object.fromEntries(['provider', 'allowApiBilling', 'maxDocumentChars'].map(key => [key, market.model[key]])),
  freshnessHours: 30, checks: ['entity', 'value', 'currency_units', 'period_date', 'qualifiers', 'event_status', 'source_support'].sort(),
  ...(group.reviewScope === 'publisher_disclosure_only' ? {
    rulesVersion: 'dated-publisher-disclosure-classification-1', reviewScope: group.reviewScope,
    allowedTransition: design.proposedReviewPolicy.basis.allowedTransition,
    checks: ['class_transition', 'limitations_scope', 'literal_disclosure', 'publisher_source_binding', 'release_attribution', 'target_identity', 'unchanged_claims_and_history'].sort(),
  } : {}),
})

function fixture(t, enabled = true) {
  const root = mkdtempSync(resolve(tmpdir(), 'smp-correction-build-'))
  t.after(() => rmSync(root, { recursive: true, force: true }))
  const web = resolve(root, 'web')
  const files = ['contracts/market.json', 'contracts/factual-corrections.json', 'contracts/factual-baseline.json', 'web/src/data/tracker/originals.json', 'web/src/data/tracker/factualCorrectionPolicy.json', 'web/src/data/generated/factualCorrections.json']
  for (const file of files) {
    mkdirSync(resolve(root, file, '..'), { recursive: true })
    const bytes = file === 'contracts/factual-corrections.json' ? historicalRequests
      : file === 'web/src/data/tracker/factualCorrectionPolicy.json' ? historicalStamp
        : readFileSync(new URL('../../' + file, import.meta.url))
    writeFileSync(resolve(root, file), bytes)
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
      ...(group.reviewScope ? { reviewScope: group.reviewScope } : {}),
      admission: { result: 'accepted', policySha256: policy.reviewPolicySha256ByGroup[group.id], candidateSha256: digest(group), evidenceSetSha256: digest(group.sources), admittedAt: '2026-10-24T06:00:00Z', reviewSha256: 'a'.repeat(64), ...(group.reviewScope ? { reviewScope: group.reviewScope } : {}) },
    })),
  } : { schemaVersion: 1, enabled: false, policySha256: null, checkedAt: null, groups: [] }
  // Synthetic seal proves file consistency only; these fixtures are never used as admission.
  function seal({ newGroupIds = policy.groupIds } = {}) {
    write(path, bundle)
    write(path.replace('.json', '.seal.json'), { schemaVersion: 1, fileSha256: digest(readFileSync(resolve(root, path))), policySha256: policy.policySha256, groupIds: policy.groupIds, targetIds: policy.targetIds, newGroupIds, publicationDate: bundle.checkedAt?.slice(0, 10) ?? '2026-10-24' })
  }
  function repin() {
    const current = read('contracts/factual-corrections.json'), market = read('contracts/market.json')
    Object.assign(policy, {
      policySha256: digest({ marketSha256: digest(market), requestsSha256: digest(current), baselineSha256: current.baseline.sha256 }),
      groupIds: current.groups.map(group => group.id), targetIds: current.groups.flatMap(group => group.targets.map(target => target.targetId)),
      sourceEvidenceIds: Object.fromEntries(current.groups.map(group => [group.id, group.sources.map(source => source.evidenceId)])),
      reviewPolicySha256ByGroup: Object.fromEntries(current.groups.map(group => [group.id, reviewPolicy(group, market, current.baseline.sha256)])),
    })
    write('web/src/data/tracker/factualCorrectionPolicy.json', policy)
    if (bundle.enabled) bundle.policySha256 = policy.policySha256
    return policy
  }
  seal()
  return { root, web, bundle, seal, repin, read, write }
}

test('build binds every requested before/after and policy without certifying synthetic admission', t => {
  const f = fixture(t)
  const result = verifyFactualCorrections(f.web)
  assert.equal(result.enabled, true)
  const requests = f.read('contracts/factual-corrections.json')
  assert.equal(requests.groups.filter(group => !group.reviewScope).length, 5)
  assert.equal(result.groupIds.length, requests.groups.length)
  assert.equal(result.targetIds.length, requests.groups.flatMap(group => group.targets).length)
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
test('unrelated source repair changes global inventory while retaining exact historical admissions', t => {
  const f = fixture(t)
  const oldGlobal = f.bundle.policySha256, oldGroups = structuredClone(f.bundle.groups)
  const market = f.read('contracts/market.json')
  market.sources.push({ ...market.sources[0], id: 'synthetic:unrelated-registration', url: market.sources[0].url + '?synthetic-repair' })
  market.suppliers.find(supplier => supplier.id === market.sources[0].supplierId).sourceIds.push('synthetic:unrelated-registration')
  f.write('contracts/market.json', market)
  const policy = f.repin()
  f.bundle.checkedAt = '2026-10-25T06:23:00Z'
  f.seal({ newGroupIds: [] })
  assert.notEqual(policy.policySha256, oldGlobal)
  assert.deepEqual(f.bundle.groups, oldGroups)
  const result = verifyFactualCorrections(f.web)
  assert.equal(result.policySha256, policy.policySha256)
  assert.deepEqual(result.newGroupIds, [])
})
test('changed relevant registration requires a new group review policy despite a fresh global seal', t => {
  const f = fixture(t)
  const oldAdmission = structuredClone(f.bundle.groups[0].admission)
  const requests = f.read('contracts/factual-corrections.json'), market = f.read('contracts/market.json')
  const source = market.sources.find(source => source.id === requests.groups[0].sources[0].sourceId)
  source.registrationProof = { ...source.registrationProof, scope: 'Synthetic changed relevant registration' }
  f.write('contracts/market.json', market)
  const policy = f.repin()
  assert.notEqual(policy.reviewPolicySha256ByGroup[f.bundle.groups[0].id], oldAdmission.policySha256)
  assert.deepEqual(f.bundle.groups[0].admission, oldAdmission)
  f.seal()
  assert.throws(() => verifyFactualCorrections(f.web), /unbound admission metadata/)
  // A synthetic replacement hash exercises consistency only, never semantic admission.
  for (const group of f.bundle.groups) group.admission.policySha256 = policy.reviewPolicySha256ByGroup[group.id]
  f.seal()
  assert.equal(verifyFactualCorrections(f.web).enabled, true)
})
test('build independently refuses missing, forged or extra group review policy stamps', t => {
  for (const mutation of ['missing', 'forged', 'extra']) {
    const f = fixture(t, false), stamp = f.read('web/src/data/tracker/factualCorrectionPolicy.json')
    if (mutation === 'missing') delete stamp.reviewPolicySha256ByGroup
    if (mutation === 'forged') stamp.reviewPolicySha256ByGroup[stamp.groupIds[0]] = 'f'.repeat(64)
    if (mutation === 'extra') stamp.reviewPolicySha256ByGroup.synthetic = 'e'.repeat(64)
    f.write('web/src/data/tracker/factualCorrectionPolicy.json', stamp)
    assert.throws(() => verifyFactualCorrections(f.web), /stamp differs/)
  }
})
test('global inventory policy cannot substitute for an atomic review policy', t => {
  const f = fixture(t)
  f.bundle.groups[0].admission.policySha256 = f.bundle.policySha256
  f.seal()
  assert.throws(() => verifyFactualCorrections(f.web), /unbound admission metadata/)
})

function publisherFixture(t, enabled = true) {
  const f = fixture(t, enabled)
  const requests = f.read('contracts/factual-corrections.json')
  const legacyRows = structuredClone(f.bundle.groups.filter(group => !group.reviewScope))
  if (!requests.groups.some(group => group.id === design.proposedGroupExample.id)) requests.groups.push(structuredClone(design.proposedGroupExample))
  f.write('contracts/factual-corrections.json', requests)
  f.repin()
  function refresh() {
    const current = f.read('contracts/factual-corrections.json'), policy = f.repin()
    if (f.bundle.enabled) {
      for (const request of current.groups) {
        let row = f.bundle.groups.find(group => group.id === request.id)
        if (!row) {
          row = { id: request.id, supplierId: request.supplierId, reasonCode: request.reasonCode, date: '2026-10-24', admission: { result: 'accepted', admittedAt: '2026-10-24T06:00:00Z', reviewSha256: 'a'.repeat(64) } }
          f.bundle.groups.push(row)
        }
        row.targets = structuredClone(request.targets)
        row.note = request.noteTemplate.replace('{date}', row.date)
        if (Object.hasOwn(request, 'reviewScope')) {
          row.reviewScope = request.reviewScope; row.admission.reviewScope = request.reviewScope
        }
        Object.assign(row.admission, { policySha256: policy.reviewPolicySha256ByGroup[request.id], candidateSha256: digest(request), evidenceSetSha256: digest(request.sources) })
      }
    }
    f.seal({ newGroupIds: f.bundle.enabled ? [design.proposedGroupExample.id] : [] })
    return policy
  }
  refresh()
  return { ...f, refresh, legacyRows,
    role: () => f.bundle.groups.find(group => group.id === design.proposedGroupExample.id),
    mutateRequest: mutate => {
      const current = f.read('contracts/factual-corrections.json')
      mutate(current.groups.find(group => group.id === design.proposedGroupExample.id), current)
      f.write('contracts/factual-corrections.json', current)
      refresh()
    } }
}

test('scoped build proves historical baseline and exact three-field amendment with accepted hashes retained', t => {
  const f = publisherFixture(t), policy = f.read('web/src/data/tracker/factualCorrectionPolicy.json')
  const repair = JSON.parse(readFileSync(new URL('../../docs/active/daily-pipeline/accuracy/failed-correction-review-repair-spec-2026-10-24.json', import.meta.url)))
  const permitted = { 'FC-20261023-checkpoint-sase': ['noteTemplate', 'reasonCode'], 'FC-20261023-zscaler': ['noteTemplate'] }
  assert.deepEqual(repair.changedFields.slice().sort(), Object.entries(permitted).flatMap(([id, fields]) => fields.map(field => `${id}.${field}`)).sort())
  assert.equal(repair.changedFields.length, 3)
  assert.equal(repair.diagnosis.length, 2)
  assert.deepEqual(repair.diagnosis.map(item => item.groupId).sort(), Object.keys(permitted).sort())
  const requests = f.read('contracts/factual-corrections.json'), market = f.read('contracts/market.json')
  const historical = structuredClone(requests)
  for (const item of repair.diagnosis) {
    const group = requests.groups.find(group => group.id === item.groupId)
    const prior = historical.groups.find(group => group.id === item.groupId)
    assert.deepEqual(Object.keys(item.proposedChanges).sort(), permitted[item.groupId])
    assert.equal(digest(group), item.proposedCandidateSha256)
    assert.equal(policy.reviewPolicySha256ByGroup[group.id], item.proposedReviewPolicySha256)
    assert.equal(digest(group.sources), item.evidenceSetSha256)
    assert.equal(digest(group.targets), item.targetSetSha256)
    for (const [field, values] of Object.entries(item.proposedChanges)) {
      assert.equal(group[field], values.new)
      assert.notEqual(values.old, values.new)
      prior[field] = values.old
    }
  }
  assert.equal(digest(historical), repair.oldRequestsCanonicalSha256)
  for (const [id, hash] of Object.entries(design.proposedImplementation.inventoryPolicy.existingReviewPoliciesUnchanged)) {
    const prior = historical.groups.find(group => group.id === id)
    assert.equal(digest(prior), design.proposedImplementation.inventoryPolicy.existingGroupCandidateSha256ById[id])
    assert.equal(reviewPolicy(prior, market, requests.baseline.sha256), hash)
  }
  assert.deepEqual(repair.preservedAcceptedAdmissions.map(item => item.groupId).sort(), ['FC-20261023-optiv', 'FC-20261023-splunk', 'FC-20261023-expel', 'XAGE-SOURCE-CLASS-20261023'].sort())
  for (const item of repair.preservedAcceptedAdmissions) {
    const group = requests.groups.find(group => group.id === item.groupId)
    assert.equal(digest(group), item.candidateSha256)
    assert.equal(digest(group.sources), item.evidenceSetSha256)
    assert.equal(policy.reviewPolicySha256ByGroup[group.id], item.reviewPolicySha256)
  }
  const historicalMarket = JSON.parse(readFileSync(new URL('../../docs/active/daily-pipeline/evaluations/2026-10-24/operational-inputs/contract.json', import.meta.url)))
  assert.equal(digest({ marketSha256: digest(historicalMarket), requestsSha256: digest(requests), baselineSha256: requests.baseline.sha256 }), repair.proposedGlobalPolicySha256)
  // D-112 changes the enclosing collection policy, preserving every group's
  // independently bound review/admission context and original admission dates.
  assert.equal(policy.policySha256, digest({ marketSha256: digest(market), requestsSha256: digest(requests), baselineSha256: requests.baseline.sha256 }))
  assert.equal(policy.reviewPolicySha256ByGroup[design.proposedGroupExample.id], design.proposedReviewPolicy.sha256)
  assert.deepEqual(f.bundle.groups.filter(group => !group.reviewScope), f.legacyRows)
  const result = verifyFactualCorrections(f.web)
  assert.equal(result.groupIds.length, 6); assert.equal(result.targetIds.length, 12)
  assert.deepEqual(result.newGroupIds, [design.proposedGroupExample.id])
})

test('scoped disabled build still verifies exact requested scope and protected metadata', t => {
  const f = publisherFixture(t, false)
  assert.equal(verifyFactualCorrections(f.web).enabled, false)
  f.mutateRequest(group => { group.targets[0].proposedValue.excerpt += ' changed financial claim' })
  assert.throws(() => verifyFactualCorrections(f.web), /proposed transition|protected fields/)
})

test('scoped build rejects every protected proposed field even with recalculated policy and seal', t => {
  for (const field of Object.keys(design.records.original).filter(key => !['sourceClass', 'limitations'].includes(key))) {
    const f = publisherFixture(t)
    f.mutateRequest(group => { group.targets[0].proposedValue[field] = Array.isArray(group.targets[0].proposedValue[field]) ? ['forged'] : 'forged' })
    assert.throws(() => verifyFactualCorrections(f.web), /proposed transition|protected fields/)
  }
})

test('scoped build refuses changed history and unsupported target/scope/transition combinations', t => {
  for (const mutate of [
    group => { group.targets[0].original.excerpt += ' changed original' },
    group => { group.targets[0].originalSha256 = 'a'.repeat(64) },
    group => { group.targets[0].targetId = 'evidence:TR-expel-2' },
    group => { group.targets[0].operation = 'replace' },
    group => { group.targets[0].proposedValue.sourceClass = 'IR' },
    group => { group.targets[0].proposedValue.limitations = 'Independently verified finances.' },
    group => { group.reviewScope = 'financial_verification' },
    group => { delete group.reviewScope },
    group => { group.supplierId = 'expel' },
    (group, requests) => { group.targets.push(structuredClone(requests.groups[0].targets[0])) },
  ]) {
    const f = publisherFixture(t); f.mutateRequest(mutate)
    assert.throws(() => verifyFactualCorrections(f.web), /publisher disclosure|review scope/)
  }
})

test('scoped build rejects altered source/quote descriptors despite fresh hashes and synthetic acceptance', t => {
  for (const mutate of [
    group => { group.sources[0].proofScope = 'financial_verification' },
    group => { group.sources[0].url += '?changed=1' },
    group => { group.sources[0].sourceId = 'other:source' },
    group => { group.sources[0].body.bytes = 0 },
    group => { group.sources[0].body.key = 'objects/forged' },
    group => { group.sources[0].fetchedAt = '2026-02-30T12:00:00Z' },
    group => { group.sources[0].visibleText.rulesVersion = 'excerpt-only' },
    group => { group.sources[0].visibleText.sha256 = 'malformed' },
    group => { group.sources[0].visibleText.chars = 30001 },
    group => { group.sources[0].disclosureQuoteIds.pop() },
    group => { group.disclosureQuotes[0].literalInUniqueArticle = false },
    group => { group.disclosureQuotes[0].normalizedWholePageStart++ },
    group => { group.disclosureQuotes[0].text += ' altered'; group.disclosureQuotes[0].textSha256 = digest(group.disclosureQuotes[0].text); group.disclosureQuotes[0].normalizedWholePageEnd += 8 },
    group => { group.disclosureQuotes[0].scope = 'financial verification' },
  ]) {
    const f = publisherFixture(t)
    f.mutateRequest(mutate)
    assert.throws(() => verifyFactualCorrections(f.web), /publisher disclosure/)
  }
})

test('scoped public row and admission must each echo only the required narrow scope', t => {
  for (const [object, value] of [['group', undefined], ['group', 'financial_verification'], ['admission', undefined], ['admission', 'financial_verification']]) {
    const f = publisherFixture(t), target = object === 'group' ? f.role() : f.role().admission
    if (value === undefined) delete target.reviewScope
    else target.reviewScope = value
    f.seal()
    assert.throws(() => verifyFactualCorrections(f.web), /review scope or schema/)
  }
  const f = publisherFixture(t)
  f.bundle.groups.find(group => !group.reviewScope).admission.reviewScope = 'publisher_disclosure_only'; f.seal()
  assert.throws(() => verifyFactualCorrections(f.web), /review scope or schema/)
})

test('scoped group remains mandatory and cannot use an ordinary review policy or a stale map', t => {
  for (const mode of ['missingGroup', 'ordinaryPolicy', 'missingMap', 'extraMap', 'staleMap']) {
    const f = publisherFixture(t)
    if (mode === 'missingGroup') { f.bundle.groups.pop(); f.seal() }
    if (mode === 'ordinaryPolicy') { f.role().admission.policySha256 = f.bundle.groups[0].admission.policySha256; f.seal() }
    if (mode.endsWith('Map')) {
      const policy = f.read('web/src/data/tracker/factualCorrectionPolicy.json')
      if (mode === 'missingMap') delete policy.reviewPolicySha256ByGroup[design.proposedGroupExample.id]
      if (mode === 'extraMap') policy.reviewPolicySha256ByGroup.extra = 'f'.repeat(64)
      if (mode === 'staleMap') policy.reviewPolicySha256ByGroup[design.proposedGroupExample.id] = 'f'.repeat(64)
      f.write('web/src/data/tracker/factualCorrectionPolicy.json', policy)
    }
    assert.throws(() => verifyFactualCorrections(f.web), /incomplete groups|unbound admission|stamp differs/)
  }
})

test('scoped admission retains its actual initial source window and dated history', t => {
  const f = publisherFixture(t), row = f.role(), source = design.proposedGroupExample.sources[0]
  row.admission.admittedAt = new Date(Date.parse(source.fetchedAt) + 30 * 3600000 + 1).toISOString()
  f.bundle.checkedAt = '2026-10-24T12:00:00Z'; f.seal()
  assert.throws(() => verifyFactualCorrections(f.web), /original source window/)
  row.admission.admittedAt = '2026-10-24T06:00:00Z'
  const original = structuredClone(row)
  f.bundle.checkedAt = '2026-11-24T12:00:00Z'; f.seal({ newGroupIds: [] })
  assert.equal(verifyFactualCorrections(f.web).enabled, true)
  assert.deepEqual(f.role(), original)
})

test('publisher class mutation cannot be disguised as an ordinary evidence replacement', t => {
  const f = publisherFixture(t)
  f.mutateRequest(group => {
    delete group.reviewScope; delete group.disclosureQuotes
    group.targets[0].operation = 'replace'
    group.sources = group.sources.map(source => Object.fromEntries(['evidenceId', 'sourceId', 'url', 'observationId', 'body', 'fetchedAt'].map(key => [key, source[key]])))
  })
  assert.throws(() => verifyFactualCorrections(f.web), /ordinary evidence replacement changes protected metadata/)
})
