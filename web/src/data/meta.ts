import { formatLongDate } from './dates'
import { runStatus } from './runStatus'

export const EPISODE_ID = 'SEC-MARKET-SIG-002'
export const EPISODE_VERSION = '0.2'
export const RESEARCH_FREEZE = '2026-08-15T19:03:08-07:00'
/**
 * When the SITE was last updated. This is the as-of stamp on the rail, the
 * header, the front-page masthead, and the sitemap's lastmod. It is not a
 * judgment date.
 *
 * AUTO-001 step 1 fix pass, item 2: this used to be a hand-set constant that
 * could drift out of step with the run-status box (the rail said one date,
 * the masthead said another, the run-status line said a third). It is now
 * derived from `runStatus.lastChecked` — the single source every rendered
 * "as of" / "site updated" / masthead date reads from, so they cannot
 * disagree. Move the site's as-of date by moving `runStatus.lastChecked`,
 * not by editing this constant directly.
 *
 * This constant used to also carry three other facts at once — the date on
 * the tracked hypotheses, the date on the platform-pressure reads, and the
 * window `weekMoves` describes — those are their own constants below and are
 * untouched by this derivation.
 */
export const LAST_UPDATED_ISO = runStatus.lastChecked
/** Long-form display of LAST_UPDATED_ISO, e.g. `September 25, 2026`. */
export const LAST_UPDATED_DISPLAY = formatLongDate(LAST_UPDATED_ISO)

/**
 * When a person last signed the tracked hypotheses and the platform-pressure
 * reads. Move this only when those judgments are actually reviewed again.
 * Shipping the site is not reviewing them.
 */
export const JUDGED_AS_OF_ISO = '2026-08-17'

/** Last day of the seven-day window `weekMoves` describes. */
export const WEEK_MOVES_ENDING_ISO = '2026-08-17'
export const PRODUCT_TITLE = 'Security Market Pulse'
export const SITE_URL = 'https://securitymarketpulse.com'
export const AUTHOR_NAME = 'Jesse Pike'
export const CONTACT_EMAIL = 'jp@jessepike.dev'
/** License for the published data and pages (owner decision, 2026-11-06, D-139). */
export const DATA_LICENSE = 'CC-BY-4.0'
export const DATA_LICENSE_URL = 'https://creativecommons.org/licenses/by/4.0/'

/**
 * One-sentence description of what the site is (design-spec v0.3 §3.2). Shown
 * as the first content in #overview and reused for the page description —
 * see index.html's <meta name="description"> and the machine surface
 * (scripts/generate-seo.ts reads it back off the built page). The owner edits
 * this on the preview.
 */
/**
 * The front page's `h1` (SEC-MARKET-CORE-001 §5). It names what the site is
 * about and does not change from week to week.
 *
 * It used to be the newest issue's one-line read, which made the biggest type
 * on the page a news headline for one week — wrong for a site whose own
 * description says it is not a news site, and wrong for a first-time reader
 * who learns what the site covers only from the grey line above it. The
 * weekly read now sits in the issue strip under this, still the first thing
 * a returning reader sees, and it is still the `h1` on the issue's own page
 * where it is genuinely that page's subject. The owner edits this line.
 */
export const SITE_HEADLINE = 'Who grew. Who raised. Who bought. Who cut.'

export const SITE_DESCRIPTION =
  'Public, sourced facts about the business of the security market: who is growing, stalling, ' +
  'consolidating, being bought, or in financial trouble. Collected, checked and published ' +
  'automatically, with no stances, rankings or forecasts. Public sources only.'

/** One-line disclaimer shown directly under SITE_DESCRIPTION, first screen, both widths. */
export const SITE_DISCLAIMER = 'Not a news site and not investment advice.'

/**
 * D-80 (2026-10-02): the site's one neutral independence line, shown as its
 * own paragraph near the top of the Method section (HowThisWorks.tsx). Names
 * no employer and makes no other claim — use the exact words.
 */
export const INDEPENDENCE_STATEMENT =
  'Security Market Pulse is independent and is not sponsored or paid for by any company it tracks.'
