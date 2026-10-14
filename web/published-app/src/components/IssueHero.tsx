import { formatShortDate } from '../data/dates'
import { securityDomains } from '../data/domains'
import { jargonNoteFor } from '../data/jargonNotes'
import { AUTHOR_NAME, LAST_UPDATED_DISPLAY, SITE_DESCRIPTION, SITE_DISCLAIMER } from '../data/meta'
import type { Issue } from '../data/types'

// Fix pass T6-7 item 4: the front page's as-of line previously read
// JUDGED_AS_OF_ISO (17 Aug 2026), but that constant's own doc comment in
// meta.ts says it covers the tracked hypotheses and platform-pressure
// reads, not domain stances — a wrong constant, not a deliberately
// computed "latest across domains/platforms/hypotheses" figure. The domain
// cards in MarketPicture all carry asOf: '2026-08-16'. Sourcing the date
// straight from securityDomains, the same data the cards themselves read,
// makes this line agree with the cards by construction instead of by
// coincidence, and never reads the clock.
const domainsJudgedIso = securityDomains.reduce(
  (latest, domain) => (domain.asOf > latest ? domain.asOf : latest),
  securityDomains[0].asOf,
)

export function IssueHero({ issue, showAsOf = false }: { issue: Issue; showAsOf?: boolean }) {
  const weekEndingLabel = formatShortDate(issue.weekEnding)
  // T6-12 pass 2: split off the id-bearing lead-in so the front page (where
  // showAsOf is true — see the comment below) can swap it for a plain-word
  // link, while the permalink and the render check below keep seeing the
  // exact same "Issue <id> · ..." text as before.
  const eyebrowRest =
    issue.status === 'published' && issue.published
      ? `week ending ${weekEndingLabel} · published ${formatShortDate(issue.published)}`
      : `week ending ${weekEndingLabel} · draft, awaiting signature`
  // Read off the newest issue's own headline, never generated from the
  // clock — see data/jargonNotes.ts. Rendered by this component only, so it
  // can never enter issue.read itself, the issue JSON export, or the feed.
  const note = jargonNoteFor(issue.read)

  return (
    <section id="overview" className="issue-hero" aria-labelledby="issue-hero-heading">
      <p className="issue-hero__description">{SITE_DESCRIPTION}</p>
      <p className="issue-hero__disclaimer">{SITE_DISCLAIMER}</p>
      {/* Fix pass T6-7 item 4: front page only. The issue permalink shows no
          domains, so a line naming domain stances has nothing to point at
          there — IssuePage doesn't pass showAsOf, so it defaults to false. */}
      {showAsOf ? (
        <p className="issue-hero__asof">
          Legacy snapshot date {LAST_UPDATED_DISPLAY}. Domain stances judged {formatShortDate(domainsJudgedIso)} by{' '}
          {AUTHOR_NAME}.
        </p>
      ) : null}
      <p className="eyebrow">
        {/* T6-12 pass 2: "2026-w36" is an internal id a new reader can't
            decode. showAsOf is true only on the front page (see above), so
            only there the lead-in becomes a plain-word link to this issue's
            own permalink, where the id is still shown in full. */}
        {showAsOf ? (
          <a href={`/issues/${issue.id}/`}>Weekly issue</a>
        ) : (
          `Issue ${issue.id}`
        )}{' '}
        · {eyebrowRest} · <a href="/feed.xml">Feed</a>
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
