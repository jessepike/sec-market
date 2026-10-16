// Independent SEC verifier for the certified tier (SEC-MARKET-AUTO-002-P0).
//
// This module deliberately imports nothing from the code that produces the
// displayed values (edgarLogic.ts, edgarRevenue.ts, filing-events.ts). It
// re-derives each claim from the raw SEC response and compares it with the
// candidate value. A producer bug therefore cannot certify itself.
//
// Every function here is pure: it takes parsed SEC JSON plus the candidate
// value and returns { ok, reason, locator, excerpt }.

const DAY = 86400000
const days = (a, b) => Math.round((Date.parse(b + 'T00:00:00Z') - Date.parse(a + 'T00:00:00Z')) / DAY)
const isQuarter = f => f.start && days(f.start, f.end) >= 80 && days(f.start, f.end) <= 100
const isYear = f => f.start && days(f.start, f.end) >= 340 && days(f.start, f.end) <= 386
const FILING_FORMS = new Set(['10-Q', '10-K'])
const GROWTH_BAND = 0.8

export const dollars = n => `$${n.toLocaleString('en-US')}`
export const growthText = g => `${g >= 0 ? '+' : ''}${(g * 100).toFixed(1)}%`

/** USD 10-Q/10-K facts for one concept, or []. */
function conceptFacts(companyFacts, concept) {
  const usd = companyFacts?.facts?.['us-gaap']?.[concept]?.units?.USD ?? []
  return usd.filter(f => FILING_FORMS.has(f.form) && typeof f.val === 'number' && f.end)
}

/** Latest-filed fact per end date (restatements win). */
function latestFiled(facts) {
  const byEnd = new Map()
  for (const f of facts) {
    const cur = byEnd.get(f.end)
    if (!cur || f.filed > cur.filed || (f.filed === cur.filed && f.accn > cur.accn)) byEnd.set(f.end, f)
  }
  return byEnd
}

/** The concept whose newest quarter or fiscal year ends latest. Ties keep priority order. */
export function currentConcept(companyFacts, concepts) {
  let best = null
  for (const concept of concepts) {
    const facts = conceptFacts(companyFacts, concept).filter(f => isQuarter(f) || (f.form === '10-K' && isYear(f)))
    if (!facts.length) continue
    const newest = facts.reduce((m, f) => (f.end > m ? f.end : m), '')
    if (!best || newest > best.newest) best = { concept, newest }
  }
  return best
}

/** Revenue for the quarter ending `end`: a filed quarter, or a 10-K year less its three filed quarters. */
export function quarterRevenue(companyFacts, concept, end) {
  const facts = conceptFacts(companyFacts, concept)
  const quarters = latestFiled(facts.filter(isQuarter))
  const direct = quarters.get(end)
  if (direct) return { value: direct.val, filed: direct.filed, accn: direct.accn, start: direct.start, derived: false }
  const year = latestFiled(facts.filter(f => f.form === '10-K' && isYear(f))).get(end)
  if (!year) return null
  const q1 = [...quarters.values()].find(q => q.start === year.start)
  if (!q1) return null
  const q2 = [...quarters.values()].find(q => days(q1.end, q.start) >= 0 && days(q1.end, q.start) <= 1)
  if (!q2) return null
  const q3 = [...quarters.values()].find(q => days(q2.end, q.start) >= 0 && days(q2.end, q.start) <= 1)
  if (!q3 || days(q3.end, year.end) < 80) return null
  return { value: year.val - q1.val - q2.val - q3.val, filed: year.filed, accn: year.accn, start: null, derived: true }
}

/** Every period end in this concept that could be a quarter end (quarters and fiscal years). */
function quarterEnds(companyFacts, concept) {
  const facts = conceptFacts(companyFacts, concept)
  return [...new Set(facts.filter(f => isQuarter(f) || (f.form === '10-K' && isYear(f))).map(f => f.end))]
}

/**
 * Verifies one displayed revenue period. `candidate` is the RevenuePeriod shown
 * on the site (strings), plus releaseDate for the latest period.
 */
