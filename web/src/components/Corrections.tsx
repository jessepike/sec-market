import { formatShortDate } from '../data/dates'
import { correctionsNewestFirst } from '../data/correctionHelpers'
import { corrections } from '../data/corrections'
import { issueById } from '../data/issues/index'
import { CONTACT_EMAIL } from '../data/meta'
import { factualCorrectionHistory } from '../data/factualCorrectionHelpers'
import type { CorrectionHistorySources } from '../data/factualCorrectionHelpers'
import type { FactualCorrectionGroup } from '../data/tracker/factualCorrections'
import { factualCorrectionGroups, factualCorrectionSourceEvidenceIds } from '../data/tracker/correctionData'
import { evidenceById } from '../data/evidence'
import { trackerSuppliers } from '../data/tracker/suppliers'

function mailto(subject: string): string {
  return `mailto:${CONTACT_EMAIL}?subject=${encodeURIComponent(subject)}`
}

/** `/corrections/`: every published correction, newest first (SEC-MARKET-FABLE-001 T6-13). */
export function Corrections({ groups = factualCorrectionGroups, sources = { evidence: evidenceById, suppliers: trackerSuppliers, groupEvidenceIds: factualCorrectionSourceEvidenceIds } }: { groups?: readonly FactualCorrectionGroup[]; sources?: CorrectionHistorySources } = {}) {
  const ordered = correctionsNewestFirst(corrections)
  const factual = factualCorrectionHistory(groups, sources, '')
  const history = [...ordered, ...factual].sort((a, b) => b.date.localeCompare(a.date))

  return (
    <section id="corrections" className="corrections-page" aria-labelledby="corrections-heading">
      <h1 id="corrections-heading">Corrections</h1>
      <p className="corrections-page__lede">
        A published issue is never edited after the fact. When something in one is wrong, the fix is
        a dated note placed beside the item on the page, and the correction is listed here too, with
        the original left in the record exactly as it was published. The standing tables are
        different: a wrong entry there is fixed in place, given the date of the fix, and listed
        here. To report an error, write to{' '}
        <a href={mailto('Security Market Pulse — correction or question')}>{CONTACT_EMAIL}</a>.
      </p>
      {history.length === 0 ? (
        <p className="corrections-page__empty">No corrections have been published.</p>
      ) : (
        <ul className="corrections-page__list">
          {history.map((correction) => {
            if ('kind' in correction) return (
              <li key={correction.id} id={correction.id} className="corrections-page__item">
                <p className="corrections-page__meta">
                  <time dateTime={correction.date}>{formatShortDate(correction.date)}</time>
                  {' · '}{correction.supplierName}{correction.reviewScope === 'publisher_disclosure_only' ? ' · Publisher disclosure correction' : ' · Source-verified factual correction'}
                </p>
                <p className="corrections-page__text">{correction.note}</p>
                {correction.changes.map((change) => (
                  <div key={change.targetId}>
                    <p>{change.label}</p>
                    <p>Before: {change.before}</p>
                    <p>After: {change.after}</p>
                  </div>
                ))}
                <p>Sources: {correction.sources.map((source, index) => (
                  <span key={source.id}>{index > 0 ? '; ' : ''}<a href={source.url}>{source.title}</a></span>
                ))}</p>
                <details>
                  <summary>Review record</summary>
                  <p>Admitted: {correction.admission.admittedAt}</p>
                  {correction.reviewScope === 'publisher_disclosure_only' ? <p>Review scope: publication role only. Financial, funding and operating figures are unchanged and are not verified by this correction.</p> : null}
                  <p>Candidate SHA-256: <code style={{ overflowWrap: 'anywhere' }}>{correction.admission.candidateSha256}</code></p>
                  <p>Evidence set SHA-256: <code style={{ overflowWrap: 'anywhere' }}>{correction.admission.evidenceSetSha256}</code></p>
                  <p>Policy SHA-256: <code style={{ overflowWrap: 'anywhere' }}>{correction.admission.policySha256}</code></p>
                  <p>Review SHA-256: <code style={{ overflowWrap: 'anywhere' }}>{correction.admission.reviewSha256}</code></p>
                </details>
              </li>
            )
            const issue = correction.issueId ? issueById[correction.issueId] : undefined
            return (
              <li key={correction.id} id={correction.id} className="corrections-page__item">
                <p className="corrections-page__meta">
                  <time dateTime={correction.date}>{formatShortDate(correction.date)}</time>
                  {correction.issueId ? (
                    <>
                      {' · '}
                      {issue ? (
                        <a href={`/issues/${issue.id}/`}>Issue {issue.id}</a>
                      ) : (
                        <span>Issue {correction.issueId}</span>
                      )}
                    </>
                  ) : null}
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
