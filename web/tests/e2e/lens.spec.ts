import { expect, test } from '@playwright/test'

/**
 * Step 5 (autonomy-coverage-plan.md §3, D-76/D-77): the vendor lens
 * (`?vendors=`, SEC-031) filtered exactly two things — PrintGrid's
 * scorecard and the front page's own copy of IssueLanes. The twelve-domain
 * tracker replaces both (MarketByDomain, WhatChangedTracker), and neither
 * PrintGrid nor a front-page IssueLanes renders on any route any more, so
 * the lens has nothing left to filter. `VendorLensProvider`, `VendorLens.tsx`
 * and `useVendorLens` are untouched — nothing deletes the mechanism, App.tsx
 * simply stops mounting the provider on the front page — this suite is
 * replaced with a direct check that the control and its filter-status
 * strings are gone rather than continuing to exercise dead UI. See
 * tests/e2e/smoke.spec.ts for the equivalent front-page assertions.
 */
test('the vendor lens no longer renders on the front page', async ({ page }) => {
  const pageErrors: string[] = []
  page.on('pageerror', (error) => pageErrors.push(error.message))

  await page.goto('/?vendors=fortinet')

  await expect(page.locator('#vendor-lens-slot')).toHaveCount(0)
  await expect(page.locator('.vendor-lens__chip')).toHaveCount(0)
  await expect(page.locator('.print-grid__filter-status')).toHaveCount(0)
  await expect(page.locator('.issue-lane__filter-status')).toHaveCount(0)

  expect(pageErrors).toEqual([])
})
