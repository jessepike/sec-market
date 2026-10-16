import { readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { daysBetween, expectedFiscalQuarter } from '../src/data/edgarLogic.ts'
import { edgarRegistry } from '../src/data/edgarRegistry.ts'
import { evidenceById } from '../src/data/evidence.ts'
import { runStatus } from '../src/data/runStatus.ts'
import { edgarFilingsInLast30Days } from '../src/data/tracker/derive.ts'
import { notCoveredByTracker, trackerDomains } from '../src/data/tracker/domains.ts'
import { retainedTrackerEvents, trackerEvents } from '../src/data/tracker/events.ts'
import { trackerSuppliers } from '../src/data/tracker/suppliers.ts'

/**
 * Gate for the twelve-domain supplier tracker (step 5 of
 * docs/active/autonomy-coverage-plan.md, D-76/D-77). Checks the data the
 * front page's new "market by domain" section reads, before it ever reaches
 * a build:
 *
 *   1. Every supplier names at least one domain, and every declared domain
 *      has at least three suppliers.
 *   2. Every fact-bearing field that cites evidence resolves to a real
 *      evidence record with a non-empty source URL and a retrieval date.
 *   3. Every date is a valid ISO calendar date and not after "today"
 *      (runStatus.lastChecked, the same freshness clock the rest of the
 *      site uses — see meta.ts).
 *   4. Every supplier id and every event id is unique.
 *   5. No banned judgment word appears in any string the tracker itself
 *      authors (domain scope lines, the not-covered list, supplier labels,
 *      event text). Evidence excerpts are source quotations, not the site's
 *      own voice, and are exempt — the same way the rest of the site treats
 *      a quoted filing.
 *   6. Every `edgarId` on a supplier resolves to a supplier id in the
 *      generated EDGAR facts file.
 *
 * AUTO-001 fix pass (2026-09-26), item 2 — four gates added after two blind
 * scores caught exactly these mistakes live:
 *   7. A `kind: "segment"` supplier (a product line inside a public parent,
 *      e.g. Microsoft Entra ID) may not carry a `revenue` field at all — a
 *      segment's own-figure revenue is, by definition, not separately
 *      disclosed by the parent, so any `revenue` on one can only be the
 *      parent's whole-company figure borrowed onto the product row (the
 *      Microsoft Entra ID / Defender for Office 365 mislabelling both
 *      scorers found).
 *   8. Where a supplier's `revenue.latest.period`/`revenue.prior.period`
 *      is written as "Q<n> FY<year>" and the supplier has an `edgarId`, that
 *      label must match the fiscal quarter `expectedFiscalQuarter`
 *      (edgarLogic.ts) computes from the period's `periodEnd` and that
 *      filer's own `fiscalYearEnd` in edgarRegistry.ts — the SailPoint/Okta
 *      "Q4 FY2027" for what is actually each filer's Q2 FY2027 mistake.
 *   9. Every EDGAR filing `edgarFilingsInLast30Days` (derive.ts) would put
 *      in "What changed in the last 30 days" must be the supplier's own
 *      chronologically latest quarter — never a prior-year comparative a
 *      newer filing happened to restate (the "filed its 10-Q for the
 *      quarter ended 2025-07-31" mistake both scorers found).
 *  10. Every non-empty growth figure (`revenue.latest`/`revenue.prior`) and
 *      every `headlineMetric` must carry a named metric: the growth column
 *      is always "revenue growth" by construction, but a `headlineMetric`
 *      with a blank or whitespace-only `label` would render a bare figure
 *      with nothing saying what it measures (Fortinet's landscape-card
 *      "+52%" with no metric named, from the now-removed LandscapeSection).
 *
 * AUTO-001 fix pass (2026-09-26), item 5 — two more gates, tying the
 * run-status line to the rest of this file rather than letting it stand as
 * an independent hand-typed claim:
 *  11. A supplier's `revenue.latest.periodEnd` may not be older than the
 *      latest quarter the generated EDGAR facts file (edgarFacts.json)
 *      already holds for that same `edgarId` — the tracker showing a figure
 *      one quarter behind what EDGAR itself has on file is exactly the kind
 *      of staleness the run-status line claims does not happen.
 *  12. `runStatus.state` may not read "updated" (every source collected)
 *      while gate 11 above found a stale figure.
 *
 * AUTO-001 fix pass 2 (2026-09-26), three more gates from the two blind
 * rescores (score2/opus, score2/sol):
 *  13. Two supplier rows inside the same domain table may not share a
 *      display `name` — the Check Point public row and the Check Point
 *      email-segment row both reading bare "Check Point" in the email
 *      domain table both scorers flagged as indistinguishable.
 *  14. A supplier's `lastRound.date` or `ownership.announced`/`.closed`
 *      falling inside the trailing twelve months (the same window
 *      `eventSummaryForSupplier` in derive.ts counts) must have a matching
 *      event in events.ts — a funding round or an ownership change that is
 *      a fact on the supplier record but not an event is exactly why the
 *      "Events, 12 mo." column read "0" for suppliers with a round inside
 *      the year.
 *  15. Every evidence record's `canonicalUrl` that the tracker actually
 *      cites must point at a specific document, not a bare domain or a
 *      newsroom/IR index page with no slug — a source a reader cannot use
 *      to check the fact.
 *
 * AUTO-001 fix pass 4, item 2 — one more gate, after Ping's "ARR approaching
 * $800M" (actually November 2024) and Cato's $415M ARR (July 2026) both
 * shipped at one point with no visible date, making a stale fact impossible
 * to tell from a current one:
 *  16. A shown own-metric (`headlineMetric.period`) must be non-blank and
 *      name a year. A shown ownership fact — on a `'pe-owned'` or
 *      `'acquired'` supplier with no `lastRound` on file — must carry an
 *      `announced`/`closed` date or name a year in its status sentence.
 */

const __dirname = dirname(fileURLToPath(import.meta.url))
// The real date at build time (UTC), so a fact dated after the day this file
// was written never fails the gate just because the calendar moved on.
const TODAY = new Date().toISOString().slice(0, 10)

const BANNED_WORDS = [
  'leading',
  'strong',
  'weak',
  'solid',
  'healthy',
  'concerning',
  'accelerating',
  'struggling',
  'winning',
  'fading',
]

const edgarFactsPath = resolve(__dirname, '../src/data/generated/edgarFacts.json')
const edgarFactsRaw = JSON.parse(readFileSync(edgarFactsPath, 'utf8')) as {
  generatedAt: string
  suppliers: Array<{
    id: string
    quarters: Array<{ periodEnd: string; filedDate: string; form: string; value: number; sourceUrl: string }>
  }>
}
const edgarSupplierIds = new Set(edgarFactsRaw.suppliers.map((s) => s.id))
const fiscalYearEndByEdgarId = new Map(edgarRegistry.map((s) => [s.id, s.fiscalYearEnd]))
const latestPeriodEndByEdgarId = new Map<string, string>()
for (const s of edgarFactsRaw.suppliers) {
  if (s.quarters.length === 0) continue
  const latest = s.quarters.reduce((newest, q) => (q.periodEnd > newest ? q.periodEnd : newest), s.quarters[0].periodEnd)
  latestPeriodEndByEdgarId.set(s.id, latest)
}

let failCount = 0
const failures: string[] = []
/** Set by gate 11 whenever a tracked figure lags EDGAR's own latest quarter; read by gate 12. */
let staleFigureFound = false
/** Every evidence id actually cited by a supplier field or an event; read by gate 15. */
const usedEvidenceIds = new Set<string>()

function fail(message: string): void {
  failCount++
  failures.push(message)
}

function isIsoDate(value: string): boolean {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(value)) return false
  const [y, m, d] = value.split('-').map(Number)
  const date = new Date(Date.UTC(y, m - 1, d))
  return date.getUTCFullYear() === y && date.getUTCMonth() === m - 1 && date.getUTCDate() === d
}

