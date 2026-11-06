/**
 * Agent access (D-139, 2026-11-06): the machine-readable files and Markdown
 * views built beside the HTML site. Pure builders, no file I/O. The writer is
 * scripts/generate-agent.ts; the human page that lists the same files is
 * src/components/DataForAgents.tsx. Everything here is read from the same
 * data the page renders, so the two cannot disagree. Do not add a number,
 * date or claim here that is not already in the site data.
 */
import type { EvidenceRecord } from './types'
import type { RunStatus } from './runStatus'
import type { TrackerDomain } from './tracker/domains'
import type { TrackerEvent } from './tracker/events'
import type { TrackerSupplier } from './tracker/suppliers'
import { trackerJsonPayload, type TrackerJsonPayload } from './tracker/jsonExport'
import { DATA_LICENSE, DATA_LICENSE_URL, PRODUCT_TITLE, SITE_DESCRIPTION, SITE_URL } from './meta'

export interface DataFile {
  path: string
  format: 'JSON' | 'CSV' | 'Markdown' | 'Text' | 'RSS'
  what: string
}

/** Every file an agent or program can read, in the order the data page lists them. */
export const dataFiles: DataFile[] = [
  { path: '/llms.txt', format: 'Text', what: 'A short guide to this site for language models and agents.' },
  { path: '/index.md', format: 'Markdown', what: 'The tracker as Markdown: every supplier, figure, period, source and recent event.' },
  { path: '/tracker.json', format: 'JSON', what: 'Suppliers, market domains and every tracker figure with its period, sources and certified flag.' },
  { path: '/tracker.csv', format: 'CSV', what: 'The same figures as tracker.json, one row per figure.' },
  { path: '/events.json', format: 'JSON', what: 'Dated events for the trailing 12 months: funding, acquisitions, layoffs, restructuring, debt, leadership changes and more.' },
  { path: '/events.csv', format: 'CSV', what: 'The same events as events.json, one row per event.' },
  { path: '/certified-coverage.json', format: 'JSON', what: 'The certification receipt: every SEC claim re-derived from filings, with its result.' },
  { path: '/corrections.json', format: 'JSON', what: 'Every correction, newest first.' },
  { path: '/issues/index.json', format: 'JSON', what: 'The weekly issue archive.' },
  { path: '/feed.xml', format: 'RSS', what: 'New issues and corrections.' },
]

export interface EventRow {
  id: string
  supplierId: string
  supplierName: string
  date: string
  type: TrackerEvent['type']
  text: string
  sourceUrls: string[]
  sourceDates: string[]
  certified: boolean
}

export interface EventsJsonPayload {
  about: string
  license: string
  licenseUrl: string
  documentation: string
  generatedAt: string
  window: { from: string; to: string }
  events: EventRow[]
}

function sources(ids: string[], evidence: Record<string, EvidenceRecord>): { urls: string[]; dates: string[] } {
  const urls: string[] = []
  const dates: string[] = []
  for (const id of ids) {
    const record = evidence[id]
    if (record?.canonicalUrl && !urls.includes(record.canonicalUrl)) {
      urls.push(record.canonicalUrl)
      dates.push(record.publicationDate)
    }
  }
  return { urls, dates }
}

export function eventsJsonPayload(
  events: readonly TrackerEvent[],
  suppliers: readonly TrackerSupplier[],
  evidence: Record<string, EvidenceRecord>,
  status: RunStatus,
  isCertifiedEvent: (event: TrackerEvent) => boolean,
): EventsJsonPayload {
  const names = new Map(suppliers.map((s) => [s.id, s.name]))
  const to = status.lastChecked
  const from = new Date(Date.parse(to + 'T00:00:00Z') - 365 * 86_400_000).toISOString().slice(0, 10)
  const rows = [...events]
    .sort((a, b) => b.date.localeCompare(a.date) || a.id.localeCompare(b.id))
    .map((event) => {
      const src = sources(event.evidenceIds, evidence)
      return {
        id: event.id,
        supplierId: event.supplierId,
        supplierName: names.get(event.supplierId) ?? event.supplierId,
        date: event.date,
        type: event.type,
        text: event.text,
        sourceUrls: src.urls,
        sourceDates: src.dates,
        certified: isCertifiedEvent(event),
      }
    })
  return {
    about: `${PRODUCT_TITLE}: dated events for tracked security suppliers. Each event carries its date and source. ` +
      'certified means the filing and date were re-derived from SEC filings; the event text is not part of that check.',
    license: DATA_LICENSE,
    licenseUrl: DATA_LICENSE_URL,
    documentation: `${SITE_URL}/data/`,
    generatedAt: status.lastChecked,
    window: { from, to },
    events: rows,
  }
}

