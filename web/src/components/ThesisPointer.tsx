import { marketCall } from '../data/market'
import { AUTHOR_NAME, LAST_UPDATED_DISPLAY, LAST_UPDATED_ISO } from '../data/meta'

/**
 * Front-page pointer to the standing thesis (SEC-MARKET-FABLE-001 T6-16).
 * product-core.md §5: the founding thesis is "one standing analysis on the
 * site, not the site's identity", so it keeps its own home at `/thesis/`
 * and the front page carries only this compact pointer to it — the full
 * argument (JudgmentBoard, the running score, the Do/Avoid panels) moved to
 * that page.
 *
 * Keeps the section id `read`, unchanged from what JudgmentBoard used to
 * render here, so `/#read` anchors, the prerender must-see gate, and any
 * existing deep link keep resolving to this same spot on the front page.
 *
 * marketCall carries no thesis-specific "judged" date of its own — only the
 * site-wide LAST_UPDATED stamp, which is the same date HeroContent shows in
 * its own UPDATED line on the full /thesis/ page — so the JUDGED line here
 * reuses that constant rather than inventing a new one.
 */
export function ThesisPointer() {
  return (
    <section id="read" className="thesis-pointer" aria-labelledby="thesis-pointer-heading">
      <p className="eyebrow">Standing analysis</p>
      <h2 id="thesis-pointer-heading">Does security spending lag infrastructure spending?</h2>
      <p className="thesis-pointer__position">{marketCall.headline}</p>
      <p className="stamp-label">
        JUDGED <time dateTime={LAST_UPDATED_ISO}>{LAST_UPDATED_DISPLAY}</time> &middot; {AUTHOR_NAME}
      </p>
      <p className="thesis-pointer__link">
        <a href="/thesis/">Read the analysis and its record</a>
      </p>
    </section>
  )
}
