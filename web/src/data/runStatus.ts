/**
 * The honest run status shown near the top of the front page
 * (docs/active/autonomy-coverage-plan.md §3, §6 step 1). Distinguishes a
 * quiet week from a failed run — the two must never look the same.
 *
 * `updated` — every declared source was collected and checked this run.
 * `no-change` — the run completed but nothing in our coverage moved.
 * `incomplete` — one or more declared sources failed; `failedSources` names
 * them. The page must say so rather than silently showing stale figures.
 *
 * This is a static value today, hand-set at each publish. It becomes
 * machine-written once the EDGAR/model runners land (plan steps 2–4).
 */
export type RunState = 'updated' | 'no-change' | 'incomplete'

export interface RunStatus {
  /** ISO date the most recent collection run completed. */
  lastChecked: string
  state: RunState
  /** Source names that failed to collect this run. Empty unless state is 'incomplete'. */
  failedSources: string[]
}

export const runStatus: RunStatus = {
  lastChecked: "2026-09-26",
  state: "updated",
  failedSources: [],
}
