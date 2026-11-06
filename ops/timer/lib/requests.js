// Public "Want a company tracked?" box (SEC-081).
// A visitor types a company name. The name lands in one private GitHub issue
// that lists every request with a count. Nothing reaches the site: the owner
// decides what to add. The token asked for here can touch issues only.
import { client, githubToken } from './core.js'

export const QUEUE_TITLE = 'Company requests from the site'
export const QUEUE_LABEL = 'company-request'
const START = '<!-- company-requests:'
const END = '-->'
const DEFAULT_ORIGINS = ['https://securitymarketpulse.com', 'https://www.securitymarketpulse.com',
  'https://security-market-pulse-git-preview-pikeholdings.vercel.app']
export const LIMITS = { minChars: 2, maxChars: 60, maxBody: 1000, minMillis: 1500, newPerDay: 10, maxEntries: 500 }

export function origins(env) {
  return env.REQUEST_ORIGINS ? env.REQUEST_ORIGINS.split(',').map(s => s.trim()).filter(Boolean) : DEFAULT_ORIGINS
}

// Letters, digits, spaces and . & ' + - only. No links, no markup, no email.
export function cleanName(raw) {
  if (typeof raw !== 'string') return null
  const name = raw.normalize('NFKC').replace(/\s+/g, ' ').trim()
  if (name.length < LIMITS.minChars || name.length > LIMITS.maxChars) return null
  if (!/^[\p{L}\p{N} .&'+-]+$/u.test(name) || !/\p{L}/u.test(name)) return null
  if (/\b(www|https?)\b|\.(com|net|org|io|ru|xyz)\b/i.test(name)) return null
  return name
}

export const nameKey = name => name.toLowerCase().replace(/[^\p{L}\p{N}]+/gu, '')

// The issue body keeps the list as JSON in a comment and shows it as a table.
export function readQueue(body = '') {
  const at = body.indexOf(START)
  if (at < 0) return []
  try {
    const list = JSON.parse(body.slice(at + START.length, body.indexOf(END, at)))
    return Array.isArray(list) ? list : []
  } catch { return [] }
}

export function writeQueue(list) {
  const rows = [...list].sort((a, b) => b.count - a.count || a.name.localeCompare(b.name))
    .map(r => `| ${r.name} | ${r.count} | ${r.first} | ${r.last} |`)
  return ['Names typed into the "Want a company tracked?" box on the site. Nothing here is published.',
    'Ask Claude to add a company, or ignore it. Close this issue to start a fresh list.', '',
    '| Company | Requests | First | Last |', '|---|---|---|---|', ...rows, '',
    START + JSON.stringify(list) + END].join('\n')
}

// Adds one request. Returns the new list and whether the name is new.
export function addRequest(list, name, today) {
  const key = nameKey(name)
  const found = list.find(r => nameKey(r.name) === key)
  if (found) return { list: list.map(r => r === found ? { ...r, count: r.count + 1, last: today } : r), added: false, dropped: false }
  const newToday = list.filter(r => r.first === today).length
  if (newToday >= LIMITS.newPerDay || list.length >= LIMITS.maxEntries) return { list, added: false, dropped: true }
  return { list: [...list, { name, count: 1, first: today, last: today }], added: true, dropped: false }
}

function cors(origin) {
  return { 'access-control-allow-origin': origin, 'access-control-allow-methods': 'POST, OPTIONS',
           'access-control-allow-headers': 'content-type', 'access-control-max-age': '86400', vary: 'origin',
           'cache-control': 'no-store' }
}

export async function handle(request, env, fetcher = fetch, now = Date.now()) {
  const origin = request.headers.get('origin') || ''
  if (!origins(env).includes(origin)) return new Response('forbidden', { status: 403 })
  const headers = cors(origin)
  if (request.method === 'OPTIONS') return new Response(null, { status: 204, headers })
  if (request.method !== 'POST') return new Response('method not allowed', { status: 405, headers })
  const text = await request.text()
  if (text.length > LIMITS.maxBody) return Response.json({ ok: false, error: 'too_long' }, { status: 413, headers })
  let input
  try { input = JSON.parse(text) } catch { return Response.json({ ok: false, error: 'bad_request' }, { status: 400, headers }) }
  // Bots fill the hidden field or submit instantly. Tell them it worked.
  if (input.website || !(Number(input.elapsed) >= LIMITS.minMillis)) return Response.json({ ok: true }, { headers })
  const name = cleanName(input.name)
  if (!name) return Response.json({ ok: false, error: 'invalid_name' }, { status: 400, headers })
  try {
    await record(env, name, fetcher, now)
    return Response.json({ ok: true }, { headers })
  } catch (error) {
    console.error('company request failed', String(error.message || error))
    return Response.json({ ok: false, error: 'unavailable' }, { status: 503, headers })
  }
}

export async function record(cfg, name, fetcher = fetch, now = Date.now()) {
  const token = await githubToken(cfg, fetcher, now, { issues: 'write', metadata: 'read' })
  const gh = client(token, fetcher)
  const repo = `/repos/${cfg.GITHUB_REPO}`
  const today = new Date(now).toISOString().slice(0, 10)
  const open = await gh(`${repo}/issues?state=open&labels=${QUEUE_LABEL}&per_page=10`)
  const issue = open.find(i => i.title === QUEUE_TITLE && !i.pull_request)
  const { list, added, dropped } = addRequest(issue ? readQueue(issue.body) : [], name, today)
  if (dropped) return { added: false, dropped: true }
  const body = writeQueue(list)
  if (!issue) {
    await gh(`${repo}/issues`, { method: 'POST', body: JSON.stringify({ title: QUEUE_TITLE, body,
      labels: [QUEUE_LABEL], assignees: [cfg.ASSIGNEE || cfg.GITHUB_REPO.split('/')[0]] }) })
    return { added, dropped: false, created: true }
  }
  await gh(`${repo}/issues/${issue.number}`, { method: 'PATCH', body: JSON.stringify({ body }) })
  // Only a new name sends a notification. Repeat requests just raise the count.
  if (added) await gh(`${repo}/issues/${issue.number}/comments`, { method: 'POST', body: JSON.stringify({ body: `New company request: ${name}` }) })
  return { added, dropped: false, created: false }
}
