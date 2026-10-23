import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { describe, it } from 'node:test'
import { corrections } from '../src/data/corrections.ts'
import type { EvidenceRecord } from '../src/data/types.ts'
import type { TrackerEvent } from '../src/data/tracker/events.ts'
import type { TrackerSupplier } from '../src/data/tracker/suppliers.ts'
import { projectEvents, projectEvidence, projectSuppliers, validateBundle } from '../src/data/tracker/factualCorrections.ts'
import type { FactualCorrectionBundle, FactualCorrectionGroup, FactualCorrectionInventories, FactualCorrectionTarget } from '../src/data/tracker/factualCorrections.ts'

// Synthetic admissions exercise mechanics only. They never admit these draft corrections.
const POLICY = 'a'.repeat(64)
// The real gate enables the generated bundle before running this suite.
// Disabled mechanics use an explicit fixture, never a constraint on that live build input.
const disabled: FactualCorrectionBundle = { schemaVersion: 1, enabled: false, policySha256: null, checkedAt: null, groups: [] }
const clone = <T>(value: T): T => JSON.parse(JSON.stringify(value)) as T
const drafts = JSON.parse(readFileSync(new URL('../../docs/active/daily-pipeline/accuracy/dated-correction-candidates-2026-10-23.v2.json', import.meta.url), 'utf8')).candidates as Array<{
  targetId: string; operation: string; original: Record<string, unknown>; originalSha256: string; proposedValue: unknown
}>
const groupTargets = [
  ['checkpoint-sase', 'event:EV-checkpoint-2', 'evidence:TR-checkpoint-4'],
  ['optiv', 'event:EV-optiv-2', 'evidence:TR-optiv-3'],
  ['splunk', 'event:EV-splunk-1', 'evidence:TR-splunk-2'],
  ['zscaler', 'event:EV-zscaler-2', 'evidence:TR-zscaler-4'],
  ['expel', 'supplier:expel:lastRound', 'supplier:expel:ownership', 'evidence:TR-expel-2'],
]
const REVIEW_POLICIES = Object.fromEntries(groupTargets.map((_, index) => [`synthetic-non-admitting-${index}`, String(index + 1).repeat(64)]))

function fixtures() {
  const suppliers = groupTargets.map(([id]) => ({ id, name: id, domainIds: ['fixture'], kind: 'private' })) as TrackerSupplier[]
  for (const draft of drafts.filter((draft) => draft.targetId.startsWith('supplier:'))) {
    const [, id, field] = draft.targetId.split(':')
    Object.assign(suppliers.find((supplier) => supplier.id === id)!, { [field]: clone(draft.original) })
  }
  const events = drafts.filter((draft) => draft.targetId.startsWith('event:')).map((draft) => clone(draft.original) as unknown as TrackerEvent)
  events.push({ ...clone(events[0]), id: 'EV-checkpoint-4', date: '2025-12-08', text: 'Original December issuance.' })
  const evidence = drafts.filter((draft) => draft.targetId.startsWith('evidence:')).map((draft) => clone(draft.original) as unknown as EvidenceRecord)
  const inventories: FactualCorrectionInventories = { events, suppliers, evidence }
  const bundle: FactualCorrectionBundle = {
    schemaVersion: 1, enabled: true, policySha256: POLICY, checkedAt: '2026-10-24T06:23:00Z',
    groups: groupTargets.map(([supplierId, ...ids], i) => ({
      id: `synthetic-non-admitting-${i}`, supplierId, reasonCode: 'factual-correction', date: '2026-10-24',
      note: 'Correction, 24 October 2026. Synthetic mechanics fixture only.',
      targets: ids.map((id) => {
        const draft = drafts.find((draft) => draft.targetId === id)!
        return clone({ targetId: draft.targetId, operation: draft.operation, original: draft.original, originalSha256: draft.originalSha256, proposedValue: draft.proposedValue }) as FactualCorrectionTarget
      }),
      admission: { candidateSha256: 'b'.repeat(64), evidenceSetSha256: 'c'.repeat(64), policySha256: REVIEW_POLICIES[`synthetic-non-admitting-${i}`], admittedAt: '2026-10-24T06:00:00Z', reviewSha256: 'd'.repeat(64), result: 'accepted' },
    })),
  }
  return { inventories, bundle }
}

function freeze(value: unknown) {
  if (value !== null && typeof value === 'object') {
    Object.freeze(value)
    Object.values(value).forEach(freeze)
  }
}

