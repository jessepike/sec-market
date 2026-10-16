import { readFileSync } from 'node:fs'
import { spawnSync } from 'node:child_process'
import { resolve } from 'node:path'

// Runs the Playwright suite against the local build (dist/) or, with
// E2E_BASE_URL set, against a deployed site. Either target must carry its
// app-release.json receipt, which proves it is a gated certified build.
if (process.env.E2E_BASE_URL) {
  const response = await fetch(`${process.env.E2E_BASE_URL.replace(/\/$/, '')}/app-release.json`, { signal: AbortSignal.timeout(20000) })
  if (!response.ok || !response.headers.get('content-type')?.includes('json')) throw new Error('Browser target lacks its declared app release receipt.')
} else JSON.parse(readFileSync('dist/app-release.json', 'utf8'))
const result = spawnSync(process.execPath, [resolve('node_modules/@playwright/test/cli.js'), 'test', ...process.argv.slice(2)], { stdio: 'inherit', env: process.env })
process.exitCode = result.status ?? 1
