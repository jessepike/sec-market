import { expect, test } from '@playwright/test'
import { corrections } from '../../src/data/corrections.ts'
import { factualCorrectionHistory, publicCorrectionsJsonPayload } from '../../src/data/factualCorrectionHelpers.ts'
import { evidenceById } from '../../src/data/evidence.ts'
import { SITE_URL } from '../../src/data/meta.ts'
import { factualCorrectionBundle, factualCorrectionGroups, factualCorrectionSourceEvidenceIds } from '../../src/data/tracker/correctionData.ts'
import { trackerSuppliers } from '../../src/data/tracker/suppliers.ts'

const correction = corrections.find((c) => c.id === 'C-2026-09-20-01')!
const historySources = { evidence: evidenceById, suppliers: trackerSuppliers, groupEvidenceIds: factualCorrectionSourceEvidenceIds }
const factualHistory = factualCorrectionHistory(factualCorrectionGroups, historySources, SITE_URL)

test.describe('corrections (SEC-MARKET-FABLE-001 T6-13)', () => {
  // The correction is fixed to the issue it corrected (2026-w36), not to
  // whatever issue happens to be newest — so this and the next test both
  // target that issue's own permalink, never "/" or `latestIssue.id`. Both
  // used to point at the front page / latestIssue, which only worked by
  // coincidence while 2026-w36 was still the newest issue; publishing any
  // later issue broke that assumption, which is exactly what happened the
  // first time this suite ran against a newly-signed 2026-w37.
  test("the corrected issue's own page shows the corrected note beside both items, originals still present", async ({
    page,
  }) => {
    await page.goto(`/issues/${correction.issueId}/`)

    for (const original of [
      'Zscaler FY2026 revenue grows to $898.2M, +25% YoY; ARR grows to $3,771M, +25%',
      'Palo Alto FY2026 revenue grows 34% to $3.41B; Next-Gen Security ARR $9.10B, +63%',
    ]) {
      await expect(page.getByText(original, { exact: true })).toBeVisible()
    }

    for (const reading of correction.correctedReadings) {
      const item = page.locator(`text=${reading.correctedHeadline}`).first()
      await expect(item).toBeVisible()
    }

    await expect(page.getByText(/CORRECTED/).first()).toBeVisible()
    await expect(page.getByRole('link', { name: 'See correction' }).first()).toHaveAttribute(
      'href',
      `/corrections/#${correction.id}`,
    )
  })

  test('issue permalink shows the corrected note beside both items', async ({ page }) => {
    await page.goto(`/issues/${correction.issueId}/`)
    for (const reading of correction.correctedReadings) {
      await expect(page.locator(`text=${reading.correctedHeadline}`).first()).toBeVisible()
    }
    await expect(page.getByRole('link', { name: 'See correction' }).first()).toHaveAttribute(
      'href',
      `/corrections/#${correction.id}`,
    )
  })

  test('/corrections/ renders the entry and the anchor resolves', async ({ page }) => {
    await page.goto('/corrections/')
    await expect(page.getByRole('heading', { level: 1 })).toHaveText('Corrections')
    await expect(page.locator(`#${correction.id}`)).toBeVisible()
    await expect(page.locator(`#${correction.id}`)).toContainText(correction.approvedBy)
    await expect(page.locator(`#${correction.id}`).getByRole('link', { name: `Issue ${correction.issueId}` })).toHaveAttribute(
      'href',
      `/issues/${correction.issueId}/`,
    )

    await page.goto(`/corrections/#${correction.id}`)
    await expect(page.locator(`#${correction.id}`)).toBeInViewport()
  })

  test('/corrections.json is served and matches the source data', async ({ request }) => {
    const response = await request.get('/corrections.json')
    expect(response.status()).toBe(200)
    const body = await response.json()
    expect(Array.isArray(body)).toBe(true)
    expect(body).toEqual(publicCorrectionsJsonPayload(corrections, factualCorrectionGroups, historySources, SITE_URL))
    const entry = body.find((c: { id: string }) => c.id === correction.id)
    expect(entry).toBeTruthy()
    expect(entry.issueId).toBe(correction.issueId)
    expect(entry.url).toBe(`https://securitymarketpulse.com/corrections/#${correction.id}`)
    expect(entry.approvedBy).toBe(correction.approvedBy)
    for (const group of factualCorrectionGroups) {
      const factual = body.find((candidate: { id: string }) => candidate.id === group.id)
      expect(factual.kind).toBe(group.reviewScope === 'publisher_disclosure_only' ? 'publisher_disclosure_correction' : 'source_verified_factual_correction')
      expect(factual.date).toBe(group.date)
      expect(factual.note).toBe(group.note)
      expect(factual.admission).toEqual(group.admission)
      expect(factual).not.toHaveProperty('approvedBy')
      expect(factual).not.toHaveProperty('issueId')
    }
  })

  test('/corrections/ retains owner notes alongside every source-verified factual correction', async ({ page }) => {
    await page.goto('/corrections/')
    await expect(page.locator('.corrections-page__item')).toHaveCount(corrections.length + factualHistory.length)
    for (const legacy of corrections) {
      const item = page.locator(`[id="${legacy.id}"]`)
      await expect(item.locator('.corrections-page__approved')).toHaveText(`Approved by ${legacy.approvedBy}`)
      await expect(item.locator('.corrections-page__text')).toHaveText(legacy.text)
    }
    for (const factual of factualHistory) {
      const item = page.locator(`[id="${factual.id}"]`)
      await expect(item).toBeVisible()
      await expect(item.locator('time')).toHaveAttribute('datetime', factual.date)
      await expect(item.locator('.corrections-page__text')).toHaveText(factual.note)
      await expect(item).toContainText(factual.reviewScope === 'publisher_disclosure_only' ? 'Publisher disclosure correction' : 'Source-verified factual correction')
      await expect(item.locator('.corrections-page__approved')).toHaveCount(0)
      await expect(item).not.toContainText('Approved by')
      for (const source of factual.sources) {
        await expect(item.getByRole('link', { name: source.title, exact: true })).toHaveAttribute('href', source.url)
      }
      for (const change of factual.changes) {
        await expect(item).toContainText(`Before: ${change.before}`)
        await expect(item).toContainText(`After: ${change.after}`)
      }
      await expect(item).toContainText(factual.admission.reviewSha256)
    }
  })

  test('/factual-corrections.json matches the complete gate projection', async ({ request }) => {
    const response = await request.get('/factual-corrections.json')
    expect(response.status()).toBe(200)
    expect(await response.json()).toEqual(factualCorrectionBundle)
  })
})
