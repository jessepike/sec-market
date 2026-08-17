/**
 * Build-time prerender step.
 *
 * Runs after `vite build` (client) and `vite build --ssr` (server bundle).
 * Imports the server bundle, renders the app to an HTML string, and injects it
 * into the empty `#root` div of dist/index.html. The client entry detects the
 * existing markup and hydrates instead of mounting fresh.
 *
 * This exists so crawlers, link unfurlers, and assistants that do not execute
 * JavaScript see the real page content instead of an empty div.
 */
import { readFileSync, writeFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'

const webRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const serverEntry = resolve(webRoot, 'dist-ssr/entry-server.js')
const htmlPath = resolve(webRoot, 'dist/index.html')

const ROOT_PLACEHOLDER = '<div id="root"></div>'

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

const mod: { render?: () => string } = await import(pathToFileURL(serverEntry).href)

if (typeof mod.render !== 'function') {
  fail(`${serverEntry} does not export a render() function.`)
}

const appHtml = mod.render()

if (!appHtml || appHtml.length < 1000) {
  fail(`render() returned suspiciously little markup (${appHtml.length} chars).`)
}

// Replacer function form: appHtml is untrusted as a replacement pattern, and a
// literal "$&" or "$'" in the content would otherwise be expanded by String.replace.
const html = template.replace(ROOT_PLACEHOLDER, () => `<div id="root">${appHtml}</div>`)

writeFileSync(htmlPath, html)

console.log(
  `Prerender OK: injected ${appHtml.length} chars of markup into dist/index.html ` +
    `(${Buffer.byteLength(html)} bytes total).`,
)
