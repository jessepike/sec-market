import { certifiedClaimCount, certifiedCount, certifiedDateDisplay, checkInterval, receiptComplete } from '../data/tracker/certification'

/**
 * AUTO-002 Phase 2: the `#overview` slot states what is certified and when,
 * in one paragraph. It replaces the collector run-status line and its list of
 * failed newsroom sources (the laptop collector is retired). The prerender
 * must-see gate and the header brand link still resolve to `#overview`.
 *
 * The date is the certification run that produced the committed data. The
 * scheduled check runs every 4 hours and commits only when a certified value
 * changes (D-96), so this is the date of the last certified change; a missed
 * check is reported to the owner by the freshness probe, not shown here.
 */
export function RunStatus() {
  return (
    <section id="overview" className="run-status" aria-labelledby="run-status-heading">
      <h2 id="run-status-heading" className="visually-hidden">
        What is certified
      </h2>
      <p className={`run-status__line run-status__line--${receiptComplete ? 'updated' : 'incomplete'}`}>
        SEC figures for {certifiedCount} public companies are re-derived from their own SEC filings and must
        pass all {certifiedClaimCount} checks before they publish. Last certified change: {certifiedDateDisplay}.
        A check is scheduled {checkInterval}.
      </p>
      <p className="run-status__note">
        Other figures keep their own source and date and are not re-checked automatically.{' '}
        <a href="#method">How this works</a> · <a href="/certified-coverage.json">Certification receipt</a>
      </p>
    </section>
  )
}
