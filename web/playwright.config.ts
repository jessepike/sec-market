import { defineConfig, devices } from '@playwright/test'

const baseURL = process.env.E2E_BASE_URL ?? 'http://127.0.0.1:4173'

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: false,
  retries: 0,
  reporter: 'line',
  use: {
    baseURL,
    trace: 'retain-on-failure',
  },
  projects: [
    // Existing single-width smoke coverage. Kept separate from issue.spec.ts
    // (which needs both widths below) so smoke does not also run at 390 —
    // the print scorecard groups collapse below the 769px breakpoint, and
    // smoke's heading-visibility assertions assume the desktop, open state.
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
      testIgnore: /issue\.spec\.ts/,
    },
    // Spec §7: tests/e2e/issue.spec.ts runs at both 1440×900 and 390×844.
    {
      name: 'desktop',
      use: { ...devices['Desktop Chrome'], viewport: { width: 1440, height: 900 } },
      testMatch: /issue\.spec\.ts/,
    },
    {
      name: 'phone',
      use: { ...devices['Desktop Chrome'], viewport: { width: 390, height: 844 } },
      testMatch: /issue\.spec\.ts/,
    },
  ],
  // When E2E_BASE_URL is set (e.g. the live preview URL), there is nothing
  // local to serve — Playwright hits the deployed site directly and no
  // webServer is started.
  webServer: process.env.E2E_BASE_URL
    ? undefined
    : {
        command: 'npm run preview -- --host 127.0.0.1 --port 4173',
        url: 'http://127.0.0.1:4173',
        reuseExistingServer: true,
        timeout: 30_000,
      },
})
