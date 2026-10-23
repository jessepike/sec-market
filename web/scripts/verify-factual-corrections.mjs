// Build consistency checks. Semantic admission is replayed by the independent
// Python gate against the immutable archive; a JSON seal alone is not that proof.
import { readFileSync, existsSync } from 'node:fs'
import { resolve } from 'node:path'
import { createHash } from 'node:crypto'

const canonical = value => Array.isArray(value) ? '[' + value.map(canonical).join(',') + ']' : value && typeof value === 'object' ? '{' + Object.keys(value).sort().map(k => JSON.stringify(k) + ':' + canonical(value[k])).join(',') + '}' : JSON.stringify(value)
const digest = value => createHash('sha256').update(Buffer.isBuffer(value) ? value : canonical(value)).digest('hex')
const equal = (a, b) => canonical(a) === canonical(b)
const requireThat = (condition, reason) => { if (!condition) throw new Error(`Factual correction build refused: ${reason}`) }
const reviewChecks = ['entity', 'value', 'currency_units', 'period_date', 'qualifiers', 'event_status', 'source_support'].sort()
const roleScope = 'publisher_disclosure_only'
const roleChecks = ['class_transition', 'limitations_scope', 'literal_disclosure', 'publisher_source_binding', 'release_attribution', 'target_identity', 'unchanged_claims_and_history'].sort()
const roleUrl = 'https://finance.yahoo.com/news/xage-security-hits-record-growth-120000615.html'
const roleOriginalHash = '62bb8bcce0698b5f164867d9bc070be77ee4eebde095947dd96eb8a693d0d6fb'
const roleProposedHash = '86b06657bb1139a5d98d293b5599590539baec7e099b59294a3a3e7e0001fe76'
const roleTransition = { targetId: 'evidence:TR-xage-1', originalSha256: roleOriginalHash, from: 'INDEPENDENT', to: 'OFFICIAL', mutableFields: ['limitations', 'sourceClass'] }
const roleQuotes = {
  publisher_paid_disclosure: 'This is a paid press release. Contact the press release distributor directly with any inquiries.',
  issuer_attributed_dateline: 'PALO ALTO, Calif., March 18, 2026 (GLOBE NEWSWIRE) -- Xage Security',
  article_issuer_byline_context: 'Xage Security March 18, 2026 7 min read',
}
const shaShape = /^[a-f0-9]{64}$/
const exactKeys = (value, keys) => value && typeof value === 'object' && !Array.isArray(value) && equal(Object.keys(value).sort(), [...keys].sort())
const scoped = group => Object.hasOwn(group, 'reviewScope')
const validUtc = value => typeof value === 'string' && /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$/.test(value) && Number.isFinite(Date.parse(value)) && new Date(value).toISOString().slice(0, 10) === value.slice(0, 10)