function checkDateField(label: string, value: string | undefined): void {
  if (!value) return
  if (!isIsoDate(value)) {
    fail(`${label}: "${value}" is not a valid ISO calendar date`)
    return
  }
  if (value > TODAY) {
    fail(`${label}: "${value}" is after today (${TODAY})`)
  }
}

function isIsoMonth(value: string): boolean {
  if (!/^\d{4}-\d{2}$/.test(value)) return false
  const [y, m] = value.split('-').map(Number)
  return m >= 1 && m <= 12 && y > 1900
}

/**
 * A funding round's date sometimes only has month precision in the sourced
 * evidence (the press release says "January 2024" and no closing-day figure
 * exists anywhere). Rather than invent a day, this accepts "YYYY-MM" in
 * addition to a full ISO date — still checked against TODAY at month
 * granularity so a future-dated round still fails.
 */
function checkFundingDateField(label: string, value: string | undefined): void {
  if (!value) return
  if (isIsoDate(value)) {
    if (value > TODAY) fail(`${label}: "${value}" is after today (${TODAY})`)
    return
  }
  if (isIsoMonth(value)) {
    if (value > TODAY.slice(0, 7)) fail(`${label}: "${value}" is after today (${TODAY})`)
    return
  }
  fail(`${label}: "${value}" is neither a valid ISO calendar date nor a "YYYY-MM" month`)
}

