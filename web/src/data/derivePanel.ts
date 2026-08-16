import {
  ALPHABET_CAPEX_BILLIONS,
  AMAZON_CAPEX_BILLIONS,
  BASE_QUARTER,
  CHECKPOINT_REVENUE_MILLIONS,
  CROWDSTRIKE_REVENUE_MILLIONS,
  FORTINET_REVENUE_MILLIONS,
  MICROSOFT_CAPEX_BILLIONS,
  NVIDIA_DATA_CENTER_BILLIONS,
  OKTA_REVENUE_MILLIONS,
  PANEL_QUARTERS,
  type PanelQuarter,
  ZSCALER_REVENUE_MILLIONS,
} from './panelRaw'

export interface CompanyIndexSeries {
  company: string
  baseQuarter: PanelQuarter
  values: Record<PanelQuarter, number | null>
}

export interface DerivedQuarterRow {
  quarter: PanelQuarter
  nvidiaIndex: number | null
  microsoftIndex: number | null
  amazonIndex: number | null
  alphabetIndex: number | null
  hyperscalerMedianIndex: number | null
  crowdstrikeIndex: number | null
  oktaIndex: number | null
  fortinetIndex: number | null
  zscalerIndex: number | null
  checkpointIndex: number | null
  securityMedianIndex: number | null
}

/** Index = 100 × (value / value at base quarter). No interpolation. */
export function indexSeries(
  raw: Record<PanelQuarter, number | null>,
  baseQuarter: PanelQuarter = BASE_QUARTER,
): Record<PanelQuarter, number | null> {
  const base = raw[baseQuarter]
  if (base === null || base === 0) {
    throw new Error(`Cannot index series: base quarter ${baseQuarter} is null or zero`)
  }
  const indexed = {} as Record<PanelQuarter, number | null>
  for (const quarter of PANEL_QUARTERS) {
    const value = raw[quarter]
    indexed[quarter] = value === null ? null : (100 * value) / base
  }
  return indexed
}

/** Median of available numeric values; returns null when none available. */
export function median(values: (number | null | undefined)[]): number | null {
  const nums = values.filter((v): v is number => v !== null && v !== undefined).sort((a, b) => a - b)
  if (nums.length === 0) return null
  const mid = Math.floor(nums.length / 2)
  if (nums.length % 2 === 1) return nums[mid]
  return (nums[mid - 1] + nums[mid]) / 2
}

const nvidiaIndexed = indexSeries(NVIDIA_DATA_CENTER_BILLIONS)
const microsoftIndexed = indexSeries(MICROSOFT_CAPEX_BILLIONS)
const amazonIndexed = indexSeries(AMAZON_CAPEX_BILLIONS)
const alphabetIndexed = indexSeries(ALPHABET_CAPEX_BILLIONS)
const crowdstrikeIndexed = indexSeries(CROWDSTRIKE_REVENUE_MILLIONS)
const oktaIndexed = indexSeries(OKTA_REVENUE_MILLIONS)
const fortinetIndexed = indexSeries(FORTINET_REVENUE_MILLIONS)
const zscalerIndexed = indexSeries(ZSCALER_REVENUE_MILLIONS)
const checkpointIndexed = indexSeries(CHECKPOINT_REVENUE_MILLIONS)

export const companyIndexSeries: CompanyIndexSeries[] = [
  { company: 'NVIDIA Data Center', baseQuarter: BASE_QUARTER, values: nvidiaIndexed },
  { company: 'Microsoft cash PP&E', baseQuarter: BASE_QUARTER, values: microsoftIndexed },
  { company: 'Amazon gross PP&E', baseQuarter: BASE_QUARTER, values: amazonIndexed },
  { company: 'Alphabet PP&E', baseQuarter: BASE_QUARTER, values: alphabetIndexed },
  { company: 'CrowdStrike revenue', baseQuarter: BASE_QUARTER, values: crowdstrikeIndexed },
  { company: 'Okta revenue', baseQuarter: BASE_QUARTER, values: oktaIndexed },
  { company: 'Fortinet revenue', baseQuarter: BASE_QUARTER, values: fortinetIndexed },
  { company: 'Zscaler revenue', baseQuarter: BASE_QUARTER, values: zscalerIndexed },
  { company: 'Check Point revenue', baseQuarter: BASE_QUARTER, values: checkpointIndexed },
]

export const derivedPanelRows: DerivedQuarterRow[] = PANEL_QUARTERS.map((quarter) => {
  const ms = microsoftIndexed[quarter]
  const amzn = amazonIndexed[quarter]
  const goog = alphabetIndexed[quarter]
  const crwd = crowdstrikeIndexed[quarter]
  const okta = oktaIndexed[quarter]
  const ftnt = fortinetIndexed[quarter]
  const zs = zscalerIndexed[quarter]
  const chkp = checkpointIndexed[quarter]

  return {
    quarter,
    nvidiaIndex: nvidiaIndexed[quarter],
    microsoftIndex: ms,
    amazonIndex: amzn,
    alphabetIndex: goog,
    hyperscalerMedianIndex: median([ms, amzn, goog]),
    crowdstrikeIndex: crwd,
    oktaIndex: okta,
    fortinetIndex: ftnt,
    zscalerIndex: zs,
    checkpointIndex: chkp,
    securityMedianIndex: median([crwd, okta, ftnt, zs, chkp]),
  }
})

/** Rounded values for chart display (full precision retained in derivation). */
export function roundIndex(value: number | null, decimals = 1): number | null {
  if (value === null) return null
  const factor = 10 ** decimals
  return Math.round(value * factor) / factor
}

export interface ChartLayerPoint {
  quarter: PanelQuarter
  infrastructure: number | null
  hyperscalerMedian: number | null
  securityMedian: number | null
}

export const chartLayerPoints: ChartLayerPoint[] = derivedPanelRows.map((row) => ({
  quarter: row.quarter,
  infrastructure: roundIndex(row.nvidiaIndex),
  hyperscalerMedian: roundIndex(row.hyperscalerMedianIndex),
  securityMedian: roundIndex(row.securityMedianIndex),
}))
