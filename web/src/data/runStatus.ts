import collectStateRaw from './generated/collectState.json' with { type: 'json' }
import edgarFactsRaw from './generated/edgarFacts.json' with { type: 'json' }
import { formatShortDate } from './dates'
import { shortSupplierName } from './tracker/names'
import { trackerSuppliers } from './tracker/suppliers'

/**
 * The honest run status shown near the top of the front page
 * (docs/active/autonomy-coverage-plan.md §3, §6 step 1). Distinguishes a
 * quiet week from a failed run — the two must never look the same.
 *
 * `updated` — every declared source was collected and checked this run.
 * `no-change` — the run completed but nothing in our coverage moved.
 * `incomplete` — one or more declared sources failed, or the last collect
 * run covered only a subset of suppliers; `detail` and/or
 * `failedNewsSuppliers` say why.
 *
 * AUTO-001 fix pass 2 (2026-09-26), item 4: this used to be a static value,
 * hand-set at each publish. It is computed at import time from the two
 * generated files that actually know what ran: `generated/edgarFacts.json`
 * (the structured EDGAR side — `generatedAt`, `failures`) and
 * `generated/collectState.json` (the unstructured press/funding/distress
 * side — see collect-brief.md §4 for the model-owned
 * `lastSuccessfulCollectDate`/`lastRunAt` fields, and the `collectorRun`
 * block below for the script-owned receipt of the most recent run,
 * restricted or not).
 *
 * Third fix pass (2026-09-26), items 1–3: the first version of this
 * derivation rendered `collectorRun.failedSources` as a flat list of 25 raw
 * collector strings — URLs, HTTP status codes, and a reference to
 * `.collect/failed-sources.json`, a file the site never publishes. A status
 * line built for a reader (the brief's own framing: "read like a status
 * line for a security leader") cannot repeat a collector's internal error
 * log verbatim. `collectState.json`'s `failedSources` is now an array of
 * `{ supplierId, reason, detail }` records — `reason` a small fixed
 * vocabulary (`REASON_TEXT` below), `detail` the full technical string kept
 * for whoever debugs `collect.sh` next but never rendered. This module
 * derives `failedNewsSuppliers`, one deduplicated, plain-language row per
 * distinct supplier, from that list.
 */
export type RunState = 'updated' | 'no-change' | 'incomplete'

export interface FailedSupplier {
  supplierId: string
  /** Short reader-facing name (shortSupplierName), not the full legal name. */
  displayName: string
  /** Plain language only — never a URL, an HTTP status code, or a file path. */
  reason: string
}

export interface RunStatus {
  /** ISO date of the older of the two sources below — the site is only as fresh as its stalest one. */
  lastChecked: string
  state: RunState
  /**
   * The clause(s) appended after "Figures checked <date>." Always plain
   * language: no URLs, HTTP status codes, or references to an unpublished
   * file.
   */
  detail?: string
  /**
   * One row per distinct supplier whose company-news sources could not be
   * read this run — backs the closed "Which sources failed" disclosure.
   * Empty whenever state is not 'incomplete' for this reason.
   */
  failedNewsSuppliers: FailedSupplier[]
}

interface EdgarFailure {
  id: string
  name: string
  reason: string
}

interface EdgarFacts {
  generatedAt: string
  suppliers: unknown[]
  failures: EdgarFailure[]
}

/**
 * The small, fixed vocabulary a collector-run failure is classified into.
 * `collect.sh`/`collect-brief.md` record one of these per failed source
 * (third fix pass, item 1) instead of a free-text sentence, so the display
 * text is centralized here rather than baked into the data.
 */
type CollectFailureReason = 'blocked' | 'not-found' | 'no-readable-releases' | 'no-primary-source'

const REASON_TEXT: Record<CollectFailureReason, string> = {
  blocked: 'newsroom blocked automated reading',
  'not-found': 'page not found',
  'no-readable-releases': 'newsroom listed no readable releases',
  'no-primary-source': 'no primary source found',
}

interface CollectFailure {
  supplierId: string
  reason: CollectFailureReason
  /** Full technical detail (URL, HTTP status) — kept for debugging, never rendered. */
  detail: string
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
  failedSources: CollectFailure[]
}

interface CollectState {
  lastSuccessfulCollectDate: string | null
  lastRunAt: string | null
  collectorRun: CollectorRun | null
}

