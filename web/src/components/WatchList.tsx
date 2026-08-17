import { watchItems } from '../data/watch'

export function WatchList() {
  return (
    <section className="watch-list" aria-labelledby="watch-heading">
      <div className="section-heading">
        <h2 id="watch-heading">Watch next</h2>
        <p>What would change the read before the next freeze.</p>
      </div>
      <ol className="watch-list__items">
        {watchItems.map((item) => (
          <li key={item.id} className="watch-item">
            <p className="watch-item__window">{item.window}</p>
            <h3>{item.item}</h3>
            <p>{item.why}</p>
          </li>
        ))}
      </ol>
    </section>
  )
}
