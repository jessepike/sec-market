import { createContext } from 'react'

export interface EvidenceContextValue {
  selectedIds: string[]
  isOpen: boolean
  canGoBack: boolean
  openEvidence: (ids: string | string[]) => void
  openConflictingEvidence: (id: string) => void
  goBack: () => void
  closeEvidence: () => void
}

export const EvidenceContext = createContext<EvidenceContextValue | null>(null)
