/**
 * Agent access files (D-139). Called from generate-feed.ts after
 * dist/tracker.json is written. Writes, beside the HTML site:
 *   dist/llms.txt, dist/index.md, dist/data/index.md,
 *   dist/tracker.csv, dist/events.json, dist/events.csv.
 * Every value comes from the builders in src/data/agentExport.ts, which read
 * the same data the page renders. verify-dist.ts checks each file.
 */
import { mkdirSync, writeFileSync } from 'node:fs'
import { resolve } from 'node:path'
import {
  dataPageMarkdown,
  eventsCsv,
  eventsJsonPayload,
  llmsTxt,
  trackerCsv,
  trackerJsonPayload,
  trackerMarkdown,
} from '../src/data/agentExport.ts'
import type { EvidenceRecord } from '../src/data/types.ts'
import type { RunStatus } from '../src/data/runStatus.ts'
import type { TrackerDomain } from '../src/data/tracker/domains.ts'
import type { TrackerEvent } from '../src/data/tracker/events.ts'
import type { TrackerSupplier } from '../src/data/tracker/suppliers.ts'

export const AGENT_FILES = ['llms.txt', 'index.md', 'data/index.md', 'tracker.csv', 'events.json', 'events.csv'] as const

export function writeAgentFiles(
  suppliers: TrackerSupplier[],
  domains: TrackerDomain[],
  events: readonly TrackerEvent[],
  evidence: Record<string, EvidenceRecord>,
  status: RunStatus,
  isCertifiedEvent: (event: TrackerEvent) => boolean,
  distDir: string,
): string[] {
  const tracker = trackerJsonPayload(suppliers, domains, evidence, status)
  const eventsPayload = eventsJsonPayload(events, suppliers, evidence, status, isCertifiedEvent)
  mkdirSync(resolve(distDir, 'data'), { recursive: true })
  const files: Record<(typeof AGENT_FILES)[number], string> = {
    'llms.txt': llmsTxt(tracker, eventsPayload.events.length),
    'index.md': trackerMarkdown(tracker, eventsPayload),
    'data/index.md': dataPageMarkdown(tracker),
    'tracker.csv': trackerCsv(tracker),
    'events.json': JSON.stringify(eventsPayload, null, 2) + '\n',
    'events.csv': eventsCsv(eventsPayload),
  }
  for (const [name, body] of Object.entries(files)) writeFileSync(resolve(distDir, name), body, 'utf8')
  return Object.keys(files)
}
