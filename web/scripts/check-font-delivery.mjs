import assert from 'node:assert/strict'
import { createHash } from 'node:crypto'
import { createServer } from 'node:http'
import { readFileSync, writeFileSync, mkdirSync, readdirSync, statSync } from 'node:fs'
import { dirname, resolve, extname, sep } from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'
import { chromium } from '@playwright/test'

const webRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const sha = body => createHash('sha256').update(body).digest('hex')
const canonical = value => Array.isArray(value) ? `[${value.map(canonical).join(',')}]` : value && typeof value === 'object' ? `{${Object.keys(value).sort().map(key => `${JSON.stringify(key)}:${canonical(value[key])}`).join(',')}}` : JSON.stringify(value)
const mime = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.xml': 'application/xml', '.svg': 'image/svg+xml', '.png': 'image/png', '.ico': 'image/x-icon', '.txt': 'text/plain', '.woff2': 'font/woff2' }

export function verifyFontAssets(web = webRoot, read = readFileSync) {
  const manifest = JSON.parse(read(resolve(web, 'fonts/source-manifest.json')))
  assert.equal(manifest.schemaVersion, 1)
  assert.equal(manifest.kind, 'pinned_font_delivery_assets')
  const source = read(resolve(web, '..', manifest.sourceCss.path))
  assert.equal(sha(source), manifest.sourceCss.sha256, 'Upstream font CSS changed')
  assert.equal(source.length, manifest.sourceCss.bytes)
  const faces = [...source.toString().matchAll(/@font-face\s*\{([^}]+)\}/g)]
  assert.equal(faces.length, 39)
  assert.equal(manifest.faces.length, 39)
  assert.equal(manifest.assets.length, 24)
  assert.equal(new Set(manifest.assets.map(asset => asset.sourceUrl)).size, 24)
  const urls = new Set([...source.toString().matchAll(/url\((https:\/\/[^)]+)\)/g)].map(match => match[1]))
  assert.deepEqual([...urls].sort(), manifest.assets.map(asset => asset.sourceUrl).sort())
  assert.deepEqual([...new Set(manifest.faces.map(face => face.family))].sort(), ['Archivo', 'IBM Plex Mono', 'IBM Plex Sans'])
  for (const [index, match] of faces.entries()) {
    const fields = Object.fromEntries([...match[1].matchAll(/([\w-]+)\s*:\s*([^;]+);/g)].map(field => [field[1], field[2].trim()]))
    const face = manifest.faces[index]
    assert.equal(fields['font-family'].replace(/^['"]|['"]$/g, ''), face.family)
    assert.equal(Number(fields['font-weight']), face.weight)
    assert.equal(fields['font-style'], face.style)
    assert.equal(fields['font-display'], face.display)
    assert.equal(fields['font-stretch'] ?? null, face.stretch)
    assert.equal(fields['unicode-range'], face.unicodeRange)
    assert.equal(fields.src, `url(${face.sourceUrl}) format('woff2')`)
  }
  let expected = source.toString()
  for (const asset of manifest.assets) {
    assert.match(asset.sourceUrl, /^https:\/\/fonts\.gstatic\.com\/s\/(archivo\/v25|ibmplexmono\/v20|ibmplexsans\/v23)\/[^/]+\.woff2$/)
    assert.equal(asset.localUrl, `/assets/fonts/${asset.sha256}-${asset.sourceUrl.split('/').at(-1)}`)
    assert.equal(asset.path, `web/public${asset.localUrl}`)
    const body = read(resolve(web, '..', asset.path))
    assert.equal(body.subarray(0, 4).toString(), 'wOF2', 'Invalid WOFF2 file')
    assert.equal(body.length, asset.bytes)
    assert.equal(sha(body), asset.sha256, 'Font asset hash differs')
    expected = expected.replaceAll(asset.sourceUrl, asset.localUrl)
  }
  const local = read(resolve(web, '..', manifest.localCss.path))
  assert.equal(local.toString(), expected, 'Local font declarations differ beyond source URLs')
  assert.equal(local.length, manifest.localCss.bytes)
  assert.equal(sha(local), manifest.localCss.sha256)
  assert.equal(manifest.licenses.length, 3)
  assert.deepEqual(manifest.licenses.map(license => license.family).sort(), ['Archivo', 'IBM Plex Mono', 'IBM Plex Sans'])
  for (const license of manifest.licenses) {
    assert.match(license.upstreamRevision, /^[a-f0-9]{40}$/)
    assert.ok(license.sourceUrl.startsWith(`https://raw.githubusercontent.com/google/fonts/${license.upstreamRevision}/ofl/`))
    const body = read(resolve(web, '..', license.path))
    assert.equal(body.length, license.bytes)
    assert.equal(sha(body), license.sha256)
    assert.match(body.toString(), /SIL OPEN FONT LICENSE Version 1\.1/)
    assert.match(body.toString(), /Copyright/)
    if (license.family.startsWith('IBM')) assert.match(body.toString(), /Reserved Font Name "Plex"/)
  }
  assert.doesNotMatch(read(resolve(web, 'index.html')).toString(), /fonts\.(googleapis|gstatic)\.com/)
  assert.match(read(resolve(web, 'src/index.css')).toString(), /^@import ['"]\.\/fonts\.css['"];/)
  return manifest
}

/** Outside requests are either denied or, only in baseline mode, replayed from pinned bytes. */
export async function inspectFontDelivery(page, base, manifest, { mode = 'candidate', web = webRoot, corruptAsset = null, invalidAsset = null, route = '/' } = {}) {
  const origin = new URL(base).origin
  const requests = [], blocked = [], failures = [], fonts = [], pending = [], fontErrors = []
  const byUrl = new Map(manifest.assets.map(asset => [mode === 'baseline_replay' ? asset.sourceUrl : origin + asset.localUrl, asset]))
  page.on('request', request => requests.push({ url: request.url(), type: request.resourceType() }))
  page.on('requestfailed', request => failures.push({ url: request.url(), error: request.failure()?.errorText }))
  page.on('console', message => { if (/failed to decode downloaded font|OTS parsing error/i.test(message.text())) fontErrors.push(message.text()) })
  page.on('response', response => {
    const asset = byUrl.get(response.url())
    if (asset) pending.push((async () => {
      const body = await response.body()
      fonts.push({ url: response.url(), status: response.status(), mime: response.headers()['content-type'], bytes: body.length, sha256: sha(body) })
    })().catch(error => failures.push({ url: response.url(), error: error.message })))
  })
  await page.route('**/*', async intercepted => {
    const url = intercepted.request().url()
    if (new URL(url).origin === origin) {
      if (corruptAsset && new URL(url).pathname === corruptAsset) return intercepted.fulfill({ status: 404, contentType: 'text/plain', body: 'Missing fixture font' })
      if (invalidAsset && new URL(url).pathname === invalidAsset) return intercepted.fulfill({ status: 200, contentType: 'font/woff2', body: 'wOF2 invalid fixture font' })
      return intercepted.continue()
    }
    if (mode === 'baseline_replay') {
      if (url === manifest.sourceCss.url) return intercepted.fulfill({ status: 200, contentType: 'text/css', body: readFileSync(resolve(web, '..', manifest.sourceCss.path)) })
      const asset = byUrl.get(url)
      if (asset) return intercepted.fulfill({ status: 200, contentType: 'font/woff2', body: readFileSync(resolve(web, '..', asset.path)) })
    }
    blocked.push(url)
    return intercepted.abort('blockedbyclient')
  })
  await page.goto(new URL(route, origin).href)
  const loaded = await page.evaluate(async () => {
    await document.fonts.ready
    await Promise.all([...document.fonts].map(face => face.load()))
    await document.fonts.ready
    const families = ['Archivo', 'IBM Plex Mono', 'IBM Plex Sans']
    return { faces: [...document.fonts].map(face => ({ family: face.family.replace(/^['"]|['"]$/g, ''), weight: face.weight, style: face.style, status: face.status })),
      checks: Object.fromEntries(families.map(family => [family, document.fonts.check(`600 16px "${family}"`, 'Security Market Pulse 123')])) }
  })
  await Promise.all(pending)
  assert.equal(blocked.length, 0, `Outside network dependency: ${blocked.join(', ')}`)
  const google = requests.filter(request => /^https:\/\/fonts\.(googleapis|gstatic)\.com\//.test(request.url))
  if (mode === 'candidate') assert.equal(google.length, 0, 'Candidate requested Google fonts')
  assert.equal(loaded.faces.length, 39, 'Incomplete declared font inventory')
  assert.ok(loaded.faces.every(face => face.status === 'loaded'), 'A font face did not load')
  assert.ok(Object.values(loaded.checks).every(Boolean), 'Intended family unavailable')
  assert.deepEqual(fontErrors, [], 'Browser font decoding failed')
  assert.equal(fonts.length, 24, 'Incomplete font response inventory')
  for (const font of fonts) {
    const expected = byUrl.get(font.url)
    assert.equal(font.status, 200, 'Font HTTP failure')
    assert.equal(font.mime, 'font/woff2', 'Font MIME differs')
    assert.equal(font.bytes, expected.bytes)
    assert.equal(font.sha256, expected.sha256, 'Served font bytes differ')
  }
  const licenses = []
  if (mode === 'candidate') for (const license of manifest.licenses) {
    const response = await page.request.get(origin + license.localUrl)
    assert.equal(response.status(), 200)
    const body = await response.body()
    assert.equal(sha(body), license.sha256)
    licenses.push({ url: response.url(), status: response.status(), sha256: sha(body), bytes: body.length })
  }
  const layout = await page.evaluate(() => {
    const box = selector => {
      const element = document.querySelector(selector)
      if (!element) return null
      const rect = element.getBoundingClientRect(), style = getComputedStyle(element)
      return { x: rect.x, y: rect.y, width: rect.width, height: rect.height, fontFamily: style.fontFamily, fontWeight: style.fontWeight, fontSize: style.fontSize, lineHeight: style.lineHeight, text: element.textContent }
    }
    return { width: innerWidth, height: innerHeight, scrollWidth: document.documentElement.scrollWidth, scrollHeight: document.body.scrollHeight,
      masthead: box('.site-masthead'), title: box('h1'), firstChange: box('.desk-change'), growth: box('#reported-growth'), table: box('.desk-growth__rows'), correction: box('.corrections-page__item') }
  })
  assert.equal(layout.scrollWidth, layout.width, 'Horizontal overflow')
  return { mode, route, fontReadiness: true, declaredFaces: loaded.faces, familyChecks: loaded.checks, fonts: fonts.sort((a, b) => a.url.localeCompare(b.url)), licenses,
    googleRequests: google.length, outsideRequestsDenied: blocked, requests, failures, fontErrors, layout }
}

function serve(directory) {
  const root = resolve(directory)
  const server = createServer((request, response) => {
    try {
      let file = resolve(root, `.${decodeURIComponent(new URL(request.url, 'http://localhost').pathname)}`)
      assert.ok(file === root || file.startsWith(root + sep))
      if (statSync(file).isDirectory()) file = resolve(file, 'index.html')
      response.writeHead(200, { 'Content-Type': mime[extname(file)] ?? 'application/octet-stream' })
      response.end(readFileSync(file))
    } catch { response.writeHead(404); response.end('Not found') }
  })
  return new Promise(resolveServer => server.listen(0, '127.0.0.1', () => resolveServer({ origin: `http://127.0.0.1:${server.address().port}`, close: () => new Promise(done => server.close(done)) })))
}

function inventory(directory) {
  const files = []
  const walk = root => { for (const name of readdirSync(root).sort()) { const path = resolve(root, name); if (statSync(path).isDirectory()) walk(path); else { const body = readFileSync(path); files.push({ path: path.slice(resolve(directory).length + 1), sha256: sha(body), bytes: body.length }) } } }
  walk(resolve(directory)); return files
}

async function comparePixels(browser, before, after) {
  const page = await browser.newPage()
  try {
    return await page.evaluate(async ([left, right]) => {
      const images = await Promise.all([left, right].map(async body => { const image = new Image(); image.src = body; await image.decode(); return image }))
      if (images[0].width !== images[1].width || images[0].height !== images[1].height) return { sameDimensions: false, before: { width: images[0].width, height: images[0].height }, after: { width: images[1].width, height: images[1].height } }
      const arrays = images.map(image => { const canvas = document.createElement('canvas'); canvas.width = image.width; canvas.height = image.height; const context = canvas.getContext('2d'); context.drawImage(image, 0, 0); return context.getImageData(0, 0, image.width, image.height).data })
      let changedPixels = 0
      for (let index = 0; index < arrays[0].length; index += 4) if ([0, 1, 2, 3].some(offset => arrays[0][index + offset] !== arrays[1][index + offset])) changedPixels++
      return { sameDimensions: true, width: images[0].width, height: images[0].height, changedPixels, totalPixels: images[0].width * images[0].height }
    }, [before, after].map(body => `data:image/png;base64,${body.toString('base64')}`))
  } finally { await page.close() }
}

export async function compareFontDelivery(baselineDirectory, candidateDirectory, output, web = webRoot) {
  const manifest = verifyFontAssets(web)
  mkdirSync(output, { recursive: true })
  const baseline = await serve(baselineDirectory), candidate = await serve(candidateDirectory)
  const browser = await chromium.launch()
  const routes = ['/', '/corrections/', '/issues/2026-w36/']
  const results = []
  try {
    for (const width of [1440, 390]) for (const route of routes) {
      const records = []
      for (const [mode, target] of [['baseline_replay', baseline], ['candidate', candidate]]) {
        const context = await browser.newContext({ viewport: { width, height: width === 390 ? 844 : 900 }, serviceWorkers: 'block', reducedMotion: 'reduce' })
        try {
          const page = await context.newPage()
          const proof = await inspectFontDelivery(page, target.origin, manifest, { mode, web, route })
          const label = route === '/' ? 'root' : route.replaceAll('/', '').replaceAll('#', '-')
          const captures = {}
          for (const fullPage of [false, true]) {
            const file = resolve(output, `${mode}-${label}-${width}-${fullPage ? 'full' : 'fold'}.png`)
            const body = await page.screenshot({ path: file, fullPage, animations: 'disabled' })
            captures[fullPage ? 'full' : 'fold'] = { path: file, sha256: sha(body), bytes: body.length }
          }
          records.push({ ...proof, captures })
        } finally { await context.close() }
      }
      const pixels = {}
      for (const type of ['fold', 'full']) pixels[type] = await comparePixels(browser, readFileSync(records[0].captures[type].path), readFileSync(records[1].captures[type].path))
      results.push({ width, route, baseline: records[0], candidate: records[1], pixels, identicalLayout: canonical(records[0].layout) === canonical(records[1].layout) })
    }
  } finally { await browser.close(); await baseline.close(); await candidate.close() }
  const beforeFiles = inventory(baselineDirectory), afterFiles = inventory(candidateDirectory)
  const samePublicJson = beforeFiles.filter(file => file.path.endsWith('.json') && file.path !== 'app-release.json').every(file => afterFiles.some(candidateFile => candidateFile.path === file.path && candidateFile.sha256 === file.sha256))
  assert.ok(samePublicJson, 'Public data changed during font-only comparison')
  const receipt = { schemaVersion: 1, kind: 'font_delivery_repair_verification', checkedAt: new Date().toISOString(),
    applicationRevision: JSON.parse(readFileSync(resolve(candidateDirectory, 'app-release.json'))).appRevision,
    sourceManifestSha256: sha(readFileSync(resolve(web, 'fonts/source-manifest.json'))), sourceCss: manifest.sourceCss,
    assetSources: manifest.assets, licenses: manifest.licenses, browserVersion: browser.version(), viewports: [{ width: 1440, height: 900 }, { width: 390, height: 844 }],
    contextPolicy: { freshContexts: true, serviceWorkers: 'block', outsideNetworkDenied: true, baselineFontsReplayedFromPinnedBytes: true, candidateFontsReplayed: false },
    baseline: { directory: resolve(baselineDirectory), inventorySha256: sha(Buffer.from(canonical(beforeFiles))), files: beforeFiles, originalBrowserStatus: 'one timeout among 38 tests; Google font requests pending' },
    candidate: { directory: resolve(candidateDirectory), inventorySha256: sha(Buffer.from(canonical(afterFiles))), files: afterFiles }, samePublicJson,
    results, identicalPixels: results.every(result => Object.values(result.pixels).every(diff => diff.sameDimensions && diff.changedPixels === 0)), identicalLayout: results.every(result => result.identicalLayout),
    visualInspection: { performed: false, pairs: [], note: 'Requires the agent to open and inspect the retained images.' },
    semanticAdmission: false, marketSourceRequests: 0, modelCalls: 0, productionChanged: false }
  writeFileSync(resolve(output, 'font-delivery-replay.json'), JSON.stringify(receipt, null, 2) + '\n')
  return receipt
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  try {
    const [baseline, candidate, output] = process.argv.slice(2)
    assert.ok(baseline && candidate && output, 'Usage: node scripts/check-font-delivery.mjs <baseline-dist> <candidate-dist> <output-directory>')
    const receipt = await compareFontDelivery(baseline, candidate, output)
    console.log(JSON.stringify({ identicalPixels: receipt.identicalPixels, identicalLayout: receipt.identicalLayout, comparisons: receipt.results.length, receipt: resolve(output, 'font-delivery-replay.json') }))
    assert.ok(receipt.identicalPixels && receipt.identicalLayout, 'Font delivery changed pixels or layout; inspect the receipt')
  } catch (error) { console.error(error.message); process.exitCode = 2 }
}
