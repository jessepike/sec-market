import { LAST_UPDATED_DISPLAY, SITE_DESCRIPTION, SITE_DISCLAIMER, SITE_HEADLINE } from '../data/meta'

/**
 * The front page's masthead (SEC-MARKET-CORE-001 §5): what the site is, in
 * the largest type, above the run status and the market picture.
 *
 * Front page only. The issue permalink keeps IssueHero, where the issue's
 * own read is the `h1` because there it really is the page's subject.
 *
 * D-76/autonomy-coverage-plan.md §3, step 1: the as-of line used to add
 * "Domain stances judged <date> by <name>" — a judgment stamp. The site
 * no longer publishes domain stances on live pages, so that clause is
 * dropped rather than left pointing at nothing.
 */
/**
 * Coordinator follow-up after reviewing the fix pass 4 after-renders: at
 * 390px the first supplier row's top sat at 840.9px, leaving the whole row
 * off screen — the target is the row's bottom at or under 820px. This
 * description plus the stamps line below it ran to about six lines before
 * the run-status box even started. Neither is mine to shorten (SITE_
 * DESCRIPTION and SITE_DISCLAIMER are data/meta.ts values), so both now sit
 * inside a <details>, the same disclosure pattern as .run-status__failed
 * and the page's own .depth sections. index.css forces it open with no
 * visible summary above 640px (the coordinator's own "at phone width"
 * framing, and desktop never had a first-screen problem) — every word
 * stays on the page either way, just one tap away at phone width instead
 * of always on screen.
 */
export function SiteMasthead() {
  return (
    <section className="site-masthead" aria-labelledby="site-masthead-heading">
      <h1 id="site-masthead-heading">{SITE_HEADLINE}</h1>
      <details className="masthead-more">
        <summary>What this site is</summary>
        <p className="site-masthead__description">{SITE_DESCRIPTION}</p>
        <p className="site-masthead__stamps">
          {SITE_DISCLAIMER} · Site updated {LAST_UPDATED_DISPLAY}.
        </p>
      </details>
    </section>
  )
}
