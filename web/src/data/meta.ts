export const EPISODE_ID = 'SEC-MARKET-SIG-002'
export const EPISODE_VERSION = '0.2'
export const RESEARCH_FREEZE = '2026-08-15T19:03:08-07:00'
/**
 * When the SITE was last updated. This is the as-of stamp on the rail and in
 * the header, and the sitemap's lastmod. It is not a judgment date.
 *
 * This constant used to carry four different facts at once — the site stamp,
 * the date on the tracked hypotheses, the date on the platform-pressure reads,
 * and the window `weekMoves` describes — so publishing an edition moved all
 * four together and re-dated judgments nobody had revisited. The other three
 * are now their own constants below. Move this one whenever the site ships.
 */
export const LAST_UPDATED_DISPLAY = 'September 21, 2026'
/** Machine-readable form of LAST_UPDATED_DISPLAY. Same date, ISO 8601. */
export const LAST_UPDATED_ISO = '2026-09-21'

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
export const CONTACT_EMAIL = 'jesse@keatingpike.com'

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
export const SITE_HEADLINE = 'The security market, from public numbers'

export const SITE_DESCRIPTION =
  "A practitioner's read on the business of the security market: who is growing, who is " +
  'consolidating, who is being bought, and what it means if you run a security program. Public ' +
  'sources only. Written by Jesse Pike.'

/** One-line disclaimer shown directly under SITE_DESCRIPTION, first screen, both widths. */
export const SITE_DISCLAIMER = 'Not a news site and not investment advice.'
