import { AUTHOR_NAME } from './meta'
import type { Correction } from './types'

/**
 * Append-only list of owner-approved corrections. Never edit an existing
 * entry once published — add a new one instead. See docs/active/fable-run/
 * drafts/correction-2026-w36.md for the approval record (owner approved
 * 2026-09-20, decisions.md D-68) and CorrectedReading in types.ts for the
 * per-item shape.
 *
 * Approved text is reproduced verbatim from the owner-approved draft, with
 * "[date approved]" replaced by the actual approval date.
 */
export const corrections: Correction[] = [
  {
    id: 'C-2026-09-20-01',
    date: '2026-09-20',
    issueId: '2026-w36',
    approvedBy: AUTHOR_NAME,
    text:
      "Correction, 20 September 2026. In the issue for the week ending 6 September 2026, two headlines " +
      "gave a quarterly revenue figure as a full-year figure. Zscaler's revenue of $898.2 million and " +
      "Palo Alto Networks' revenue of $3.41 billion are each for the fiscal fourth quarter ended " +
      "31 July 2026, not for fiscal year 2026. The growth rates and the recurring-revenue figures were " +
      "stated correctly. The same issue described Palo Alto's 63 percent growth in Next-Generation " +
      "Security recurring revenue as the fastest of the week's results; that figure is a company-defined " +
      "segment and is not comparable with other companies' total revenue growth, so the comparison is " +
      'withdrawn. The original text is unchanged in the record. Jesse Pike.',
    correctedReadings: [
      {
        itemId: '2026-w36-prints-2',
        correctedHeadline:
          'Zscaler fiscal fourth-quarter revenue (quarter ended 31 July 2026) grows to $898.2M, +25% YoY; ARR grows to $3,771M, +25%',
        evidenceIds: ['W36-15'],
      },
      {
        itemId: '2026-w36-prints-6',
        correctedHeadline:
          'Palo Alto fiscal fourth-quarter revenue (quarter ended 31 July 2026) grows 34% to $3.41B; Next-Gen Security ARR $9.10B, +63%',
        evidenceIds: ['W36-19'],
        note:
          'The original "why it matters" comparison — that this growth was the fastest among this ' +
          "week's public-issuer prints — is withdrawn. Next-Gen Security ARR is a company-defined " +
          "segment and is not comparable with other companies' total revenue growth.",
      },
    ],
  },
]
