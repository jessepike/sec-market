// Page-structure guard (D-103). Compares two built sites on what data changes
// never alter, so any difference is a change a reader would notice and waits
// for the owner even when no commit was marked Owner-Review:
//   - the set of routes;
//   - on every page: h1 and h2 headings, ids on section, nav, main, header,
//     footer and article elements, and navigation links;
//   - the stylesheet (layout, type, colour), by content hash;
//   - the full text of the dated records (thesis, issue 2026-w36, corrections),
//     which change only through a published correction.
// It does not see wording changes elsewhere on the tracker page, h3 and lower
// headings, or chart markup; those rely on the agent's Owner-Review trailer.
//
//   node scripts/promotion/structure.mjs <production-dist> <candidate-dist>
import { readdirSync, readFileSync, statSync, appendFileSync } from 'node:fs'
import { join, relative } from 'node:path'
import { createHash } from 'node:crypto'
import { pathToFileURL } from 'node:url'

function htmlFiles(dir) {
  const out = []
  const walk = d => { for (const f of readdirSync(d)) { const p = join(d, f); if (statSync(p).isDirectory()) { if (f !== 'assets') walk(p) } else if (f.endsWith('.html')) out.push(p) } }
  walk(dir)
  return out.map(p => relative(dir, p)).sort()
}

const RECORDS = ['thesis/index.html', 'issues/2026-w36/index.html', 'corrections/index.html']
const sha = s => createHash('sha256').update(s).digest('hex').slice(0, 16)
const text = s => s.replace(/<[^>]+>/g, '').replace(/&amp;/g, '&').replace(/\s+/g, ' ').trim()

/** Route -> sorted list of structural markers. */
export function skeleton(dist) {
  const pages = {}
  for (const route of htmlFiles(dist)) {
    const html = readFileSync(join(dist, route), 'utf8')
    const marks = new Set()
    for (const m of html.matchAll(/<h([12])\b[^>]*>([\s\S]*?)<\/h\1>/g)) marks.add(`h${m[1]}: ${text(m[2])}`)
    for (const m of html.matchAll(/<(section|nav|main|header|footer|article)\b[^>]*\sid="([^"]+)"/g)) marks.add(`#${m[2]} (${m[1]})`)
    for (const nav of html.matchAll(/<nav\b[\s\S]*?<\/nav>/g)) for (const a of nav[0].matchAll(/<a\b[^>]*href="([^"]+)"[^>]*>([\s\S]*?)<\/a>/g)) marks.add(`nav: ${text(a[2])} -> ${a[1]}`)
    if (RECORDS.includes(route)) {
      const main = /<main[\s\S]*?<\/main>/.exec(html)?.[0] ?? ''
      // Dates are blanked first: the pages show the site's last-updated date, which moves with data.
      const body = text(main).replace(/(January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, \d{4}|\d{4}-\d{2}-\d{2}/g, '<date>')
      marks.add(`record text sha256 ${sha(body)}`)
    }
    pages[route] = [...marks].sort()
  }
  const css = readdirSync(join(dist, 'assets')).filter(f => f.endsWith('.css')).sort().map(f => readFileSync(join(dist, 'assets', f), 'utf8')).join('\n')
  pages['(stylesheet)'] = [`css sha256 ${sha(css)}`]
  return pages
}

/** Human-readable differences; empty when the structure is the same. */
export function compare(before, after) {
  const out = []
  for (const r of Object.keys(after)) if (!(r in before)) out.push(`new page: /${r}`)
  for (const r of Object.keys(before)) if (!(r in after)) out.push(`page removed: /${r}`)
  for (const r of Object.keys(after)) {
    if (!(r in before)) continue
    const a = new Set(before[r]), b = new Set(after[r])
    for (const m of b) if (!a.has(m)) out.push(`/${r} added ${m}`)
    for (const m of a) if (!b.has(m)) out.push(`/${r} removed ${m}`)
  }
  return out
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const [base, head] = process.argv.slice(2)
  const diffs = compare(skeleton(base), skeleton(head))
  console.log(diffs.length ? diffs.join('\n') : 'Page structure unchanged.')
  if (process.env.GITHUB_OUTPUT) appendFileSync(process.env.GITHUB_OUTPUT, `changed=${diffs.length > 0}\ndiff<<EOF\n${diffs.map(d => `- ${d}`).join('\n')}\nEOF\n`)
}
