/**
 * One-line facts for the front page feed. Each line is pulled from the event's own sourced text
 * by fixed patterns, never written by a model. When no pattern matches, the line falls back to
 * the opening words of the source text. Every dollar figure carries what it measures.
 */
import type { ChangeItem } from './presentation'

export interface EventFact {
  /** The extracted line, e.g. "Proofpoint acquiring Varonis". */
  line: string
  /** Deal status for acquisitions and divestitures. */
  status: 'Announced' | 'Closed' | null
  /** A dollar figure and what it measures, e.g. { text: '$6.3B', label: 'deal value' }. */
  amount: { value: number; text: string; label: string } | null
}

const ROLES: [RegExp, string][] = [
  [/\bChief Executive Officer\b|\bCEO\b/, 'CEO'], [/\bChief Financial Officer\b|\bCFO\b/, 'CFO'],
  [/\bChief Revenue Officer\b|\bCRO\b/, 'CRO'], [/\bChief Operating Officer\b|\bCOO\b/, 'COO'],
  [/\bChief Technology Officer\b|\bCTO\b/, 'CTO'], [/\bChief Marketing Officer\b|\bCMO\b/, 'CMO'],
  [/\bChief (?:Information )?Security Officer\b|\bCISO\b/, 'CISO'], [/\bChief Product\b/, 'Chief Product Officer'],
  [/\bPresident\b/, 'President'], [/\bboard\b/i, 'Board'],
]

/** "$6.3 billion" -> 6.3e9; "$1,250,000,000" -> 1.25e9. Per-share prices and amounts under $1M are ignored. */
export function parseAmount(text: string): number | null {
  const m = text.match(/\$\s?(\d[\d,]*(?:\.\d+)?)\s*(million|billion)\b/i)
  if (m) return Number(m[1].replaceAll(',', '')) * (m[2].toLowerCase() === 'billion' ? 1e9 : 1e6)
  const full = text.match(/\$(\d{1,3}(?:,\d{3}){2,})(?!\.\d|\d)/)
  return full ? Number(full[1].replaceAll(',', '')) : null
}

export function shortUsd(n: number): string {
  const trim = (x: string) => x.includes('.') ? x.replace(/\.?0+$/, '') : x
  if (n >= 1e9) return `$${trim((n / 1e9).toFixed(n >= 1e10 ? 1 : 2))}B`
  return `$${trim((n / 1e6).toFixed(n >= 1e8 ? 0 : 1))}M`
}

function amountWith(text: string, label: string): EventFact['amount'] {
  const value = parseAmount(text)
  return value === null ? null : { value, text: shortUsd(value), label }
}

/** The opening words of the source text, cut at a word boundary. */
function opening(text: string, max = 80): string {
  const first = text.split(/(?<=[a-z0-9)])\.\s/)[0].replace(/\.$/, '')
  if (first.length <= max) return first
  return first.slice(0, max).replace(/\s+\S*$/, '') + '…'
}

function dealStatus(text: string): EventFact['status'] {
  if (/\b(completed|closed|complete|now complete|absorbed|ceased to exist|acquired all outstanding|announced it acquired|had acquired)\b/i.test(text)) return 'Closed'
  if (/\b(definitive agreement|agreement to acquire|intent to acquire|to acquire|is acquiring|signed)\b/i.test(text)) return 'Announced'
  return null
}

