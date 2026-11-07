import { authorized, client, config, githubToken } from '../lib/core.js'
import { finishGate } from '../lib/health.js'

// Every 10 minutes. GitHub does not start the publisher's workflow_run callback
// for a gate the workflow token dispatched (seen 2026-11-07), so this is how a
// split release finishes. Two read calls when there is nothing to do.
export async function GET(request) {
  const cfg = config(process.env)
  if (!authorized(request, cfg.CRON_SECRET)) return new Response('unauthorized', { status: 401 })
  const gh = client(await githubToken(cfg), fetch)
  return Response.json(await finishGate(cfg, gh))
}