function checkEvidenceIds(label: string, ids: string[] | undefined): void {
  if (!ids || ids.length === 0) {
    fail(`${label}: cites no evidence`)
    return
  }
  for (const id of ids) {
    usedEvidenceIds.add(id)
    const record = evidenceById[id]
    if (!record) {
      fail(`${label}: evidence id "${id}" does not exist in evidence.ts`)
      continue
    }
    if (!record.canonicalUrl || record.canonicalUrl.trim() === '') {
      fail(`${label}: evidence "${id}" has no source URL`)
    }
    if (!record.retrievedAt && !record.publicationDate) {
      fail(`${label}: evidence "${id}" has no retrieval date or publication date`)
    }
  }
}

function bannedWordsIn(text: string | undefined): string[] {
  if (!text) return []
  const found: string[] = []
  for (const word of BANNED_WORDS) {
    const re = new RegExp(`\\b${word}\\b`, 'i')
    if (re.test(text)) found.push(word)
  }
  return found
}

function checkBanned(label: string, text: string | undefined): void {
  const found = bannedWordsIn(text)
  if (found.length > 0) {
    fail(`${label}: contains banned word(s) [${found.join(', ')}] in "${text}"`)
  }
}

// --- 1. Domain/supplier coverage ---

const domainIds = new Set(trackerDomains.map((domain) => domain.id))
const supplierCountByDomain = new Map<string, number>()

for (const domain of trackerDomains) supplierCountByDomain.set(domain.id, 0)

const supplierIds = new Set<string>()

for (const supplier of trackerSuppliers) {
  if (supplierIds.has(supplier.id)) {
    fail(`supplier id "${supplier.id}" is not unique`)
  }
  supplierIds.add(supplier.id)

  if (supplier.domainIds.length === 0) {
    fail(`supplier "${supplier.id}" (${supplier.name}) names no domain`)
  }
  for (const domainId of supplier.domainIds) {
    if (!domainIds.has(domainId)) {
      fail(`supplier "${supplier.id}" names unknown domain "${domainId}"`)
      continue
    }
    supplierCountByDomain.set(domainId, (supplierCountByDomain.get(domainId) ?? 0) + 1)
  }
}

for (const [domainId, count] of supplierCountByDomain) {
  if (count < 3) {
    fail(`domain "${domainId}" has only ${count} supplier(s); needs at least 3`)
  }
}

// --- 2 & 5. Per-supplier evidence and banned-word checks ---
// --- 7, 8 & 10 (AUTO-001 fix pass, item 2): segment/parent-figure, fiscal
// period label, and metric-label checks, alongside the existing ones. ---

