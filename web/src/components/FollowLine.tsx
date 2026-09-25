/**
 * "Follow" — design-spec v0.3 §3.1 row 5. One sentence saying what arrives
 * and how often, with a visible link to the feed. Sits between the four
 * lanes and the domain landscape.
 */
export function FollowLine() {
  return (
    <section id="follow" className="follow-line" aria-label="Follow">
      <p>
        Tracked figures arrive through the week as companies report them —{' '}
        <a href="/feed.xml">follow by RSS</a>.
      </p>
    </section>
  )
}
