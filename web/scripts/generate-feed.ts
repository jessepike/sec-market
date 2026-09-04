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
 *
 * Also adds a feed-autodiscovery <link rel="alternate" type="application/
 * rss+xml"> to every emitted route's <head>.
 */
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { evidenceById } from '../src/data/evidence.ts'
import { archiveEntriesNewestFirst, feedIssuesNewestFirst, issueJsonCopy } from '../src/data/issueHelpers.ts'
import { issues } from '../src/data/issues/index.ts'
import { PRODUCT_TITLE, SITE_URL } from '../src/data/meta.ts'
import { routes, type RouteEntry } from '../src/data/routes.ts'

const webRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..')

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

/** ISO calendar date -> RFC 822 date-time, as RSS pubDate requires. */
function toRfc822(isoDate: string): string {
  const date = new Date(`${isoDate}T00:00:00Z`)
  if (Number.isNaN(date.getTime())) {
    fail(`published date "${isoDate}" does not convert to a valid Date for pubDate`)
  }
  return date.toUTCString()
}

// --- feed.xml -----------------------------------------------------------

const publishedIssues = feedIssuesNewestFirst(issues)

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

const feed = `<?xml version="1.0" encoding="UTF-8"?>
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

writeFileSync(resolve(webRoot, 'dist/feed.xml'), feed)
console.log(`generate-feed OK: dist/feed.xml written with ${publishedIssues.length} item(s).`)

// --- issues/<id>.json -----------------------------------------------------

mkdirSync(resolve(webRoot, 'dist/issues'), { recursive: true })

for (const issue of issues) {
  let payload: { issue: typeof issue; evidence: unknown[] }
  try {
    payload = issueJsonCopy(issue, evidenceById)
  } catch (error) {
    fail(error instanceof Error ? error.message : String(error))
  }
  writeFileSync(
    resolve(webRoot, 'dist/issues', `${issue.id}.json`),
    JSON.stringify(payload, null, 2),
  )
}

console.log(`generate-feed OK: wrote ${issues.length} dist/issues/<id>.json file(s).`)

// --- issues/index.json ------------------------------------------------------

const indexPayload = archiveEntriesNewestFirst(issues).map((entry) => ({
  ...entry,
  url: `${SITE_URL}/issues/${entry.id}/`,
}))

writeFileSync(
  resolve(webRoot, 'dist/issues/index.json'),
  JSON.stringify(indexPayload, null, 2),
)

console.log(`generate-feed OK: wrote dist/issues/index.json with ${indexPayload.length} entr${indexPayload.length === 1 ? 'y' : 'ies'}.`)

// --- feed autodiscovery link, every route ------------------------------------

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
