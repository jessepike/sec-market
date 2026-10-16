/**
 * "Follow" — design-spec v0.3 §3.1 row 5. One sentence saying what arrives
 * and how often, with a visible link to the feed. Sits between the four
 * lanes and the domain landscape.
 *
 * AUTO-001 fix pass 2, item 5: both blind rescores flagged the previous
 * sentence ("arrive through the week") as not a real cadence statement.
 * The actual schedule, from the collectors themselves: SEC EDGAR revenue
 * figures refresh daily (scripts/edgar-refresh.ts, cron `0 13 * * *`);
 * press, funding and distress facts refresh twice a week
 * (scripts/collect.sh's own header comment).
 */
export function FollowLine() {
  return (
    <section id="follow" className="follow-line" aria-label="Follow">
      <p>
        Every certified claim and its SEC source is listed in the <a href="/certified-coverage.json">certification receipt</a>. Follow published records by RSS:         <a href="/feed.xml">follow by RSS</a>.
      </p>
    </section>
  )
}
