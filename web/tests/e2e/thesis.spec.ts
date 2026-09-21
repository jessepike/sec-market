import { expect, test } from '@playwright/test'
import { issues, latestIssue } from '../../src/data/issues/index.ts'
import { newestThesisJudgment } from '../../src/data/issueHelpers.ts'
import { marketCall } from '../../src/data/market.ts'

/**
 * SEC-MARKET-FABLE-001 T6-16: the founding thesis moved off the front page
 * to its own address, /thesis/ (product-core.md §5 — "one standing analysis
 * on the site, not the site's identity"). This spec is the new home for the
 * coverage that used to live on the front page in tests/e2e/smoke.spec.ts:
 * the market-call headline, the running score, the change triggers, the
 * no-call boundaries, and the Do/Avoid panels. It also checks the front
 * page's pointer to this page, and that the front page no longer carries
 * the full argument itself.
 */
test.describe('/thesis/ — the standing thesis', () => {
  test('renders the headline, running score, change triggers, no-call boundaries and Do/Avoid', async ({
    page,
  }) => {
    const pageErrors: string[] = []
    page.on('pageerror', (error) => pageErrors.push(error.message))

    await page.goto('/thesis/')

    await expect(page.getByRole('heading', { level: 1 })).toHaveText(
      'Standing analysis: does security spending lag infrastructure spending?',
    )
    // Exactly one h1 on the page — HeroContent inside JudgmentBoard renders
    // its own heading as an h2 (see src/components/Hero.tsx), not a second h1.
    await expect(page.getByRole('heading', { level: 1 })).toHaveCount(1)

    // The heading text has a <br /> between its two sentences (see
    // src/components/Hero.tsx), which drops the space between them in
    // textContent — checked as two fragments, same as the front page smoke
    // test used to check this heading before it moved here.
    await expect(page.locator('#market-call-heading')).toBeVisible()
    await expect(page.locator('#market-call-heading')).toContainText('Infrastructure is running ahead')
    await expect(page.locator('#market-call-heading')).toContainText('Security is splitting, not booming.')

    await expect(page.locator('.thesis-running-score')).toBeVisible()

    for (const trigger of marketCall.changeTriggers) {
      await expect(page.getByText(trigger, { exact: true })).toBeVisible()
    }
    for (const boundary of marketCall.noCallBoundaries) {
      await expect(page.getByText(boundary, { exact: true })).toBeVisible()
    }

    await expect(page.getByRole('heading', { name: 'Do', exact: true })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Avoid', exact: true })).toBeVisible()
    for (const item of marketCall.actions.doItems) {
      await expect(page.getByText(item, { exact: true })).toBeVisible()
    }
    for (const item of marketCall.actions.avoidItems) {
      await expect(page.getByText(item, { exact: true })).toBeVisible()
    }

    await expect(page.getByRole('link', { name: 'Back to the front page' })).toHaveAttribute('href', '/')

    expect(pageErrors).toEqual([])
  })

  test('an evidence chip opens the drawer', async ({ page }) => {
    await page.goto('/thesis/')

    await page.locator('#read').getByRole('button', { name: /Sources/ }).first().click()

    const dialog = page.getByRole('dialog', { name: 'Evidence' })
    await expect(dialog).toBeVisible()

    await page.keyboard.press('Escape')
    await expect(dialog).toBeHidden()
  })

  test('front page: the #read pointer links to /thesis/, and the full argument is gone', async ({ page }) => {
    await page.goto('/')

    const pointer = page.locator('#read')
    await expect(pointer).toBeVisible()
    await expect(pointer).toContainText('Does security spending lag infrastructure spending?')
    await expect(pointer).toContainText(marketCall.headline)
    await expect(pointer.getByRole('link', { name: 'Read the analysis and its record' })).toHaveAttribute(
      'href',
      '/thesis/',
    )

    // The full standing argument — the change-trigger list, the Do/Avoid
    // panels, the market-call heading itself — left the front page entirely.
    await expect(page.locator('#market-call-heading')).toHaveCount(0)
    await expect(page.getByRole('heading', { name: 'Do', exact: true })).toHaveCount(0)
    await expect(page.getByRole('heading', { name: 'Avoid', exact: true })).toHaveCount(0)
    for (const trigger of marketCall.changeTriggers) {
      await expect(page.getByText(trigger, { exact: true })).toHaveCount(0)
    }

    // "Thesis" left the top nav; "Standing analysis" is the secondary link
    // that replaces it (see src/components/NextEdition.tsx).
    await expect(page.locator('.site-header').getByRole('link', { name: 'Thesis' })).toHaveCount(0)
    await expect(page.getByRole('link', { name: 'Standing analysis' })).toHaveAttribute('href', '/thesis/')

    // #we-think's own thesis line is condensed to a pointer here too — but
    // only when the newest issue actually carries a verdict. Since build 3
    // (SEC-MARKET-PUBLISH-001 §3) the thesis left the weekly issue, so the
    // newest issue very often has none, and #we-think must then render
    // neither the pointer nor an empty/"null" block (see WeThink.tsx).
    const latestThesis =
      latestIssue.status === 'published' ? latestIssue.weThink.thesis : (latestIssue.proposed?.thesis ?? null)
    if (latestThesis) {
      await expect(page.locator('#we-think')).toContainText('Standing analysis:')
      await expect(page.locator('#we-think').getByRole('link', { name: 'See the record.' })).toHaveAttribute(
        'href',
        '/thesis/',
      )
    } else {
      await expect(page.locator('#we-think')).not.toContainText('Standing analysis:')
      await expect(page.locator('#we-think')).not.toContainText('null')
    }

    // The pointer's JUDGED stamp is the newest published issue's actual
    // signed thesis date (SEC-MARKET-FABLE-001 T6-16 fix), not the site's
    // LAST_UPDATED stamp — read here from the data the way the page itself
    // computes it (newestThesisJudgment), not hard-coded.
    const judgment = newestThesisJudgment(issues)
    expect(judgment).not.toBeNull()
    await expect(pointer.locator('.stamp-label time')).toHaveAttribute('datetime', judgment!.signedOn)
    await expect(pointer.locator('.stamp-label')).toContainText(judgment!.signedBy)
  })
})