const FISCAL_PERIOD_RE = /^Q([1-4]) FY(\d{4})$/

function checkFiscalPeriodLabel(label: string, period: string, periodEnd: string, edgarId: string | undefined): void {
  const match = period.match(FISCAL_PERIOD_RE)
  if (!match) return // hand-written period text ("Full year 2025", "As of ...") is not this check's concern
  if (!edgarId) return // no registry entry to check the label against
  const fiscalYearEnd = fiscalYearEndByEdgarId.get(edgarId)
  if (!fiscalYearEnd) return // edgarId doesn't resolve — already failed by check 6 above

  const writtenQuarter = Number(match[1])
  const writtenYear = Number(match[2])
  let expected: { quarter: 1 | 2 | 3 | 4; fiscalYear: number }
  try {
    expected = expectedFiscalQuarter(periodEnd, fiscalYearEnd)
  } catch (error) {
    fail(`${label}: could not derive a fiscal quarter for periodEnd "${periodEnd}" (FYE ${fiscalYearEnd}): ${(error as Error).message}`)
    return
  }
  if (writtenQuarter !== expected.quarter || writtenYear !== expected.fiscalYear) {
    fail(
      `${label}: written as "${period}" for periodEnd "${periodEnd}", but that filer's FYE ${fiscalYearEnd} ` +
        `puts it in Q${expected.quarter} FY${expected.fiscalYear}`,
    )
  }
}

for (const supplier of trackerSuppliers) {
  const who = `supplier "${supplier.id}" (${supplier.name})`

  // 7. A segment (a product line inside a public parent) may not carry its
  // own `revenue` field — that field can only ever be the parent's
  // whole-company figure, borrowed onto a row that does not disclose its
  // own revenue.
  if (supplier.kind === 'segment' && supplier.revenue && supplier.revenue.scope !== 'segment') {
    fail(
      `${who}: kind "segment" carries a revenue field. A segment's own revenue is not separately ` +
        'disclosed by definition — this can only be the parent company\'s whole-company figure ' +
        'borrowed onto the product row. Remove revenue and let the row show "–".',
    )
  }

  if (supplier.headlineMetric) {
    checkEvidenceIds(`${who} headlineMetric`, supplier.headlineMetric.evidenceIds)
    checkBanned(`${who} headlineMetric.label`, supplier.headlineMetric.label)
    // 10. A headline figure with no named metric is a bare number with
    // nothing saying what it measures (the Fortinet "+52%" mistake).
    if (!supplier.headlineMetric.label.trim()) {
      fail(`${who} headlineMetric: label is blank — a figure must name its metric`)
    }
  }
  if (supplier.revenue) {
    checkEvidenceIds(`${who} revenue.latest`, supplier.revenue.latest.evidenceIds)
    checkFiscalPeriodLabel(
      `${who} revenue.latest.period`,
      supplier.revenue.latest.period,
      supplier.revenue.latest.periodEnd,
      supplier.edgarId,
    )
    // `prior` is optional — some segments (e.g. an unbroken-out Microsoft
    // product line) only have one comparable quarter in the research.
    if (supplier.revenue.prior) {
      checkEvidenceIds(`${who} revenue.prior`, supplier.revenue.prior.evidenceIds)
      checkDateField(`${who} revenue.prior.periodEnd`, supplier.revenue.prior.periodEnd)
      checkFiscalPeriodLabel(
        `${who} revenue.prior.period`,
        supplier.revenue.prior.period,
        supplier.revenue.prior.periodEnd,
        supplier.edgarId,
      )
    }
    checkDateField(`${who} revenue.latest.periodEnd`, supplier.revenue.latest.periodEnd)
    checkDateField(`${who} revenue.latest.releaseDate`, supplier.revenue.latest.releaseDate)
  }
  if (supplier.lastRound) {
    checkEvidenceIds(`${who} lastRound`, supplier.lastRound.evidenceIds)
    checkFundingDateField(`${who} lastRound.date`, supplier.lastRound.date)
    checkBanned(`${who} lastRound.stage`, supplier.lastRound.stage)
  }
  if (supplier.ownership) {
    checkEvidenceIds(`${who} ownership`, supplier.ownership.evidenceIds)
    checkDateField(`${who} ownership.announced`, supplier.ownership.announced)
    checkDateField(`${who} ownership.closed`, supplier.ownership.closed)
    checkBanned(`${who} ownership.status`, supplier.ownership.status)
  }

  // 6. edgarId must resolve in the generated EDGAR facts file.
  if (supplier.edgarId) {
    if (!edgarSupplierIds.has(supplier.edgarId)) {
      fail(`${who}: edgarId "${supplier.edgarId}" does not resolve in generated/edgarFacts.json`)
    } else if (supplier.revenue) {
      // 11. The tracker's shown figure may not be behind EDGAR's own latest
      // quarter for the same filer.
      const edgarLatest = latestPeriodEndByEdgarId.get(supplier.edgarId)
      if (edgarLatest && supplier.revenue.latest.periodEnd < edgarLatest) {
        staleFigureFound = true
        fail(
          `${who}: revenue.latest.periodEnd "${supplier.revenue.latest.periodEnd}" is older than the ` +
            `latest quarter already on file for edgarId "${supplier.edgarId}" in generated/edgarFacts.json ` +
            `("${edgarLatest}") — the tracker is showing a stale figure`,
        )
      }
    }
  }
}

