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
import { issues } from '../src/data/issues/index.ts'
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
  }
  return `${issues.length} issue JSON file(s) present and well-formed`
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
})

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
  const publishedCount = issues.filter((issue) => issue.status === 'published' && issue.published).length
  if (openTags !== publishedCount) {
    throw new Error(
      `dist/feed.xml has ${openTags} <item> element(s), expected exactly one per published issue (${publishedCount})`,
    )
  }
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
