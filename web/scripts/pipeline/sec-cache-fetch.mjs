// Used only by the independent release gate's SEC refresh/certification commands.
// The collector's archived responses are verified again, with their actual ages.
import { readFileSync } from 'node:fs'
import { createHash } from 'node:crypto'
const manifest = JSON.parse(readFileSync(process.env.SMP_SEC_CACHE_MANIFEST, 'utf8'))
globalThis.fetch = async input => {
  const url = typeof input === 'string' ? input : input.url
  const item = manifest.sources[url]
  if (!item || !(url.startsWith('https://data.sec.gov/') || url.startsWith('https://www.sec.gov/Archives/'))) throw new Error('Unarchived SEC request held by release gate')
  const age = (Date.now() - Date.parse(item.checkedAt)) / 3600000
  if (!Number.isFinite(age) || age < -5/60 || age > manifest.overdueHours) throw new Error('Archived SEC check is stale or future dated')
  const bytes = readFileSync(item.path)
  if (createHash('sha256').update(bytes).digest('hex') !== item.sha256) throw new Error('Archived SEC response hash mismatch')
  return new Response(bytes, { status: 200, headers: { 'content-type': item.contentType, 'x-smp-source-checked-at': item.checkedAt } })
}
