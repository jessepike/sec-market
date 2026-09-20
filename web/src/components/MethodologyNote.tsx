import { EPISODE_ID, EPISODE_VERSION, RESEARCH_FREEZE } from '../data/meta'
import { publishedIssues } from '../data/issues/index'

/**
 * Visible machine-surface links (agent-surface-spec.md §3.6/§6, wave 1): the
 * three JSON files that already exist and were previously linked from
 * nowhere in the page. Reads the newest PUBLISHED issue only, never a draft
 * — `publishedIssues` already excludes drafts (data/issues/index.ts).
 */
export function MethodologyNote() {
  const newestPublished = publishedIssues[publishedIssues.length - 1]

  return (
    <footer className="methodology-note">
      <p>
        Frozen from {EPISODE_ID} v{EPISODE_VERSION} ({RESEARCH_FREEZE}). Public sources only. Not
        investment advice. See How this is built.
      </p>
      <p className="methodology-note__data">
        Data: <a href="/issues/index.json">issue index</a>
        {newestPublished ? (
          <>
            {' · '}
            <a href={`/issues/${newestPublished.id}.json`}>newest issue</a>
          </>
        ) : null}
        {' · '}
        <a href="/issues/lock.json">publication ledger</a>
      </p>
    </footer>
  )
}
