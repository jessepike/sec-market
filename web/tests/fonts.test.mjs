import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { resolve, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'
import test from 'node:test'
import { verifyFontAssets } from '../scripts/check-font-delivery.mjs'

const web = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const manifest = JSON.parse(readFileSync(resolve(web, 'fonts/source-manifest.json')))
const altered = (suffix, change) => path => {
  const bytes = readFileSync(path)
  return path.endsWith(suffix) ? Buffer.from(change(bytes)) : bytes
}

test('all original faces, exact binaries and complete licenses remain available locally', () => {
  const result = verifyFontAssets(web)
  assert.equal(result.assets.reduce((sum, asset) => sum + asset.bytes, 0), 396100)
  assert.equal(result.semanticAdmission, false)
})

test('changed binary bytes fail even with a valid WOFF2 signature', () => {
  assert.throws(() => verifyFontAssets(web, altered(manifest.assets[0].path, bytes => {
    const copy = Buffer.from(bytes); copy[copy.length - 1] ^= 1; return copy
  })), /Font asset hash differs/)
})

test('a font weight or Unicode coverage change cannot hide behind local delivery', () => {
  for (const [before, after] of [['font-weight: 600', 'font-weight: 700'], ['U+0102', 'U+0103']]) {
    assert.throws(() => verifyFontAssets(web, altered('/src/fonts.css', bytes => bytes.toString().replace(before, after))), /Local font declarations differ/)
  }
})

test('license truncation and restored external runtime links fail', () => {
  assert.throws(() => verifyFontAssets(web, altered(manifest.licenses[0].path, bytes => bytes.subarray(0, 100))))
  assert.throws(() => verifyFontAssets(web, altered('/index.html', bytes => bytes + '<link href="https://fonts.googleapis.com/css2">')))
})
