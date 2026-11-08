/**
 * Health figures for certified SEC filers: trailing-four-quarter operating and
 * free cash flow margins, and cash and debt at the latest balance sheet, all
 * anchored on the same revenue quarters the tracker shows (edgarFacts.json).
 *
 * Pure logic. `web/scripts/edgar-refresh.ts` runs it on the same companyfacts
 * responses it reads for revenue, so the daily refresh and the release gate
 * keep margins on the revenue quarter beside them. This is the TypeScript
 * form of `web/scripts/health/compute.py` (the 2026-11-06 snapshot), with
 * cash and debt added (improvement loop IL-002 and IL-003, 2026-11-08).
 */
import type { CompanyFacts, QuarterFact, XbrlFact } from './edgarLogic.ts'

export interface HealthFigure { value: number; periodEnd: string; form: string; sourceUrl: string }
/** debt is null when the filer tags no borrowing on that date (often a company without debt, but not proven). */
export interface BalanceFigure { cash: number; debt: number | null; asOf: string; form: string; sourceUrl: string }
export interface SupplierHealth { operatingMargin: HealthFigure | null; fcfMargin: HealthFigure | null; balance: BalanceFigure | null }
export interface HealthFile {
  generatedAt: string
  method: Record<string, string>
  suppliers: Record<string, SupplierHealth>
  gaps: Record<string, string[]>
  notes?: Record<string, string[]>
}

export const CASH = 'CashAndCashEquivalentsAtCarryingValue'
export const INVESTMENTS = ['ShortTermInvestments', 'MarketableSecuritiesCurrent', 'AvailableForSaleSecuritiesDebtSecuritiesCurrent', 'DebtSecuritiesAvailableForSaleExcludingAccruedInterestCurrent']
/** Debt in order of preference; each entry is one way a filer tags its total. */
export const DEBT_WAYS: { total?: string; parts?: string[] }[] = [
  { total: 'LongTermDebt' },
  { parts: ['LongTermDebtNoncurrent', 'LongTermDebtCurrent'] },
  { total: 'ConvertibleNotesPayable' },
  { parts: ['ConvertibleLongTermNotesPayable', 'ConvertibleNotesPayableCurrent'] },
  { parts: ['ConvertibleDebtNoncurrent', 'ConvertibleDebtCurrent'] },
  { total: 'DebtInstrumentCarryingAmount' },
  { total: 'SecuredLongTermDebt' },
]

export const healthMethod: Record<string, string> = {
  operatingMargin: 'OperatingIncomeLoss over revenue, trailing four quarters ending on the latest revenue quarter. Year-to-date facts are converted with the prior fiscal year: FY + YTD - prior YTD.',
  fcfMargin: 'NetCashProvidedByUsedInOperatingActivities minus PaymentsToAcquirePropertyPlantAndEquipment (PaymentsToAcquireProductiveAssets when PP&E is not tagged) minus capitalized software (PaymentsToDevelopSoftware or PaymentsForSoftware), over revenue, trailing four quarters.',
  balance: `Cash: ${CASH} plus the first of ${INVESTMENTS.join(', ')} that is tagged, on the latest revenue quarter end. Debt: carrying value from the first of LongTermDebt, LongTermDebtNoncurrent plus LongTermDebtCurrent, or the convertible notes tags that the filer uses on that date. When no borrowing tag is filed for that date, cash is shown and debt is marked as not tagged.`,
  revenue: 'The same four quarters of certified SEC revenue the tracker shows (edgarFacts.json).',
}

type Fact = XbrlFact
const FORMS = new Set(['10-Q', '10-K', '10-Q/A', '10-K/A'])
const day = (s: string) => Date.parse(`${s}T00:00:00Z`) / 86_400_000
const span = (f: Fact) => day(f.end) - day(f.start!)

function facts(cf: CompanyFacts, concept: string): Fact[] {
  const best = new Map<string, Fact>()
  for (const f of (cf.facts?.['us-gaap']?.[concept]?.units?.USD ?? []) as Fact[]) {
    if (!FORMS.has(f.form ?? '')) continue
    const k = `${f.start ?? ''}|${f.end}`
    const prev = best.get(k)
    if (!prev || f.filed > prev.filed) best.set(k, f)
  }
  return [...best.values()]
}

type Ttm = { value: number; used: Fact[] }
function ttmFrom(fs: Fact[], end: string): Ttm | null {
  const withStart = fs.filter(f => f.start)
  const at = withStart.filter(f => f.end === end)
  if (!at.length) return null
  const f = at.reduce((a, b) => (span(b) > span(a) ? b : a))
  const days = span(f)
  if (days > 350) return { value: f.val, used: [f] }
  const fy = withStart.filter(g => day(g.end) === day(f.start!) - 1 && span(g) > 350)
  const py = withStart.filter(g => Math.abs(day(g.end) - (day(f.end) - 365)) <= 7 && Math.abs(span(g) - days) <= 7)
  if (!fy.length || !py.length) return null
  return { value: fy[0].val + f.val - py[0].val, used: [f, fy[0], py[0]] }
}
const ttm = (cf: CompanyFacts, c: string, end: string) => ttmFrom(facts(cf, c), end)

