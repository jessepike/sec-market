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
  await expect(page.locator('#overview')).toContainText(coverage.intake?.evaluated === false
    ? `Daily source intake: not yet collected (${coverage.successfulTasks} of ${coverage.requiredTasks})`
    : coverage.schemaVersion === 2 ? `${coverage.successfulTasks} of ${coverage.requiredTasks} checked` : `${coverage.successfulTasks} of ${coverage.requiredTasks} required source checks completed`)
  if (coverage.schemaVersion === 2) {
    await expect(page.locator('#overview')).toContainText('Daily source intake:')
    await expect(page.locator('#overview')).toContainText(coverage.processing.evaluated === false
      ? 'Document processing: not evaluated; pending, held and unknown-date counts unmeasured'
      : `Document processing (${coverage.processing.complete ? 'complete' : 'incomplete'}): ${coverage.processing.inventoryDocuments ? `${coverage.processing.reviewedDocuments} of ${coverage.processing.inventoryDocuments} reviewed` : 'no documents observed'}`)
    await expect(page.locator('#overview')).toContainText(coverage.historicalReview.evaluated === false
      ? 'Historical review: not evaluated; pending and held counts unmeasured'
      : `Historical review (${coverage.historicalReview.complete ? 'complete' : 'incomplete'}): ${coverage.historicalReview.inventoryDocuments ? `${coverage.historicalReview.reviewedDocuments} of ${coverage.historicalReview.inventoryDocuments} reviewed` : 'no documents observed'}`)
    if (!coverage.complete && coverage.intake.evaluated) await expect(page.locator('#overview')).toContainText('checked; incomplete.')
    if (!coverage.processing.complete && coverage.processing.evaluated !== false) await expect(page.locator('#overview')).toContainText('Document processing (incomplete)')
    if (!coverage.historicalReview.complete && coverage.historicalReview.evaluated !== false) await expect(page.locator('#overview')).toContainText('Historical review (incomplete)')
    await page.getByText('Dates, review limits and source receipts', { exact: true }).click()
    await expect(page.locator('#overview details').filter({ has: page.getByText('Dates, review limits and source receipts', { exact: true }) })).toContainText('Source intake does not mean every current event or historical claim has been reviewed.')
  } else if (!coverage.complete) await expect(page.locator('#overview')).toContainText('Coverage is incomplete.')
  await expect(page.getByRole('link', { name: 'Sources, frequency and check receipts' })).toHaveAttribute('href', '/daily-coverage.json')
})

test('a missed future run becomes visibly overdue without another deployment', async ({ page }) => {
  test.skip(!snapshot.enabled || !snapshot.coverage?.validUntil, 'No source deadline in this build')
  const deadline = Date.parse(snapshot.coverage!.validUntil!)
  await page.clock.install({ time: new Date(deadline + 3600000) })
  await page.goto('/')
  await expect(page.locator('#overview')).toContainText(/The next (source )?check is overdue\./)
})
