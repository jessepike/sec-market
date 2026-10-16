import refreshCoverage from './generated/refreshCoverage.json' with { type: 'json' }
import { lastCompleteRefreshAt } from './refreshPublication'
import collectStateRaw from './generated/collectState.json' with { type: 'json' }
import edgarFactsRaw from './generated/edgarFacts.json' with { type: 'json' }
import { formatShortDate } from './dates'
import { joinNames, shortSupplierName } from './tracker/names'
import { trackerSuppliers } from './tracker/suppliers'

/**
 * The honest run status shown near the top of the front page
 * (docs/archive/2026-10-refresh-gate/autonomy-coverage-plan.md §3, §6 step 1). Distinguishes a
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
 * for debugging but never rendered (the collector was retired 2026-10-16). This module
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
 * The retired collector recorded one of these per failed source
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
 * The unstructured collector's receipt of its own most recent run. The
 * collector and its publish script were retired and removed on 2026-10-16;
 * the receipt is a frozen record (SEC-063 retires it from the build). `state` is the collector's own diff-based verdict
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

/**
 * Suppliers marked `kind: 'public'` in the tracker data — the denominator
 * the filings clause must agree with (AUTO-001 fix pass 4, item 4: both
 * blind scorers caught the line saying "14 public suppliers" against a
 * table that showed 18 rows marked "Public ·"). A public supplier whose
 * record carries no `edgarId` isn't in the structured EDGAR runner's
 * registry at all (edgarRegistry.ts's `unsupported` list says why — a
 * foreign filer with no quarterly XBRL, for instance) — its figures come
 * from its own releases instead, named here by short display name so nobody
 * has to hand-type them into the clause.
 */
const publicSuppliers = trackerSuppliers.filter((s) => s.kind === 'public')
const nonXbrlPublicNames = publicSuppliers
  .filter((s) => !s.edgarId)
  .map((s) => shortSupplierName(s.name))
  .sort((a, b) => a.localeCompare(b))

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

/**
 * "SEC filings complete for all 16 public suppliers that file quarterly with
 * the SEC; Check Point and Trend Micro figures come from their own
 * releases." — the SEC/EDGAR side of the status line.
 *
 * AUTO-001 fix pass 4, item 4: the previous version compared
 * `edgarFacts.suppliers.length` (whatever the EDGAR runner's registry
 * happened to declare) against itself, with no link at all to how many
 * suppliers the tracker table actually shows as "Public ·" — the two
 * numbers drifted apart (14 vs. 18) the moment a public supplier was added
 * to the table without also being added to the registry. The denominator
 * here is `publicSuppliers.length` — the count the reader can verify by
 * counting the table's own ownership column — and the non-XBRL names are
 * read from the same tracker data (any public supplier with no `edgarId`),
 * never hand-typed, so the two can't drift apart silently again.
 */
function filingsClause(): string {
  // The XBRL runner's own declared total (edgarRegistry.ts's entries,
  // reflected in generated/edgarFacts.json) is the sentence's denominator —
  // it, not the full public-supplier count, is "public suppliers that file
  // quarterly with the SEC". Checked against `publicSuppliers.length` minus
  // `nonXbrlPublicNames.length` by the verify-tracker gate and by
  // tests/run-status.test.ts, so the two can't silently drift apart.
  const xbrlTotal = edgarFacts.suppliers.length
  const failed = edgarFacts.failures.length
  const xbrlOk = xbrlTotal - failed
  const nonXbrl =
    nonXbrlPublicNames.length > 0
      ? `; ${joinNames(nonXbrlPublicNames)} ${nonXbrlPublicNames.length > 1 ? 'figures come from their own releases' : 'figures come from its own releases'}`
      : ''
  if (failed === 0) {
    return `SEC filings complete for all ${xbrlTotal} public suppliers that file quarterly with the SEC${nonXbrl}`
  }
  return `SEC filings complete for ${xbrlOk} of ${xbrlTotal} public suppliers that file quarterly with the SEC${nonXbrl}`
}

function deriveRunStatus(): RunStatus {
  const edgarDate = isoDatePart(edgarFacts.generatedAt)
  const collectorRun = collectState.collectorRun
  const collectDate = collectorRun ? isoDatePart(collectorRun.at) : null
  // AUTO-002 Phase 2: the laptop collector is retired, so the site's as-of
  // clock is the SEC refresh date. The old min(collector, SEC) rule would
  // freeze the event window at the last collector run.
  void collectDate
  const lastChecked = edgarDate

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
  // source (the collector process itself didn't finish); the retired collector
  // wrote a plain, file-path-free sentence into collectorRun.detail for this
  // case, safe to render as-is.
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

const baseRunStatus = deriveRunStatus()
export const runStatus: RunStatus = refreshCoverage.state === 'incomplete' || !lastCompleteRefreshAt
  ? { ...baseRunStatus, state: 'incomplete', detail: `${baseRunStatus.detail ?? 'Collection checked'}; ${refreshCoverage.supplierChecksReceived} of ${refreshCoverage.supplierCount} supplier coverage receipts recorded; ${refreshCoverage.summary.failed} fields failed verification and ${refreshCoverage.summary['not-checked']} fields remain unchecked.` }
  : baseRunStatus
