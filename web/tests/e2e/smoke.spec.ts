import { expect, test } from '@playwright/test'

test('renders the market briefing without runtime errors', async ({ page }) => {
  const pageErrors: string[] = []
  page.on('pageerror', (error) => pageErrors.push(error.message))

  await page.goto('/')

  await expect(page.getByRole('heading', { level: 1 })).toContainText(
    'Where the security market is going',
  )
  await expect(page.getByText('refreshed weekly')).toHaveCount(0)
  await expect(page.getByText('Tell me when the next edition publishes')).toHaveCount(0)
  await expect(page.getByText('TRACKED', { exact: false }).first()).toBeVisible()
  await expect(page.locator('#moved')).toBeVisible()
  await expect(page.getByRole('heading', { name: 'Tracked hypotheses' })).toBeVisible()
  await expect(page.getByText('NO-CALL', { exact: true }).first()).toBeVisible()
  await expect(page.getByRole('heading', { name: 'Network / SASE' })).toBeVisible()
  await expect(page.getByRole('button', { name: /Fortinet/ }).first()).toBeVisible()
  await expect(page.locator('.landscape .evidence-link').nth(2)).toContainText(/CrowdStrike|Upwind|Orca|Aqua/)
  await expect(page.locator('.landscape .evidence-link').nth(2)).not.toContainText('Alphabet')
  await expect(page.locator('#method summary')).toHaveText('How this is built')
  await expect(page.locator('#research-depth > summary')).toHaveText(
    'Episode 002 research and the full scorecard',
  )

  // Edition stack stays in the markup for evidence and crawlers, closed until opened.
  // Closed <details> content is not in the accessibility tree, so query the DOM.
  const scorecard = page.locator('#research-depth')
  await expect(scorecard.locator('#market-call-heading')).toBeAttached()
  await expect(scorecard.locator('#prints-heading')).toBeAttached()
  await expect(scorecard.locator('#domains-heading')).toBeAttached()
  await expect(scorecard.locator('#activity-heading')).toBeAttached()
  await expect(page.getByText('Google closed Wiz')).toBeAttached()
  await expect(page.getByText('Alphabet announced ~$32B Wiz acquisition')).toHaveCount(0)
  await expect(page.getByText('Secuvy last disclosed seed')).toBeHidden()
  await expect(page.getByText('RUN', { exact: true })).toHaveCount(0)
  await expect(page.getByText('INSUFFICIENT COVERAGE')).toHaveCount(0)

  await page.locator('#research-depth > summary').click()
  await expect(page.locator('#market-call-heading')).toBeVisible()
  await expect(page.locator('#prints-heading')).toBeVisible()
  await expect(page.locator('#domains-heading')).toBeVisible()
  await expect(page.getByRole('heading', { name: 'Since 16 August 2026' })).toBeVisible()
  await expect(page.locator('.edition-table .edition-kind').first()).toBeVisible()
  await expect(page.getByText('Produced by', { exact: true }).first()).toBeVisible()
  await expect(page.getByRole('heading', { name: 'Fortinet' })).toBeVisible()
  await expect(page.getByRole('heading', { name: 'SentinelOne' })).toBeVisible()
  await expect(page.getByRole('heading', { name: 'Entra / Ping / PE PAM' })).toBeVisible()
  await expect(page.getByText('SecOps', { exact: true }).first()).toBeVisible()
  await expect(page.getByText('PREPARE', { exact: true }).first()).toBeVisible()

  expect(pageErrors).toEqual([])
})

test('opens attributed evidence without a private GitHub artifact link', async ({ page }) => {
  await page.goto('/')

  await page.getByRole('button', { name: /Fortinet/ }).first().click()

  const dialog = page.getByRole('dialog', { name: 'Evidence' })
  await expect(dialog).toBeVisible()
  await expect(dialog.getByRole('link', { name: /Canonical source/ }).first()).toBeVisible()
  await expect(dialog.getByRole('heading', { name: 'Limitations / confounds' }).first()).toBeVisible()
  await expect(dialog.getByRole('link', { name: /github.com\/jessepike\/sec-market/ })).toHaveCount(0)

  await page.keyboard.press('Escape')
  await expect(dialog).toBeHidden()
})
