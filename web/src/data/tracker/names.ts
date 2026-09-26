/**
 * Supplier display-name shortening, split out of `derive.ts` (third fix
 * pass, item 1/2) so it has zero dependencies of its own. `derive.ts`
 * imports `runStatus` (for `eventSummaryForSupplier`'s trailing-window
 * math), and `runStatus.ts` needs a short, readable supplier name for the
 * "Which sources failed" disclosure — importing `shortSupplierName` from
 * `derive.ts` there would be a circular import. This module has no imports
 * at all, so both `derive.ts` and `runStatus.ts` can depend on it safely.
 * `derive.ts` re-exports `shortSupplierName` from here, so every existing
 * `from '../data/tracker/derive'` import keeps working unchanged.
 *
 * Density pass (coordinator instruction, following the step 5 build) — a
 * reader-facing short name, stripping the legal-entity suffix a filing or
 * press release carries ("CrowdStrike Holdings, Inc." -> "CrowdStrike") but
 * leaving genuine brand words alone ("Palo Alto Networks", "Cato Networks",
 * "Microsoft Defender for Endpoint" are untouched). The full legal name
 * stays wherever a name is sourced as a fact — evidence.ts, and the `title`
 * attribute anywhere this is used. A trailing parenthetical alternate name
 * ("Sophos Group (Sophos Ltd)") is dropped in favor of the leading name.
 */
const LEGAL_SUFFIX = /,?\s+(Incorporated|Corporation|Corp\.?|Holdings|Technologies|Software|Group|Inc\.?|LLC|Ltd\.?|Limited)$/i

export function shortSupplierName(name: string): string {
  let short = name.trim().replace(/\s*\([^)]*\)\s*$/, '')
  let previous: string
  do {
    previous = short
    short = short.replace(LEGAL_SUFFIX, '').trim()
  } while (short !== previous && short.length > 0)
  return short || name
}
