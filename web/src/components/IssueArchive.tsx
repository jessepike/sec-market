import { formatShortDate } from '../data/dates'
import { issues } from '../data/issues/index'

export function IssueArchive() {
  const newestFirst = [...issues].reverse()

  return (
    <section id="issues" className="issue-archive" aria-labelledby="issue-archive-heading">
      <h1 id="issue-archive-heading">Issues</h1>
      <p className="archive-notice">
        Signed weekly issues were discontinued on 25 September 2026. This page is kept unchanged as
        a dated record.
      </p>
      <ul className="issue-archive__list">
        {newestFirst.map((issue) => (
          <li key={issue.id} className="issue-archive__row">
            <span className="issue-archive__id mono">{issue.id}</span>
            <span className="issue-archive__week">
              week ending {formatShortDate(issue.weekEnding)}
            </span>
            <span className="issue-archive__read">{issue.read}</span>
            <span className="issue-archive__status">
              {issue.status === 'published'
                ? `Signed by ${issue.weThink.signedBy}${
                    issue.weThink.signedOn ? ` · ${formatShortDate(issue.weThink.signedOn)}` : ''
                  }`
                : 'Draft'}
            </span>
            <a href={`/issues/${issue.id}/`}>Open issue {issue.id}</a>
          </li>
        ))}
      </ul>
      <p className="issue-archive__back">
        <a href="/">Back to the standing reference</a>
      </p>
    </section>
  )
}
