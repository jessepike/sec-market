import { EPISODE_ID, EPISODE_VERSION, RESEARCH_FREEZE } from '../data/meta'

export function MethodologyNote() {
  return (
    <footer className="methodology-note">
      <p>
        Frozen from {EPISODE_ID} v{EPISODE_VERSION} ({RESEARCH_FREEZE}). Public sources only. Not
        investment advice. See How this is built.
      </p>
    </footer>
  )
}