const edgarFacts = edgarFactsRaw as EdgarFacts
const collectState = collectStateRaw as CollectState

const supplierNameById = new Map(trackerSuppliers.map((s) => [s.id, s.name]))
const TOTAL_SUPPLIERS = trackerSuppliers.length

function isoDatePart(isoDateTime: string): string {
  return isoDateTime.slice(0, 10)
}

/** One deduplicated, plain-language row per distinct supplier in `failedSources` — first occurrence wins, sorted for a stable, scannable read. */
function newsFailureRows(failedSources: CollectFailure[]): FailedSupplier[] {
  const bySupplier = new Map<string, CollectFailure>()
  for (const failure of failedSources) {
    if (!bySupplier.has(failure.supplierId)) bySupplier.set(failure.supplierId, failure)
  }
  const rows = Array.from(bySupplier.entries()).map(([supplierId, failure]) => ({
    supplierId,
    displayName: shortSupplierName(supplierNameById.get(supplierId) ?? supplierId),
    reason: REASON_TEXT[failure.reason],
  }))
  rows.sort((a, b) => a.displayName.localeCompare(b.displayName))
  return rows
}

/** "Filings complete for all 14 public suppliers" / "Filings complete for 12 of 14 public suppliers" — the SEC/EDGAR side of the status line, always in reader terms, never a raw failure count alone. */
function filingsClause(): string {
  const n = edgarFacts.suppliers.length
  const failed = edgarFacts.failures.length
  if (failed === 0) return `Filings complete for all ${n} public suppliers`
  return `Filings complete for ${n - failed} of ${n} public suppliers`
}

function deriveRunStatus(): RunStatus {
  const edgarDate = isoDatePart(edgarFacts.generatedAt)
  const collectorRun = collectState.collectorRun
  const collectDate = collectorRun ? isoDatePart(collectorRun.at) : null
  const lastChecked = collectDate && collectDate < edgarDate ? collectDate : edgarDate

  // No collect run has ever left a receipt in this repo — say so rather
  // than implying a clean run that never happened.
  if (!collectorRun) {
    return {
      lastChecked,
      state: 'incomplete',
      failedNewsSuppliers: [],
      detail: `${filingsClause()}; company news pages have not been checked yet.`,
    }
  }

  const newsFailures = newsFailureRows(collectorRun.failedSources)

  if (edgarFacts.failures.length > 0) {
    return {
      lastChecked,
      state: 'incomplete',
      failedNewsSuppliers: newsFailures,
      detail:
        newsFailures.length > 0
          ? `${filingsClause()}; company news pages could not be read for ${newsFailures.length} of ${TOTAL_SUPPLIERS} suppliers.`
          : `${filingsClause()}.`,
    }
  }

  if (collectorRun.restrictedTo !== null) {
    const n = collectorRun.restrictedTo.length
    return {
      lastChecked,
      state: 'incomplete',
      failedNewsSuppliers: newsFailures,
      detail:
        `${filingsClause()}; press, funding and distress sources last checked for ${n} of ` +
        `${TOTAL_SUPPLIERS} suppliers on ${formatShortDate(collectDate!)} (restricted run: ` +
        `${collectorRun.restrictedTo.join(', ')}).`,
    }
  }

  if (newsFailures.length > 0) {
    return {
      lastChecked,
      state: 'incomplete',
      failedNewsSuppliers: newsFailures,
      detail: `${filingsClause()}; company news pages could not be read for ${newsFailures.length} of ${TOTAL_SUPPLIERS} suppliers.`,
    }
  }

  // A run can be incomplete for a reason that isn't a specific supplier's
  // source (the collector process itself didn't finish) — collect.sh writes
  // a plain, file-path-free sentence into collectorRun.detail for exactly
  // this case (see its own comment), safe to render as-is.
  if (collectorRun.state === 'incomplete') {
    return {
      lastChecked,
      state: 'incomplete',
      failedNewsSuppliers: [],
      detail: `${filingsClause()}; ${collectorRun.detail}.`,
    }
  }

  // Both sides ran clean and covered every declared supplier — trust the
  // collector's own diff-based verdict for 'no-change' vs. 'updated'.
  return {
    lastChecked,
    state: collectorRun.state,
    failedNewsSuppliers: [],
  }
}

export const runStatus: RunStatus = deriveRunStatus()
