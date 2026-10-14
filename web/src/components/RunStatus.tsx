import { runStatus } from '../data/runStatus'
import { completeRefreshDisplay, lastAttemptAt, lastCompleteRefreshAt } from '../data/refreshPublication'

/**
 * Near-top-of-page run status (autonomy-coverage-plan.md §3, §6 step 1):
 * a plain statement of whether collection ran, and whether it was complete.
 * Replaces the weekly issue strip that used to sit here — this keeps the
 * section id `overview` so the header's nav link and the prerender's
 * front-page must-see gate keep resolving to this spot.
 *
 * Third fix pass (2026-09-26), items 1–2: the first line reads like a
 * status line for a security leader — "Figures checked <date>." plus one
 * plain clause for the state — and never a raw failure count with no
 * context. When company-news sources could not be read, the affected
 * suppliers move into a closed, opt-in disclosure (`<details>`, native and
 * keyboard-operable) named by short display name with one plain reason
 * each — no URLs, HTTP status codes, or file paths anywhere in the visible
 * text.
 */
function statusLine(): string {
  if (!lastCompleteRefreshAt || runStatus.state === 'incomplete') return `Last complete data refresh: ${completeRefreshDisplay}. Latest attempt ${lastAttemptAt}: held. Published data and its complete-refresh date are retained. ${runStatus.detail ?? ''}`
  if (runStatus.state === 'updated') {
    return `Last complete data refresh: ${completeRefreshDisplay}. Every required check passed.`
  }
  if (runStatus.state === 'no-change') {
    return `Last complete data refresh: ${completeRefreshDisplay}. Every required check passed with no material change within our coverage.`
  }
  // 'incomplete': runStatus.ts always sets a plain-language detail for this
  // state (see filingsClause()/deriveRunStatus() there) — there is no
  // generic fallback line here, so the wording is never a bare number with
  // no context.
  return `Last complete data refresh: ${completeRefreshDisplay}. ${runStatus.detail}`
}

export function RunStatus() {
  return (
    <section id="overview" className="run-status" aria-labelledby="run-status-heading">
      <h2 id="run-status-heading" className="visually-hidden">
        Run status
      </h2>
      <p className={`run-status__line run-status__line--${lastCompleteRefreshAt ? runStatus.state : 'incomplete'}`}>{statusLine()}</p>
      {runStatus.state === 'incomplete' && runStatus.failedNewsSuppliers.length > 0 ? (
        <details className="run-status__failed">
          <summary>Which sources failed</summary>
          <ul>
            {runStatus.failedNewsSuppliers.map((supplier) => (
              <li key={supplier.supplierId}>
                {supplier.displayName} — {supplier.reason}
              </li>
            ))}
          </ul>
        </details>
      ) : null}
    </section>
  )
}
