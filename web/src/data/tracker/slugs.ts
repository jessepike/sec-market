/**
 * Readable URL slugs for per-company pages (D-139): the short display name,
 * lower-cased, e.g. "CrowdStrike Holdings, Inc." -> "crowdstrike". Falls back
 * to the supplier id if two suppliers would share a slug, so a URL never
 * points at the wrong company. Depends only on names.ts and suppliers.ts.
 */
import { shortSupplierName } from './names'
import { trackerSuppliers } from './suppliers'

function slugify(text: string): string {
  return text
    .normalize('NFKD')
    .replace(/[̀-ͯ]/g, '')
    .toLowerCase()
    .replace(/&/g, ' and ')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
}

function buildSlugs(): Map<string, string> {
  const counts = new Map<string, number>()
  const base = trackerSuppliers.map((s) => [s.id, slugify(shortSupplierName(s.name)) || s.id] as const)
  for (const [, slug] of base) counts.set(slug, (counts.get(slug) ?? 0) + 1)
  return new Map(base.map(([id, slug]) => [id, counts.get(slug) === 1 ? slug : id]))
}

const slugById = buildSlugs()

export function companySlug(id: string): string {
  return slugById.get(id) ?? id
}
