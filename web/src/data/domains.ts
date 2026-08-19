import { vendorPrints } from './prints'
import type { SecurityDomain } from './types'

/** The four landscape cards. Remaining domains stay on prints and Activity. */
export const landscapeDomainIds = [
  'network-sase',
  'data-ai-security',
  'cloud-security',
  'identity',
] as const

export const securityDomains: SecurityDomain[] = [
  {
    id: 'network-sase',
    name: 'Network / SASE',
    coverage: 'PASS_WITH_LIMITATION',
    posture: 'PREPARE',
    tag: 'PREPARE',
    asOf: '2026-08-16',
    horizon: 'This quarter',
    momentum: 'accelerating',
    evidenceStrength: 'medium',
    print: 'Fortinet +52% · Cato +43% · Netskope +31%',
    why: 'Refresh is live. Cato and Netskope are growing faster than Zscaler organic. That is a split, not a new SASE wave.',
    summary:
      'Appliance-led network security is live now. Private SASE and public SSE are split from Zscaler organic — not a category re-acceleration.',
    watchItems: [
      'Next Fortinet print: refresh spike vs lasting rotation',
      'Zscaler FY27 guide: company-specific or SASE-wide',
    ],
    supportingEvidenceIds: ['C3', 'C4', 'C5', 'C11', 'C12', 'A2'],
    counterEvidenceIds: ['C6a', 'C6b'],
  },
  {
    id: 'data-ai-security',
    name: 'Data / AI Security',
    coverage: 'PASS_WITH_LIMITATION',
    posture: 'PREPARE',
    tag: 'PREPARE',
    asOf: '2026-08-16',
    horizon: 'This planning cycle',
    momentum: 'accelerating',
    evidenceStrength: 'medium',
    print: 'Rubrik +32% · Varonis +25% · Sentra · Securiti close',
    why: 'Public data vendors are up. DSPM names are capital and M&A, not a broad spend series.',
    summary: 'Selected data vendors are accelerating. Not a broad realized series yet.',
    watchItems: ['Sensitive data entering production AI', 'DSPM absorption into platforms'],
    supportingEvidenceIds: ['C8a', 'C8b', 'D8', 'D9', 'C14', 'C15', 'C16', 'D2', 'D7'],
    counterEvidenceIds: ['D1'],
  },
  {
    id: 'cloud-security',
    name: 'Cloud Security',
    coverage: 'PASS_WITH_LIMITATION',
    posture: 'INVESTIGATE',
    tag: 'WATCH',
    asOf: '2026-08-16',
    horizon: 'Next 1–4 quarters',
    momentum: 'mixed-positive',
    evidenceStrength: 'medium',
    print: 'Falcon Cloud >$800M · Upwind · Orca · Aqua',
    why: 'CrowdStrike cloud segment is real. CNAPP names show 2026 GTM or last disclosed equity — not a clean category ARR series.',
    summary: 'Qualify residual gaps when capacity goes live.',
    watchItems: ['Workload activation', 'Native controls vs specialist gaps'],
    supportingEvidenceIds: ['D5a', 'D7', 'C13', 'C17', 'C18', 'C19', 'C24', 'D30'],
    counterEvidenceIds: ['D1'],
  },
  {
    id: 'identity',
    name: 'Identity',
    coverage: 'PASS_WITH_LIMITATION',
    posture: 'INVESTIGATE',
    tag: 'WATCH',
    asOf: '2026-08-16',
    horizon: 'Next 1–4 quarters',
    momentum: 'stable-to-decelerating',
    evidenceStrength: 'medium',
    print: 'SailPoint +28% · Oak $60M · Hush $30M',
    why: 'IGA is up. Mega-seed and strategic rounds are capital heat in agentic identity — not buyer spend yet.',
    summary: 'Use identity as a qualification topic where machine identities go live.',
    watchItems: ['First disclosed agentic-identity revenue', 'Palo Alto vs CyberArk mix'],
    supportingEvidenceIds: ['C10', 'D5b', 'D10', 'D11', 'D20', 'D21', 'C23', 'D7', 'D6'],
    counterEvidenceIds: ['C7', 'D12'],
  },
  {
    id: 'secops',
    name: 'SecOps',
    coverage: 'PASS_WITH_LIMITATION',
    posture: 'INVESTIGATE',
    tag: 'WATCH',
    asOf: '2026-08-16',
    horizon: 'Next 1–4 quarters',
    momentum: 'mixed-positive',
    evidenceStrength: 'medium',
    print: 'S1 +23% · CRWD +24% · XSIAM +100% · Torq $1.2B',
    why: 'Public XDR and XSIAM segments are healthy. SOAR capital (Torq, Tines) is scale-up, not a new cycle.',
    summary: 'Share shift and platformization, not a new SecOps cycle.',
    watchItems: ['Organic bridges after acquisitions'],
    supportingEvidenceIds: ['C9', 'C1', 'C6b', 'C21', 'C25', 'D31', 'D4'],
    counterEvidenceIds: ['C6a', 'C6b'],
  },
  {
    id: 'ai-runtime',
    name: 'AI Runtime',
    coverage: 'PASS_WITH_LIMITATION',
    posture: 'INVESTIGATE',
    tag: 'WATCH',
    asOf: '2026-08-16',
    horizon: 'Next 1–4 quarters',
    momentum: 'stable-positive',
    evidenceStrength: 'medium',
    print: 'Zenity $125M · WitnessAI $58M · Onyx $113M',
    why: 'Agent governance capital is real and sourced. Company-stated growth is not public buyer spend.',
    summary: 'Do not run a specialist-platform motion from survey intent alone.',
    watchItems: ['Pilot-to-production scaling', 'First disclosed agentic-identity revenue print'],
    supportingEvidenceIds: ['D19', 'D18', 'C20', 'C22', 'D2', 'D3'],
    counterEvidenceIds: ['D1'],
  },
]

export const landscapeDomains: SecurityDomain[] = landscapeDomainIds.map((id) => {
  const domain = securityDomains.find((item) => item.id === id)
  if (!domain) {
    throw new Error('Landscape is missing domain ' + id)
  }
  return domain
})

/** Names written on a landscape card's TRACKED print line, in display order. */
function namesOnPrintLine(line: string): string[] {
  return line
    .split('·')
    .map((part) =>
      part
        .replace(/\s+[+$].*$/, '')
        .replace(/\s+>\$\d.*$/, '')
        .replace(/\s+\$\d.*$/, '')
        .replace(/\s+close\s*$/i, '')
        .trim(),
    )
    .filter(Boolean)
}

function printMatchesName(printName: string, token: string): boolean {
  return printName === token || printName.startsWith(token + ' ') || printName.endsWith(' ' + token)
}

/**
 * Evidence for the prints on a landscape card, not the wider posture bundle.
 * Cloud's supporting list includes the Wiz close; that must not label Falcon Cloud.
 */
export function trackedPrintEvidenceIds(domain: SecurityDomain): string[] {
  const ids: string[] = []
  const seen = new Set<string>()
  for (const token of namesOnPrintLine(domain.print)) {
    const print = vendorPrints.find((row) => printMatchesName(row.name, token))
    if (!print) {
      throw new Error(`Landscape card ${domain.id} print "${token}" has no vendor print`)
    }
    for (const id of print.evidenceIds) {
      if (seen.has(id)) continue
      seen.add(id)
      ids.push(id)
    }
  }
  if (ids.length === 0) {
    throw new Error(`Landscape card ${domain.id} has no print-linked evidence`)
  }
  return ids
}
