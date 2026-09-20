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
export const LAST_UPDATED_DISPLAY = 'September 19, 2026'
/** Machine-readable form of LAST_UPDATED_DISPLAY. Same date, ISO 8601. */
export const LAST_UPDATED_ISO = '2026-09-19'

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
