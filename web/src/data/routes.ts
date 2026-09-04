import { issues } from './issues/index'

export type RouteKind = 'front' | 'archive' | 'issue'

export interface RouteEntry {
  /** Always starts and ends with "/", e.g. "/", "/issues/", "/issues/2026-w36/". */
  path: string
  kind: RouteKind
  issueId?: string
}

/**
 * Every prerendered HTML route, derived from the issues array so the route
 * table can never drift from what issues actually exist. Shared by
 * src/App.tsx (client/server render switch), scripts/prerender.ts,
 * scripts/generate-seo.ts, scripts/generate-feed.ts and scripts/verify-dist.ts.
 */
export const routes: RouteEntry[] = [
  { path: '/', kind: 'front' },
  { path: '/issues/', kind: 'archive' },
  ...issues.map((issue) => ({ path: `/issues/${issue.id}/`, kind: 'issue' as const, issueId: issue.id })),
]

/** Normalises a pathname: drops a query string, ensures a single trailing slash. */
export function normalizePath(path: string): string {
  const withoutQuery = path.split('?')[0].split('#')[0]
  if (withoutQuery === '' || withoutQuery === '/') return '/'
  return withoutQuery.endsWith('/') ? withoutQuery : `${withoutQuery}/`
}

/** Resolves a pathname to its route entry. Unknown paths fall back to the front page. */
export function matchRoute(path: string): RouteEntry {
  const normalized = normalizePath(path)
  return routes.find((route) => route.path === normalized) ?? routes[0]
}
