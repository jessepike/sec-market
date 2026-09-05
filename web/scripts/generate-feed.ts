/**
 * Build-time feed + JSON-copy step.
 *
 * Runs after scripts/generate-seo.ts, against dist/. Writes:
 *   - dist/feed.xml — RSS 2.0, one <item> per published issue (valid XML with
 *     zero items when none are published yet, as issue 2026-w36 is at launch).
 *   - dist/issues/<id>.json — { issue, evidence } for every issue, `evidence`
 *     holding every evidence record the issue cites (issueEvidenceIds already
 *     folds in weThink.thesis and, on a draft, proposed.thesis).
 *   - dist/issues/index.json — [{ id, weekEnding, published, status, read, url }].
 *   - dist/issues/lock.json — a public copy of src/data/issues/issues.lock.json,
 *     the append-only publication manifest. verify-issue.ts's check 8 fetches
 *     this file from the live site as its second history anchor (the first is
 *     git parent commits), so a build with no git history to compare against
 *     still has something to check append-only against. verify-dist.ts
 *     requires it to exist and equal the source file exactly.
 *
 * Also adds a feed-autodiscovery <link rel="alternate" type="application/
 * rss+xml"> to every emitted route's <head>.
 *
 * The four writers above (buildFeedXml/writeFeedXml, writeIssueJsonCopies,
 * writeIssuesIndexJson, writeLockManifestCopy) are exported and parameterised
 * by an issues array and an output directory, so tests/dist-fixtures.test.ts
 * can run the real writers against a fixture into a temp directory and then
 * run the real verify-dist.ts checks against that directory — instead of
 * only exercising the pure helpers underneath and hoping the writer that
 * calls them still agrees. The feed-autodiscovery injection below stays
 * script-only: it rewrites already-prerendered HTML, which a fixture test
 * has no reason to fabricate.
 */
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'
import { evidenceById } from '../src/data/evidence.ts'
import {
  archiveEntriesNewestFirst,
  feedIssuesNewestFirst,
  issueJsonCopy,
  toRfc822,
} from '../src/data/issueHelpers.ts'
import { issues } from '../src/data/issues/index.ts'
import { PRODUCT_TITLE, SITE_URL } from '../src/data/meta.ts'
import { routes, type RouteEntry } from '../src/data/routes.ts'
import type { EvidenceRecord, Issue } from '../src/data/types.ts'

const webRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const SOURCE_LOCK_PATH = resolve(webRoot, 'src/data/issues/issues.lock.json')

function fail(message: string): never {
  console.error(`generate-feed FAILED: ${message}`)
  process.exit(1)
}