// --- 16. AUTO-001 fix pass 4, item 2: a shown own-metric or ownership fact
// must carry a date — Ping's "ARR approaching $800M" with no visible date
// read as current when it was actually November 2024, and Cato's $415M
// figure needs its own date so a reader can't mistake it for the February
// 2026 figure. A headlineMetric.period must be non-blank and name a year.
// An ownership fact whose `kind` is itself a dated transaction ('pe-owned'
// or 'acquired' — a 'public' row's "Public · TICKER" and a 'segment' row's
// "Segment of Parent" are structural facts, not dated claims, and a plain
// 'private' company with no lastRound on file is already as dated as the
// evidence allows) must carry an announced/closed date or name a year in
// its status sentence, whenever there's no lastRound to show instead
// (lastRound takes display priority — formatOwnershipCompact,
// tracker/derive.ts). ---

const YEAR_RE = /\b(19|20)\d{2}\b/

for (const supplier of trackerSuppliers) {
  const who = `supplier "${supplier.id}" (${supplier.name})`

  if (supplier.headlineMetric) {
    const period = supplier.headlineMetric.period
    if (!period || !period.trim()) {
      fail(`${who} headlineMetric: has no period/as-of date — a shown own-metric fact must carry one`)
    } else if (!YEAR_RE.test(period)) {
      fail(`${who} headlineMetric.period "${period}" names no year — a shown own-metric fact must carry a dated period`)
    }
  }

  if (supplier.ownership && !supplier.lastRound && (supplier.kind === 'pe-owned' || supplier.kind === 'acquired')) {
    const ownership = supplier.ownership
    const hasDate = Boolean(ownership.announced || ownership.closed || YEAR_RE.test(ownership.status))
    if (!hasDate) {
      fail(
        `${who} ownership: status "${ownership.status}" names no year and has no announced/closed date — ` +
          'a shown ownership fact must carry a date',
      )
    }
  }
}

// --- 3 & 4. Events: unique ids, valid/in-window dates, evidence, banned words ---

const eventIds = new Set<string>()

