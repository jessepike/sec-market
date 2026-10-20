import raw from '../generated/dailyMarket.json' with { type: 'json' }
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
export const dailyEvidence: EvidenceRecord[] = dailySnapshot.enabled ? dailySnapshot.evidence : []
export const dailyEvents: TrackerEvent[] = dailySnapshot.enabled ? dailySnapshot.events : []

export interface DailyCoverage {
  checkedAt: string
  complete: boolean
  successfulTasks: number
  requiredTasks: number
  overdueHours: number
  automationEnabled: boolean
  lastCollectionAt: string
  validUntil: string | null
}
export const dailyCoverage = dailySnapshot.enabled ? dailySnapshot.coverage as unknown as DailyCoverage : null

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
