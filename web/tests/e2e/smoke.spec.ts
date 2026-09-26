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
 *
 * Step 5 (autonomy-coverage-plan.md §3): this test used to also check
 * PrintGrid's scorecard ("This period", `#prints-heading`, print-card
 * headings for Fortinet/SentinelOne/"Entra / Ping / PE PAM") and the
 * vendor-lens control (`#vendor-lens-slot`) — both gone from this route.
 * MarketPicture and PrintGrid are replaced by the twelve-domain tracker
 * (MarketByDomain at `#market`, WhatChangedTracker at `#tracker-changed`,
 * CoverageStatement at `#tracker-coverage`); the vendor lens has nothing
 * left on this route to filter now that PrintGrid and the front page's
 * IssueLanes are both gone. See the assertions below for the new sections.
 *
 * AUTO-001 fix pass (2026-09-26), item 4: DomainBoard's LandscapeSection
 * (`#landscape`, "the security market, by domain" cards), "What moved"
 * (`#moved-depth`/`WhatMoved`), "M&A and funding activity"
 * (`#research-depth`/`ActivityBoard`), and "Market layers"
 * (`#layers`/`MarketLayersChart`) are all gone from the front page too — see
 * App.tsx's FrontPage doc-comment. None of the four is deleted; none renders
 * on any route any longer. This test now asserts they are absent rather than
 * asserting their (now-retired) collapsed-by-default behaviour.
 */
test('renders the market briefing without runtime errors', async ({ page }) => {
  const pageErrors: string[] = []
  page.on('pageerror', (error) => pageErrors.push(error.message))

  await page.goto('/')

  await expect(page.getByRole('heading', { level: 1 })).toHaveText(SITE_HEADLINE)

  // RunStatus replaces the old issue strip in the same #overview slot — an
  // honest statement of whether collection ran, never a judgment.
  //
  // AUTO-001 fix pass 2, item 4: runStatus is now derived from
  // generated/edgarFacts.json and generated/collectState.json (see
  // runStatus.ts's header comment) instead of hand-set, so this test reads
  // whatever that derivation actually produces rather than asserting a
  // fixed "updated" state — the two rescores' whole complaint was that the
  // page claimed "every source collected" with no run behind the claim.
  await expect(page.locator('#overview .run-status__line')).toContainText('Figures checked')
  expect(['updated', 'no-change', 'incomplete']).toContain(runStatus.state)
  if (runStatus.state === 'updated') {
    await expect(page.locator('#overview .run-status__line')).toContainText('every source collected')
  } else if (runStatus.state === 'no-change') {
    await expect(page.locator('#overview .run-status__line')).toContainText('no material change')
  } else {
    await expect(page.locator('#overview .run-status__line')).toContainText(
      runStatus.detail ?? 'collection incomplete',
    )
  }

  await expect(page.getByText('refreshed weekly')).toHaveCount(0)
  await expect(page.getByText('Tell me when the next edition publishes')).toHaveCount(0)

  // Pre-tracker material (item 4) is gone from the front page in full.
  await expect(page.locator('#landscape')).toHaveCount(0)
  await expect(page.locator('#moved-depth')).toHaveCount(0)
  await expect(page.locator('#research-depth')).toHaveCount(0)
  await expect(page.locator('#layers')).toHaveCount(0)
  await expect(page.locator('.domain-card')).toHaveCount(0)
  await expect(page.getByText('Tracked suppliers and the latest sourced figure for each')).toHaveCount(0)

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

  await expect(page.locator('#method summary')).toHaveText('How this is built')
  await expect(page.locator('#research summary')).toHaveText('Research & evidence')

  // Step 5: PrintGrid ("This period", #prints-heading) and its print-card
  // headings are gone from the front page — no route renders PrintGrid any
  // more. The vendor lens had nothing left to filter once PrintGrid and the
  // front page's IssueLanes both left, so it is gone too.
  await expect(page.locator('#prints-heading')).toHaveCount(0)
  await expect(page.locator('#vendor-lens-slot')).toHaveCount(0)

  // The twelve-domain tracker stays visible on first paint — no click
  // required to reach the market-by-domain tables, the 30-day change log,
  // or the coverage statement.
  await expect(page.locator('#market-heading')).toHaveText('The market by domain')
  await expect(page.locator('#market .tracker-domain')).toHaveCount(12)
  await expect(page.locator('#tracker-changed-heading')).toHaveText('What changed in the last 30 days')
  await expect(page.locator('#tracker-coverage-heading')).toHaveText('What this site covers')
  await expect(page.locator('.tracker-coverage__domains li').first()).toBeVisible()

  // A Microsoft segment row (item 1) shows "–" for revenue growth, not the
  // parent company's whole-company figure, and says plainly why.
  const entraRow = page.locator('#market .tracker-table tr', { has: page.getByTitle('Microsoft Entra ID') })
  await expect(entraRow.locator('td[data-label="Rev. growth"]')).toContainText('–')
  await expect(entraRow.locator('td[data-label="Ownership or last round"]')).toContainText('Segment of Microsoft')

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

  // The Microsoft Entra ID row (item 1: a segment may not borrow its
  // parent's figure) has no revenue or headline-metric evidence link, so its
  // Ownership cell's "src" control is what this test opens. Its evidence
  // record (TR-msft-entra-1) carries a non-empty limitations note, which
  // this test also uses to check the drawer's "Limitations / confounds"
  // section still renders when there is something to say.
  // The compact evidence button's visible text is "src", but its
  // accessible name is overridden by an aria-label naming the source and
  // date (EvidenceLink.tsx, evidenceCompactAriaLabel: "<context> — source:
  // ..."). The row also carries a second compact link for its "Latest
  // event" cell, so the Ownership one is picked out by that aria-label
  // prefix rather than by class alone.
  const entraRow = page.locator('#market .tracker-table tr', { has: page.getByTitle('Microsoft Entra ID') })
  await entraRow.getByLabel(/^Ownership — source:/).click()

  const dialog = page.getByRole('dialog', { name: 'Evidence' })
  await expect(dialog).toBeVisible()
  await expect(dialog.getByRole('link', { name: /Canonical source/ }).first()).toBeVisible()
  await expect(dialog.getByRole('heading', { name: 'Limitations / confounds' }).first()).toBeVisible()
  await expect(dialog.getByRole('link', { name: /github.com\/jessepike\/sec-market/ })).toHaveCount(0)

  await page.keyboard.press('Escape')
  await expect(dialog).toBeHidden()
})

/**
 * AUTO-001 fix pass (2026-09-26), item 4: the front page's evidence drawer
 * and evidence library must never surface a judged, thesis-era evidence
 * record — those carry an "Interpretation" the facts-only tracker does not
 * state. EvidenceDrawer hides an empty Interpretation/Limitations section
 * (every TR- tracker record's is empty by construction), and the front
 * page's evidence library (#research) now lists tracker (TR-) records only.
 */
test('the front page never opens a judged evidence record', async ({ page }) => {
  await page.goto('/')

  await page.locator('#research > summary').click()
  const libraryText = await page.locator('#research .evidence-library__list').innerText()
  expect(libraryText).not.toContain('strongest realized network-security acceleration')

  const entraRow = page.locator('#market .tracker-table tr', { has: page.getByTitle('Microsoft Entra ID') })
  await entraRow.getByLabel(/^Ownership — source:/).click()
  const dialog = page.getByRole('dialog', { name: 'Evidence' })
  await expect(dialog.getByRole('heading', { name: 'Interpretation' })).toHaveCount(0)
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
