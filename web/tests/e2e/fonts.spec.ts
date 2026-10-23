import { test, expect } from '@playwright/test'
import { inspectFontDelivery, verifyFontAssets } from '../../scripts/check-font-delivery.mjs'

const manifest = verifyFontAssets()
for (const width of [1440, 390]) {
  test(`all pinned fonts load without outside network at ${width}px`, async ({ page, baseURL }) => {
    await page.setViewportSize({ width, height: width === 390 ? 844 : 900 })
    const proof = await inspectFontDelivery(page, baseURL!, manifest)
    expect(proof.googleRequests).toBe(0)
    expect(proof.fonts).toHaveLength(24)
  })
}

test('a missing font fails even when fallback text remains readable', async ({ page, baseURL }) => {
  await expect(inspectFontDelivery(page, baseURL!, manifest, { corruptAsset: manifest.assets[0].localUrl })).rejects.toThrow()
})

test('a corrupt font fails even with a successful HTTP response', async ({ page, baseURL }) => {
  await expect(inspectFontDelivery(page, baseURL!, manifest, { invalidAsset: manifest.assets[0].localUrl })).rejects.toThrow()
})

test('a reintroduced Google stylesheet fails with outside network denied', async ({ page, baseURL }) => {
  await page.addInitScript(() => document.addEventListener('DOMContentLoaded', () => {
    const link = document.createElement('link')
    link.rel = 'stylesheet'; link.href = 'https://fonts.googleapis.com/css2?family=Archivo'
    document.head.append(link)
  }))
  await expect(inspectFontDelivery(page, baseURL!, manifest)).rejects.toThrow(/Outside network dependency/)
})
