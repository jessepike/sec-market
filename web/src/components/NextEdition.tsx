import { Mail, MessageSquare } from 'lucide-react'
import { AUTHOR_NAME, CONTACT_EMAIL } from '../data/meta'

function mailto(subject: string): string {
  return `mailto:${CONTACT_EMAIL}?subject=${encodeURIComponent(subject)}`
}

export function NextEdition() {
  return (
    <section id="next" className="next-edition" aria-labelledby="next-edition-heading">
      <p className="eyebrow">Next edition</p>
      <h2 id="next-edition-heading">Get the next read, or argue with this one</h2>
      <p>
        Editions publish when the evidence moves, not on a fixed schedule. The next one will show
        what held or moved from this edition. Ask to be told when it is out and you will get an
        email when it publishes. There is no form and no signup behind these links — they open a
        plain message to me.
      </p>
      <p>
        Corrections and counter-evidence are more useful than agreement. If a print is wrong, a
        source has been superseded, or a call reads further than the evidence goes, that is worth an
        email.
      </p>
      <div className="next-edition__actions">
        <a
          className="next-edition__action"
          href={mailto('Security Market Pulse — tell me when the next edition publishes')}
        >
          <Mail size={14} aria-hidden="true" />
          <span>Tell me when the next edition publishes</span>
        </a>
        <a
          className="next-edition__action next-edition__action--quiet"
          href={mailto('Security Market Pulse — correction or question')}
        >
          <MessageSquare size={14} aria-hidden="true" />
          <span>Send a correction or a question</span>
        </a>
      </div>
      <p className="next-edition__meta">
        {AUTHOR_NAME} · <a href={`mailto:${CONTACT_EMAIL}`}>{CONTACT_EMAIL}</a>
      </p>
    </section>
  )
}
