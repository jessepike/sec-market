import { certifiedClaimCount, certifiedCount, certifiedDateDisplay, checkInterval, receiptComplete } from '../data/tracker/certification'
import { useEffect, useState } from 'react'
import { dailyCoverage, dailyOverdue, type DailyCoverage } from '../data/tracker/daily'

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
export function DailyCollectionStatus({ className = 'run-status__line', coverage = dailyCoverage }: {
  className?: string; coverage?: DailyCoverage | null
}) {
  const [overdue, setOverdue] = useState(false)
  useEffect(() => {
    if (!coverage) return
    const update = () => setOverdue(dailyOverdue(coverage, Date.now()))
    update()
    const timer = setInterval(update, 60000)
    return () => clearInterval(timer)
  }, [coverage])
  if (!coverage) return null
  if (coverage.schemaVersion === 2) {
    const { intake, processing, historicalReview: history } = coverage
    const complete = intake.complete && processing.complete && history.complete && history.heldDocuments === 0
    return <div className={`${className} run-status__line--${complete && !overdue ? 'updated' : 'incomplete'}`} aria-live="polite">
      {intake.evaluated && overdue && 'The next source check is overdue. '}
      {intake.evaluated ? <>Daily source intake: {intake.successfulTasks} of {intake.requiredTasks} checked; {intake.complete ? 'complete' : 'incomplete'}.</> : <>Daily source intake: not yet collected ({intake.successfulTasks} of {intake.requiredTasks}).</>}<br />
      {processing.evaluated === false ? <>Document processing: not evaluated; pending, held and unknown-date counts unmeasured.</> : <>
      Document processing ({processing.complete ? 'complete' : 'incomplete'}): {processing.inventoryDocuments === 0 ? 'no documents observed' : <>{processing.reviewedDocuments} of {processing.inventoryDocuments} reviewed</>};{' '}
      {processing.pendingDocuments} pending, {processing.heldDocuments} held,{' '}
      {processing.changedDocuments} changed, {processing.unknownDateDocuments} dates unknown.</>}<br />
      {history.evaluated === false ? <>Historical review: not evaluated; pending and held counts unmeasured.</> : <>
      Historical review ({history.complete ? 'complete' : 'incomplete'}): {history.inventoryDocuments === 0 ? 'no documents observed' : <>{history.reviewedDocuments} of {history.inventoryDocuments} reviewed</>};{' '}
      {history.pendingDocuments} pending, {history.heldDocuments} held.</>}{' '}
      <details>
        <summary>Dates, review limits and source receipts</summary>
        {intake.evaluated ? 'Latest recorded source intake: ' : 'Source intake has not yet been collected under this policy. Earlier recorded collection: '}
        {coverage.lastCollectionAt.slice(0, 16).replace('T', ' ')} UTC.{' '}
        Source intake does not mean every current event or historical claim has been reviewed. Earlier evidence keeps its original source and review dates.{' '}
        Index date hints guide collection; they do not verify article publication or event dates.{' '}
        Processing counts refer to inventoried documents; historical review counts refer to retained documents. Held documents have been reviewed but remain unresolved. Changed and unknown-date counts are separate classifications, not additional reviewed documents.{' '}
        <a href="/daily-coverage.json">Sources, frequency and check receipts</a>
      </details>
    </div>
  }
  return <p className={`${className} run-status__line--${coverage.complete && !overdue ? 'updated' : 'incomplete'}`} aria-live="polite">
    Latest recorded collection: {coverage.lastCollectionAt.slice(0, 16).replace('T', ' ')} UTC.{' '}
    {coverage.successfulTasks} of {coverage.requiredTasks} required source checks completed.
    {!coverage.complete && ' Coverage is incomplete.'}{overdue && ' The next check is overdue.'}{' '}
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
