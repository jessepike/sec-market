import { currentEdition } from '../data/edition'
import { contextStats, marketCall } from '../data/market'
import { LAST_UPDATED_DISPLAY } from '../data/meta'
import { EvidenceLink } from './EvidenceLink'

/**
 * Shared body for the market-call headline, stamp and context band. Extracted
 * so the weekly-issue front page can carry this same content as an `h2`
 * inside the standing-reference thesis block (`#read`) instead of duplicating
 * it — see HeroContent below and JudgmentBoard's `leadContent` prop.
 */
function HeroBody({ headingLevel }: { headingLevel: 'h1' | 'h2' }) {
  const Heading = headingLevel
  return (
    <>
      <p className="eyebrow">Security Market Pulse · August 2026</p>
      <Heading id="market-call-heading">
        Infrastructure is running ahead.
        <br />
        Security is splitting, not booming.
      </Heading>
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
    </>
  )
}

/**
 * The original standalone masthead. Unused on the weekly-issue front page
 * (superseded there by IssueHero's `#overview`, and by HeroContent inside the
 * standing-reference thesis block) but kept exported and working so nothing
 * that already imports it breaks.
 */
export function Hero() {
  return (
    <section id="overview" className="masthead" aria-labelledby="market-call-heading">
      <HeroBody headingLevel="h1" />
    </section>
  )
}

/**
 * The same market-call headline, stamp and context band as Hero(), without
 * the outer `<section id="overview">` wrapper and as an `h2` rather than an
 * `h1` — for embedding inside another section (the thesis block, `#read`)
 * that already owns the top-level heading and section id.
 */
export function HeroContent() {
  return <HeroBody headingLevel="h2" />
}
