import { useContext } from 'react'
import { EvidenceContext } from './evidenceContext'

export function useEvidence() {
  const context = useContext(EvidenceContext)
  if (!context) {
    throw new Error('useEvidence must be used within EvidenceProvider')
  }
  return context
}
