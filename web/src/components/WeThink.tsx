import { formatShortDate } from '../data/dates'
import { securityDomains } from '../data/domains'
import type { Issue } from '../data/types'
import { EvidenceLink } from './EvidenceLink'

function domainName(domainId: string): string {
  return securityDomains.find((domain) => domain.id === domainId)?.name ?? domainId
}

export function WeThink({ issue }: { issue: Issue }) {
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
            <div className="we-think__thesis">
              <p>
                Thesis &mdash; {issue.weThink.thesis.verdict}: {issue.weThink.thesis.basis}
              </p>
              <p className="stamp-label">
                CONFIDENCE &middot; {issue.weThink.thesis.confidence.toUpperCase()}
              </p>
              <EvidenceLink ids={issue.weThink.thesis.evidenceIds} />
            </div>
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

          <div className="we-think__thesis">
            <p>
              Thesis &mdash; {issue.proposed.thesis.verdict}: {issue.proposed.thesis.basis}
            </p>
            <p className="stamp-label">
              CONFIDENCE &middot; {issue.proposed.thesis.confidence.toUpperCase()}
            </p>
            <EvidenceLink ids={issue.proposed.thesis.evidenceIds} />
          </div>

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
