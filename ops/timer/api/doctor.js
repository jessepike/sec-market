import { authorized, client, config, githubToken } from '../lib/core.js'
import { doctor } from '../lib/doctor.js'

// Every 10 minutes. Sorts the day into one known case and takes at most one
// bounded step per case (lib/doctor.js). Set DOCTOR_DRY_RUN=true to only report.
export async function GET(request) {
  const cfg = config(process.env)
  if (!authorized(request, cfg.CRON_SECRET)) return new Response('unauthorized', { status: 401 })
  const gh = client(await githubToken(cfg), fetch)
  const result = await doctor(cfg, gh)
  return Response.json(result, { status: result.escalate.length ? 503 : 200 })
}
