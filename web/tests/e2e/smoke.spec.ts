import { expect, test } from '@playwright/test'

test('renders the market briefing without runtime errors', async ({ page }) => {
  const pageErrors: string[] = []
  page.on('pageerror', (error) => pageErrors.push(error.message))

  await page.goto('/')

  await expect(page.getByRole('heading', { level: 1 })).toContainText(
    'Where the security market is going',
  )
  await expect(
    page.getByRole('heading', { level: 2, name: /Infrastructure is running ahead/ }),
  ).toBeVisible()
  await expect(page.getByText('TRACKED', { exact: false }).first()).toBeVisible()
  await expect(page.getByText('NEEDS A SOURCE')).toBeVisible()
  await expect(page.getByRole('heading', { name: 'What moved this week' })).toBeVisible()
  await expect(page.getByRole('heading', { name: 'Tracked hypotheses' })).toBeVisible()
  await expect(page.getByText('NO-CALL', { exact: true }).first()).toBeVisible()
  await expect(page.getByRole('heading', { name: 'This period' })).toBeVisible()
  await expect(page.getByRole('heading', { name: 'Tempo' })).toBeVisible()
  await expect(page.getByRole('heading', { name: 'Since 16 August 2026' })).toBeVisible()
  // Assert the delta renders structurally, not by its prose. The summary is
  // rewritten every edition; the derived Held/Moved chip is the durable contract.
  await expect(page.locator('.edition-table .edition-kind').first()).toBeVisible()
  await expect(page.getByText('This quarter', { exact: true })).toBeVisible()
  await expect(page.getByText('This planning cycle', { exact: true })).toBeVisible()
  await expect(page.getByText('Produced by', { exact: true }).first()).toBeVisible()
  await expect(page.getByRole('button', { name: /Fortinet/ }).first()).toBeVisible()
  await expect(page.locator('#method summary')).toHaveText('How this is built')
  await expect(page.getByRole('heading', { name: 'M&A and startups' })).toBeVisible()
  // Background-surface item: collapsed inside a <details>, so it's in the DOM
  // (crawlers and the prerendered markup both see it) but not visible until expanded.
  await expect(page.getByText('Google closed Wiz')).toBeAttached()
  await expect(page.getByRole('heading', { name: 'Fortinet' })).toBeVisible()
  await expect(page.getByRole('heading', { name: 'SentinelOne' })).toBeVisible()
  await expect(page.getByText('SecOps', { exact: true }).first()).toBeVisible()
  await expect(page.getByText('PREPARE', { exact: true }).first()).toBeVisible()
  await expect(page.getByText('RUN', { exact: true })).toHaveCount(0)
  await expect(page.getByText('INSUFFICIENT COVERAGE')).toHaveCount(0)
  await expect(page.getByText('Alphabet announced ~$32B Wiz acquisition')).toHaveCount(0)
  // Ping Identity has no public print of its own; it's disclosed as a
  // coverage row grouped with the other PE-owned identity platforms.
  await expect(page.getByRole('heading', { name: 'Entra / Ping / PE PAM' })).toBeVisible()
  // Same background-surface pattern as Wiz above: the old raise stays in the
  // evidence base inside the collapsed details, just not shown by default.
  await expect(page.getByText('Secuvy last disclosed seed')).toBeHidden()

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
