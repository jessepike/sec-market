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
export function SiteMasthead() {
  return (
    <section className="site-masthead" aria-labelledby="site-masthead-heading">
      <h1 id="site-masthead-heading">{SITE_HEADLINE}</h1>
      <p className="site-masthead__description">{SITE_DESCRIPTION}</p>
      <p className="site-masthead__stamps">
        {SITE_DISCLAIMER} · Site updated {LAST_UPDATED_DISPLAY}.
      </p>
    </section>
  )
}
