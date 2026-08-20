import { activityItems } from './activity'
import { formatWeekRange } from './dates'
import { landscapeDomainIds } from './domains'
import { currentEdition, editionDomainRows } from './edition'
import { LAST_UPDATED_ISO } from './meta'
import { reasoningSteps } from './method'
import { platformPressure } from './platformPressure'
import { vendorPrints } from './prints'

export interface WeekMove {
  kind: string
  text: string
  evidenceIds: string[]
  basisHref?: string
  basisLabel?: string
}

function uniq(ids: string[]): string[] {
  const seen = new Set<string>()
  const out: string[] = []
  for (const id of ids) {
    if (seen.has(id)) continue
    seen.add(id)
    out.push(id)
  }
  return out
}

const fasterRead = 'printing faster'
const breadthRule = reasoningSteps.find((step) => step.step === 'Need breadth before a domain call')

const earlyNames = new Set(
  vendorPrints.filter((print) => print.position === 'early').map((print) => print.name),
)

const printMove = platformPressure.outrun.find((row) => row.read.includes(fasterRead))
const capitalItems = activityItems.filter(
  (item) => item.kind === 'funding' && earlyNames.has(item.target),
)
const closedLeadMa = activityItems.filter(
  (item) => item.kind === 'ma' && item.surface === 'lead' && item.headline.toLowerCase().includes('closed'),
)
const absorbed = platformPressure['buying-in']

function trackedPrint(): WeekMove | null {
  if (!printMove) return null
  return {
    kind: 'PRINT',
    text: printMove.read,
    evidenceIds: uniq(
      printMove.provenance.print.layer === 'tracked' ? printMove.provenance.print.evidenceIds : [],
    ),
  }
}

function trackedCapital(): WeekMove | null {
  if (capitalItems.length === 0) return null
  return {
    kind: 'CAPITAL',
    text:
      capitalItems.map((item) => item.target + ' raised ' + item.value).join(', ') +
      '. Capital heat, not disclosed revenue.',
    evidenceIds: uniq(capitalItems.flatMap((item) => item.evidenceIds)),
  }
}

function trackedMa(): WeekMove {
  if (closedLeadMa.length > 0) {
    return {
      kind: 'M&A',
      text: closedLeadMa.map((item) => item.headline).join(' '),
      evidenceIds: uniq(closedLeadMa.flatMap((item) => item.evidenceIds)),
    }
  }
  const priorCloses = absorbed.map((row) => row.print).join(' and ')
  return {
    kind: 'M&A',
    text:
      'No new closed transaction in the window.' +
      (priorCloses ? ' ' + priorCloses + '. Neither is this month\'s demand signal.' : ''),
    evidenceIds: uniq(
      absorbed.flatMap((row) =>
        row.provenance.print.layer === 'tracked' ? row.provenance.print.evidenceIds : [],
      ),
    ),
  }
}

const landscapeRows = editionDomainRows().filter((row) =>
  (landscapeDomainIds as readonly string[]).includes(row.id),
)
const heldCount = landscapeRows.filter((row) => row.kind === 'held').length
const allHeld = heldCount === landscapeRows.length && landscapeRows.length > 0

export const weekMoves = {
  label: formatWeekRange(LAST_UPDATED_ISO),
  asOf: LAST_UPDATED_ISO,
  tracked: [trackedPrint(), trackedCapital(), trackedMa()].filter((item): item is WeekMove => item !== null),
  judged: [
    {
      kind: allHeld ? 'HELD' : 'MOVED',
      text: allHeld
        ? 'All ' + String(landscapeRows.length) + ' postures unchanged.'
        : landscapeRows
            .filter((row) => row.kind !== 'held')
            .map((row) => row.name + ' ' + row.change)
            .join(' '),
      evidenceIds: [],
      basisHref: '#domains',
      basisLabel: 'Edition delta',
    },
    {
      kind: 'WHY',
      text: breadthRule
        ? breadthRule.rule
        : 'A posture needs more than one company and a reason the motion is not just share shift.',
      evidenceIds: [],
      basisHref: '#method',
      basisLabel: 'Method · breadth rule',
    },
  ] satisfies WeekMove[],
  quietNote: 'A quiet week is reported as a quiet week. Nothing is invented to fill the space.',
  editionSummary: currentEdition.summary,
}
