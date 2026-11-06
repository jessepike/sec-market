#!/usr/bin/env node
// Print the site health checks without writing anything:
//   GITHUB_TOKEN=$(gh auth token) node ops/timer/health-cli.mjs
// Add --json for machine output.
import { client } from './lib/core.js'
import { assess, overall } from './lib/health.js'

const env = process.env
const cfg = { GITHUB_REPO: env.GITHUB_REPO || 'jessepike/sec-market', WORKFLOW_FILE: env.WORKFLOW_FILE || 'subscription-collector.yml',
  DATA_URL: env.DATA_URL || 'https://securitymarketpulse.com/daily-coverage.json', MAX_AGE_HOURS: Number(env.MAX_AGE_HOURS || 30),
  REF: env.WORKFLOW_REF || 'main', ...Object.fromEntries(Object.entries(env).filter(([k]) => /^(PUBLISHER|FUNDING|OBSERVER|BUILD)_FILE$|^LIVE_PATHS$|^REQUEST_URL$|^ACTIONS_/.test(k))) }
if (!env.GITHUB_TOKEN) { console.error('Set GITHUB_TOKEN (for example $(gh auth token)).'); process.exit(2) }
const { checks } = await assess(cfg, client(env.GITHUB_TOKEN, fetch))
if (process.argv.includes('--json')) console.log(JSON.stringify(checks, null, 2))
else {
  const mark = { ok: 'OK  ', warn: 'WARN', fail: 'FAIL', none: 'INFO' }
  console.log(overall(checks).title)
  for (const c of checks) console.log(`${mark[c.status]}  ${c.label}: ${c.detail}`)
}
process.exit(checks.some(c => c.status === 'fail') ? 1 : 0)
