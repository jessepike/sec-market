/**
 * Build-time SEO step.
 *
 * Runs after `vite build` and after scripts/prerender.ts, against dist/.
 *
 * Jobs, all driven off src/data so that nothing here can drift from the page
 * content when a new edition or issue ships:
 *   1. Fail the build if the hand-maintained OG image (assets-src/og.svg) or
 *      the front page's og:image:alt / twitter:image:alt no longer carry the
 *      current SITE_HEADLINE. See the OG staleness gate below.
 *      This check runs against the front page only; it is the only route with
 *      a hand-authored social image.
 *   2. Inject a schema.org JSON-LD block into every emitted route's HTML —
 *      `Report` for the front page, `CollectionPage` for the archive, and
 *      `Article` (with `datePublished` when published) for each issue.
 *   3. Write dist/sitemap.xml with one `<url>` per route in the route table.
 *
 * robots.txt is static and lives in public/, because it never changes.
 *
 * Every value below is copied from existing site data. Do not add a number,
 * date, or claim here that is not already on the page.
 */
import { readFileSync, writeFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { correctionsNewestFirst } from '../src/data/correctionHelpers.ts'
import { corrections } from '../src/data/corrections.ts'
import { feedIssuesNewestFirst } from '../src/data/issueHelpers.ts'
import { issueById, issues } from '../src/data/issues/index.ts'
import { routes, type RouteEntry } from '../src/data/routes.ts'
import { companyDescription, companyView } from '../src/data/companyPages.ts'
import { marketCall } from '../src/data/market.ts'
import {
  AUTHOR_NAME,
  DATA_LICENSE_URL,
  LAST_UPDATED_ISO,
  PRODUCT_TITLE,
  SITE_DESCRIPTION,
  SITE_HEADLINE,
  SITE_URL,
} from '../src/data/meta.ts'

const webRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const htmlPath = resolve(webRoot, 'dist/index.html')
const sitemapPath = resolve(webRoot, 'dist/sitemap.xml')

const CANONICAL_URL = `${SITE_URL}/`
const OG_IMAGE_URL = `${SITE_URL}/og.png`
// AUTO-001 fix pass 4, item 10: a stable @id so every JSON-LD block's
// `publisher` resolves to the same entity, instead of three separate
// anonymous Organization objects that happen to share a name.
const PUBLISHER_ID = `${SITE_URL}/#organization`

function fail(message: string): never {
  console.error(`SEO step FAILED: ${message}`)
  process.exit(1)
}

function outPathFor(routeEntry: RouteEntry): string {
  return routeEntry.path === '/'
    ? htmlPath
    : resolve(webRoot, 'dist', routeEntry.path.replace(/^\//, ''), 'index.html')
}

/** Reads the <meta name="description"> already declared in an emitted route's HTML. */
function readDescription(html: string): string {
  const match = html.match(/<meta\s+name="description"\s+content="([^"]+)"/)
  if (!match) {
    fail('could not find <meta name="description"> in the route HTML.')
  }
  return match[1]
}

/** Reads the <title> already declared in an emitted route's HTML. */
function readTitle(html: string): string {
  const match = html.match(/<title>([^<]+)<\/title>/)
  if (!match) {
    fail('could not find <title> in the route HTML.')
  }
  return match[1]
}

const frontHtml = readFileSync(htmlPath, 'utf8')

// --- OG staleness gate (front page only) ------------------------------------
// assets-src/og.svg bakes SITE_HEADLINE into the image as literal text; it is
// rasterized to public/og.png by the manual step assets-src/render-og.mjs,
// which nothing in `npm run build` runs. index.html's og:image:alt and
// twitter:image:alt repeat the headline for the same unfurl. None of that is
// derived at build time, so editing SITE_HEADLINE alone would leave the build
// green while every LinkedIn/Slack unfurl kept showing the old headline. Fail
// closed instead. The card carries no figures, so only the headline is checked.
const ogSvg = readFileSync(resolve(webRoot, 'assets-src/og.svg'), 'utf8')

// The headline is laid out as separate <text> elements (one per line), so
// strip comments/tags and collapse whitespace to read the image's text as the
// single sentence a viewer sees.
const ogSvgText = ogSvg
  .replace(/<!--[\s\S]*?-->/g, ' ')
  .replace(/<[^>]+>/g, ' ')
  .replace(/\s+/g, ' ')
  .trim()

const ogDrift: string[] = []

if (!ogSvgText.includes(SITE_HEADLINE)) {
  ogDrift.push(`assets-src/og.svg does not contain the current headline: "${SITE_HEADLINE}"`)
}

/** Reads a `content="…"` attribute off the named property/name meta tag in the front page HTML. */
function readMetaContent(attr: 'property' | 'name', key: string): string | null {
  const match = frontHtml.match(new RegExp(`${attr}="${key}"[\\s\\S]*?content="([^"]*)"`))
  return match ? match[1] : null
}

for (const [attr, key] of [['property', 'og:image:alt'], ['name', 'twitter:image:alt']] as const) {
  const alt = readMetaContent(attr, key)
  if (alt === null) {
    ogDrift.push(`index.html has no ${key} meta tag`)
  } else if (!alt.includes(SITE_HEADLINE)) {
    ogDrift.push(`index.html ${key} does not contain the current headline: "${SITE_HEADLINE}"`)
  }
}

if (ogDrift.length > 0) {
  fail(
    `${ogDrift.join('; ')}. SITE_HEADLINE changed and the OG image / social meta tags were not ` +
      "updated to match: edit assets-src/og.svg's text to match, then re-run " +
      'node assets-src/render-og.mjs (from web/) to rebuild public/og.png, and update ' +
      "index.html's og:image:alt and twitter:image:alt to the current headline.",
  )
}

// --- JSON-LD injection, per route --------------------------------------------

function structuredDataFor(routeEntry: RouteEntry, html: string) {
  const url = `${SITE_URL}${routeEntry.path}`

  if (routeEntry.kind === 'archive') {
    // Wave 1 of agent-surface-spec.md §3.5: author + dates were the one L3
    // JSON-LD test this block failed. Both dates come from the published
    // issues themselves (never the render-time clock), falling back to the
    // site's own build stamp only if no issue has published yet.
    const published = feedIssuesNewestFirst(issues)
    const datePublished = published.at(-1)?.published ?? LAST_UPDATED_ISO
    const dateModified = published.at(0)?.published ?? LAST_UPDATED_ISO
    return {
      '@context': 'https://schema.org',
      '@type': 'CollectionPage',
      '@id': `${url}#collection`,
      url,
      name: readTitle(html),
      description: readDescription(html),
      isPartOf: { '@type': 'WebSite', name: PRODUCT_TITLE, url: `${SITE_URL}/` },
      inLanguage: 'en',
      author: { '@type': 'Person', name: AUTHOR_NAME },
      datePublished,
      dateModified,
    }
  }

  if (routeEntry.kind === 'corrections') {
    const ordered = correctionsNewestFirst(corrections)
    const datePublished = ordered.at(-1)?.date ?? LAST_UPDATED_ISO
    const dateModified = ordered.at(0)?.date ?? LAST_UPDATED_ISO
    return {
      '@context': 'https://schema.org',
      '@type': 'CollectionPage',
      '@id': `${url}#collection`,
      url,
      name: readTitle(html),
      description: readDescription(html),
      isPartOf: { '@type': 'WebSite', name: PRODUCT_TITLE, url: `${SITE_URL}/` },
      inLanguage: 'en',
      datePublished,
      dateModified,
    }
  }

  if (routeEntry.kind === 'coverage' || routeEntry.kind === 'funding' || routeEntry.kind === 'market' || routeEntry.kind === 'method') {
    return {
      '@context': 'https://schema.org',
      '@type': 'CollectionPage',
      '@id': `${url}#collection`,
      url,
      name: readTitle(html),
      description: readDescription(html),
      isPartOf: { '@type': 'WebSite', name: PRODUCT_TITLE, url: `${SITE_URL}/` },
      inLanguage: 'en',
      dateModified: LAST_UPDATED_ISO,
    }
  }

  if (routeEntry.kind === 'company' && routeEntry.supplierId) {
    // D-139: one supplier's page. `about` names the company; values come from the same view the page renders.
    const view = companyView(routeEntry.supplierId)
    if (!view) fail(`no company view for ${routeEntry.supplierId}`)
    return {
      '@context': 'https://schema.org',
      '@type': 'WebPage',
      '@id': `${url}#page`,
      url,
      name: `${view.displayName}: revenue, funding and events`,
      description: companyDescription(view),
      inLanguage: 'en',
      isAccessibleForFree: true,
      license: DATA_LICENSE_URL,
      dateModified: LAST_UPDATED_ISO,
      about: {
        '@type': 'Organization',
        name: view.name,
        ...(view.ticker ? { tickerSymbol: view.ticker } : {}),
      },
      publisher: { '@type': 'Organization', '@id': PUBLISHER_ID, name: PRODUCT_TITLE, url: `${SITE_URL}/` },
      isPartOf: { '@type': 'WebSite', name: PRODUCT_TITLE, url: `${SITE_URL}/` },
    }
  }

  if (routeEntry.kind === 'data') {
    // D-139: schema.org Dataset, so dataset search and agents can find the files.
    return {
      '@context': 'https://schema.org',
      '@type': 'Dataset',
      '@id': `${url}#dataset`,
      url,
      name: `${PRODUCT_TITLE} tracker data`,
      description: readDescription(html),
      inLanguage: 'en',
      isAccessibleForFree: true,
      license: DATA_LICENSE_URL,
      dateModified: LAST_UPDATED_ISO,
      creator: { '@type': 'Organization', '@id': PUBLISHER_ID, name: PRODUCT_TITLE, url: `${SITE_URL}/` },
      publisher: { '@type': 'Organization', '@id': PUBLISHER_ID, name: PRODUCT_TITLE, url: `${SITE_URL}/` },
      isPartOf: { '@type': 'WebSite', name: PRODUCT_TITLE, url: `${SITE_URL}/` },
      keywords: ['cybersecurity market', 'security vendors', 'revenue', 'funding', 'acquisitions', 'layoffs', 'SEC filings'],
      distribution: [
        { '@type': 'DataDownload', encodingFormat: 'application/json', contentUrl: `${SITE_URL}/tracker.json` },
        { '@type': 'DataDownload', encodingFormat: 'text/csv', contentUrl: `${SITE_URL}/tracker.csv` },
        { '@type': 'DataDownload', encodingFormat: 'application/json', contentUrl: `${SITE_URL}/events.json` },
        { '@type': 'DataDownload', encodingFormat: 'text/csv', contentUrl: `${SITE_URL}/events.csv` },
      ],
    }
  }

  if (routeEntry.kind === 'thesis') {
    // SEC-MARKET-FABLE-001 T6-16: the standing thesis, moved off the front
    // page to its own address. Modeled as an Article, like an issue
    // permalink, rather than the front page's own Report type, because it is
    // one analysis among the site's outputs (product-core.md §5), not the
    // site itself. No page-specific judged date exists (see ThesisPointer.tsx
    // and HeroContent in Hero.tsx) so this falls back to the site's own
    // LAST_UPDATED_ISO, same as every other non-issue route below.
    return {
      '@context': 'https://schema.org',
      '@type': 'Article',
      '@id': `${url}#article`,
      url,
      mainEntityOfPage: { '@type': 'WebPage', '@id': url },
      headline: marketCall.headline,
      name: readTitle(html),
      description: readDescription(html),
      inLanguage: 'en',
      isAccessibleForFree: true,
      datePublished: LAST_UPDATED_ISO,
      dateModified: LAST_UPDATED_ISO,
      author: { '@type': 'Person', name: AUTHOR_NAME },
      publisher: { '@type': 'Organization', '@id': PUBLISHER_ID, name: PRODUCT_TITLE, url: `${SITE_URL}/` },
      isPartOf: { '@type': 'WebSite', name: PRODUCT_TITLE, url: `${SITE_URL}/` },
    }
  }

  if (routeEntry.kind === 'issue' && routeEntry.issueId) {
    const issue = issueById[routeEntry.issueId]
    return {
      '@context': 'https://schema.org',
      '@type': 'Article',
      '@id': `${url}#article`,
      url,
      mainEntityOfPage: { '@type': 'WebPage', '@id': url },
      headline: issue.read,
      name: readTitle(html),
      description: readDescription(html),
      inLanguage: 'en',
      isAccessibleForFree: true,
      ...(issue.published ? { datePublished: issue.published, dateModified: issue.published } : {}),
      author: { '@type': 'Person', name: AUTHOR_NAME },
      publisher: { '@type': 'Organization', '@id': PUBLISHER_ID, name: PRODUCT_TITLE, url: `${SITE_URL}/` },
      isPartOf: { '@type': 'WebSite', name: PRODUCT_TITLE, url: `${SITE_URL}/` },
    }
  }

  // D-76/autonomy-coverage-plan.md §3, step 1: the front page's JSON-LD used
  // to carry the judged market-call headline/subhead (marketCall.headline /
  // marketCall.subhead) as its own headline/abstract. The front page no
  // longer asserts that call — it moved to the dated /thesis/ record, which
  // still uses marketCall.headline below, correctly, since that page is
  // about the thesis. This route now describes what the page actually is.
  return {
    '@context': 'https://schema.org',
    '@type': 'Report',
    '@id': `${CANONICAL_URL}#report`,
    url: CANONICAL_URL,
    mainEntityOfPage: { '@type': 'WebPage', '@id': CANONICAL_URL },
    name: readTitle(html),
    headline: SITE_HEADLINE,
    description: readDescription(html),
    abstract: SITE_DESCRIPTION,
    inLanguage: 'en',
    isAccessibleForFree: true,
    datePublished: LAST_UPDATED_ISO,
    dateModified: LAST_UPDATED_ISO,
    image: OG_IMAGE_URL,
    publisher: { '@type': 'Organization', '@id': PUBLISHER_ID, name: PRODUCT_TITLE, url: CANONICAL_URL },
  }
}

function injectJsonLd(routeEntry: RouteEntry): void {
  const outPath = outPathFor(routeEntry)
  const html = readFileSync(outPath, 'utf8')

  // Anchoring on the head-closing tag is only safe when there is exactly one of
  // them. A stray copy inside a comment silently swallows the injected block (and
  // Vite's own script tags with it), so refuse to guess which one is real.
  const headCloseCount = html.split('</head>').length - 1
  if (headCloseCount !== 1) {
    fail(
      `route "${routeEntry.path}": expected exactly one head-closing tag, found ${headCloseCount}. ` +
        'Remove the extra one (check for it inside an HTML comment).',
    )
  }

  if (html.includes('application/ld+json')) {
    fail(`route "${routeEntry.path}" already contains a JSON-LD block; refusing to inject a second one.`)
  }

  const structuredData = structuredDataFor(routeEntry, html)

  // JSON.stringify cannot emit "<", but a "</script" sequence inside any string value
  // would still close the tag early, so escape the one character that can do it.
  const jsonLd = JSON.stringify(structuredData, null, 2).replace(/</g, '\\u003c')
  const scriptTag = `    <script type="application/ld+json">\n${jsonLd}\n    </script>\n  `

  // Replacer-function form: the payload is untrusted as a replacement pattern.
  const nextHtml = html.replace('</head>', () => `${scriptTag}</head>`)
  writeFileSync(outPath, nextHtml)

  console.log(`SEO OK: injected ${jsonLd.length} chars of JSON-LD into route "${routeEntry.path}".`)
}

for (const routeEntry of routes) {
  injectJsonLd(routeEntry)
}

// --- Sitemap: one <url> per route --------------------------------------------

const urlEntries = routes
  .map((routeEntry) => {
    const url = `${SITE_URL}${routeEntry.path}`
    const lastmod =
      routeEntry.kind === 'issue' && routeEntry.issueId
        ? (issueById[routeEntry.issueId].published ?? LAST_UPDATED_ISO)
        : routeEntry.kind === 'corrections'
          ? (correctionsNewestFirst(corrections).at(0)?.date ?? LAST_UPDATED_ISO)
          : LAST_UPDATED_ISO
    const priority = routeEntry.kind === 'front' ? '1.0' : '0.7'
    return `  <url>
    <loc>${url}</loc>
    <lastmod>${lastmod}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>${priority}</priority>
  </url>`
  })
  .join('\n')

// Wave 1 of agent-surface-spec.md §3.6: the three JSON machine-surface files
// that already existed but appeared nowhere else in the sitemap.
const newestPublishedForSitemap = feedIssuesNewestFirst(issues)[0]
const jsonUrls = [
  `${SITE_URL}/issues/index.json`,
  ...(newestPublishedForSitemap ? [`${SITE_URL}/issues/${newestPublishedForSitemap.id}.json`] : []),
  `${SITE_URL}/issues/lock.json`,
  `${SITE_URL}/corrections.json`,
  `${SITE_URL}/tracker.json`,
]
const jsonEntries = jsonUrls
  .map(
    (url) => `  <url>
    <loc>${url}</loc>
    <lastmod>${LAST_UPDATED_ISO}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.3</priority>
  </url>`,
  )
  .join('\n')

const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urlEntries}
${jsonEntries}
</urlset>
`

writeFileSync(sitemapPath, sitemap)

console.log(
  `SEO OK: wrote dist/sitemap.xml with ${routes.length} route(s) and ${jsonUrls.length} JSON machine-surface entr${jsonUrls.length === 1 ? 'y' : 'ies'}.`,
)
