import raw from '../generated/dailyMarket.json' with { type: 'json' }
import { heldOnboardingIds } from './graduation'
import type { EvidenceRecord } from '../types'
import type { TrackerEvent } from './events'
import type { TrackerSupplier } from './suppliers'

type Update = Pick<Partial<TrackerSupplier>, 'headlineMetric' | 'lastRound'>
interface Snapshot {
  schemaVersion: number
  enabled: boolean
  runId: string | null
  checkedAt: string | null
  contractSha256: string | null
  supplierUpdates: Record<string, Update>
  events: TrackerEvent[]
  evidence: EvidenceRecord[]
  coverage: Record<string, unknown> | null
  reviewQueue: Array<{ supplierId: string; factId: string; reason: string }>
}
export const dailySnapshot = raw as unknown as Snapshot
// Suppliers still onboarding (D-138) are collected by the pipeline but publish
// nothing until they graduate: their daily events, and evidence used only by
// them, stay out of every page and export.
export const onboardingSupplierIds: ReadonlySet<string> = new Set(heldOnboardingIds)
const allEvents = dailySnapshot.enabled ? dailySnapshot.events : []
const allUpdates = Object.entries(dailySnapshot.enabled ? dailySnapshot.supplierUpdates ?? {} : {})
const updateEvidence = (u: Update) => [...(u.headlineMetric?.evidenceIds ?? []), ...(u.lastRound?.evidenceIds ?? [])]
const liveEvents = allEvents.filter((e) => !onboardingSupplierIds.has(e.supplierId))
const liveEvidenceIds = new Set([
  ...liveEvents.flatMap((e) => e.evidenceIds),
  ...allUpdates.filter(([sid]) => !onboardingSupplierIds.has(sid)).flatMap(([, u]) => updateEvidence(u)),
])
const heldEvidenceIds = new Set([
  ...allEvents.filter((e) => onboardingSupplierIds.has(e.supplierId)).flatMap((e) => e.evidenceIds),
  ...allUpdates.filter(([sid]) => onboardingSupplierIds.has(sid)).flatMap(([, u]) => updateEvidence(u)),
].filter((id) => !liveEvidenceIds.has(id)))
export const dailyEvidence: EvidenceRecord[] = dailySnapshot.enabled ? dailySnapshot.evidence.filter((e) => !heldEvidenceIds.has(e.id)) : []
export const dailyEvents: TrackerEvent[] = liveEvents

interface DailyCoverageBase {
  checkedAt: string
  complete: boolean
  successfulTasks: number
  requiredTasks: number
  overdueHours: number
  automationEnabled: boolean
  lastCollectionAt: string
  validUntil: string | null
}
interface LegacyDailyCoverage extends DailyCoverageBase {
  schemaVersion?: 1
  measure?: string
}
export interface ReviewProgress {
  evaluated?: boolean
  status?: string
  complete: boolean
  inventoryDocuments: number
  reviewedDocuments: number
  pendingDocuments: number
  heldDocuments: number
}
export interface IntakeDailyCoverage extends DailyCoverageBase {
  schemaVersion: 2
  measure: 'daily_source_intake_v2'
  gapTaskIds: string[]
  intake: {
    evaluated: boolean
    status: 'collected' | 'uncollected'
    measure: 'daily_source_intake_v2'
    successfulTasks: number
    requiredTasks: number
    gapTaskIds: string[]
    complete: boolean
  }
  processing: ReviewProgress & { changedDocuments: number; unknownDateDocuments: number; archivedDocuments?: number; notAboutSupplierDocuments?: number }
  historicalReview: ReviewProgress
}
export type DailyCoverage = LegacyDailyCoverage | IntakeDailyCoverage

