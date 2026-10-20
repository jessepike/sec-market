import { expect, test } from '@playwright/test'
import snapshot from '../../src/data/generated/dailyMarket.json' with { type: 'json' }

test('visible collection status agrees with the public source receipt', async ({ page, request }) => {
  test.skip(!snapshot.enabled, 'Daily coverage has not been materialized for this build')
  const response = await request.get('/daily-coverage.json')
  expect(response.status()).toBe(200)
  const coverage = await response.json()
  expect(coverage.runId).toBe(snapshot.runId)
  expect(coverage.requiredTasks).toBe(snapshot.coverage?.requiredTasks)
  await page.goto('/')
  await expect(page.locator('.desk-hero')).toContainText(`${coverage.successfulTasks} of ${coverage.requiredTasks} required source checks completed`)
  if (!coverage.complete) await expect(page.locator('.desk-hero')).toContainText('Coverage is incomplete.')
  await expect(page.getByRole('link', { name: 'Sources, frequency and check receipts' })).toHaveAttribute('href', '/daily-coverage.json')
})

test('a missed future run becomes visibly overdue without another deployment', async ({ page }) => {
  test.skip(!snapshot.enabled || !snapshot.coverage?.validUntil, 'No source deadline in this build')
  const deadline = Date.parse(snapshot.coverage!.validUntil!)
  await page.clock.install({ time: new Date(deadline + 3600000) })
  await page.goto('/')
  await expect(page.locator('.desk-hero')).toContainText('The next check is overdue.')
})
