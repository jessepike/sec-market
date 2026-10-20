// Durable object/record transport. No delete route and no model access to tokens.
const PREFIXES = {
  collect: ['objects/', 'observations/', 'runs/'],
  verify: ['objects/', 'facts/', 'fact-observations/', 'document-validation/', 'heads/source-', 'heads/latest-run'],
  publish: ['objects/', 'releases/', 'rollback-events/', 'heads/production'],
}
const encode = new TextEncoder()
export function stable(v) {
  if (Array.isArray(v)) return '[' + v.map(stable).join(',') + ']'
  if (v && typeof v === 'object') return '{' + Object.keys(v).sort().map(k=>JSON.stringify(k)+':'+stable(v[k])).join(',') + '}'
  return JSON.stringify(v)
}
async function hash(body) {
  return [...new Uint8Array(await crypto.subtle.digest('SHA-256', body))].map(b=>b.toString(16).padStart(2,'0')).join('')
}
function safeEqual(a,b) {
  if (!a || !b || a.length !== b.length) return false
  let diff=0
  for(let i=0;i<a.length;i++) diff|=a.charCodeAt(i)^b.charCodeAt(i)
  return diff===0
}
function response(value,status=200) { return new Response(JSON.stringify(value),{status,headers:{'content-type':'application/json','cache-control':'no-store'}}) }
function keyAllowed(key) { return /^[A-Za-z0-9][A-Za-z0-9_./-]*$/.test(key) && !key.split('/').includes('..') }

export async function handle(request,env) {
  if (!env.ARCHIVE || !env.READ_TOKEN || !env.COLLECT_TOKEN || !env.VERIFY_TOKEN || !env.PUBLISH_TOKEN) return response({error:'ARCHIVE_NOT_CONFIGURED'},503)
  const token=request.headers.get('authorization')?.replace(/^Bearer /,'')
  const role=[['read',env.READ_TOKEN],['collect',env.COLLECT_TOKEN],['verify',env.VERIFY_TOKEN],['publish',env.PUBLISH_TOKEN]].find(([,secret])=>safeEqual(token,secret))?.[0]
  if(!role) return response({error:'UNAUTHORIZED'},401)
  const url=new URL(request.url)
  if(request.method==='DELETE') return response({error:'DELETE_PROHIBITED'},405)
  if(url.pathname==='/v1/list' && request.method==='GET') {
    if(role!=='read') return response({error:'READ_ROLE_REQUIRED'},403)
    const result=await env.ARCHIVE.list({limit:1000,cursor:url.searchParams.get('cursor')||undefined,include:['customMetadata']})
    return response({keys:result.objects.map(o=>({key:o.key,bytes:o.size,sha256:o.customMetadata?.sha256})),truncated:result.truncated,cursor:result.cursor??null})
  }
  const head=url.pathname.startsWith('/v1/heads/')
  if(!head&&!url.pathname.startsWith('/v1/records/')) return response({error:'NOT_FOUND'},404)
  const suffix=decodeURIComponent(url.pathname.slice(head?10:12))
  if(head && !/^[A-Za-z0-9_-]+$/.test(suffix)) return response({error:'INVALID_HEAD'},400)
  const key=head?`heads/${suffix}.json`:suffix
  if(!keyAllowed(key)) return response({error:'INVALID_KEY'},400)
  if(!head&&key.startsWith('heads/')) return response({error:'HEAD_REQUIRES_CAS_ROUTE'},400)
  if(request.method==='GET') {
    const item=await env.ARCHIVE.get(key)
    return item?new Response(item.body,{headers:{'content-type':'application/octet-stream','cache-control':'no-store','x-smp-sha256':item.customMetadata?.sha256||'','x-smp-writer-role':item.customMetadata?.writerRole||''}}):response({error:'NOT_FOUND'},404)
  }
  if(request.method!=='PUT') return response({error:'METHOD_NOT_ALLOWED'},405)
  if(!(PREFIXES[role]||[]).some(prefix=>key.startsWith(prefix))) return response({error:'WRITE_ROLE_DENIED'},403)
  if(Number(request.headers.get('content-length')||0)>32000000) return response({error:'BODY_TOO_LARGE'},413)
  const bytes=await request.arrayBuffer()
  if(bytes.byteLength>32000000) return response({error:'BODY_TOO_LARGE'},413)
  if(head) {
    let input
    try { input=JSON.parse(new TextDecoder().decode(bytes)) } catch { return response({error:'CAS_SHAPE'},400) }
    if(!input||typeof input!=='object') return response({error:'CAS_SHAPE'},400)
    if(!Object.hasOwn(input,'expected')||!Object.hasOwn(input,'value')) return response({error:'CAS_SHAPE'},400)
    const old=await env.ARCHIVE.get(key)
    const previous=old?JSON.parse(await old.text()):null
    if(stable(previous)!==stable(input.expected)) return response({error:'STALE_HEAD'},409)
    const body=encode.encode(stable(input.value))
    const result=await env.ARCHIVE.put(key,body,{onlyIf:old?{etagMatches:old.etag}:{etagDoesNotMatch:'*'},customMetadata:{sha256:await hash(body),writerRole:role}})
    return result?response({ok:true}):response({error:'CAS_CONFLICT'},409)
  }
  const sha=await hash(bytes)
  if(request.headers.get('x-smp-sha256')!==sha || (key.startsWith('objects/')&&key!==`objects/${sha}`)) return response({error:'HASH_MISMATCH'},400)
  const old=await env.ARCHIVE.head(key)
  if(old) return old.customMetadata?.sha256===sha?response({ok:true,idempotent:true}):response({error:'IMMUTABLE_COLLISION'},409)
  const result=await env.ARCHIVE.put(key,bytes,{onlyIf:{etagDoesNotMatch:'*'},customMetadata:{sha256:sha,writerRole:role}})
  if(!result) {
    const raced=await env.ARCHIVE.head(key)
    return raced?.customMetadata?.sha256===sha?response({ok:true,idempotent:true}):response({error:'IMMUTABLE_COLLISION'},409)
  }
  return response({ok:true,sha256:sha},201)
}
export default {async fetch(request,env) {
  try{return await handle(request,env)}catch{return response({error:'ARCHIVE_REQUEST_FAILED'},500)}
}}
