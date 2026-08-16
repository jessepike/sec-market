import { EPISODE_ID, EPISODE_VERSION, RESEARCH_FREEZE } from '../data/meta'

export function MethodologyNote() {
  return (
    <footer className="methodology-note">
      <p>
        <strong>Methodology.</strong> Frozen from {EPISODE_ID} v{EPISODE_VERSION} (research freeze{' '}
        {RESEARCH_FREEZE}). Not investment advice. Material claims link to source excerpts,
        limitations, and conflicting evidence. A stable infrastructure-to-security lag is not
        measurable from the current public window.
      </p>
    </footer>
  )
}
