import { authorized, config, dispatch } from '../lib/core.js'

// Daily outside clock: starts the collector workflow with timer=true.
export async function GET(request) {
  const cfg = config(process.env)
  if (!authorized(request, cfg.CRON_SECRET)) return new Response('unauthorized', { status: 401 })
  const result = await dispatch(cfg)
  // A failed dispatch returns 502 so it shows in Vercel's cron logs; the
  // GitHub backup schedule and the watchdog still cover the day.
  return Response.json(result, { status: result.ok ? 200 : 502 })
}
