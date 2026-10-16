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
 * The weekly gather job must never edit this file (docs/archive/2026-09-weekly-issue/gather-brief.md).
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
      'The card is labelled "FY26," and its cited evidence (C13) gives economicPeriod "Quarter ' +
      'ended 2026-01-31." For an ending-ARR balance, the balance at that quarter end and the ' +
      'balance at fiscal year end are the same number, so the label is probably acceptable — it is ' +
      'not the flow mistake SEC-043 corrected, where a quarter\'s revenue was mislabelled a year\'s ' +
      'revenue. But the check cannot tell a balance metric from a flow metric, because ' +
      'EvidenceRecord carries no structured metric field, so this is listed for the owner to ' +
      'confirm or to relabel as "JAN ’26," the way the total CrowdStrike ARR card ' +
      '(print-crwd) is labelled "APR ’26" rather than "FY26." Found by scripts/verify-prints.ts ' +
      '(SEC-044); not changed here.',
  },
]
