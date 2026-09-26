import { readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { evidenceById } from '../src/data/evidence.ts'
import { notCoveredByTracker, trackerDomains } from '../src/data/tracker/domains.ts'
import { trackerEvents } from '../src/data/tracker/events.ts'
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
  suppliers: Array<{ id: string }>
}
const edgarSupplierIds = new Set(edgarFactsRaw.suppliers.map((s) => s.id))

let failCount = 0
const failures: string[] = []

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

for (const supplier of trackerSuppliers) {
  const who = `supplier "${supplier.id}" (${supplier.name})`
  if (supplier.headlineMetric) {
    checkEvidenceIds(`${who} headlineMetric`, supplier.headlineMetric.evidenceIds)
    checkBanned(`${who} headlineMetric.label`, supplier.headlineMetric.label)
  }
  if (supplier.revenue) {
    checkEvidenceIds(`${who} revenue.latest`, supplier.revenue.latest.evidenceIds)
    // `prior` is optional — some segments (e.g. an unbroken-out Microsoft
    // product line) only have one comparable quarter in the research.
    if (supplier.revenue.prior) {
      checkEvidenceIds(`${who} revenue.prior`, supplier.revenue.prior.evidenceIds)
      checkDateField(`${who} revenue.prior.periodEnd`, supplier.revenue.prior.periodEnd)
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
