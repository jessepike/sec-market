import { useVendorLens } from '../context/useVendorLens'

/**
 * The vendor lens control (SEC-031). Sits at the top of the Scorecard
 * (`#prints`), in the slot the previous operator reserved between Hypotheses
 * and PrintGrid. Reads its state from VendorLensProvider (App.tsx wraps the
 * front page in one) — inactive by default, including on the server, where
 * `useVendorLens` always returns its inactive fallback.
 *
 * When inactive this renders the exact same empty `<div id="vendor-lens-slot" />`
 * the placeholder did, so the page's prerendered HTML is unaffected by this
 * component existing: prerendering never sees `window`, so it always takes
 * this branch.
 */
export function VendorLens() {
  const { activeSlugs, setActiveSlugs, clear } = useVendorLens()

  if (activeSlugs === null) {
    return <div id="vendor-lens-slot" />
  }

  function removeSlug(slug: string) {
    setActiveSlugs(activeSlugs!.filter((candidate) => candidate !== slug))
  }

  return (
    <div id="vendor-lens-slot" className="vendor-lens" role="region" aria-label="Vendor lens">
      <p className="vendor-lens__label">Vendor lens</p>
      <div className="vendor-lens__chips">
        {activeSlugs.length === 0 ? (
          <span className="vendor-lens__empty-note">No vendor slugs in this URL.</span>
        ) : (
          activeSlugs.map((slug) => (
            <button
              key={slug}
              type="button"
              className="vendor-lens__chip"
              onClick={() => removeSlug(slug)}
            >
              {slug}
              <span aria-hidden="true"> ×</span>
            </button>
          ))
        )}
      </div>
      <a
        href="#"
        className="vendor-lens__clear"
        onClick={(event) => {
          event.preventDefault()
          clear()
        }}
      >
        Clear
      </a>
    </div>
  )
}
