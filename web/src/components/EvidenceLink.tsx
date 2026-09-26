import { useEvidence } from '../context/useEvidence'
import { evidenceAriaLabel, evidenceCompactAriaLabel, evidenceSourceLabel } from '../data/evidenceLabels'
import { FileSearch } from 'lucide-react'

interface EvidenceLinkProps {
  ids: string | string[]
  label?: string
  className?: string
  /**
   * Density pass — "compact" renders a small mono "src" mark instead of the
   * source's name, for a dense table cell where a full evidence-link chip
   * per row does not fit. Opens the same evidence drawer; its accessible
   * label still names the source and date since the visible mark does not.
   */
  variant?: 'default' | 'compact'
  context?: string
}

export function EvidenceLink({ ids, label, className = '', variant = 'default', context }: EvidenceLinkProps) {
  const { openEvidence } = useEvidence()
  const idList = Array.isArray(ids) ? ids : [ids]

  if (variant === 'compact') {
    return (
      <button
        type="button"
        className={`evidence-link evidence-link--compact ${className}`}
        onClick={() => openEvidence(idList)}
        aria-label={evidenceCompactAriaLabel(idList, context)}
      >
        src
      </button>
    )
  }

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