const CAP = /^(?:[A-Z][\w&.'/-]*|AI|of)$/
const clean = (s: string) => s.replace(/[.,;]+$/, '').replace(/\s+(Inc|Ltd|Corp|Corporation|Holdings|Software Ltd)\.?$/g, '').replace(/^(?:The|With|With the)\s+/, '').trim()

/** The longest run of capitalized words ending right before `index`. */
function nameBefore(text: string, index: number): string {
  const words = text.slice(0, index).trim().split(/\s+/)
  const run: string[] = []
  for (let i = words.length - 1; i >= 0 && CAP.test(words[i]) && !/[.;]$/.test(words[i]); i--) run.unshift(words[i])
  while (run[0] === 'of') run.shift()
  return clean(run.join(' '))
}

/** The longest run of capitalized words starting at `index`. */
function nameAfter(text: string, index: number): string {
  const words = text.slice(index).trim().split(/\s+/)
  const run: string[] = []
  for (const w of words) { const bare = w.replace(/[.,;:]+$/, ''); if (!CAP.test(bare)) break; run.push(bare); if (bare !== w) break }
  while (run.at(-1) === 'of') run.pop()
  return clean(run.join(' '))
}

function deal(text: string): EventFact {
  const status = dealStatus(text)
  const verb = status === 'Announced' ? 'acquiring' : 'acquired'
  let line = ''
  const target = text.match(/\b(?:to acquire|acquisition of|acquired|acquiring)\s+(?:all outstanding equity of\s+|a majority stake in\s+)?/)
  if (target) {
    const after = nameAfter(text, target.index! + target[0].length)
    const head = text.slice(0, target.index!)
    const verbAt = head.search(/\s(?:has |had )?(?:announced|completed|closed|signed|stated|disclosed|is|its|for|it|a definitive)\b[^.]*$/)
    const before = nameBefore(text, verbAt >= 0 ? verbAt : target.index!) || nameBefore(text, target.index!)
    if (after && before && after !== before) line = `${before} ${verb} ${after}`
  }
  return { line: line || opening(text, 70), status, amount: amountWith(text, 'deal value') }
}

function funding(text: string): EventFact {
  const stage = text.match(/\b(Series [A-Z](?:\s(?:extension|\d))?|growth[- ]equity(?: investment)?|growth financing|seed|strategic funding round|equity round)\b/i)?.[1]
  const lead = text.match(/led by (?:funds managed by )?([A-Z][^,.;]*?)(?=,| with| at | achieving| bringing| in [A-Z]|\.|$)/)?.[1]
  const valuation = text.match(/(?:valuation of (?:over |approximately )?|at a |its valuation to )\$(\d[\d.,]*)\s*(billion|million)/i)
  const kind = stage ? stage.replace(/^growth[- ]equity investment$/i, 'growth equity') : 'funding round'
  const parts = [kind[0].toUpperCase() + kind.slice(1), lead ? `led by ${lead}` : null,
    valuation ? `${shortUsd(Number(valuation[1].replaceAll(',', '')) * (valuation[2].toLowerCase() === 'billion' ? 1e9 : 1e6))} valuation` : null]
  return { line: parts.filter(Boolean).join(' · '), status: null, amount: amountWith(text, 'raised') }
}

function debt(text: string): EventFact {
  if (/revolving credit facility|credit facility|credit agreement/i.test(text) && !/notes/i.test(text)) {
    const drawn = /no outstanding revolving loans/i.test(text) ? ', none drawn' : ''
    return { line: `Revolving credit line${drawn}`, status: null, amount: amountWith(text, 'available') }
  }
  if (/convertible/i.test(text)) return { line: 'Convertible notes', status: null, amount: amountWith(text, 'principal') }
  if (/term loan/i.test(text)) return { line: 'Term loan', status: null, amount: amountWith(text, 'principal') }
  if (/Item 2\.03/.test(text)) return { line: 'New financial obligation (8-K)', status: null, amount: amountWith(text, 'principal') }
  if (/amend|extend/i.test(text)) return { line: 'Credit agreement amended or extended', status: null, amount: null }
  return { line: opening(text, 70), status: null, amount: amountWith(text, 'amount') }
}

function leadership(text: string): EventFact {
  if (/^Form 8-K \(Item 5\.02\)/.test(text)) return { line: 'Officer or director change (8-K)', status: null, amount: null }
  const role = ROLES.find(([re]) => re.test(text))?.[1]
  const leaving = /\b(resign|stepped (?:down|back)|step down|retire|depart|ceased|notified)/i.test(text)
  const joining = /\b(appointed|appointment|named|join|promoted|became|succeed)/i.test(text)
  const action = joining && leaving ? 'change' : leaving ? 'departure' : joining ? 'appointed' : 'change'
  return { line: role ? `${role} ${action}` : opening(text, 70), status: null, amount: null }
}

function restructuring(text: string): EventFact {
  const pct = text.match(/(\d+(?:\.\d+)?)%\s*(?:workforce|headcount)/i) ?? text.match(/(?:workforce|headcount) reduction of (?:approximately )?(\d+(?:\.\d+)?)%/i)
  const people = text.match(/approximately ([\d,]+) employees/i)
  if (pct || people) return { line: [pct ? `${pct[1]}% workforce reduction` : 'Workforce reduction', people ? `about ${people[1]} employees` : null].filter(Boolean).join(', '), status: null, amount: amountWith(text, 'charges') }
  if (/Item 2\.05/.test(text)) return { line: 'Exit or disposal costs (8-K)', status: null, amount: null }
  const charges = /charge|cost/i.test(text) ? amountWith(text, 'charges') : null
  return { line: charges && /^(\$|Restructuring)/.test(text) ? 'Restructuring charges' : opening(text, 70), status: null, amount: charges }
}

export function eventFact(item: Pick<ChangeItem, 'type' | 'text'>): EventFact {
  switch (item.type) {
    case 'acquisition': case 'divestiture': return deal(item.text)
    case 'funding': return funding(item.text)
    case 'debt': return debt(item.text)
    case 'exec-change': return leadership(item.text)
    case 'restructuring': case 'layoff': case 'shutdown': return restructuring(item.text)
    default: return { line: opening(item.text, 70), status: null, amount: null }
  }
}
