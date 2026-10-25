import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { describe, it } from 'node:test'
import { createHash } from 'node:crypto'
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { Corrections } from '../src/components/Corrections.tsx'
import { factualCorrectionFeedText, factualCorrectionHistory, publicCorrectionsJsonPayload } from '../src/data/factualCorrectionHelpers.ts'
import { projectEvents, projectEvidence, projectSuppliers, validateBundle } from '../src/data/tracker/factualCorrections.ts'
import type { FactualCorrectionBundle, FactualCorrectionGroup, FactualCorrectionInventories } from '../src/data/tracker/factualCorrections.ts'
import { assertCurrentFacts, expectedCurrentFacts, loadCurrentFactInputs } from '../scripts/verify-current-facts.ts'

const read = (relative: string) => JSON.parse(readFileSync(new URL(relative, import.meta.url), 'utf8'))
const design = read('../../docs/active/daily-pipeline/accuracy/source-classification-admission-design-2026-10-23.json')
const historicalRequests = readFileSync(new URL('../../ops/ci/fixtures/accepted-six-correction-requests-2026-10-25.json', import.meta.url))
assert.equal(createHash('sha256').update(historicalRequests).digest('hex'), '9c9fbe0d3d40ece11e1407ce9460086c732f62da88d3b0f220ab9d6f8757da00')
const requests = JSON.parse(historicalRequests.toString('utf8'))
const policy = read('../src/data/tracker/factualCorrectionPolicy.json')
const raw = read('../src/data/tracker/originals.json') as FactualCorrectionInventories
const copy = <T>(value: T): T => structuredClone(value)
const globalPolicy = 'a'.repeat(64)

function fixture() {
  // All admissions below are synthetic mechanics; no semantic acceptance is created.
  const legacy: FactualCorrectionGroup[] = requests.groups.filter((group: { reviewScope?: string }) => !group.reviewScope).map((group: any) => ({
    id: group.id, supplierId: group.supplierId, reasonCode: group.reasonCode, date: '2026-10-23',
    note: group.noteTemplate.replace('{date}', '2026-10-23'), targets: copy(group.targets),
    admission: { result: 'accepted', candidateSha256: 'b'.repeat(64), evidenceSetSha256: 'c'.repeat(64),
      policySha256: policy.reviewPolicySha256ByGroup[group.id], reviewSha256: 'd'.repeat(64), admittedAt: '2026-10-23T21:00:00Z' },
  }))
  const request = copy(design.proposedGroupExample)
  const role: FactualCorrectionGroup = {
    id: request.id, supplierId: request.supplierId, reviewScope: 'publisher_disclosure_only', reasonCode: request.reasonCode,
    date: '2026-10-24', note: request.noteTemplate.replace('{date}', '2026-10-24'), targets: request.targets,
    admission: { result: 'accepted', reviewScope: 'publisher_disclosure_only', candidateSha256: design.proposedGroupSha256,
      evidenceSetSha256: design.proposedEvidenceSetSha256, policySha256: design.proposedReviewPolicy.sha256,
      reviewSha256: 'e'.repeat(64), admittedAt: '2026-10-24T06:00:00Z' },
  }
  const inventories = copy(raw)
  const reviewPolicies = { ...Object.fromEntries(legacy.map(group => [group.id, group.admission.policySha256])), [role.id]: role.admission.policySha256 }
  const bundle: FactualCorrectionBundle = { schemaVersion: 1, enabled: true, checkedAt: '2026-10-24T06:23:00Z', policySha256: globalPolicy, groups: [...legacy, role] }
  return { inventories, bundle, role, legacy, reviewPolicies }
}

function rejectedEverywhere(mutate: (f: ReturnType<typeof fixture>) => void) {
  const f = fixture(); mutate(f)
  assert.throws(() => validateBundle(f.bundle, globalPolicy, f.inventories, f.reviewPolicies), /Invalid factual corrections/)
  for (const project of [projectEvents, projectSuppliers, projectEvidence]) {
    assert.throws(() => project(f.inventories, f.bundle, globalPolicy, f.reviewPolicies), /Invalid factual corrections/)
  }
}

