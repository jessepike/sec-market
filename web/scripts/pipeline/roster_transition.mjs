// Additive roster transition (D-138, SEC-083). Mirrors web/scripts/pipeline/roster_transition.py.
// A snapshot produced under the base contract J stays valid after J's reviewed
// additive successor lands, because removing the declared additions from the
// current contract must give back J byte for byte.
import { existsSync, readFileSync } from 'node:fs'
import { createHash } from 'node:crypto'
import { resolve } from 'node:path'

const canonical = x => Array.isArray(x) ? '[' + x.map(canonical).join(',') + ']' : x && typeof x === 'object' ? '{' + Object.keys(x).sort().map(k => JSON.stringify(k) + ':' + canonical(x[k])).join(',') + '}' : JSON.stringify(x)
const hash = x => createHash('sha256').update(canonical(x)).digest('hex')
const demand = (condition, message) => { if (!condition) throw new Error(message) }

export function invertRoster(contract, transition) {
  const suppliers = new Set(transition.addedSuppliers), sources = new Set(transition.addedSources)
  const appended = transition.appendedSourceIds
  const base = JSON.parse(JSON.stringify(contract))
  demand([...suppliers].every(id => contract.suppliers.some(s => s.id === id)) &&
    [...sources].every(id => contract.sources.some(s => s.id === id)), 'ROSTER_TRANSITION_ADDITION_MISSING')
  base.suppliers = base.suppliers.filter(s => !suppliers.has(s.id))
  base.sources = base.sources.filter(s => !sources.has(s.id))
  for (const supplier of base.suppliers) {
    const ids = appended[supplier.id]
    if (!ids) continue
    demand(ids.every(id => sources.has(id)) && canonical(supplier.sourceIds.slice(-ids.length)) === canonical(ids), 'ROSTER_TRANSITION_APPEND_ORDER_DIFFERS')
    supplier.sourceIds = supplier.sourceIds.slice(0, -ids.length)
  }
  return base
}

/** The base contract when `current` is the declared successor of `wanted`, else null. */
export function rosterBaseFor(web, current, wanted) {
  const path = resolve(web, '../contracts/roster-transition.json')
  if (!existsSync(path)) return null
  const transition = JSON.parse(readFileSync(path, 'utf8'))
  if (transition.kind !== 'additive_roster_transition' || transition.baseContractSha256 !== wanted ||
    transition.activatedContractSha256 !== hash(current)) return null
  const base = invertRoster(current, transition)
  demand(hash(base) === wanted, 'ROSTER_TRANSITION_INVERSE_DIFFERS')
  return base
}

/** The J base of the repository's current contract (J itself when no successor is declared). */
export function repoBaseContract(web) {
  const current = JSON.parse(readFileSync(resolve(web, '../contracts/market.json'), 'utf8'))
  const path = resolve(web, '../contracts/roster-transition.json')
  if (!existsSync(path)) return current
  const transition = JSON.parse(readFileSync(path, 'utf8'))
  return hash(current) === transition.baseContractSha256 ? current : (rosterBaseFor(web, current, transition.baseContractSha256) ?? current)
}
