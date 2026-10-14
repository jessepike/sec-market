import { useCallback, useMemo, useState, type ReactNode } from 'react'
import { EvidenceContext } from './evidenceContext'

export function EvidenceProvider({ children }: { children: ReactNode }) {
  const [selectedIds, setSelectedIds] = useState<string[]>([])
  const [history, setHistory] = useState<string[][]>([])
  const [isOpen, setIsOpen] = useState(false)

  const openEvidence = useCallback((ids: string | string[]) => {
    const list = Array.isArray(ids) ? ids : [ids]
    setHistory([])
    setSelectedIds(list)
    setIsOpen(true)
  }, [])

  const openConflictingEvidence = useCallback(
    (id: string) => {
      setHistory((prev) => [...prev, selectedIds])
      setSelectedIds([id])
      setIsOpen(true)
    },
    [selectedIds],
  )

  const goBack = useCallback(() => {
    setHistory((prev) => {
      if (prev.length === 0) return prev
      const next = [...prev]
      const prior = next.pop()
      if (prior) setSelectedIds(prior)
      return next
    })
  }, [])

  const closeEvidence = useCallback(() => {
    setIsOpen(false)
    setHistory([])
  }, [])

  const value = useMemo(
    () => ({
      selectedIds,
      isOpen,
      canGoBack: history.length > 0,
      openEvidence,
      openConflictingEvidence,
      goBack,
      closeEvidence,
    }),
    [selectedIds, isOpen, history.length, openEvidence, openConflictingEvidence, goBack, closeEvidence],
  )

  return <EvidenceContext.Provider value={value}>{children}</EvidenceContext.Provider>
}
