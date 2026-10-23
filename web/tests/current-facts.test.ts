import assert from 'node:assert/strict'
import { describe, it } from 'node:test'
import { assertCurrentFacts, actualCurrentFacts, expectedCurrentFacts, loadCurrentFactInputs, verifyCurrentFacts } from '../scripts/verify-current-facts.ts'
import type { CurrentFactInputs } from '../scripts/verify-current-facts.ts'
import type { EvidenceRecord } from '../src/data/types.ts'
import type { TrackerEvent } from '../src/data/tracker/events.ts'
import type { TrackerSupplier } from '../src/data/tracker/suppliers.ts'

const copy = <T>(value: T): T => structuredClone(value)

function syntheticInputs(): CurrentFactInputs {
  const evidence: EvidenceRecord = { id: 'SYN-source', title: 'Synthetic source', organization: 'Synthetic', publicationDate: '2026-10-20',
    economicPeriod: 'Synthetic', canonicalUrl: 'https://example.invalid/', excerpt: 'Synthetic original excerpt.', sourceClass: 'OFFICIAL',
    interpretation: '', limitations: '', conflictingEvidenceIds: [], artifactLabel: 'Synthetic non-admitting', tags: [] }
  const event: TrackerEvent = { id: 'SYN-event', supplierId: 'synthetic', date: '2026-10-20', type: 'funding', text: 'Synthetic original event.', evidenceIds: [evidence.id], rung: 1 }
  const supplier: TrackerSupplier = { id: 'synthetic', name: 'Synthetic', domainIds: [], kind: 'private',
    ownership: { status: 'Original ownership.', evidenceIds: [evidence.id] },
    headlineMetric: { label: 'Metric', value: 'Original', period: 'Original', evidenceIds: [evidence.id] },
    lastRound: { date: '2026-01-01', stage: 'Synthetic', amount: '$1', evidenceIds: [evidence.id] } }
  return {
    originals: { events: [event], suppliers: [supplier, { ...copy(supplier), id: 'public', edgarId: 'public' }], evidence: [evidence] },
    corrections: { schemaVersion: 1, enabled: false, policySha256: null, checkedAt: null, groups: [] }, expectedPolicySha256: null,
    daily: { enabled: true, supplierUpdates: {}, events: [{ ...copy(event), id: 'SYN-daily' }], evidence: [{ ...copy(evidence), id: 'SYN-daily-source' }] },
    filingEvents: [{ ...copy(event), id: 'SYN-filing' }], filingEvidence: [{ ...copy(evidence), id: 'SYN-filing-source' }],
    edgarEvidence: [{ ...copy(evidence), id: 'SYN-sec-source' }], applySecRevenue: (supplier) => supplier, lastChecked: '2026-10-23',
  }
}

