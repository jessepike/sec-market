import { certifiedClaimCount, certifiedCount, certifiedDateDisplay, checkInterval, receiptComplete } from '../data/tracker/certification'
import { useEffect, useState } from 'react'
import { dailyCoverage, dailyOverdue } from '../data/tracker/daily'

/**
 * AUTO-002 Phase 2: the `#overview` slot states what is certified and when,
 * in one paragraph. It replaces the collector run-status line and its list of
 * failed newsroom sources (the laptop collector is retired). The prerender
 * must-see gate and the header brand link still resolve to `#overview`.
 *
 * The date is the certification run that produced the committed data. The
 * scheduled check follows the active collection cadence and publishes a new
 * value only when that value changes, so this is the date of the last certified change; a missed
 * check is reported to the owner by the freshness probe, not shown here.
 */
export function DailyCollectionStatus({ className = 'run-status__line' }: { className?: string }) {
  const [overdue, setOverdue] = useState(false)
  useEffect(() => {
    const coverage = dailyCoverage
    if (!coverage) return
    const update = () => setOverdue(dailyOverdue(coverage, Date.now()))
    update()
    const timer = setInterval(update, 60000)
    return () => clearInterval(timer)
  }, [])
  if (!dailyCoverage) return null
  return <p className={`${className} run-status__line--${dailyCoverage.complete && !overdue ? 'updated' : 'incomplete'}`} aria-live="polite">
    Latest recorded collection: {dailyCoverage.lastCollectionAt.slice(0, 16).replace('T', ' ')} UTC.{' '}
    {dailyCoverage.successfulTasks} of {dailyCoverage.requiredTasks} required source checks completed.
    {!dailyCoverage.complete && ' Coverage is incomplete.'}{overdue && ' The next check is overdue.'}{' '}
    <a href="/daily-coverage.json">Sources, frequency and check receipts</a>
  </p>
}

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
        Other figures keep their own source and date{dailyCoverage ? '. Source checks do not certify every historical claim.' : ' and are not re-checked automatically.'}{' '}
        <a href="#method">How this works</a> · <a href="/certified-coverage.json">Certification receipt</a>
      </p>
    </section>
  )
}
