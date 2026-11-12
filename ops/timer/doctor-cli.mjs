#!/usr/bin/env node
// Run the pipeline doctor's diagnosis without acting (always a dry run):
//   node ops/timer/doctor-cli.mjs [--json]   (uses gh; or set GITHUB_TOKEN)
// The repair step (docs/reference/repair-loop.md) starts here. Exit 0 when
// nothing needs repair, 3 when the repair step or the owner is needed.
import { execFileSync } from 'node:child_process'
import { client } from './lib/core.js'
import { doctor } from './lib/doctor.js'

const env = process.env
// Without GITHUB_TOKEN, read through the gh CLI (works behind proxies where the
// raw token is not usable). Reads only: the doctor runs as a dry run here.
const viaGh = async path => JSON.parse(execFileSync('gh', ['api', path.replace(/^\//, '')], { encoding: 'utf8', maxBuffer: 1 << 26 }))
const gh = env.GITHUB_TOKEN ? client(env.GITHUB_TOKEN, fetch) : viaGh
const cfg = { GITHUB_REPO: env.GITHUB_REPO || 'jessepike/sec-market', WORKFLOW_FILE: env.WORKFLOW_FILE || 'subscription-collector.yml',
  DATA_URL: env.DATA_URL || 'https://securitymarketpulse.com/daily-coverage.json', REF: env.WORKFLOW_REF || 'main',
  ...Object.fromEntries(Object.entries(env).filter(([k]) => /^(PUBLISHER|GATE)_FILE$|^COLLECT_|^GATES_PER_DAY$/.test(k))),
  DOCTOR_DRY_RUN: 'true' }
// The cloud sandbox cannot reach the live site. Pass the live checkedAt from
// another route (for example the Vercel connector) with --live-at <iso>.
const i = process.argv.indexOf('--live-at')
const liveAt = i > 0 ? process.argv[i + 1] : null
const fetcher = liveAt ? async () => ({ ok: true, json: async () => ({ checkedAt: liveAt }) }) : fetch
const r = await doctor(cfg, gh, fetcher)
if (process.argv.includes('--json')) console.log(JSON.stringify(r, null, 2))
else {
  console.log(`${r.code}: ${r.summary}`)
  for (const f of r.facts) console.log(`  - ${f}`)
  for (const f of r.findings) console.log(`${f.code} [${f.handling}] ${f.summary}\n  plan: ${f.plan.step} (${f.plan.why}); escalate: ${f.plan.escalate}`)
}
process.exit(r.escalate.length ? 3 : 0)