/** RFC 4180 field: quoted when it holds a comma, quote or line break. */
function csvField(value: string | boolean): string {
  const text = String(value)
  return /[",\r\n]/.test(text) ? `"${text.replace(/"/g, '""')}"` : text
}

function csv(header: string[], rows: (string | boolean)[][]): string {
  return [header, ...rows].map((row) => row.map(csvField).join(',')).join('\r\n') + '\r\n'
}

export function trackerCsv(payload: TrackerJsonPayload): string {
  const suppliers = new Map(payload.suppliers.map((s) => [s.id, s]))
  return csv(
    ['figure_id', 'supplier_id', 'supplier_name', 'supplier_kind', 'domain_ids', 'type', 'label', 'value', 'period', 'certified', 'source_urls', 'source_dates'],
    payload.figures.map((f) => {
      const s = suppliers.get(f.supplierId)
      return [f.id, f.supplierId, s?.name ?? '', s?.kind ?? '', (s?.domainIds ?? []).join(' '), f.type, f.label, f.value, f.period, f.certified, f.sourceUrls.join(' '), f.sourceDates.join(' ')]
    }),
  )
}

export function eventsCsv(payload: EventsJsonPayload): string {
  return csv(
    ['event_id', 'supplier_id', 'supplier_name', 'date', 'type', 'text', 'certified', 'source_urls', 'source_dates'],
    payload.events.map((e) => [e.id, e.supplierId, e.supplierName, e.date, e.type, e.text, e.certified, e.sourceUrls.join(' '), e.sourceDates.join(' ')]),
  )
}

const RULES = [
  'Facts only. The site publishes no stances, rankings, forecasts or interpretation.',
  'Every figure keeps the reporting period or as-of date it is true for, and the source it is cited to. Quote the period with the figure.',
  '"certified" means re-derived from the company\'s own SEC filings by an automated check. Other figures keep their own source and date and are not re-checked automatically.',
  'Corrections are published, never silent. See /corrections.json.',
]

function absolute(path: string): string {
  return `${SITE_URL}${path}`
}

/** `/llms.txt`, in the llmstxt.org shape: title, summary, then link sections. */
export function llmsTxt(payload: TrackerJsonPayload, eventCount: number): string {
  const lines = [
    `# ${PRODUCT_TITLE}`,
    '',
    `> ${SITE_DESCRIPTION}`,
    '',
    `It tracks ${payload.suppliers.length} security suppliers across ${payload.domains.length} market domains. ` +
      `It holds ${payload.figures.length} figures and ${eventCount} dated events from the trailing 12 months. ` +
      `Data last checked ${payload.runStatus.lastChecked}. License: ${DATA_LICENSE} (${DATA_LICENSE_URL}). Credit "${PRODUCT_TITLE}" with a link.`,
    '',
    'Rules for using this data:',
    '',
    ...RULES.map((rule) => `- ${rule}`),
    '',
    '## Data',
    '',
    ...dataFiles.filter((f) => f.path !== '/llms.txt').map((f) => `- [${f.path}](${absolute(f.path)}): ${f.format}. ${f.what}`),
    '',
    '## Pages',
    '',
    `- [Tracker](${SITE_URL}/): the front page. Send "Accept: text/markdown" to get it as Markdown.`,
    `- [Supplier coverage](${SITE_URL}/coverage/): every supplier and how much is covered for it.`,
    `- [Data for agents](${SITE_URL}/data/): these files, their fields and the license.`,
    `- [Corrections](${SITE_URL}/corrections/)`,
    `- [Issue archive](${SITE_URL}/issues/)`,
    '',
  ]
  return lines.join('\n')
}

function mdCell(text: string): string {
  return text.replace(/\|/g, '\\|').replace(/\r?\n/g, ' ')
}

function sourceLinks(urls: string[], dates: string[]): string {
  return urls.map((url, i) => `[${dates[i] || 'source'}](${url})`).join(', ')
}

/** `/index.md`: the tracker as one Markdown document an agent can read whole. */
export function trackerMarkdown(payload: TrackerJsonPayload, events: EventsJsonPayload): string {
  const domainNames = new Map(payload.domains.map((d) => [d.id, d.name]))
  const figuresBySupplier = new Map<string, TrackerJsonPayload['figures']>()
  for (const f of payload.figures) {
    const list = figuresBySupplier.get(f.supplierId) ?? []
    list.push(f)
    figuresBySupplier.set(f.supplierId, list)
  }
  const out: string[] = [
    '---',
    `title: ${PRODUCT_TITLE}`,
    `url: ${SITE_URL}/`,
    `data_checked: ${payload.runStatus.lastChecked}`,
    `license: ${DATA_LICENSE}`,
    '---',
    '',
    `# ${PRODUCT_TITLE}`,
    '',
    SITE_DESCRIPTION,
    '',
    ...RULES.map((rule) => `- ${rule}`),
    '',
    `Machine-readable copies: [tracker.json](${SITE_URL}/tracker.json), [tracker.csv](${SITE_URL}/tracker.csv), ` +
      `[events.json](${SITE_URL}/events.json), [events.csv](${SITE_URL}/events.csv). Guide: [/data/](${SITE_URL}/data/).`,
    '',
    '## Market domains',
    '',
    ...payload.domains.map((d) => `- **${d.name}** (\`${d.id}\`): ${d.scope}`),
    '',
    `## Suppliers (${payload.suppliers.length})`,
    '',
  ]
  for (const s of [...payload.suppliers].sort((a, b) => a.name.localeCompare(b.name))) {
    out.push(`### ${s.name}`, '')
    out.push(`- id: \`${s.id}\` · type: ${s.kind} · domains: ${s.domainIds.map((id) => domainNames.get(id) ?? id).join(', ')}`)
    for (const f of figuresBySupplier.get(s.id) ?? []) {
      const period = f.period ? ` (${f.period})` : ''
      const cert = f.certified ? ' · certified, re-derived from SEC filings' : ''
      out.push(`- ${f.label}: ${f.value}${period}${cert}. Source: ${sourceLinks(f.sourceUrls, f.sourceDates) || 'none listed'}`)
    }
    out.push('')
  }
  out.push(`## Events, ${events.window.from} to ${events.window.to} (${events.events.length})`, '')
  out.push('| Date | Supplier | Type | Event | Source |', '|---|---|---|---|---|')
  for (const e of events.events) {
    out.push(`| ${e.date} | ${mdCell(e.supplierName)} | ${e.type} | ${mdCell(e.text)} | ${sourceLinks(e.sourceUrls, e.sourceDates)} |`)
  }
  out.push('')
  return out.join('\n')
}

/** `/data/index.md`: the data page as Markdown. */
export function dataPageMarkdown(payload: TrackerJsonPayload): string {
  return [
    '---',
    `title: Data for agents · ${PRODUCT_TITLE}`,
    `url: ${SITE_URL}/data/`,
    `license: ${DATA_LICENSE}`,
    '---',
    '',
    '# Data for agents',
    '',
    `Everything on ${PRODUCT_TITLE} is also published as files that programs and AI agents can read. ` +
      `The files are rebuilt with the site. Data last checked ${payload.runStatus.lastChecked}.`,
    '',
    '## Rules',
    '',
    ...RULES.map((rule) => `- ${rule}`),
    '',
    '## Files',
    '',
    '| File | Format | What it holds |',
    '|---|---|---|',
    ...dataFiles.map((f) => `| [${f.path}](${absolute(f.path)}) | ${f.format} | ${f.what} |`),
    '',
    '## Markdown',
    '',
    `Send the header \`Accept: text/markdown\` to ${SITE_URL}/ or ${SITE_URL}/data/ to get the page as Markdown.`,
    '',
    '## License',
    '',
    `${DATA_LICENSE} (${DATA_LICENSE_URL}). Reuse is allowed with credit to "${PRODUCT_TITLE}" and a link to ${SITE_URL}/.`,
    '',
  ].join('\n')
}

export { trackerJsonPayload }
export type { TrackerDomain }
