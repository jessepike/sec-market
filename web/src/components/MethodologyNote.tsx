import { publishedIssues } from '../data/issues/index'

/**
 * Visible machine-surface links (agent-surface-spec.md §3.6/§6, wave 1): the
 * three JSON files that already exist and were previously linked from
 * nowhere in the page. Reads the newest PUBLISHED issue only, never a draft
 * — `publishedIssues` already excludes drafts (data/issues/index.ts).
 *
 * AUTO-001 fix pass (2026-09-26), item 4: the "Frozen from {EPISODE_ID}
 * v{EPISODE_VERSION} (2026-08-15T19:03:08-07:00)" line is removed — it
 * described a frozen research packet from over a month before the scoring
 * date, on the same page as a "Figures checked 26 Sep 2026" run-status
 * line, which both scorers read as a live page contradicting itself
 * (fit-for-purpose blocker 4). The tracker is not built from a frozen
 * packet any longer.
 */
export function MethodologyNote() {
  const newestPublished = publishedIssues[publishedIssues.length - 1]

  return (
    <footer className="methodology-note">
      <p>Public sources only. Not investment advice. See How this is built.</p>
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
