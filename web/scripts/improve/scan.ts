/**
 * Weekly improvement loop, step 1: a deterministic scorecard of how well the
 * site answers the owner's product question (docs/reference/improvement-loop.md):
 * who is growing, shrinking or stalling against domain peers, and is that
 * growth healthy. It measures gaps in the data the pages already show. It
 * writes no page text and makes no judgment about any company.
 *
 *   npx tsx --tsconfig tsconfig.app.json scripts/improve/scan.ts \
 *     [--requests <file with the request-queue issue body>] [--out <file.json>]
 *
 * Prints a Markdown summary. With --out also writes the full JSON.
 */
import { readFileSync, writeFileSync } from 'node:fs'
import { isCertifiedSupplier } from '../../src/data/tracker/certification'
import { eventsForSupplier } from '../../src/data/tracker/derive'
import { domainMomentum, healthFacts } from '../../src/data/tracker/momentum'
import { onboardingSuppliers } from '../../src/data/tracker/onboarding'
import { trackerSuppliers } from '../../src/data/tracker/suppliers'
import { runStatus } from '../../src/data/runStatus'

export interface Gap {
  id: string
  /** Which half of the product question the gap weakens. */
  question: 'growth' | 'peers' | 'health' | 'freshness' | 'coverage'
  title: string
  count: number
  items: string[]
  /** What kind of change would close it; decides the ship rule. */
  fix: 'data' | 'coverage' | 'feature'
}

const arg = (name: string) => {
  const i = process.argv.indexOf(name)
  return i > 0 ? process.argv[i + 1] : undefined
}
const asOf = runStatus.lastChecked
const days = (from: string, to = asOf) => Math.floor((Date.parse(to) - Date.parse(from)) / 86_400_000)
const name = (id: string) => trackerSuppliers.find(s => s.id === id)?.name ?? id

export function scan(requestBody = ''): { asOf: string; gaps: Gap[]; requests: { name: string; count?: number; first?: string }[] } {
  const gaps: Gap[] = []
  const add = (g: Omit<Gap, 'count'>) => { if (g.items.length) gaps.push({ ...g, count: g.items.length }) }
  const momentum = domainMomentum()

  // Growth: suppliers with nothing that says whether they grow or shrink.
  add({ id: 'no-growth-signal', question: 'growth', fix: 'data',
    title: 'Suppliers with no revenue, headline metric or funding round on file',
    items: trackerSuppliers.filter(s => !s.revenue && !s.headlineMetric && !s.lastRound && s.kind !== 'acquired').map(s => s.name) })

  // Growth: company-reported revenue for public companies that are not certified.
  add({ id: 'public-uncertified', question: 'growth', fix: 'coverage',
    title: 'Public companies whose growth is company-reported, not re-derived from SEC filings',
    items: trackerSuppliers.filter(s => s.kind === 'public' && !isCertifiedSupplier(s.id)).map(s => s.name) })

  // Peers: revenue domains with fewer than three certified filers show no median.
  add({ id: 'no-domain-median', question: 'peers', fix: 'coverage',
    title: 'Revenue domains with fewer than three certified filers, so no peer median shows',
    items: momentum.filter(d => d.revenueBars && d.median === null).map(d => `${d.name} (${d.rows.length} certified)`) })

  // Health: growth rows without margins or balance sheet.
  const rows = momentum.flatMap(d => d.rows)
  for (const [field, label] of [['operatingMargin', 'operating margin'], ['fcfMargin', 'FCF margin'], ['balance', 'cash and debt']] as const)
    add({ id: `growth-without-${field}`, question: 'health', fix: 'data',
      title: `Certified growth rows with no ${label}, so healthy growth cannot be judged`,
      items: [...new Set(rows.filter(r => !r.health?.[field]).map(r => r.supplier.name))] })

  // Health lags growth: margins from an older quarter than the revenue beside them.
  add({ id: 'health-lags-growth', question: 'health', fix: 'data',
    title: `Margins older than the revenue quarter shown beside them (health figures of ${healthFacts.generatedAt.slice(0, 10)})`,
    items: [...new Set(rows.filter(r => {
      const h = r.health?.operatingMargin?.periodEnd
      const g = r.supplier.revenue?.latest.periodEnd
      return h && g && h < g
    }).map(r => `${r.supplier.name} (margins ${r.health!.operatingMargin!.periodEnd}, revenue ${r.supplier.revenue!.latest.periodEnd})`))] })

  // Freshness: a latest revenue quarter that ended more than 135 days ago is overdue.
  add({ id: 'revenue-overdue', question: 'freshness', fix: 'data',
    title: 'Latest revenue quarter ended more than 135 days ago',
    items: trackerSuppliers.filter(s => s.revenue && days(s.revenue.latest.periodEnd) > 135)
      .map(s => `${s.name} (${s.revenue!.latest.periodEnd}, ${days(s.revenue!.latest.periodEnd)} days)`) })

  // Freshness: private companies with an old round and no tracked event in a year.
  add({ id: 'private-quiet', question: 'freshness', fix: 'data',
    title: 'Private companies with a round older than 18 months and no tracked event in 12 months',
    items: trackerSuppliers.filter(s => (s.kind === 'private' || s.kind === 'pe-owned') && s.lastRound
      && days(s.lastRound.date.length === 7 ? `${s.lastRound.date}-01` : s.lastRound.date) > 548
      && !eventsForSupplier(s.id).some(e => days(e.date) <= 365)).map(s => `${s.name} (${s.lastRound!.date})`) })

  // Coverage: suppliers still held in onboarding.
  add({ id: 'onboarding-held', question: 'coverage', fix: 'coverage',
    title: 'Suppliers still held in onboarding (preview only)',
    items: onboardingSuppliers.map(s => s.name) })

  // Health snapshot gaps the generator itself recorded.
  for (const [id, missing] of Object.entries(healthFacts.gaps ?? {}))
    add({ id: `health-gap-${id}`, question: 'health', fix: 'data', title: `Health figures the generator could not find for ${name(id)}`, items: missing })

  // Requests: same marker the request box writes (ops/timer/lib/requests.js).
  const start = '<!-- company-requests:'
  const at = requestBody.indexOf(start)
  let requests: { name: string; count?: number; first?: string }[] = []
  if (at >= 0) {
    try { requests = JSON.parse(requestBody.slice(at + start.length, requestBody.indexOf('-->', at))) } catch { requests = [] }
  }
  const tracked = new Set([...trackerSuppliers, ...onboardingSuppliers].map(s => s.name.toLowerCase()))
  requests = requests.filter(r => ![...tracked].some(t => t.includes(String(r.name).toLowerCase())))
  return { asOf, gaps, requests }
}

function markdown(r: ReturnType<typeof scan>): string {
  const out = [`# Product-goal scorecard, repository data as of ${r.asOf.slice(0, 10)}`, '']
  for (const g of r.gaps) {
    out.push(`- **${g.title}** (${g.question}, ${g.fix} fix): ${g.count}`)
    out.push(`  - ${g.items.slice(0, 12).join('; ')}${g.items.length > 12 ? `; and ${g.items.length - 12} more` : ''}`)
  }
  out.push('', `Untracked company requests: ${r.requests.length ? r.requests.map(q => `${q.name}${q.count ? ` (${q.count})` : ''}`).join(', ') : 'none'}`)
  return out.join('\n')
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const file = arg('--requests')
  const result = scan(file ? readFileSync(file, 'utf8') : '')
  const out = arg('--out')
  if (out) writeFileSync(out, `${JSON.stringify(result, null, 2)}\n`)
  console.log(markdown(result))
}
