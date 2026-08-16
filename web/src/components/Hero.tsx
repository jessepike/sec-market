import { marketCall } from '../data/market'
import { LAST_UPDATED_DISPLAY } from '../data/meta'
import { EvidenceLink } from './EvidenceLink'

export function Hero() {
  return (
    <section id="overview" className="hero" aria-labelledby="market-call-heading">
      <p className="hero__updated">
        Last updated <time dateTime="2026-08-15">{LAST_UPDATED_DISPLAY}</time>
      </p>
      <h1 id="market-call-heading">{marketCall.headline}</h1>
      <p className="hero__subhead">{marketCall.subhead}</p>

      <div className="hero__above-fold">
        <div className="hero__block hero__block--changed">
          <h2>What changed</h2>
          <ul>
            {marketCall.whatChanged.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>

        <div className="hero__actions">
          <div className="hero__block hero__block--do">
            <h2>What to do</h2>
            <ul>
              {marketCall.actions.doItems.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>
          <div className="hero__block hero__block--avoid">
            <h2>What not to claim</h2>
            <ul>
              {marketCall.actions.avoidItems.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>
        </div>
      </div>

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

      <details className="hero__details">
        <summary>Lag boundaries &amp; what would change the call</summary>
        <div className="hero__boundaries">
          <h3>Not supported from current evidence</h3>
          <ul>
            {marketCall.noCallBoundaries.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
        <div className="hero__triggers">
          <h3>Would change the call</h3>
          <ul>
            {marketCall.changeTriggers.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      </details>

      <EvidenceLink ids={marketCall.evidenceIds} label="Sources for this call" />
    </section>
  )
}
