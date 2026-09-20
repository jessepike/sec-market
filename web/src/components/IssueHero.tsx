import { formatShortDate } from '../data/dates'
import { jargonNoteFor } from '../data/jargonNotes'
import { JUDGED_AS_OF_ISO, LAST_UPDATED_DISPLAY, SITE_DESCRIPTION, SITE_DISCLAIMER } from '../data/meta'
import type { Issue } from '../data/types'

export function IssueHero({ issue }: { issue: Issue }) {
  const weekEndingLabel = formatShortDate(issue.weekEnding)
  const eyebrow =
    issue.status === 'published' && issue.published
      ? `Issue ${issue.id} · week ending ${weekEndingLabel} · published ${formatShortDate(issue.published)}`
      : `Issue ${issue.id} · week ending ${weekEndingLabel} · draft, awaiting signature`
  // Read off the newest issue's own headline, never generated from the
  // clock — see data/jargonNotes.ts. Rendered by this component only, so it
  // can never enter issue.read itself, the issue JSON export, or the feed.
  const note = jargonNoteFor(issue.read)

  return (
    <section id="overview" className="issue-hero" aria-labelledby="issue-hero-heading">
      <p className="issue-hero__description">{SITE_DESCRIPTION}</p>
      <p className="issue-hero__disclaimer">{SITE_DISCLAIMER}</p>
      <p className="issue-hero__asof">
        Updated {LAST_UPDATED_DISPLAY}. Domain stances judged {formatShortDate(JUDGED_AS_OF_ISO)}.
      </p>
      <p className="eyebrow">
        {eyebrow} · <a href="/feed.xml">Feed</a>
      </p>
      <h1 id="issue-hero-heading">{issue.read}</h1>
      {note ? (
        <p className="issue-hero__note">
          <span className="issue-hero__note-label">Site note</span> {note}
        </p>
      ) : null}
      {issue.status === 'draft' ? <p className="issue-draft-banner">Draft. Not yet signed.</p> : null}
    </section>
  )
}
