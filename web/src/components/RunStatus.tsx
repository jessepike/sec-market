import { formatShortDate } from '../data/dates'
import { runStatus } from '../data/runStatus'

/**
 * Near-top-of-page run status (autonomy-coverage-plan.md §3, §6 step 1):
 * a plain statement of whether collection ran, and whether it was complete.
 * Replaces the weekly issue strip that used to sit here — this keeps the
 * section id `overview` so the header's nav link and the prerender's
 * front-page must-see gate keep resolving to this spot.
 */
function statusLine(): string {
  const checked = formatShortDate(runStatus.lastChecked)
  if (runStatus.state === 'updated') {
    return `Figures checked ${checked} · every source collected.`
  }
  if (runStatus.state === 'no-change') {
    return `Figures checked ${checked} · no material change within our coverage.`
  }
  const n = runStatus.failedSources.length
  const noun = n === 1 ? 'source' : 'sources'
  return `Figures checked ${checked} · collection incomplete: ${n} ${noun} failed.`
}

export function RunStatus() {
  return (
    <section id="overview" className="run-status" aria-labelledby="run-status-heading">
      <h2 id="run-status-heading" className="visually-hidden">
        Run status
      </h2>
      <p className={`run-status__line run-status__line--${runStatus.state}`}>{statusLine()}</p>
      {runStatus.state === 'incomplete' && runStatus.failedSources.length > 0 ? (
        <p className="run-status__failed">Failed: {runStatus.failedSources.join(', ')}</p>
      ) : null}
    </section>
  )
}
