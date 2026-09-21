import { expect, test } from '@playwright/test'
import { latestIssue } from '../../src/data/issues/index.ts'
import { marketCall } from '../../src/data/market.ts'
import { SITE_HEADLINE } from '../../src/data/meta.ts'

test('renders the market briefing without runtime errors', async ({ page }) => {
  const pageErrors: string[] = []
  page.on('pageerror', (error) => pageErrors.push(error.message))

  await page.goto('/')

  // The h1 is the site's standing headline (SEC-MARKET-CORE-001 §5); the
  // newest issue's read lives in the issue strip right below it (D-71). The
  // former market-call h1 used to live on this same page as an h2 inside
  // #read; under SEC-MARKET-FABLE-001 T6-16 that whole argument
  // (JudgmentBoard, the running score, the market-call heading) moved to its
  // own page at /thesis/ (product-core.md §5) — see tests/e2e/thesis.spec.ts.
  // #read here is now a compact pointer to that page; see the assertions
  // further down.
  await expect(page.getByRole('heading', { level: 1 })).toHaveText(SITE_HEADLINE)
  await expect(page.locator('#overview .issue-strip__read')).toHaveText(latestIssue.read)

  await expect(page.getByText('refreshed weekly')).toHaveCount(0)
  await expect(page.getByText('Tell me when the next edition publishes')).toHaveCount(0)
  await expect(page.getByText('TRACKED', { exact: false }).first()).toBeVisible()

  // "What moved" now sits inside a closed depth disclosure (#moved-depth) —
  // the issue's four lanes are the always-visible account of what moved, per
  // §4 of docs/active/weekly-issue-spec.md. Present for evidence/crawlers,
  // closed until opened, exactly like #research-depth below.
  await expect(page.locator('#moved-depth > summary')).toHaveText('What moved: edition delta')
  await expect(page.locator('#moved-depth #moved')).toBeAttached()
  await expect(page.locator('#moved-depth #moved')).toBeHidden()

  await expect(page.getByRole('heading', { name: 'Tracked hypotheses' })).toBeVisible()
  await expect(page.getByText('NO-CALL', { exact: true }).first()).toBeVisible()

  // Landscape cards now lead with the trigger sentence as their title (an h2);
  // the domain name moved to a label above it, no longer a heading itself.
  await expect(page.locator('#landscape').getByText('Network / SASE', { exact: true })).toBeVisible()

  await expect(page.getByRole('button', { name: /Fortinet/ }).first()).toBeVisible()
  await expect(page.locator('.landscape .evidence-link').nth(2)).toContainText(/CrowdStrike|Upwind|Orca|Aqua/)
  await expect(page.locator('.landscape .evidence-link').nth(2)).not.toContainText('Alphabet')
  await expect(page.locator('#method summary')).toHaveText('How this is built')
  await expect(page.locator('#research-depth > summary')).toHaveText(
    'Domain tempo and M&A activity',
  )

  // The full scorecard's prints (2026-08-22) stay visible on first paint — no
  // click required to reach them. The market-call headline itself
  // (#market-call-heading) no longer lives on the front page — it moved to
  // /thesis/ with the rest of the thesis argument; see tests/e2e/thesis.spec.ts.
  // What stays here is the compact pointer at #read: its own heading, and the
  // market-call headline text quoted from data, not retyped.
  await expect(page.locator('#market-call-heading')).toHaveCount(0)
  await expect(page.locator('#read')).toContainText('Does security spending lag infrastructure spending?')
  await expect(page.locator('#read')).toContainText(marketCall.headline)
  await expect(page.locator('#read').getByRole('link', { name: 'Read the analysis and its record' })).toHaveAttribute(
    'href',
    '/thesis/',
  )
  await expect(page.locator('#prints-heading')).toBeVisible()
  await expect(page.getByRole('heading', { name: 'Fortinet' })).toBeVisible()
  await expect(page.getByRole('heading', { name: 'SentinelOne' })).toBeVisible()
  await expect(page.getByRole('heading', { name: 'Entra / Ping / PE PAM' })).toBeVisible()
  // SecOps and PREPARE now surface pre-click too: SecOps as a promoted print-group
  // title, PREPARE as a landscape domain chip — neither lives inside the
  // remaining disclosure any more.
  await expect(page.getByText('SecOps', { exact: true }).first()).toBeVisible()
  await expect(page.getByText('PREPARE', { exact: true }).first()).toBeVisible()

  // Domain tempo and M&A activity are still gated behind #research-depth:
  // present in the markup for evidence and crawlers, closed until opened.
  // Closed <details> content is not in the accessibility tree, so query the DOM.
  const scorecard = page.locator('#research-depth')
  await expect(scorecard.locator('#domains-heading')).toBeAttached()
  await expect(scorecard.locator('#domains-heading')).toBeHidden()
  await expect(scorecard.locator('#activity-heading')).toBeAttached()
  await expect(scorecard.locator('#activity-heading')).toBeHidden()
  await expect(page.getByText('Google closed Wiz')).toBeAttached()
  await expect(page.getByText('Alphabet announced ~$32B Wiz acquisition')).toHaveCount(0)
  await expect(page.getByText('Secuvy last disclosed seed')).toBeHidden()
  await expect(page.getByText('RUN', { exact: true })).toHaveCount(0)
  await expect(page.getByText('INSUFFICIENT COVERAGE')).toHaveCount(0)

  await page.locator('#research-depth > summary').click()
  await expect(page.locator('#domains-heading')).toBeVisible()
  await expect(page.locator('#activity-heading')).toBeVisible()
  await expect(page.getByRole('heading', { name: 'Since 17 August 2026' })).toBeVisible()
  await expect(page.locator('.edition-table .edition-kind').first()).toBeVisible()
  await expect(page.getByText('Produced by', { exact: true }).first()).toBeVisible()
  // Only becomes visible once the disclosure opens — the lead M&A/funding row.
  await expect(page.getByText('Zenity raised $115M Series C')).toBeVisible()

  // Opening #moved-depth reveals the edition-delta account "What moved" used
  // to give on its own — still there, just one click deeper now.
  await page.locator('#moved-depth > summary').click()
  await expect(page.locator('#moved-heading')).toBeVisible()

  expect(pageErrors).toEqual([])
})

test('every judged stamp with a date also names who judged it', async ({ page }) => {
  await page.goto('/')

  // A judged stamp is any element carrying the literal word JUDGED next to a
  // dated <time> element (the legend text in the provenance rail and the
  // "TRACKED PRINTS · JUDGED READ" column header both say JUDGED without a
  // date and are correctly excluded here). Queried directly against the DOM
  // so stamps inside closed <details> disclosures (e.g. "What moved") are
  // still checked without needing to open them first.
  const judgedStamps = await page.locator('body').evaluate(() => {
    const candidates = Array.from(document.querySelectorAll('.stamp-label'))
    return candidates
      .filter((el) => (el.textContent ?? '').includes('JUDGED') && el.querySelector('time'))
      .map((el) => el.textContent ?? '')
  })

  expect(judgedStamps.length).toBeGreaterThan(0)
  for (const stamp of judgedStamps) {
    expect(stamp).toContain('Jesse Pike')
  }
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
