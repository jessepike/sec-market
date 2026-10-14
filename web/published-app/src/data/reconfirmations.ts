import type { Reconfirmation } from './types'

/**
 * Append-only record of owner-approved reconfirmations (SEC-MARKET-PUBLISH-001
 * §4.3). Never edit or remove an entry once written — add a new one instead,
 * the same append-only discipline as corrections.ts. Written only by
 * `scripts/sign-issue.ts` (via `scripts/reconfirmLogic.ts` and
 * `scripts/reconfirmRender.ts`), and only when the owner's approval of a
 * weekly issue pull request contained the word `reconfirm`. Starts empty:
 * nothing on the site has ever been re-dated under this mechanism.
 *
 * Reading this file directly is rarely what you want — use
 * `effectiveJudgment()` in `reconfirmationHelpers.ts`, which combines a
 * claim's original `judgedOn` with the newest entry here for that claim, if
 * any.
 */
export const reconfirmations: Reconfirmation[] = []
