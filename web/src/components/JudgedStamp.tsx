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
 * reconfirmations check), so this never takes a name prop.
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
      JUDGED <time dateTime={judgedOn}>{formatShortDate(judgedOn)}</time> &middot; RECONFIRMED{' '}
      <time dateTime={reconfirmedOn}>{formatShortDate(reconfirmedOn)}</time> &middot; {AUTHOR_NAME}
    </p>
  )
}
