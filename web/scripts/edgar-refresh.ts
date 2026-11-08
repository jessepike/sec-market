import { mkdir, readFile, writeFile } from 'node:fs/promises'
import { createHash } from 'node:crypto'
import { dirname } from 'node:path'
import { fileURLToPath } from 'node:url'
import { edgarRegistry, unsupported } from '../src/data/edgarRegistry.ts'
import { refreshReleases } from './release-refresh.ts'
import { buildSupplierRecord, type CompanyFacts, type SupplierFailure, type SupplierRecord } from '../src/data/edgarLogic.ts'
import { computeHealth, healthMethod, type HealthFile } from '../src/data/healthLogic.ts'

// Fetches SEC EDGAR's structured XBRL "companyfacts" API for every supplier
// in edgarRegistry.ts, extracts eight quarters of GAAP revenue with Q4
// derivation and YoY growth (all pure logic in ../src/data/edgarLogic.ts),
// and writes web/src/data/generated/edgarFacts.json. No model is involved —
// this is step 2 of docs/archive/2026-10-refresh-gate/autonomy-coverage-plan.md §5: EDGAR gives
// structured facts for every US filer, so this runner cannot invent a
// number. Run with `npm run refresh:edgar`.
//
// Per docs/archive/2026-09-weekly-issue/gather-brief.md's User-Agent convention, and at a rate
// SEC's fair-access policy (https://www.sec.gov/os/webmaster-faq#developers)
// asks for (no more than 10 requests/second; this stays well under that at
// ~4/second).

const USER_AGENT = 'SecurityMarketPulse research jesse@keatingpike.com'
const REQUEST_INTERVAL_MS = 250 // 4 requests/second, under the ≤5/second budget
const OUTPUT_PATH = new URL('../src/data/generated/edgarFacts.json', import.meta.url)
const HEALTH_PATH = new URL('../src/data/generated/healthFacts.json', import.meta.url)
const CONTRACT_PATH = new URL('../src/data/tracker/certifiedContract.json', import.meta.url)
const fetchedFacts = new Map<string, CompanyFacts>()
const checks: Array<{ supplierId: string; checkedAt: string; url: string; status: string; sha256?: string; reason?: string }> = []

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

async function fetchCompanyFacts(cik: string): Promise<CompanyFacts> {
  const url = `https://data.sec.gov/api/xbrl/companyfacts/CIK${cik}.json`
  let lastError: unknown
  for (let attempt = 0; attempt < 3; attempt++) {
    try {
      const response = await fetch(url, { headers: { 'User-Agent': USER_AGENT, Accept: 'application/json' }, signal: AbortSignal.timeout(30000) })
      if (!response.ok) throw new Error(`HTTP ${response.status} fetching ${url}`)
      const text = await response.text()
      const data = JSON.parse(text) as CompanyFacts
      checks.push({ supplierId: edgarRegistry.find(s => s.cik === cik)!.id, checkedAt: response.headers.get('x-smp-source-checked-at') ?? new Date().toISOString(), url, status: 'checked', sha256: createHash('sha256').update(text).digest('hex') })
      return data
    } catch (error) { lastError = error; if (attempt < 2) await sleep(1000) }
  }
  throw lastError
}

interface CheckedSupplierRecord extends SupplierRecord {
  sourceCheck?: { checkedAt: string; url: string; sha256: string }
}
interface RunResult {
  generatedAt: string
  suppliers: CheckedSupplierRecord[]
  unsupported: typeof unsupported
  failures: SupplierFailure[]
  checks: typeof checks
}

