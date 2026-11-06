/**
 * Per-company pages (D-139, option B): one view per tracked supplier, built
 * from the same payloads as /tracker.json and /events.json so the HTML page,
 * its Markdown copy and its JSON copy cannot disagree. Pure, no file I/O.
 */
import { evidenceById } from './evidence'
import { runStatus } from './runStatus'
import { DATA_LICENSE, DATA_LICENSE_URL, PRODUCT_TITLE, SITE_URL } from './meta'
import { eventsJsonPayload, trackerJsonPayload, type EventRow } from './agentExport'
import { isCertifiedEvent } from './tracker/certification'
import { coverageRows, coverageTiers, type CoverageRow } from './tracker/coverage'
import { trackerDomains } from './tracker/domains'
import { trackerEvents } from './tracker/events'
import { trackerSuppliers } from './tracker/suppliers'
import type { TrackerFigure } from './tracker/jsonExport'
import { companySlug } from './tracker/slugs'
import { filingSeries, secFilingsInLastYear } from './tracker/presentation'

export interface SecQuarter { periodEnd: string; revenueUsd: number; derived: boolean; filedDate: string; form: string; sourceUrl: string }

export interface LedgerFiling { form: string; periodEnd: string; filedDate: string; sourceUrl: string }

export interface CompanyView {
  id: string
  name: string
  displayName: string
  ticker?: string
  typeLabel: string
  domains: string[]
  tierNumber: number
  tierName: string
  figures: TrackerFigure[]
  events: EventRow[]
  /** Quarterly revenue from SEC filings, exact USD, where the company files with the SEC. */
  secQuarters: SecQuarter[]
  /** Activity ledger: each SEC 10-Q and 10-K filed in the trailing 12 months, newest first. */
  filings: LedgerFiling[]
  path: string
}

const tracker = trackerJsonPayload(trackerSuppliers, trackerDomains, evidenceById, runStatus)
const events = eventsJsonPayload(trackerEvents, trackerSuppliers, evidenceById, runStatus, isCertifiedEvent)
const rowById = new Map<string, CoverageRow>(coverageRows.map((row) => [row.supplier.id, row]))

export const eventWindow = events.window

export function companyPath(id: string): string {
  return `/companies/${companySlug(id)}/`
}

export function companyView(id: string): CompanyView | undefined {
  const row = rowById.get(id)
  if (!row) return undefined
  const tier = coverageTiers.find((t) => t.id === row.tier)
  return {
    id,
    name: row.supplier.name,
    displayName: row.displayName,
    ticker: row.supplier.ticker,
    typeLabel: row.typeLabel,
    domains: row.domains,
    tierNumber: tier?.number ?? 0,
    tierName: tier?.name ?? '',
    figures: tracker.figures.filter((f) => f.supplierId === id),
    events: events.events.filter((e) => e.supplierId === id),
    secQuarters: (row.supplier.edgarId ? filingSeries.find((s) => s.id === row.supplier.edgarId)?.quarters ?? [] : []).map((q) => ({
      periodEnd: q.periodEnd, revenueUsd: q.value, derived: !!q.derived, filedDate: q.filedDate, form: q.form, sourceUrl: q.sourceUrl,
    })),
    filings: row.supplier.edgarId ? secFilingsInLastYear().filter((f) => f.supplierId === row.supplier.edgarId)
      .sort((a, b) => b.filedDate.localeCompare(a.filedDate))
      .map((f) => ({ form: f.form, periodEnd: f.periodEnd, filedDate: f.filedDate, sourceUrl: f.sourceUrl })) : [],
    path: companyPath(id),
  }
}

/** Every tracked supplier id, in the order the tracker lists them. */
export const companyIds: string[] = trackerSuppliers.map((s) => s.id)

export function companyDescription(view: CompanyView): string {
  const parts: string[] = []
  if (view.figures.some((f) => f.type === 'revenue-latest')) parts.push('quarterly revenue')
  if (view.figures.some((f) => f.type === 'last-round')) parts.push('funding')
  if (view.figures.some((f) => f.type === 'ownership')) parts.push('ownership')
  if (view.events.length) parts.push(`${view.events.length} dated event${view.events.length === 1 ? '' : 's'} in the last 12 months`)
  const what = parts.length ? parts.join(', ') : 'the facts on record'
  return `${view.displayName}${view.ticker ? ` (${view.ticker})` : ''}: ${what}, each with its period and source. ${view.typeLabel}, ${view.domains.join(', ')}.`
}

