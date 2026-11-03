/**
 * Rows that report one transaction on different dates, such as an announcement and its completion.
 * Same-day rows about one deal are grouped automatically in `countedUnits` (presentation.ts).
 * Add a pair here when a deal's stages are both tracked, so the counts show it once.
 */
export const dealIds: Record<string, string> = {
  'EV-delinea-2': 'delinea-strongdm-2026',
  'EV-delinea-3': 'delinea-strongdm-2026',
}
