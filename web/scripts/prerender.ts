/**
 * Build-time prerender step.
 *
 * Runs after `vite build` (client) and `vite build --ssr` (server bundle).
 * Imports the server bundle, renders each route in the route table (src/data/
 * routes.ts) to an HTML string, and writes one file per route from the
 * dist/index.html template — injecting the rendered markup into the empty
 * `#root` div and rewriting the per-route <title>, canonical, description and
 * Open Graph/Twitter tags. The client entry detects the existing markup and
 * hydrates instead of mounting fresh.
 *
 * This exists so crawlers, link unfurlers, and assistants that do not execute
 * JavaScript see the real page content instead of an empty div.
 */
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'
import { escapeHtmlAttr } from '../src/data/htmlEscape.ts'
import { issueById } from '../src/data/issues/index.ts'
import { routes, type RouteEntry } from '../src/data/routes.ts'
import { companyDescription, companyView } from '../src/data/companyPages.ts'

const webRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const serverEntry = resolve(webRoot, 'dist-ssr/entry-server.js')
const htmlPath = resolve(webRoot, 'dist/index.html')

const ROOT_PLACEHOLDER = '<div id="root"></div>'
const SITE_URL = 'https://securitymarketpulse.com'

function fail(message: string): never {
  console.error(`Prerender FAILED: ${message}`)
  process.exit(1)
}

const template = readFileSync(htmlPath, 'utf8')

if (!template.includes(ROOT_PLACEHOLDER)) {
  fail(
    `could not find ${ROOT_PLACEHOLDER} in dist/index.html. ` +
      'The root element changed shape; update ROOT_PLACEHOLDER in scripts/prerender.ts.',
  )
}

const mod: { render?: (path?: string) => string } = await import(pathToFileURL(serverEntry).href)

if (typeof mod.render !== 'function') {
  fail(`${serverEntry} does not export a render() function.`)
}

/**
 * Sections that must reach a reader without a click, per route. See §4 of
 * docs/archive/2026-09-weekly-issue/weekly-issue-spec.md. A closed <details> renders its children at
 * zero height and excludes them from hit-testing, so "present in the markup"
 * says nothing about whether anyone can read it — this asserts the structural
 * precondition (no <details> ancestor), the part a build can know.
 * `checkVisibility()` in the e2e suite is what actually settles visibility.
 */
// D-76/autonomy-coverage-plan.md §3, step 1: 'we-think', 'read' (the
// standing-thesis pointer) and 'hypotheses' are removed from the front
// page's must-see list because the sections themselves no longer render
// there — the site publishes sourced facts only, no judgments, on live
// pages. 'overview' now names RunStatus (an honest collection-status line)
// rather than the old weekly-issue strip; the id is unchanged so the
// header's nav link and this gate both still resolve. The issue permalink
// and /thesis/ routes are unaffected: both are kept as dated archive pages
// and still carry their original judged content in full.
//
// Step 1 fix pass, item 3: 'platforms' (Platform pressure) also dropped from
// this list — the whole section stopped rendering on the front page, not
// just its judged "read" column, because every row named a hand-assigned
// vendor-position label (footing the site no longer states).
//
// Step 5 (autonomy-coverage-plan.md §3): 'formation', 'absorption',
// 'prints-this-week' and 'capital' (the week-36 IssueLanes) and 'prints'
// (PrintGrid, the old scorecard) are dropped from the front list — neither
// renders on this route any more. 'market' stays: MarketByDomain (the new
// twelve-domain tracker) keeps the same section id MarketPicture used, so
// both this gate and the header's nav link keep resolving without a rename.
// 'tracker-changed' and 'tracker-coverage' are the two new must-see
// sections (WhatChangedTracker, CoverageStatement); ArchiveLinks
// ('tracker-links') is a one-line links row, not required reading, so it is
// not added here.
//
// AUTO-001 fix pass (2026-09-26), item 4: 'landscape' is dropped from the
// front list — DomainBoard's LandscapeSection (the old "security market, by
// domain" cards) no longer renders on this route; see the comment above
// FrontPage() in src/App.tsx.
const MUST_SEE_SECTION_IDS: Record<RouteEntry['kind'], string[]> = {
  front: ['overview', 'tracker-changed', 'momentum', 'tracker-coverage', 'follow'],
  market: ['event-timeline', 'reported-growth', 'market'],
  archive: ['issues'],
  corrections: ['corrections'],
  issue: ['overview', 'formation', 'absorption', 'prints-this-week', 'capital', 'we-think'],
  // SEC-MARKET-FABLE-001 T6-16: 'read' here is JudgmentBoard, the same
  // section id the front page's own #read pointer reuses (ThesisPointer) —
  // never nested on either page, both routes covered by this one entry.
  thesis: ['thesis', 'read'],
  coverage: ['coverage'],
  data: ['data'],
  funding: ['funding'],
  company: ['company'],
}

