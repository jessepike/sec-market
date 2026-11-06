/**
 * Pure parsing for quarterly results releases furnished on Form 6-K
 * (releaseRegistry.ts, backlog SEC-080). No network, no model.
 *
 * The parser accepts one exact shape and refuses anything else: the
 * consolidated statement of income headed "in millions", whose first header
 * row reads "Three Months Ended", followed by a month-and-day row and a year
 * row, and whose "Total revenues" row gives the current quarter first and the
 * same quarter a year earlier second. A refusal keeps the last good record.
 */

export interface ReleaseQuarter {
  periodEnd: string
  /** USD. */
  value: number
  /** USD, same quarter one year earlier, as printed in the same release. */
  priorYearValue: number
  scale: 'USD millions'
  form: '6-K'
  accessionNumber: string
  filedDate: string
  sourceUrl: string
  sha256: string
  checkedAt: string
}

export interface ReleaseRecord {
  id: string
  name: string
  cik: string
  quarters: ReleaseQuarter[]
  latest: ReleaseQuarter | null
  prior: ReleaseQuarter | null
}

export interface ParsedRelease { periodEnd: string; value: number; priorYearValue: number }

const MONTHS: Record<string, string> = { March: '03', June: '06', September: '09', December: '12' }
const DAYS: Record<string, string> = { '03': '31', '06': '30', '09': '30', '12': '31' }

const text = (fragment: string) => fragment.replace(/<[^>]+>/g, ' ')
  .replace(/&nbsp;|&#160;|&#xa0;/gi, ' ').replace(/&amp;/gi, '&').replace(/&#8217;|&rsquo;/gi, '’')
  .replace(/\s+/g, ' ').trim()

function rows(table: string): string[][] {
  return [...table.matchAll(/<tr\b[^>]*>([\s\S]*?)<\/tr>/gi)]
    .map(r => [...r[1].matchAll(/<t[dh]\b[^>]*>([\s\S]*?)<\/t[dh]>/gi)].map(c => text(c[1])).filter(c => c !== '' && c !== '$'))
}

const number = (cell: string) => {
  if (!/^\d{1,3}(,\d{3})*(\.\d)?$/.test(cell)) throw new Error(`Unexpected revenue cell "${cell}"`)
  return Math.round(Number(cell.replaceAll(',', '')) * 10) * 100_000
}

export function parseResultsRelease(html: string): ParsedRelease {
  const heading = /CONSOLIDATED STATEMENTS? OF INCOME/i.exec(html.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' '))
  if (!heading) throw new Error('No consolidated statement of income')
  const tables = [...html.matchAll(/<table\b[\s\S]*?<\/table>/gi)].map(m => ({ at: m.index ?? 0, body: m[0] }))
  const found = tables.find(t => rows(t.body).some(r => r[0] === 'Total revenues'))
  if (!found) throw new Error('No "Total revenues" row')
  // The scale must be stated in the lead-in to this same table.
  const before = text(html.slice(Math.max(0, found.at - 3000), found.at))
  const lead = before.slice(before.search(/CONSOLIDATED STATEMENTS? OF INCOME/i))
  if (!/CONSOLIDATED STATEMENTS? OF INCOME/i.test(lead) || !/in millions/i.test(lead)) throw new Error('Income statement scale is not "in millions"')
  const body = rows(found.body)
  const head = body.findIndex(r => r[0] === 'Three Months Ended')
  if (head < 0) throw new Error('First column is not "Three Months Ended"')
  const date = /^(March|June|September|December) (\d{1,2}),?$/.exec(body[head + 1]?.[0] ?? '')
  const years = (body[head + 2] ?? []).map(Number)
  if (!date || years.length < 2 || !years.every(Number.isInteger)) throw new Error('Unexpected period header')
  const month = MONTHS[date[1]]
  if (DAYS[month] !== date[2].padStart(2, '0')) throw new Error('Period end is not a calendar quarter end')
  if (years[1] !== years[0] - 1) throw new Error('Prior-year column is not the preceding year')
  const total = body.filter(r => r[0] === 'Total revenues')
  if (total.length !== 1 || total[0].length < 3) throw new Error('Ambiguous "Total revenues" row')
  const value = number(total[0][1]), priorYearValue = number(total[0][2])
  if (value <= 0 || priorYearValue <= 0) throw new Error('Non-positive revenue')
  return { periodEnd: `${years[0]}-${month}-${DAYS[month]}`, value, priorYearValue }
}

const previousQuarterEnd = (periodEnd: string) => {
  const [y, m] = periodEnd.split('-').map(Number)
  const pm = m === 3 ? 12 : m - 3, py = m === 3 ? y - 1 : y
  const mm = String(pm).padStart(2, '0')
  return `${py}-${mm}-${DAYS[mm]}`
}

/**
 * Merge freshly parsed quarters into the retained ones. The same quarter must
 * carry the same figure in every release that prints it, including as the
 * prior-year column a year later; any difference refuses the whole record.
 */
export function buildReleaseRecord(id: string, name: string, cik: string, retained: ReleaseQuarter[], fresh: ReleaseQuarter[]): ReleaseRecord {
  const byEnd = new Map<string, ReleaseQuarter>()
  for (const q of [...retained, ...fresh]) {
    const old = byEnd.get(q.periodEnd)
    if (old && (old.value !== q.value || old.priorYearValue !== q.priorYearValue)) throw new Error(`Conflicting figures for ${q.periodEnd}`)
    if (!old || q.filedDate > old.filedDate) byEnd.set(q.periodEnd, q)
  }
  const quarters = [...byEnd.values()].sort((a, b) => b.periodEnd.localeCompare(a.periodEnd))
  for (const q of quarters) {
    const yearAgo = `${Number(q.periodEnd.slice(0, 4)) - 1}${q.periodEnd.slice(4)}`
    const earlier = byEnd.get(yearAgo)
    if (earlier && earlier.value !== q.priorYearValue) throw new Error(`Prior-year figure for ${yearAgo} differs between releases`)
  }
  const latest = quarters[0] ?? null
  const prior = latest ? byEnd.get(previousQuarterEnd(latest.periodEnd)) ?? null : null
  return { id, name, cik, quarters, latest, prior }
}