describe('runtime exported current fact assertions', () => {
  it('binds the real application exports to fresh disk inventories and generated overlays', () => {
    verifyCurrentFacts()
    assertCurrentFacts(actualCurrentFacts(), expectedCurrentFacts(loadCurrentFactInputs()))
  })

  for (const mutation of ['ownership', 'event-text', 'source-excerpt', 'omit-event', 'raw-history', 'evidence-map', 'supplier-order']) {
    it(`rejects ${mutation} overrides while original JSON, policy and correction inputs remain unchanged`, () => {
      const inputs = loadCurrentFactInputs()
      const before = copy(inputs.originals)
      const policy = inputs.expectedPolicySha256
      const reviewPolicies = copy(inputs.expectedReviewPolicySha256ByGroup)
      const bundle = copy(inputs.corrections)
      const expected = expectedCurrentFacts(inputs)
      const actual = copy(expected)
      if (mutation === 'ownership') actual.trackerSuppliers.find((record) => record.id === 'expel')!.ownership!.status += ' forged static override'
      if (mutation === 'event-text') actual.retainedTrackerEvents.find((record) => record.id === 'EV-optiv-2')!.text += ' forged static override'
      if (mutation === 'source-excerpt') actual.evidenceRecords.find((record) => record.id === 'TR-expel-2')!.excerpt += ' forged static override'
      if (mutation === 'omit-event') actual.trackerEvents = actual.trackerEvents.slice(1)
      if (mutation === 'raw-history') actual.handCollectedEvents[0].text += ' changed history'
      if (mutation === 'evidence-map') actual.evidenceById = { ...actual.evidenceById, 'TR-expel-2': { ...actual.evidenceById['TR-expel-2'], excerpt: 'Map-only replacement.' } }
      if (mutation === 'supplier-order') actual.trackerSuppliers = [...actual.trackerSuppliers].reverse()
      assert.throws(() => assertCurrentFacts(actual, expected), /Current facts refused/)
      assert.deepEqual(inputs.originals, before)
      assert.equal(inputs.expectedPolicySha256, policy)
      assert.deepEqual(inputs.expectedReviewPolicySha256ByGroup, reviewPolicies)
      assert.deepEqual(inputs.corrections, bundle)
    })
  }

  it('rejects a mutation shared by raw history and the current view', () => {
    const inputs = syntheticInputs()
    const expected = expectedCurrentFacts(inputs)
    const actual = copy(expected)
    const shared = actual.handCollectedEvents[0]
    actual.retainedTrackerEvents = [shared, ...actual.retainedTrackerEvents.slice(1)]
    actual.trackerEvents = [shared, ...actual.trackerEvents.slice(1)]
    shared.text = 'Aliased static mutation.'
    assert.throws(() => assertCurrentFacts(actual, expected), /handCollectedEvents/)
    assert.equal(inputs.originals.events[0].text, 'Synthetic original event.')
  })

  it('reconstructs an enabled atomic correction before overlays and the event window (synthetic, non-admitting)', () => {
    const inputs = syntheticInputs()
    const event = inputs.originals.events[0]
    const supplier = inputs.originals.suppliers[0]
    const source = inputs.originals.evidence[0]
    const policy = 'a'.repeat(64)
    const reviewPolicy = '2'.repeat(64)
    inputs.expectedPolicySha256 = policy
    inputs.expectedReviewPolicySha256ByGroup = { 'synthetic-correction': reviewPolicy }
    inputs.corrections = {
      schemaVersion: 1, enabled: true, policySha256: policy, checkedAt: '2026-10-23T12:00:00Z',
      groups: [{ id: 'synthetic-correction', supplierId: supplier.id, reasonCode: 'synthetic-only', date: '2026-10-23',
        note: 'Synthetic mechanics only, 2026-10-23.', targets: [
          { targetId: `event:${event.id}`, operation: 'replace', original: copy(event), originalSha256: 'b'.repeat(64), proposedValue: { ...copy(event), date: '2025-10-22', text: 'Corrected synthetic event.' } },
          { targetId: `supplier:${supplier.id}:ownership`, operation: 'replace', original: copy(supplier.ownership), originalSha256: 'c'.repeat(64), proposedValue: { ...copy(supplier.ownership), status: 'Corrected synthetic ownership.' } },
          { targetId: `evidence:${source.id}`, operation: 'replace', original: copy(source), originalSha256: 'd'.repeat(64), proposedValue: { ...copy(source), excerpt: 'Corrected synthetic excerpt.' } },
        ], admission: { candidateSha256: 'e'.repeat(64), evidenceSetSha256: 'f'.repeat(64), policySha256: reviewPolicy, admittedAt: '2026-10-23T11:00:00Z', reviewSha256: '1'.repeat(64), result: 'accepted' } }],
    }
    const originals = copy(inputs.originals)
    const expected = expectedCurrentFacts(inputs)
    assert.equal(expected.retainedTrackerEvents[0].text, 'Corrected synthetic event.')
    assert.equal(expected.trackerEvents.some((record) => record.id === event.id), false)
    assert.equal(expected.trackerSuppliers[0].ownership!.status, 'Corrected synthetic ownership.')
    assert.equal(expected.evidenceById[source.id].excerpt, 'Corrected synthetic excerpt.')
    assert.deepEqual(expected.handCollectedEvents, originals.events)
    assert.deepEqual(expected.manualTrackerSuppliers, originals.suppliers)
    assert.deepEqual(expected.handWrittenEvidenceRecords, originals.evidence)
    assertCurrentFacts(copy(expected), expected)
    const overridden = copy(expected)
    overridden.trackerSuppliers[0].ownership = copy(supplier.ownership)
    assert.throws(() => assertCurrentFacts(overridden, expected), /trackerSuppliers/)
    assert.deepEqual(inputs.originals, originals)
    delete inputs.expectedReviewPolicySha256ByGroup
    assert.throws(() => expectedCurrentFacts(inputs), /expected group review policies/)
    inputs.expectedReviewPolicySha256ByGroup = { 'synthetic-correction': policy }
    assert.throws(() => expectedCurrentFacts(inputs), /current group-policy admission/)
    inputs.expectedReviewPolicySha256ByGroup = { 'synthetic-correction': reviewPolicy }
    const correctedBundle = inputs.corrections as { policySha256: string; groups: unknown[] }
    const historicalRows = copy(correctedBundle.groups)
    correctedBundle.policySha256 = '3'.repeat(64)
    inputs.expectedPolicySha256 = correctedBundle.policySha256
    assert.deepEqual(expectedCurrentFacts(inputs), expected)
    assert.deepEqual(correctedBundle.groups, historicalRows)
  })

  it('checks original supplier and evidence arrays as well as displayed views', () => {
    const expected = expectedCurrentFacts(syntheticInputs())
    const supplierChanged = copy(expected)
    supplierChanged.manualTrackerSuppliers[0].name = 'Changed original name'
    assert.throws(() => assertCurrentFacts(supplierChanged, expected), /manualTrackerSuppliers/)
    const evidenceChanged = copy(expected)
    evidenceChanged.handWrittenEvidenceRecords[0].excerpt = 'Changed original excerpt'
    assert.throws(() => assertCurrentFacts(evidenceChanged, expected), /handWrittenEvidenceRecords/)
  })

  it('applies daily headline updates only to non-SEC suppliers and replaces rounds only with newer dates', () => {
    const inputs = syntheticInputs()
    const headline = { label: 'Daily metric', value: 'New', period: 'New', evidenceIds: ['SYN-daily-source'] }
    const newer = { date: '2026-02-01', stage: 'Synthetic new', amount: '$2', evidenceIds: ['SYN-daily-source'] }
    inputs.daily.supplierUpdates = { synthetic: { headlineMetric: headline, lastRound: newer }, public: { headlineMetric: headline, lastRound: { ...newer, date: '2025-12-31' } } }
    const before = copy(inputs.originals)
    const expected = expectedCurrentFacts(inputs)
    assert.deepEqual(expected.trackerSuppliers[0].headlineMetric, headline)
    assert.deepEqual(expected.trackerSuppliers[0].lastRound, newer)
    assert.deepEqual(expected.trackerSuppliers[1].headlineMetric, inputs.originals.suppliers[1].headlineMetric)
    assert.deepEqual(expected.trackerSuppliers[1].lastRound, inputs.originals.suppliers[1].lastRound)
    assert.deepEqual(inputs.originals, before)
    inputs.daily.supplierUpdates.synthetic.lastRound!.date = '2026-01-01'
    assert.deepEqual(expectedCurrentFacts(inputs).trackerSuppliers[0].lastRound, inputs.originals.suppliers[0].lastRound)
  })

  it('retains event/evidence merge order and uses the same trailing-year boundaries', () => {
    const inputs = syntheticInputs()
    inputs.originals.events = [
      { ...inputs.originals.events[0], id: 'SYN-old', date: '2025-10-22' },
      { ...inputs.originals.events[0], id: 'SYN-start', date: '2025-10-23' },
      { ...inputs.originals.events[0], id: 'SYN-end', date: '2026-10-23' },
      { ...inputs.originals.events[0], id: 'SYN-future', date: '2026-10-24' },
    ]
    const expected = expectedCurrentFacts(inputs)
    assert.deepEqual(expected.retainedTrackerEvents.map((record) => record.id), ['SYN-old', 'SYN-start', 'SYN-end', 'SYN-future', 'SYN-filing', 'SYN-daily'])
    assert.deepEqual(expected.trackerEvents.map((record) => record.id), ['SYN-start', 'SYN-end', 'SYN-filing', 'SYN-daily'])
    assert.deepEqual(expected.evidenceRecords.map((record) => record.id), ['SYN-source', 'SYN-sec-source', 'SYN-filing-source', 'SYN-daily-source'])
    const reordered = copy(expected)
    reordered.evidenceRecords = [...reordered.evidenceRecords].reverse()
    assert.throws(() => assertCurrentFacts(reordered, expected), /evidenceRecords/)
  })

  it('ignores all disabled daily values and rejects unsupported enabled daily fields', () => {
    const inputs = syntheticInputs()
    inputs.daily.enabled = false
    inputs.daily.supplierUpdates.synthetic = { headlineMetric: { label: 'Unused', value: 'Unused', period: 'Unused', evidenceIds: [] } }
    const expected = expectedCurrentFacts(inputs)
    assert.deepEqual(expected.trackerSuppliers, inputs.originals.suppliers)
    assert.deepEqual(expected.retainedTrackerEvents.map((record) => record.id), ['SYN-event', 'SYN-filing'])
    assert.deepEqual(expected.evidenceRecords.map((record) => record.id), ['SYN-source', 'SYN-sec-source', 'SYN-filing-source'])
    inputs.daily.enabled = true
    Object.assign(inputs.daily.supplierUpdates.synthetic, { ownership: { status: 'Forbidden', evidenceIds: [] } })
    assert.throws(() => expectedCurrentFacts(inputs), /unsupported daily supplier field/)
  })
})
