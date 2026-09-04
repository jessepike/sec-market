import type { ReactNode } from 'react'
import { marketCall } from '../data/market'
import { EvidenceLink } from './EvidenceLink'

/**
 * `leadContent` renders inside `#read` before the existing "The read" content
 * — the weekly-issue front page uses it to carry the thesis running score and
 * the market-call headline (HeroContent) into this same section, so `#read`
 * stays the one standing-reference thesis block the spec calls for. Omitted,
 * this renders exactly as it always has.
 */
export function JudgmentBoard({ leadContent }: { leadContent?: ReactNode } = {}) {
  return (
    <section id="read" className="judgment" aria-labelledby="judgment-heading">
      {leadContent}
      <div className="section-heading">
        <h2 id="judgment-heading">The read</h2>
        <p>{marketCall.confidenceNote}</p>
      </div>

      <div className="judgment__grid">
        <div className="judgment__card">
          <h3>What changed</h3>
          <ol className="judgment__list">
            {marketCall.whatChanged.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ol>
        </div>
        <div className="judgment__split">
          <div className="judgment__card">
            <h3>Do</h3>
            <ul className="judgment__list">
              {marketCall.actions.doItems.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>
          <div className="judgment__card">
            <h3>Avoid</h3>
            <ul className="judgment__list judgment__list--avoid">
              {marketCall.actions.avoidItems.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>
        </div>
        <div className="judgment__card">
          <h3>We will not call</h3>
          <ul className="judgment__list">
            {marketCall.noCallBoundaries.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
        <div className="judgment__card">
          <h3>What would change the call</h3>
          <ul className="judgment__list">
            {marketCall.changeTriggers.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      </div>
      <EvidenceLink ids={marketCall.evidenceIds} label="Sources" />
    </section>
  )
}
