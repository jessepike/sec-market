import { spawnSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'

// Existing GitHub web CI calls npm test without installing Playwright's browser.
// Keep local system-Chrome tests unchanged; supply the reviewed test dependency in CI.
if (process.env.CI === 'true' && process.platform === 'linux') {
  const cli = fileURLToPath(new URL('../node_modules/playwright/cli.js', import.meta.url))
  const result = spawnSync(process.execPath, [cli, 'install', '--with-deps', 'chromium'], { stdio: 'inherit' })
  if (result.status !== 0) process.exit(result.status ?? 1)
}
