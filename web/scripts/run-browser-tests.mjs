import { readFileSync } from 'node:fs'
import { spawnSync } from 'node:child_process'
import { resolve } from 'node:path'

let release
if (process.env.E2E_BASE_URL) {
  const response = await fetch(`${process.env.E2E_BASE_URL.replace(/\/$/, '')}/app-release.json`, { signal: AbortSignal.timeout(20000) })
  if (!response.ok || !response.headers.get('content-type')?.includes('json')) throw new Error('Browser target lacks its declared app release receipt.')
  release = await response.json()
} else release = JSON.parse(readFileSync('dist/app-release.json', 'utf8'))
const config = release.rootView === 'published' ? ['--config', 'published-app/playwright.config.ts'] : []
const result = spawnSync(process.execPath, [resolve('node_modules/@playwright/test/cli.js'), 'test', ...config, ...process.argv.slice(2)], { stdio: 'inherit', env: process.env })
process.exitCode = result.status ?? 1
