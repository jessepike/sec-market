import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { activityItems } from '../src/data/activity.ts'
import { evidenceById, evidenceRecords } from '../src/data/evidence.ts'
import { securityDomains, trackedPrintEvidenceIds } from '../src/data/domains.ts'
import { hypotheses } from '../src/data/hypotheses.ts'
import { issueEvidenceIds } from '../src/data/issueHelpers.ts'
import { issues } from '../src/data/issues/index.ts'
import { contextStats, chartEvidenceIds, marketCall } from '../src/data/market.ts'
import { allPressureRows } from '../src/data/platformPressure.ts'
import { printGroups, vendorPrints } from '../src/data/prints.ts'
import { retainedTrackerEvents } from '../src/data/tracker/events.ts'
import { trackerSuppliers, manualTrackerSuppliers } from '../src/data/tracker/suppliers.ts'
import type { Provenance } from '../src/data/types.ts'
import { weekMoves } from '../src/data/whatMoved.ts'
import { PrintGrid } from '../src/components/PrintGrid.tsx'
import { EvidenceProvider } from '../src/context/EvidenceProvider.tsx'

const MAX_UNREFERENCED = 5

function fail(message: string): never {
  console.error('Integrity check FAILED:', message)
  process.exit(1)
}

function idsFromProvenance(provenance: Provenance): string[] {
  return [...provenance.evidenceIds]
}

function assertNoDuplicates(label: string, ids: string[]): void {
  const seen = new Set<string>()
  for (const id of ids) {
    if (seen.has(id)) {
      fail(`${label} has duplicate evidence id "${id}"`)
    }
    seen.add(id)
  }
}

function collectDuplicateCheckArrays(): Array<{ label: string; ids: string[] }> {
  const arrays: Array<{ label: string; ids: string[] }> = []

  for (const item of weekMoves.tracked) {
    arrays.push({ label: `weekMoves.tracked ${item.kind}`, ids: item.evidenceIds })
  }
  for (const item of weekMoves.judged) {
    arrays.push({ label: `weekMoves.judged ${item.kind}`, ids: item.evidenceIds })
  }
  for (const domain of securityDomains) {
    arrays.push({ label: `${domain.id} supportingEvidenceIds`, ids: domain.supportingEvidenceIds })
    arrays.push({ label: `${domain.id} counterEvidenceIds`, ids: domain.counterEvidenceIds })
  }
  for (const row of allPressureRows()) {
    arrays.push({ label: `${row.id} provenance.print`, ids: idsFromProvenance(row.provenance.print) })
    arrays.push({ label: `${row.id} provenance.read`, ids: idsFromProvenance(row.provenance.read) })
  }
  for (const hypothesis of hypotheses) {
    arrays.push({ label: `${hypothesis.id} evidenceIds`, ids: hypothesis.evidenceIds })
    arrays.push({
      label: `${hypothesis.id} provenance.evidenceIds`,
      ids: hypothesis.provenance.evidenceIds,
    })
  }

  return arrays
}

function collectAllReferencedIds(): Set<string> {
  const ids = new Set<string>()

  const add = (value: string | string[] | undefined) => {
    if (!value) return
    for (const id of Array.isArray(value) ? value : [value]) {
      ids.add(id)
    }
  }

  for (const item of weekMoves.tracked) add(item.evidenceIds)
  for (const item of weekMoves.judged) add(item.evidenceIds)
  for (const domain of securityDomains) {
    add(domain.supportingEvidenceIds)
    add(domain.counterEvidenceIds)
  }
  for (const row of allPressureRows()) {
    add(idsFromProvenance(row.provenance.print))
    add(idsFromProvenance(row.provenance.read))
  }
  for (const hypothesis of hypotheses) {
    add(hypothesis.evidenceIds)
    add(hypothesis.provenance.evidenceIds)
  }
  for (const item of activityItems) add(item.evidenceIds)
  for (const print of vendorPrints) add(print.evidenceIds)
  add(marketCall.evidenceIds)
  add(chartEvidenceIds)
  for (const stat of contextStats) add(stat.evidenceIds)
  for (const record of evidenceRecords) add(record.conflictingEvidenceIds)
  for (const issue of issues) add(issueEvidenceIds(issue))

  // Tracker data (step 5, docs/archive/2026-10-refresh-gate/autonomy-coverage-plan.md §4) — the
  // supplier tracker cites evidence.ts records the same way the rest of the
  // site does, so those citations count here too.
  // Manual claims remain the actual fallback when an SEC source check fails.
  // Their references are retained dependencies, not orphan evidence.
  for (const supplier of [...trackerSuppliers, ...manualTrackerSuppliers]) {
    add(supplier.headlineMetric?.evidenceIds)
    add(supplier.revenue?.latest.evidenceIds)
    add(supplier.revenue?.prior?.evidenceIds)
    add(supplier.lastRound?.evidenceIds)
    add(supplier.ownership?.evidenceIds)
  }
  for (const event of retainedTrackerEvents) add(event.evidenceIds)

  return ids
}