describe('scoped publisher disclosure projection (synthetic, non-admitting)', () => {
  it('changes exactly Xage class/limitations and preserves every legacy row and original', () => {
    const f = fixture(), originals = copy(f.inventories), rows = copy(f.legacy)
    const legacyBundle = { ...copy(f.bundle), groups: copy(f.legacy) }
    const legacyPolicies = Object.fromEntries(f.legacy.map(group => [group.id, group.admission.policySha256]))
    validateBundle(f.bundle, globalPolicy, f.inventories, f.reviewPolicies)
    assert.deepEqual(projectEvents(f.inventories, f.bundle, globalPolicy, f.reviewPolicies), projectEvents(f.inventories, legacyBundle, globalPolicy, legacyPolicies))
    assert.deepEqual(projectSuppliers(f.inventories, f.bundle, globalPolicy, f.reviewPolicies), projectSuppliers(f.inventories, legacyBundle, globalPolicy, legacyPolicies))
    const evidence = projectEvidence(f.inventories, f.bundle, globalPolicy, f.reviewPolicies)
    const original = originals.evidence.find(record => record.id === 'TR-xage-1')!
    const current = evidence.find(record => record.id === original.id)!
    assert.equal(current.sourceClass, 'OFFICIAL')
    assert.equal(current.limitations, design.records.proposed.limitations)
    assert.deepEqual(Object.keys(original).filter(key => JSON.stringify((original as any)[key]) !== JSON.stringify((current as any)[key])).sort(), ['limitations', 'sourceClass'])
    assert.deepEqual(f.inventories, originals)
    assert.deepEqual(f.bundle.groups.slice(0, 5), rows)
    current.excerpt = 'A local override cannot mutate original history.'
    assert.equal(f.inventories.evidence.find(record => record.id === original.id)!.excerpt, original.excerpt)
  })

  it('does not reinterpret the immutable original class as financial proof', () => {
    const f = fixture()
    const current = projectEvidence(f.inventories, f.bundle, globalPolicy, f.reviewPolicies).find(record => record.id === 'TR-xage-1')!
    assert.equal(current.sourceClass, 'OFFICIAL')
    assert.equal(f.inventories.evidence.find(record => record.id === 'TR-xage-1')!.sourceClass, 'INDEPENDENT')
    assert.equal(current.excerpt, design.records.original.excerpt)
    assert.match(current.limitations, /does not independently verify the financial, funding or operating figures/)
    assert.equal(f.role.admission.reviewScope, 'publisher_disclosure_only')
  })

  for (const key of ['id', 'title', 'organization', 'publicationDate', 'economicPeriod', 'canonicalUrl', 'excerpt', 'interpretation', 'conflictingEvidenceIds', 'artifactLabel', 'tags', 'retrievedAt']) {
    it(`protects the scoped ${key} value`, () => rejectedEverywhere(f => {
      const value = f.role.targets[0].proposedValue as any
      value[key] = Array.isArray(value[key]) ? ['forged'] : 'forged'
    }))
  }

  it('rejects added/deleted metadata, modified before-values, class transitions and arbitrary limitations', () => {
    for (const mutate of [
      (f: ReturnType<typeof fixture>) => { (f.role.targets[0].proposedValue as any).sourceAttributions = [] },
      (f: ReturnType<typeof fixture>) => { delete (f.role.targets[0].proposedValue as any).retrievedAt },
      (f: ReturnType<typeof fixture>) => { (f.role.targets[0].original as any).excerpt += ' altered history' },
      (f: ReturnType<typeof fixture>) => { f.role.targets[0].originalSha256 = 'f'.repeat(64) },
      (f: ReturnType<typeof fixture>) => { (f.role.targets[0].proposedValue as any).sourceClass = 'IR' },
      (f: ReturnType<typeof fixture>) => { (f.role.targets[0].proposedValue as any).limitations = 'Financials independently verified.' },
      (f: ReturnType<typeof fixture>) => { (f.role.targets[0].proposedValue as any).retrieval = { finalUrl: design.records.original.canonicalUrl, sha256: 'f'.repeat(64), fetchedAt: '2026-10-24T06:00:00Z' } },
    ]) rejectedEverywhere(mutate)
  })

  it('rejects missing/unknown/mixed scopes and admission scope substitution', () => {
    for (const mutate of [
      (f: ReturnType<typeof fixture>) => { delete f.role.reviewScope },
      (f: ReturnType<typeof fixture>) => { (f.role as any).reviewScope = 'financial_verification' },
      (f: ReturnType<typeof fixture>) => { delete f.role.admission.reviewScope },
      (f: ReturnType<typeof fixture>) => { (f.role.admission as any).reviewScope = 'financial_verification' },
      (f: ReturnType<typeof fixture>) => { f.legacy[0].admission.reviewScope = 'publisher_disclosure_only' },
      (f: ReturnType<typeof fixture>) => { (f.role.targets[0] as any).operation = 'replace' },
      (f: ReturnType<typeof fixture>) => { f.role.targets.push(copy(f.legacy[0].targets[0])) },
      (f: ReturnType<typeof fixture>) => { f.role.supplierId = 'expel' },
      (f: ReturnType<typeof fixture>) => { (f.role.targets[0] as any).targetId = 'evidence:TR-expel-2' },
      (f: ReturnType<typeof fixture>) => { (f.role.targets[0] as any).targetId = 'event:EV-optiv-2' },
    ]) rejectedEverywhere(mutate)
  })

  it('keeps ordinary replacement metadata protections and rejects duplicate role targets', () => {
    rejectedEverywhere(f => {
      const target = f.legacy[0].targets.find(target => target.targetId.startsWith('evidence:'))!
      ;(target.proposedValue as any).sourceClass = (target.original as any).sourceClass === 'INDEPENDENT' ? 'OFFICIAL' : 'INDEPENDENT'
    })
    rejectedEverywhere(f => { f.legacy[0].targets.push(copy(f.role.targets[0])) })
    rejectedEverywhere(f => { f.bundle.groups.push(copy(f.role)) })
    rejectedEverywhere(f => { f.role.admission.policySha256 = globalPolicy })
    rejectedEverywhere(f => { delete f.reviewPolicies[f.role.id] })
  })

  it('binds runtime exported evidence views and rejects a post-projection class, excerpt or map edit', () => {
    const f = fixture(), inputs = loadCurrentFactInputs()
    inputs.originals = f.inventories; inputs.corrections = f.bundle
    inputs.expectedPolicySha256 = globalPolicy; inputs.expectedReviewPolicySha256ByGroup = f.reviewPolicies
    const expected = expectedCurrentFacts(inputs)
    assert.equal(expected.evidenceById['TR-xage-1'].sourceClass, 'OFFICIAL')
    assert.equal(expected.handWrittenEvidenceRecords.find(record => record.id === 'TR-xage-1')!.sourceClass, 'INDEPENDENT')
    assertCurrentFacts(copy(expected), expected)
    for (const field of ['class', 'excerpt', 'map', 'history']) {
      const actual = copy(expected)
      if (field === 'class') actual.evidenceRecords.find(record => record.id === 'TR-xage-1')!.sourceClass = 'INDEPENDENT'
      if (field === 'excerpt') actual.evidenceRecords.find(record => record.id === 'TR-xage-1')!.excerpt += ' forged financial claim'
      if (field === 'map') actual.evidenceById = { ...actual.evidenceById, 'TR-xage-1': copy(design.records.original) }
      if (field === 'history') actual.handWrittenEvidenceRecords.find(record => record.id === 'TR-xage-1')!.sourceClass = 'OFFICIAL'
      assert.throws(() => assertCurrentFacts(actual, expected), /Current facts refused/)
    }
  })

  it('uses the current history/JSON/feed route with narrow scope and exact publisher/class readings', () => {
    const f = fixture()
    const evidence = Object.fromEntries(projectEvidence(f.inventories, f.bundle, globalPolicy, f.reviewPolicies).map(record => [record.id, record]))
    const sources = { evidence, suppliers: f.inventories.suppliers, groupEvidenceIds: { [f.role.id]: ['TR-xage-1'] } }
    const legacyBefore = factualCorrectionHistory(f.legacy, sources, 'https://example.invalid')
    const entry = factualCorrectionHistory([f.role], sources, 'https://example.invalid')[0]
    assert.equal(entry.kind, 'publisher_disclosure_correction')
    assert.match(entry.changes[0].before, /Publisher: Yahoo Finance; Source class: INDEPENDENT/)
    assert.match(entry.changes[0].after, /Publisher: Yahoo Finance; Source class: OFFICIAL/)
    assert.equal(entry.changes[0].operation, 'reclassify_publisher_disclosure')
    const feed = factualCorrectionFeedText(entry)
    assert.match(feed, /publication role only and does not verify financial/)
    assert.doesNotMatch(feed, /Source-verified factual correction/)
    const all = factualCorrectionHistory(f.bundle.groups, sources, 'https://example.invalid')
    assert.deepEqual(all.filter(row => row.id !== f.role.id), legacyBefore)
    const json = publicCorrectionsJsonPayload([], f.bundle.groups, sources, 'https://example.invalid')
    assert.equal(json.find(row => row.id === f.role.id)!.kind, 'publisher_disclosure_correction')
    const html = renderToStaticMarkup(createElement(Corrections, { groups: [f.role], sources }))
    const roleHtml = html.slice(html.indexOf(`id="${f.role.id}"`), html.indexOf('</li>', html.indexOf(`id="${f.role.id}"`)))
    assert.match(roleHtml, /Publisher disclosure correction/)
    assert.match(roleHtml, /Source class: INDEPENDENT/); assert.match(roleHtml, /Source class: OFFICIAL/)
    assert.match(roleHtml, /Yahoo Finance/); assert.match(roleHtml, /publication role only/)
    assert.doesNotMatch(roleHtml, /Approved by|Source-verified factual correction/)
  })
})