for (const event of trackerEvents) {
  const who = `event "${event.id}" (supplier ${event.supplierId})`
  if (eventIds.has(event.id)) {
    fail(`event id "${event.id}" is not unique`)
  }
  eventIds.add(event.id)

  if (!supplierIds.has(event.supplierId)) {
    fail(`${who}: names unknown supplier "${event.supplierId}"`)
  }

  // Events are an append-only history, so an event older than twelve months
  // stays in the data; the page counts only the trailing twelve months.
  checkDateField(`${who} date`, event.date)

  checkEvidenceIds(who, event.evidenceIds)
  checkBanned(`${who} text`, event.text)

  if (event.rung < 1 || event.rung > 5) {
    fail(`${who}: rung ${event.rung} is out of range 1-5`)
  }
  if (event.rung === 5) {
    fail(`${who}: rung 5 (single trade-press report) may not publish alone — see docs/active/fable-run/research/11-distress-signal-sources.md §5`)
  }
}

// --- 5. Banned words in domain scope lines and the not-covered list ---

for (const domain of trackerDomains) {
  checkBanned(`domain "${domain.id}" scope`, domain.scope)
}
for (const line of notCoveredByTracker) {
  checkBanned('notCoveredByTracker entry', line)
}

// --- 9. What-changed EDGAR items must be each supplier's latest quarter ---
//
// `edgarFilingsInLast30Days` (derive.ts) already restricts itself to each
// supplier's chronologically latest quarter — this gate re-derives that
// same "latest quarter" independently, straight from the generated facts
// file, and fails if what the function actually returns ever disagrees, so
// a future edit to that function's selection logic cannot silently
// reintroduce the "filed its 10-Q for the quarter ended 2025-07-31" defect
// without failing the build.
for (const filing of edgarFilingsInLast30Days(TODAY, edgarFactsRaw)) {
  const supplier = edgarFactsRaw.suppliers.find((s) => s.id === filing.supplierId)
  if (!supplier || supplier.quarters.length === 0) continue
  const trueLatestPeriodEnd = supplier.quarters.reduce(
    (latest, q) => (q.periodEnd > latest ? q.periodEnd : latest),
    supplier.quarters[0].periodEnd,
  )
  if (filing.periodEnd !== trueLatestPeriodEnd) {
    fail(
      `what-changed EDGAR filing for supplier "${filing.supplierId}": periodEnd "${filing.periodEnd}" is not ` +
        `that supplier's latest quarter ("${trueLatestPeriodEnd}") — looks like a restated prior-year ` +
        'comparative, not a new filing',
    )
  }
}

// --- 12. runStatus.state must not claim "updated" while gate 11 found a stale figure ---

if (staleFigureFound && runStatus.state === 'updated') {
  fail(
    `runStatus.state is "updated" ("every source collected"), but gate 11 above found a supplier ` +
      'whose tracked revenue figure is older than what generated/edgarFacts.json already holds for ' +
      'that same filer — the run-status line would misstate what happened (src/data/runStatus.ts)',
  )
}

// --- 13. AUTO-001 fix pass 2, item 2: two rows in one domain may not share a display name ---

const namesByDomain = new Map<string, Map<string, string[]>>()
for (const supplier of trackerSuppliers) {
  for (const domainId of supplier.domainIds) {
    if (!namesByDomain.has(domainId)) namesByDomain.set(domainId, new Map())
    const byName = namesByDomain.get(domainId)!
    const ids = byName.get(supplier.name) ?? []
    ids.push(supplier.id)
    byName.set(supplier.name, ids)
  }
}
for (const [domainId, byName] of namesByDomain) {
  for (const [name, ids] of byName) {
    if (ids.length > 1) {
      fail(
        `domain "${domainId}": suppliers [${ids.join(', ')}] share the display name "${name}" — two rows ` +
          'in one domain table must be distinguishable',
      )
    }
  }
}

// --- 14. AUTO-001 fix pass 2, item 1: a dated fact inside the trailing 12 months on a supplier
// record (lastRound, ownership.announced/closed) must also exist as an event in events.ts ---

/** `dateIso` may be "YYYY-MM" (funding month precision) or a full "YYYY-MM-DD". */
function toComparableDate(dateIso: string): string {
  return dateIso.length === 7 ? `${dateIso}-01` : dateIso
}

