/**
 * Build-time SEO step.
 *
 * Runs after `vite build` and after scripts/prerender.ts, against dist/.
 *
 * Two jobs, both driven off src/data/meta.ts and src/data/market.ts so that
 * nothing here can drift from the page content when a new edition ships:
 *   1. Inject a schema.org JSON-LD block into dist/index.html.
 *   2. Write dist/sitemap.xml with lastmod set from LAST_UPDATED_ISO.
 *
 * robots.txt is static and lives in public/, because it never changes.
 *
 * Every value below is copied from existing site data. Do not add a number,
 * date, or claim here that is not already on the page.
 */
import { readFileSync, writeFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { marketCall } from '../src/data/market.ts'
import {
  AUTHOR_NAME,
  EPISODE_ID,
  EPISODE_VERSION,
  LAST_UPDATED_ISO,
  PRODUCT_TITLE,
  RESEARCH_FREEZE,
  SITE_URL,
} from '../src/data/meta.ts'

const webRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const htmlPath = resolve(webRoot, 'dist/index.html')
const sitemapPath = resolve(webRoot, 'dist/sitemap.xml')

const CANONICAL_URL = `${SITE_URL}/`
const OG_IMAGE_URL = `${SITE_URL}/og.png`

function fail(message: string): never {
  console.error(`SEO step FAILED: ${message}`)
  process.exit(1)
}

/** Reads the <meta name="description"> already declared in index.html. */
function readDescription(html: string): string {
  const match = html.match(/<meta\s+name="description"\s+content="([^"]+)"/)
  if (!match) {
    fail('could not find <meta name="description"> in dist/index.html.')
  }
  return match[1]
}

const html = readFileSync(htmlPath, 'utf8')

// Anchoring on the head-closing tag is only safe when there is exactly one of
// them. A stray copy inside a comment silently swallows the injected block (and
// Vite's own script tags with it), so refuse to guess which one is real.
const headCloseCount = html.split('</head>').length - 1

if (headCloseCount !== 1) {
  fail(
    `expected exactly one head-closing tag in dist/index.html, found ${headCloseCount}. ` +
      'Remove the extra one (check for it inside an HTML comment in index.html).',
  )
}

if (html.includes('application/ld+json')) {
  fail('dist/index.html already contains a JSON-LD block; refusing to inject a second one.')
}

const structuredData = {
  '@context': 'https://schema.org',
  '@type': 'Report',
  '@id': `${CANONICAL_URL}#report`,
  url: CANONICAL_URL,
  mainEntityOfPage: { '@type': 'WebPage', '@id': CANONICAL_URL },
  name: `${PRODUCT_TITLE} — ${EPISODE_ID} v${EPISODE_VERSION}`,
  headline: marketCall.headline,
  description: readDescription(html),
  abstract: marketCall.subhead,
  reportNumber: `${EPISODE_ID} v${EPISODE_VERSION}`,
  inLanguage: 'en',
  isAccessibleForFree: true,
  datePublished: RESEARCH_FREEZE,
  dateModified: LAST_UPDATED_ISO,
  image: OG_IMAGE_URL,
  author: { '@type': 'Person', name: AUTHOR_NAME },
  publisher: { '@type': 'Organization', name: PRODUCT_TITLE, url: CANONICAL_URL },
}

// JSON.stringify cannot emit "<", but a "</script" sequence inside any string value
// would still close the tag early, so escape the one character that can do it.
const jsonLd = JSON.stringify(structuredData, null, 2).replace(/</g, '\\u003c')

const scriptTag = `    <script type="application/ld+json">\n${jsonLd}\n    </script>\n  `

// Replacer-function form: the payload is untrusted as a replacement pattern.
const nextHtml = html.replace('</head>', () => `${scriptTag}</head>`)

writeFileSync(htmlPath, nextHtml)

const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>${CANONICAL_URL}</loc>
    <lastmod>${LAST_UPDATED_ISO}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>
`

writeFileSync(sitemapPath, sitemap)

console.log(
  `SEO OK: injected ${jsonLd.length} chars of JSON-LD into dist/index.html and wrote ` +
    `dist/sitemap.xml (lastmod ${LAST_UPDATED_ISO}).`,
)
