import refreshCoverage from '../src/data/generated/refreshCoverage.json' with { type: 'json' }
import refreshPublication from '../src/data/generated/refreshPublication.json' with { type: 'json' }
import refreshVerification from '../src/data/generated/refreshVerification.json' with { type: 'json' }
import refreshContract from '../src/data/tracker/refreshContract.json' with { type: 'json' }
import dailyMarket from '../src/data/generated/dailyMarket.json' with { type: 'json' }
/**
 * Build-time feed + JSON-copy step.
 *
 * Runs after scripts/generate-seo.ts, against dist/. Writes:
 *   - dist/feed.xml — RSS 2.0, one <item> per published issue (valid XML with
 *     zero items when none are published yet, as issue 2026-w36 is at launch),
 *     plus one <item> per published correction (SEC-MARKET-FABLE-001 T6-13).
 *   - dist/issues/<id>.json — { issue, evidence, corrections } for every
 *     issue, `evidence` holding every evidence record the issue cites
 *     (issueEvidenceIds already folds in weThink.thesis and, on a draft,
 *     proposed.thesis), `corrections` holding any corrections that apply to
 *     that issue as a sibling field — the hashed `issue` object is untouched.
 *   - dist/issues/index.json — [{ id, weekEnding, published, status, read, url }].
 *   - dist/issues/lock.json — a public copy of src/data/issues/issues.lock.json,
 *     the append-only publication manifest. verify-issue.ts's check 8 fetches
 *     this file from the live site as its second history anchor (the first is
 *     git parent commits), so a build with no git history to compare against
 *     still has something to check append-only against. verify-dist.ts
 *     requires it to exist and equal the source file exactly.
 *   - dist/corrections.json — every correction, newest first, in the shape
 *     src/data/correctionHelpers.ts's correctionsJsonPayload builds.
 *   - dist/tracker.json — run status, domains, suppliers, and every tracker
 *     figure (headline metric, revenue reading, last funding round,
 *     ownership fact) with a stable id/value/period/source URL, in the
 *     shape src/data/tracker/jsonExport.ts's trackerJsonPayload builds
 *     (AUTO-001 fix pass 4, item 10).
 *
 * Also adds a feed-autodiscovery <link rel="alternate" type="application/
 * rss+xml"> to every emitted route's <head>.
 *
 * The writers above (buildFeedXml/writeFeedXml, writeIssueJsonCopies,
 * writeIssuesIndexJson, writeLockManifestCopy, writeCorrectionsJson) are
 * exported and parameterised by an issues array and an output directory, so
 * tests/dist-fixtures.test.ts can run the real writers against a fixture
 * into a temp directory and then run the real verify-dist.ts checks against
 * that directory — instead of only exercising the pure helpers underneath
 * and hoping the writer that calls them still agrees. The feed-autodiscovery
 * injection below stays script-only: it rewrites already-prerendered HTML,
 * which a fixture test has no reason to fabricate.
 */
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'
import { correctionsNewestFirst } from '../src/data/correctionHelpers.ts'
import { emptyCorrectionHistorySources, factualCorrectionFeedText, factualCorrectionHistory, publicCorrectionsJsonPayload } from '../src/data/factualCorrectionHelpers.ts'
import type { CorrectionHistorySources } from '../src/data/factualCorrectionHelpers.ts'
import { factualCorrectionBundle, factualCorrectionGroups, factualCorrectionSourceEvidenceIds } from '../src/data/tracker/correctionData.ts'
import type { FactualCorrectionBundle, FactualCorrectionGroup } from '../src/data/tracker/factualCorrections.ts'
import { corrections } from '../src/data/corrections.ts'
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
import { runStatus } from '../src/data/runStatus.ts'
import { trackerDomains } from '../src/data/tracker/domains.ts'
import { trackerJsonPayload } from '../src/data/tracker/jsonExport.ts'
import { trackerSuppliers } from '../src/data/tracker/suppliers.ts'
import { trackerEvents } from '../src/data/tracker/events.ts'
import { isCertifiedEvent } from '../src/data/tracker/certification.ts'
import { writeAgentFiles } from './generate-agent.ts'
import type { Correction, EvidenceRecord, Issue } from '../src/data/types.ts'
import type { RunStatus } from '../src/data/runStatus.ts'
import type { TrackerDomain } from '../src/data/tracker/domains.ts'
import type { TrackerSupplier } from '../src/data/tracker/suppliers.ts'

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

