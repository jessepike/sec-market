/**
 * Post-build dist verification (spec §6, check 11).
 *
 * Runs last in `npm run build`, after generate-feed.ts. Checks the emitted
 * files themselves rather than the data that produced them — verify-issue.ts
 * owns the data checks, this owns "did the build actually write what it was
 * supposed to write."
 *
 * Every check below is exported as `(distDir, issuesList) => CheckResult`
 * rather than reading module-level `dist`/`issues` constants directly, so
 * tests/dist-fixtures.test.ts can run the real writers (generate-feed.ts)
 * into a temporary directory for a small fixture and then run these same
 * checks against that directory — the real dist pipeline, not a stand-in.
 */
import assert from 'node:assert/strict'
import { existsSync, readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'
import {
  archiveEntriesNewestFirst,
  feedIssuesNewestFirst,
  issueEvidenceIds,
  toRfc822,
} from '../src/data/issueHelpers.ts'
import { issues } from '../src/data/issues/index.ts'
import { SITE_URL } from '../src/data/meta.ts'
import { routesFor } from '../src/data/routes.ts'
import type { Issue } from '../src/data/types.ts'

const webRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const SOURCE_LOCK_PATH = resolve(webRoot, 'src/data/issues/issues.lock.json')

export interface CheckResult {
  name: string
  pass: boolean
  detail?: string
}

function runCheck(name: string, fn: () => string | void): CheckResult {
  try {
    const detail = fn()
    return { name, pass: true, detail: detail ?? undefined }
  } catch (error) {
    const detail = error instanceof Error ? error.message : String(error)
    return { name, pass: false, detail }
  }
}

function routeHtmlPath(distDir: string, path: string): string {
  return path === '/' ? resolve(distDir, 'index.html') : resolve(distDir, path.replace(/^\//, ''), 'index.html')
}

// --- 11a: every route's HTML file exists ------------------------------------

export function checkEveryRouteHtmlExists(distDir: string, issuesList: Issue[]): CheckResult {
  return runCheck('11a every-route-html-exists', () => {
    const routesList = routesFor(issuesList)
    for (const routeEntry of routesList) {
      const path = routeHtmlPath(distDir, routeEntry.path)
      if (!existsSync(path)) {
        throw new Error(`route "${routeEntry.path}" is missing its HTML file at ${path}`)
      }
    }
    return `${routesList.length} route HTML file(s) present`
  })
}

// --- 11b: every issue JSON copy exists, is well-formed, and identity-checked

export function checkEveryIssueJsonExists(distDir: string, issuesList: Issue[]): CheckResult {
  return runCheck('11b every-issue-json-exists', () => {
    for (const issue of issuesList) {
      const path = resolve(distDir, 'issues', `${issue.id}.json`)
      if (!existsSync(path)) {
        throw new Error(`issue "${issue.id}" is missing its JSON copy at ${path}`)
      }
      const parsed = JSON.parse(readFileSync(path, 'utf8'))
      if (!parsed.issue || !Array.isArray(parsed.evidence)) {
        throw new Error(`issue "${issue.id}" JSON copy does not have the shape { issue, evidence: [] }`)
      }
      if (parsed.issue.id !== issue.id) {
        throw new Error(
          `dist/issues/${issue.id}.json has issue.id "${parsed.issue.id}", expected "${issue.id}" (from the filename)`,
        )
      }
      // Full identity: the written "issue" object must deep-equal the source
      // issue (round-tripped through JSON so `undefined`-free comparison
      // matches what was actually written) — not just its id and evidence
      // count.
      const expectedIssue = JSON.parse(JSON.stringify(issue))
      try {
        assert.deepStrictEqual(parsed.issue, expectedIssue)
      } catch (error) {
        throw new Error(
          `dist/issues/${issue.id}.json "issue" does not deep-equal the source issue: ${
            error instanceof Error ? error.message : String(error)
          }`,
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
    return `${issuesList.length} issue JSON file(s) present, well-formed, and identity-checked`
  })
}

// --- 11c: issues/index.json exists, ordered, and row-identical -------------

export function checkIssuesIndexJsonExists(distDir: string, issuesList: Issue[]): CheckResult {
  return runCheck('11c issues-index-json-exists', () => {
    const path = resolve(distDir, 'issues/index.json')
    if (!existsSync(path)) {
      throw new Error(`dist/issues/index.json is missing`)
    }
    const parsed = JSON.parse(readFileSync(path, 'utf8'))
    if (!Array.isArray(parsed)) {
      throw new Error('dist/issues/index.json does not parse to an array')
    }
    if (parsed.length !== issuesList.length) {
      throw new Error(`dist/issues/index.json has ${parsed.length} entries, expected ${issuesList.length}`)
    }
    // The archive is newest-first; check the full expected row (whatever
    // fields the writer emits, url included), not just id and status.
    const expectedOrder = archiveEntriesNewestFirst(issuesList).map((entry) => ({
      ...entry,
      url: `${SITE_URL}/issues/${entry.id}/`,
    }))
    for (let i = 0; i < expectedOrder.length; i++) {
      try {
        assert.deepStrictEqual(parsed[i], expectedOrder[i])
      } catch (error) {
        throw new Error(
          `dist/issues/index.json entry ${i} does not deep-equal the expected row: ${
            error instanceof Error ? error.message : String(error)
          }`,
        )
      }
    }
    return `${parsed.length} entries in the expected newest-first order, full row identity checked`
  })
}

// --- 11d: feed.xml exists, parses, and every item is identity-checked ------

interface FeedItem {
  guid: string
  pubDate: string
}

/**
 * A deliberately narrow, tolerant RSS item extractor — not a general XML
 * parser. No XML-parsing package is present in node_modules, and
 * generate-feed.ts's own output has a fixed, simple shape with no CDATA
 * inside <item>, so a boundary-tracking scan is enough to check what this
 * gate needs. Unlike a naive `<item>[\s\S]*?<\/item>` regex — which silently
 * truncates at the FIRST `</item>` it finds, mis-extracting a block that
 * contains a nested `<item>` — this tracks open/close depth explicitly and
 * throws on a nested `<item>` or an unbalanced tag, rather than returning a
 * quietly-wrong block.
 */
function extractFeedItems(xml: string): FeedItem[] {
  const tagPattern = /<(\/?)item>/g
  const blocks: string[] = []
  let depth = 0
  let blockStart = -1
  let match: RegExpExecArray | null
  while ((match = tagPattern.exec(xml)) !== null) {
    const closing = match[1] === '/'
    if (!closing) {
      depth++
      if (depth > 1) {
        throw new Error(`dist/feed.xml has a nested <item> at character ${match.index} — not well-formed`)
      }
      blockStart = match.index
    } else {
      depth--
      if (depth < 0) {
        throw new Error(`dist/feed.xml has an unmatched </item> at character ${match.index} — not well-formed`)
      }
      blocks.push(xml.slice(blockStart, match.index + '</item>'.length))
    }
  }
  if (depth !== 0) {
    throw new Error(`dist/feed.xml has ${depth} unclosed <item> tag(s) — not well-formed`)
  }
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

export function checkFeedXmlExistsAndParses(distDir: string, issuesList: Issue[]): CheckResult {
  return runCheck('11d feed-xml-exists-and-parses', () => {
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

    const publishedIssues = feedIssuesNewestFirst(issuesList)
    const parsedItems = extractFeedItems(xml) // throws on a nested/unbalanced <item>

    if (parsedItems.length !== publishedIssues.length) {
      throw new Error(
        `dist/feed.xml has ${parsedItems.length} <item> element(s), expected exactly one per published issue (${publishedIssues.length})`,
      )
    }

    const issueById = new Map(issuesList.map((issue) => [issue.id, issue]))
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

    // Map each item's guid back to its issue and require the pubDate to
    // equal the RFC 822 form of that issue's published date — not merely a
    // syntactically valid RFC 822 string.
    for (const item of parsedItems) {
      const idMatch = item.guid.match(/\/issues\/([^/]+)\/$/)
      const issue = idMatch ? issueById.get(idMatch[1]) : undefined
      if (!issue) {
        throw new Error(`dist/feed.xml item guid "${item.guid}" does not map to a known issue id`)
      }
      if (issue.published === null) {
        throw new Error(`dist/feed.xml item guid "${item.guid}" maps to issue "${issue.id}", which has no published date`)
      }
      const expectedPubDate = toRfc822(issue.published)
      if (item.pubDate !== expectedPubDate) {
        throw new Error(
          `dist/feed.xml item "${item.guid}" pubDate is "${item.pubDate}", expected "${expectedPubDate}" ` +
            `(the RFC 822 form of issue "${issue.id}"'s published date "${issue.published}")`,
        )
      }
    }

    return `${parsedItems.length} <item>(s), guid set and per-item pubDate verified against their issue's published date`
  })
}

// --- 11e: sitemap.xml lists every route -------------------------------------

export function checkSitemapXmlListsEveryRoute(distDir: string, issuesList: Issue[]): CheckResult {
  return runCheck('11e sitemap-xml-lists-every-route', () => {
    const path = resolve(distDir, 'sitemap.xml')
    if (!existsSync(path)) {
      throw new Error('dist/sitemap.xml is missing')
    }
    const xml = readFileSync(path, 'utf8')
    if (!xml.includes('<urlset')) {
      throw new Error('dist/sitemap.xml is not a well-formed sitemap document')
    }
    const routesList = routesFor(issuesList)
    for (const routeEntry of routesList) {
      const loc = `<loc>${SITE_URL}${routeEntry.path}</loc>`
      if (!xml.includes(loc)) {
        throw new Error(`dist/sitemap.xml is missing an entry for route "${routeEntry.path}" (${loc})`)
      }
    }
    return `${routesList.length} route(s) present in sitemap.xml`
  })
}

// --- 11f: dist/issues/lock.json equals the source manifest (G1b) -----------

export function checkLockJsonMatchesSource(distDir: string, sourceLockPath: string): CheckResult {
  return runCheck('11f issues-lock-json-matches-source', () => {
    const path = resolve(distDir, 'issues/lock.json')
    if (!existsSync(path)) {
      throw new Error('dist/issues/lock.json is missing')
    }
    const distRaw = readFileSync(path, 'utf8').trim()
    const distManifest: Record<string, string> = distRaw === '' ? {} : JSON.parse(distRaw)

    const sourceRaw = existsSync(sourceLockPath) ? readFileSync(sourceLockPath, 'utf8').trim() : ''
    const sourceManifest: Record<string, string> = sourceRaw === '' ? {} : JSON.parse(sourceRaw)

    try {
      assert.deepStrictEqual(distManifest, sourceManifest)
    } catch (error) {
      throw new Error(
        `dist/issues/lock.json does not equal the source manifest at ${sourceLockPath}: ${
          error instanceof Error ? error.message : String(error)
        }`,
      )
    }
    return `dist/issues/lock.json matches the source manifest exactly, ${Object.keys(distManifest).length} entr${
      Object.keys(distManifest).length === 1 ? 'y' : 'ies'
    }`
  })
}

// --- 11g: per-route description / og:description / twitter:description (G8)

const META_PATTERNS = {
  description: /<meta\s+name="description"\s+content="([^"]*)"/,
  ogDescription: /<meta\b[^>]*?property="og:description"[^>]*?content="([^"]*)"/,
  twitterDescription: /<meta\b[^>]*?name="twitter:description"[^>]*?content="([^"]*)"/,
} as const

type MetaKey = keyof typeof META_PATTERNS

/** Decodes the handful of entities scripts/prerender.ts's escapeHtmlAttr can produce. `&amp;` last so it cannot re-decode an entity this function just produced. */
function htmlUnescapeAttr(value: string): string {
  return value
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&apos;/g, "'")
    .replace(/&amp;/g, '&')
}

