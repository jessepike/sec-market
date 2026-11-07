import { issues } from './issues/index'
import type { Issue } from './types'
import { trackerSuppliers } from './tracker/suppliers'
import { companySlug } from './tracker/slugs'

export type RouteKind = 'front' | 'archive' | 'corrections' | 'issue' | 'thesis' | 'coverage' | 'data' | 'funding' | 'market' | 'method' | 'company'

export interface RouteEntry {
  /** Always starts and ends with "/", e.g. "/", "/issues/", "/issues/2026-w36/". */
  path: string
  kind: RouteKind
  issueId?: string
  supplierId?: string
}

/**
 * Every prerendered HTML route for a given issues array — the front page,
 * the archive, and one permalink per issue. Parameterised so a test fixture
 * (a small hand-built issues array, e.g. tests/dist-fixtures.test.ts) can
 * compute the same route table a real build would, without importing the
 * real src/data/issues data.
 */
export function routesFor(issuesList: Issue[], supplierIds: readonly string[] = []): RouteEntry[] {
  return [
    { path: '/', kind: 'front' },
    { path: '/issues/', kind: 'archive' },
    { path: '/corrections/', kind: 'corrections' },
    { path: '/thesis/', kind: 'thesis' },
    { path: '/coverage/', kind: 'coverage' },
    { path: '/data/', kind: 'data' },
    { path: '/funding/', kind: 'funding' },
    { path: '/market/', kind: 'market' },
    { path: '/method/', kind: 'method' },
    ...issuesList.map((issue) => ({ path: `/issues/${issue.id}/`, kind: 'issue' as const, issueId: issue.id })),
    // D-139: one page per tracked supplier.
    ...supplierIds.map((id) => ({ path: `/companies/${companySlug(id)}/`, kind: 'company' as const, supplierId: id })),
  ]
}

/**
 * Every prerendered HTML route, derived from the issues array so the route
 * table can never drift from what issues actually exist. Shared by
 * src/App.tsx (client/server render switch), scripts/prerender.ts,
 * scripts/generate-seo.ts, scripts/generate-feed.ts and scripts/verify-dist.ts.
 */
export const routes: RouteEntry[] = routesFor(issues, trackerSuppliers.map((s) => s.id))

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
