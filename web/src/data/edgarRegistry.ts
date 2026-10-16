/**
 * SEC EDGAR coverage registry — step 2 of the autonomy plan
 * (docs/archive/2026-10-refresh-gate/autonomy-coverage-plan.md §4–5, D-76/D-77). Lists the public
 * suppliers whose quarterly GAAP revenue can be pulled straight from SEC
 * EDGAR's structured XBRL "companyfacts" API with no model in the loop, so
 * the figure can never be invented. `web/scripts/edgar-refresh.ts` reads
 * this registry and fetches each supplier in turn.
 *
 * `id` reuses the supplier id already used in `prints.ts` (the `print-<id>`
 * ids there, with the `print-` prefix stripped) wherever that supplier is
 * already tracked, so the two data sets can be joined later without a
 * remapping table. A supplier with no existing print gets a fresh short id
 * in the same style.
 *
 * `cik` is the ten-digit, zero-padded SEC filer id, exactly as EDGAR expects
 * it in `https://data.sec.gov/api/xbrl/companyfacts/CIK##########.json`.
 * Every CIK below was looked up against `https://www.sec.gov/files/company_tickers.json`
 * on 2026-09-25 and cross-checked against that filer's own
 * `https://data.sec.gov/submissions/CIK##########.json` (name + fiscal year
 * end match).
 *
 * `revenueConcepts` is a priority list of us-gaap XBRL concept names. The
 * refresh script tries each in order and uses the first one present in that
 * filer's companyfacts with USD-denominated quarterly facts. Most filers
 * that adopted ASC 606 (all of these did, years ago) tag revenue under
 * `RevenueFromContractWithCustomerExcludingAssessedTax`; `Revenues` is kept
 * as a fallback for any filer that still uses the older, broader tag for a
 * given period.
 */

export interface EdgarSupplier {
  /** Stable id, joins to `print-<id>` in prints.ts where that supplier is tracked there. */
  id: string
  /** Display name for reports and the generated JSON. */
  name: string
  /** Ticker, for human cross-reference only — not used to call the API. */
  ticker: string
  /** Ten-digit, zero-padded SEC CIK. */
  cik: string
  /** Fiscal year end as MMDD, from that filer's own EDGAR submissions record. */
  fiscalYearEnd: string
  /** us-gaap concept names to try, in priority order. */
  revenueConcepts: string[]
}

export interface UnsupportedSupplier {
  id: string
  name: string
  ticker?: string
  cik?: string
  reason: string
}

const STANDARD_REVENUE_CONCEPTS = [
  'RevenueFromContractWithCustomerExcludingAssessedTax',
  'RevenueFromContractWithCustomerIncludingAssessedTax',
  'Revenues',
]

export const edgarRegistry: EdgarSupplier[] = [
  {
    id: 'crwd',
    name: 'CrowdStrike',
    ticker: 'CRWD',
    cik: '0001535527',
    fiscalYearEnd: '0131',
    revenueConcepts: STANDARD_REVENUE_CONCEPTS,
  },
  {
    id: 'zscaler',
    name: 'Zscaler',
    ticker: 'ZS',
    cik: '0001713683',
    fiscalYearEnd: '0731',
    revenueConcepts: STANDARD_REVENUE_CONCEPTS,
  },
  {
    id: 'panw',
    name: 'Palo Alto Networks',
    ticker: 'PANW',
    cik: '0001327567',
    fiscalYearEnd: '0731',
    revenueConcepts: STANDARD_REVENUE_CONCEPTS,
  },
  {
    id: 'fortinet',
    name: 'Fortinet',
    ticker: 'FTNT',
    cik: '0001262039',
    fiscalYearEnd: '1231',
    revenueConcepts: STANDARD_REVENUE_CONCEPTS,
  },
  {
    id: 'cloudflare',
    name: 'Cloudflare',
    ticker: 'NET',
    cik: '0001477333',
    fiscalYearEnd: '1231',
    revenueConcepts: STANDARD_REVENUE_CONCEPTS,
  },
  {
    id: 'okta',
    name: 'Okta',
    ticker: 'OKTA',
    cik: '0001660134',
    fiscalYearEnd: '0131',
    revenueConcepts: STANDARD_REVENUE_CONCEPTS,
  },
  {
    id: 'sailpoint',
    name: 'SailPoint',
    ticker: 'SAIL',
    cik: '0002030781',
    fiscalYearEnd: '0131',
    revenueConcepts: STANDARD_REVENUE_CONCEPTS,
  },
  {
    id: 's1',
    name: 'SentinelOne',
    ticker: 'S',
    cik: '0001583708',
    fiscalYearEnd: '0131',
    revenueConcepts: STANDARD_REVENUE_CONCEPTS,
  },
  {
    id: 'rubrik',
    name: 'Rubrik',
    ticker: 'RBRK',
    cik: '0001943896',
    fiscalYearEnd: '0131',
    revenueConcepts: STANDARD_REVENUE_CONCEPTS,
  },
  {
    id: 'varonis',
    name: 'Varonis',
    ticker: 'VRNS',
    cik: '0001361113',
    fiscalYearEnd: '1231',
    revenueConcepts: STANDARD_REVENUE_CONCEPTS,
  },
  {
    id: 'netskope',
    name: 'Netskope',
    ticker: 'NTSK',
    cik: '0002063196',
    fiscalYearEnd: '0131',
    revenueConcepts: STANDARD_REVENUE_CONCEPTS,
  },
  {
    id: 'tenable',
    name: 'Tenable',
    ticker: 'TENB',
    cik: '0001660280',
    fiscalYearEnd: '1231',
    revenueConcepts: STANDARD_REVENUE_CONCEPTS,
  },
  {
    id: 'qualys',
    name: 'Qualys',
    ticker: 'QLYS',
    cik: '0001107843',
    fiscalYearEnd: '1231',
    revenueConcepts: STANDARD_REVENUE_CONCEPTS,
  },
  {
    id: 'rapid7',
    name: 'Rapid7',
    ticker: 'RPD',
    cik: '0001560327',
    fiscalYearEnd: '1231',
    revenueConcepts: STANDARD_REVENUE_CONCEPTS,
  },
  {
    id: 'commvault',
    name: 'Commvault Systems',
    ticker: 'CVLT',
    cik: '0001169561',
    fiscalYearEnd: '0331',
    revenueConcepts: STANDARD_REVENUE_CONCEPTS,
  },
  {
    id: 'jfrog',
    name: 'JFrog',
    ticker: 'FROG',
    cik: '0001800667',
    fiscalYearEnd: '1231',
    revenueConcepts: STANDARD_REVENUE_CONCEPTS,
  },
]

