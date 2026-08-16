import { useEvidence } from '../context/useEvidence'
import { evidenceAriaLabel, evidenceSourceLabel } from '../data/evidenceLabels'
import { FileSearch } from 'lucide-react'

interface EvidenceLinkProps {
  ids: string | string[]
  label?: string
  className?: string
}

export function EvidenceLink({ ids, label, className = '' }: EvidenceLinkProps) {
  const { openEvidence } = useEvidence()
  const idList = Array.isArray(ids) ? ids : [ids]
  const displayLabel = label ?? evidenceSourceLabel(idList)

  return (
    <button
      type="button"
      className={`evidence-link ${className}`}
      onClick={() => openEvidence(idList)}
      aria-label={evidenceAriaLabel(idList, label)}
    >
      <FileSearch size={14} aria-hidden="true" />
      <span>{displayLabel}</span>
    </button>
  )
}