function runMustSeeGate(routeEntry: RouteEntry, appHtml: string): void {
  const ids = MUST_SEE_SECTION_IDS[routeEntry.kind]
  for (const id of ids) {
    const marker = `id="${id}"`
    const at = appHtml.indexOf(marker)
    if (at === -1) {
      fail(
        `route "${routeEntry.path}": section id="${id}" is not in the rendered markup at all. ` +
          'It is listed in MUST_SEE_SECTION_IDS in scripts/prerender.ts. Either the section was ' +
          'renamed or removed — update that list deliberately rather than deleting this check.',
      )
    }
    const before = appHtml.slice(0, at)
    const opened = (before.match(/<details/g) ?? []).length
    const closed = (before.match(/<\/details>/g) ?? []).length
    if (opened > closed) {
      fail(
        `route "${routeEntry.path}": section id="${id}" is nested inside a <details> disclosure ` +
          'and will render collapsed. A reader cannot see it without clicking. Sections in ' +
          'MUST_SEE_SECTION_IDS must sit at the top level of <main>.',
      )
    }
  }
}

interface RouteHead {
  title: string
  description: string
  ogUrl: string
}

function headFor(routeEntry: RouteEntry): RouteHead {
  const url = `${SITE_URL}${routeEntry.path}`
  if (routeEntry.kind === 'archive') {
    return {
      title: 'Issues · Security Market Pulse',
      description: 'Every Security Market Pulse weekly issue, newest first, with its permalink.',
      ogUrl: url,
    }
  }
  if (routeEntry.kind === 'issue' && routeEntry.issueId) {
    const issue = issueById[routeEntry.issueId]
    return {
      title: `Issue ${issue.id} · Security Market Pulse`,
      description: issue.read,
      ogUrl: url,
    }
  }
  if (routeEntry.kind === 'corrections') {
    return {
      title: 'Corrections · Security Market Pulse',
      description:
        'Every correction published to Security Market Pulse, newest first, with the issue and item it applies to.',
      ogUrl: url,
    }
  }
  if (routeEntry.kind === 'coverage') {
    return {
      title: 'Supplier coverage · Security Market Pulse',
      description:
        'Every security supplier Security Market Pulse tracks, its company type, and how much is covered for it: ' +
        'SEC-checked revenue, company-reported results, funding and company statements, or ownership and events only.',
      ogUrl: url,
    }
  }
  if (routeEntry.kind === 'data') {
    return {
      title: 'Data for agents · Security Market Pulse',
      description:
        'Every fact on Security Market Pulse as files that programs and AI agents can read: JSON, CSV and ' +
        'Markdown, each figure with its period, source and certified flag. Licensed CC BY 4.0.',
      ogUrl: url,
    }
  }
  if (routeEntry.kind === 'company' && routeEntry.supplierId) {
    const view = companyView(routeEntry.supplierId)
    if (!view) throw new Error(`no company view for ${routeEntry.supplierId}`)
    return {
      title: `${view.displayName}${view.ticker ? ` (${view.ticker})` : ''}: revenue, funding and events · Security Market Pulse`,
      description: companyDescription(view),
      ogUrl: url,
    }
  }
  if (routeEntry.kind === 'market') {
    return {
      title: 'Market detail: twelve months of events, growth and domains · Security Market Pulse',
      description:
        'Twelve months of tracked security market events by month, revenue growth for every public supplier, ' +
        'and every tracked company by security domain, each with its source.',
      ogUrl: url,
    }
  }
  if (routeEntry.kind === 'funding') {
    return {
      title: 'Funding rounds · Security Market Pulse',
      description:
        'Security funding rounds by week, each confirmed against the source it links to, ' +
        'and companies newly listed on cyber-specialist investors\' portfolio pages.',
      ogUrl: url,
    }
  }
  if (routeEntry.kind === 'thesis') {
    return {
      title: 'Standing analysis: does security spending lag infrastructure spending? · Security Market Pulse',
      description:
        'The standing analysis behind Security Market Pulse: whether security spending follows a rise in ' +
        'infrastructure spending, and how long after. One analysis among the site’s outputs, kept here with ' +
        'its record.',
      ogUrl: url,
    }
  }
  // Front page keeps the template's existing head as-is (see rewriteHead).
  // AUTO-001 fix pass (2026-09-26), item 4: the prior title/description
  // ("where the security market is going" / "makes no call where the
  // evidence is thin") read as a forecast and a stance, not a fact — banned
  // on a live page under fit-for-purpose blocker 3. Replaced with a plain
  // description of what the page is.
  return {
    title: 'Security Market Pulse — a facts-only supplier tracker',
    description:
      'Sourced facts about the business of the security market: who is growing, stalling, ' +
      'consolidating, being bought, or in financial trouble. Collected, checked and published ' +
      'automatically, with no stances, rankings or forecasts.',
    ogUrl: url,
  }
}

