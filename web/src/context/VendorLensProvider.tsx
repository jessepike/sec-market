import { useCallback, useEffect, useMemo, useState, type ReactNode } from 'react'
import { parseVendorsParam, serializeVendorsParam } from '../data/issueHelpers'
import { VendorLensContext, type VendorLensState } from './vendorLensContext'

/**
 * Client-only vendor lens state (SEC-031, weekly-issue-spec.md §5). Starts
 * inactive (`null`) so the server render and the client's first hydration
 * pass agree — a `useEffect` reads `?vendors=` from the URL only after
 * mount, so prerendered HTML never sees a filtered render and there is
 * nothing for hydration to disagree about. Scoped to the front page only:
 * wrap just the part of the tree that has the lens control and the two
 * filterable surfaces (see App.tsx's FrontPage).
 */
export function VendorLensProvider({ children }: { children: ReactNode }) {
  const [activeSlugs, setActiveSlugsState] = useState<string[] | null>(null)

  useEffect(() => {
    const sync = () => setActiveSlugsState(parseVendorsParam(window.location.search))
    sync()
    // A reader can also arrive at a filtered URL via back/forward navigation.
    window.addEventListener('popstate', sync)
    return () => window.removeEventListener('popstate', sync)
  }, [])

  const setActiveSlugs = useCallback((slugs: string[] | null) => {
    const encoded = serializeVendorsParam(slugs)
    setActiveSlugsState(encoded === null ? null : slugs)

    const url = new URL(window.location.href)
    if (encoded === null) {
      url.searchParams.delete('vendors')
    } else {
      url.searchParams.set('vendors', encoded)
    }
    window.history.replaceState(null, '', `${url.pathname}${url.search}${url.hash}`)
  }, [])

  const clear = useCallback(() => setActiveSlugs(null), [setActiveSlugs])

  const value = useMemo<VendorLensState>(
    () => ({ activeSlugs, setActiveSlugs, clear }),
    [activeSlugs, setActiveSlugs, clear],
  )

  return <VendorLensContext.Provider value={value}>{children}</VendorLensContext.Provider>
}
