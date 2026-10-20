// Runs outside GitHub Actions. Only current, complete, pinned coverage is healthy.
export function inspect(receipt,expected,now=Date.now()) {
  const age=(now-Date.parse(receipt?.checkedAt))/3600000
  const reasons=[]
  if(!Number.isFinite(age)||age<0||age>expected.overdueHours) reasons.push('MISSING_OR_OVERDUE_RECEIPT')
  if(receipt?.contractSha256!==expected.contractSha256) reasons.push('CONTRACT_CHANGED_OR_UNKNOWN')
  if(receipt?.supplierCount!==expected.supplierCount||receipt?.requiredTasks!==expected.requiredTasks) reasons.push('COVERAGE_DENOMINATOR_DIFFERS')
  if(receipt?.complete!==true||receipt?.successfulTasks!==expected.requiredTasks||!Array.isArray(receipt?.gapTaskIds)||receipt.gapTaskIds.length) reasons.push('REQUIRED_COVERAGE_INCOMPLETE')
  return {healthy:reasons.length===0,reasons,runId:receipt?.runId??null}
}
export function inspectDeployment(expected, live) {
  const pins=['appRevision','dataReleaseId','snapshotSha256','artifactSha256','contractSha256']
  return expected && live?.ready === true && pins.every(k => typeof expected[k] === 'string' && expected[k].length > 0 && live[k] === expected[k])
}
export async function check(env,fetcher=fetch,now=Date.now()) {
  if(!env.COVERAGE_URL||!env.RELEASE_EXPECTATION_URL||!env.LIVE_RECEIPT_URL||!env.EXPECTED_CONTRACT_SHA256||!env.EXPECTED_SUPPLIERS||!env.EXPECTED_REQUIRED_TASKS||!env.ALERT_WEBHOOK||!env.ALERT_STATE) throw new Error('WATCHDOG_NOT_CONFIGURED')
  if([env.COVERAGE_URL,env.RELEASE_EXPECTATION_URL,env.LIVE_RECEIPT_URL,env.ALERT_WEBHOOK].some(url=>new URL(url).protocol!=='https:')) throw new Error('HTTPS_REQUIRED')
  let receipt=null
  try {
    const r=await fetcher(env.COVERAGE_URL,{signal:AbortSignal.timeout(20000)})
    if(r.ok) {
      const body=await r.text()
      if(body.length<=4000000) receipt=JSON.parse(body)
    }
  }catch{ /* An unavailable site is an alert, never implicit health. */ }
  const status=inspect(receipt,{contractSha256:env.EXPECTED_CONTRACT_SHA256,supplierCount:Number(env.EXPECTED_SUPPLIERS),requiredTasks:Number(env.EXPECTED_REQUIRED_TASKS),overdueHours:30},now)
  let expectedRelease=null,live=null
  try {
    const responses=await Promise.all([env.RELEASE_EXPECTATION_URL,env.LIVE_RECEIPT_URL].map(url=>fetcher(url,{signal:AbortSignal.timeout(20000)})))
    const values=await Promise.all(responses.map(async r=>{
      if(!r.ok) return null
      const body=await r.text()
      return body.length<=100000?JSON.parse(body):null
    }))
    expectedRelease=values[0]
    live=values[1]
  }catch{ /* Publication failure is distinct from successful collection. */ }
  if(!inspectDeployment(expectedRelease,live)) status.reasons.push('PRODUCTION_RELEASE_NOT_ACKNOWLEDGED')
  status.healthy=status.reasons.length===0
  const key='watchdog/last-alert.json'
  const priorObject=await env.ALERT_STATE.get(key)
  const prior=priorObject?await priorObject.json():null
  const signature=JSON.stringify(status.reasons)
  const due=!prior||prior.signature!==signature||(!status.healthy&&now-prior.notifiedAt>=24*3600000)
  if(due) {
    const text=status.healthy?'Security Market Pulse recovered: all required daily checks are current.':`Security Market Pulse needs attention: ${status.reasons.join(', ')}. Last observed run: ${status.runId||'none'}.`
    const r=await fetcher(env.ALERT_WEBHOOK,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({text}),signal:AbortSignal.timeout(20000)})
    if(!r.ok) throw new Error('ALERT_DELIVERY_FAILED')
    await env.ALERT_STATE.put(key,JSON.stringify({signature,notifiedAt:now,healthy:status.healthy}))
  }
  return status
}
export default {async scheduled(_event,env,ctx){ctx.waitUntil(check(env))}}
