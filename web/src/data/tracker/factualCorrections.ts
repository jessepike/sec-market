import type { EvidenceRecord } from '../types'
import type { TrackerEvent } from './events'
import type { FundingRound, HeadlineMetric, Ownership, TrackerSupplier } from './suppliers'

export type SupplierCorrectionField = 'lastRound' | 'headlineMetric' | 'ownership'
export type PublisherDisclosureReviewScope = 'publisher_disclosure_only'

/** Publication-role metadata only; this operation supplies no financial authority. */
export type PublisherDisclosureCorrectionTarget = {
  targetId: 'evidence:TR-xage-1'
  operation: 'reclassify_publisher_disclosure'
  original: EvidenceRecord
  originalSha256: string
  proposedValue: EvidenceRecord
}

type Replacement<T, Id extends string> = {
  targetId: Id
  operation: 'replace'
  original: T
  originalSha256: string
  proposedValue: T
}

export type FactualCorrectionTarget =
  | Replacement<TrackerEvent, `event:${string}`>
  | { targetId: `event:${string}`; operation: 'withdraw'; original: TrackerEvent; originalSha256: string; proposedValue: null }
  | Replacement<FundingRound, `supplier:${string}:lastRound`>
  | Replacement<HeadlineMetric, `supplier:${string}:headlineMetric`>
  | Replacement<Ownership, `supplier:${string}:ownership`>
  | Replacement<EvidenceRecord, `evidence:${string}`>
  | PublisherDisclosureCorrectionTarget

export interface FactualCorrectionAdmission {
  candidateSha256: string
  evidenceSetSha256: string
  /** This group's review policy, independent of the bundle's global inventory policy. */
  policySha256: string
  admittedAt: string
  reviewSha256: string
  result: 'accepted'
  reviewScope?: PublisherDisclosureReviewScope
}

export interface FactualCorrectionGroup {
  id: string
  supplierId: string
  reasonCode: string
  date: string
  note: string
  targets: FactualCorrectionTarget[]
  admission: FactualCorrectionAdmission
  reviewScope?: PublisherDisclosureReviewScope
}

export type FactualCorrectionBundle =
  | { schemaVersion: 1; enabled: false; policySha256: null; checkedAt: null; groups: [] }
  | { schemaVersion: 1; enabled: true; policySha256: string; checkedAt: string; groups: FactualCorrectionGroup[] }

export type FactualCorrectionReviewPolicyMap = Readonly<Record<string, string>>

/** Pass the same complete raw inventories to every projection, including before date filtering. */
export interface FactualCorrectionInventories {
  events: readonly TrackerEvent[]
  suppliers: readonly TrackerSupplier[]
  evidence: readonly EvidenceRecord[]
}

type ObjectValue = Record<string, unknown>
const hashShape = /^[a-f0-9]{64}$/
const idShape = /^[A-Za-z0-9][A-Za-z0-9_.-]*$/
const supplierFields = new Set(['lastRound', 'headlineMetric', 'ownership'])
const eventTypes = new Set(['funding', 'acquisition', 'layoff', 'restructuring', 'debt', 'rating', 'going-concern', 'exec-change', 'divestiture', 'shutdown', 'results', 'late-filing'])
const evidenceChanges = new Set(['title', 'publicationDate', 'economicPeriod', 'excerpt', 'limitations'])
const publisherDisclosureScope = 'publisher_disclosure_only'
const publisherDisclosureOriginalSha256 = '62bb8bcce0698b5f164867d9bc070be77ee4eebde095947dd96eb8a693d0d6fb'
const publisherDisclosureUrl = 'https://finance.yahoo.com/news/xage-security-hits-record-growth-120000615.html'
const publisherDisclosureLimitations = 'Yahoo Finance labels this page as a paid press release and attributes it to Xage Security with a GlobeNewswire dateline. It is issuer-attributed release material republished by Yahoo Finance, not independent editorial reporting. This publication-role correction does not independently verify the financial, funding or operating figures in the unchanged excerpt.'

function requireThat(condition: unknown, message: string): asserts condition {
  if (!condition) throw new Error(`Invalid factual corrections: ${message}`)
}

function object(value: unknown, label: string): ObjectValue {
  requireThat(value !== null && typeof value === 'object' && !Array.isArray(value), `${label} must be an object`)
  requireThat(Object.getPrototypeOf(value) === Object.prototype || Object.getPrototypeOf(value) === null, `${label} must be plain JSON`)
  return value as ObjectValue
}

