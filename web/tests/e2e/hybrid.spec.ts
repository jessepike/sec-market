import { expect, test } from '@playwright/test'
import { feedEntries } from '../../src/data/tracker/feed'

for (const width of [1440, 390]) {
  test(`approved hybrid works at ${width}px with keyboard, sourced figures and compact phone views`, async ({ page }) => {
    await page.setViewportSize({ width, height: width === 390 ? 844 : 900 })
    const errors: string[] = []
    page.on('pageerror', error => errors.push(error.message))
    await page.goto('/')
    await expect(page.locator('.site-masthead__stamps')).toContainText('Not a news site and not investment advice.')
    await expect(page.locator('.site-masthead__stamps a')).toHaveAttribute('href', '/method/#overview')
    await expect(page.locator('.desk-hero')).not.toContainText(/Daily source intake|Document processing|Historical review/)
    await expect(page.locator('.site-masthead__stamps')).toContainText('Certified SEC figures last changed')
    await expect(page.locator('.desk-counts small')).toHaveCount(0)
    await expect(page.locator('.desk-counts-note a', { hasText: 'Explore 12 months' })).toHaveAttribute('href', '/market/#event-timeline')
    await expect(page.locator('.desk-hero')).not.toContainText(/\d+ suppliers|SEC filers certified/)
    await expect(page.locator('.market-desk')).not.toContainText(/Diagnostic candidate|Latest attempt/)
    await expect(page.locator('.market-desk')).not.toContainText(/owner.s read/i)
    await expect(page.locator('.market-desk')).not.toContainText('—')
    // Landing order (design review 2026-11-06): tiles, a short feed, then company revenue growth.
    const top = (sel: string) => page.locator(sel).evaluate(e => e.getBoundingClientRect().top)
    expect(await top('.desk-counts')).toBeLessThan(await top('#tracker-changed'))
    expect(await top('#tracker-changed')).toBeLessThan(await top('#momentum'))
    await expect(page.locator('#momentum-heading')).toHaveText('Company revenue growth')
    await expect(page.locator('#momentum .momentum__row').first()).toContainText('pts')
    await expect(page.locator('.desk-counts__snapshot').first()).not.toBeEmpty()
    await expect(page.locator('#tracker-changed .desk-tag', { hasText: 'SEC filing' })).toHaveCount(0)
    // Eight entries on a wide screen, five on a phone, each stating a fact and never a bare filing notice.
    await expect(page.locator('#tracker-changed .desk-line:visible')).toHaveCount(Math.min(width === 390 ? 5 : 8, feedEntries.length))
    await expect(page.locator('#tracker-changed .desk-line__fact', { hasText: /^Form [^,]+ reporting/ })).toHaveCount(0)
    await expect(page.locator('#momentum .momentum__row .momentum__spark').first()).toBeVisible()
    await expect(page.locator('#momentum .momentum__rev').first()).toContainText('$')
    expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBe(width)
    // The heatmap, the full growth chart and the domain index moved to /market/.
    await expect(page.locator('#event-timeline, #reported-growth, #market')).toHaveCount(0)
    // All domains: every SEC filer once.
    await page.getByRole('button', { name: 'All domains', exact: true }).click()
    await expect(page.locator('.momentum__all .momentum__row:not(.momentum__axis)')).toHaveCount(16)
    await page.getByRole('button', { name: 'By domain', exact: true }).click()
    // An entry opens the event in the side panel, with its source.
    await page.locator('#tracker-changed .desk-line__fact').first().click()
    const event = page.locator('.desk-event-dialog')
    await expect(event).toBeVisible()
    await expect(event.locator('.desk-sources a, .desk-filing').first()).toHaveAttribute('href', /^https:\/\//)
    await page.keyboard.press('Escape')
    await expect(event).toBeHidden()
    if (width === 390) expect(await page.evaluate(() => document.body.scrollHeight)).toBeLessThan(10000)
    if (feedEntries.length > (width === 390 ? 5 : 8)) {
      await page.locator('#tracker-changed .desk-show-all').click()
      await expect(page.locator('#tracker-changed .desk-line:visible')).toHaveCount(feedEntries.length)
    }
    // All domains opens with growth against free cash flow margin, one dot per filer.
    await page.getByRole('button', { name: 'All domains', exact: true }).click()
    await expect(page.locator('.momentum__scatter circle')).toHaveCount(16)
    expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBe(width)
    expect(errors).toEqual([])
  })
}

for (const width of [1440, 390]) {
  test(`market page holds the timeline, growth chart and domains at ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: width === 390 ? 844 : 900 })
    const errors: string[] = []
    page.on('pageerror', error => errors.push(error.message))
    await page.goto('/market/')
    expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBe(width)
    await expect(page.locator('#desk-timeline-heading + span')).toContainText(/\d+ events from \d+ entries/)
    if (width === 390) {
      await expect(page.locator('.desk-domain.is-selected')).toBeVisible()
      await page.locator('.desk-domain-select select').selectOption('identity')
      await expect(page.locator('#domain-identity')).toBeVisible()
      await expect(page.locator('#domain-endpoint-xdr')).toBeHidden()
      await page.locator('.desk-growth__mobile-toggle').click()
    }
    const chart = page.locator('.desk-growth__rows')
    await expect(chart.locator('li')).toHaveCount(20)
    // The comparison opens ranked by growth; A to Z is one press away.
    await expect(page.getByRole('button', { name: 'Sort A–Z', exact: true })).toHaveAttribute('aria-pressed', 'true')
    await page.getByRole('button', { name: 'Sort A–Z', exact: true }).click()
    expect(await chart.locator('li').first().innerText()).toContain('Akamai')
    const open = chart.getByRole('button', { name: 'Cloudflare', exact: true })
    await open.focus(); await page.keyboard.press('Enter')
    const dialog = page.locator('.desk-dialog')
    await expect(dialog).toBeVisible()
    await expect(dialog).toContainText('+35.9%')
    await expect(page.locator('.desk-quarter-table')).toBeVisible()
    await page.keyboard.press('Tab')
    expect(await page.evaluate(() => document.activeElement?.closest('dialog') !== null)).toBe(true)
    await page.keyboard.press('Escape')
    await expect(dialog).toBeHidden()
    await expect(open).toBeFocused()
    const point = page.locator('.desk-timeline__cell button').first()
    const rect = await point.boundingBox()
    expect(rect!.width).toBeGreaterThanOrEqual(24); expect(rect!.height).toBeGreaterThanOrEqual(24)
    await point.focus(); await page.keyboard.press('Enter')
    await expect(point).toHaveAttribute('aria-pressed', 'true')
    await expect(page.locator('#desk-timeline-events .desk-change').first()).toBeVisible()
    await expect(page.locator('#desk-timeline-events .desk-sources a').first()).toHaveAttribute('href', /^https:\/\//)
    expect(errors).toEqual([])
  })
}