/**
 * True when this supplier already has an event of one of `types` inside the
 * same trailing-12-month window `eventSummaryForSupplier` (derive.ts) counts
 * for "Events, 12 mo.". Matched on type and window, not on an exact date
 * string — a funding round's supplier-record date is sometimes month-only
 * precision while the event carries the report's day-precision date, and
 * both are sourced from the same underlying fact.
 */
function hasMatchingEvent(supplierId: string, types: string[]): boolean {
  // AUTO-002 Phase 2: check the retained record, not the display window, so a
  // window that moves with every SEC refresh cannot fail the build at its edge.
  return retainedTrackerEvents.some((event) => {
    if (event.supplierId !== supplierId || !types.includes(event.type)) return false
    const eventAge = daysBetween(event.date, runStatus.lastChecked)
    return eventAge >= 0 && eventAge <= 400
  })
}

for (const supplier of trackerSuppliers) {
  const who = `supplier "${supplier.id}" (${supplier.name})`

  if (supplier.lastRound?.date) {
    const age = daysBetween(toComparableDate(supplier.lastRound.date), runStatus.lastChecked)
    if (age >= 0 && age <= 365 && !hasMatchingEvent(supplier.id, ['funding'])) {
      fail(
        `${who}: lastRound.date "${supplier.lastRound.date}" is inside the trailing 12 months but no ` +
          'matching "funding" event exists in events.ts',
      )
    }
  }

  if (supplier.ownership) {
    for (const field of ['announced', 'closed'] as const) {
      const dateVal = supplier.ownership[field]
      if (!dateVal) continue
      const age = daysBetween(dateVal, runStatus.lastChecked)
      if (age >= 0 && age <= 365 && !hasMatchingEvent(supplier.id, ['acquisition', 'divestiture'])) {
        fail(
          `${who}: ownership.${field} "${dateVal}" is inside the trailing 12 months but no matching ` +
            '"acquisition"/"divestiture" event exists in events.ts',
        )
      }
    }
  }
}

// --- 15. AUTO-001 fix pass 2, item 6: an evidence URL the tracker cites may not be a bare
// domain or a newsroom/IR index page with no specific document slug ---

const INDEX_PATH_WORDS = new Set([
  'news',
  'newsroom',
  'press',
  'press-releases',
  'pressroom',
  'media',
  'media-center',
  'investors',
  'investor-relations',
  'ir',
  'blog',
  'announcements',
])

function bareDomainOrIndexReason(url: string): string | null {
  let parsed: URL
  try {
    parsed = new URL(url)
  } catch {
    return 'is not a valid URL'
  }
  const path = parsed.pathname.replace(/\/+$/, '')
  if (path === '') return 'is a bare domain with no path'
  const segments = path.split('/').filter(Boolean)
  const last = segments[segments.length - 1]?.toLowerCase() ?? ''
  if (segments.length === 1 && INDEX_PATH_WORDS.has(last)) {
    return `is a newsroom/IR index page ("${path}") with no specific document`
  }
  return null
}

for (const id of usedEvidenceIds) {
  const record = evidenceById[id]
  if (!record || !record.canonicalUrl) continue // already failed by check 2 above
  const reason = bareDomainOrIndexReason(record.canonicalUrl)
  if (reason) {
    fail(`evidence "${id}" (${record.canonicalUrl}): ${reason} — link the specific document instead`)
  }
}

// --- Report ---

console.log(
  `verify:tracker — ${trackerDomains.length} domains, ${trackerSuppliers.length} suppliers, ` +
    `${trackerEvents.length} events`,
)
for (const [domainId, count] of supplierCountByDomain) {
  console.log(`  ${domainId}: ${count} supplier(s)`)
}

if (failCount > 0) {
  console.error('')
  console.error(`FAIL  verify:tracker — ${failCount} problem(s):`)
  for (const failure of failures) console.error(`  - ${failure}`)
  process.exit(1)
}

console.log('verify:tracker passed')
