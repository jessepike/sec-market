import { authorized, config, watch } from '../lib/core.js'

// Independent of GitHub Actions. Every six hours it checks that the published
// data is fresh, the latest daily collector run succeeded, and the ChatGPT
// login still works. Any problem opens one issue assigned to the owner
// (authored by the GitHub App, so GitHub notifies the owner by email/push).
export async function GET(request) {
  const cfg = config(process.env)
  if (!authorized(request, cfg.CRON_SECRET)) return new Response('unauthorized', { status: 401 })
  const result = await watch(cfg)
  return Response.json(result, { status: result.problems.length ? 503 : 200 })
}
