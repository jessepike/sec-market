import { formatShortDate } from '../data/dates'
import type { Issue } from '../data/types'

export function IssueHero({ issue }: { issue: Issue }) {
  const weekEndingLabel = formatShortDate(issue.weekEnding)
  const eyebrow =
    issue.status === 'published' && issue.published
      ? `Issue ${issue.id} · week ending ${weekEndingLabel} · published ${formatShortDate(issue.published)}`
      : `Issue ${issue.id} · week ending ${weekEndingLabel} · draft, awaiting signature`

  return (
    <section id="overview" className="issue-hero" aria-labelledby="issue-hero-heading">
      <p className="eyebrow">{eyebrow}</p>
      <h1 id="issue-hero-heading">{issue.read}</h1>
      {issue.status === 'draft' ? <p className="issue-draft-banner">Draft. Not yet signed.</p> : null}
    </section>
  )
}
