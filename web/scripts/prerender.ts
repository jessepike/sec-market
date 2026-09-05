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
 * docs/active/weekly-issue-spec.md. A closed <details> renders its children at
 * zero height and excludes them from hit-testing, so "present in the markup"
 * says nothing about whether anyone can read it — this asserts the structural
 * precondition (no <details> ancestor), the part a build can know.
 * `checkVisibility()` in the e2e suite is what actually settles visibility.
 */
const MUST_SEE_SECTION_IDS: Record<RouteEntry['kind'], string[]> = {
  front: [
    'overview',
    'formation',
    'absorption',
    'prints-this-week',
    'capital',
    'we-think',
    'read',
    'landscape',
    'platforms',
    'hypotheses',
    'prints',
  ],
  archive: ['issues'],
  issue: ['overview', 'formation', 'absorption', 'prints-this-week', 'capital', 'we-think'],
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
  // Front page keeps the template's existing head as-is (see rewriteHead).
  return {
    title: 'Security Market Pulse — where the security market is going',
    description:
      'An evidence-linked read on the cybersecurity market for security leaders. Every number links to a public source, and the page makes no call where the evidence is thin.',
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