async function run(): Promise<RunResult> {
  const previous = JSON.parse(await readFile(OUTPUT_PATH, 'utf8')) as RunResult
  const suppliers: CheckedSupplierRecord[] = []
  const failures: SupplierFailure[] = []

  for (const [index, supplier] of edgarRegistry.entries()) {
    if (index > 0) await sleep(REQUEST_INTERVAL_MS)
    try {
      const companyFacts = await fetchCompanyFacts(supplier.cik)
      fetchedFacts.set(supplier.id, companyFacts)
      const record = buildSupplierRecord(
        supplier.id,
        supplier.name,
        supplier.cik,
        companyFacts,
        supplier.revenueConcepts,
      )
      const source = checks.find(c => c.supplierId === supplier.id && c.status === 'checked')!
      suppliers.push({ ...record, sourceCheck: { checkedAt: source.checkedAt, url: source.url, sha256: source.sha256! } })
      console.log(`ok    ${supplier.id.padEnd(12)} ${record.concept} — ${record.quarters.length} quarters`)
    } catch (error) {
      const reason = error instanceof Error ? error.message : String(error)
      failures.push({ id: supplier.id, name: supplier.name, reason })
      const retained = previous.suppliers.find(s => s.id === supplier.id)
      if (retained) suppliers.push(retained)
      checks.push({ supplierId: supplier.id, checkedAt: new Date().toISOString(), url: `https://data.sec.gov/api/xbrl/companyfacts/CIK${supplier.cik}.json`, status: 'failed-retained', reason })
      console.error(`FAIL  ${supplier.id.padEnd(12)} ${reason}`)
    }
  }

  return {
    generatedAt: new Date().toISOString(),
    suppliers,
    unsupported,
    failures,
    checks,
  }
}

async function refreshHealth(result: RunResult) {
  const certified = new Set((JSON.parse(await readFile(CONTRACT_PATH, 'utf8')) as { supplierIds: string[] }).supplierIds)
  const previous = JSON.parse(await readFile(HEALTH_PATH, 'utf8')) as HealthFile
  const out: HealthFile = { generatedAt: result.generatedAt, method: healthMethod, suppliers: {}, gaps: {} }
  for (const record of result.suppliers) {
    if (!certified.has(record.id)) continue
    const facts = fetchedFacts.get(record.id)
    if (!facts) {
      // Revenue was retained from the last run, so keep the health figures that went with it.
      if (previous.suppliers[record.id]) out.suppliers[record.id] = previous.suppliers[record.id]
      if (previous.gaps[record.id]) out.gaps[record.id] = previous.gaps[record.id]
      continue
    }
    const { health, gaps, notes } = computeHealth(record.cik, record.quarters, facts)
    out.suppliers[record.id] = health
    if (gaps.length) out.gaps[record.id] = gaps
    if (notes.length) (out.notes ??= {})[record.id] = notes
  }
  await writeFile(HEALTH_PATH, `${JSON.stringify(out, null, 1)}\n`, 'utf8')
  console.log(`health: ${Object.keys(out.suppliers).length} certified filers, ${Object.keys(out.gaps).length} with gaps`)
}

async function main() {
  const result = await run()

  await mkdir(dirname(fileURLToPath(OUTPUT_PATH)), { recursive: true })
  await writeFile(OUTPUT_PATH, `${JSON.stringify(result, null, 2)}\n`, 'utf8')
  console.log(`\nwrote ${fileURLToPath(OUTPUT_PATH)}`)
  console.log(`${result.suppliers.length} ok, ${result.failures.length} failed, ${result.unsupported.length} unsupported by design`)
  // Margins and cash and debt from the same responses, so they sit on the revenue quarter shown
  // beside them. A failure keeps the last good file and never fails the run (improvement loop IL-002).
  try { await refreshHealth(result) } catch (error) { console.error('health refresh kept the last good record:', error) }
  // 6-K results releases (SEC-080). A failure here keeps the last good record and never fails the run.
  try { await refreshReleases() } catch (error) { console.error('6-K release refresh kept the last good record:', error) }

  const totalAttempted = edgarRegistry.length
  const failureRatio = result.failures.length / totalAttempted
  if (failureRatio > 0.5) {
    console.error(`more than half of suppliers failed (${result.failures.length}/${totalAttempted}) — exiting non-zero`)
    process.exit(1)
  }
}

main().catch((error) => {
  console.error(error)
  process.exit(1)
})