function keys(value: ObjectValue, required: string[], optional: string[], label: string) {
  requireThat(required.every((key) => Object.hasOwn(value, key)), `${label} has missing fields`)
  requireThat(Object.keys(value).every((key) => required.includes(key) || optional.includes(key)), `${label} has unsupported fields`)
}

function string(value: unknown, label: string, allowEmpty = false): asserts value is string {
  requireThat(typeof value === 'string' && (allowEmpty || value.trim().length > 0), `${label} must be a string`)
}

function id(value: unknown, label: string): asserts value is string {
  string(value, label)
  requireThat(idShape.test(value), `${label} is malformed`)
}

function hash(value: unknown, label: string): asserts value is string {
  requireThat(typeof value === 'string' && hashShape.test(value), `${label} must be a SHA-256 string`)
}

function calendarDate(value: unknown, label: string): asserts value is string {
  requireThat(typeof value === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(value), `${label} must be a date`)
  const parsed = new Date(`${value}T00:00:00Z`)
  requireThat(Number.isFinite(parsed.getTime()) && parsed.toISOString().slice(0, 10) === value, `${label} is an invalid date`)
}

function timestamp(value: unknown, label: string): asserts value is string {
  requireThat(typeof value === 'string' && /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$/.test(value), `${label} must be a UTC timestamp`)
  calendarDate(value.slice(0, 10), label)
  const [, hours, minutes, seconds] = value.match(/T(\d{2}):(\d{2}):(\d{2})/)!
  requireThat(+hours < 24 && +minutes < 60 && +seconds < 60 && Number.isFinite(Date.parse(value)), `${label} is invalid`)
}

function strings(value: unknown, label: string, nonempty = false) {
  requireThat(Array.isArray(value) && (!nonempty || value.length > 0), `${label} must be an array`)
  value.forEach((entry) => string(entry, label))
  requireThat(new Set(value).size === value.length, `${label} has duplicate values`)
}

function url(value: unknown, label: string) {
  string(value, label)
  let parsed: URL
  try { parsed = new URL(value) } catch { throw new Error(`Invalid factual corrections: ${label} is not a URL`) }
  requireThat(['https:', 'http:'].includes(parsed.protocol) && !parsed.username && !parsed.password, `${label} must be a public HTTP URL`)
}

/** JSON equality is deliberate. Cryptographic binding is independently checked by the gate. */
function canonical(value: unknown, ancestors = new Set<unknown>()): string {
  if (value === null || typeof value === 'boolean' || typeof value === 'string') return JSON.stringify(value)
  if (typeof value === 'number') {
    requireThat(Number.isFinite(value), 'non-finite JSON number')
    return JSON.stringify(value)
  }
  requireThat(typeof value === 'object' && value !== null && !ancestors.has(value), 'value must be acyclic JSON')
  ancestors.add(value)
  let result: string
  if (Array.isArray(value)) {
    requireThat(Object.keys(value).length === value.length, 'sparse arrays are not JSON inventories')
    result = `[${value.map((entry) => canonical(entry, ancestors)).join(',')}]`
  } else {
    const record = object(value, 'value')
    result = `{${Object.keys(record).sort().map((key) => `${JSON.stringify(key)}:${canonical(record[key], ancestors)}`).join(',')}}`
  }
  ancestors.delete(value)
  return result
}

function same(left: unknown, right: unknown) { return canonical(left) === canonical(right) }
function copy<T>(value: T): T { return JSON.parse(canonical(value)) as T }

function event(value: unknown) {
  const record = object(value, 'event')
  keys(record, ['id', 'supplierId', 'date', 'type', 'text', 'evidenceIds', 'rung'], [], 'event')
  id(record.id, 'event id')
  id(record.supplierId, 'event supplier')
  calendarDate(record.date, 'event date')
  string(record.text, 'event text')
  strings(record.evidenceIds, 'event evidence', true)
  requireThat(eventTypes.has(record.type as string), 'unsupported event type')
  requireThat([1, 2, 3, 4, 5].includes(record.rung as number), 'unsupported event rung')
  return record
}

function supplierField(value: unknown, field: string) {
  const record = object(value, `supplier ${field}`)
  const required = field === 'lastRound' ? ['date', 'stage', 'amount', 'evidenceIds']
    : field === 'headlineMetric' ? ['label', 'value', 'period', 'evidenceIds'] : ['status', 'evidenceIds']
  const optional = field === 'lastRound' ? ['lead', 'valuation']
    : field === 'ownership' ? ['acquirer', 'announced', 'closed', 'price', 'relationship'] : []
  keys(record, required, optional, `supplier ${field}`)
  for (const key of Object.keys(record)) if (key !== 'evidenceIds') string(record[key], `supplier ${field}.${key}`)
  strings(record.evidenceIds, 'supplier evidence', true)
  if (field === 'lastRound') {
    const date = record.date as string
    if (/^\d{4}-\d{2}$/.test(date)) calendarDate(`${date}-01`, 'funding date')
    else calendarDate(date, 'funding date')
  }
  for (const date of ['announced', 'closed']) if (record[date] !== undefined) calendarDate(record[date], `ownership ${date}`)
  return record
}

