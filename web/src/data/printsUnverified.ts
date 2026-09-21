/**
 * The figure-meaning check's exemption list (publish-path-spec.md §4.1,
 * SEC-044/SEC-045). An existing `prints.ts` entry that cannot pass
 * scripts/verify-prints.ts goes here, dated, with the reason in plain words
 * — it is never deleted and never silently exempted. `scripts/verify-prints.ts`
 * still checks a listed print and prints its result as a warning rather than
 * a build failure; it does not skip the check.
 *
 * Shrink-only: this list may only get shorter over time (an entry is
 * removed once the underlying print is corrected or retired through the
 * owner's normal correction process — never edited here). Growing it needs
 * the owner's word; see `scripts/prints-unverified-baseline.json` and the
 * comment beside where verify-prints.ts reads it.
 *
 * The weekly gather job must never edit this file (docs/active/gather-brief.md).
 */
export interface PrintsUnverifiedEntry {
  /** A VendorPrint id from web/src/data/prints.ts. */
  id: string
  /** ISO date this entry was added to the list. */
  dateListed: string
  /** Plain-language reason the print cannot pass, or cannot be checked. */
  reason: string
}

export const printsUnverified: PrintsUnverifiedEntry[] = [
  {
    id: 'print-crwd-cloud',
    dateListed: '2026-09-21',
    reason:
      'The card labels the period "FY26" (a full fiscal year), but the print cites only C13, ' +
      'whose economicPeriod is "Quarter ended 2026-01-31" — a single quarter\'s ending ARR ' +
      '(CrowdStrike\'s Q4 FY2026 Falcon Cloud segment), not a fiscal-year figure. The same shape ' +
      'of mistake SEC-043 corrected on an issue headline. The figure itself ($800M+, >35%) is not ' +
      'in question — only the period label is wrong. Found by scripts/verify-prints.ts (SEC-044); ' +
      'not fixed here per the owner\'s correction process.',
  },
]
