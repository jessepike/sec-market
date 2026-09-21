import { formatShortDate } from '../data/dates'
import { issues } from '../data/issues/index'
import { newestThesisJudgment } from '../data/issueHelpers'
import { marketCall } from '../data/market'

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
 * The JUDGED stamp is the newest published issue's actual signed thesis
 * date (`newestThesisJudgment`, sourced from `weThink.signedOn`/`signedBy`)
 * — never the site-wide LAST_UPDATED stamp, which only says when the site
 * last shipped a change, not when anyone judged the thesis. When no issue
 * has signed a thesis verdict yet, the stamp is omitted rather than
 * inventing one.
 */
export function ThesisPointer() {
  const judgment = newestThesisJudgment(issues)

  return (
    <section id="read" className="thesis-pointer" aria-labelledby="thesis-pointer-heading">
      <p className="eyebrow">Standing analysis</p>
      <h2 id="thesis-pointer-heading">Does security spending lag infrastructure spending?</h2>
      <p className="thesis-pointer__position">{marketCall.headline}</p>
      {judgment && (
        <p className="stamp-label">
          JUDGED <time dateTime={judgment.signedOn}>{formatShortDate(judgment.signedOn)}</time> &middot;{' '}
          {judgment.signedBy}
        </p>
      )}
      <p className="thesis-pointer__link">
        <a href="/thesis/">Read the analysis and its record</a>
      </p>
    </section>
  )
}