function evidenceRecord(value: unknown) {
  const record = object(value, 'evidence')
  const required = ['id', 'title', 'organization', 'publicationDate', 'economicPeriod', 'canonicalUrl', 'excerpt', 'sourceClass', 'interpretation', 'limitations', 'conflictingEvidenceIds', 'artifactLabel', 'tags']
  keys(record, required, ['sourceAttributions', 'retrievedAt', 'retrieval'], 'evidence')
  id(record.id, 'evidence id')
  for (const key of ['title', 'organization', 'economicPeriod', 'canonicalUrl', 'excerpt', 'artifactLabel']) string(record[key], `evidence ${key}`)
  for (const key of ['interpretation', 'limitations']) string(record[key], `evidence ${key}`, true)
  url(record.canonicalUrl, 'evidence URL')
  calendarDate(record.publicationDate, 'evidence publication date')
  if (record.retrievedAt !== undefined) calendarDate(record.retrievedAt, 'evidence retrieval date')
  if (record.retrieval !== undefined) {
    const retrieval = object(record.retrieval, 'evidence retrieval')
    keys(retrieval, ['finalUrl', 'sha256', 'fetchedAt'], ['locator'], 'evidence retrieval')
    url(retrieval.finalUrl, 'retrieval URL')
    hash(retrieval.sha256, 'retrieval hash')
    timestamp(retrieval.fetchedAt, 'retrieval time')
    if (retrieval.locator !== undefined) string(retrieval.locator, 'retrieval locator')
  }
  if (record.sourceAttributions !== undefined) {
    requireThat(Array.isArray(record.sourceAttributions), 'source attributions must be an array')
    for (const entry of record.sourceAttributions) {
      const attribution = object(entry, 'source attribution')
      keys(attribution, ['organization', 'publicationDate', 'economicPeriod'], ['canonicalUrl'], 'source attribution')
      string(attribution.organization, 'attribution organization')
      string(attribution.economicPeriod, 'attribution period')
      calendarDate(attribution.publicationDate, 'attribution publication date')
      if (attribution.canonicalUrl !== undefined) url(attribution.canonicalUrl, 'attribution URL')
    }
  }
  requireThat(['FILING', 'IR', 'TRANSCRIPT', 'OFFICIAL', 'INDEPENDENT', 'OWN_ANALYSIS', 'VENDOR-SURVEY', 'VENDOR-RESEARCH'].includes(record.sourceClass as string), 'unsupported evidence source class')
  strings(record.conflictingEvidenceIds, 'conflicting evidence')
  strings(record.tags, 'evidence tags')
  canonical(record)
  return record
}

function index<T extends { id: string }>(values: readonly T[], label: string) {
  requireThat(Array.isArray(values), `${label} inventory is missing`)
  const result = new Map<string, T>()
  for (const value of values) {
    const record = object(value, label)
    id(record.id, `${label} id`)
    requireThat(!result.has(value.id), `duplicate ${label} inventory id ${value.id}`)
    result.set(value.id, value)
  }
  return result
}

/**
 * Fails the whole bundle before any projection is returned. This validates structure and
 * exact raw before-values; the gate authenticates hashes, review bytes and the policy manifest.
 * A syntactically valid admission string alone is not proof of independent review.
 */
