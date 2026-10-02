import { evidenceRecords } from '../src/data/evidence.ts'

/**
 * AUTO-001 fix pass 4, item 9: a report, not a build gate — requests every
 * distinct `canonicalUrl` in evidence.ts with a descriptive User-Agent and
 * prints which ones don't return 200, and which ones land on a generic
 * index/landing page rather than a specific document. `verify-tracker.ts`'s
 * gate 15 already catches the narrowest case of this (a bare domain, or a
 * single-segment path that's exactly an index word like "/newsroom") at
 * build time; this script is deliberately broader — it actually fetches
 * each URL and also flags a deeper index-like path (e.g.
 * ".../en/company/newsroom.html" or ".../en-us/investor"), which gate 15's
 * static path check cannot see without making a network call. Run with
 * `npm run check:links`. Never exits non-zero; a human reads the report and
 * fixes what it finds, the way the brief asks.
 */

const USER_AGENT = 'SecurityMarketPulse jesse@keatingpike.com'
const REQUEST_TIMEOUT_MS = 15_000
const REQUEST_INTERVAL_MS = 500

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

interface CheckResult {
  url: string
  usedBy: string[]
  status: number | null
  error: string | null
  indexLike: string | null
}

/**
 * The same "is this an index/landing page" heuristic as gate 15 in
 * verify-tracker.ts, but checked against every path segment (not only a
 * single-segment path) and against the final filename with its extension
 * stripped — catching ".../en/company/newsroom.html" and
 * ".../en-us/investor", neither of which gate 15's stricter, cheaper,
 * build-time-only check can see.
 */
const INDEX_PATH_WORDS = new Set([
  'news',
  'newsroom',
  'press',
  'press-releases',
  'pressroom',
  'media',
  'media-center',
  'investors',
  'investor',
  'investor-relations',
  'ir',
  'blog',
  'announcements',
  'about',
  'about-us',
])

function indexLikeReason(url: string): string | null {
  let parsed: URL
  try {
    parsed = new URL(url)
  } catch {
    return 'not a valid URL'
  }
  const path = parsed.pathname.replace(/\/+$/, '')
  if (path === '') return 'bare domain with no path'
  const segments = path.split('/').filter(Boolean)
  const last = segments[segments.length - 1]?.toLowerCase() ?? ''
  const lastNoExt = last.replace(/\.(html?|aspx?|php)$/, '')
  if (INDEX_PATH_WORDS.has(lastNoExt)) {
    return `last path segment "${last}" is a generic index/landing word`
  }
  return null
}

async function checkUrl(url: string, usedBy: string[]): Promise<CheckResult> {
  const indexLike = indexLikeReason(url)
  try {
    const controller = new AbortController()
    const timer = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS)
    const response = await fetch(url, {
      method: 'GET',
      redirect: 'follow',
      headers: { 'User-Agent': USER_AGENT },
      signal: controller.signal,
    })
    clearTimeout(timer)
    return { url, usedBy, status: response.status, error: null, indexLike }
  } catch (error) {
    return { url, usedBy, status: null, error: error instanceof Error ? error.message : String(error), indexLike }
  }
}

async function main() {
  const byUrl = new Map<string, string[]>()
  for (const record of evidenceRecords) {
    if (!record.canonicalUrl) continue
    const ids = byUrl.get(record.canonicalUrl) ?? []
    ids.push(record.id)
    byUrl.set(record.canonicalUrl, ids)
  }

  const urls = Array.from(byUrl.entries())
  console.log(`check:links — checking ${urls.length} distinct source URL(s) from ${evidenceRecords.length} evidence record(s)\n`)

  const results: CheckResult[] = []
  for (const [index, [url, usedBy]] of urls.entries()) {
    if (index > 0) await sleep(REQUEST_INTERVAL_MS)
    const result = await checkUrl(url, usedBy)
    results.push(result)
    const statusLabel = result.status !== null ? String(result.status) : `ERROR (${result.error})`
    console.log(`${statusLabel.padEnd(20)} ${url}`)
  }

  const nonOk = results.filter((r) => r.status === null || r.status < 200 || r.status >= 300)
  const indexLike = results.filter((r) => r.indexLike !== null)

  console.log(`\n${'-'.repeat(60)}`)
  console.log(`\nNon-200 responses: ${nonOk.length}`)
  for (const r of nonOk) {
    console.log(`  ${r.status ?? 'ERROR'}  ${r.url}`)
    console.log(`    cited by: ${r.usedBy.join(', ')}`)
    if (r.error) console.log(`    error: ${r.error}`)
  }

  console.log(`\nIndex/landing-page-like URLs: ${indexLike.length}`)
  for (const r of indexLike) {
    console.log(`  ${r.url}`)
    console.log(`    reason: ${r.indexLike}`)
    console.log(`    cited by: ${r.usedBy.join(', ')}`)
  }

  console.log(`\ncheck:links done — ${urls.length} checked, ${nonOk.length} non-200, ${indexLike.length} index-like`)
}

main().catch((error) => {
  console.error(error)
  process.exit(1)
})
