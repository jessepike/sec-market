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

/**
 * Sections that must reach a reader without a click.
 *
 * This exists because the market read — the headline, what changed, Do, Avoid,
 * and the no-call boundaries — shipped to production nested inside a closed
 * <details> and stayed there. The page carried every judgment the site makes and
 * showed a reader none of them. The vendor scorecard had the same defect six
 * days earlier and was fixed on its own, which is exactly why this check is a
 * list rather than a one-off: fixing one instance of a defect is not fixing the
 * defect. Both times a human had to notice.
 *
 * A closed <details> renders its children at zero height and excludes them from
 * hit-testing, so "present in the markup" says nothing about whether anyone can
 * read it. This asserts the structural precondition — no <details> ancestor —
 * which is the part a build can know. It cannot prove visibility; only a browser
 * can, and `checkVisibility()` is what settles that question.
 */
const ALWAYS_VISIBLE_SECTION_IDS = [
  'overview',
  'read',
  'landscape',
  'moved',
  'platforms',
  'hypotheses',
  'prints',
]

for (const id of ALWAYS_VISIBLE_SECTION_IDS) {
  const marker = `id="${id}"`
  const at = appHtml.indexOf(marker)
  if (at === -1) {
    fail(
      `section id="${id}" is not in the rendered markup at all. It is listed in ` +
        'ALWAYS_VISIBLE_SECTION_IDS in scripts/prerender.ts. Either the section was ' +
        'renamed or removed — update that list deliberately rather than deleting this check.',
    )
  }
  const before = appHtml.slice(0, at)
  const opened = (before.match(/<details/g) ?? []).length
  const closed = (before.match(/<\/details>/g) ?? []).length
  if (opened > closed) {
    fail(
      `section id="${id}" is nested inside a <details> disclosure and will render ` +
        'collapsed. A reader cannot see it without clicking. Sections in ' +
        'ALWAYS_VISIBLE_SECTION_IDS must sit at the top level of <main>.',
    )
  }
}

// Replacer function form: appHtml is untrusted as a replacement pattern, and a
// literal "$&" or "$'" in the content would otherwise be expanded by String.replace.
const html = template.replace(ROOT_PLACEHOLDER, () => `<div id="root">${appHtml}</div>`)

writeFileSync(htmlPath, html)

console.log(
  `Prerender OK: ${ALWAYS_VISIBLE_SECTION_IDS.length} sections verified un-nested; ` +
    `injected ${appHtml.length} chars of markup into dist/index.html ` +
    `(${Buffer.byteLength(html)} bytes total).`,
)