/**
 * Rewrites <title>, canonical, description and OG/Twitter tags for one
 * route's HTML. Every dynamic value (an issue's `read`, its id, the site
 * URL) is HTML-attribute-escaped before insertion — `headFor` returns raw
 * text, so a `read` line free-authored by the gather job or a human can
 * safely carry `&`, `<`, `>`, `"` or `'` without breaking the attribute or
 * the `<title>` text node it lands in.
 */
function rewriteHead(html: string, routeEntry: RouteEntry): string {
  if (routeEntry.kind === 'front') return html // front page keeps the hand-authored head verbatim

  const raw = headFor(routeEntry)
  const head = {
    title: escapeHtmlAttr(raw.title),
    description: escapeHtmlAttr(raw.description),
    ogUrl: escapeHtmlAttr(raw.ogUrl),
  }
  let next = html
  next = next.replace(/<title>[^<]*<\/title>/, `<title>${head.title}</title>`)
  next = next.replace(
    /(<link rel="canonical" href=")[^"]*(")/,
    `$1${head.ogUrl}$2`,
  )
  next = next.replace(
    /(<meta\s+name="description"\s+content=")[^"]*(")/,
    `$1${head.description}$2`,
  )
  next = next.replace(/(property="og:title" content=")[^"]*(")/, `$1${head.title}$2`)
  next = next.replace(
    /(<meta\b[^>]*?property="og:description"[^>]*?content=")[^"]*(")/,
    `$1${head.description}$2`,
  )
  next = next.replace(/(property="og:url" content=")[^"]*(")/, `$1${head.ogUrl}$2`)
  next = next.replace(/(name="twitter:title" content=")[^"]*(")/, `$1${head.title}$2`)
  next = next.replace(
    /(<meta\b[^>]*?name="twitter:description"[^>]*?content=")[^"]*(")/,
    `$1${head.description}$2`,
  )
  return next
}

function writeRoute(routeEntry: RouteEntry): void {
  const appHtml = mod.render!(routeEntry.path)

  if (!appHtml || appHtml.length < 500) {
    fail(`render("${routeEntry.path}") returned suspiciously little markup (${appHtml.length} chars).`)
  }

  runMustSeeGate(routeEntry, appHtml)

  // Replacer function form: appHtml is untrusted as a replacement pattern, and a
  // literal "$&" or "$'" in the content would otherwise be expanded by String.replace.
  let html = template.replace(ROOT_PLACEHOLDER, () => `<div id="root">${appHtml}</div>`)
  html = rewriteHead(html, routeEntry)

  const outPath =
    routeEntry.path === '/'
      ? htmlPath
      : resolve(webRoot, 'dist', routeEntry.path.replace(/^\//, ''), 'index.html')

  mkdirSync(dirname(outPath), { recursive: true })
  writeFileSync(outPath, html)

  console.log(
    `Prerender OK: route "${routeEntry.path}" — ${MUST_SEE_SECTION_IDS[routeEntry.kind].length} ` +
      `sections verified un-nested; wrote ${outPath.replace(webRoot + '/', '')} ` +
      `(${Buffer.byteLength(html)} bytes).`,
  )
}

if (!existsSync(htmlPath)) {
  fail(`${htmlPath} does not exist. Run "vite build" before scripts/prerender.ts.`)
}

for (const routeEntry of routes) {
  writeRoute(routeEntry)
}

console.log(`Prerender OK: ${routes.length} route(s) written.`)
