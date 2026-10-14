import { writeFileSync } from 'node:fs'
import { trackerSuppliers } from '../src/data/tracker/suppliers'
import { trackerEvents } from '../src/data/tracker/events'
import { evidenceById } from '../src/data/evidence'

const ids = new Set(trackerSuppliers.flatMap(s => [...(s.revenue?.latest.evidenceIds ?? []), ...(s.revenue?.prior?.evidenceIds ?? []), ...(s.headlineMetric?.evidenceIds ?? []), ...(s.lastRound?.evidenceIds ?? []), ...(s.ownership?.evidenceIds ?? [])]))
trackerEvents.forEach(e => e.evidenceIds.forEach(id => ids.add(id)))
writeFileSync(process.argv[2] ?? '../.collect/live-inventory.json', JSON.stringify({ suppliers: trackerSuppliers, events: trackerEvents, sources: Object.fromEntries([...ids].map(id => [id, evidenceById[id]])) }, null, 2) + '\n')
