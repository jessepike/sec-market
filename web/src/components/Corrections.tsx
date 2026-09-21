import { formatShortDate } from '../data/dates'
import { correctionsNewestFirst } from '../data/correctionHelpers'
import { corrections } from '../data/corrections'
import { issueById } from '../data/issues/index'
import { CONTACT_EMAIL } from '../data/meta'

function mailto(subject: string): string {
  return `mailto:${CONTACT_EMAIL}?subject=${encodeURIComponent(subject)}`
}

/** `/corrections/`: every published correction, newest first (SEC-MARKET-FABLE-001 T6-13). */
export function Corrections() {
  const ordered = correctionsNewestFirst(corrections)

  return (
    <section id="corrections" className="corrections-page" aria-labelledby="corrections-heading">
      <h1 id="corrections-heading">Corrections</h1>
      <p className="corrections-page__lede">
        A published issue is never edited after the fact. When something in one is wrong, the fix is
        a dated note placed beside the item on the page, and the correction is listed here too, with
        the original left in the record exactly as it was published. To report an error, write to{' '}
        <a href={mailto('Security Market Pulse — correction or question')}>{CONTACT_EMAIL}</a>.
      </p>
      {ordered.length === 0 ? (
        <p className="corrections-page__empty">No corrections have been published.</p>
      ) : (
        <ul className="corrections-page__list">
          {ordered.map((correction) => {
            const issue = issueById[correction.issueId]
            return (
              <li key={correction.id} id={correction.id} className="corrections-page__item">
                <p className="corrections-page__meta">
                  <time dateTime={correction.date}>{formatShortDate(correction.date)}</time>
                  {' · '}
                  {issue ? (
                    <a href={`/issues/${issue.id}/`}>Issue {issue.id}</a>
                  ) : (
                    <span>Issue {correction.issueId}</span>
                  )}
                </p>
                <p className="corrections-page__text">{correction.text}</p>
                <p className="corrections-page__approved">Approved by {correction.approvedBy}</p>
              </li>
            )
          })}
        </ul>
      )}
      <p className="corrections-page__back">
        <a href="/">Back to the standing reference</a>
      </p>
    </section>
  )
}
