import { createContext } from 'react'

export interface VendorLensState {
  /** `null` when the `vendors` query parameter is absent — the lens is inactive
   * and every consumer must render unfiltered. */
  activeSlugs: string[] | null
  /** Sets the active slugs and writes `?vendors=` via `history.replaceState`.
   * `null` or `[]` clears the parameter entirely. */
  setActiveSlugs: (slugs: string[] | null) => void
  /** Shorthand for `setActiveSlugs(null)`. */
  clear: () => void
}

/** `null` default (rather than an inactive object) lets `useVendorLens` tell
 * "no provider in the tree" apart from "provider, lens inactive" if it ever
 * needs to — see useVendorLens.ts. */
export const VendorLensContext = createContext<VendorLensState | null>(null)
