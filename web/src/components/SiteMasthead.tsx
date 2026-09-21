import { formatShortDate } from '../data/dates'
import { securityDomains } from '../data/domains'
import {
  AUTHOR_NAME,
  LAST_UPDATED_DISPLAY,
  SITE_DESCRIPTION,
  SITE_DISCLAIMER,
  SITE_HEADLINE,
} from '../data/meta'

// Same derivation as IssueHero's as-of line used: the newest judgment date
// across the domain cards, read off the same data the cards render, so the
// line agrees with them by construction rather than by coincidence.
const domainsJudgedIso = securityDomains.reduce(
  (latest, domain) => (domain.asOf > latest ? domain.asOf : latest),
  securityDomains[0].asOf,
)

/**
 * The front page's masthead (SEC-MARKET-CORE-001 §5): what the site is, in
 * the largest type, above the weekly issue strip and the market picture.
 *
 * Front page only. The issue permalink keeps IssueHero, where the issue's
 * own read is the `h1` because there it really is the page's subject.
 */
export function SiteMasthead() {
  return (
    <section className="site-masthead" aria-labelledby="site-masthead-heading">
      <h1 id="site-masthead-heading">{SITE_HEADLINE}</h1>
      <p className="site-masthead__description">{SITE_DESCRIPTION}</p>
      {/* One line rather than three stacked grey lines: the disclaimer and
          both stamps carry the same weight and reading them together is how
          anyone actually uses them. */}
      <p className="site-masthead__stamps">
        {SITE_DISCLAIMER} · Site updated {LAST_UPDATED_DISPLAY} · Domain stances judged{' '}
        {formatShortDate(domainsJudgedIso)} by {AUTHOR_NAME}.
      </p>
    </section>
  )
}