export function verifyRevenuePeriod(companyFacts, concepts, candidate, { requireReleaseDate }) {
  const fail = reason => ({ ok: false, reason })
  if (!candidate) return fail('no displayed revenue period')
  const chosen = currentConcept(companyFacts, concepts)
  if (!chosen) return fail('no usable revenue concept in SEC facts')
  const q = quarterRevenue(companyFacts, chosen.concept, candidate.periodEnd)
  if (!q) return fail(`no filed or derivable quarter ending ${candidate.periodEnd} under ${chosen.concept}`)
  if (candidate.value !== dollars(q.value)) return fail(`value ${candidate.value} does not equal SEC ${dollars(q.value)}`)
  const expectedPeriod = `Quarter ended ${candidate.periodEnd}${q.derived ? ' (derived from annual less preceding quarters)' : ''}`
  if (candidate.period !== expectedPeriod) return fail(`period text "${candidate.period}" does not match "${expectedPeriod}"`)
  if (requireReleaseDate && candidate.releaseDate !== q.filed) return fail(`releaseDate ${candidate.releaseDate} does not equal SEC filing date ${q.filed}`)
  const ends = quarterEnds(companyFacts, chosen.concept)
  const target = Date.parse(candidate.periodEnd + 'T00:00:00Z') - 365 * DAY
  const priorEnd = ends.filter(e => Math.abs(Date.parse(e + 'T00:00:00Z') - target) <= 10 * DAY)
    .sort((a, b) => Math.abs(Date.parse(a + 'T00:00:00Z') - target) - Math.abs(Date.parse(b + 'T00:00:00Z') - target))[0]
  const prior = priorEnd ? quarterRevenue(companyFacts, chosen.concept, priorEnd) : null
  if (prior) {
    if (candidate.priorYearValue !== dollars(prior.value)) return fail(`prior-year value ${candidate.priorYearValue} does not equal SEC ${dollars(prior.value)}`)
    const g = prior.value !== 0 ? (q.value - prior.value) / prior.value : null
    const clean = g !== null && Math.abs(g) <= GROWTH_BAND && (q.derived || isQuarter({ start: q.start, end: candidate.periodEnd }))
    if (clean && candidate.yoyGrowth !== growthText(g)) return fail(`growth ${candidate.yoyGrowth} does not equal recomputed ${growthText(g)}`)
    if (!clean && candidate.yoyGrowth !== '') return fail('growth shown where no clean comparison exists')
  } else if (candidate.priorYearValue !== undefined || candidate.yoyGrowth !== '') {
    return fail('prior-year value or growth shown with no matching prior-year quarter in SEC facts')
  }
  return { ok: true, concept: chosen.concept, accession: q.accn, filed: q.filed, derived: q.derived,
    locator: `${chosen.concept}; USD; quarter ended ${candidate.periodEnd}; accession ${q.accn}; filed ${q.filed}${q.derived ? '; 10-K year less three filed quarters' : ''}`,
    excerpt: `USD ${q.value.toLocaleString('en-US')}${prior ? `; prior-year quarter ended ${priorEnd} USD ${prior.value.toLocaleString('en-US')}` : ''}` }
}

/** The displayed prior quarter must be the quarter immediately before the displayed latest one. */
export function verifyPriorAdjacent(companyFacts, concepts, latestEnd, priorEnd) {
  const chosen = currentConcept(companyFacts, concepts)
  if (!chosen) return { ok: false, reason: 'no usable revenue concept in SEC facts' }
  const before = quarterEnds(companyFacts, chosen.concept).filter(e => e < latestEnd && days(e, latestEnd) >= 80).sort()
  const expected = before.filter(e => quarterRevenue(companyFacts, chosen.concept, e)).at(-1)
  if (expected !== priorEnd) return { ok: false, reason: `prior quarter ends ${priorEnd}; the quarter before ${latestEnd} in SEC facts ends ${expected ?? 'nowhere'}` }
  return { ok: true }
}