function readMetaDescriptions(html: string, routeLabel: string): Record<MetaKey, string> {
  const result = {} as Record<MetaKey, string>
  for (const key of Object.keys(META_PATTERNS) as MetaKey[]) {
    const match = html.match(META_PATTERNS[key])
    if (!match) {
      throw new Error(`route "${routeLabel}": could not find a ${key} meta tag`)
    }
    result[key] = htmlUnescapeAttr(match[1])
  }
  return result
}

const ARCHIVE_DESCRIPTION = 'Every Security Market Pulse weekly issue, newest first, with its permalink.'

/**
 * Every non-front route's description / og:description / twitter:description
 * must equal its expected route-specific text (the archive's fixed blurb, or
 * an issue permalink's `read`) — HTML-unescaped, since prerender.ts writes
 * the attribute-escaped form — and must differ from the front page's, which
 * keeps its own hand-authored head verbatim (scripts/prerender.ts's
 * rewriteHead skips the front route entirely).
 */
export function checkRouteDescriptionMeta(distDir: string, issuesList: Issue[]): CheckResult {
  return runCheck('11g route-description-meta-identity', () => {
    const frontPath = resolve(distDir, 'index.html')
    if (!existsSync(frontPath)) {
      throw new Error('dist/index.html is missing')
    }
    const front = readMetaDescriptions(readFileSync(frontPath, 'utf8'), '/')

    let checkedCount = 0

    function checkRoute(path: string, expectedText: string, label: string): void {
      if (!existsSync(path)) {
        throw new Error(`route "${label}": HTML file is missing at ${path}`)
      }
      const actual = readMetaDescriptions(readFileSync(path, 'utf8'), label)
      for (const key of Object.keys(META_PATTERNS) as MetaKey[]) {
        if (actual[key] !== expectedText) {
          throw new Error(`route "${label}" ${key} is "${actual[key]}", expected "${expectedText}"`)
        }
        if (actual[key] === front[key]) {
          throw new Error(
            `route "${label}" ${key} equals the front page's ${key} ("${front[key]}") — expected route-specific text`,
          )
        }
      }
      checkedCount++
    }

    checkRoute(resolve(distDir, 'issues/index.html'), ARCHIVE_DESCRIPTION, '/issues/')
    for (const issue of issuesList) {
      checkRoute(resolve(distDir, 'issues', issue.id, 'index.html'), issue.read, `/issues/${issue.id}/`)
    }

    return `front page description confirmed distinct; ${checkedCount} non-front route(s) verified (description, og:description, twitter:description)`
  })
}

// --- Script entry point: only runs when this file is executed directly -----

function isMainModule(): boolean {
  return process.argv[1] !== undefined && pathToFileURL(process.argv[1]).href === import.meta.url
}

const EXPECTED_CHECK_COUNT = 7

export function report(results: CheckResult[]): boolean {
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
  return anyFail
}

if (isMainModule()) {
  try {
    const distDir = resolve(webRoot, 'dist')
    const results = [
      checkEveryRouteHtmlExists(distDir, issues),
      checkEveryIssueJsonExists(distDir, issues),
      checkIssuesIndexJsonExists(distDir, issues),
      checkFeedXmlExistsAndParses(distDir, issues),
      checkSitemapXmlListsEveryRoute(distDir, issues),
      checkLockJsonMatchesSource(distDir, SOURCE_LOCK_PATH),
      checkRouteDescriptionMeta(distDir, issues),
    ]
    const anyFail = report(results)
    if (anyFail) {
      console.error('verify:dist FAILED')
      process.exit(1)
    }
    console.log('verify:dist passed')
  } catch (error) {
    const detail = error instanceof Error ? (error.stack ?? error.message) : String(error)
    console.error('verify:dist CRASHED before reaching a verdict:')
    console.error(detail)
    process.exit(1)
  }
}
