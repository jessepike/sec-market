import { securityDomains } from '../data/domains'
import { EvidenceLink } from './EvidenceLink'
import { StatusBadge } from './StatusBadge'

function coverageBadge(coverage: string) {
  if (coverage === 'INSUFFICIENT_COVERAGE') return <StatusBadge kind="insufficient" />
  if (coverage === 'NO-CALL') return <StatusBadge kind="no-call" />
  return <StatusBadge kind={coverage} />
}

export function DomainBoard() {
  return (
    <section id="domains" className="domain-board" aria-labelledby="domains-heading">
      <div className="section-heading">
        <h2 id="domains-heading">Security domains</h2>
        <p>Momentum, coverage, posture, and what to watch — by domain.</p>
      </div>
      <div className="domain-board__grid">
        {securityDomains.map((domain) => (
          <article key={domain.id} className="domain-card">
            <header className="domain-card__header">
              <h3>{domain.name}</h3>
              <div className="domain-card__badges">
                {coverageBadge(domain.coverage)}
                <StatusBadge kind={domain.posture} />
              </div>
            </header>
            <dl className="domain-card__meta">
              <div>
                <dt>Momentum</dt>
                <dd>{domain.momentum.replace(/-/g, ' ')}</dd>
              </div>
              <div>
                <dt>Evidence strength</dt>
                <dd>{domain.evidenceStrength}</dd>
              </div>
            </dl>
            <p className="domain-card__summary">{domain.summary}</p>
            <div className="domain-card__watch">
              <h4>What to watch</h4>
              <ul>
                {domain.watchItems.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>
            <div className="domain-card__evidence">
              <EvidenceLink ids={domain.supportingEvidenceIds} label="Supporting evidence" />
              {domain.counterEvidenceIds.length > 0 && (
                <EvidenceLink
                  ids={domain.counterEvidenceIds}
                  label="Counter-evidence"
                  className="evidence-link--counter"
                />
              )}
            </div>
          </article>
        ))}
      </div>
    </section>
  )
}