/** As ttm, but when the prior fiscal year is tagged only under `alt`, use it if both concepts share an identical prior period (a tag rename). */
function ttmBridged(cf: CompanyFacts, c: string, alt: string, end: string): (Ttm & { bridged?: true }) | null {
  const direct = ttm(cf, c, end)
  if (direct) return direct
  const own = facts(cf, c).filter(f => f.start)
  const other = facts(cf, alt).filter(f => f.start)
  const key = (f: Fact) => `${f.start}|${f.end}`
  const ownVals = new Map(own.map(f => [key(f), f.val]))
  if (!other.some(f => ownVals.get(key(f)) === f.val)) return null
  const merged = [...own, ...other.filter(f => !ownVals.has(key(f)) && span(f) > 350)]
  const r = ttmFrom(merged, end)
  return r ? { ...r, bridged: true } : null
}

function instant(cf: CompanyFacts, c: string, end: string): Fact | null {
  const at = facts(cf, c).filter(f => f.end === end && !f.start)
  return at.length ? at.reduce((a, b) => (b.filed > a.filed ? b : a)) : null
}

const indexUrl = (cik: string, f: Fact) =>
  `https://www.sec.gov/Archives/edgar/data/${Number(cik)}/${f.accn.replace(/-/g, '')}/${f.accn}-index.htm`
const round1 = (n: number) => Math.round(n * 10) / 10

export function computeHealth(cik: string, quarters: QuarterFact[], cf: CompanyFacts): { health: SupplierHealth; gaps: string[]; notes: string[] } {
  const qs = quarters.slice().sort((a, b) => b.periodEnd.localeCompare(a.periodEnd)).slice(0, 4)
  const gaps: string[] = []
  const notes: string[] = []
  const health: SupplierHealth = { operatingMargin: null, fcfMargin: null, balance: null }
  if (!qs.length) return { health, gaps: ['four consecutive revenue quarters'], notes }
  const end = qs[0].periodEnd
  const consecutive = qs.length === 4 && [0, 1, 2].every(i => { const d = day(qs[i].periodEnd) - day(qs[i + 1].periodEnd); return d >= 80 && d <= 100 })
  const rev = consecutive ? qs.reduce((s, q) => s + q.value, 0) : null
  if (rev === null) gaps.push('four consecutive revenue quarters')

  const op = ttm(cf, 'OperatingIncomeLoss', end)
  const cfo = ttm(cf, 'NetCashProvidedByUsedInOperatingActivities', end)
  // PP&E capex first; a filer that tags capex only as PaymentsToAcquireProductiveAssets falls back to it.
  const cap = ttmBridged(cf, 'PaymentsToAcquirePropertyPlantAndEquipment', 'PaymentsToAcquireProductiveAssets', end)
    ?? ttm(cf, 'PaymentsToAcquireProductiveAssets', end)
  if (cap && 'bridged' in cap && cap.bridged) notes.push('prior fiscal year capital expenditure tagged as PaymentsToAcquireProductiveAssets; matched on a shared period')
  const sw = ttm(cf, 'PaymentsToDevelopSoftware', end) ?? ttm(cf, 'PaymentsForSoftware', end)

  if (op && rev) health.operatingMargin = { value: round1(op.value / rev * 100), periodEnd: end, form: op.used[0].form!, sourceUrl: indexUrl(cik, op.used[0]) }
  else gaps.push('operating income, trailing four quarters')
  if (cfo && cap && rev) {
    const fcf = cfo.value - cap.value - (sw?.value ?? 0)
    health.fcfMargin = { value: round1(fcf / rev * 100), periodEnd: end, form: cfo.used[0].form!, sourceUrl: indexUrl(cik, cfo.used[0]) }
  } else gaps.push('operating cash flow or capital expenditure, trailing four quarters')

  const cash = instant(cf, CASH, end)
  const inv = INVESTMENTS.map(c => instant(cf, c, end)).find(Boolean) ?? null
  let debt: number | null = null
  for (const way of DEBT_WAYS) {
    if (way.total) { const f = instant(cf, way.total, end); if (f) { debt = f.val; break } }
    else {
      const parts = way.parts!.map(c => instant(cf, c, end))
      if (parts.some(Boolean)) { debt = parts.reduce((s, f) => s + (f?.val ?? 0), 0); break }
    }
  }
  if (cash) health.balance = { cash: cash.val + (inv?.val ?? 0), debt, asOf: end, form: cash.form!, sourceUrl: indexUrl(cik, cash) }
  else gaps.push('cash at the latest quarter end')
  if (cash && debt === null) notes.push('no borrowing tagged at the latest quarter end')
  return { health, gaps, notes }
}
