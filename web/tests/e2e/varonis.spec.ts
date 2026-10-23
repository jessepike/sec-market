import { expect, test } from '@playwright/test'

const primaryRelease = 'https://www.proofpoint.com/us/newsroom/press-releases/proofpoint-acquire-varonis-creating-global-leader-data-and-ai-security'

for (const width of [1440, 390]) {
  test(`Varonis agreement is readable from acquisitions and supplier record at ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: width === 390 ? 844 : 900 })
    await page.goto('/')
    await page.locator('.desk-counts').getByRole('button', { name: /Acquisitions & divestitures/ }).click()
    const agreement = page.locator('#tracker-changed .desk-change').filter({ hasText: 'Proofpoint to acquire Varonis' })
    await expect(agreement).toHaveCount(1)
    await expect(agreement).toBeVisible()
    await expect(agreement).toContainText('2026-10-15')
    await expect(agreement).toContainText('approximately $6.3 billion, or $49.75 per share')
    await expect(agreement).toContainText('first half of 2027, subject to shareholder and regulatory approvals')
    await expect(agreement).toContainText('separate companies until closing')
    await expect(agreement.locator('.desk-sources a')).toHaveAttribute('href', primaryRelease)
    await agreement.getByRole('button', { name: 'Varonis Systems', exact: true }).click()
    const record = page.getByRole('dialog', { name: 'Varonis Systems, Inc.' })
    await expect(record).toBeVisible()
    const ownership = record.locator('.desk-fact').filter({ hasText: 'Ownership' })
    await expect(ownership).toContainText('Publicly traded (Nasdaq: VRNS)')
    await expect(ownership).toContainText('Announced 2026-10-15')
    await expect(ownership).not.toContainText('Closed')
    const datedEvent = record.locator('.desk-dialog__events li').filter({ hasText: 'Proofpoint to acquire Varonis' })
    await expect(datedEvent).toBeVisible()
    await expect(datedEvent).toContainText('definitive agreement')
    await expect(datedEvent).toContainText('separate companies until closing')
    await expect(datedEvent.locator('.desk-sources a')).toHaveAttribute('href', primaryRelease)
  })
}
