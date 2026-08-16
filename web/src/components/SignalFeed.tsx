import { marketSignals } from '../data/signals'
import { formatIsoDate } from '../utils/formatDate'
import { EvidenceLink } from './EvidenceLink'

const categoryLabels: Record<string, string> = {
  financial: 'Financial',
  investment: 'Investment',
  buyer: 'Buyer',
  regulation: 'Regulation',
  operating: 'Operating',
  incident: 'Incident',
}

export function SignalFeed() {
  const sorted = [...marketSignals].sort((a, b) => b.date.localeCompare(a.date))

  return (
    <section id="signals" className="signal-feed" aria-labelledby="signals-heading">
      <div className="section-heading">
        <h2 id="signals-heading">Latest signals</h2>
        <p>Financial results, investment, buyer evidence, regulation, and operating events.</p>
      </div>
      <ol className="signal-feed__list">
        {sorted.map((signal) => (
          <li key={signal.id} className="signal-item">
            <div className="signal-item__meta">
              <time dateTime={signal.date}>{formatIsoDate(signal.date)}</time>
              <span className="signal-item__category">{categoryLabels[signal.category]}</span>
            </div>
            <h3>{signal.headline}</h3>
            <p>{signal.detail}</p>
            <EvidenceLink ids={signal.evidenceIds} />
          </li>
        ))}
      </ol>
    </section>
  )
}
