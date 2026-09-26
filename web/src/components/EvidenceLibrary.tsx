import { useMemo, useState } from 'react'
import { Search } from 'lucide-react'
import { evidenceRecords } from '../data/evidence'
import type { SourceClass } from '../data/types'
import { useEvidence } from '../context/useEvidence'

/**
 * AUTO-001 fix pass (2026-09-26), item 4: `evidence.ts` holds both the
 * tracker's own facts-only evidence (`TR-` ids, empty `interpretation` by
 * construction) and the older, judged thesis-era evidence this facts-only
 * front page no longer states a stance from (ids like `C3`, whose
 * `interpretation` reads "strongest realized network-security acceleration
 * in the panel"). This library is reachable from the live front page only
 * (`App.tsx`'s FrontPage, inside `#research`) — `/thesis/` and
 * `/issues/<id>/` do not render it — so it now searches the tracker's own
 * evidence exclusively. The full library (including the judged records) is
 * still reachable per source, unfiltered, from the archived pages that cite
 * them directly.
 */
const trackerEvidenceRecords = evidenceRecords.filter((record) => record.id.startsWith('TR-'))

const PRESENT_CLASSES: SourceClass[] = [
  ...new Set(trackerEvidenceRecords.map((record) => record.sourceClass)),
].sort()

export function EvidenceLibrary() {
  const { openEvidence } = useEvidence()
  const [query, setQuery] = useState('')
  const [classFilter, setClassFilter] = useState<SourceClass | 'ALL'>('ALL')

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase()
    return trackerEvidenceRecords.filter((record) => {
      if (classFilter !== 'ALL' && record.sourceClass !== classFilter) return false
      if (!q) return true
      const haystack = [record.id, record.title, record.organization, record.excerpt, ...record.tags]
        .join(' ')
        .toLowerCase()
      return haystack.includes(q)
    })
  }, [query, classFilter])

  return (
    <section className="evidence-library" aria-labelledby="research-heading">
      <div className="section-heading">
        <h2 id="research-heading">Research &amp; evidence library</h2>
        <p>Search the tracker&rsquo;s sourced evidence. Click any row to inspect full attribution.</p>
      </div>
      <div className="evidence-library__controls">
        <label className="search-field">
          <Search size={18} aria-hidden="true" />
          <span className="visually-hidden">Search evidence</span>
          <input
            type="search"
            placeholder="Search by title, organization, excerpt, or tag…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </label>
        <label className="filter-field">
          <span className="filter-field__label">Source class</span>
          <select
            value={classFilter}
            onChange={(e) => setClassFilter(e.target.value as SourceClass | 'ALL')}
          >
            <option value="ALL">All classes</option>
            {PRESENT_CLASSES.map((cls) => (
              <option key={cls} value={cls}>
                {cls}
              </option>
            ))}
          </select>
        </label>
      </div>
      <p className="evidence-library__count" aria-live="polite">
        {filtered.length} source{filtered.length === 1 ? '' : 's'}
      </p>
      <ul className="evidence-library__list">
        {filtered.map((record) => (
          <li key={record.id}>
            <button
              type="button"
              className="evidence-library__item"
              onClick={() => openEvidence(record.id)}
            >
              <span className="evidence-library__title">{record.title}</span>
              <span className="evidence-library__org">{record.organization}</span>
              <span className="evidence-library__class">{record.sourceClass}</span>
              <span className="evidence-library__date">{record.publicationDate}</span>
            </button>
          </li>
        ))}
      </ul>
    </section>
  )
}