/** Every row of the displayed quarter table equals SEC (value, filing date, accession, derived flag). */
export function verifyHistory(companyFacts, concepts, rows) {
  const chosen = currentConcept(companyFacts, concepts)
  if (!chosen) return { ok: false, reason: 'no usable revenue concept in SEC facts' }
  if (!Array.isArray(rows) || !rows.length) return { ok: false, reason: 'no displayed quarter table' }
  for (const row of rows) {
    const q = quarterRevenue(companyFacts, chosen.concept, row.periodEnd)
    if (!q) return { ok: false, reason: `table row ${row.periodEnd} has no filed or derivable SEC quarter` }
    if (q.value !== row.value || q.filed !== row.filedDate || q.accn !== row.accessionNumber || q.derived !== row.derived)
      return { ok: false, reason: `table row ${row.periodEnd} (${row.value}, ${row.filedDate}, ${row.accessionNumber}) differs from SEC (${q.value}, ${q.filed}, ${q.accn})` }
  }
  return { ok: true, locator: `${chosen.concept}; USD; ${rows.length} quarters ending ${rows.at(-1).periodEnd} to ${rows[0].periodEnd}`, excerpt: rows.map(r => `${r.periodEnd} USD ${r.value.toLocaleString('en-US')}`).join('; ') }
}

/** No concept has a later quarter, and no 10-Q/10-K was filed after the displayed release date. */
export function verifyNotStale(companyFacts, submissions, concepts, latest) {
  for (const concept of concepts) {
    const newer = quarterEnds(companyFacts, concept).filter(e => e > latest.periodEnd)
    if (newer.length) return { ok: false, reason: `${concept} has a newer period ending ${newer.sort().at(-1)} than the displayed ${latest.periodEnd}` }
  }
  const r = submissions?.filings?.recent
  if (!r) return { ok: false, reason: 'submissions index unreadable' }
  const newestReport = r.form.map((f, i) => (FILING_FORMS.has(f) ? r.filingDate[i] : '')).reduce((m, d) => (d > m ? d : m), '')
  if (newestReport > latest.releaseDate) return { ok: false, reason: `a ${'10-Q/10-K'} was filed ${newestReport}, after the displayed release ${latest.releaseDate}` }
  return { ok: true }
}

const SUFFIXES = new Set(['inc', 'ltd', 'corp', 'corporation', 'holdings', 'co', 'plc', 'nv', 'sa', 'incorporated', 'limited'])
export const normalizeName = name => name.toLowerCase().replace(/[.,]/g, ' ').split(/\s+/).filter(t => t && !SUFFIXES.has(t)).join(' ')

export function verifyIdentity(submissions, candidate, now = Date.now()) {
  const fail = reason => ({ ok: false, reason })
  if (!submissions?.name) return fail('submissions index unreadable')
  if (normalizeName(submissions.name) !== normalizeName(candidate.name)) return fail(`name "${candidate.name}" does not match SEC "${submissions.name}"`)
  if (!(submissions.tickers ?? []).includes(candidate.ticker)) return fail(`ticker ${candidate.ticker} not among SEC tickers ${JSON.stringify(submissions.tickers)}`)
  if (candidate.kind !== 'public') return fail(`kind ${candidate.kind} is not public`)
  const r = submissions.filings.recent
  const cutoff = new Date(now - 400 * DAY).toISOString().slice(0, 10)
  const exit = r.form.findIndex((f, i) => /^(25|25-NSE|15-12B|15-12G|15-15D)$/.test(f) && r.filingDate[i] >= cutoff)
  if (exit >= 0) return fail(`Form ${r.form[exit]} filed ${r.filingDate[exit]}: no longer an independent public filer`)
  return { ok: true, locator: `CIK ${submissions.cik}; name; tickers; no Form 15 or 25 since ${cutoff}`, excerpt: `${submissions.name} (${(submissions.tickers ?? []).join(', ')})` }
}

/** Accession from an sec.gov Archives URL, e.g. .../data/1660280/000166028026000046/x.htm -> 0001660280-26-000046 */
export function accessionFromUrl(url) {
  const m = /sec\.gov\/Archives\/edgar\/data\/\d+\/(\d{18})\//.exec(url ?? '')
  if (!m) return null
  const d = m[1]
  return `${d.slice(0, 10)}-${d.slice(10, 12)}-${d.slice(12)}`
}

