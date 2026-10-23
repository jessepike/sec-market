/** Bind the application's actual exports to the immutable inventories and admitted overlays. */
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'
import { handWrittenEvidenceRecords, evidenceRecords, evidenceById } from '../src/data/evidence.ts'
import { runStatus } from '../src/data/runStatus.ts'
import { handCollectedEvents, retainedTrackerEvents, trackerEvents } from '../src/data/tracker/events.ts'
import { manualTrackerSuppliers, trackerSuppliers } from '../src/data/tracker/suppliers.ts'
import { edgarRevenueEvidence, withEdgarRevenue } from '../src/data/tracker/edgarRevenue.ts'
import { projectEvents, projectSuppliers, projectEvidence } from '../src/data/tracker/factualCorrections.ts'
import type { FactualCorrectionInventories } from '../src/data/tracker/factualCorrections.ts'
import type { TrackerEvent } from '../src/data/tracker/events.ts'
import type { TrackerSupplier } from '../src/data/tracker/suppliers.ts'
import type { EvidenceRecord } from '../src/data/types.ts'

export interface CurrentFactViews {
  handCollectedEvents: readonly TrackerEvent[]
  retainedTrackerEvents: readonly TrackerEvent[]
  trackerEvents: readonly TrackerEvent[]
  manualTrackerSuppliers: readonly TrackerSupplier[]
  trackerSuppliers: readonly TrackerSupplier[]
  handWrittenEvidenceRecords: readonly EvidenceRecord[]
  evidenceRecords: readonly EvidenceRecord[]
  evidenceById: Readonly<Record<string, EvidenceRecord>>
}

export interface DailyFactInput {
  enabled: boolean
  supplierUpdates: Record<string, Pick<Partial<TrackerSupplier>, 'headlineMetric' | 'lastRound'>>
  events: readonly TrackerEvent[]
  evidence: readonly EvidenceRecord[]
}

export interface CurrentFactInputs {
  originals: FactualCorrectionInventories
  corrections: unknown
  expectedPolicySha256: string | null
  daily: DailyFactInput
  filingEvents: readonly TrackerEvent[]
  filingEvidence: readonly EvidenceRecord[]
  edgarEvidence: readonly EvidenceRecord[]
  applySecRevenue: (supplier: TrackerSupplier) => TrackerSupplier
  lastChecked: string
}

const copy = <T>(value: T): T => structuredClone(value)

/**
 * Reconstruct the expected values independently of correctionData and daily.ts.
 * The separate SEC certification gate verifies applySecRevenue's filed values.
 */
export function expectedCurrentFacts(inputs: CurrentFactInputs): CurrentFactViews {
  const { originals, corrections, expectedPolicySha256, daily } = inputs
  const correctedEvents = projectEvents(originals, corrections, expectedPolicySha256)
  const correctedSuppliers = projectSuppliers(originals, corrections, expectedPolicySha256)
  const correctedEvidence = projectEvidence(originals, corrections, expectedPolicySha256)
  const expectedSuppliers = correctedSuppliers.map((supplier) => {
    const current = copy(supplier)
    if (daily.enabled) {
      const update = daily.supplierUpdates[supplier.id]
      if (update) {
        assert.ok(Object.keys(update).every((key) => key === 'headlineMetric' || key === 'lastRound'), 'Current facts refused: unsupported daily supplier field')
        if (!supplier.edgarId && update.headlineMetric) current.headlineMetric = copy(update.headlineMetric)
        if (update.lastRound && (!supplier.lastRound || update.lastRound.date > supplier.lastRound.date)) current.lastRound = copy(update.lastRound)
      }
    }
    return inputs.applySecRevenue(current)
  })
  const retained = [...correctedEvents, ...copy(inputs.filingEvents), ...copy(daily.enabled ? daily.events : [])]
  const end = Date.parse(`${inputs.lastChecked}T00:00:00Z`)
  assert.ok(Number.isFinite(end), 'Current facts refused: invalid event window')
  const evidence = [...correctedEvidence, ...copy(inputs.edgarEvidence), ...copy(inputs.filingEvidence), ...copy(daily.enabled ? daily.evidence : [])]
  return {
    handCollectedEvents: copy(originals.events),
    retainedTrackerEvents: retained,
    trackerEvents: retained.filter((event) => {
      const date = Date.parse(`${event.date}T00:00:00Z`)
      return date >= end - 365 * 86400000 && date <= end
    }),
    manualTrackerSuppliers: copy(originals.suppliers),
    trackerSuppliers: expectedSuppliers,
    handWrittenEvidenceRecords: copy(originals.evidence),
    evidenceRecords: evidence,
    evidenceById: Object.fromEntries(evidence.map((record) => [record.id, record])),
  }
}

/** Exact array order and every exported record must match; original objects are checked too. */
export function assertCurrentFacts(actual: CurrentFactViews, expected: CurrentFactViews): void {
  for (const key of Object.keys(expected) as Array<keyof CurrentFactViews>) {
    assert.deepStrictEqual(actual[key], expected[key], `Current facts refused: ${key} differs from the admitted projection and generated overlays`)
  }
}

/** Parse fresh bytes rather than sharing the JSON module objects used by application imports. */
export function loadCurrentFactInputs(web = resolve(dirname(fileURLToPath(import.meta.url)), '..')): CurrentFactInputs {
  const read = <T>(path: string): T => JSON.parse(readFileSync(resolve(web, path), 'utf8')) as T
  const policy = read<{ policySha256: string }>('src/data/tracker/factualCorrectionPolicy.json')
  return {
    originals: read<FactualCorrectionInventories>('src/data/tracker/originals.json'),
    corrections: read<unknown>('src/data/generated/factualCorrections.json'),
    expectedPolicySha256: policy.policySha256,
    daily: read<DailyFactInput>('src/data/generated/dailyMarket.json'),
    filingEvents: read<TrackerEvent[]>('src/data/generated/filingEvents.json'),
    filingEvidence: read<EvidenceRecord[]>('src/data/generated/filingEvidence.json'),
    edgarEvidence: copy(edgarRevenueEvidence), applySecRevenue: withEdgarRevenue,
    lastChecked: runStatus.lastChecked,
  }
}

export function actualCurrentFacts(): CurrentFactViews {
  return { handCollectedEvents, retainedTrackerEvents, trackerEvents, manualTrackerSuppliers, trackerSuppliers, handWrittenEvidenceRecords, evidenceRecords, evidenceById }
}

export function verifyCurrentFacts(): void {
  assertCurrentFacts(actualCurrentFacts(), expectedCurrentFacts(loadCurrentFactInputs()))
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  try {
    verifyCurrentFacts()
    console.log('Current facts verified: original histories and all exported event, supplier and evidence views match.')
  } catch (error) {
    console.error(error instanceof Error ? error.message : 'Current facts verification failed')
    process.exitCode = 2
  }
}
