import { formatShortDate } from '../data/dates'
import { AUTHOR_NAME } from '../data/meta'

/**
 * The "JUDGED <date> · NAME" stamp, shared by every component that renders
 * one for a domain stance, a hypothesis, or a Platform-pressure row
 * (SEC-MARKET-PUBLISH-001 §4.3). With no reconfirmation the markup is
 * byte-identical to what each caller used to render inline — this must
 * never change on the page until an owner-approved reconfirmation exists.
 * With one, both dates show, honestly: "JUDGED <date> · RECONFIRMED <date> ·
 * NAME". `by` is always `AUTHOR_NAME` (validated in verify-issue.ts's
 * reconfirmations check), so this never takes a name prop. The reconfirmed
 * form only — never the no-reconfirmation form, which must stay untouched —
 * wraps each of its three segments ("JUDGED <date>", "RECONFIRMED <date>",
 * the name) in a `.stamp-segment` span (`white-space: nowrap` in
 * index.css), so a narrow phone screen wraps the line between segments
 * rather than inside one, e.g. splitting "Jesse" from "Pike".
 *
 * Three shapes exist, not one, because the four call sites wrote this stamp
 * as three different literal JSX structures before this refactor, and
 * React's server rendering inserts `<!-- -->` boundary comments between
 * adjacent children that both produce plain text, in a way that depends on
 * exactly how the JSX source grouped them (a bare `{' '}` as its own child
 * versus a space folded into a neighbouring string) — not on the visible
 * characters, and not reliably reproducible by eye. This was verified
 * against the real build (`dist/index.html`, `vite build` + prerender),
 * not by reasoning about the transform, after an earlier version of this
 * component that looked right by inspection still changed bytes on two of
 * the three shapes. `JudgedStamp` reproduces market-picture's shape (the
 * space before the name folded into the same text as the middle dot);
 * `JudgedStampSpaced` reproduces the domain-stance shape (that space as its
 * own `{' '}` child); `JudgedStampStacked` reproduces the hypothesis and
 * Platform-pressure shape (date wrapped across lines with a bare `{' '}` on
 * both sides). Picking the wrong one still shows the right words, but it
 * changes the rendered HTML byte-for-byte, which is exactly the diff this
 * component exists to keep at zero. If a fifth call site is ever added,
 * confirm which shape it needs the same way: build both branches and diff
 * the real `dist/` output, not a component-level test — the test runner's
 * own JSX-to-JS transform is not guaranteed to match the production build's.
 */
export function JudgedStamp({
  judgedOn,
  reconfirmedOn,
}: {
  judgedOn: string
  reconfirmedOn: string | null
}) {
  if (!reconfirmedOn) {
    return (
      <p className="stamp-label">
        JUDGED <time dateTime={judgedOn}>{formatShortDate(judgedOn)}</time> &middot; {AUTHOR_NAME}
      </p>
    )
  }
  return (
    <p className="stamp-label">
      <span className="stamp-segment">
        JUDGED <time dateTime={judgedOn}>{formatShortDate(judgedOn)}</time>
      </span>{' '}
      &middot;{' '}
      <span className="stamp-segment">
        RECONFIRMED <time dateTime={reconfirmedOn}>{formatShortDate(reconfirmedOn)}</time>
      </span>{' '}
      &middot; <span className="stamp-segment">{AUTHOR_NAME}</span>
    </p>
  )
}

export function JudgedStampSpaced({
  judgedOn,
  reconfirmedOn,
}: {
  judgedOn: string
  reconfirmedOn: string | null
}) {
  if (!reconfirmedOn) {
    return (
      <p className="stamp-label">
        JUDGED <time dateTime={judgedOn}>{formatShortDate(judgedOn)}</time> &middot;{' '}
        {AUTHOR_NAME}
      </p>
    )
  }
  return (
    <p className="stamp-label">
      <span className="stamp-segment">
        JUDGED <time dateTime={judgedOn}>{formatShortDate(judgedOn)}</time>
      </span>{' '}
      &middot;{' '}
      <span className="stamp-segment">
        RECONFIRMED <time dateTime={reconfirmedOn}>{formatShortDate(reconfirmedOn)}</time>
      </span>{' '}
      &middot; <span className="stamp-segment">{AUTHOR_NAME}</span>
    </p>
  )
}

export function JudgedStampStacked({
  judgedOn,
  reconfirmedOn,
}: {
  judgedOn: string
  reconfirmedOn: string | null
}) {
  if (!reconfirmedOn) {
    return (
      <p className="stamp-label">
        JUDGED{' '}
        <time dateTime={judgedOn}>{formatShortDate(judgedOn)}</time>{' '}
        &middot; {AUTHOR_NAME}
      </p>
    )
  }
  return (
    <p className="stamp-label">
      <span className="stamp-segment">
        JUDGED <time dateTime={judgedOn}>{formatShortDate(judgedOn)}</time>
      </span>{' '}
      &middot;{' '}
      <span className="stamp-segment">
        RECONFIRMED <time dateTime={reconfirmedOn}>{formatShortDate(reconfirmedOn)}</time>
      </span>{' '}
      &middot; <span className="stamp-segment">{AUTHOR_NAME}</span>
    </p>
  )
}
