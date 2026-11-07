import { expect, test } from '@playwright/test'
import { issues, latestIssue } from '../../src/data/issues/index.ts'
import { SITE_HEADLINE } from '../../src/data/meta.ts'

// D-76/autonomy-coverage-plan.md §3, step 1: 'read' (the standing-thesis
// pointer) and 'hypotheses' left the front page's always-visible sections —
// the site publishes sourced facts only, no judgments, there. 'overview' now
// names RunStatus rather than the old issue strip, and 'we-think' ("What we
// now think") is gone from the front page entirely — it survives, unchanged,
// on the issue permalink, where ISSUE_SECTION_IDS below still applies.
// Step 1 fix pass, item 3: 'platforms' (Platform pressure) also dropped —
// the whole section, not just its judged column, stopped rendering on the
// front page because every row carried a hand-assigned vendor-position label.
//
// Step 5 (autonomy-coverage-plan.md §3): the front page's own lane ids
// changed again. 'formation', 'absorption', 'prints-this-week', and
// 'capital' were IssueLanes ids that used to render on both the front page
// and the issue permalink; IssueLanes no longer mounts on the front page at
// all (App.tsx's FrontPage doc-comment), so those four now only exist on
// `/issues/<id>/` — ISSUE_SECTION_IDS below (unchanged) still checks them
// there. 'prints' (PrintGrid's heading id) is also gone from the front page
// — smoke.spec.ts asserts `#prints-heading` has count 0 there. The front
// page's own standing-reference ids are TRACKER_FRONT_IDS: the twelve-domain
// tracker (`market`) and its two supporting sections, plus `follow`.
// AUTO-001 fix pass (2026-09-26), item 4: 'landscape' is dropped —
// DomainBoard's LandscapeSection no longer renders on any route.
const TRACKER_FRONT_IDS = ['tracker-changed', 'momentum', 'follow']
const ISSUE_SECTION_IDS = ['overview', 'formation', 'absorption', 'prints-this-week', 'capital', 'we-think']

test.describe('weekly issue — front page', () => {
  test('h1 is the site headline, run status is visible; the tracker and standing reference are visible', async ({
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
    await expect(page.locator('.site-masthead__stamps a')).toHaveAttribute('href', '/method/#overview')

    for (const id of TRACKER_FRONT_IDS) {
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
  // a nav target — see tests/e2e/thesis.spec.ts). AUTO-001 fix pass
  // (2026-09-26): "Landscape" (#landscape) was this regression's exercise
  // target until DomainBoard's LandscapeSection stopped rendering on any
  // route (item 4); "What changed" (#tracker-changed) is a front-page-only hash item,
  // absent from the issue permalink, and exercises the same regression.
  test('permalink page: the nav reaches the market page and marks it current', async ({
    page,
  }) => {
    await page.goto(`/issues/${latestIssue.id}/`)

    const navToggle = page.locator('.nav-toggle')
    if (await navToggle.isVisible()) {
      await navToggle.click()
    }

    // exact: true — the brand link's own accessible name ("Security Market
    // Pulse") also contains the substring "Market", which a non-exact match
    // resolves ambiguously against the nav's "Market" link.
    await page.locator('.site-header').getByRole('link', { name: 'Market', exact: true }).click()
    await page.waitForURL(/\/market\/$/)
    if (await navToggle.isVisible()) await navToggle.click()
    await expect(page.locator('.site-header').getByRole('link', { name: 'Market', exact: true })).toHaveAttribute('aria-current', 'page')
    await expect(page.getByRole('heading', { level: 1 })).toHaveText('Market')
  })
})