/**
 * The RSS 2.0 document `dist/feed.xml` holds — one `<item>` per published
 * issue, plus one `<item>` per correction (`correctionsList`, defaulting to
 * none). Correction items are appended after issue items and use
 * `isPermaLink="false"` since their guid is an anchor on `/corrections/`,
 * not a standalone resource of its own.
 */
export function buildFeedXml(issuesList: Issue[], correctionsList: Correction[] = [], factualGroups: readonly FactualCorrectionGroup[] = [], sources: CorrectionHistorySources = emptyCorrectionHistorySources): string {
  const publishedIssues = feedIssuesNewestFirst(issuesList)

  const issueItems = publishedIssues.map((issue) => {
    const url = `${SITE_URL}/issues/${issue.id}/`
    return `    <item>
      <title>${xmlEscape(`Issue ${issue.id}`)}</title>
      <link>${url}</link>
      <guid isPermaLink="true">${url}</guid>
      <pubDate>${toRfc822(issue.published!)}</pubDate>
      <description>${xmlEscape(issue.read)}</description>
    </item>`
  })

  const correctionItems = correctionsNewestFirst(correctionsList).map((correction) => {
    const url = `${SITE_URL}/corrections/#${correction.id}`
    const title = correction.issueId
      ? `Correction — issue ${correction.issueId}`
      : 'Correction — standing reference'
    return `    <item>
      <title>${xmlEscape(title)}</title>
      <link>${url}</link>
      <guid isPermaLink="false">${url}</guid>
      <pubDate>${toRfc822(correction.date)}</pubDate>
      <description>${xmlEscape(correction.text)}</description>
    </item>`
  })

  const factualItems = factualCorrectionHistory(factualGroups, sources, SITE_URL).map((entry) => `    <item>
      <title>${xmlEscape(`Source-verified factual correction: ${entry.supplierName}`)}</title>
      <link>${xmlEscape(entry.url)}</link>
      <guid isPermaLink="false">${xmlEscape(entry.url)}</guid>
      <pubDate>${toRfc822(entry.date)}</pubDate>
      <description>${xmlEscape(factualCorrectionFeedText(entry))}</description>
    </item>`)
  const items = [...issueItems, ...correctionItems, ...factualItems].join('\n')

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

export function writeFeedXml(
  issuesList: Issue[],
  correctionsList: Correction[],
  distDir: string,
  factualGroups: readonly FactualCorrectionGroup[] = [],
  sources: CorrectionHistorySources = emptyCorrectionHistorySources,
): { path: string; itemCount: number } {
  const feed = buildFeedXml(issuesList, correctionsList, factualGroups, sources)
  const path = resolve(distDir, 'feed.xml')
  writeFileSync(path, feed)
  return { path, itemCount: feedIssuesNewestFirst(issuesList).length + correctionsList.length + factualGroups.length }
}

/**
 * Writes `dist/corrections.json` — every correction, newest first, in the
 * stable shape `correctionsJsonPayload` builds. Mirrors
 * `writeIssueJsonCopies` below: a pure payload builder in
 * src/data/correctionHelpers.ts, a thin writer here, and a matching checker
 * in verify-dist.ts, so the writer and its checker cannot compute the shape
 * two different ways.
 */
export function writeCorrectionsJson(
  correctionsList: Correction[],
  distDir: string,
  factualGroups: readonly FactualCorrectionGroup[] = [],
  sources: CorrectionHistorySources = emptyCorrectionHistorySources,
): { path: string; count: number } {
  const payload = publicCorrectionsJsonPayload(correctionsList, factualGroups, sources, SITE_URL)
  const path = resolve(distDir, 'corrections.json')
  writeFileSync(path, JSON.stringify(payload, null, 2))
  return { path, count: payload.length }
}

/** Full gate-produced projection, bound as a separate public release artifact. */
export function writeFactualCorrectionsJson(bundle: FactualCorrectionBundle, distDir: string): string {
  const path = resolve(distDir, 'factual-corrections.json')
  writeFileSync(path, JSON.stringify(bundle, null, 2) + '\n')
  return path
}

/** Writes dist/issues/<id>.json for every issue. Throws (does not exit) on an unresolved evidence id. */
export function writeIssueJsonCopies(
  issuesList: Issue[],
  evidenceByIdMap: Record<string, EvidenceRecord>,
  distDir: string,
  correctionsList: Correction[] = [],
): string[] {
  mkdirSync(resolve(distDir, 'issues'), { recursive: true })
  const written: string[] = []
  for (const issue of issuesList) {
    const payload = issueJsonCopy(issue, evidenceByIdMap, correctionsList)
    const path = resolve(distDir, 'issues', `${issue.id}.json`)
    writeFileSync(path, JSON.stringify(payload, null, 2))
    written.push(path)
  }
  return written
}

/**
 * Writes `dist/tracker.json` — run status, domains, suppliers, and every
 * tracker figure, in the stable shape `trackerJsonPayload` builds. Mirrors
 * `writeCorrectionsJson` above: a pure payload builder in
 * src/data/tracker/jsonExport.ts, a thin writer here, and a matching checker
 * in verify-dist.ts.
 */
export function writeTrackerJson(
  suppliers: TrackerSupplier[],
  domains: TrackerDomain[],
  evidenceByIdMap: Record<string, EvidenceRecord>,
  status: RunStatus,
  distDir: string,
): { path: string; figureCount: number } {
  const payload = trackerJsonPayload(suppliers, domains, evidenceByIdMap, status)
  writeFileSync(resolve(distDir, 'refresh-coverage.json'), JSON.stringify(refreshCoverage, null, 2) + '\n', 'utf8')
  writeFileSync(resolve(distDir, 'daily-coverage.json'), JSON.stringify(dailyMarket.enabled ? dailyMarket.coverage : { complete: false, checkedAt: null, reason: 'DAILY_COLLECTION_NOT_ACTIVATED' }, null, 2) + '\n', 'utf8')
  writeFileSync(resolve(distDir, 'refresh-publication.json'), JSON.stringify(refreshPublication, null, 2) + '\n', 'utf8')
  writeFileSync(resolve(distDir, 'refresh-certification.json'), JSON.stringify({ contract: refreshContract, verification: refreshVerification, publication: refreshPublication }, null, 2) + '\n', 'utf8')
  const path = resolve(distDir, 'tracker.json')
  writeFileSync(path, JSON.stringify(payload, null, 2))
  return { path, figureCount: payload.figures.length }
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
    feedResult = writeFeedXml(issues, corrections, distDir, factualCorrectionGroups, { evidence: evidenceById, suppliers: trackerSuppliers, groupEvidenceIds: factualCorrectionSourceEvidenceIds })
  } catch (error) {
    fail(error instanceof Error ? error.message : String(error))
  }
  console.log(`generate-feed OK: dist/feed.xml written with ${feedResult.itemCount} item(s).`)

  let jsonPaths: string[]
  try {
    jsonPaths = writeIssueJsonCopies(issues, evidenceById, distDir, corrections)
  } catch (error) {
    fail(error instanceof Error ? error.message : String(error))
  }
  console.log(`generate-feed OK: wrote ${jsonPaths.length} dist/issues/<id>.json file(s).`)

  const correctionsResult = writeCorrectionsJson(corrections, distDir, factualCorrectionGroups, { evidence: evidenceById, suppliers: trackerSuppliers, groupEvidenceIds: factualCorrectionSourceEvidenceIds })
  writeFactualCorrectionsJson(factualCorrectionBundle, distDir)
  console.log(
    `generate-feed OK: wrote dist/corrections.json with ${correctionsResult.count} entr${correctionsResult.count === 1 ? 'y' : 'ies'}.`,
  )

  const indexResult = writeIssuesIndexJson(issues, distDir)
  console.log(
    `generate-feed OK: wrote dist/issues/index.json with ${indexResult.count} entr${indexResult.count === 1 ? 'y' : 'ies'}.`,
  )

  const lockResult = writeLockManifestCopy(distDir, SOURCE_LOCK_PATH)
  console.log(
    `generate-feed OK: wrote dist/issues/lock.json with ${lockResult.entryCount} entr${lockResult.entryCount === 1 ? 'y' : 'ies'}.`,
  )

  const trackerResult = writeTrackerJson(trackerSuppliers, trackerDomains, evidenceById, runStatus, distDir)
  const agentFiles = writeAgentFiles(trackerSuppliers, trackerDomains, trackerEvents, evidenceById, runStatus, isCertifiedEvent, distDir)
  console.log(`generate-feed OK: wrote ${agentFiles.length} agent file(s): ${agentFiles.join(', ')}.`)
  console.log(
    `generate-feed OK: wrote dist/tracker.json with ${trackerResult.figureCount} figure(s).`,
  )

  // --- feed + JSON machine-surface autodiscovery links, every route -------
  //
  // Wave 1 of agent-surface-spec.md §3.6/§6: the three JSON files above were
  // already written but linked from nowhere. Every route now advertises the
  // RSS feed and all three JSON files with a <link rel="alternate">, so a
  // program that starts from any page can reach them without guessing an
  // address — and scripts/verify-dist.ts's alternate-link check (11h) fails
  // the build if any of these targets stops existing in dist.

  const newestPublished = feedIssuesNewestFirst(issues)[0]

  const jsonLinkTargets: Array<{ href: string; title: string }> = [
    { href: `${SITE_URL}/issues/index.json`, title: 'Issue index (JSON)' },
    ...(newestPublished
      ? [{ href: `${SITE_URL}/issues/${newestPublished.id}.json`, title: 'Newest issue (JSON)' }]
      : []),
    { href: `${SITE_URL}/issues/lock.json`, title: 'Publication ledger (JSON)' },
    { href: `${SITE_URL}/corrections.json`, title: 'Corrections (JSON)' },
    ...(factualCorrectionGroups.length ? [{ href: `${SITE_URL}/factual-corrections.json`, title: 'Factual correction records (JSON)' }] : []),
    { href: `${SITE_URL}/tracker.json`, title: 'Tracker (JSON)' },
    { href: `${SITE_URL}/events.json`, title: 'Events (JSON)' },
  ]

  for (const routeEntry of routes) {
    const outPath = outPathFor(routeEntry)
    const html = readFileSync(outPath, 'utf8')

    if (html.includes('type="application/rss+xml"')) {
      fail(`route "${routeEntry.path}" already has an rss+xml alternate link; refusing to add a second one.`)
    }
    if (html.includes('rel="alternate" type="application/json"')) {
      fail(`route "${routeEntry.path}" already has a JSON alternate link; refusing to add a second one.`)
    }

    const headCloseCount = html.split('</head>').length - 1
    if (headCloseCount !== 1) {
      fail(`route "${routeEntry.path}": expected exactly one head-closing tag, found ${headCloseCount}.`)
    }

    const rssLinkTag = `    <link rel="alternate" type="application/rss+xml" title="${xmlEscape(PRODUCT_TITLE)}" href="${SITE_URL}/feed.xml" />`
    const jsonLinkTags = jsonLinkTargets
      .map(
        (link) =>
          `    <link rel="alternate" type="application/json" title="${xmlEscape(link.title)}" href="${link.href}" />`,
      )
      .join('\n')

    // D-139: the Markdown twin of this page, where one is built, plus the CSV
    // copy of the tracker and the agent guide.
    const markdownHref = routeEntry.path === '/' ? `${SITE_URL}/index.md` : routeEntry.path === '/data/' ? `${SITE_URL}/data/index.md` : routeEntry.kind === 'company' ? `${SITE_URL}${routeEntry.path}index.md` : null
    const agentLinkTags = [
      ...(markdownHref ? [`    <link rel="alternate" type="text/markdown" title="This page (Markdown)" href="${markdownHref}" />`] : []),
      `    <link rel="alternate" type="text/csv" title="Tracker (CSV)" href="${SITE_URL}/tracker.csv" />`,
      `    <link rel="help" type="text/plain" title="Guide for agents" href="${SITE_URL}/llms.txt" />`,
    ].join('\n')
    const linkTags = `${rssLinkTag}\n${jsonLinkTags}\n${agentLinkTags}\n  `
    const nextHtml = html.replace('</head>', () => `${linkTags}</head>`)
    writeFileSync(outPath, nextHtml)
  }

  console.log(
    `generate-feed OK: added feed + ${jsonLinkTargets.length} JSON alternate link(s) to ${routes.length} route(s).`,
  )
}
