import { currentEdition } from '../data/edition'
import { contextStats, marketCall } from '../data/market'
import { LAST_UPDATED_DISPLAY } from '../data/meta'
import { EvidenceLink } from './EvidenceLink'

export function Hero() {
  return (
    <section id="overview" className="masthead" aria-labelledby="market-call-heading">
      <p className="eyebrow">Security Market Pulse · August 2026</p>
      <h2 id="market-call-heading">
        Infrastructure is running ahead.
        <br />
        Security is splitting, not booming.
      </h2>
      <div className="stamp">
        <span>
          EDITION <b>{currentEdition.id}</b>
        </span>
        <span>
          UPDATED <b>{LAST_UPDATED_DISPLAY}</b>
        </span>
        <span>
          LAG <b>NO-CALL</b>
        </span>
      </div>

      <div className="context-band">
        <p className="eyebrow">Market condition · not vendor performance</p>
        <div className="context-band__grid">
          {contextStats.map((stat) => (
            <div key={stat.label} className={`context-stat context-stat--${stat.tone}`}>
              <p className="context-stat__value">{stat.value}</p>
              <p className="context-stat__label">{stat.label}</p>
            </div>
          ))}
        </div>
        <p className="context-band__note">{marketCall.subhead}</p>
        <EvidenceLink ids={marketCall.evidenceIds} label="Sources" />
      </div>
    </section>
  )
}
