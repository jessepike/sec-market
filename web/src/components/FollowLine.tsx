/**
 * "Follow": one line pointing to the certification receipt (every certified
 * claim with its SEC source) and the RSS feed. Sits between the change log
 * and the domain landscape.
 */
export function FollowLine() {
  return (
    <section id="follow" className="follow-line" aria-label="Follow">
      <p>
        Every certified claim and its SEC source is listed in the <a href="/certified-coverage.json">certification receipt</a>. Follow new records by <a href="/feed.xml">RSS</a>.
      </p>
    </section>
  )
}
