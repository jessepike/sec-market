import { expect, test } from '@playwright/test'

test('renders the market briefing without runtime errors', async ({ page }) => {
  const pageErrors: string[] = []
  page.on('pageerror', (error) => pageErrors.push(error.message))

  await page.goto('/')

  await expect(page.getByRole('heading', { level: 1 })).toContainText('Infrastructure')
  await expect(page.getByText('What changed')).toBeVisible()
  await expect(page.getByText('NO-CALL', { exact: true }).first()).toBeVisible()
  await expect(page.getByRole('heading', { name: 'Security domains' })).toBeVisible()
  await expect(page.getByRole('heading', { name: 'Research & evidence' })).toBeVisible()

  expect(pageErrors).toEqual([])
})

test('opens attributed evidence and exposes the canonical source', async ({ page }) => {
  await page.goto('/')

  await page.getByRole('button', { name: /Sources for this call/ }).click()

  const dialog = page.getByRole('dialog', { name: 'Evidence' })
  await expect(dialog).toBeVisible()
  await expect(dialog.getByRole('link', { name: /Canonical source/ }).first()).toBeVisible()
  await expect(dialog.getByRole('heading', { name: 'Limitations / confounds' }).first()).toBeVisible()

  await page.keyboard.press('Escape')
  await expect(dialog).toBeHidden()
})

