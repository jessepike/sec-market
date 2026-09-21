import { formatShortDate } from '../data/dates'
import { securityDomains } from '../data/domains'
import type { Issue, ThesisScore } from '../data/types'
import { EvidenceLink } from './EvidenceLink'

function domainName(domainId: string): string {
  return securityDomains.find((domain) => domain.id === domainId)?.name ?? domainId
}

/**
 * The thesis verdict, in one of two shapes. Full (the default, and always
 * what the issue permalink shows — the permalink is the record of that
 * period) is the original paragraph, confidence stamp and evidence link.
 * `condense` (front page only, SEC-MARKET-FABLE-001 T6-16) reduces it to one
 * quiet line pointing at `/thesis/`, now the standing home for the thesis
 * and its record — product-core.md §5.
 */
function ThesisLine({ thesis, condense }: { thesis: ThesisScore; condense: boolean }) {
  if (condense) {
    return (
      <p className="we-think__thesis-link">
        Standing analysis: {thesis.verdict}. <a href="/thesis/">See the record.</a>
      </p>
    )
  }
  return (
    <div className="we-think__thesis">
      <p>
        Thesis &mdash; {thesis.verdict}: {thesis.basis}
      </p>
      <p className="stamp-label">CONFIDENCE &middot; {thesis.confidence.toUpperCase()}</p>
      <EvidenceLink ids={thesis.evidenceIds} />
    </div>
  )
}

/**
 * `condenseThesis` defaults to false, today's behaviour, unchanged — the
 * issue permalink page never passes it. The front page passes it as true
 * (see src/App.tsx) so this block's thesis verdict becomes a quiet pointer
 * to `/thesis/` instead of the full paragraph.
 */
export function WeThink({ issue, condenseThesis = false }: { issue: Issue; condenseThesis?: boolean }) {
  const isPublished = issue.status === 'published'

  return (
    <section id="we-think" className="we-think" aria-labelledby="we-think-heading">
      <h2 id="we-think-heading">
        {isPublished ? 'What we now think' : 'Machine proposal, unsigned'}
      </h2>

      {isPublished ? (
        <>
          <p className="we-think__summary">{issue.weThink.summary}</p>

          {issue.weThink.postureDeltas.length > 0 ? (
            <ul className="we-think__deltas">
              {issue.weThink.postureDeltas.map((delta) => (
                <li key={delta.domainId} className="we-think__delta">
                  <p className="we-think__delta-move">
                    <strong>{domainName(delta.domainId)}</strong>: {delta.from} &rarr; {delta.to}
                  </p>
                  <p>{delta.basis}</p>
                  <p className="stamp-label">CONFIDENCE &middot; {delta.confidence.toUpperCase()}</p>
                  <EvidenceLink ids={delta.evidenceIds} />
                </li>
              ))}
            </ul>
          ) : null}

          {issue.weThink.thesis ? (
            <ThesisLine thesis={issue.weThink.thesis} condense={condenseThesis} />
          ) : null}

          {issue.weThink.noCalls.length > 0 ? (
            <ul className="we-think__nocalls">
              {issue.weThink.noCalls.map((call) => (
                <li key={call}>{call}</li>
              ))}
            </ul>
          ) : null}

          <p className="we-think__signature">
            Signed by {issue.weThink.signedBy}
            {issue.weThink.signedOn ? ` · ${formatShortDate(issue.weThink.signedOn)}` : ''}
          </p>
        </>
      ) : issue.proposed ? (
        <>
          <p className="we-think__proposed-read">{issue.proposed.read}</p>
          <p className="we-think__summary">{issue.proposed.summary}</p>

          {issue.proposed.thesis ? (
            <ThesisLine thesis={issue.proposed.thesis} condense={condenseThesis} />
          ) : null}

          {issue.proposed.noCalls.length > 0 ? (
            <ul className="we-think__nocalls">
              {issue.proposed.noCalls.map((call) => (
                <li key={call}>{call}</li>
              ))}
            </ul>
          ) : null}

          <p className="we-think__posture-deltas-prose">{issue.proposed.postureDeltas}</p>

          <p className="issue-draft-banner">
            Unsigned draft. Nothing here is a judgment until a named person signs it.
          </p>
        </>
      ) : (
        <p>No proposal yet.</p>
      )}
    </section>
  )
}