function sourceLinks(urls: string[], dates: string[]): string {
  return urls.map((url, i) => `[${dates[i] || 'source'}](${url})`).join(', ')
}

function cell(text: string): string {
  return text.replace(/\|/g, '\\|').replace(/\r?\n/g, ' ')
}

export function companyMarkdown(view: CompanyView): string {
  const url = `${SITE_URL}${view.path}`
  const out = [
    '---',
    `title: ${view.displayName} · ${PRODUCT_TITLE}`,
    `url: ${url}`,
    `data_checked: ${runStatus.lastChecked}`,
    `license: ${DATA_LICENSE}`,
    '---',
    '',
    `# ${view.displayName}${view.ticker ? ` (${view.ticker})` : ''}`,
    '',
    `- Name on record: ${view.name}`,
    `- Company type: ${view.typeLabel}`,
    `- Market domains: ${view.domains.join(', ')}`,
    `- Coverage tier ${view.tierNumber}: ${view.tierName}`,
    `- JSON copy: ${SITE_URL}${view.path}data.json`,
    '',
    'Every figure keeps the period it is true for and its source. "Certified" means re-derived from the company\'s own SEC filings by an automated check.',
    '',
    '## Figures',
    '',
  ]
  if (view.figures.length === 0) out.push('No figures on record.', '')
  for (const f of view.figures) {
    out.push(`- ${f.label}: ${f.value.replace(/\.+$/, '')}${f.period ? ` (${f.period})` : ''}${f.certified ? ' · certified' : ''}. Source: ${sourceLinks(f.sourceUrls, f.sourceDates) || 'none listed'}`)
  }
  if (view.secQuarters.length) {
    out.push('', '## Quarterly revenue from SEC filings (USD)', '', '| Quarter ended | Revenue, USD | Filed | Source |', '|---|---|---|---|')
    for (const q of view.secQuarters) out.push(`| ${q.periodEnd} | ${q.revenueUsd.toLocaleString('en-US')}${q.derived ? ' (derived)' : ''} | ${q.filedDate} | [${q.form}](${q.sourceUrl}) |`)
  }
  if (view.filings.length) {
    out.push('', '## Activity ledger: SEC filings, last 12 months', '', '| Filed | Form | Latest quarter reported | Source |', '|---|---|---|---|')
    for (const f of view.filings) out.push(`| ${f.filedDate} | ${f.form} | ${f.periodEnd} | [${f.form}](${f.sourceUrl}) |`)
  }
  out.push('', `## Events, ${events.window.from} to ${events.window.to}`, '')
  if (view.events.length === 0) out.push('No events on record in this window.', '')
  else {
    out.push('| Date | Type | Event | Source |', '|---|---|---|---|')
    for (const e of view.events) out.push(`| ${e.date} | ${e.type} | ${cell(e.text)} | ${sourceLinks(e.sourceUrls, e.sourceDates)} |`)
    out.push('')
  }
  out.push(`License: ${DATA_LICENSE} (${DATA_LICENSE_URL}). Credit ${PRODUCT_TITLE} with a link to ${url}.`, '')
  return out.join('\n')
}

export function companyJson(view: CompanyView) {
  return {
    about: `${PRODUCT_TITLE}: sourced, dated facts for one tracked security supplier.`,
    license: DATA_LICENSE,
    licenseUrl: DATA_LICENSE_URL,
    url: `${SITE_URL}${view.path}`,
    generatedAt: runStatus.lastChecked,
    supplier: { id: view.id, name: view.name, ticker: view.ticker ?? null, type: view.typeLabel, domains: view.domains, coverageTier: view.tierNumber },
    figures: view.figures,
    secQuarterlyRevenue: view.secQuarters,
    secFilings: view.filings,
    eventWindow: events.window,
    events: view.events,
  }
}
