import { mkdir, readFile, writeFile } from 'node:fs/promises'
import { dirname } from 'node:path'
import { fileURLToPath } from 'node:url'
import { edgarRegistry } from '../src/data/edgarRegistry.ts'
import { handCollectedEvents } from '../src/data/tracker/events.ts'
import { debtExcerpt } from './sec-verify/debt-excerpt.mjs'
import type { TrackerEvent, TrackerEventType } from '../src/data/tracker/events.ts'

/**
 * AUTO-001 fix pass 4, item 5: dated events drawn straight from each SEC
 * filer's own 8-K item codes — no model in the loop. Reads each supplier in
 * edgarRegistry.ts (the domestic SEC filers that already have XBRL coverage;
 * a foreign private issuer like Check Point files 6-Ks, not 8-Ks, so it has
 * no item codes to scan), fetches that filer's own submissions index, and
 * picks out every 8-K whose "items" field names one of five codes that are
 * always a dated, material fact rather than routine disclosure:
 *
 *   5.02  departure/election of directors or certain officers
 *   2.01  completed acquisition or disposition of assets
 *   1.03  bankruptcy or receivership
 *   2.05  costs associated with exit or disposal activities
 *   3.01  notice of delisting or failure to satisfy a listing rule
 *
 * Each match becomes a TrackerEvent (same shape and rung-1 sourcing as a
 * hand-collected one) plus a matching synthetic evidence record pointing at
 * the filing document itself — both written to generated/ files that
 * tracker/events.ts and evidence.ts import and merge in at module load, so
 * nothing here is hand-typed. Run with `npm run refresh:filing-events` — it
 * reads edgarRegistry.ts directly, not generated/edgarFacts.json's output,
 * so it can run before or after `refresh:edgar`.
 *
 * Item 5.02's own cover caption is "Departure of Directors or Certain
 * Officers; Election of Directors; Appointment of Certain Officers;
 * Compensatory Arrangements of Certain Officers" on every single 5.02
 * filing, appointment or departure or both — so a plain keyword match
 * against the filing text would see both words on every filing and could
 * never tell them apart without reading the caption against the body, and
 * some 5.02 filings (Okta's 2026-09-18 one among them) report a departure
 * and an appointment in the same filing, so a single-direction label would
 * misstate it either way. This script deliberately does not attempt that
 * distinction — it reports what the item code itself establishes (a change
 * in directors or officers, dated and linked to the filing) and leaves the
 * specifics to whoever opens the filing, rather than guessing.
 */

const USER_AGENT = 'SecurityMarketPulse research jesse@keatingpike.com'
const REQUEST_INTERVAL_MS = 300
const EVENTS_OUTPUT_PATH = new URL('../src/data/generated/filingEvents.json', import.meta.url)
const EVIDENCE_OUTPUT_PATH = new URL('../src/data/generated/filingEvidence.json', import.meta.url)

// events.ts's own contract is "append-only, trailing-12-month record of
// dated facts per supplier" — so this generator uses the SAME window the
// rest of the site shows events in (the 365 days ending on
// runStatus.lastChecked, the pipeline's own "as of" date — not today's wall
// clock, which would include a filing nothing else on the site is treating
// as current yet).
const refreshDate = process.env.SMP_REFRESH_DATE ?? new Date().toISOString().slice(0, 10)
const [lastCheckedYear, lastCheckedMonth, lastCheckedDay] = refreshDate.split('-').map(Number)
const WINDOW_END_MS = Date.UTC(lastCheckedYear, lastCheckedMonth - 1, lastCheckedDay)
const WINDOW_START = new Date(WINDOW_END_MS - 365 * 86_400_000).toISOString().slice(0, 10)

const ITEM_CODE_MAP: Record<string, { type: TrackerEventType; label: string }> = {
  '5.02': { type: 'exec-change', label: 'a change in directors or certain officers' },
  '2.01': { type: 'acquisition', label: 'a completed acquisition or disposition of assets' },
  '1.03': { type: 'going-concern', label: 'a bankruptcy or receivership filing' },
  '2.05': { type: 'restructuring', label: 'costs associated with an exit or disposal activity' },
  '3.01': { type: 'going-concern', label: 'a notice of delisting or failure to satisfy a continued listing rule' },
  // AUTO-002 Phase 0 (D-91): debt obligations are listed as filed events.
  '2.03': { type: 'debt', label: 'the creation of a direct financial obligation' },
}