function verifyScope(group, originals, market) {
  if (!scoped(group)) {
    requireThat(group.targets.every(target => ['replace', 'withdraw'].includes(target.operation)), 'operation requires its explicit review scope')
    for (const target of group.targets.filter(target => target.targetId.startsWith('evidence:') && target.operation === 'replace')) {
      const allowed = ['title', 'publicationDate', 'economicPeriod', 'excerpt', 'limitations']
      const protectedKeys = [...new Set([...Object.keys(target.original), ...Object.keys(target.proposedValue)])].filter(key => !allowed.includes(key))
      requireThat(protectedKeys.every(key => Object.hasOwn(target.original, key) === Object.hasOwn(target.proposedValue, key) && equal(target.original[key], target.proposedValue[key])), 'ordinary evidence replacement changes protected metadata')
    }
    return
  }
  requireThat(group.reviewScope === roleScope, 'unknown review scope')
  requireThat(exactKeys(group, ['id', 'supplierId', 'reasonCode', 'noteTemplate', 'targets', 'sources', 'reviewScope', 'disclosureQuotes']), 'publisher disclosure group schema differs')
  requireThat(group.supplierId === 'xage' && Array.isArray(group.targets) && group.targets.length === 1, 'publisher disclosure requires one exact Xage target')
  const target = group.targets[0]
  requireThat(exactKeys(target, ['targetId', 'operation', 'original', 'originalSha256', 'proposedValue']) && target.targetId === roleTransition.targetId && target.operation === 'reclassify_publisher_disclosure', 'publisher disclosure operation or target differs')
  const original = originals.evidence.find(record => record.id === 'TR-xage-1')
  requireThat(original && equal(target.original, original) && target.originalSha256 === roleOriginalHash && digest(target.original) === roleOriginalHash, 'publisher disclosure immutable original differs')
  requireThat(target.original.sourceClass === 'INDEPENDENT' && target.original.organization === 'Yahoo Finance' && target.original.canonicalUrl === roleUrl && target.proposedValue?.sourceClass === 'OFFICIAL' && digest(target.proposedValue) === roleProposedHash, 'publisher disclosure proposed transition differs')
  requireThat(equal(Object.keys(target.original).sort(), Object.keys(target.proposedValue).sort()) && Object.keys(target.original).filter(key => !roleTransition.mutableFields.includes(key)).every(key => equal(target.original[key], target.proposedValue[key])), 'publisher disclosure changes protected fields')
  requireThat(Array.isArray(group.sources) && group.sources.length === 1, 'publisher disclosure requires its exact publisher source')
  const source = group.sources[0]
  requireThat(exactKeys(source, ['evidenceId', 'sourceId', 'url', 'observationId', 'body', 'fetchedAt', 'proofScope', 'visibleText', 'disclosureQuoteIds']) && source.evidenceId === 'TR-xage-1' && source.sourceId === 'xage:citation:TR-xage-1' && source.url === roleUrl && source.proofScope === roleScope, 'publisher disclosure source binding or scope differs')
  const configured = market.sources.filter(candidate => candidate.id === source.sourceId)
  requireThat(configured.length === 1 && configured[0].supplierId === 'xage' && configured[0].kind === 'citation' && configured[0].family === 'citation_integrity' && configured[0].registration === 'verified' && configured[0].url === roleUrl && configured[0].evidenceId === source.evidenceId && equal(configured[0].allowedHosts, ['finance.yahoo.com']), 'publisher disclosure configured source differs')
  const supplier = market.suppliers.filter(candidate => candidate.id === 'xage')
  requireThat(supplier.length === 1 && supplier[0].sourceIds?.includes(source.sourceId), 'publisher disclosure supplier/source join differs')
  requireThat(shaShape.test(source.observationId) && exactKeys(source.body, ['key', 'sha256', 'bytes']) && shaShape.test(source.body.sha256) && source.body.key === `objects/${source.body.sha256}` && Number.isSafeInteger(source.body.bytes) && source.body.bytes > 0, 'publisher disclosure body provenance differs')
  requireThat(validUtc(source.fetchedAt), 'publisher disclosure fetch time differs')
  const visible = source.visibleText
  requireThat(exactKeys(visible, ['rulesVersion', 'sha256', 'chars']) && visible.rulesVersion === 'page-all-visible-text-whitespace-1' && shaShape.test(visible.sha256) && Number.isSafeInteger(visible.chars) && visible.chars >= 100 && visible.chars <= Math.min(30000, market.model.maxDocumentChars), 'publisher disclosure whole-text descriptor differs')
  requireThat(Array.isArray(group.disclosureQuotes) && group.disclosureQuotes.length === 3 && equal(source.disclosureQuoteIds, group.disclosureQuotes.map(quote => quote.id)) && equal([...source.disclosureQuoteIds].sort(), ['article_issuer_byline_context', 'issuer_attributed_dateline', 'publisher_paid_disclosure']), 'publisher disclosure quote inventory differs')
  for (const quote of group.disclosureQuotes) {
    requireThat(Object.hasOwn(roleQuotes, quote.id) && quote.text === roleQuotes[quote.id], 'publisher disclosure literal quote differs')
    requireThat(exactKeys(quote, ['id', 'text', 'normalizedWholePageStart', 'normalizedWholePageEnd', 'textSha256', 'literalInWholePageText', 'literalInUniqueArticle', 'scope']) && typeof quote.text === 'string' && quote.text.length > 0 && quote.textSha256 === digest(Buffer.from(quote.text)) && Number.isSafeInteger(quote.normalizedWholePageStart) && Number.isSafeInteger(quote.normalizedWholePageEnd) && quote.normalizedWholePageStart >= 0 && quote.normalizedWholePageEnd <= visible.chars && quote.normalizedWholePageEnd - quote.normalizedWholePageStart === [...quote.text].length && quote.literalInWholePageText === true && quote.literalInUniqueArticle === true && quote.scope === 'publication role and attribution only', 'publisher disclosure quote descriptor differs')
  }
}