// 1. Print lines resolve for every domain.
for (const domain of securityDomains) {
  try {
    const ids = trackedPrintEvidenceIds(domain)
    if (ids.length === 0) {
      fail(`Domain "${domain.id}" print resolves to an empty evidence list`)
    }
  } catch (error) {
    const detail = error instanceof Error ? error.message : String(error)
    fail(`Domain "${domain.id}" print line failed: ${detail}`)
  }
}

// 2. Every judged claim has a warrant.
for (const item of weekMoves.judged) {
  const hasEvidence = item.evidenceIds.length > 0
  const hasBasis = Boolean(item.basisHref?.trim())
  if (!hasEvidence && !hasBasis) {
    fail(`Judged row "${item.kind}" has neither evidenceIds nor basisHref`)
  }
}

// 3. No duplicate evidence ids in scoped arrays.
for (const { label, ids } of collectDuplicateCheckArrays()) {
  assertNoDuplicates(label, ids)
}

// 4. Every referenced evidence id exists.
const referenced = collectAllReferencedIds()
const missing = [...referenced].filter((id) => !evidenceById[id])
if (missing.length > 0) {
  fail(`Unresolved evidence ids: ${missing.sort().join(', ')}`)
}

// 5. Unreferenced evidence records are reported; fail only above threshold.
const unreferenced = evidenceRecords.filter((record) => !referenced.has(record.id))
if (unreferenced.length > 0) {
  console.log(`Unreferenced evidence records (${unreferenced.length}):`)
  for (const record of unreferenced) {
    console.log(`  ${record.id} - ${record.title}`)
  }
}
if (unreferenced.length > MAX_UNREFERENCED) {
  fail(
    `${unreferenced.length} unreferenced evidence records exceeds the allowed ${MAX_UNREFERENCED}`,
  )
}

// 6. A print's secondaryGroup, when present, must name a real domain.
for (const print of vendorPrints) {
  if (print.secondaryGroup === undefined) continue
  if (!(printGroups as readonly string[]).includes(print.secondaryGroup)) {
    fail(
      `Print "${print.id}" has secondaryGroup "${print.secondaryGroup}" which is not a member of printGroups`,
    )
  }
}

// 7. A print's secondaryGroup must differ from its primary group — a print
// cannot borrow into the domain it already belongs to.
for (const print of vendorPrints) {
  if (print.secondaryGroup !== undefined && print.secondaryGroup === print.group) {
    fail(
      `Print "${print.id}" has secondaryGroup equal to its primary group "${print.group}" — that is not a second domain`,
    )
  }
}

// 8. Every print carrying a secondaryGroup must render, in the secondary
// group's section, a visible label naming its primary group. This is the
// check that keeps a borrowed card from silently reading like an extra,
// undifferentiated print in the group it was borrowed into. The same
// server render is reused below (8b) to check each group header's stated
// count against what the render actually shows.
const markup = renderToStaticMarkup(createElement(EvidenceProvider, null, createElement(PrintGrid)))

const borrowedPrints = vendorPrints.filter((print) => print.secondaryGroup !== undefined)
for (const print of borrowedPrints) {
  const label = `also counted under ${print.group}`
  if (!markup.includes(label)) {
    fail(
      `Print "${print.id}" carries secondaryGroup "${print.secondaryGroup}" but the rendered ` +
        `output does not contain the primary-group label "${label}"`,
    )
  }
}

// 8b. Every print-group header's stated "covered" count must equal the
// number of print-card articles actually rendered inside that group. A
// header reading "0 prints" shipped above a group displaying a real
// comparable print, and every gate passed — this parses the header back out
// of the server-rendered markup and checks it against the actual cards
// rather than trusting the component's own arithmetic.
const groupBlocks = [...markup.matchAll(/<details class="print-group">([\s\S]*?)<\/details>/g)]
if (groupBlocks.length === 0) {
  fail('No print-group sections found in the rendered PrintGrid markup')
}
for (const match of groupBlocks) {
  const block = match[1]
  const titleMatch = block.match(/<span class="grouphdr__title">([^<]*)<\/span>/)
  const groupName = titleMatch?.[1] ?? '(unknown group)'
  const countMatch = block.match(/(\d+) covered/)
  if (!countMatch) {
    fail(`Print-group "${groupName}" header is missing a "covered" count`)
  }
  const statedCount = Number(countMatch[1])
  const renderedCount = (
    block.match(/<article class="print-card(?: print-card--coverage)?">/g) ?? []
  ).length
  if (statedCount !== renderedCount) {
    fail(
      `Print-group "${groupName}" header states ${statedCount} covered but ${renderedCount} ` +
        `print-card articles are actually rendered in that group`,
    )
  }
}

console.log('Integrity check passed')