function outPathFor(routeEntry: RouteEntry): string {
  return routeEntry.path === '/'
    ? resolve(webRoot, 'dist/index.html')
    : resolve(webRoot, 'dist', routeEntry.path.replace(/^\//, ''), 'index.html')
}

/** Escapes text for inclusion in XML character data. */
function xmlEscape(text: string): string {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;')
}

// --- Pure writers: issues + an output directory in, files out ---------------

/** The RSS 2.0 document `dist/feed.xml` holds — one `<item>` per published issue. */
export function buildFeedXml(issuesList: Issue[]): string {
  const publishedIssues = feedIssuesNewestFirst(issuesList)

  const items = publishedIssues
    .map((issue) => {
      const url = `${SITE_URL}/issues/${issue.id}/`
      return `    <item>
      <title>${xmlEscape(`Issue ${issue.id}`)}</title>
      <link>${url}</link>
      <guid isPermaLink="true">${url}</guid>
      <pubDate>${toRfc822(issue.published!)}</pubDate>
      <description>${xmlEscape(issue.read)}</description>
    </item>`
    })
    .join('\n')

  return `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>${xmlEscape(PRODUCT_TITLE)}</title>
    <link>${SITE_URL}/</link>
    <description>${xmlEscape('Weekly issues of the Security Market Pulse, one per ISO week.')}</description>
    <language>en-us</language>
${items}
  </channel>
</rss>
`
}

export function writeFeedXml(issuesList: Issue[], distDir: string): { path: string; itemCount: number } {
  const feed = buildFeedXml(issuesList)
  const path = resolve(distDir, 'feed.xml')
  writeFileSync(path, feed)
  return { path, itemCount: feedIssuesNewestFirst(issuesList).length }
}

/** Writes dist/issues/<id>.json for every issue. Throws (does not exit) on an unresolved evidence id. */
export function writeIssueJsonCopies(
  issuesList: Issue[],
  evidenceByIdMap: Record<string, EvidenceRecord>,
  distDir: string,
): string[] {
  mkdirSync(resolve(distDir, 'issues'), { recursive: true })
  const written: string[] = []
  for (const issue of issuesList) {
    const payload = issueJsonCopy(issue, evidenceByIdMap)
    const path = resolve(distDir, 'issues', `${issue.id}.json`)
    writeFileSync(path, JSON.stringify(payload, null, 2))
    written.push(path)
  }
  return written
}

export function writeIssuesIndexJson(issuesList: Issue[], distDir: string): { path: string; count: number } {
  const indexPayload = archiveEntriesNewestFirst(issuesList).map((entry) => ({
    ...entry,
    url: `${SITE_URL}/issues/${entry.id}/`,
  }))
  const path = resolve(distDir, 'issues/index.json')
  writeFileSync(path, JSON.stringify(indexPayload, null, 2))
  return { path, count: indexPayload.length }
}

/**
 * Copies the source lock manifest to dist/issues/lock.json verbatim (an
 * empty file or a missing file both become `{}`), so verify-dist.ts can
 * require the copy to equal the source, and so the live site serves it for
 * verify-issue.ts's network append-only anchor.
 */
export function writeLockManifestCopy(distDir: string, sourceLockPath: string): { path: string; entryCount: number } {
  const raw = existsSync(sourceLockPath) ? readFileSync(sourceLockPath, 'utf8').trim() : ''
  const manifest: Record<string, string> = raw === '' ? {} : JSON.parse(raw)
  mkdirSync(resolve(distDir, 'issues'), { recursive: true })
  const path = resolve(distDir, 'issues/lock.json')
  writeFileSync(path, `${JSON.stringify(manifest, null, 2)}\n`)
  return { path, entryCount: Object.keys(manifest).length }
}

// --- Script entry point: only runs when this file is executed directly -----

function isMainModule(): boolean {
  return process.argv[1] !== undefined && pathToFileURL(process.argv[1]).href === import.meta.url
}

if (isMainModule()) {
  const distDir = resolve(webRoot, 'dist')

  let feedResult: { path: string; itemCount: number }
  try {
    feedResult = writeFeedXml(issues, distDir)
  } catch (error) {
    fail(error instanceof Error ? error.message : String(error))
  }
  console.log(`generate-feed OK: dist/feed.xml written with ${feedResult.itemCount} item(s).`)

  let jsonPaths: string[]
  try {
    jsonPaths = writeIssueJsonCopies(issues, evidenceById, distDir)
  } catch (error) {
    fail(error instanceof Error ? error.message : String(error))
  }
  console.log(`generate-feed OK: wrote ${jsonPaths.length} dist/issues/<id>.json file(s).`)

  const indexResult = writeIssuesIndexJson(issues, distDir)
  console.log(
    `generate-feed OK: wrote dist/issues/index.json with ${indexResult.count} entr${indexResult.count === 1 ? 'y' : 'ies'}.`,
  )

  const lockResult = writeLockManifestCopy(distDir, SOURCE_LOCK_PATH)
  console.log(
    `generate-feed OK: wrote dist/issues/lock.json with ${lockResult.entryCount} entr${lockResult.entryCount === 1 ? 'y' : 'ies'}.`,
  )

  // --- feed autodiscovery link, every route ------------------------------

  for (const routeEntry of routes) {
    const outPath = outPathFor(routeEntry)
    const html = readFileSync(outPath, 'utf8')

    if (html.includes('type="application/rss+xml"')) {
      fail(`route "${routeEntry.path}" already has an rss+xml alternate link; refusing to add a second one.`)
    }

    const headCloseCount = html.split('</head>').length - 1
    if (headCloseCount !== 1) {
      fail(`route "${routeEntry.path}": expected exactly one head-closing tag, found ${headCloseCount}.`)
    }

    const linkTag = `    <link rel="alternate" type="application/rss+xml" title="${xmlEscape(PRODUCT_TITLE)}" href="${SITE_URL}/feed.xml" />\n  `
    const nextHtml = html.replace('</head>', () => `${linkTag}</head>`)
    writeFileSync(outPath, nextHtml)
  }

  console.log(`generate-feed OK: added feed-autodiscovery link to ${routes.length} route(s).`)
}
