import { mkdir, writeFile } from 'node:fs/promises'
import { dirname } from 'node:path'
import { fileURLToPath } from 'node:url'
import { edgarRegistry, unsupported } from '../src/data/edgarRegistry.ts'
import { buildSupplierRecord, type CompanyFacts, type SupplierFailure, type SupplierRecord } from '../src/data/edgarLogic.ts'

// Fetches SEC EDGAR's structured XBRL "companyfacts" API for every supplier
// in edgarRegistry.ts, extracts eight quarters of GAAP revenue with Q4
// derivation and YoY growth (all pure logic in ../src/data/edgarLogic.ts),
// and writes web/src/data/generated/edgarFacts.json. No model is involved —
// this is step 2 of docs/active/autonomy-coverage-plan.md §5: EDGAR gives
// structured facts for every US filer, so this runner cannot invent a
// number. Run with `npm run refresh:edgar`.
//
// Per docs/active/gather-brief.md's User-Agent convention, and at a rate
// SEC's fair-access policy (https://www.sec.gov/os/webmaster-faq#developers)
// asks for (no more than 10 requests/second; this stays well under that at
// ~4/second).

const USER_AGENT = 'SecurityMarketPulse research jesse@keatingpike.com'
const REQUEST_INTERVAL_MS = 250 // 4 requests/second, under the ≤5/second budget
const OUTPUT_PATH = new URL('../src/data/generated/edgarFacts.json', import.meta.url)

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

async function fetchCompanyFacts(cik: string): Promise<CompanyFacts> {
  const url = `https://data.sec.gov/api/xbrl/companyfacts/CIK${cik}.json`
  const response = await fetch(url, { headers: { 'User-Agent': USER_AGENT, Accept: 'application/json' } })
  if (!response.ok) {
    throw new Error(`HTTP ${response.status} ${response.statusText} fetching ${url}`)
  }
  return (await response.json()) as CompanyFacts
}

interface RunResult {
  generatedAt: string
  suppliers: SupplierRecord[]
  unsupported: typeof unsupported
  failures: SupplierFailure[]
}

async function run(): Promise<RunResult> {
  const suppliers: SupplierRecord[] = []
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
      suppliers.push(record)
      console.log(`ok    ${supplier.id.padEnd(12)} ${record.concept} — ${record.quarters.length} quarters`)
    } catch (error) {
      const reason = error instanceof Error ? error.message : String(error)
      failures.push({ id: supplier.id, name: supplier.name, reason })
      console.error(`FAIL  ${supplier.id.padEnd(12)} ${reason}`)
    }
  }

  return {
    generatedAt: new Date().toISOString(),
    suppliers,
    unsupported,
    failures,
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
