import { writeFileSync } from 'node:fs'
import { createHash } from 'node:crypto'
const folder = process.argv[2]
const records = []
for (const [target,base] of [['production','https://securitymarketpulse.com'],['local','http://127.0.0.1:4371']]) {
  for (const name of ['app-release.json','deployment-receipt.json','daily-coverage.json','factual-corrections.json','tracker.json']) {
    const at = new Date().toISOString()
    const response = await fetch(`${base}/${name}`,{signal:AbortSignal.timeout(30000)})
    const bytes = Buffer.from(await response.arrayBuffer())
    records.push({target,url:`${base}/${name}`,observedAt:at,status:response.status,contentType:response.headers.get('content-type'),sha256:createHash('sha256').update(bytes).digest('hex'),bytes:bytes.length})
    writeFileSync(`${folder}/${target}-${name}`,bytes)
  }
}
writeFileSync(`${folder}/public-readback-index.json`,JSON.stringify(records,null,2)+'\n')
