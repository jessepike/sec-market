import edgarFacts from '../data/generated/edgarFacts.json'
import { LAST_UPDATED_ISO } from '../data/meta'
import { edgarFilingsInLast30Days, eventsInLast30Days, formatShortDate, shortSupplierName } from '../data/tracker/derive'
import { trackerSuppliers } from '../data/tracker/suppliers'
import { EvidenceLink } from './EvidenceLink'

type ChangeRow =
  | { kind: 'event'; date: string; text: string; evidenceIds: string[]; sortKey: string }
  | { kind: 'filing'; date: string; text: string; sourceUrl: string; sortKey: string }

function supplierName(supplierId: string): string {
  const name = trackerSuppliers.find((supplier) => supplier.id === supplierId)?.name ?? supplierId
  return shortSupplierName(name)
}

function buildRows(): ChangeRow[] {
  const events = eventsInLast30Days(LAST_UPDATED_ISO).map((event) => ({
    kind: 'event' as const,
    date: event.date,
    text: `${supplierName(event.supplierId)} — ${event.text}`,
    evidenceIds: event.evidenceIds,
    sortKey: `${event.date}-${event.id}`,
  }))
  const filings = edgarFilingsInLast30Days(LAST_UPDATED_ISO, edgarFacts).map((filing) => ({
    kind: 'filing' as const,
    date: filing.filedDate,
    text: `${supplierName(filing.supplierId)} filed its ${filing.form} for the quarter ended ${filing.periodEnd}.`,
    sourceUrl: filing.sourceUrl,
    sortKey: `${filing.filedDate}-${filing.supplierId}-${filing.periodEnd}`,
  }))
  return [...events, ...filings].sort((a, b) => (a.sortKey < b.sortKey ? 1 : a.sortKey > b.sortKey ? -1 : 0))
}

/**
 * "What changed in the last 30 days" — autonomy-coverage-plan.md §3b. Merges
 * data/tracker/events.ts with any EDGAR quarter filed in the trailing 30
 * days (generated/edgarFacts.json), newest first. One factual line each,
 * every line linked to its source.
 *
 * Density pass (coordinator instruction, after the initial step 5 build):
 * a short supplier name, a mono date, and a compact "src" evidence link
 * instead of a name-carrying button — the full legal name stays in
 * evidence.ts and in each supplier's own row on "The market by domain".
 */
export function WhatChangedTracker() {
  const rows = buildRows()

  return (
    <section id="tracker-changed" className="tracker-changed" aria-labelledby="tracker-changed-heading">
      <div className="section-heading">
        <h2 id="tracker-changed-heading">What changed in the last 30 days</h2>
      </div>
      {rows.length === 0 ? (
        <p>No tracked change in the last 30 days.</p>
      ) : (
        <ul className="tracker-changed__list">
          {rows.map((row) => (
            <li key={row.sortKey} className="tracker-changed__row">
              <time dateTime={row.date} className="tracker-changed__date">
                {formatShortDate(row.date)}
              </time>
              <span className="tracker-changed__text">{row.text}</span>
              {row.kind === 'event' ? (
                <EvidenceLink ids={row.evidenceIds} variant="compact" context={row.text} />
              ) : (
                <a
                  className="evidence-link evidence-link--compact"
                  href={row.sourceUrl}
                  target="_blank"
                  rel="noreferrer"
                  aria-label={`Source: ${row.text}`}
                >
                  src
                </a>
              )}
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
