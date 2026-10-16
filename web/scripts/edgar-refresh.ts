import { mkdir, readFile, writeFile } from 'node:fs/promises'
import { createHash } from 'node:crypto'
import { dirname } from 'node:path'
import { fileURLToPath } from 'node:url'
import { edgarRegistry, unsupported } from '../src/data/edgarRegistry.ts'
import { buildSupplierRecord, type CompanyFacts, type SupplierFailure, type SupplierRecord } from '../src/data/edgarLogic.ts'

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
      checks.push({ supplierId: edgarRegistry.find(s => s.cik === cik)!.id, checkedAt: new Date().toISOString(), url, status: 'checked', sha256: createHash('sha256').update(text).digest('hex') })
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

async function main() {
  const result = await run()

  await mkdir(dirname(fileURLToPath(OUTPUT_PATH)), { recursive: true })
  await writeFile(OUTPUT_PATH, `${JSON.stringify(result, null, 2)}\n`, 'utf8')
  console.log(`\nwrote ${fileURLToPath(OUTPUT_PATH)}`)
  console.log(`${result.suppliers.length} ok, ${result.failures.length} failed, ${result.unsupported.length} unsupported by design`)

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
