import { useMemo, useState } from 'react'
import { Search } from 'lucide-react'
import { evidenceRecords } from '../data/evidence'
import type { SourceClass } from '../data/types'
import { useEvidence } from '../context/useEvidence'

const ALL_CLASSES: SourceClass[] = [
  'FILING',
  'IR',
  'TRANSCRIPT',
  'OFFICIAL',
  'INDEPENDENT',
  'OWN_ANALYSIS',
  'VENDOR-SURVEY',
  'VENDOR-RESEARCH',
]

export function EvidenceLibrary() {
  const { openEvidence } = useEvidence()
  const [query, setQuery] = useState('')
  const [classFilter, setClassFilter] = useState<SourceClass | 'ALL'>('ALL')

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase()
    return evidenceRecords.filter((record) => {
      if (classFilter !== 'ALL' && record.sourceClass !== classFilter) return false
      if (!q) return true
      const haystack = [
        record.id,
        record.title,
        record.organization,
        record.excerpt,
        record.interpretation,
        ...record.tags,
      ]
        .join(' ')
        .toLowerCase()
      return haystack.includes(q)
    })
  }, [query, classFilter])

  return (
    <section className="evidence-library" aria-labelledby="research-heading">
      <div className="section-heading">
        <h2 id="research-heading">Research &amp; evidence library</h2>
        <p>
          Search the Episode 002 packet and the August 2026 surface refresh. Click any row to
          inspect full attribution.
        </p>
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
            {ALL_CLASSES.map((cls) => (
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
