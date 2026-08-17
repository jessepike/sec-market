import { expect, test } from '@playwright/test'

test('renders the market briefing without runtime errors', async ({ page }) => {
  const pageErrors: string[] = []
  page.on('pageerror', (error) => pageErrors.push(error.message))

  await page.goto('/')

  await expect(page.getByRole('heading', { level: 1 })).toContainText('Infrastructure')
  await expect(page.getByText('NO-CALL', { exact: true }).first()).toBeVisible()
  await expect(page.getByRole('heading', { name: 'This period' })).toBeVisible()
  await expect(page.getByRole('heading', { name: 'Tempo' })).toBeVisible()
  await expect(page.locator('#method summary')).toHaveText('How this is built')
  await expect(page.getByRole('heading', { name: 'M&A and startups' })).toBeVisible()
  await expect(page.getByText('Google closed Wiz')).toBeVisible()
  await expect(page.getByRole('heading', { name: 'Fortinet' })).toBeVisible()
  await expect(page.getByRole('heading', { name: 'SentinelOne' })).toBeVisible()
  await expect(page.getByText('SecOps', { exact: true }).first()).toBeVisible()
  await expect(page.getByText('PREPARE', { exact: true }).first()).toBeVisible()
  await expect(page.getByText('RUN', { exact: true })).toHaveCount(0)
  await expect(page.getByText('INSUFFICIENT COVERAGE')).toHaveCount(0)
  await expect(page.getByText('Alphabet announced ~$32B Wiz acquisition')).toHaveCount(0)
  await expect(page.getByRole('heading', { name: 'Ping Identity' })).toBeVisible()
  await expect(page.getByText('Secuvy last disclosed seed')).toHaveCount(0)

  expect(pageErrors).toEqual([])
})

test('opens attributed evidence without a private GitHub artifact link', async ({ page }) => {
  await page.goto('/')

  await page.getByRole('button', { name: 'Sources' }).first().click()

  const dialog = page.getByRole('dialog', { name: 'Evidence' })
  await expect(dialog).toBeVisible()
  await expect(dialog.getByRole('link', { name: /Canonical source/ }).first()).toBeVisible()
  await expect(dialog.getByRole('heading', { name: 'Limitations / confounds' }).first()).toBeVisible()
  await expect(dialog.getByRole('link', { name: /github.com\/jessepike\/sec-market/ })).toHaveCount(0)

  await page.keyboard.press('Escape')
  await expect(dialog).toBeHidden()
})
