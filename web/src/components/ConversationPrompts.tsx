import { conversationPrompts } from '../data/prompts'
import { EvidenceLink } from './EvidenceLink'

export function ConversationPrompts() {
  return (
    <section id="prompts" className="prompts" aria-labelledby="prompts-heading">
      <div className="section-heading">
        <h2 id="prompts-heading">Account conversation prompts</h2>
        <p>Practical questions for client and account discussions — bounded and reversible.</p>
      </div>
      <div className="prompts__grid">
        {conversationPrompts.map((item) => (
          <article key={item.id} className="prompt-card">
            <p className="prompt-card__audience">{item.audience}</p>
            <blockquote className="prompt-card__quote">{item.prompt}</blockquote>
            <p className="prompt-card__when">
              <strong>When:</strong> {item.whenToUse}
            </p>
            <EvidenceLink ids={item.evidenceIds} label="Grounding evidence" />
          </article>
        ))}
      </div>
    </section>
  )
}
