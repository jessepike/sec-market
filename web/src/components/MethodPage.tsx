import { EvidenceLibrary } from './EvidenceLibrary'
import { HowThisWorks } from './HowThisWorks'
import { MethodologyNote } from './MethodologyNote'
import { RunStatus } from './RunStatus'

/**
 * `/method/`, "How this works": the data status, how the tracker is built and the evidence
 * library, moved off the landing page by the UX and consistency review (2026-11-07).
 */
export function MethodPage() {
  return (
    <div className="method-page">
      <section className="method-page__head" aria-labelledby="method-page-heading">
        <h1 id="method-page-heading">How this works</h1>
        <p className="desk-note">What is checked and when, how the tracker is built, and every source it cites.</p>
      </section>
      <RunStatus />
      <div id="method" className="method-page__section"><HowThisWorks /></div>
      <details className="depth" id="research">
        <summary>Research &amp; evidence library</summary>
        <EvidenceLibrary />
      </details>
      <MethodologyNote />
    </div>
  )
}
