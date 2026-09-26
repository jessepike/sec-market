import collectStateRaw from './generated/collectState.json' with { type: 'json' }
import edgarFactsRaw from './generated/edgarFacts.json' with { type: 'json' }
import { formatShortDate } from './dates'
import { trackerSuppliers } from './tracker/suppliers'

/**
 * The honest run status shown near the top of the front page
 * (docs/active/autonomy-coverage-plan.md §3, §6 step 1). Distinguishes a
 * quiet week from a failed run — the two must never look the same.
 *
 * `updated` — every declared source was collected and checked this run.
 * `no-change` — the run completed but nothing in our coverage moved.
 * `incomplete` — one or more declared sources failed, or the last collect
 * run covered only a subset of suppliers; `failedSources` and/or `detail`
 * say why.
 *
 * AUTO-001 fix pass 2 (2026-09-26), item 4: this used to be a static value,
 * hand-set at each publish — the exact "misstated run-status" failure mode
 * both blind rescores caught (the page claimed "every source collected"
 * with no collection workflow behind that claim). It is now computed at
 * import time from the two generated files that actually know what ran:
 * `generated/edgarFacts.json` (the structured EDGAR side — `generatedAt`,
 * `failures`) and `generated/collectState.json` (the unstructured
 * press/funding/distress side — see collect-brief.md §4 for the
 * model-owned `lastSuccessfulCollectDate`/`lastRunAt` fields, and the
 * `collectorRun` block below for the script-owned receipt of the most
 * recent run, restricted or not). Nobody hand-edits this file's `runStatus`
 * value again; `scripts/collect.sh` and `scripts/auto-publish.sh` write
 * `collectState.json`'s `collectorRun` block instead (see each script's own
 * comments), and this module derives the rest.
 */
export type RunState = 'updated' | 'no-change' | 'incomplete'

export interface RunStatus {
  /** ISO date of the older of the two sources below — the site is only as fresh as its stalest one. */
  lastChecked: string
  state: RunState
  /** Source names that failed to collect this run. May be empty even when state is 'incomplete' — see `detail`. */
  failedSources: string[]
  /**
   * A plain-language reason for an 'incomplete' state when `failedSources`
   * alone would not say why — chiefly a scope-restricted collect run,
   * where nothing failed but not everything was checked either.
   */
  detail?: string
}

interface EdgarFailure {
  id: string
  name: string
  reason: string
}

interface EdgarFacts {
  generatedAt: string
  failures: EdgarFailure[]
}

/**
 * The unstructured collector's receipt of its own most recent run,
 * written by `scripts/collect.sh` step 6 (or, for a gate-failure/held
 * publish, by `scripts/auto-publish.sh`'s `push_incomplete_status`) —
 * never hand-edited. `state` is the collector's own diff-based verdict
 * ('no-change'/'updated' only meaningful when `restrictedTo` is null and
 * `failedSources` is empty — an unrestricted, clean run). `restrictedTo`
 * is the supplier-id list the run was limited to, or null for a run that
 * covered every declared supplier.
 */
interface CollectorRun {
  at: string
  state: RunState
  detail: string
  restrictedTo: string[] | null
  failedSources: string[]
}

interface CollectState {
  lastSuccessfulCollectDate: string | null
  lastRunAt: string | null
  collectorRun: CollectorRun | null
}

const edgarFacts = edgarFactsRaw as EdgarFacts
const collectState = collectStateRaw as CollectState

function isoDatePart(isoDateTime: string): string {
  return isoDateTime.slice(0, 10)
}

function deriveRunStatus(): RunStatus {
  const edgarDate = isoDatePart(edgarFacts.generatedAt)
  const collectorRun = collectState.collectorRun
  const collectDate = collectorRun ? isoDatePart(collectorRun.at) : null
  const lastChecked = collectDate && collectDate < edgarDate ? collectDate : edgarDate
  const edgarFailureNames = edgarFacts.failures.map((f) => f.name)

  // No collect run has ever left a receipt in this repo — say so rather
  // than implying a clean run that never happened.
  if (!collectorRun) {
    return {
      lastChecked,
      state: 'incomplete',
      failedSources: edgarFailureNames,
      detail: 'No unstructured-collector run has completed yet; only the EDGAR structured-data side has run.',
    }
  }

  if (edgarFailureNames.length > 0) {
    return {
      lastChecked,
      state: 'incomplete',
      failedSources: [...edgarFailureNames, ...collectorRun.failedSources],
      detail: `EDGAR structured-data collection failed for ${edgarFailureNames.length} supplier(s).`,
    }
  }

  if (collectorRun.restrictedTo !== null) {
    const total = trackerSuppliers.length
    const n = collectorRun.restrictedTo.length
    return {
      lastChecked,
      state: 'incomplete',
      failedSources: collectorRun.failedSources,
      detail:
        `Press, funding and distress sources last checked for ${n} of ${total} suppliers on ` +
        `${formatShortDate(collectDate!)} (restricted run: ${collectorRun.restrictedTo.join(', ')}).`,
    }
  }

  if (collectorRun.failedSources.length > 0) {
    return {
      lastChecked,
      state: 'incomplete',
      failedSources: collectorRun.failedSources,
      detail: collectorRun.detail,
    }
  }

  // Both sides ran clean and covered every declared supplier — trust the
  // collector's own diff-based verdict for 'no-change' vs. 'updated'.
  return {
    lastChecked,
    state: collectorRun.state === 'incomplete' ? 'updated' : collectorRun.state,
    failedSources: [],
  }
}

export const runStatus: RunStatus = deriveRunStatus()