function record(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === 'object' && !Array.isArray(value)
}
function count(value: unknown): value is number {
  return typeof value === 'number' && Number.isSafeInteger(value) && value >= 0
}
function requireCoverage(condition: unknown): asserts condition {
  if (!condition) throw new Error('Daily coverage schema or measure is inconsistent')
}
function reviewProgress(value: unknown, processing: boolean): void {
  requireCoverage(record(value) && typeof value.complete === 'boolean')
  requireCoverage(value.evaluated === undefined || typeof value.evaluated === 'boolean')
  requireCoverage(value.evaluated !== false || (value.status === 'uncollected' && value.complete === false))
  for (const key of ['inventoryDocuments', 'reviewedDocuments', 'pendingDocuments', 'heldDocuments']) {
    requireCoverage(count(value[key]))
  }
  const progress = value as unknown as ReviewProgress
  requireCoverage(progress.reviewedDocuments + progress.pendingDocuments === progress.inventoryDocuments &&
    progress.heldDocuments <= progress.reviewedDocuments)
  requireCoverage(!progress.complete || (progress.pendingDocuments === 0 && (!processing || progress.heldDocuments === 0)))
  if (processing) {
    requireCoverage(count(value.changedDocuments) && count(value.unknownDateDocuments) &&
      value.changedDocuments + value.unknownDateDocuments <= progress.inventoryDocuments)
    // Present only under a history window; archived documents sit outside this inventory.
    for (const key of ['archivedDocuments', 'notAboutSupplierDocuments']) requireCoverage(value[key] === undefined || count(value[key]))
    requireCoverage((value.notAboutSupplierDocuments === undefined ? 0 : (value.notAboutSupplierDocuments as number)) <= progress.reviewedDocuments)
  }
}

/** Version 2 aliases measure intake only. Never infer review completion from them. */
export function readDailyCoverage(value: unknown): DailyCoverage | null {
  if (value === null) return null
  requireCoverage(record(value) && typeof value.checkedAt === 'string' && typeof value.lastCollectionAt === 'string' &&
    typeof value.complete === 'boolean' && typeof value.automationEnabled === 'boolean' && count(value.successfulTasks) &&
    count(value.requiredTasks) && value.requiredTasks > 0 && value.successfulTasks <= value.requiredTasks && count(value.overdueHours) &&
    (value.validUntil === null || typeof value.validUntil === 'string'))
  if (value.schemaVersion === undefined || value.schemaVersion === 1) {
    requireCoverage(value.intake === undefined && value.processing === undefined && value.historicalReview === undefined &&
      value.measure !== 'daily_source_intake_v2')
    return value as unknown as LegacyDailyCoverage
  }
  requireCoverage(value.schemaVersion === 2 && value.measure === 'daily_source_intake_v2' && record(value.intake))
  const intake = value.intake
  requireCoverage(Array.isArray(intake.gapTaskIds) && Array.isArray(value.gapTaskIds))
  const intakeGaps = intake.gapTaskIds
  requireCoverage(typeof intake.evaluated === 'boolean' &&
    (intake.evaluated ? intake.status === 'collected' :
      intake.status === 'uncollected' && value.successfulTasks === 0 && value.complete === false && value.validUntil === null))
  requireCoverage(intake.measure === value.measure && intake.successfulTasks === value.successfulTasks &&
    intake.requiredTasks === value.requiredTasks && intake.complete === value.complete &&
    Array.isArray(intake.gapTaskIds) && intake.gapTaskIds.every(id => typeof id === 'string') &&
    new Set(intake.gapTaskIds).size === intake.gapTaskIds.length &&
    intake.gapTaskIds.length === value.requiredTasks - value.successfulTasks &&
    Array.isArray(value.gapTaskIds) && value.gapTaskIds.length === intake.gapTaskIds.length &&
    new Set(value.gapTaskIds).size === value.gapTaskIds.length &&
    value.gapTaskIds.every(id => intakeGaps.includes(id)) &&
    (!value.complete || intake.gapTaskIds.length === 0))
  reviewProgress(value.processing, true)
  reviewProgress(value.historicalReview, false)
  return value as unknown as IntakeDailyCoverage
}
export const dailyCoverage = dailySnapshot.enabled ? readDailyCoverage(dailySnapshot.coverage) : null

export function dailyOverdue(coverage: DailyCoverage, now: number): boolean {
  const age = (now - Date.parse(coverage.checkedAt)) / 3600000
  const deadline = Date.parse(coverage.validUntil ?? '')
  return !Number.isFinite(age) || !Number.isFinite(deadline) || age < 0 || now > deadline
}

export function withDailyData(supplier: TrackerSupplier): TrackerSupplier {
  if (!dailySnapshot.enabled) return supplier
  const update = dailySnapshot.supplierUpdates[supplier.id]
  if (!update) return supplier
  if (Object.keys(update).some(k => k !== 'headlineMetric' && k !== 'lastRound')) throw new Error('Daily snapshot attempted an unsupported supplier mutation')
  const round = update.lastRound && (!supplier.lastRound || update.lastRound.date > supplier.lastRound.date) ? update.lastRound : supplier.lastRound
  // Certified revenue and supplier identity are never replaced by generic extraction.
  return { ...supplier, ...(!supplier.edgarId && update.headlineMetric ? { headlineMetric: update.headlineMetric } : {}), ...(round ? { lastRound: round } : {}) }
}
