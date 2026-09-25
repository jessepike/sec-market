import { expect, test } from '@playwright/test'
import { formatLongDate, formatShortDate } from '../../src/data/dates.ts'
import { LAST_UPDATED_DISPLAY, LAST_UPDATED_ISO, SITE_HEADLINE } from '../../src/data/meta.ts'
import { runStatus } from '../../src/data/runStatus.ts'

/**
 * D-76/autonomy-coverage-plan.md §3, step 1: the front page now publishes
 * sourced facts only, no judgments. This test used to also check the
 * weekly-issue strip, "Tracked hypotheses", the standing-thesis pointer, the
 * domain-tempo table and its judged delta — all removed from this route; see
 * DomainBoard.tsx, MarketPicture.tsx, WhatMoved.tsx, ActivityBoard.tsx and
 * App.tsx for where each piece went. Step 1 fix pass, item 3: PlatformPressure
 * is now gone from this route in full — not just its judged "read" column —
 * because every row it drew from carried a hand-assigned vendor-position
 * label (see the `#platforms` and position-label assertions below).
 */
test('renders the market briefing without runtime errors', async ({ page }) => {
  const pageErrors: string[] = []
  page.on('pageerror', (error) => pageErrors.push(error.message))

  await page.goto('/')

  await expect(page.getByRole('heading', { level: 1 })).toHaveText(SITE_HEADLINE)

  // RunStatus replaces the old issue strip in the same #overview slot — an
  // honest statement of whether collection ran, never a judgment.
  await expect(page.locator('#overview .run-status__line')).toContainText('Figures checked')
  await expect(page.locator('#overview .run-status__line')).toContainText('every source collected')
  expect(runStatus.state).toBe('updated')

  await expect(page.getByText('refreshed weekly')).toHaveCount(0)
  await expect(page.getByText('Tell me when the next edition publishes')).toHaveCount(0)
  await expect(page.getByText('TRACKED', { exact: false }).first()).toBeVisible()

  // "What moved" now sits inside a closed depth disclosure (#moved-depth) —
  // the issue's four lanes are the always-visible account of what moved, per
  // §4 of docs/active/weekly-issue-spec.md. Present for evidence/crawlers,
  // closed until opened, exactly like #research-depth below.
  await expect(page.locator('#moved-depth > summary')).toHaveText('What moved: tracked prints and capital')
  await expect(page.locator('#moved-depth #moved')).toBeAttached()
  await expect(page.locator('#moved-depth #moved')).toBeHidden()

  // No judgment sections at all on the front page.
  await expect(page.getByRole('heading', { name: 'Tracked hypotheses' })).toHaveCount(0)
  await expect(page.locator('#hypotheses')).toHaveCount(0)
  await expect(page.locator('#we-think')).toHaveCount(0)
  await expect(page.locator('#read')).toHaveCount(0)
  await expect(page.locator('#watch')).toHaveCount(0)

  // Step 1 fix pass, item 3: Platform pressure is gone from the front page
  // entirely, and no hand-assigned vendor-position label survives anywhere
  // on the page — those describe competitive footing, which the site no
  // longer states. The factual 'absorbed'/acquisition wording (acquirer,
  // target, price, close date) is unaffected and checked separately below.
  await expect(page.locator('#platforms')).toHaveCount(0)
  await expect(page.locator('.pressure')).toHaveCount(0)
  for (const label of ['Holding', 'Buying in', 'Outrun', 'Challengers', 'Incumbent', 'Challenger']) {
    await expect(page.getByText(label, { exact: true })).toHaveCount(0)
  }

  // Landscape cards show the domain name and its tracked print only — no
  // stance chip, no JUDGED stamp, no horizon.
  await expect(page.locator('#landscape').getByText('Network / SASE', { exact: true })).toBeVisible()
  await expect(page.locator('.domain-card .chip')).toHaveCount(0)
  await expect(page.locator('.domain-card').getByText('HORIZON', { exact: false })).toHaveCount(0)
  await expect(page.getByText('PREPARE', { exact: true })).toHaveCount(0)

  await expect(page.getByRole('button', { name: /Fortinet/ }).first()).toBeVisible()
  await expect(page.locator('.landscape .evidence-link').nth(2)).toContainText(/CrowdStrike|Upwind|Orca|Aqua/)
  await expect(page.locator('.landscape .evidence-link').nth(2)).not.toContainText('Alphabet')
  await expect(page.locator('#method summary')).toHaveText('How this is built')
  await expect(page.locator('#research-depth > summary')).toHaveText('M&A and funding activity')

  // The full scorecard's prints stay visible on first paint — no click
  // required to reach them.
  await expect(page.locator('#prints-heading')).toBeVisible()
  await expect(page.getByRole('heading', { name: 'Fortinet' })).toBeVisible()
  await expect(page.getByRole('heading', { name: 'SentinelOne' })).toBeVisible()
  await expect(page.getByRole('heading', { name: 'Entra / Ping / PE PAM' })).toBeVisible()
  // SecOps surfaces pre-click too: a promoted print-group title, not gated
  // behind any remaining disclosure.
  await expect(page.getByText('SecOps', { exact: true }).first()).toBeVisible()

  // M&A and funding activity is gated behind #research-depth: present in the
  // markup for evidence and crawlers, closed until opened. Closed <details>
  // content is not in the accessibility tree, so query the DOM.
  const activity = page.locator('#research-depth')
  await expect(activity.locator('#activity-heading')).toBeAttached()
  await expect(activity.locator('#activity-heading')).toBeHidden()
  await expect(page.getByText('Google closed Wiz')).toBeAttached()
  await expect(page.getByText('Alphabet announced ~$32B Wiz acquisition')).toHaveCount(0)
  await expect(page.getByText('Secuvy last disclosed seed')).toBeHidden()
  await expect(page.getByText('Platforms that bought identity are now seeding', { exact: false })).toHaveCount(0)

  await page.locator('#research-depth > summary').click()
  await expect(page.locator('#activity-heading')).toBeVisible()
  // Only becomes visible once the disclosure opens — the lead M&A/funding row.
  await expect(page.getByText('Zenity raised $115M Series C')).toBeVisible()

  // Opening #moved-depth reveals the tracked account "What moved" gives.
  await page.locator('#moved-depth > summary').click()
  await expect(page.locator('#moved-heading')).toBeVisible()
  await expect(page.locator('#moved .week-moved__col--judged')).toHaveCount(0)

  expect(pageErrors).toEqual([])
})

