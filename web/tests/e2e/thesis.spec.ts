import { expect, test } from '@playwright/test'
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

    // D-76/autonomy-coverage-plan.md §3, step 1: /thesis/ is kept as a dated
    // record and carries a plain notice saying so, above the unaltered
    // argument checked above.
    await expect(page.getByText('This analysis is kept as a dated record and is no longer updated.')).toBeVisible()

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

  /**
   * D-76/autonomy-coverage-plan.md §3, step 1: the front page no longer
   * carries any judgment, including the compact #read pointer this test used
   * to check. The full standing argument stays only at /thesis/, reached
   * from a plain link (ArchiveLinks' "Standing thesis"), never quoted or
   * pointed to inline on a live page.
   *
   * AUTO-001 fix pass (2026-09-26), item 4: this link used to be
   * NextEdition's "Standing analysis" (inside the now-removed "How a
   * posture is set" band); ArchiveLinks already carried the same /thesis/
   * link under "Standing thesis", so that one link row was not rebuilt.
   */
  test('front page: no #read pointer, no #we-think, and the full argument is gone', async ({ page }) => {
    await page.goto('/')

    await expect(page.locator('#read')).toHaveCount(0)
    await expect(page.locator('#we-think')).toHaveCount(0)
    await expect(page.locator('#hypotheses')).toHaveCount(0)

    // The full standing argument — the change-trigger list, the Do/Avoid
    // panels, the market-call heading itself — is not on the front page.
    await expect(page.locator('#market-call-heading')).toHaveCount(0)
    await expect(page.getByRole('heading', { name: 'Do', exact: true })).toHaveCount(0)
    await expect(page.getByRole('heading', { name: 'Avoid', exact: true })).toHaveCount(0)
    for (const trigger of marketCall.changeTriggers) {
      await expect(page.getByText(trigger, { exact: true })).toHaveCount(0)
    }

    // "Thesis" left the top nav; "Standing thesis" is the plain link to the
    // archived record (see src/components/ArchiveLinks.tsx).
    await expect(page.locator('.site-header').getByRole('link', { name: 'Thesis' })).toHaveCount(0)
    await expect(page.getByRole('link', { name: 'Standing thesis' })).toHaveAttribute('href', '/thesis/')
  })
})