/**
 * Suppliers named in the coverage plan (or otherwise in scope) that this
 * structured-data runner cannot cover, and why. Checked against each
 * filer's own `data.sec.gov/submissions/CIK##########.json` on 2026-09-25.
 */
export const unsupported: UnsupportedSupplier[] = [
  {
    id: 'checkpoint',
    name: 'Check Point Software Technologies',
    ticker: 'CHKP',
    cik: '0001015922',
    reason:
      'Foreign private issuer — files an annual 20-F (most recent 2026-03-31) and furnishes ' +
      '6-Ks, never a 10-Q or 10-K. Its 20-F XBRL only carries annual-duration facts, so no ' +
      'discrete quarterly revenue exists in EDGAR structured data for it. Confirmed against its ' +
      'submissions record: no 10-Q or 10-K in its filing history.',
  },
  {
    id: 'trend-micro',
    name: 'Trend Micro Incorporated',
    ticker: '4704 (Tokyo Stock Exchange)',
    cik: '0001089463',
    reason:
      'Listed on the Tokyo Stock Exchange (4704). It was once an SEC foreign private issuer under ' +
      'this CIK, but its own Form 15F-12G terminated that registration, and its EDGAR record has ' +
      'no 10-Q, 10-K, 6-K, or 20-F since 2009 (confirmed against its submissions record on ' +
      '2026-09-30: the only filings are legacy 6-K/20-F/S-8/SC 13G items from 2000-2009, ending ' +
      'with the deregistration). It now reports quarterly and annual results under Japanese ' +
      'disclosure rules (kessan tanshin / yukashoken hokokusho) via the Tokyo Stock Exchange and ' +
      'its own newsroom, not SEC XBRL, so no discrete quarterly revenue exists in EDGAR structured ' +
      'data for it.',
  },
  {
    id: 'cisco-secops',
    name: 'Cisco (security)',
    ticker: 'CSCO',
    cik: '0000858877',
    reason:
      "Cisco's total revenue is not a security figure, and EDGAR's companyfacts API only " +
      'exposes entity-wide, non-dimensional facts — the security product-category split Cisco ' +
      "discloses (e.g. in its 10-K's segment footnote) is tagged with a member/axis dimension " +
      "that companyfacts strips out. Pulling it needs the filing's own XBRL viewer or the " +
      'frames API per member, not a plain revenue concept lookup, so it stays out of this ' +
      'structured runner. Fiscal year end 0725; most recent 10-K 2026-09-02.',
  },
  {
    id: 'akamai-security',
    name: 'Akamai (security segment)',
    ticker: 'AKAM',
    cik: '0001086222',
    reason:
      "Same limitation as Cisco: Akamai's security-line revenue is a disclosed segment, not a " +
      'top-level GAAP concept, and companyfacts does not expose dimensional (segment-member) ' +
      'facts. Total Akamai revenue is tracked but is not a security figure, so it is left out ' +
      'entirely rather than published mislabeled.',
  },
]