/**
 * D-76/autonomy-coverage-plan.md §3, step 1: this used to require at least
 * one JUDGED stamp on the front page (from the domain-stance cards, the
 * Platform-pressure "read" column, tracked hypotheses, or the standing-
 * thesis pointer). All four are removed from the front page, so the correct
 * invariant is now the opposite: none appear there.
 *
 * Neither /thesis/ nor an issue permalink ever rendered a literal
 * "JUDGED <date>" stamp — their own judgment is dated and signed a different
 * way ("Signed by <name> · <date>" in WeThink.tsx), which this pass leaves
 * untouched. There is nothing left in the app to assert the positive half of
 * the old test against.
 */
test('no judged stamps on the front page', async ({ page }) => {
  await page.goto('/')
  const judgedStamps = await page.locator('body').evaluate(() => {
    const candidates = Array.from(document.querySelectorAll('.stamp-label'))
    return candidates
      .filter((el) => (el.textContent ?? '').includes('JUDGED') && el.querySelector('time'))
      .map((el) => el.textContent ?? '')
  })
  expect(judgedStamps).toEqual([])
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

/**
 * Step 1 fix pass, item 2: the rail's "AS OF", the header's masthead date,
 * the front-page masthead's "Site updated", and the run-status line used to
 * each read from a different constant and could disagree (rail/header said
 * 21 Sep, run-status said 25 Sep). `LAST_UPDATED_ISO`/`LAST_UPDATED_DISPLAY`
 * (meta.ts) are now derived from `runStatus.lastChecked`, so this test reads
 * every one of those four rendered dates back off the page and fails if any
 * of them differs from `runStatus.lastChecked` — the single source.
 */
test('every as-of / site-updated / masthead date on the front page matches runStatus.lastChecked', async ({
  page,
}) => {
  await page.goto('/')

  expect(LAST_UPDATED_ISO).toBe(runStatus.lastChecked)
  expect(LAST_UPDATED_DISPLAY).toBe(formatLongDate(runStatus.lastChecked))

  await expect(page.locator('.rail__asof time')).toHaveAttribute('datetime', runStatus.lastChecked)
  await expect(page.locator('.rail__asof time')).toHaveText(formatShortDate(runStatus.lastChecked))

  await expect(page.locator('.site-header__updated time')).toHaveAttribute('datetime', runStatus.lastChecked)
  await expect(page.locator('.site-header__updated time')).toHaveText(formatLongDate(runStatus.lastChecked))

  await expect(page.locator('.site-masthead__stamps')).toContainText(
    `Site updated ${formatLongDate(runStatus.lastChecked)}`,
  )

  await expect(page.locator('#overview .run-status__line')).toContainText(
    `Figures checked ${formatShortDate(runStatus.lastChecked)}`,
  )
})
