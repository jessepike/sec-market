import { expect, test } from '@playwright/test'
import { issues, latestIssue } from '../../src/data/issues/index.ts'

const STANDING_REFERENCE_IDS = ['market', 'follow', 'read', 'landscape', 'platforms', 'hypotheses', 'prints']
const ISSUE_SECTION_IDS = ['overview', 'formation', 'absorption', 'prints-this-week', 'capital', 'we-think']

test.describe('weekly issue — front page', () => {
  test('h1 is the newest issue read; issue sections and standing reference are visible', async ({
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

    await expect(page.getByRole('heading', { level: 1 })).toHaveText(latestIssue.read)

    for (const id of ISSUE_SECTION_IDS) {
      await expect(page.locator(`#${id}`)).toBeVisible()
    }
    for (const id of STANDING_REFERENCE_IDS) {
      await expect(page.locator(`#${id}`)).toBeVisible()
    }

    const draftBanner = page.locator('.issue-hero .issue-draft-banner')
    if (latestIssue.status === 'draft') {
      await expect(draftBanner).toBeVisible()
    } else {
      await expect(draftBanner).toHaveCount(0)
    }

    expect(pageErrors).toEqual([])
    expect(consoleErrors).toEqual([])
  })

  test('/issues/ lists every issue', async ({ page }) => {
    await page.goto('/issues/')
    await expect(page.getByRole('heading', { level: 1 })).toHaveText('Issues')
    for (const issue of issues) {
      await expect(page.locator('.issue-archive__list').getByText(issue.id, { exact: true })).toBeVisible()
    }
  })

  test('/issues/<newest>/ renders with the same h1', async ({ page }) => {
    await page.goto(`/issues/${latestIssue.id}/`)
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

  // F7: on the permalink page, "Thesis" (#read) has no local target — the
  // click must fall through to a real navigation to /#read on the front
  // page, not a same-page no-op.
  test('permalink page: clicking "Thesis" navigates to the front page at #read', async ({
    page,
  }) => {
    await page.goto(`/issues/${latestIssue.id}/`)

    const navToggle = page.locator('.nav-toggle')
    if (await navToggle.isVisible()) {
      await navToggle.click()
    }

    await page.getByRole('link', { name: 'Thesis' }).click()
    await page.waitForURL(/\/#read$/)

    expect(new URL(page.url()).hash).toBe('#read')
    await expect(page.locator('#read')).toBeVisible()
  })
})
