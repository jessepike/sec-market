import feedJson from './feed.json'
import { trackerSuppliers } from '../tracker/suppliers'
import { shortSupplierName } from '../tracker/names'

/**
 * Weekly funding-rounds feed written by ops/funding/collect.py. Only rounds
 * confirmed against the company's own announcement or SEC Form D are in
 * `rounds`; anything unconfirmed sits in `held` and is never shown.
 */
export interface FundingRound {
  id: string
  company: string
  country: string
  amountUsd: number | null
  stage: string
  lead: string | null
  companyUrl: string
  sourceUrl: string
  sourceKind: 'announcement' | 'sec-form-d'
  weekOf: string
  checkedAt: string
  confirmation: string
  foundVia: { name: string; issue: number; url: string }
}

interface PortfolioCompany {
  firstSeen: string
  lastSeen: string
  baseline: boolean
}

interface PortfolioState {
  name: string
  url: string
  baselineAt: string | null
  companies: Record<string, PortfolioCompany>
}

interface FundingFeed {
  updatedAt?: string
  rounds: FundingRound[]
  held: unknown[]
  portfolios: Record<string, PortfolioState>
}

const feed = feedJson as unknown as FundingFeed

export const fundingUpdatedAt: string | null = feed.updatedAt ?? null
export const fundingRounds: FundingRound[] = feed.rounds
export const heldRoundCount = feed.held.length

function normName(name: string): string {
  return name.toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim()
}

const trackedNames = new Set(
  trackerSuppliers.flatMap((s) => [normName(s.name), normName(shortSupplierName(s.name))]),
)

/** True when a round's company is one of the tracked suppliers (exact name match). */
export function isTracked(company: string): boolean {
  return trackedNames.has(normName(company))
}

/** Weeks shown on the page; older weeks stay in the data file. */
export const WEEKS_SHOWN = 12

/** Rounds grouped by the newsletter week they were announced in, newest week first. */
export function roundsByWeek(limit = WEEKS_SHOWN): { weekOf: string; rounds: FundingRound[] }[] {
  const weeks = new Map<string, FundingRound[]>()
  for (const round of fundingRounds) {
    const list = weeks.get(round.weekOf) ?? []
    list.push(round)
    weeks.set(round.weekOf, list)
  }
  return [...weeks.entries()]
    .sort(([a], [b]) => (a < b ? 1 : -1))
    .slice(0, limit)
    .map(([weekOf, rounds]) => ({
      weekOf,
      rounds: [...rounds].sort((a, b) => (b.amountUsd ?? -1) - (a.amountUsd ?? -1) || a.company.localeCompare(b.company)),
    }))
}

function host(url: string): string {
  try {
    return new URL(url).hostname.replace(/^www\./, '')
  } catch {
    return ''
  }
}

/** What kind of page confirmed the round, from its address. */
export function sourceLabel(round: FundingRound): string {
  if (round.sourceKind === 'sec-form-d') return 'SEC Form D'
  const company = host(round.companyUrl)
  const source = host(round.sourceUrl)
  if (company && (source === company || source.endsWith(`.${company}`))) return 'Company announcement'
  return 'Investor or press report'
}

export function formatUsd(amount: number | null): string {
  if (amount === null) return 'Not disclosed'
  if (amount >= 1e9) return `$${trim(amount / 1e9)}B`
  if (amount >= 1e6) return `$${trim(amount / 1e6)}M`
  if (amount >= 1e3) return `$${trim(amount / 1e3)}K`
  return `$${amount}`
}

function trim(n: number): string {
  return n.toFixed(1).replace(/\.0$/, '')
}

export interface PortfolioAddition {
  investor: string
  investorUrl: string
  company: string
  firstSeen: string
}

/** Companies that appeared on an investor's portfolio page after its first read. */
export function portfolioAdditions(): PortfolioAddition[] {
  return Object.values(feed.portfolios)
    .flatMap((p) =>
      Object.entries(p.companies)
        .filter(([, c]) => !c.baseline)
        .map(([slug, c]) => ({ investor: p.name, investorUrl: p.url, company: slugLabel(slug), firstSeen: c.firstSeen })),
    )
    .sort((a, b) => (a.firstSeen < b.firstSeen ? 1 : a.firstSeen > b.firstSeen ? -1 : a.company.localeCompare(b.company)))
}

export function portfolioSummary(): { name: string; url: string; count: number; baselineAt: string | null }[] {
  return Object.values(feed.portfolios)
    .map((p) => ({ name: p.name, url: p.url, count: Object.keys(p.companies).length, baselineAt: p.baselineAt }))
    .sort((a, b) => a.name.localeCompare(b.name))
}

/** "frame-security" -> "Frame Security"; "hush.security" -> "hush.security" (a domain stays as written). */
function slugLabel(slug: string): string {
  if (slug.includes('.')) return slug
  return slug
    .split('-')
    .map((w) => (w.length <= 2 ? w.toUpperCase() : w[0].toUpperCase() + w.slice(1)))
    .join(' ')
}
