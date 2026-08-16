import { EPISODE_ID, EPISODE_VERSION, RESEARCH_FREEZE } from '../data/meta'

export function MethodologyNote() {
  return (
    <footer className="methodology-note">
      <p>
        <strong>Methodology &amp; evidence.</strong> Content is frozen from {EPISODE_ID} v
        {EPISODE_VERSION} (research freeze {RESEARCH_FREEZE}). This is not investment advice. Material
        claims link to source excerpts, limitations, and conflicting evidence. A stable
        infrastructure-to-security lag is explicitly <span className="mono">NO-CALL</span>.
      </p>
    </footer>
  )
}
