/**
 * Tracked events — step 5 of the autonomy plan
 * (docs/archive/2026-10-refresh-gate/autonomy-coverage-plan.md §4–5, D-76/D-77). Append-only,
 * trailing-12-month record of dated facts per supplier, each citing evidence
 * in evidence.ts with a real source URL. Only rungs 1–4 of the sourcing
 * ladder (docs/archive/2026-09-weekly-issue/fable-run/research/11-distress-signal-sources.md §5)
 * publish here — a fact resting only on a single trade-press report (rung
 * 5) is excluded, per web/scripts/verify-tracker.ts.
 */

import { effectiveHandCollectedEvents, originalHandCollectedEvents } from './correctionData'
import generatedFilingEvents from '../generated/filingEvents.json' with { type: 'json' }
import { runStatus } from '../runStatus'
import { dailyEvents } from './daily'

export type TrackerEventType =
  | 'funding'
  | 'acquisition'
  | 'layoff'
  | 'restructuring'
  | 'debt'
  | 'rating'
  | 'going-concern'
  | 'exec-change'
  | 'divestiture'
  | 'shutdown'
  | 'results'
  | 'late-filing'

export interface TrackerEvent {
  id: string
  supplierId: string
  date: string
  type: TrackerEventType
  text: string
  evidenceIds: string[]
  rung: 1 | 2 | 3 | 4 | 5
}

/**
 * Hand-collected events only. AUTO-001 fix pass 4, item 5 adds a second,
 * generated source — `generated/filingEvents.json`, built by
 * `scripts/filing-events.ts` straight from each SEC filer's own 8-K item
 * codes with no model in the loop — merged in below as `trackerEvents`, the
 * name every consumer in this codebase already imports. The generator
 * de-duplicates against this hand-collected array by supplier + date at
 * build time, so the merge below never needs to de-duplicate again.
 */
export { originalHandCollectedEvents as handCollectedEvents, effectiveHandCollectedEvents } from './correctionData'


export const retainedTrackerEvents: TrackerEvent[] = [
  ...effectiveHandCollectedEvents,
  ...(generatedFilingEvents as TrackerEvent[]),
  ...dailyEvents,
]

// Immutable source history remains available alongside the corrected current view.
export const originalRetainedTrackerEvents: TrackerEvent[] = [
  ...originalHandCollectedEvents,
  ...(generatedFilingEvents as TrackerEvent[]),
  ...dailyEvents,
]

const eventWindowEnd = Date.parse(runStatus.lastChecked + 'T00:00:00Z')
// The retained source history is append-only; the live view rolls with the actual check date.
export const trackerEvents = retainedTrackerEvents.filter(event => {
  const date = Date.parse(event.date + 'T00:00:00Z')
  return date >= eventWindowEnd - 365 * 86400000 && date <= eventWindowEnd
})
