import { MessageSquare } from 'lucide-react'
import { AUTHOR_NAME, CONTACT_EMAIL } from '../data/meta'
import { reasoningSteps } from '../data/method'

function mailto(subject: string): string {
  return `mailto:${CONTACT_EMAIL}?subject=${encodeURIComponent(subject)}`
}

const postureRule = reasoningSteps.find((step) => step.step === 'Need breadth before a domain call')

export function NextEdition() {
  return (
    <section id="next" className="next-edition" aria-labelledby="next-edition-heading">
      <div className="method-band">
        <div className="method-band__copy">
          <p className="eyebrow">How a posture is set</p>
          <p>
            {postureRule
              ? postureRule.rule
              : 'A posture needs more than one company and a reason the motion is not just share shift.'}
          </p>
        </div>
        <div className="method-band__links">
          <a href="#method">Read the method</a>
          <a href="#research">Open the evidence library</a>
          <a href={mailto('Security Market Pulse — correction or question')}>Send a correction</a>
        </div>
      </div>
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
        {AUTHOR_NAME} · <a href={`mailto:${CONTACT_EMAIL}`}>{CONTACT_EMAIL}</a>
      </p>
    </section>
  )
}