export function validateBundle(bundle: unknown, expectedPolicySha256: string | null, inventories: FactualCorrectionInventories, expectedReviewPolicySha256ByGroup?: FactualCorrectionReviewPolicyMap): asserts bundle is FactualCorrectionBundle {
  const value = object(bundle, 'bundle')
  keys(value, ['schemaVersion', 'enabled', 'policySha256', 'checkedAt', 'groups'], [], 'bundle')
  requireThat(value.schemaVersion === 1 && typeof value.enabled === 'boolean' && Array.isArray(value.groups), 'unsupported bundle schema')
  if (!value.enabled) {
    requireThat(value.policySha256 === null && value.checkedAt === null && value.groups.length === 0, 'disabled bundle must be empty')
    return
  }
  hash(expectedPolicySha256, 'expected policy')
  hash(value.policySha256, 'policy')
  requireThat(value.policySha256 === expectedPolicySha256, 'stale policy')
  timestamp(value.checkedAt, 'checkedAt')
  requireThat(value.groups.length > 0, 'enabled bundle has no groups')
  const reviewPolicies = object(expectedReviewPolicySha256ByGroup, 'expected group review policies')
  for (const [groupId, policy] of Object.entries(reviewPolicies)) {
    id(groupId, 'expected review group id')
    hash(policy, `expected review policy for ${groupId}`)
  }
  requireThat(Object.keys(reviewPolicies).length === value.groups.length, 'expected review group inventory differs')
  const events = index(inventories.events, 'event')
  const suppliers = index(inventories.suppliers, 'supplier')
  const evidence = index(inventories.evidence, 'evidence')
  const groupIds = new Set<string>()
  const targetIds = new Set<string>()
  for (const entry of value.groups) {
    const group = object(entry, 'group')
    keys(group, ['id', 'supplierId', 'reasonCode', 'date', 'note', 'targets', 'admission'], ['reviewScope'], 'group')
    const publisherDisclosure = Object.hasOwn(group, 'reviewScope')
    requireThat(!publisherDisclosure || group.reviewScope === publisherDisclosureScope, 'unsupported group review scope')
    id(group.id, 'group id')
    id(group.supplierId, 'group supplier')
    requireThat(!groupIds.has(group.id), `duplicate group ${group.id}`)
    groupIds.add(group.id)
    requireThat(suppliers.has(group.supplierId), `missing group supplier ${group.supplierId}`)
    string(group.reasonCode, 'reason code')
    string(group.note, 'note')
    requireThat(!group.note.includes('{date}') && !group.note.includes('[publication date]'), 'undated note template')
    calendarDate(group.date, 'correction date')
    requireThat(group.date <= value.checkedAt.slice(0, 10), 'correction date is after check date')
    const admission = object(group.admission, 'admission')
    keys(admission, ['candidateSha256', 'evidenceSetSha256', 'policySha256', 'admittedAt', 'reviewSha256', 'result', ...(publisherDisclosure ? ['reviewScope'] : [])], [], 'admission')
    requireThat(!publisherDisclosure || admission.reviewScope === publisherDisclosureScope, 'publisher disclosure admission scope differs')
    for (const key of ['candidateSha256', 'evidenceSetSha256', 'policySha256', 'reviewSha256']) hash(admission[key], key)
    requireThat(Object.hasOwn(reviewPolicies, group.id), `missing expected review policy for ${group.id}`)
    requireThat(admission.result === 'accepted' && admission.policySha256 === reviewPolicies[group.id], 'missing accepted current group-policy admission')
    timestamp(admission.admittedAt, 'admittedAt')
    requireThat(Date.parse(admission.admittedAt) <= Date.parse(value.checkedAt), 'admission is after check time')
    requireThat(group.date >= admission.admittedAt.slice(0, 10), 'correction predates admission')
    requireThat(Array.isArray(group.targets) && group.targets.length > 0, 'group targets are missing')
    requireThat(!publisherDisclosure || group.supplierId === 'xage' && group.targets.length === 1, 'publisher disclosure requires one exact Xage target')
    for (const targetEntry of group.targets) {
      const target = object(targetEntry, 'target')
      keys(target, ['targetId', 'operation', 'original', 'originalSha256', 'proposedValue'], [], 'target')
      string(target.targetId, 'target id')
      const parts = target.targetId.split(':')
      requireThat(parts.length === (parts[0] === 'supplier' ? 3 : 2) && ['event', 'supplier', 'evidence'].includes(parts[0]), 'unsupported target id')
      id(parts[1], 'target record id')
      requireThat(!targetIds.has(target.targetId), `duplicate target ${target.targetId}`)
      targetIds.add(target.targetId)
      hash(target.originalSha256, 'original hash')
      requireThat(publisherDisclosure ? target.operation === 'reclassify_publisher_disclosure'
        : target.operation === 'replace' || target.operation === 'withdraw', 'unsupported target operation for review scope')
      requireThat(!publisherDisclosure || target.targetId === 'evidence:TR-xage-1', 'publisher disclosure target is not allowed')
      requireThat(target.operation !== 'withdraw' || (parts[0] === 'event' && target.proposedValue === null), 'only complete events can be withdrawn')
      if (parts[0] === 'event') {
        const original = event(target.original)
        requireThat(original.id === parts[1] && original.supplierId === group.supplierId, 'event identity does not match group')
        requireThat(events.has(parts[1]) && same(events.get(parts[1]), original), `event before-value differs: ${parts[1]}`)
        if (target.operation === 'replace') {
          const proposed = event(target.proposedValue)
          requireThat(['id', 'supplierId', 'type', 'rung'].every((key) => same(original[key], proposed[key])), 'event replacement changes identity, type or rung')
        }
      } else if (parts[0] === 'supplier') {
        requireThat(parts[1] === group.supplierId && supplierFields.has(parts[2]) && target.operation === 'replace', 'supplier field is not allowed')
        supplierField(target.original, parts[2])
        supplierField(target.proposedValue, parts[2])
        requireThat(same((suppliers.get(parts[1]) as unknown as ObjectValue)[parts[2]], target.original), `supplier before-value differs: ${target.targetId}`)
      } else {
        requireThat(target.operation === 'replace' || publisherDisclosure && target.operation === 'reclassify_publisher_disclosure', 'evidence cannot be withdrawn')
        const original = evidenceRecord(target.original)
        const proposed = evidenceRecord(target.proposedValue)
        requireThat(original.id === parts[1] && proposed.id === parts[1], 'evidence identity does not match target')
        requireThat(evidence.has(parts[1]) && same(evidence.get(parts[1]), original), `evidence before-value differs: ${parts[1]}`)
        if (publisherDisclosure) {
          requireThat(target.targetId === 'evidence:TR-xage-1' && target.originalSha256 === publisherDisclosureOriginalSha256
            && original.organization === 'Yahoo Finance' && original.canonicalUrl === publisherDisclosureUrl,
          'publisher disclosure target or immutable original differs')
          requireThat(original.sourceClass === 'INDEPENDENT' && proposed.sourceClass === 'OFFICIAL'
            && proposed.limitations === publisherDisclosureLimitations, 'publisher disclosure transition or limitations differs')
          requireThat(same(Object.keys(original).sort(), Object.keys(proposed).sort()), 'publisher disclosure record shape differs')
        }
        const allowed = publisherDisclosure ? new Set(['sourceClass', 'limitations']) : evidenceChanges
        const unchanged = new Set([...Object.keys(original), ...Object.keys(proposed)].filter((key) => !allowed.has(key)))
        requireThat([...unchanged].every((key) => Object.hasOwn(original, key) === Object.hasOwn(proposed, key) && (!Object.hasOwn(original, key) || same(original[key], proposed[key]))), 'evidence replacement changes protected metadata')
      }
    }
  }
}

