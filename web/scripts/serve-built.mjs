import { createServer } from 'node:http'
import { readFile, stat } from 'node:fs/promises'
import { resolve, sep, extname } from 'node:path'

const root = resolve('dist')
const mime = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.xml': 'application/xml', '.svg': 'image/svg+xml', '.png': 'image/png', '.ico': 'image/x-icon', '.txt': 'text/plain' }
createServer(async (request, response) => {
  try {
    const path = decodeURIComponent(new URL(request.url, 'http://localhost').pathname)
    let file = resolve(root, `.${path}`)
    if (file !== root && !file.startsWith(root + sep)) throw new Error('Invalid path')
    if ((await stat(file)).isDirectory()) file = resolve(file, 'index.html')
    const body = await readFile(file)
    response.writeHead(200, { 'Content-Type': mime[extname(file)] ?? 'application/octet-stream' })
    response.end(body)
  } catch {
    response.writeHead(404, { 'Content-Type': 'text/plain' })
    response.end('Not found')
  }
}).listen(Number(process.env.SMP_TEST_PORT ?? 4173), '127.0.0.1')
