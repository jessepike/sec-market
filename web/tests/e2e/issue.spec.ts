import { expect, test } from '@playwright/test'
import { issues, latestIssue } from '../../src/data/issues/index.ts'
import { SITE_HEADLINE } from '../../src/data/meta.ts'

// D-76/autonomy-coverage-plan.md §3, step 1: 'read' (the standing-thesis
// pointer) and 'hypotheses' left the front page's always-visible sections —
// the site publishes sourced facts only, no judgments, there. The front
// page's four lane ids stay, but 'overview' now names RunStatus rather than
// the old issue strip, and 'we-think' ("What we now think") is gone from the
// front page entirely — both survive, unchanged, on the issue permalink.
// Step 1 fix pass, item 3: 'platforms' (Platform pressure) also dropped —
// the whole section, not just its judged column, stopped rendering on the
// front page because every row carried a hand-assigned vendor-position label.
const STANDING_REFERENCE_IDS = ['market', 'follow', 'landscape', 'prints']
const FRONT_LANE_IDS = ['overview', 'formation', 'absorption', 'prints-this-week', 'capital']
const ISSUE_SECTION_IDS = ['overview', 'formation', 'absorption', 'prints-this-week', 'capital', 'we-think']

test.describe('weekly issue — front page', () => {
  test('h1 is the site headline, run status is visible; issue lanes and standing reference are visible', async ({
    page,
  }) => {
    const pageErrors: string[] = []
    const consoleErrors: string[] = []
    let expectedAnalytics404 = false
    page.on('pageerror', (error) => pageErrors.push(error.message))
    page.on('response', (response) => {
      // @vercel/analytics's <Analytics /> requests /_vercel/insights/script.js,
      // a path Vercel's edge serves in production but that 404s against any
      // local build (vite preview, or the OrbStack dev VM) — expected here,
      // not a defect in this page. Chromium logs it as the browser's generic
      // "Failed to load resource" console error, with no URL in the message
      // text, so this flags it via the network response instead.
      if (response.status() === 404 && response.url().includes('/_vercel/insights/script.js')) {
        expectedAnalytics404 = true
      }
    })
    page.on('console', (message) => {
      if (message.type() !== 'error') return
      if (
        expectedAnalytics404 &&
        message.text() === 'Failed to load resource: the server responded with a status of 404 (Not Found)'
      ) {
        expectedAnalytics404 = false // consume: only swallow one match per known 404
        return
      }
      consoleErrors.push(message.text())
    })

    await page.goto('/')

    // SEC-MARKET-CORE-001 §5: the front page's h1 is the site's own subject
    // and does not change week to week. RunStatus, not a weekly-issue read,
    // is the first thing below it now (D-76/autonomy-coverage-plan.md §3,
    // step 1) — the issue permalink below still has the read as its h1.
    await expect(page.getByRole('heading', { level: 1 })).toHaveText(SITE_HEADLINE)
    await expect(page.locator('#overview .run-status__line')).toContainText('Figures checked')

    for (const id of FRONT_LANE_IDS) {
      await expect(page.locator(`#${id}`)).toBeVisible()
    }
    for (const id of STANDING_REFERENCE_IDS) {
      await expect(page.locator(`#${id}`)).toBeVisible()
    }

    // The old "Draft. Not yet signed." banner lived in the issue strip this
    // pass removed from the front page — that status now surfaces only on
    // the issue permalink (checked in "renders with the same h1" below).
    await expect(page.locator('.run-status .issue-draft-banner')).toHaveCount(0)

    expect(pageErrors).toEqual([])
    expect(consoleErrors).toEqual([])
  })

  test('/issues/ lists every issue and carries the discontinuation notice', async ({ page }) => {
    await page.goto('/issues/')
    await expect(page.getByRole('heading', { level: 1 })).toHaveText('Issues')
    await expect(page.locator('.archive-notice')).toContainText(
      'Signed weekly issues were discontinued on 25 September 2026',
    )
    for (const issue of issues) {
      await expect(page.locator('.issue-archive__list').getByText(issue.id, { exact: true })).toBeVisible()
    }
  })

  test('/issues/<newest>/ renders with the same h1 and the discontinuation notice, content unaltered', async ({
    page,
  }) => {
    await page.goto(`/issues/${latestIssue.id}/`)
    await expect(page.locator('.archive-notice')).toContainText(
      'Signed weekly issues were discontinued on 25 September 2026',
    )
    await expect(page.getByRole('heading', { level: 1 })).toHaveText(latestIssue.read)
    for (const id of ISSUE_SECTION_IDS) {
      await expect(page.locator(`#${id}`)).toBeVisible()
    }
  })

  test('/feed.xml returns 200 with an XML content type', async ({ request }) => {
    const response = await request.get('/feed.xml')
    expect(response.status()).toBe(200)
    const contentType = response.headers()['content-type'] ?? ''
    expect(contentType).toMatch(/xml/)
  })

  test('/issues/<newest>.json parses with a non-empty evidence array', async ({ request }) => {
    const response = await request.get(`/issues/${latestIssue.id}.json`)
    expect(response.status()).toBe(200)
    const body = await response.json()
    expect(body.issue.id).toBe(latestIssue.id)
    expect(Array.isArray(body.evidence)).toBe(true)
    expect(body.evidence.length).toBeGreaterThan(0)
  })

  // F7: on the permalink page, a front-page-only nav hash target has no local
  // target — the click must fall through to a real navigation to /#<id> on
  // the front page, not a same-page no-op. This used to be exercised through
  // "Thesis" (#read); under SEC-MARKET-FABLE-001 T6-16 "Thesis" left the top
  // nav entirely (product-core.md §5 — the founding thesis moved to its own
  // page, /thesis/, and #read on the front page is now a compact pointer, not
  // a nav target — see tests/e2e/thesis.spec.ts). "Landscape" (#landscape) is
  // still a front-page-only hash item and exercises the same regression.
  test('permalink page: clicking "Landscape" navigates to the front page at #landscape', async ({
    page,
  }) => {
    await page.goto(`/issues/${latestIssue.id}/`)

    const navToggle = page.locator('.nav-toggle')
    if (await navToggle.isVisible()) {
      await navToggle.click()
    }

    await page.getByRole('link', { name: 'Landscape' }).click()
    await page.waitForURL(/\/#landscape$/)

    expect(new URL(page.url()).hash).toBe('#landscape')
    await expect(page.locator('#landscape')).toBeVisible()
  })
})