function rejectedEverywhere(inventories: FactualCorrectionInventories, bundle: unknown, policy: string | null = POLICY, reviewPolicies: Readonly<Record<string, string>> | undefined = REVIEW_POLICIES) {
  assert.throws(() => validateBundle(bundle, policy, inventories, reviewPolicies), /Invalid factual corrections/)
  for (const project of [projectEvents, projectSuppliers, projectEvidence]) assert.throws(() => project(inventories, bundle, policy, reviewPolicies), /Invalid factual corrections/)
}

function target(bundle: FactualCorrectionBundle, id: string) {
  const found = bundle.groups.flatMap((group) => group.targets).find((target) => target.targetId === id)
  assert.ok(found)
  return found
}

describe('dated factual corrections (synthetic non-admitting replays)', () => {
  it('accepts the empty disabled fixture and preserves all eleven real draft shapes', () => {
    assert.deepEqual(disabled, { schemaVersion: 1, enabled: false, policySha256: null, checkedAt: null, groups: [] })
    const { inventories, bundle } = fixtures()
    assert.equal(bundle.groups.flatMap((group) => group.targets).length, 11)
    validateBundle(bundle, POLICY, inventories, REVIEW_POLICIES)
    assert.deepEqual(projectEvents(inventories, disabled, null), inventories.events)
    assert.deepEqual(projectSuppliers(inventories, disabled, null), inventories.suppliers)
    assert.deepEqual(projectEvidence(inventories, disabled, null), inventories.evidence)
  })

  it('retains immutable original events, supplier fields and evidence independently of returned objects', () => {
    const { inventories, bundle } = fixtures()
    const originals = clone(inventories)
    const originalBundle = clone(bundle)
    freeze(inventories)
    freeze(bundle)
    const events = projectEvents(inventories, bundle, POLICY, REVIEW_POLICIES)
    const suppliers = projectSuppliers(inventories, bundle, POLICY, REVIEW_POLICIES)
    const evidence = projectEvidence(inventories, bundle, POLICY, REVIEW_POLICIES)
    events[0].evidenceIds.push('output-only')
    suppliers.find((record) => record.id === 'expel')!.lastRound!.amount = 'output-only'
    evidence[0].tags.push('output-only')
    assert.deepEqual(inventories, originals)
    assert.deepEqual(bundle, originalBundle)
  })

  it('applies both Expel fields and its source excerpt coherently, preserving source retrieval dates', () => {
    const { inventories, bundle } = fixtures()
    const expel = projectSuppliers(inventories, bundle, POLICY, REVIEW_POLICIES).find((record) => record.id === 'expel')!
    const source = projectEvidence(inventories, bundle, POLICY, REVIEW_POLICIES).find((record) => record.id === 'TR-expel-2')!
    assert.deepEqual(expel.lastRound, target(bundle, 'supplier:expel:lastRound').proposedValue)
    assert.deepEqual(expel.ownership, target(bundle, 'supplier:expel:ownership').proposedValue)
    assert.match(expel.lastRound!.amount, /expanded Series E total/)
    assert.match(source.excerpt, /increased its Series E funding round/)
    assert.equal(source.retrievedAt, '2026-09-30')
    assert.equal(projectEvents(inventories, bundle, POLICY, REVIEW_POLICIES).filter((record) => record.type === 'funding').length, 0)
  })

  it('applies the Optiv date before filtering and keeps its quoted source and publication date consistent', () => {
    const { inventories, bundle } = fixtures()
    const effective = projectEvents(inventories, bundle, POLICY, REVIEW_POLICIES)
    assert.equal(effective.find((record) => record.id === 'EV-optiv-2')!.date, '2026-03-16')
    assert.equal(inventories.events.filter((record) => record.date >= '2026-04-01').some((record) => record.id === 'EV-optiv-2'), true)
    assert.equal(effective.filter((record) => record.date >= '2026-04-01').some((record) => record.id === 'EV-optiv-2'), false)
    const source = projectEvidence(inventories, bundle, POLICY, REVIEW_POLICIES).find((record) => record.id === 'TR-optiv-3')!
    assert.equal(source.publicationDate, '2026-03-16')
    assert.match(source.excerpt, /Upon closing/)
  })

  it('withdraws complete Check Point and Splunk events exactly once without inventing counted events', () => {
    const { inventories, bundle } = fixtures()
    const effective = projectEvents(inventories, bundle, POLICY, REVIEW_POLICIES)
    assert.equal(effective.length, inventories.events.length - 2)
    assert.equal(effective.some((record) => record.id === 'EV-checkpoint-2' || record.id === 'EV-splunk-1'), false)
    assert.equal(effective.filter((record) => record.id === 'EV-checkpoint-4').length, 1)
    assert.equal(effective.filter((record) => record.type === 'debt').length, 2)
    assert.deepEqual(projectEvents(inventories, bundle, POLICY, REVIEW_POLICIES), effective)
  })

  it('validates all targets before any projection, including an invalid final Expel evidence target', () => {
    const { inventories, bundle } = fixtures()
    const originals = clone(inventories)
    const expel = target(bundle, 'evidence:TR-expel-2')
    ;(expel.proposedValue as EvidenceRecord).retrievedAt = '2026-10-24'
    rejectedEverywhere(inventories, bundle)
    assert.deepEqual(inventories, originals)
  })

  it('rejects a missing raw target even when another inventory would project successfully', () => {
    const { inventories, bundle } = fixtures()
    inventories.evidence = inventories.evidence.filter((record) => record.id !== 'TR-expel-2')
    rejectedEverywhere(inventories, bundle)
  })

  it('uses canonical object equality while retaining array order and exact before-values', () => {
    const { inventories, bundle } = fixtures()
    const optiv = target(bundle, 'event:EV-optiv-2')
    optiv.original = Object.fromEntries(Object.entries(optiv.original).reverse()) as unknown as TrackerEvent
    validateBundle(bundle, POLICY, inventories, REVIEW_POLICIES)
    ;(optiv.original as TrackerEvent).text += ' changed'
    rejectedEverywhere(inventories, bundle)
    const next = fixtures()
    ;(target(next.bundle, 'supplier:expel:lastRound').original as Record<string, unknown>).evidenceIds = ['TR-expel-2', 'TR-expel-1']
    rejectedEverywhere(next.inventories, next.bundle)
  })

  for (const mutate of [
    (bundle: any) => { bundle.policySha256 = 'e'.repeat(64) },
    (bundle: any) => { bundle.policySha256 = null },
    (bundle: any) => { bundle.groups[0].admission.policySha256 = 'e'.repeat(64) },
    (bundle: any) => { bundle.groups[0].admission.result = 'pending' },
    (bundle: any) => { delete bundle.groups[0].admission.reviewSha256 },
    (bundle: any) => { bundle.groups[0].admission.reviewSha256 = 'stale-review' },
    (bundle: any) => { bundle.groups[0].admission.candidateSha256 = 'not-a-hash' },
    (bundle: any) => { bundle.groups[0].admission.evidenceSetSha256 = 'A'.repeat(64) },
    (bundle: any) => { bundle.groups[0].targets[0].originalSha256 = 'wrong-before-hash' },
    (bundle: any) => { bundle.groups[0].targets = [] },
    (bundle: any) => { bundle.groups = [] },
  ]) {
    it(`rejects invalid policy/admission/target metadata: ${mutate.toString()}`, () => {
      const { inventories, bundle } = fixtures()
      mutate(bundle)
      rejectedEverywhere(inventories, bundle)
    })
  }

  it('requires an explicit expected policy for enabled data', () => {
    const { inventories, bundle } = fixtures()
    rejectedEverywhere(inventories, bundle, null)
    rejectedEverywhere(inventories, bundle, 'f'.repeat(64))
  })

  it('requires the exact current expected review policy for every group without a global fallback', () => {
    const { inventories, bundle } = fixtures()
    const missing = { ...REVIEW_POLICIES }
    delete missing[bundle.groups[0].id]
    const renamed = { ...missing, 'different-group': REVIEW_POLICIES[bundle.groups[0].id] }
    for (const reviewPolicies of [
      undefined, {}, missing, renamed,
      { ...REVIEW_POLICIES, [bundle.groups[0].id]: 'stale-or-malformed' },
      { ...REVIEW_POLICIES, [bundle.groups[0].id]: 'e'.repeat(64) },
      { ...REVIEW_POLICIES, [bundle.groups[0].id]: POLICY },
      { ...REVIEW_POLICIES, unexpected: 'f'.repeat(64) },
    ]) {
      assert.throws(() => validateBundle(bundle, POLICY, inventories, reviewPolicies), /Invalid factual corrections/)
      for (const project of [projectEvents, projectSuppliers, projectEvidence]) {
        assert.throws(() => project(inventories, bundle, POLICY, reviewPolicies), /Invalid factual corrections/)
      }
    }
  })

  it('retains unchanged group admissions and rows when the global policy changes', () => {
    const { inventories, bundle } = fixtures()
    const originalRows = clone(bundle.groups)
    const prior = projectEvents(inventories, bundle, POLICY, REVIEW_POLICIES)
    const updatedGlobalPolicy = 'e'.repeat(64)
    bundle.policySha256 = updatedGlobalPolicy
    bundle.checkedAt = '2026-11-24T06:23:00Z'
    validateBundle(bundle, updatedGlobalPolicy, inventories, REVIEW_POLICIES)
    assert.deepEqual(projectEvents(inventories, bundle, updatedGlobalPolicy, REVIEW_POLICIES), prior)
    assert.deepEqual(bundle.groups, originalRows)
    assert.ok(bundle.groups.every((group) => group.admission.policySha256 !== bundle.policySha256))
    rejectedEverywhere(inventories, bundle, POLICY)
  })

  it('rejects populated or relabelled disabled bundles', () => {
    const { inventories, bundle } = fixtures()
    rejectedEverywhere(inventories, { ...bundle, enabled: false })
    rejectedEverywhere(inventories, { ...disabled, checkedAt: '2026-10-24T06:23:00Z' })
    rejectedEverywhere(inventories, { ...disabled, policySha256: POLICY })
  })

  it('rejects invalid calendar dates, invalid UTC times and undated notes', () => {
    for (const mutate of [
      (bundle: any) => { bundle.groups[0].date = '2026-02-30' },
      (bundle: any) => { bundle.checkedAt = '2026-10-24T25:00:00Z' },
      (bundle: any) => { bundle.groups[0].admission.admittedAt = '2026-10-24T06:24:00Z' },
      (bundle: any) => { bundle.groups[0].date = '2026-10-23' },
      (bundle: any) => { bundle.groups[0].note = 'Correction, {date}.' },
      (bundle: any) => { bundle.groups[0].note = 'Correction, [publication date].' },
      (bundle: any) => { bundle.groups[1].targets[0].proposedValue.date = '2026-13-01' },
    ]) {
      const { inventories, bundle } = fixtures()
      mutate(bundle)
      rejectedEverywhere(inventories, bundle)
    }
  })

  it('rejects duplicate groups, targets across groups and duplicate raw identities', () => {
    for (const mutate of [
      (bundle: any, _inventories: any) => { bundle.groups.push(clone(bundle.groups[0])) },
      (bundle: any, _inventories: any) => { bundle.groups[1].targets.push(clone(bundle.groups[0].targets[0])) },
      (_bundle: any, inventories: any) => { inventories.events.push(clone(inventories.events[0])) },
    ]) {
      const { inventories, bundle } = fixtures()
      mutate(bundle, inventories)
      rejectedEverywhere(inventories, bundle)
    }
  })

  it('rejects supplier identity, revenue and nested-patch targets and wrong target types', () => {
    for (const targetId of ['supplier:expel:name', 'supplier:expel:revenue', 'supplier:expel:lastRound:amount', 'owner:expel', 'event:EV-optiv-2:date']) {
      const { inventories, bundle } = fixtures()
      ;(target(bundle, 'supplier:expel:lastRound') as any).targetId = targetId
      rejectedEverywhere(inventories, bundle)
    }
    const { inventories, bundle } = fixtures()
    ;(target(bundle, 'supplier:expel:lastRound').proposedValue as any).revenue = { value: '$1 billion' }
    rejectedEverywhere(inventories, bundle)
  })

  it('rejects event replacement identity, supplier, type, rung and partial-record changes', () => {
    for (const [key, value] of [['id', 'EV-new'], ['supplierId', 'expel'], ['type', 'funding'], ['rung', 2], ['text', null]]) {
      const { inventories, bundle } = fixtures()
      ;(target(bundle, 'event:EV-optiv-2').proposedValue as any)[key as string] = value
      rejectedEverywhere(inventories, bundle)
    }
  })

  it('rejects supplier/evidence withdrawals and event withdrawals with a non-null after-value', () => {
    for (const targetId of ['supplier:expel:ownership', 'evidence:TR-expel-2', 'event:EV-checkpoint-2']) {
      const { inventories, bundle } = fixtures()
      const change = target(bundle, targetId) as any
      change.operation = 'withdraw'
      change.proposedValue = targetId.startsWith('event:') ? {} : null
      rejectedEverywhere(inventories, bundle)
    }
  })

  it('protects every evidence identity, source, URL, attribution and retrieval field', () => {
    for (const [key, value] of [
      ['id', 'TR-forged'], ['canonicalUrl', 'https://example.test/changed'], ['organization', 'Another company'],
      ['sourceClass', 'IR'], ['tags', ['changed']], ['conflictingEvidenceIds', ['TR-other']], ['artifactLabel', 'changed'],
      ['interpretation', 'A new machine judgment'], ['retrievedAt', '2026-10-24'],
      ['retrieval', { finalUrl: 'https://example.test/', sha256: 'f'.repeat(64), fetchedAt: '2026-10-24T00:00:00Z' }],
      ['sourceAttributions', [{ organization: 'Changed', publicationDate: '2026-01-01', economicPeriod: 'changed' }]],
    ]) {
      const { inventories, bundle } = fixtures()
      ;(target(bundle, 'evidence:TR-expel-2').proposedValue as any)[key as string] = value
      rejectedEverywhere(inventories, bundle)
    }
  })

  it('rejects altered existing retrieval receipts and malformed receipt dates/hashes', () => {
    for (const change of ['time', 'hash', 'url', 'delete', 'malformed-time', 'malformed-hash']) {
      const { inventories, bundle } = fixtures()
      const raw = inventories.evidence.find((record) => record.id === 'TR-expel-2')!
      const correction = target(bundle, 'evidence:TR-expel-2')
      const receipt = { finalUrl: raw.canonicalUrl, sha256: 'e'.repeat(64), fetchedAt: '2026-10-23T04:14:50.674018Z' }
      raw.retrieval = clone(receipt)
      ;(correction.original as EvidenceRecord).retrieval = clone(receipt)
      ;(correction.proposedValue as EvidenceRecord).retrieval = clone(receipt)
      const after = (correction.proposedValue as EvidenceRecord).retrieval!
      if (change === 'time') after.fetchedAt = '2026-10-24T04:14:50Z'
      if (change === 'hash') after.sha256 = 'f'.repeat(64)
      if (change === 'url') after.finalUrl += '?changed=1'
      if (change === 'delete') delete (correction.proposedValue as EvidenceRecord).retrieval
      if (change.startsWith('malformed')) {
        for (const record of [raw, correction.original, correction.proposedValue] as EvidenceRecord[]) {
          if (change === 'malformed-time') record.retrieval!.fetchedAt = '2026-02-30T00:00:00Z'
          else record.retrieval!.sha256 = 'invalid'
        }
      }
      rejectedEverywhere(inventories, bundle)
    }
  })

  it('rejects unknown group/admission metadata without granting owner attribution', () => {
    const { inventories, bundle } = fixtures()
    ;(bundle.groups[0] as any).approvedBy = 'Jesse Pike'
    rejectedEverywhere(inventories, bundle)
    delete (bundle.groups[0] as any).approvedBy
    ;(bundle.groups[0].admission as any).checks = { entity: 'pass' }
    rejectedEverywhere(inventories, bundle)
  })

  it('does not expire an acknowledged historical correction on subsequent check dates', () => {
    const { inventories, bundle } = fixtures()
    bundle.checkedAt = '2027-10-24T06:23:00Z'
    validateBundle(bundle, POLICY, inventories, REVIEW_POLICIES)
    assert.equal(bundle.groups[0].date, '2026-10-24')
    assert.equal(bundle.groups[0].admission.admittedAt, '2026-10-24T06:00:00Z')
  })

  it('keeps the legacy owner-approved issue/thesis correction records independent', () => {
    const legacy = corrections.filter((record) => ['C-2026-09-20-01', 'C-2026-09-21-01'].includes(record.id))
    const before = clone(legacy)
    const { inventories, bundle } = fixtures()
    projectEvents(inventories, bundle, POLICY, REVIEW_POLICIES)
    projectSuppliers(inventories, bundle, POLICY, REVIEW_POLICIES)
    projectEvidence(inventories, bundle, POLICY, REVIEW_POLICIES)
    assert.deepEqual(legacy, before)
    assert.equal(legacy.length, 2)
    assert.ok(legacy.every((record) => record.approvedBy === 'Jesse Pike'))
    assert.ok(bundle.groups.every((group: FactualCorrectionGroup) => !Object.hasOwn(group, 'approvedBy')))
  })
})
