import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from 'react'

interface EvidenceContextValue {
  selectedIds: string[]
  isOpen: boolean
  openEvidence: (ids: string | string[]) => void
  closeEvidence: () => void
}

const EvidenceContext = createContext<EvidenceContextValue | null>(null)

export function EvidenceProvider({ children }: { children: ReactNode }) {
  const [selectedIds, setSelectedIds] = useState<string[]>([])
  const [isOpen, setIsOpen] = useState(false)

  const openEvidence = useCallback((ids: string | string[]) => {
    const list = Array.isArray(ids) ? ids : [ids]
    setSelectedIds(list)
    setIsOpen(true)
  }, [])

  const closeEvidence = useCallback(() => {
    setIsOpen(false)
  }, [])

  const value = useMemo(
    () => ({ selectedIds, isOpen, openEvidence, closeEvidence }),
    [selectedIds, isOpen, openEvidence, closeEvidence],
  )

  return <EvidenceContext.Provider value={value}>{children}</EvidenceContext.Provider>
}

export function useEvidence() {
  const context = useContext(EvidenceContext)
  if (!context) {
    throw new Error('useEvidence must be used within EvidenceProvider')
  }
  return context
}