// Derive the complete review binding here, independently of the Python gate.
// Global inventory changes do not relabel an unchanged group's admission.
function reviewPolicy(group, market, baselineSha256) {
  const suppliers = market.suppliers.filter(supplier => supplier.id === group.supplierId)
  requireThat(suppliers.length === 1, 'review supplier missing or duplicate')
  const supplier = suppliers[0]
  requireThat(['id', 'name', 'kind'].every(key => typeof supplier[key] === 'string' && supplier[key]) && Array.isArray(supplier.aliases) && supplier.aliases.every(alias => typeof alias === 'string'), 'review supplier identity incomplete')
  const sources = group.sources.map(source => {
    const matches = market.sources.filter(configured => configured.id === source.sourceId)
    requireThat(matches.length === 1, 'review source missing or duplicate')
    return matches[0]
  })
  const basis = {
    schemaVersion: 1, rulesVersion: 'dated-factual-correction-review-1', baselineSha256,
    candidateSha256: digest(group),
    supplier: { id: supplier.id, name: supplier.name, aliases: supplier.aliases, kind: supplier.kind },
    sources,
    model: { provider: market.model.provider, allowApiBilling: market.model.allowApiBilling, maxDocumentChars: market.model.maxDocumentChars },
    freshnessHours: 30, checks: reviewChecks,
  }
  if (scoped(group)) {
    requireThat(group.reviewScope === roleScope, 'unknown review scope')
    Object.assign(basis, { rulesVersion: 'dated-publisher-disclosure-classification-1', reviewScope: roleScope,
      allowedTransition: roleTransition, checks: roleChecks })
  }
  return digest(basis)
}

