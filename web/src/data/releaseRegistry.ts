/**
 * Public suppliers whose quarterly revenue comes from the results release they
 * furnish to the SEC on Form 6-K, not from XBRL (backlog SEC-080).
 *
 * A foreign private issuer files no 10-Q, so EDGAR's structured companyfacts
 * hold no discrete quarters for it (see `unsupported` in edgarRegistry.ts).
 * Its results release is still an SEC filing. `web/scripts/release-refresh.ts`
 * reads the 6-K primary documents listed in the filer's own submissions index
 * and takes the "Total revenues" row of the income statement table with a
 * fixed parser (`sixKLogic.ts`). No model is involved.
 *
 * These figures are company-reported. They are not part of the certified SEC
 * cohort (`certifiedContract.json`), and the page labels them that way.
 */
export interface ReleaseSupplier {
  /** Stable id for the generated record. */
  id: string
  /** Tracker supplier id whose revenue this record feeds. */
  supplierId: string
  name: string
  /** Ten-digit, zero-padded SEC CIK. */
  cik: string
  form: '6-K'
}

export const releaseRegistry: ReleaseSupplier[] = [
  { id: 'checkpoint', supplierId: 'checkpoint-sase', name: 'Check Point Software Technologies', cik: '0001015922', form: '6-K' },
]
