import { useEffect, useId, useRef } from 'react'
import { ArrowLeft, ExternalLink, X } from 'lucide-react'
import { evidenceById } from '../data/evidence'
import { useEvidence } from '../context/useEvidence'

export function EvidenceDrawer() {
  const { isOpen, selectedIds, canGoBack, closeEvidence, openConflictingEvidence, goBack } =
    useEvidence()
  const titleId = useId()
  const closeRef = useRef<HTMLButtonElement>(null)
  const panelRef = useRef<HTMLElement>(null)

  const records = selectedIds.map((id) => evidenceById[id]).filter(Boolean)

  useEffect(() => {
    if (!isOpen) return

    const previousFocus = document.activeElement as HTMLElement | null
    closeRef.current?.focus()

    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        closeEvidence()
        return
      }
      if (event.key === 'Tab' && panelRef.current) {
        const focusable = panelRef.current.querySelectorAll<HTMLElement>(
          'a[href], button:not([disabled]), textarea, input, select, [tabindex]:not([tabindex="-1"])',
        )
        if (focusable.length === 0) return
        const first = focusable[0]
        const last = focusable[focusable.length - 1]
        if (event.shiftKey && document.activeElement === first) {
          event.preventDefault()
          last.focus()
        } else if (!event.shiftKey && document.activeElement === last) {
          event.preventDefault()
          first.focus()
        }
      }
    }

    document.addEventListener('keydown', onKeyDown)
    document.body.style.overflow = 'hidden'

    return () => {
      document.removeEventListener('keydown', onKeyDown)
      document.body.style.overflow = ''
      previousFocus?.focus()
    }
  }, [isOpen, closeEvidence])

  if (!isOpen || records.length === 0) return null

  return (
    <div className="evidence-drawer-backdrop" onClick={closeEvidence} role="presentation">
      <aside
        ref={panelRef}
        className="evidence-drawer"
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        onClick={(e) => e.stopPropagation()}
      >
        <header className="evidence-drawer__header">
          <div className="evidence-drawer__header-start">
            {canGoBack && (
              <button
                type="button"
                className="evidence-drawer__back"
                onClick={goBack}
                aria-label="Back to previous evidence"
              >
                <ArrowLeft size={18} aria-hidden="true" />
                Back
              </button>
            )}
            <h2 id={titleId}>Evidence</h2>
          </div>
          <button
            ref={closeRef}
            type="button"
            className="evidence-drawer__close"
            onClick={closeEvidence}
            aria-label="Close evidence panel"
          >
            <X size={20} />
          </button>
        </header>
        <div className="evidence-drawer__body">
          {records.map((record) => {
            const conflicting = record.conflictingEvidenceIds
              .map((id) => evidenceById[id])
              .filter(Boolean)

            return (
              <article key={record.id} className="evidence-record">
                <h3>{record.title}</h3>
                <p className="evidence-record__org">{record.organization}</p>
                <dl className="evidence-record__grid">
                  {record.sourceAttributions ? (
                    <div className="evidence-record__sources">
                      <dt>Source dates</dt>
                      <dd>
                        <ul className="source-attribution-list">
                          {record.sourceAttributions.map((source) => (
                            <li key={source.organization}>
                              <strong>{source.organization}</strong>
                              {' — '}
                              <time dateTime={source.publicationDate}>{source.publicationDate}</time>
                              {source.economicPeriod ? ` (${source.economicPeriod})` : ''}
                              {source.canonicalUrl && (
                                <>
                                  {' '}
                                  <a
                                    href={source.canonicalUrl}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                  >
                                    Source
                                    <ExternalLink size={11} aria-hidden="true" />
                                  </a>
                                </>
                              )}
                            </li>
                          ))}
                        </ul>
                      </dd>
                    </div>
                  ) : (
                    <>
                      <div>
                        <dt>Publication date</dt>
                        <dd>
                          <time dateTime={record.publicationDate}>{record.publicationDate}</time>
                        </dd>
                      </div>
                      <div>
                        <dt>Economic period</dt>
                        <dd>{record.economicPeriod}</dd>
                      </div>
                    </>
                  )}
                  <div>
                    <dt>Source class</dt>
                    <dd>{record.sourceClass}</dd>
                  </div>
                  <div>
                    <dt>Packet label</dt>
                    <dd>{record.artifactLabel}</dd>
                  </div>
                </dl>
                {record.canonicalUrl && !record.sourceAttributions ? (
                  <p className="evidence-record__url">
                    <a href={record.canonicalUrl} target="_blank" rel="noopener noreferrer">
                      Canonical source
                      <ExternalLink size={14} aria-hidden="true" />
                    </a>
                  </p>
                ) : !record.sourceAttributions && !record.canonicalUrl ? (
                  <p className="evidence-record__url evidence-record__url--missing">
                    Canonical URL unavailable for this internal disposition record.
                  </p>
                ) : null}
                <div className="evidence-record__section">
                  <h4>Excerpt / locator</h4>
                  <blockquote>{record.excerpt}</blockquote>
                </div>
                <div className="evidence-record__section">
                  <h4>Interpretation</h4>
                  <p>{record.interpretation}</p>
                </div>
                <div className="evidence-record__section">
                  <h4>Limitations / confounds</h4>
                  <p>{record.limitations}</p>
                </div>
                {conflicting.length > 0 && (
                  <div className="evidence-record__section evidence-record__section--conflict">
                    <h4>Conflicting evidence</h4>
                    <ul className="conflict-list">
                      {conflicting.map((item) => (
                        <li key={item.id}>
                          <button
                            type="button"
                            className="conflict-link"
                            onClick={() => openConflictingEvidence(item.id)}
                          >
                            <strong>{item.organization}</strong> — {item.title}
                          </button>
                          <p>{item.interpretation}</p>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </article>
            )
          })}
        </div>
      </aside>
    </div>
  )
}
