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

function SignalList({
  signals,
  headingId,
  heading,
  intro,
}: {
  signals: typeof marketSignals
  headingId: string
  heading: string
  intro: string
}) {
  return (
    <div className="signal-group">
      <div className="section-heading">
        <h3 id={headingId}>{heading}</h3>
        <p>{intro}</p>
      </div>
      <ol className="signal-feed__list">
        {signals.map((signal) => (
          <li key={signal.id} className="signal-item">
            <div className="signal-item__meta">
              <time dateTime={signal.date}>{formatIsoDate(signal.date)}</time>
              <span className="signal-item__category">{categoryLabels[signal.category]}</span>
            </div>
            <h4>{signal.headline}</h4>
            <p>{signal.detail}</p>
            <EvidenceLink ids={signal.evidenceIds} />
          </li>
        ))}
      </ol>
    </div>
  )
}

export function SignalFeed() {
  const current = marketSignals
    .filter((signal) => signal.freshness === 'current')
    .sort((a, b) => b.date.localeCompare(a.date))
  const background = marketSignals
    .filter((signal) => signal.freshness === 'background')
    .sort((a, b) => b.date.localeCompare(a.date))

  return (
    <section id="signals" className="signal-feed" aria-labelledby="signals-heading">
      <div className="section-heading">
        <h2 id="signals-heading">Signals</h2>
        <p>Current-period prints first. Older context stays in the background.</p>
      </div>
      <SignalList
        signals={current}
        headingId="signals-current"
        heading="This period"
        intro="Latest frozen financial prints, buyer intent, and operating events."
      />
      <details className="signal-background">
        <summary>Background — 2025 budget, M&A, regulation, and incidents</summary>
        <SignalList
          signals={background}
          headingId="signals-background"
          heading="Background"
          intro="Still in the evidence base. Not this month’s news."
        />
      </details>
    </section>
  )
}
