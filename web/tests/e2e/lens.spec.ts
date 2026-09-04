import { expect, test } from '@playwright/test'
import { latestIssue } from '../../src/data/issues/index.ts'
import { vendorPrints } from '../../src/data/prints.ts'

// Real slugs from the 2026-w36 data (both appear on an issue item's `vendors`
// and on a VendorPrint's derived `vendorSlug`, so filtering has something to
// show on both surfaces).
const LENS_SLUGS = ['crowdstrike', 'zscaler']
const UNKNOWN_SLUG = 'not-a-real-vendor'

function totalIssueItems(): number {
  return latestIssue.sections.reduce((sum, section) => sum + section.items.length, 0)
}

function matchingIssueItems(slugs: string[]): number {
  return latestIssue.sections.reduce(
    (sum, section) =>
      sum +
      section.items.filter((item) => (item.vendors ?? []).some((vendor) => slugs.includes(vendor)))
        .length,
    0,
  )
}

function matchingPrints(slugs: string[]): number {
  return vendorPrints.filter((print) => print.vendorSlug !== undefined && slugs.includes(print.vendorSlug))
    .length
}

function trackConsole(page: import('@playwright/test').Page) {
  const pageErrors: string[] = []
  const consoleErrors: string[] = []
  page.on('pageerror', (error) => pageErrors.push(error.message))
  page.on('console', (message) => {
    if (message.type() !== 'error') return
    // Known, expected 404 in every local/preview build — see the identical
    // guard in tests/e2e/issue.spec.ts.
    if (message.text().includes('404') && message.text().includes('Failed to load resource')) return
    consoleErrors.push(message.text())
  })
  return { pageErrors, consoleErrors }
}

test.describe('vendor lens', () => {
  test('?vendors= filters both the issue items and the scorecard, showing Showing N of M on each', async ({
    page,
  }) => {
    const { pageErrors, consoleErrors } = trackConsole(page)

    await page.goto(`/?vendors=${LENS_SLUGS.join(',')}`)

    const expectedItems = matchingIssueItems(LENS_SLUGS)
    const expectedPrints = matchingPrints(LENS_SLUGS)

    await expect(page.locator('.issue-lane__filter-status')).toContainText(
      `Showing ${expectedItems} of ${totalIssueItems()}`,
    )
    await expect(page.locator('.print-grid__filter-status')).toContainText(
      `Showing ${expectedPrints} of ${vendorPrints.length}`,
    )

    expect(pageErrors).toEqual([])
    expect(consoleErrors).toEqual([])
  })

  test('an unknown slug yields Showing 0 of M and a clear link, not an error', async ({ page }) => {
    const { pageErrors, consoleErrors } = trackConsole(page)

    await page.goto(`/?vendors=${UNKNOWN_SLUG}`)

    await expect(page.locator('.issue-lane__filter-status')).toContainText(
      `Showing 0 of ${totalIssueItems()}`,
    )
    await expect(page.locator('.print-grid__filter-status')).toContainText(
      `Showing 0 of ${vendorPrints.length}`,
    )
    await expect(page.locator('#vendor-lens-slot .vendor-lens__clear')).toBeVisible()

    expect(pageErrors).toEqual([])
    expect(consoleErrors).toEqual([])
  })

  test('the clear link restores the unfiltered URL', async ({ page }) => {
    await page.goto(`/?vendors=${LENS_SLUGS.join(',')}`)
    await expect(page.locator('#vendor-lens-slot .vendor-lens__clear')).toBeVisible()

    await page.locator('#vendor-lens-slot .vendor-lens__clear').click()

    await expect.poll(() => new URL(page.url()).search).toBe('')
    await expect(page.locator('#vendor-lens-slot .vendor-lens__clear')).toHaveCount(0)
    await expect(page.locator('.issue-lane__filter-status')).toHaveCount(0)
    await expect(page.locator('.print-grid__filter-status')).toHaveCount(0)
  })

  test('the URL round-trips through the control: toggling a chip off updates it and re-filters', async ({
    page,
  }) => {
    await page.goto(`/?vendors=${LENS_SLUGS.join(',')}`)
    await expect(page.locator('.vendor-lens__chip')).toHaveCount(LENS_SLUGS.length)

    await page.locator('.vendor-lens__chip').first().click()

    await expect.poll(() => new URL(page.url()).search).toBe(`?vendors=${LENS_SLUGS[1]}`)
    await expect(page.locator('.vendor-lens__chip')).toHaveCount(LENS_SLUGS.length - 1)

    const expectedItems = matchingIssueItems([LENS_SLUGS[1]])
    await expect(page.locator('.issue-lane__filter-status')).toContainText(
      `Showing ${expectedItems} of ${totalIssueItems()}`,
    )
  })

  test('at 390 the chip row is reachable and scrollable', async ({ page }, testInfo) => {
    test.skip(testInfo.project.name !== 'phone', 'chip-row scroll behaviour is a phone-only assertion')

    await page.goto(`/?vendors=${LENS_SLUGS.join(',')}`)

    const chipRow = page.locator('.vendor-lens__chips')
    await expect(chipRow).toBeVisible()
    await expect(page.locator('.vendor-lens__chip').first()).toBeVisible()

    const overflowX = await chipRow.evaluate((el) => getComputedStyle(el).overflowX)
    expect(overflowX).toBe('auto')
  })
})
