import { securityDomains } from '../data/domains'
import { EvidenceLink } from './EvidenceLink'
import { StatusBadge } from './StatusBadge'

function coverageNote(coverage: string): string | null {
  if (coverage === 'PASS_WITH_LIMITATION') return 'Evidence with comparability limits'
  return null
}

export function DomainBoard() {
  return (
    <section id="domains" className="domain-board" aria-labelledby="domains-heading">
      <div className="section-heading">
        <h2 id="domains-heading">Security domains</h2>
        <p>Current momentum, recommended posture, and what to watch.</p>
      </div>
      <div className="domain-board__grid">
        {securityDomains.map((domain) => {
          const note = coverageNote(domain.coverage)
          return (
            <article key={domain.id} className="domain-card">
              <header className="domain-card__header">
                <h3>{domain.name}</h3>
                <div className="domain-card__badges">
                  {domain.coverage === 'INSUFFICIENT_COVERAGE' && (
                    <StatusBadge kind="insufficient" />
                  )}
                  <StatusBadge kind={domain.posture} />
                </div>
              </header>
              {note && <p className="domain-card__note">{note}</p>}
              <dl className="domain-card__meta">
                <div>
                  <dt>Momentum</dt>
                  <dd>{domain.momentum.replace(/-/g, ' ')}</dd>
                </div>
                <div>
                  <dt>Signal strength</dt>
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
                <EvidenceLink ids={domain.supportingEvidenceIds} label="Supporting sources" />
                {domain.counterEvidenceIds.length > 0 && (
                  <EvidenceLink
                    ids={domain.counterEvidenceIds}
                    label="Counter-sources"
                    className="evidence-link--counter"
                  />
                )}
              </div>
            </article>
          )
        })}
      </div>
    </section>
  )
}
