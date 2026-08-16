import { useEvidence } from '../context/EvidenceContext'
import { FileSearch } from 'lucide-react'

interface EvidenceLinkProps {
  ids: string | string[]
  label?: string
  className?: string
}

export function EvidenceLink({ ids, label = 'View evidence', className = '' }: EvidenceLinkProps) {
  const { openEvidence } = useEvidence()
  const idList = Array.isArray(ids) ? ids : [ids]

  return (
    <button
      type="button"
      className={`evidence-link ${className}`}
      onClick={() => openEvidence(idList)}
      aria-label={`${label} (${idList.join(', ')})`}
    >
      <FileSearch size={14} aria-hidden="true" />
      <span>{label}</span>
      <span className="evidence-link-ids">{idList.join(', ')}</span>
    </button>
  )
}
