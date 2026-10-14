import { expect, test } from '@playwright/test'
import { latestIssue } from '../../src/data/issues/index.ts'
import { vendorPrints } from '../../src/data/prints.ts'

/**
 * Slugs derived from the newest issue's own data at test time, not
 * hard-coded — Codex whole-diff review finding 4: hard-coding week-36's
 * "crowdstrike"/"zscaler" meant the item-filter half of this suite silently
 * turned into a zero-match, vacuously-passing test the moment a second issue
 * without those vendors became the newest. `ITEM_SLUG` is guaranteed to
 * appear on at least one item of the newest issue; `PRINT_SLUG` is
 * guaranteed to appear on at least one vendorPrints entry (distinct from
 * `ITEM_SLUG` when the data offers a distinct one) — between the two, both
 * filterable surfaces (issue items and the scorecard) always have something
 * real to show, regardless of which issue is newest.
 */
function pickItemVendorSlug(): string {
  for (const section of latestIssue.sections) {
    for (const item of section.items) {
      const first = (item.vendors ?? [])[0]
      if (first) return first
    }
  }
  throw new Error(
    'lens.spec.ts: no item on the newest issue carries a vendors slug — cannot derive a lens test fixture from data.',
  )
}

function pickPrintVendorSlug(excluding: string): string {
  const distinct = vendorPrints.find((print) => print.vendorSlug !== undefined && print.vendorSlug !== excluding)
  if (distinct?.vendorSlug) return distinct.vendorSlug
  const anyPrint = vendorPrints.find((print) => print.vendorSlug !== undefined)
  if (anyPrint?.vendorSlug) return anyPrint.vendorSlug
  throw new Error('lens.spec.ts: no vendorPrints entry carries a vendorSlug — cannot derive a lens test fixture from data.')
}

const ITEM_SLUG = pickItemVendorSlug()
const PRINT_SLUG = pickPrintVendorSlug(ITEM_SLUG)
const LENS_SLUGS = [ITEM_SLUG, PRINT_SLUG]
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

/** The exact headline text of every issue item the given slugs match, across all lanes. */
function matchingIssueHeadlines(slugs: string[]): string[] {
  const headlines: string[] = []
  for (const section of latestIssue.sections) {
    for (const item of section.items) {
      if ((item.vendors ?? []).some((vendor) => slugs.includes(vendor))) {
        headlines.push(item.headline)
      }
    }
  }
  return headlines
}

function matchingPrints(slugs: string[]): number {
  return vendorPrints.filter((print) => print.vendorSlug !== undefined && slugs.includes(print.vendorSlug))
    .length
}

/** The exact card name of every vendorPrints entry the given slugs match. */
function matchingPrintNames(slugs: string[]): string[] {
  return vendorPrints
    .filter((print) => print.vendorSlug !== undefined && slugs.includes(print.vendorSlug))
    .map((print) => print.name)
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
  test('?vendors= filters both the issue items and the scorecard, showing the exact matching items/cards and Showing N of M on each', async ({
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

    // Not just the self-reported count — the actual rendered identities.
    // A build that filtered to the right COUNT but the wrong ITEMS would
    // pass the assertions above and fail these.
    const actualHeadlines = (await page.locator('.issue-lane__headline').allTextContents()).map((text) =>
      text.replace(/\s*·\s*background\s*$/, '').trim(),
    )
    expect(actualHeadlines.slice().sort()).toEqual(matchingIssueHeadlines(LENS_SLUGS).slice().sort())

    const actualPrintNames = (await page.locator('.print-card h3').allTextContents()).map((text) => text.trim())
    expect(actualPrintNames.slice().sort()).toEqual(matchingPrintNames(LENS_SLUGS).slice().sort())

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

  test('an empty vendors parameter is treated as no lens — identical to no parameter at all', async ({ page }) => {
    const { pageErrors, consoleErrors } = trackConsole(page)

    await page.goto('/?vendors=')

    await expect(page.locator('.issue-lane__filter-status')).toHaveCount(0)
    await expect(page.locator('.print-grid__filter-status')).toHaveCount(0)
    await expect(page.locator('#vendor-lens-slot .vendor-lens__clear')).toHaveCount(0)
    await expect(page.locator('#vendor-lens-slot .vendor-lens__chip')).toHaveCount(0)

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