// AUTO-002 Phase 0: whole-form events that carry no 8-K item codes.
const FORM_MAP: Record<string, { type: TrackerEventType; label: string }> = {
  '25': { type: 'going-concern', label: 'notification of removal from listing' },
  '25-NSE': { type: 'going-concern', label: 'notification of removal from listing' },
  'DEFM14A': { type: 'acquisition', label: 'a definitive proxy statement for a proposed merger' },
  'PREM14A': { type: 'acquisition', label: 'a preliminary proxy statement for a proposed merger' },
  // AUTO-002 Phase 2 (D-91): late-filing notices.
  'NT 10-K': { type: 'late-filing', label: 'notice that its annual report will be filed late' },
  'NT 10-Q': { type: 'late-filing', label: 'notice that its quarterly report will be filed late' },
}

interface SubmissionsRecent {
  form: string[]
  filingDate: string[]
  accessionNumber: string[]
  primaryDocument: string[]
  items: string[]
}

interface SubmissionsResponse {
  cik: string
  filings: { recent: SubmissionsRecent }
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

function documentUrl(cik: string, accessionNumber: string, primaryDocument: string): string {
  const cikNum = String(Number(cik))
  const accNoDashes = accessionNumber.replace(/-/g, '')
  return `https://www.sec.gov/Archives/edgar/data/${cikNum}/${accNoDashes}/${primaryDocument}`
}

async function fetchText(url: string): Promise<string> {
  let failure: unknown
  for (let attempt = 0; attempt < 3; attempt++) {
    try {
      const response = await fetch(url, { headers: { 'User-Agent': USER_AGENT }, signal: AbortSignal.timeout(30000) })
      if (!response.ok) throw new Error(`HTTP ${response.status} fetching ${url}`)
      return await response.text()
    } catch (error) { failure = error; if (attempt < 2) await sleep(1000) }
  }
  throw failure
}

interface GeneratedEvent extends TrackerEvent {}
interface GeneratedEvidence {
  id: string
  title: string
  organization: string
  publicationDate: string
  economicPeriod: string
  canonicalUrl: string
  excerpt: string
  sourceClass: string
  interpretation: string
  limitations: string
  conflictingEvidenceIds: string[]
  artifactLabel: string
  tags: string[]
  retrievedAt: string
}

// Dedupe against the HAND-COLLECTED set only, never against this script's
// own prior output (which `trackerEvents` in events.ts also merges in) — the
// latter would make every event this script ever found "already covered"
// on the very next run and silently empty the generated file out.
// AUTO-002 Phase 0: dedupe by supplier, date AND type. A same-day hand-collected
// event of a different type (e.g. an acquisition announced alongside an officer
// change in one 8-K) must not hide the filing's own tracked item.
const existingEventKeys = new Set(handCollectedEvents.map((event) => `${event.supplierId}|${event.date}|${event.type}`))

async function main() {
  const previousEvents = JSON.parse(await readFile(EVENTS_OUTPUT_PATH, 'utf8')) as GeneratedEvent[]
  const previousEvidence = JSON.parse(await readFile(EVIDENCE_OUTPUT_PATH, 'utf8')) as GeneratedEvidence[]
  const checks: Array<{ supplierId: string; url: string; checkedAt: string; status: string; reason?: string }> = []
  const events: GeneratedEvent[] = []
  const evidence: GeneratedEvidence[] = []
  const today = new Date().toISOString().slice(0, 10)

  for (const [index, supplier] of edgarRegistry.entries()) {
    if (index > 0) await sleep(REQUEST_INTERVAL_MS)
    const url = `https://data.sec.gov/submissions/CIK${supplier.cik}.json`
    let data: SubmissionsResponse
    try {
      data = JSON.parse(await fetchText(url)) as SubmissionsResponse
      checks.push({ supplierId: supplier.id, url, checkedAt: new Date().toISOString(), status: 'checked' })
    } catch (error) {
      console.error(`FAIL  ${supplier.id.padEnd(12)} ${error instanceof Error ? error.message : String(error)}`)
      checks.push({ supplierId: supplier.id, url, checkedAt: new Date().toISOString(), status: 'failed-retained', reason: String(error) })
      events.push(...previousEvents.filter(e => e.supplierId === supplier.id))
      const ids = new Set(events.filter(e => e.supplierId === supplier.id).flatMap(e => e.evidenceIds))
      evidence.push(...previousEvidence.filter(e => ids.has(e.id)))
      continue
    }

    const recent = data.filings.recent
    let found = 0
    for (let i = 0; i < recent.form.length; i++) {
      const form = recent.form[i]
      if (form !== '8-K' && !(form in FORM_MAP)) continue
      const filingDate = recent.filingDate[i]
      if (filingDate < WINDOW_START || filingDate > refreshDate) continue
      const itemCodes = (recent.items[i] ?? '').split(',').map((s) => s.trim())
      const matchedCode = form === '8-K' ? itemCodes.find((code) => code in ITEM_CODE_MAP) : form
      if (!matchedCode) continue

      const mapping = form === '8-K' ? ITEM_CODE_MAP[matchedCode] : FORM_MAP[form]
      const formLabel = form === '8-K' ? `Form 8-K (Item ${matchedCode})` : `Form ${form}`
      const accession = recent.accessionNumber[i]
      const primaryDocument = recent.primaryDocument[i]
      const docUrl = documentUrl(supplier.cik, accession, primaryDocument)

      const dedupeKey = `${supplier.id}|${filingDate}|${mapping.type}`
      if (existingEventKeys.has(dedupeKey)) {
        console.log(`skip  ${supplier.id.padEnd(12)} ${filingDate} item ${matchedCode} — already a hand-collected ${mapping.type} event on this date`)
        continue
      }

      let text = `${formLabel} reporting ${mapping.label}, filed ${filingDate}.`
      // D-91: a debt event quotes the filing's own description of the obligation.
      if (form === '8-K' && matchedCode === '2.03') {
        try {
          await sleep(REQUEST_INTERVAL_MS)
          const quote = debtExcerpt(await fetchText(docUrl))
          if (quote) text = quote.endsWith('…') ? `${text} The filing describes it as: “${quote.slice(0, -1)}” …` : `${text} The filing describes it as: “${quote}”`
        } catch (error) { console.error(`WARN  ${supplier.id} ${accession}: could not read the filing for its description (${String(error)})`) }
      }

      const eventId = `EV-filing-${supplier.id}-${accession}`
      const evidenceId = `TR-filing-${supplier.id}-${accession}`

      events.push({
        id: eventId,
        supplierId: supplier.id,
        date: filingDate,
        type: mapping.type,
        text,
        evidenceIds: [evidenceId],
        rung: 1,
      })

      evidence.push({
        id: evidenceId,
        title: `${supplier.name} — ${formLabel}`,
        organization: supplier.name,
        publicationDate: filingDate,
        economicPeriod: filingDate,
        canonicalUrl: docUrl,
        excerpt: `${formLabel}: ${mapping.label}.`,
        sourceClass: 'FILING',
        interpretation: '',
        limitations:
          'AUTO-001 fix pass 4, item 5: generated directly from this filer\'s own 8-K item code at ' +
          'build time, with no model in the loop. States only what the item code itself ' +
          'establishes, not the filing\'s specifics (e.g. appointment vs. departure for Item 5.02) ' +
          '— open the filing for those.',
        conflictingEvidenceIds: [],
        artifactLabel: `SEC-MARKET-AUTO-001-STEP5 / ${evidenceId}`,
        tags: ['tracker', 'filing-event'],
        retrievedAt: today,
      })

      found += 1
      console.log(`found ${supplier.id.padEnd(12)} ${filingDate} item ${matchedCode} — ${text}`)
    }
    if (found === 0) console.log(`none  ${supplier.id.padEnd(12)} no matching 8-K items in the trailing 12-month window`)
  }

  await mkdir(dirname(fileURLToPath(EVENTS_OUTPUT_PATH)), { recursive: true })
  await writeFile(new URL('../src/data/generated/filingRun.json', import.meta.url), `${JSON.stringify({ checkedAt: new Date().toISOString(), windowEnd: refreshDate, checks }, null, 2)}\n`, 'utf8')
  await writeFile(EVENTS_OUTPUT_PATH, `${JSON.stringify(events, null, 2)}\n`, 'utf8')
  await writeFile(EVIDENCE_OUTPUT_PATH, `${JSON.stringify(evidence, null, 2)}\n`, 'utf8')
  console.log(`\nwrote ${events.length} filing-driven event(s) to ${fileURLToPath(EVENTS_OUTPUT_PATH)}`)
  console.log(`wrote ${evidence.length} matching evidence record(s) to ${fileURLToPath(EVIDENCE_OUTPUT_PATH)}`)
}

main().catch((error) => {
  console.error(error)
  process.exit(1)
})
