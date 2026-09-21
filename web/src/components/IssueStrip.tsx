import { formatShortDate } from '../data/dates'
import { jargonNoteFor } from '../data/jargonNotes'
import type { Issue } from '../data/types'

/**
 * The weekly issue, compressed to a strip (SEC-MARKET-CORE-001 §5).
 *
 * The read keeps the top of the page and keeps `#overview`, so the header's
 * "Issue" link and the prerender's section list still land on it, but it is
 * no longer the `h1` and no longer three lines of 44px type. That was the
 * whole of the first screen, which belongs to the market picture.
 *
 * The read links to `#we-think`, the judgment on this same page, rather than
 * to the permalink: the issue's own sections are directly below, and sending
 * a reader away from content they can already see is the wrong move. The
 * permalink stays reachable from the eyebrow, where it carries the issue id.
 */
export function IssueStrip({ issue }: { issue: Issue }) {
  const weekEndingLabel = formatShortDate(issue.weekEnding)
  const dateLine =
    issue.status === 'published' && issue.published
      ? `week ending ${weekEndingLabel} · published ${formatShortDate(issue.published)}`
      : `week ending ${weekEndingLabel} · draft, awaiting signature`
  // Read off the issue's own headline, never generated from the clock — see
  // data/jargonNotes.ts. Rendered here only, so it can never enter
  // issue.read itself, the issue JSON export, or the feed.
  const note = jargonNoteFor(issue.read)

  return (
    <section id="overview" className="issue-strip" aria-labelledby="issue-strip-heading">
      <p className="eyebrow issue-strip__eyebrow">
        <span className="issue-strip__label">This week</span> · {dateLine} ·{' '}
        <a href={`/issues/${issue.id}/`}>Issue {issue.id}</a> · <a href="/feed.xml">Feed</a>
      </p>
      <h2 id="issue-strip-heading" className="issue-strip__read">
        <a href="#we-think">{issue.read}</a>
      </h2>
      {note ? (
        <p className="issue-strip__note">
          <span className="issue-hero__note-label">Site note</span> {note}
        </p>
      ) : null}
      {issue.status === 'draft' ? <p className="issue-draft-banner">Draft. Not yet signed.</p> : null}
    </section>
  )
}
