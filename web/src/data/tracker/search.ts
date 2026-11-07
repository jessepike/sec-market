import { suppliers as registeredSuppliers } from '../../../../contracts/market.json'
import type { TrackerSupplier } from './suppliers'

const aliasesById = new Map(registeredSuppliers.map(supplier => [supplier.id, supplier.aliases]))

/** Search identifiers only. A matching company does not establish freshness or coverage. */
function normalize(value: string): string {
  return value.normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLowerCase()
    .replace(/[^a-z0-9]+/g, ' ').trim()
}

export function searchCompanies(suppliers: readonly TrackerSupplier[], query: string): TrackerSupplier[] {
  const terms = normalize(query).split(' ').filter(Boolean)
  if (terms.length === 0) return []
  return suppliers.filter(supplier => [supplier.name, supplier.ticker ?? '', ...(aliasesById.get(supplier.id) ?? [])]
    .some(identifier => {
      const normalized = normalize(identifier)
      return terms.every(term => normalized.includes(term))
    }))
    .sort((a, b) => rank(a, terms[0]) - rank(b, terms[0]) || a.name.localeCompare(b.name))
}

/** Whole companies before their segments; a name that starts with the query before one that contains it. */
function rank(supplier: TrackerSupplier, first: string): number {
  const starts = normalize(supplier.name).startsWith(first) || normalize(supplier.ticker ?? '') === first
  return (supplier.kind === 'segment' ? 2 : 0) + (starts ? 0 : 1)
}
