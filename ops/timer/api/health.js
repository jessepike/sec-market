import { authorized, client, config, githubToken } from '../lib/core.js'
import { health } from '../lib/health.js'

// Hourly. Rewrites the one "Site health: ..." issue with every check's state.
export async function GET(request) {
  const cfg = config(process.env)
  if (!authorized(request, cfg.CRON_SECRET)) return new Response('unauthorized', { status: 401 })
  const gh = client(await githubToken(cfg), fetch)
  const result = await health(cfg, gh)
  return Response.json(result, { status: result.checks.some(c => c.status === 'fail') ? 503 : 200 })
}
