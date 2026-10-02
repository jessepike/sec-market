import { MessageSquare } from 'lucide-react'
import { CONTACT_EMAIL } from '../data/meta'

function mailto(subject: string): string {
  return `mailto:${CONTACT_EMAIL}?subject=${encodeURIComponent(subject)}`
}

/**
 * AUTO-001 fix pass (2026-09-26), item 4: the "How a posture is set" band
 * (a rule for judging a domain posture) is removed — the facts-only tracker
 * states no posture to set a rule for. `ArchiveLinks` already carries the
 * front page's pointers to the standing thesis, the method, and the
 * evidence library, so that link row is not rebuilt here.
 */
export function NextEdition() {
  return (
    <section id="next" className="next-edition" aria-labelledby="next-edition-heading">
      <p className="eyebrow">Corrections</p>
      <h2 id="next-edition-heading">If a figure is wrong, send it</h2>
      <p>
        Corrections and counter-evidence are more useful than agreement. If a print is wrong, a
        source has been superseded, or a read goes further than the evidence does, that is worth an
        email. There is no form, and every correction that gets published is listed at{' '}
        <a href="/corrections/">/corrections/</a>.
      </p>
      <div className="next-edition__actions">
        <a
          className="next-edition__action"
          href={mailto('Security Market Pulse — correction or question')}
        >
          <MessageSquare size={14} aria-hidden="true" />
          <span>Send a correction or a question</span>
        </a>
      </div>
      <p className="next-edition__meta">
        <a href={`mailto:${CONTACT_EMAIL}`}>{CONTACT_EMAIL}</a>
      </p>
    </section>
  )
}
