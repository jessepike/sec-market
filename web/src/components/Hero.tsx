import { marketCall } from '../data/market'
import { LAST_UPDATED_DISPLAY } from '../data/meta'
import { EvidenceLink } from './EvidenceLink'
import { StatusBadge } from './StatusBadge'

export function Hero() {
  return (
    <section id="overview" className="hero" aria-labelledby="market-call-heading">
      <div className="hero__meta">
        <StatusBadge kind="no-call" />
        <p className="hero__updated">
          Research freeze: <time dateTime="2026-08-15">{LAST_UPDATED_DISPLAY}</time>
        </p>
      </div>
      <h1 id="market-call-heading">{marketCall.headline}</h1>
      <p className="hero__subhead">{marketCall.subhead}</p>
      <div className="hero__body">
        <div className="hero__block">
          <h2>What it means</h2>
          <p>{marketCall.meaning}</p>
        </div>
        <div className="hero__block">
          <h2>Confidence</h2>
          <p>{marketCall.confidenceNote}</p>
        </div>
      </div>
      <div className="hero__boundaries">
        <h2>No-call boundaries</h2>
        <ul>
          {marketCall.noCallBoundaries.map((item) => (
            <li key={item}>
              <StatusBadge kind={item.includes('NO-CALL') ? 'no-call' : 'insufficient'} />
              <span>{item}</span>
            </li>
          ))}
        </ul>
      </div>
      <div className="hero__triggers">
        <h2>What would change the call</h2>
        <ul>
          {marketCall.changeTriggers.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </div>
      <EvidenceLink ids={marketCall.evidenceIds} label="Evidence for this call" />
    </section>
  )
}
