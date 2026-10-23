import { spawnSync } from 'node:child_process'
import { fileURLToPath, pathToFileURL } from 'node:url'

export async function ensureBrowser({ launch, install }) {
  const probe = async () => { const browser = await launch(); await browser.close() }
  try { await probe(); return } catch (error) {
    if (/Executable doesn't exist|browser executable.*not found/i.test(String(error))) {
      install(['install', 'chromium'])
      try { await probe(); return } catch (afterDownload) { error = afterDownload }
    }
    if (!/Host system is missing dependencies|error while loading shared libraries|cannot open shared object file/i.test(String(error))) throw error
    // Install OS packages only after an actual launch proves they are absent.
    install(['install-deps', 'chromium'])
    await probe()
  }
}

export async function main() {
  if (process.env.CI !== 'true' || process.platform !== 'linux') return
  const { chromium } = await import('playwright')
  const cli = fileURLToPath(new URL('../node_modules/playwright/cli.js', import.meta.url))
  await ensureBrowser({
    launch: () => chromium.launch({ timeout: 30_000 }),
    install: args => {
      // GNU timeout terminates the download/apt process group. Setup failure
      // fails the gate; the full browser suite never skips.
      const result = spawnSync('timeout', ['--kill-after=10s', '180s', process.execPath, cli, ...args],
        { stdio: 'inherit', timeout: 200_000 })
      if (result.error || result.status !== 0) throw new Error(`Browser setup failed (${result.status ?? result.error?.code}): playwright ${args.join(' ')}`)
    },
  })
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  main().catch(error => { console.error(error.message); process.exitCode = 1 })
}
