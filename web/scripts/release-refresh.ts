import { readFile, writeFile } from 'node:fs/promises'
import { createHash } from 'node:crypto'
import { fileURLToPath } from 'node:url'
import { releaseRegistry } from '../src/data/releaseRegistry.ts'
import { buildReleaseRecord, parseResultsRelease, type ReleaseQuarter, type ReleaseRecord } from '../src/data/sixKLogic.ts'

// Reads quarterly results releases that foreign private issuers furnish on
// Form 6-K (releaseRegistry.ts, backlog SEC-080) and writes
// web/src/data/generated/companyReleases.json. Runs at the end of
// `npm run refresh:edgar`, so the release gate runs it against the
// collector's archived SEC responses only. A fetch or parse failure keeps the
// last good record and never fails the gate. No model is involved.

const USER_AGENT = 'SecurityMarketPulse research jesse@keatingpike.com'
const OUTPUT_PATH = new URL('../src/data/generated/companyReleases.json', import.meta.url)
const LOOKBACK_DAYS = 400

interface Output { generatedAt: string; suppliers: ReleaseRecord[]; failures: { id: string; reason: string }[]; checks: { id: string; url: string; status: string; reason?: string }[] }
interface Submissions { cik: string; filings: { recent: { form: string[]; filingDate: string[]; accessionNumber: string[]; primaryDocument: string[] } } }

const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))
async function get(url: string) {
  const response = await fetch(url, { headers: { 'User-Agent': USER_AGENT }, signal: AbortSignal.timeout(30000) })
  if (!response.ok) throw new Error(`HTTP ${response.status} fetching ${url}`)
  return { text: await response.text(), checkedAt: response.headers.get('x-smp-source-checked-at') ?? new Date().toISOString() }
}

export async function refreshReleases(now = new Date(), outputPath: URL | string = OUTPUT_PATH): Promise<Output> {
  let previous: Output = { generatedAt: '', suppliers: [], failures: [], checks: [] }
  try { previous = JSON.parse(await readFile(outputPath, 'utf8')) as Output } catch { /* first run */ }
  const out: Output = { generatedAt: now.toISOString(), suppliers: [], failures: [], checks: [] }
  const since = new Date(now.getTime() - LOOKBACK_DAYS * 86_400_000).toISOString().slice(0, 10)
  for (const reg of releaseRegistry) {
    const retained = previous.suppliers.find(s => s.id === reg.id)
    try {
      const indexUrl = `https://data.sec.gov/submissions/CIK${reg.cik}.json`
      const index = JSON.parse((await get(indexUrl)).text) as Submissions
      if (String(Number(index.cik)) !== String(Number(reg.cik))) throw new Error('SEC submissions CIK differs from registry')
      out.checks.push({ id: reg.id, url: indexUrl, status: 'checked' })
      const r = index.filings.recent
      const known = new Set(retained?.quarters.map(q => q.accessionNumber))
      const newest = retained?.quarters.reduce((m, q) => q.filedDate > m ? q.filedDate : m, '') ?? ''
      const fresh: ReleaseQuarter[] = []
      for (let i = 0; i < r.form.length; i++) {
        if (r.form[i] !== reg.form || r.filingDate[i] < since || r.filingDate[i] < newest || known.has(r.accessionNumber[i])) continue
        const accession = r.accessionNumber[i], primary = r.primaryDocument[i]
        if (!/^\d{10}-\d{2}-\d{6}$/.test(accession) || !/^[A-Za-z0-9_.-]+$/.test(primary)) throw new Error('Invalid SEC filing path')
        const url = `https://www.sec.gov/Archives/edgar/data/${Number(reg.cik)}/${accession.replaceAll('-', '')}/${primary}`
        await sleep(250)
        let doc
        try { doc = await get(url) } catch (error) {
          out.checks.push({ id: reg.id, url, status: 'unavailable', reason: error instanceof Error ? error.message : String(error) }); continue
        }
        try {
          const parsed = parseResultsRelease(doc.text)
          fresh.push({ ...parsed, scale: 'USD millions', form: '6-K', accessionNumber: accession, filedDate: r.filingDate[i], sourceUrl: url,
            sha256: createHash('sha256').update(doc.text).digest('hex'), checkedAt: doc.checkedAt })
          out.checks.push({ id: reg.id, url, status: 'parsed' })
        } catch (error) {
          // Most 6-Ks are not results releases; they are skipped, not failures.
          out.checks.push({ id: reg.id, url, status: 'not-results', reason: error instanceof Error ? error.message : String(error) })
        }
      }
      out.suppliers.push(buildReleaseRecord(reg.id, reg.name, reg.cik, retained?.quarters ?? [], fresh))
    } catch (error) {
      out.failures.push({ id: reg.id, reason: error instanceof Error ? error.message : String(error) })
      if (retained) out.suppliers.push(retained)
    }
  }
  await writeFile(outputPath, `${JSON.stringify(out, null, 2)}\n`, 'utf8')
  for (const s of out.suppliers) console.log(`6-K   ${s.id.padEnd(12)} latest ${s.latest?.periodEnd ?? 'none'} (${s.quarters.length} quarters)`)
  for (const f of out.failures) console.error(`6-K   ${f.id.padEnd(12)} retained: ${f.reason}`)
  return out
}

if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) {
  refreshReleases().catch(error => { console.error(error); process.exit(1) })
}
