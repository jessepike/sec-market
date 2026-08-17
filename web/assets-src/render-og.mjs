/**
 * Rasterizes assets-src/og.svg to public/og.png at 1200x630.
 *
 * Not part of `npm run build`. Run it by hand when the market call headline or
 * the context stats change, from web/ inside the OrbStack dev VM:
 *
 *     orb run -m dev bash -lc 'cd /Users/jessepike/code/projects/sec-market/web \
 *       && node assets-src/render-og.mjs'
 *
 * It drives the Chromium that Playwright already installs for the e2e suite
 * rather than adding an image-processing dependency to package.json. Chromium is
 * used because it resolves the real webfonts (Archivo, IBM Plex) the site uses;
 * a plain SVG rasterizer would silently substitute whatever font it could find.
 */
import { readFileSync, statSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { chromium } from '@playwright/test'

const WIDTH = 1200
const HEIGHT = 630
const MAX_BYTES = 300 * 1024

const assetsRoot = dirname(fileURLToPath(import.meta.url))
const svgPath = resolve(assetsRoot, 'og.svg')
const pngPath = resolve(assetsRoot, '..', 'public', 'og.png')

const svg = readFileSync(svgPath, 'utf8').replace(/<\?xml[^?]*\?>\s*/, '')

const page = `<!doctype html>
<html><head><meta charset="utf-8" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@600;800&family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600&display=swap" />
<style>html,body{margin:0;padding:0;background:#e9ecf0}svg{display:block}</style>
</head><body>${svg}</body></html>`

const browser = await chromium.launch()
const context = await browser.newContext({
  viewport: { width: WIDTH, height: HEIGHT },
  deviceScaleFactor: 1,
})
const tab = await context.newPage()
await tab.setContent(page, { waitUntil: 'networkidle' })
await tab.evaluate(() => document.fonts.ready)
await tab.screenshot({ path: pngPath, type: 'png' })
await browser.close()

const { size } = statSync(pngPath)
console.log(`Wrote ${pngPath} (${WIDTH}x${HEIGHT}, ${size} bytes).`)

if (size > MAX_BYTES) {
  console.error(`og.png is ${size} bytes, over the ${MAX_BYTES}-byte budget.`)
  process.exit(1)
}
