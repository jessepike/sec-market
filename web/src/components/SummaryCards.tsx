import { summaryCards } from '../data/market'
import { EvidenceLink } from './EvidenceLink'
import { StatusBadge } from './StatusBadge'

export function SummaryCards() {
  return (
    <section className="summary-cards" aria-label="Market summary">
      <div className="summary-cards__grid">
        {summaryCards.map((card) => (
          <article key={card.id} className="summary-card">
            <p className="summary-card__label">{card.label}</p>
            <h2 className="summary-card__headline">
              {card.id === 'lag' ? <StatusBadge kind="no-call" /> : card.headline}
            </h2>
            <p className="summary-card__detail">{card.detail}</p>
            <p className="summary-card__disposition">{card.disposition}</p>
            <EvidenceLink ids={card.evidenceIds} label="Sources" />
          </article>
        ))}
      </div>
    </section>
  )
}
