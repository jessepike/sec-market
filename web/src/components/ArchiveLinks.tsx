/**
 * Links to the archive, evidence and method — autonomy-coverage-plan.md §3d.
 * The archive routes are dated records (issues, thesis); evidence and
 * method are same-page anchors into the existing depth sections.
 */
export function ArchiveLinks() {
  return (
    <section id="tracker-links" className="tracker-links" aria-label="Archive and reference">
      <p>
        <a href="/issues/">Issue archive</a> · <a href="/thesis/">Standing thesis</a> ·{' '}
        <a href="#research">Evidence</a> · <a href="#method">Method</a>
      </p>
    </section>
  )
}