export function verifyFactualCorrections(web) {
  const file = resolve(web, 'src/data/generated/factualCorrections.json')
  const contractPath = resolve(web, '../contracts/factual-corrections.json')
  // Older isolated release fixtures predate this feature. Actual builds must
  // include both policy and projection, including the disabled development view.
  if (!existsSync(file) && !existsSync(contractPath)) return { enabled: false }
  const read = path => JSON.parse(readFileSync(path, 'utf8'))
  const requests = read(contractPath)
  requireThat(requests.baseline?.path === 'contracts/factual-baseline.json', 'unexpected baseline path')
  const baselineBytes = readFileSync(resolve(web, '..', requests.baseline.path))
  requireThat(digest(baselineBytes) === requests.baseline.sha256, 'baseline bytes changed')
  const baseline = JSON.parse(baselineBytes)
  const originals = read(resolve(web, 'src/data/tracker/originals.json'))
  requireThat(baseline.schemaVersion === 1 && equal(Object.keys(originals).sort(), ['events', 'evidence', 'suppliers']), 'original inventory schema differs')
  for (const [kind, records] of Object.entries(originals)) {
    requireThat(Array.isArray(records) && new Set(records.map(r => r.id)).size === records.length, 'duplicate original identity')
    requireThat(equal(Object.fromEntries(records.map(record => [record.id, digest(record)])), baseline.inventories[kind]), `unreviewed ${kind} original edit`)
  }
  const market = read(resolve(web, '../contracts/market.json'))
  for (const group of requests.groups) verifyScope(group, originals, market)
  const policySha256 = digest({ marketSha256: digest(market), requestsSha256: digest(requests), baselineSha256: requests.baseline.sha256 })
  const groupIds = requests.groups.map(group => group.id)
  const targetIds = requests.groups.flatMap(group => group.targets.map(target => target.targetId))
  requireThat(new Set(groupIds).size === groupIds.length && new Set(targetIds).size === targetIds.length, 'duplicate requested group or target')
  const expected = read(resolve(web, 'src/data/tracker/factualCorrectionPolicy.json'))
  const sourceEvidenceIds = Object.fromEntries(requests.groups.map(group => [group.id, group.sources.map(source => source.evidenceId)]))
  const reviewPolicySha256ByGroup = Object.fromEntries(requests.groups.map(group => [group.id, reviewPolicy(group, market, requests.baseline.sha256)]))
  requireThat(equal(expected, { schemaVersion: 1, policySha256, groupIds, targetIds, sourceEvidenceIds, reviewPolicySha256ByGroup }), 'policy stamp differs')
  const bytes = readFileSync(file), bundle = JSON.parse(bytes)
  requireThat(bundle.schemaVersion === 1 && typeof bundle.enabled === 'boolean', 'projection schema differs')
  if (!bundle.enabled) {
    requireThat(equal(bundle, { schemaVersion: 1, enabled: false, policySha256: null, checkedAt: null, groups: [] }), 'disabled projection contains corrections')
    return { enabled: false, policySha256, fileSha256: digest(bytes) }
  }
  requireThat(bundle.policySha256 === policySha256 && equal(bundle.groups.map(group => group.id), groupIds), 'stale policy or incomplete groups')
  requireThat(Number.isFinite(Date.parse(bundle.checkedAt)) && bundle.checkedAt.endsWith('Z'), 'invalid check time')
  for (const [index, group] of bundle.groups.entries()) {
    const request = requests.groups[index]
    const role = scoped(request)
    requireThat(exactKeys(group, ['id', 'supplierId', 'reasonCode', 'date', 'note', 'targets', 'admission', ...(role ? ['reviewScope'] : [])]) && (!role || group.reviewScope === roleScope), 'public group review scope or schema differs')
    requireThat(group.supplierId === request.supplierId && group.reasonCode === request.reasonCode && equal(group.targets, request.targets), 'target before/after policy differs')
    requireThat(/^\d{4}-\d{2}-\d{2}$/.test(group.date) && new Date(group.date).toISOString().slice(0, 10) === group.date && group.date <= bundle.checkedAt.slice(0, 10), 'invalid publication date')
    requireThat(group.note === request.noteTemplate.replace('{date}', group.date), 'correction note differs from reviewed template')
    const admission = group.admission
    requireThat(exactKeys(admission, ['result', 'policySha256', 'candidateSha256', 'evidenceSetSha256', 'admittedAt', 'reviewSha256', ...(role ? ['reviewScope'] : [])]) && (!role || admission.reviewScope === roleScope), 'public admission review scope or schema differs')
    requireThat(admission?.result === 'accepted' && admission.policySha256 === reviewPolicySha256ByGroup[group.id] && admission.candidateSha256 === digest(request) && admission.evidenceSetSha256 === digest(request.sources) && /^[a-f0-9]{64}$/.test(admission.reviewSha256 ?? ''), 'unbound admission metadata')
    requireThat(Number.isFinite(Date.parse(admission.admittedAt)) && admission.admittedAt.endsWith('Z') && Date.parse(admission.admittedAt) <= Date.parse(bundle.checkedAt) && admission.admittedAt.slice(0, 10) <= group.date, 'future admission')
    if (role) requireThat(validUtc(admission.admittedAt) && validUtc(bundle.checkedAt) && request.sources.every(source => Date.parse(admission.admittedAt) >= Date.parse(source.fetchedAt) && Date.parse(admission.admittedAt) - Date.parse(source.fetchedAt) <= 30 * 3600000), 'publisher disclosure admission outside original source window')
    for (const target of group.targets) requireThat(digest(target.original) === target.originalSha256, 'wrong original hash')
  }
  const seal = read(file.replace(/\.json$/, '.seal.json'))
  requireThat(seal.schemaVersion === 1 && seal.fileSha256 === digest(bytes) && seal.policySha256 === policySha256 && equal(seal.groupIds, groupIds) && equal(seal.targetIds, targetIds), 'projection differs from gate seal')
  requireThat(Array.isArray(seal.newGroupIds) && new Set(seal.newGroupIds).size === seal.newGroupIds.length && seal.newGroupIds.every(id => groupIds.includes(id)), 'invalid new correction inventory')
  requireThat(/^\d{4}-\d{2}-\d{2}$/.test(seal.publicationDate) && seal.publicationDate === bundle.checkedAt.slice(0, 10) && bundle.groups.filter(group => seal.newGroupIds.includes(group.id)).every(group => group.date === seal.publicationDate), 'new correction date differs')
  return { enabled: true, policySha256, fileSha256: digest(bytes), groupIds, targetIds, newGroupIds: seal.newGroupIds, publicationDate: seal.publicationDate }
}