export const TRACKED_ITEMS = { '5.02': ['exec-change'], '2.01': ['acquisition', 'divestiture'], '1.03': ['going-concern', 'shutdown'], '2.05': ['restructuring', 'layoff'], '3.01': ['going-concern'], '2.03': ['debt'] }
export const TRACKED_FORMS = { '25': ['going-concern'], '25-NSE': ['going-concern'], DEFM14A: ['acquisition'], PREM14A: ['acquisition'] }
const CURRENT_REPORTS = new Set(['8-K', '8-K/A', '6-K'])
const PERIODIC = { '10-Q': 100, '10-Q/A': 100, '10-K': 380, '10-K/A': 380 }

/**
 * candidateEvents: [{ id, date, type, accessions: [..], evidenceDates: [..] }] for events with sec.gov sources.
 * allEvents: every tracker event for this supplier in the window (any source): [{ date, type, accessions }].
 *
 * Rules (SEC-MARKET-AUTO-002-P0 fix pass):
 * - every cited accession is in the filer's SEC index, and its evidence publication date equals the SEC filing date;
 * - no event is dated after a filing it cites;
 * - at least one cited filing anchors the date: for a current report (8-K) the event date equals the SEC
 *   report date (the event date the filer declared) or the filing date; for a 10-Q/10-K the event falls in
 *   the reporting period or between its end and the filing;
 * - every tracked 8-K item or form in the window is represented, per item, by an event that cites that
 *   accession or that falls on its report or filing date with a type that matches the item.
 */
export function verifySecEvents(submissions, candidateEvents, allEvents, windowStart, windowEnd, today) {
  const r = submissions?.filings?.recent
  if (!r) return { ok: false, reason: 'submissions index unreadable' }
  const filed = new Map(r.accessionNumber.map((a, i) => [a, { form: r.form[i], date: r.filingDate[i], report: r.reportDate?.[i] || r.filingDate[i], items: r.items[i] ?? '' }]))
  for (const event of candidateEvents) {
    if (!event.accessions.length) return { ok: false, reason: `${event.id}: sec.gov source with no readable accession` }
    let anchored = false
    for (const [k, a] of event.accessions.entries()) {
      const f = filed.get(a)
      if (!f) return { ok: false, reason: `${event.id}: accession ${a} is not in the SEC submissions index` }
      if (event.evidenceDates[k] !== f.date) return { ok: false, reason: `${event.id}: evidence for ${a} is dated ${event.evidenceDates[k]}; SEC filing date is ${f.date}` }
      if (event.date > f.date) return { ok: false, reason: `${event.id}: dated ${event.date}, after its source filing ${a} (${f.date})` }
      if (CURRENT_REPORTS.has(f.form) && (event.date === f.report || event.date === f.date)) anchored = true
      if (f.form in PERIODIC && days(event.date, f.report) <= PERIODIC[f.form]) anchored = true
    }
    if (!anchored) return { ok: false, reason: `${event.id}: date ${event.date} is not the report date or filing date of any cited filing, nor inside a cited report's period` }
  }
  for (let i = 0; i < r.form.length; i++) {
    const form = r.form[i], date = r.filingDate[i], report = r.reportDate?.[i] || date, accn = r.accessionNumber[i]
    const needs = form === '8-K' ? (r.items[i] ?? '').split(',').map(c => c.trim()).filter(c => c in TRACKED_ITEMS).map(c => [c, TRACKED_ITEMS[c]])
      : form in TRACKED_FORMS ? [[form, TRACKED_FORMS[form]]] : []
    if (!needs.length) continue
    if (date > windowEnd && date <= today) return { ok: false, reason: `${form} ${accn} filed ${date} after the event window end ${windowEnd}; events not yet collected` }
    if (date < windowStart || date > windowEnd) continue
    for (const [code, types] of needs) {
      const covered = allEvents.some(e => e.accessions.includes(accn) || ((e.date === date || e.date === report) && types.includes(e.type)))
      if (!covered) return { ok: false, reason: `${form} ${accn} item ${code} (report ${report}, filed ${date}) has no matching ${types.join('/')} event` }
    }
  }
  return { ok: true, locator: `SEC submissions index; 8-K items ${Object.keys(TRACKED_ITEMS).join(', ')}; forms ${Object.keys(TRACKED_FORMS).join(', ')}; ${windowStart} to ${windowEnd}`,
    excerpt: `${candidateEvents.length} SEC-sourced events matched to filings by accession, report date and filing date; every tracked item in the window represented by type` }
}
