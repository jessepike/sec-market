import type { Correction, EvidenceRecord, Issue } from './types'

/** Every correction, newest first by `date` — the ordering `/corrections/` and `corrections.json` use. */
export function correctionsNewestFirst(corrections: Correction[]): Correction[] {
  return [...corrections].sort((a, b) => b.date.localeCompare(a.date))
}

/** Every correction that applies to one issue, in no particular order. */
export function correctionsForIssue(corrections: Correction[], issueId: string): Correction[] {
  return corrections.filter((correction) => correction.issueId === issueId)
}

/** The correction (if any) covering a specific item, and that item's corrected reading. */
export function correctionForItem(
  corrections: Correction[],
  itemId: string,
): { correction: Correction; reading: Correction['correctedReadings'][number] } | null {
  for (const correction of corrections) {
    const reading = correction.correctedReadings.find((candidate) => candidate.itemId === itemId)
    if (reading) return { correction, reading }
  }
  return null
}

/**
 * The stable `{ ... }` shape written to `dist/corrections.json` — every
 * correction, newest first, with the URL of its HTML anchor on
 * `/corrections/`. Shared by generate-feed.ts (which writes it) and
 * verify-dist.ts (which checks it), so the writer and its own checker cannot
 * compute the payload two different ways.
 */
export function correctionsJsonPayload(
  corrections: Correction[],
  siteUrl: string,
): Array<Correction & { url: string }> {
  return correctionsNewestFirst(corrections).map((correction) => ({
    ...correction,
    url: `${siteUrl}/corrections/#${correction.id}`,
  }))
}

export interface FiscalPeriodViolation {
  issueId: string
  itemId: string
  headline: string
  economicPeriod: string
  evidenceId: string
}

/**
 * A headline stating a fiscal-year or full-year period ("FY2026", "fiscal
 * year", "full-year", "full year") while citing evidence whose economicPeriod
 * begins with "Quarter" is exactly the mistake corrected by
 * SEC-MARKET-FABLE-001 T6-13 (see docs/active/fable-run/drafts/
 * correction-2026-w36.md). This is the gate that would have caught it before
 * publication: it flags every item matching that pattern, in every issue,
 * unless the item is already covered by an entry in corrections.ts. Used by
 * scripts/verify-issue.ts's check 16 and unit-tested directly in
 * tests/corrections-data.test.ts so the gate's own logic can be proven
 * without a full build.
 */
const FISCAL_YEAR_PATTERN = /\bFY\s?\d{2,4}\b|\bfiscal\s+year\b|\bfull-year\b|\bfull\s+year\b/i

export function findFiscalPeriodMismatches(
  issues: Issue[],
  evidenceById: Record<string, EvidenceRecord>,
  corrections: Correction[],
): FiscalPeriodViolation[] {
  const violations: FiscalPeriodViolation[] = []
  for (const issue of issues) {
    for (const section of issue.sections) {
      for (const item of section.items) {
        if (!FISCAL_YEAR_PATTERN.test(item.headline)) continue

        const quarterlyEvidence = item.evidenceIds
          .map((id) => ({ id, record: evidenceById[id] }))
          .find(({ record }) => record && record.economicPeriod.startsWith('Quarter'))
        if (!quarterlyEvidence) continue

        const isCorrected = corrections.some(
          (correction) =>
            correction.issueId === issue.id &&
            correction.correctedReadings.some((reading) => reading.itemId === item.id),
        )
        if (isCorrected) continue

        violations.push({
          issueId: issue.id,
          itemId: item.id,
          headline: item.headline,
          economicPeriod: quarterlyEvidence.record.economicPeriod,
          evidenceId: quarterlyEvidence.id,
        })
      }
    }
  }
  return violations
}
