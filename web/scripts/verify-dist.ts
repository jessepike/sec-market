/**
 * Post-build dist verification (spec §6, check 11).
 *
 * Runs last in `npm run build`, after generate-feed.ts. Checks the emitted
 * files themselves rather than the data that produced them — verify-issue.ts
 * owns the data checks, this owns "did the build actually write what it was
 * supposed to write."
 */
import { existsSync, readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { archiveEntriesNewestFirst, feedIssuesNewestFirst, issueEvidenceIds } from '../src/data/issueHelpers.ts'
import { issues } from '../src/data/issues/index.ts'
import { SITE_URL } from '../src/data/meta.ts'
import { routes } from '../src/data/routes.ts'

const webRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const distDir = resolve(webRoot, 'dist')

interface CheckResult {
  name: string
  pass: boolean
  detail?: string
}

const results: CheckResult[] = []

function check(name: string, fn: () => string | void): void {
  try {
    const detail = fn()
    results.push({ name, pass: true, detail: detail ?? undefined })
  } catch (error) {
    const detail = error instanceof Error ? error.message : String(error)
    results.push({ name, pass: false, detail })
  }
}

function routeHtmlPath(path: string): string {
  return path === '/' ? resolve(distDir, 'index.html') : resolve(distDir, path.replace(/^\//, ''), 'index.html')
}

check('11a every-route-html-exists', () => {
  for (const routeEntry of routes) {
    const path = routeHtmlPath(routeEntry.path)
    if (!existsSync(path)) {
      throw new Error(`route "${routeEntry.path}" is missing its HTML file at ${path}`)
    }
  }
  return `${routes.length} route HTML file(s) present`
})

check('11b every-issue-json-exists', () => {
  for (const issue of issues) {
    const path = resolve(distDir, 'issues', `${issue.id}.json`)
    if (!existsSync(path)) {
      throw new Error(`issue "${issue.id}" is missing its JSON copy at ${path}`)
    }
    const parsed = JSON.parse(readFileSync(path, 'utf8'))
    if (!parsed.issue || !Array.isArray(parsed.evidence)) {
      throw new Error(`issue "${issue.id}" JSON copy does not have the shape { issue, evidence: [] }`)
    }
    // Identity: the id inside the file must match the id in its own
    // filename, and the evidence array must be exactly the set of ids the
    // issue cites — via issueEvidenceIds, the same helper the site's own
    // evidence drawer and generate-feed.ts's issueJsonCopy use — not merely
    // a non-empty array that happens to be the right length.
    if (parsed.issue.id !== issue.id) {
      throw new Error(
        `dist/issues/${issue.id}.json has issue.id "${parsed.issue.id}", expected "${issue.id}" (from the filename)`,
      )
    }
    const expectedEvidenceIds = new Set(issueEvidenceIds(issue))
    const actualEvidenceIds = new Set(
      (parsed.evidence as Array<{ id: string }>).map((record) => record.id),
    )
    const missing = [...expectedEvidenceIds].filter((id) => !actualEvidenceIds.has(id))
    const extra = [...actualEvidenceIds].filter((id) => !expectedEvidenceIds.has(id))
    if (missing.length > 0 || extra.length > 0) {
      throw new Error(
        `dist/issues/${issue.id}.json evidence ids do not equal the issue's cited ids — ` +
          `missing: [${missing.join(', ')}], extra: [${extra.join(', ')}]`,
      )
    }
  }
  return `${issues.length} issue JSON file(s) present, well-formed, and identity-checked`
})

check('11c issues-index-json-exists', () => {
  const path = resolve(distDir, 'issues/index.json')
  if (!existsSync(path)) {
    throw new Error(`dist/issues/index.json is missing`)
  }
  const parsed = JSON.parse(readFileSync(path, 'utf8'))
  if (!Array.isArray(parsed)) {
    throw new Error('dist/issues/index.json does not parse to an array')
  }
  if (parsed.length !== issues.length) {
    throw new Error(`dist/issues/index.json has ${parsed.length} entries, expected ${issues.length}`)
  }
  // The archive is newest-first; check the exact ordered id/status sequence,
  // not just the count, using the same helper generate-feed.ts writes from.
  const expectedOrder = archiveEntriesNewestFirst(issues)
  for (let i = 0; i < expectedOrder.length; i++) {
    const actual = parsed[i] as { id?: string; status?: string }
    const expected = expectedOrder[i]
    if (actual?.id !== expected.id || actual?.status !== expected.status) {
      throw new Error(
        `dist/issues/index.json entry ${i} is {id: "${actual?.id}", status: "${actual?.status}"}, ` +
          `expected {id: "${expected.id}", status: "${expected.status}"} (newest first)`,
      )
    }
  }
  return `${parsed.length} entries in the expected newest-first order`
})

/** One RSS <item>'s guid and pubDate, as extracted by the tolerant parser below. */
interface FeedItem {
  guid: string
  pubDate: string
}

/**
 * A deliberately narrow, tolerant RSS item extractor — not a general XML
 * parser. No XML-parsing package is present in node_modules (checked before
 * writing this), and generate-feed.ts's own output has a fixed, simple shape
 * with no CDATA or nested markup inside <item>, so a block-then-tag regex
 * extraction is sufficient to check what this gate needs: every item's guid
 * and pubDate. It throws rather than silently producing a short list if an
 * <item> block is missing either tag.
 */
function extractFeedItems(xml: string): FeedItem[] {
  const blocks = xml.match(/<item>[\s\S]*?<\/item>/g) ?? []
  return blocks.map((block, index) => {
    const guidMatch = block.match(/<guid[^>]*>([^<]*)<\/guid>/)
    const pubDateMatch = block.match(/<pubDate>([^<]*)<\/pubDate>/)
    if (!guidMatch) {
      throw new Error(`dist/feed.xml <item> block ${index} has no <guid>`)
    }
    if (!pubDateMatch) {
      throw new Error(`dist/feed.xml <item> block ${index} has no <pubDate>`)
    }
    return { guid: guidMatch[1], pubDate: pubDateMatch[1] }
  })
}

// RFC 822 as Date.prototype.toUTCString() produces it: "Sun, 06 Sep 2026 00:00:00 GMT".
const RFC_822_PATTERN = /^[A-Za-z]{3}, \d{2} [A-Za-z]{3} \d{4} \d{2}:\d{2}:\d{2} GMT$/

check('11d feed-xml-exists-and-parses', () => {
  const path = resolve(distDir, 'feed.xml')
  if (!existsSync(path)) {
    throw new Error('dist/feed.xml is missing')
  }
  const xml = readFileSync(path, 'utf8')
  if (!xml.startsWith('<?xml')) {
    throw new Error('dist/feed.xml does not start with an XML declaration')
  }
  if (!xml.includes('<rss version="2.0">') || !xml.includes('</rss>')) {
    throw new Error('dist/feed.xml is not a well-formed RSS 2.0 document')
  }
  const openTags = (xml.match(/<item>/g) ?? []).length
  const closeTags = (xml.match(/<\/item>/g) ?? []).length
  if (openTags !== closeTags) {
    throw new Error(`dist/feed.xml has ${openTags} <item> and ${closeTags} </item> — not well-formed`)
  }

  const publishedIssues = feedIssuesNewestFirst(issues)
  if (openTags !== publishedIssues.length) {
    throw new Error(
      `dist/feed.xml has ${openTags} <item> element(s), expected exactly one per published issue (${publishedIssues.length})`,
    )
  }

  const parsedItems = extractFeedItems(xml)

  const expectedGuids = new Set(publishedIssues.map((issue) => `${SITE_URL}/issues/${issue.id}/`))
  const actualGuids = new Set(parsedItems.map((item) => item.guid))
  const missingGuids = [...expectedGuids].filter((guid) => !actualGuids.has(guid))
  const extraGuids = [...actualGuids].filter((guid) => !expectedGuids.has(guid))
  if (missingGuids.length > 0 || extraGuids.length > 0) {
    throw new Error(
      `dist/feed.xml guid set does not equal the set of published issue permalinks — ` +
        `missing: [${missingGuids.join(', ')}], extra: [${extraGuids.join(', ')}]`,
    )
  }

  for (const item of parsedItems) {
    const parsedDate = new Date(item.pubDate)
    if (Number.isNaN(parsedDate.getTime()) || !RFC_822_PATTERN.test(item.pubDate)) {
      throw new Error(`dist/feed.xml item "${item.guid}" has an invalid RFC 822 pubDate "${item.pubDate}"`)
    }
  }

  return `${parsedItems.length} <item>(s), guid set and pubDate format verified`
})

check('11e sitemap-xml-lists-every-route', () => {
  const path = resolve(distDir, 'sitemap.xml')
  if (!existsSync(path)) {
    throw new Error('dist/sitemap.xml is missing')
  }
  const xml = readFileSync(path, 'utf8')
  if (!xml.includes('<urlset')) {
    throw new Error('dist/sitemap.xml is not a well-formed sitemap document')
  }
  for (const routeEntry of routes) {
    const loc = `<loc>https://securitymarketpulse.com${routeEntry.path}</loc>`
    if (!xml.includes(loc)) {
      throw new Error(`dist/sitemap.xml is missing an entry for route "${routeEntry.path}" (${loc})`)
    }
  }
  return `${routes.length} route(s) present in sitemap.xml`
})

const EXPECTED_CHECK_COUNT = 5

function report(): void {
  if (results.length !== EXPECTED_CHECK_COUNT) {
    throw new Error(
      `expected ${EXPECTED_CHECK_COUNT} check results, got ${results.length} — the run did not reach a verdict`,
    )
  }

  let anyFail = false
  for (const result of results) {
    if (result.pass) {
      console.log(`PASS  ${result.name}${result.detail ? ` — ${result.detail}` : ''}`)
    } else {
      anyFail = true
      console.error(`FAIL  ${result.name} — ${result.detail}`)
    }
  }

  if (anyFail) {
    console.error('verify:dist FAILED')
    process.exit(1)
  }

  console.log('verify:dist passed')
}

try {
  report()
} catch (error) {
  const detail = error instanceof Error ? (error.stack ?? error.message) : String(error)
  console.error('verify:dist CRASHED before reaching a verdict:')
  console.error(detail)
  process.exit(1)
}
