/**
 * Frozen sparse-panel raw values from SEC-MARKET-SIG-PANEL-002.
 * USD billions unless noted. Security vendor series are USD millions.
 * `null` means unavailable — never zero.
 */

export const PANEL_QUARTERS = [
  '2023-Q1',
  '2023-Q2',
  '2023-Q3',
  '2023-Q4',
  '2024-Q1',
  '2024-Q2',
  '2024-Q3',
  '2024-Q4',
  '2025-Q1',
  '2025-Q2',
  '2025-Q3',
  '2025-Q4',
  '2026-Q1',
] as const

export type PanelQuarter = (typeof PANEL_QUARTERS)[number]

export const BASE_QUARTER: PanelQuarter = '2023-Q1'

/** NVIDIA Data Center revenue — USD billions */
export const NVIDIA_DATA_CENTER_BILLIONS: Record<PanelQuarter, number | null> = {
  '2023-Q1': 4.28,
  '2023-Q2': 10.32,
  '2023-Q3': 14.51,
  '2023-Q4': 18.4,
  '2024-Q1': 22.56,
  '2024-Q2': 26.27,
  '2024-Q3': 30.77,
  '2024-Q4': 35.58,
  '2025-Q1': 39.11,
  '2025-Q2': 41.1,
  '2025-Q3': 51.22,
  '2025-Q4': 62.31,
  '2026-Q1': 75.25,
}

/** Microsoft cash additions to PP&E — USD billions */
export const MICROSOFT_CAPEX_BILLIONS: Record<PanelQuarter, number | null> = {
  '2023-Q1': 6.61,
  '2023-Q2': 8.94,
  '2023-Q3': 9.92,
  '2023-Q4': 9.74,
  '2024-Q1': 10.95,
  '2024-Q2': 13.87,
  '2024-Q3': 14.92,
  '2024-Q4': 15.8,
  '2025-Q1': 16.75,
  '2025-Q2': 17.08,
  '2025-Q3': 19.39,
  '2025-Q4': 29.88,
  '2026-Q1': 30.88,
}

/** Amazon gross purchases of PP&E — USD billions */
export const AMAZON_CAPEX_BILLIONS: Record<PanelQuarter, number | null> = {
  '2023-Q1': 14.21,
  '2023-Q2': 11.46,
  '2023-Q3': 12.48,
  '2023-Q4': 14.59,
  '2024-Q1': 14.93,
  '2024-Q2': 17.62,
  '2024-Q3': 22.62,
  '2024-Q4': 27.83,
  '2025-Q1': 25.02,
  '2025-Q2': 32.18,
  '2025-Q3': 35.1,
  '2025-Q4': 39.52,
  '2026-Q1': 44.2,
}

/** Alphabet purchases of PP&E — USD billions */
export const ALPHABET_CAPEX_BILLIONS: Record<PanelQuarter, number | null> = {
  '2023-Q1': 6.29,
  '2023-Q2': 6.89,
  '2023-Q3': 8.06,
  '2023-Q4': 11.02,
  '2024-Q1': 12.01,
  '2024-Q2': 13.19,
  '2024-Q3': 13.06,
  '2024-Q4': 14.28,
  '2025-Q1': 17.2,
  '2025-Q2': 22.45,
  '2025-Q3': 23.95,
  '2025-Q4': 27.85,
  '2026-Q1': 35.67,
}

/** Cybersecurity GAAP revenue — USD millions */
export const CROWDSTRIKE_REVENUE_MILLIONS: Record<PanelQuarter, number | null> = {
  '2023-Q1': 692.6,
  '2023-Q2': 731.6,
  '2023-Q3': 786.0,
  '2023-Q4': 845.3,
  '2024-Q1': 921.0,
  '2024-Q2': 963.9,
  '2024-Q3': 1010.2,
  '2024-Q4': 1059,
  '2025-Q1': 1103,
  '2025-Q2': 1169,
  '2025-Q3': 1234,
  '2025-Q4': 1305,
  '2026-Q1': 1386,
}

export const OKTA_REVENUE_MILLIONS: Record<PanelQuarter, number | null> = {
  '2023-Q1': 518,
  '2023-Q2': 556,
  '2023-Q3': 584,
  '2023-Q4': 605,
  '2024-Q1': 617,
  '2024-Q2': 646,
  '2024-Q3': 665,
  '2024-Q4': 682,
  '2025-Q1': 688,
  '2025-Q2': 728,
  '2025-Q3': 742,
  '2025-Q4': 761,
  '2026-Q1': 765,
}

export const FORTINET_REVENUE_MILLIONS: Record<PanelQuarter, number | null> = {
  '2023-Q1': 1262.3,
  '2023-Q2': 1292.8,
  '2023-Q3': 1334.6,
  '2023-Q4': 1415.1,
  '2024-Q1': 1353.3,
  '2024-Q2': 1434.3,
  '2024-Q3': 1508.1,
  '2024-Q4': 1660.1,
  '2025-Q1': 1539.7,
  '2025-Q2': 1630.0,
  '2025-Q3': null,
  '2025-Q4': 1905.0,
  '2026-Q1': null,
}

export const ZSCALER_REVENUE_MILLIONS: Record<PanelQuarter, number | null> = {
  '2023-Q1': 418.8,
  '2023-Q2': 455.0,
  '2023-Q3': 496.7,
  '2023-Q4': 525.0,
  '2024-Q1': 553.2,
  '2024-Q2': 592.9,
  '2024-Q3': 628.0,
  '2024-Q4': 647.9,
  '2025-Q1': 678.0,
  '2025-Q2': 719.2,
  '2025-Q3': null,
  '2025-Q4': null,
  '2026-Q1': 850.5,
}

export const CHECKPOINT_REVENUE_MILLIONS: Record<PanelQuarter, number | null> = {
  '2023-Q1': 566,
  '2023-Q2': 589,
  '2023-Q3': 596,
  '2023-Q4': 664,
  '2024-Q1': 599,
  '2024-Q2': 627.4,
  '2024-Q3': 635.1,
  '2024-Q4': 704,
  '2025-Q1': 638,
  '2025-Q2': 665,
  '2025-Q3': 678,
  '2025-Q4': 745,
  '2026-Q1': 668,
}

/** IANS average annual security-budget growth (%) — annual, not quarterly */
export const BUYER_BUDGET_GROWTH_ANNUAL: Record<number, number | null> = {
  2023: 6,
  2024: 8,
  2025: 4,
  2026: null,
}

/** IANS security share of IT (%) — annual */
export const BUYER_SECURITY_SHARE_IT: Record<number, number | null> = {
  2023: 11.6,
  2024: 11.9,
  2025: 10.9,
  2026: null,
}
