import { derivedPanelRows } from './derivePanel'

function round2(value: number | null): number | null {
  if (value === null) return null
  return Math.round(value * 100) / 100
}

function canonicalDerivedPayload(): string {
  const payload = derivedPanelRows.map((row) => ({
    quarter: row.quarter,
    nvidiaIndex: round2(row.nvidiaIndex),
    microsoftIndex: round2(row.microsoftIndex),
    amazonIndex: round2(row.amazonIndex),
    alphabetIndex: round2(row.alphabetIndex),
    hyperscalerMedianIndex: round2(row.hyperscalerMedianIndex),
    crowdstrikeIndex: round2(row.crowdstrikeIndex),
    oktaIndex: round2(row.oktaIndex),
    fortinetIndex: round2(row.fortinetIndex),
    zscalerIndex: round2(row.zscalerIndex),
    checkpointIndex: round2(row.checkpointIndex),
    securityMedianIndex: round2(row.securityMedianIndex),
  }))
  return JSON.stringify(payload)
}

/**
 * Frozen canonical derived panel JSON (SHA-256 cd7070458d4511b95f6ca433ad34cdb8488d44c67b6c8eb61a982fb760e0d1f2).
 * Regenerate with `npm run verify:panel -- --write` after intentional panelRaw.ts edits.
 */
export const EXPECTED_DERIVED_PANEL_JSON =
  '[{"quarter":"2023-Q1","nvidiaIndex":100,"microsoftIndex":100,"amazonIndex":100,"alphabetIndex":100,"hyperscalerMedianIndex":100,"crowdstrikeIndex":100,"oktaIndex":100,"fortinetIndex":100,"zscalerIndex":100,"checkpointIndex":100,"securityMedianIndex":100},{"quarter":"2023-Q2","nvidiaIndex":241.12,"microsoftIndex":135.25,"amazonIndex":80.65,"alphabetIndex":109.54,"hyperscalerMedianIndex":109.54,"crowdstrikeIndex":105.63,"oktaIndex":107.34,"fortinetIndex":102.42,"zscalerIndex":108.64,"checkpointIndex":104.06,"securityMedianIndex":105.63},{"quarter":"2023-Q3","nvidiaIndex":339.02,"microsoftIndex":150.08,"amazonIndex":87.83,"alphabetIndex":128.14,"hyperscalerMedianIndex":128.14,"crowdstrikeIndex":113.49,"oktaIndex":112.74,"fortinetIndex":105.73,"zscalerIndex":118.6,"checkpointIndex":105.3,"securityMedianIndex":112.74},{"quarter":"2023-Q4","nvidiaIndex":429.91,"microsoftIndex":147.35,"amazonIndex":102.67,"alphabetIndex":175.2,"hyperscalerMedianIndex":147.35,"crowdstrikeIndex":122.05,"oktaIndex":116.8,"fortinetIndex":112.1,"zscalerIndex":125.36,"checkpointIndex":117.31,"securityMedianIndex":117.31},{"quarter":"2024-Q1","nvidiaIndex":527.1,"microsoftIndex":165.66,"amazonIndex":105.07,"alphabetIndex":190.94,"hyperscalerMedianIndex":165.66,"crowdstrikeIndex":132.98,"oktaIndex":119.11,"fortinetIndex":107.21,"zscalerIndex":132.09,"checkpointIndex":105.83,"securityMedianIndex":119.11},{"quarter":"2024-Q2","nvidiaIndex":613.79,"microsoftIndex":209.83,"amazonIndex":124,"alphabetIndex":209.7,"hyperscalerMedianIndex":209.7,"crowdstrikeIndex":139.17,"oktaIndex":124.71,"fortinetIndex":113.63,"zscalerIndex":141.57,"checkpointIndex":110.85,"securityMedianIndex":124.71},{"quarter":"2024-Q3","nvidiaIndex":718.93,"microsoftIndex":225.72,"amazonIndex":159.18,"alphabetIndex":207.63,"hyperscalerMedianIndex":207.63,"crowdstrikeIndex":145.86,"oktaIndex":128.38,"fortinetIndex":119.47,"zscalerIndex":149.95,"checkpointIndex":112.21,"securityMedianIndex":128.38},{"quarter":"2024-Q4","nvidiaIndex":831.31,"microsoftIndex":239.03,"amazonIndex":195.85,"alphabetIndex":227.03,"hyperscalerMedianIndex":227.03,"crowdstrikeIndex":152.9,"oktaIndex":131.66,"fortinetIndex":131.51,"zscalerIndex":154.7,"checkpointIndex":124.38,"securityMedianIndex":131.66},{"quarter":"2025-Q1","nvidiaIndex":913.79,"microsoftIndex":253.4,"amazonIndex":176.07,"alphabetIndex":273.45,"hyperscalerMedianIndex":253.4,"crowdstrikeIndex":159.25,"oktaIndex":132.82,"fortinetIndex":121.98,"zscalerIndex":161.89,"checkpointIndex":112.72,"securityMedianIndex":132.82},{"quarter":"2025-Q2","nvidiaIndex":960.28,"microsoftIndex":258.4,"amazonIndex":226.46,"alphabetIndex":356.92,"hyperscalerMedianIndex":258.4,"crowdstrikeIndex":168.78,"oktaIndex":140.54,"fortinetIndex":129.13,"zscalerIndex":171.73,"checkpointIndex":117.49,"securityMedianIndex":140.54},{"quarter":"2025-Q3","nvidiaIndex":1196.73,"microsoftIndex":293.34,"amazonIndex":247.01,"alphabetIndex":380.76,"hyperscalerMedianIndex":293.34,"crowdstrikeIndex":178.17,"oktaIndex":143.24,"fortinetIndex":null,"zscalerIndex":null,"checkpointIndex":119.79,"securityMedianIndex":143.24},{"quarter":"2025-Q4","nvidiaIndex":1455.84,"microsoftIndex":452.04,"amazonIndex":278.11,"alphabetIndex":442.77,"hyperscalerMedianIndex":442.77,"crowdstrikeIndex":188.42,"oktaIndex":146.91,"fortinetIndex":150.91,"zscalerIndex":null,"checkpointIndex":131.63,"securityMedianIndex":148.91},{"quarter":"2026-Q1","nvidiaIndex":1758.18,"microsoftIndex":467.17,"amazonIndex":311.05,"alphabetIndex":567.09,"hyperscalerMedianIndex":467.17,"crowdstrikeIndex":200.12,"oktaIndex":147.68,"fortinetIndex":null,"zscalerIndex":203.08,"checkpointIndex":118.02,"securityMedianIndex":173.9}]'

export function assertPanelIntegrity(): void {
  const actual = canonicalDerivedPayload()
  if (actual !== EXPECTED_DERIVED_PANEL_JSON) {
    throw new Error(
      'Derived panel values drifted from frozen snapshot. Update panelRaw.ts and run npm run verify:panel -- --write if intentional.',
    )
  }
}

/** Used by scripts/verify-panel.ts */
export function exportCanonicalDerivedPayload(): string {
  return canonicalDerivedPayload()
}
