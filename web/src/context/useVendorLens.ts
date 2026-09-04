import { useContext } from 'react'
import { VendorLensContext, type VendorLensState } from './vendorLensContext'

/** Inactive fallback so IssueLanes/PrintGrid render unfiltered outside a
 * VendorLensProvider — the issue permalink page carries no lens control, and
 * scripts/verify-issue.ts's check 10 renders IssueLanes standalone. Neither
 * should have to know the lens exists. */
const INACTIVE: VendorLensState = {
  activeSlugs: null,
  setActiveSlugs: () => {},
  clear: () => {},
}

export function useVendorLens(): VendorLensState {
  return useContext(VendorLensContext) ?? INACTIVE
}