function targets(bundle: FactualCorrectionBundle) {
  return new Map(bundle.groups.flatMap((group) => group.targets.map((target) => [target.targetId, target] as const)))
}

export function projectEvents(inventories: FactualCorrectionInventories, bundle: unknown, expectedPolicySha256: string | null, expectedReviewPolicySha256ByGroup?: FactualCorrectionReviewPolicyMap): TrackerEvent[] {
  validateBundle(bundle, expectedPolicySha256, inventories, expectedReviewPolicySha256ByGroup)
  const changes = targets(bundle)
  return inventories.events.flatMap((record) => {
    const target = changes.get(`event:${record.id}`)
    if (target?.operation === 'withdraw') return []
    return [copy(target ? target.proposedValue as TrackerEvent : record)]
  })
}

export function projectSuppliers(inventories: FactualCorrectionInventories, bundle: unknown, expectedPolicySha256: string | null, expectedReviewPolicySha256ByGroup?: FactualCorrectionReviewPolicyMap): TrackerSupplier[] {
  validateBundle(bundle, expectedPolicySha256, inventories, expectedReviewPolicySha256ByGroup)
  const changes = targets(bundle)
  return inventories.suppliers.map((record) => {
    const result = copy(record)
    for (const field of ['lastRound', 'headlineMetric', 'ownership'] as const) {
      const target = changes.get(`supplier:${record.id}:${field}`)
      if (target) Object.assign(result, { [field]: copy(target.proposedValue) })
    }
    return result
  })
}

export function projectEvidence(inventories: FactualCorrectionInventories, bundle: unknown, expectedPolicySha256: string | null, expectedReviewPolicySha256ByGroup?: FactualCorrectionReviewPolicyMap): EvidenceRecord[] {
  validateBundle(bundle, expectedPolicySha256, inventories, expectedReviewPolicySha256ByGroup)
  const changes = targets(bundle)
  return inventories.evidence.map((record) => copy(changes.get(`evidence:${record.id}`)?.proposedValue as EvidenceRecord ?? record))
}
