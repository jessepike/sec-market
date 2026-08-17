/**
 * Build-time SEO step.
 *
 * Runs after `vite build` and after scripts/prerender.ts, against dist/.
 *
 * Three jobs, all driven off src/data/meta.ts and src/data/market.ts so that
 * nothing here can drift from the page content when a new edition ships:
 *   1. Fail the build if the hand-maintained OG image (assets-src/og.svg) or
 *      index.html's og:image:alt / twitter:image:alt no longer match the
 *      current headline and contextStats — see the OG staleness gate below.
 *   2. Inject a schema.org JSON-LD block into dist/index.html.
 *   3. Write dist/sitemap.xml with lastmod set from LAST_UPDATED_ISO.
 *
 * robots.txt is static and lives in public/, because it never changes.
 *
 * Every value below is copied from existing site data. Do not add a number,
 * date, or claim here that is not already on the page.
 */
import { readFileSync, writeFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { contextStats, marketCall } from '../src/data/market.ts'
import {
  AUTHOR_NAME,
  EPISODE_ID,
  EPISODE_VERSION,
  LAST_UPDATED_ISO,
  PRODUCT_TITLE,
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

/** Reads the <title> already declared in index.html. */
function readTitle(html: string): string {
  const match = html.match(/<title>([^<]+)<\/title>/)
  if (!match) {
    fail('could not find <title> in dist/index.html.')
  }
  return match[1]
}

const html = readFileSync(htmlPath, 'utf8')

// --- OG staleness gate ------------------------------------------------------
// assets-src/og.svg bakes marketCall.headline and every contextStats[].value
// into the image as literal text; it is rasterized to public/og.png by the
// manual step assets-src/render-og.mjs, which nothing in `npm run build` runs.
// index.html's og:image:alt and twitter:image:alt duplicate the headline for
// the same unfurl. None of that is derived at build time, so editing
// src/data/market.ts alone leaves the build green while every LinkedIn/Slack
// unfurl keeps showing the old headline and stats under the new page. Fail
// closed instead.
const ogSvg = readFileSync(resolve(webRoot, 'assets-src/og.svg'), 'utf8')

// The headline is laid out as two separate <text> elements (one per line), so
// strip comments/tags and collapse whitespace to read the image's text as the
// single sentence a viewer sees.
const ogSvgText = ogSvg
  .replace(/<!--[\s\S]*?-->/g, ' ')
  .replace(/<[^>]+>/g, ' ')
  .replace(/\s+/g, ' ')
  .trim()

const ogDrift: string[] = []

if (!ogSvgText.includes(marketCall.headline)) {
  ogDrift.push(`assets-src/og.svg does not contain the current headline: "${marketCall.headline}"`)
}

for (const stat of contextStats) {
  if (!ogSvgText.includes(stat.value)) {
    ogDrift.push(
      `assets-src/og.svg does not contain the current contextStats value "${stat.value}" (${stat.label})`,
    )
  }
}

/** Reads a `content="…"` attribute off the named property/name meta tag in index.html. */
function readMetaContent(attr: 'property' | 'name', key: string): string | null {
  const match = html.match(new RegExp(`${attr}="${key}"[\\s\\S]*?content="([^"]*)"`))
  return match ? match[1] : null
}

const ogImageAlt = readMetaContent('property', 'og:image:alt')
const twitterImageAlt = readMetaContent('name', 'twitter:image:alt')

if (ogImageAlt === null) {
  ogDrift.push('index.html has no og:image:alt meta tag to check against the current headline')
} else if (!ogImageAlt.includes(marketCall.headline)) {
  ogDrift.push(`index.html's og:image:alt does not contain the current headline: "${marketCall.headline}"`)
}

if (twitterImageAlt === null) {
  ogDrift.push('index.html has no twitter:image:alt meta tag to check against the current headline')
} else if (!twitterImageAlt.includes(marketCall.headline)) {
  ogDrift.push(`index.html's twitter:image:alt does not contain the current headline: "${marketCall.headline}"`)
}

if (ogDrift.length > 0) {
  fail(
    `${ogDrift.join('; ')}. src/data/market.ts changed and the OG image / social meta tags were not ` +
      "updated to match: edit assets-src/og.svg's text to match, then re-run assets-src/render-og.mjs " +
      '(from web/, inside the OrbStack dev VM) to rebuild public/og.png, and update index.html\'s ' +
      'og:image:alt and twitter:image:alt to the current headline.',
  )
}

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
  name: readTitle(html),
  headline: marketCall.headline,
  description: readDescription(html),
  abstract: marketCall.subhead,
  reportNumber: `${EPISODE_ID} v${EPISODE_VERSION}`,
  inLanguage: 'en',
  isAccessibleForFree: true,
  datePublished: LAST_UPDATED_ISO,
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
