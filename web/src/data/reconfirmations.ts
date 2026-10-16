import type { Reconfirmation } from './types'

/**
 * Append-only record of owner-approved reconfirmations (SEC-MARKET-PUBLISH-001
 * §4.3). Never edit or remove an entry once written — add a new one instead,
 * the same append-only discipline as corrections.ts. Its only writer, the
 * weekly-issue signing script, was retired with the weekly issue (D-93) and
 * removed on 2026-10-16, so this list stays empty: nothing on the site was
 * ever re-dated under this mechanism.
 *
 * Reading this file directly is rarely what you want — use
 * `effectiveJudgment()` in `reconfirmationHelpers.ts`, which combines a
 * claim's original `judgedOn` with the newest entry here for that claim, if
 * any.
 */
export const reconfirmations: Reconfirmation[] = []
