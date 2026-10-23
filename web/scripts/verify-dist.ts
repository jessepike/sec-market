/**
 * Post-build dist verification (spec §6, check 11).
 *
 * Runs last in `npm run build`, after generate-feed.ts. Checks the emitted
 * files themselves rather than the data that produced them — verify-issue.ts
 * owns the data checks, this owns "did the build actually write what it was
 * supposed to write."
 *
 * Every check below is exported as `(distDir, issuesList) => CheckResult`
 * rather than reading module-level `dist`/`issues` constants directly, so
 * tests/dist-fixtures.test.ts can run the real writers (generate-feed.ts)
 * into a temporary directory for a small fixture and then run these same
 * checks against that directory — the real dist pipeline, not a stand-in.
 */
import assert from 'node:assert/strict'
import { existsSync, readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'
import { emptyCorrectionHistorySources, factualCorrectionFeedText, factualCorrectionHistory, publicCorrectionsJsonPayload } from '../src/data/factualCorrectionHelpers.ts'
import type { CorrectionHistorySources } from '../src/data/factualCorrectionHelpers.ts'
import { factualCorrectionBundle, factualCorrectionGroups, factualCorrectionSourceEvidenceIds } from '../src/data/tracker/correctionData.ts'
import type { FactualCorrectionBundle, FactualCorrectionGroup } from '../src/data/tracker/factualCorrections.ts'
import { corrections } from '../src/data/corrections.ts'
import { evidenceById } from '../src/data/evidence.ts'
import {
  archiveEntriesNewestFirst,
  feedIssuesNewestFirst,
  issueEvidenceIds,
  toRfc822,
} from '../src/data/issueHelpers.ts'
import { issues } from '../src/data/issues/index.ts'
import { SITE_URL } from '../src/data/meta.ts'
import { routesFor } from '../src/data/routes.ts'
import { runStatus } from '../src/data/runStatus.ts'
import { trackerDomains } from '../src/data/tracker/domains.ts'
import { trackerJsonPayload } from '../src/data/tracker/jsonExport.ts'
import { trackerSuppliers } from '../src/data/tracker/suppliers.ts'
import type { Correction, EvidenceRecord, Issue } from '../src/data/types.ts'
import type { RunStatus } from '../src/data/runStatus.ts'
import type { TrackerDomain } from '../src/data/tracker/domains.ts'
import type { TrackerSupplier } from '../src/data/tracker/suppliers.ts'

const webRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const SOURCE_LOCK_PATH = resolve(webRoot, 'src/data/issues/issues.lock.json')

export interface CheckResult {
  name: string
  pass: boolean
  detail?: string
}

function runCheck(name: string, fn: () => string | void): CheckResult {
  try {
    const detail = fn()
    return { name, pass: true, detail: detail ?? undefined }
  } catch (error) {
    const detail = error instanceof Error ? error.message : String(error)
    return { name, pass: false, detail }
  }
}

function routeHtmlPath(distDir: string, path: string): string {
  return path === '/' ? resolve(distDir, 'index.html') : resolve(distDir, path.replace(/^\//, ''), 'index.html')
}

// --- 11a: every route's HTML file exists ------------------------------------

export function checkEveryRouteHtmlExists(distDir: string, issuesList: Issue[]): CheckResult {
  return runCheck('11a every-route-html-exists', () => {
    const routesList = routesFor(issuesList)
    for (const routeEntry of routesList) {
      const path = routeHtmlPath(distDir, routeEntry.path)
      if (!existsSync(path)) {
        throw new Error(`route "${routeEntry.path}" is missing its HTML file at ${path}`)
      }
    }
    return `${routesList.length} route HTML file(s) present`
  })
}

// --- 11b: every issue JSON copy exists, is well-formed, and identity-checked

export function checkEveryIssueJsonExists(
  distDir: string,
  issuesList: Issue[],
  evidenceByIdMap: Record<string, EvidenceRecord>,
): CheckResult {
  return runCheck('11b every-issue-json-exists', () => {
    for (const issue of issuesList) {
      const path = resolve(distDir, 'issues', `${issue.id}.json`)
      if (!existsSync(path)) {
        throw new Error(`issue "${issue.id}" is missing its JSON copy at ${path}`)
      }
      const parsed = JSON.parse(readFileSync(path, 'utf8'))
      if (!parsed.issue || !Array.isArray(parsed.evidence)) {
        throw new Error(`issue "${issue.id}" JSON copy does not have the shape { issue, evidence: [] }`)
      }
      if (parsed.issue.id !== issue.id) {
        throw new Error(
          `dist/issues/${issue.id}.json has issue.id "${parsed.issue.id}", expected "${issue.id}" (from the filename)`,
        )
      }
      // Full identity: the written "issue" object must deep-equal the source
      // issue (round-tripped through JSON so `undefined`-free comparison
      // matches what was actually written) — not just its id and evidence
      // count.
      const expectedIssue = JSON.parse(JSON.stringify(issue))
      try {
        assert.deepStrictEqual(parsed.issue, expectedIssue)
      } catch (error) {
        throw new Error(
          `dist/issues/${issue.id}.json "issue" does not deep-equal the source issue: ${
            error instanceof Error ? error.message : String(error)
          }`,
        )
      }
      // Full evidence-body identity, in the same order the writer emits
      // (issueEvidenceIds' order via evidenceByIdMap), round-tripped through
      // JSON — not just an id-set comparison, which could pass while an
      // evidence record's excerpt, receipt, or any other field silently
      // diverged from the source that produced it.
      const expectedEvidence = issueEvidenceIds(issue).map((id) => {
        const record = evidenceByIdMap[id]
        if (!record) {
          throw new Error(`issue "${issue.id}" cites evidence id "${id}" which does not resolve`)
        }
        return record
      })
      const expectedEvidenceRoundTripped = JSON.parse(JSON.stringify(expectedEvidence))
      try {
        assert.deepStrictEqual(parsed.evidence, expectedEvidenceRoundTripped)
      } catch (error) {
        throw new Error(
          `dist/issues/${issue.id}.json "evidence" does not deep-equal the source evidence records in the expected order: ${
            error instanceof Error ? error.message : String(error)
          }`,
        )
      }
    }
    return `${issuesList.length} issue JSON file(s) present, well-formed, and identity-checked (issue + full evidence bodies)`
  })
}

// --- 11c: issues/index.json exists, ordered, and row-identical -------------

export function checkIssuesIndexJsonExists(distDir: string, issuesList: Issue[]): CheckResult {
  return runCheck('11c issues-index-json-exists', () => {
    const path = resolve(distDir, 'issues/index.json')
    if (!existsSync(path)) {
      throw new Error(`dist/issues/index.json is missing`)
    }
    const parsed = JSON.parse(readFileSync(path, 'utf8'))
    if (!Array.isArray(parsed)) {
      throw new Error('dist/issues/index.json does not parse to an array')
    }
    if (parsed.length !== issuesList.length) {
      throw new Error(`dist/issues/index.json has ${parsed.length} entries, expected ${issuesList.length}`)
    }
    // The archive is newest-first; check the full expected row (whatever
    // fields the writer emits, url included), not just id and status.
    const expectedOrder = archiveEntriesNewestFirst(issuesList).map((entry) => ({
      ...entry,
      url: `${SITE_URL}/issues/${entry.id}/`,
    }))
    for (let i = 0; i < expectedOrder.length; i++) {
      try {
        assert.deepStrictEqual(parsed[i], expectedOrder[i])
      } catch (error) {
        throw new Error(
          `dist/issues/index.json entry ${i} does not deep-equal the expected row: ${
            error instanceof Error ? error.message : String(error)
          }`,
        )
      }
    }
    return `${parsed.length} entries in the expected newest-first order, full row identity checked`
  })
}

// --- 11d: feed.xml exists, parses, and every item is identity-checked ------

interface FeedItem {
  guid: string
  pubDate: string
  title: string
  description: string
}

type XmlNode =
  | { type: 'element'; name: string; children: XmlNode[] }
  | { type: 'text'; value: string }

function isNameStartChar(ch: string): boolean {
  return /[A-Za-z_:]/.test(ch)
}

function isNameChar(ch: string): boolean {
  return /[A-Za-z0-9_:.-]/.test(ch)
}

/**
 * Matches one legal entity reference at the start of the given string: one of
 * the five XML predefined entities, or a numeric character reference in
 * decimal (`&#123;`) or hex (`&#x7B;`) form. Anything else starting with "&"
 * — a bare "&", an unknown named entity, an unterminated reference — is not
 * matched and the caller treats that as a well-formedness violation.
 */
const ENTITY_REF_PATTERN = /^&(amp|lt|gt|quot|apos|#[0-9]+|#x[0-9A-Fa-f]+);/

/**
 * Scans a run of character data (text found between tags) for every "&" and
 * requires each one to begin one of the five predefined entities or a
 * numeric character reference — a bare "&" or an unrecognised entity name
 * throws, naming the offending position, rather than being passed through as
 * literal text the way the tokeniser otherwise treats ordinary characters.
 */
function validateEntities(text: string, sliceStart: number): void {
  let i = 0
  while (i < text.length) {
    const amp = text.indexOf('&', i)
    if (amp === -1) return
    if (!ENTITY_REF_PATTERN.test(text.slice(amp))) {
      throw new Error(
        `dist/feed.xml: invalid entity reference at character ${sliceStart + amp} — not well-formed`,
      )
    }
    i = amp + 1
  }
}

/**
 * Validates the raw attribute region of a tag (everything after the tag
 * name, up to but not including the trailing "/" of a self-closing tag or
 * the final ">"). Each attribute must be `name="value"` or `name='value'` —
 * a name with no "=", an "=" not followed by a quote character (an unquoted
 * value), or an unterminated quoted value throws, naming the tag and the
 * attribute.
 */
function validateAttributes(raw: string, tagName: string, tagStart: number): void {
  const len = raw.length
  let i = 0
  while (i < len) {
    while (i < len && /\s/.test(raw[i])) i++
    if (i >= len) return
    if (!isNameStartChar(raw[i])) {
      throw new Error(
        `dist/feed.xml: malformed attribute syntax on "<${tagName}" at character ${tagStart} — not well-formed`,
      )
    }
    let nameEnd = i
    while (nameEnd < len && isNameChar(raw[nameEnd])) nameEnd++
    const attrName = raw.slice(i, nameEnd)
    let k = nameEnd
    while (k < len && /\s/.test(raw[k])) k++
    if (raw[k] !== '=') {
      throw new Error(
        `dist/feed.xml: attribute "${attrName}" on "<${tagName}" at character ${tagStart} has no value — not well-formed`,
      )
    }
    k++
    while (k < len && /\s/.test(raw[k])) k++
    const quote = raw[k]
    if (quote !== '"' && quote !== "'") {
      throw new Error(
        `dist/feed.xml: attribute "${attrName}" on "<${tagName}" at character ${tagStart} is not a quoted value — not well-formed`,
      )
    }
    const closeQuote = raw.indexOf(quote, k + 1)
    if (closeQuote === -1) {
      throw new Error(
        `dist/feed.xml: attribute "${attrName}" on "<${tagName}" at character ${tagStart} has an unterminated quoted value — not well-formed`,
      )
    }
    i = closeQuote + 1
  }
}

/**
 * A small hand-written well-formedness XML tokeniser/parser — no package
 * dependency (none is present in node_modules), and generate-feed.ts's own
 * output has a fixed, simple shape (no CDATA, no DTD, no namespaces), so
 * this is enough for what this gate needs. It tokenises tags one at a time,
 * maintains an explicit open-tag stack, and requires every open tag to
 * close in order — a mismatched close, an unmatched close, an unterminated
 * tag, or an unescaped "<" found inside a tag or loose in text content
 * throws rather than silently truncating or ignoring the problem. Unlike a
 * regex-based item scanner, `<item>` blocks are found by walking the parsed
 * tree afterward, not by pattern-matching the raw text. It also requires
 * exactly one root element, named "rss"; rejects non-whitespace text found
 * at the document's root level, outside that element; rejects an entity
 * reference that is not one of the five XML predefined entities or a numeric
 * character reference; and rejects an attribute with no quoted value.
 */
function parseXmlDocument(xml: string): XmlNode[] {
  const len = xml.length
  let pos = 0

  interface Frame {
    name: string
    children: XmlNode[]
  }
  const stack: Frame[] = []
  const root: XmlNode[] = []

  function currentChildren(): XmlNode[] {
    return stack.length > 0 ? stack[stack.length - 1].children : root
  }

  function readTagName(start: number): { name: string; end: number } {
    if (start >= len || !isNameStartChar(xml[start])) {
      throw new Error(`dist/feed.xml: expected a tag name at character ${start} — not well-formed`)
    }
    let i = start
    while (i < len && isNameChar(xml[i])) i++
    return { name: xml.slice(start, i), end: i }
  }

  /**
   * Scans from just after the tag name to the closing '>', rejecting a bare
   * unescaped '<' inside the tag and an unterminated tag; quoted attribute
   * values are skipped whole so a '<' or '>' inside one does not confuse the
   * scan. Once the tag's end is found, the raw attribute region (name to the
   * trailing "/" of a self-closing tag or the final ">") is validated with
   * `validateAttributes`. Returns whether the tag was self-closing ("/>").
   */
  function readTagRest(start: number, tagName: string, tagStart: number): { end: number; selfClosing: boolean } {
    let i = start
    let quote: string | null = null
    while (i < len) {
      const ch = xml[i]
      if (quote) {
        if (ch === quote) quote = null
        i++
        continue
      }
      if (ch === '"' || ch === "'") {
        quote = ch
        i++
        continue
      }
      if (ch === '<') {
        throw new Error(`dist/feed.xml: unescaped "<" inside a tag at character ${i} — not well-formed`)
      }
      if (ch === '>') {
        const selfClosing = i > start && xml[i - 1] === '/'
        const attrEnd = selfClosing ? i - 1 : i
        validateAttributes(xml.slice(start, attrEnd), tagName, tagStart)
        return { end: i + 1, selfClosing }
      }
      i++
    }
    throw new Error(`dist/feed.xml: unterminated tag starting at character ${start} — not well-formed`)
  }

  while (pos < len) {
    const lt = xml.indexOf('<', pos)
    if (lt === -1) {
      const text = xml.slice(pos)
      if (text.trim() !== '') {
        validateEntities(text, pos)
        currentChildren().push({ type: 'text', value: text })
      }
      break
    }
    if (lt > pos) {
      const text = xml.slice(pos, lt)
      validateEntities(text, pos)
      currentChildren().push({ type: 'text', value: text })
    }

    if (xml.startsWith('<?', lt)) {
      const end = xml.indexOf('?>', lt)
      if (end === -1) {
        throw new Error(`dist/feed.xml: unterminated "<?...?>" declaration at character ${lt} — not well-formed`)
      }
      pos = end + 2
      continue
    }
    if (xml.startsWith('<!--', lt)) {
      const end = xml.indexOf('-->', lt)
      if (end === -1) {
        throw new Error(`dist/feed.xml: unterminated comment at character ${lt} — not well-formed`)
      }
      pos = end + 3
      continue
    }
    if (xml[lt + 1] === '/') {
      const { name, end: nameEnd } = readTagName(lt + 2)
      let i = nameEnd
      while (i < len && /\s/.test(xml[i])) i++
      if (xml[i] !== '>') {
        throw new Error(`dist/feed.xml: malformed closing tag "</${name}" at character ${lt} — not well-formed`)
      }
      pos = i + 1
      if (stack.length === 0) {
        throw new Error(`dist/feed.xml: unmatched closing tag "</${name}>" at character ${lt} — not well-formed`)
      }
      const top = stack.pop()!
      if (top.name !== name) {
        throw new Error(
          `dist/feed.xml: closing tag "</${name}>" at character ${lt} does not match open tag "<${top.name}>" — not well-formed`,
        )
      }
      currentChildren().push({ type: 'element', name: top.name, children: top.children })
      continue
    }

    // Opening (or self-closing) tag.
    const { name, end: nameEnd } = readTagName(lt + 1)
    const { end, selfClosing } = readTagRest(nameEnd, name, lt)
    pos = end
    if (selfClosing) {
      currentChildren().push({ type: 'element', name, children: [] })
    } else {
      stack.push({ name, children: [] })
    }
  }

  if (stack.length > 0) {
    throw new Error(
      `dist/feed.xml has ${stack.length} unclosed tag(s), innermost "<${stack[stack.length - 1].name}>" — not well-formed`,
    )
  }

  // Root-level whitespace (formatting between the XML declaration and the
  // root element, or a trailing newline) is stored as an ordinary text node
  // like anywhere else in the tree, so only non-whitespace text at the root
  // counts as stray content outside the document element.
  const strayText = root.find((node) => node.type === 'text' && node.value.trim() !== '')
  if (strayText && strayText.type === 'text') {
    throw new Error(
      `dist/feed.xml has non-whitespace text outside the root element: "${strayText.value.trim()}" — not well-formed`,
    )
  }
  const rootElements = root.filter((node): node is Extract<XmlNode, { type: 'element' }> => node.type === 'element')
  if (rootElements.length !== 1) {
    throw new Error(
      `dist/feed.xml has ${rootElements.length} root element(s), expected exactly one — not well-formed`,
    )
  }
  if (rootElements[0].name !== 'rss') {
    throw new Error(
      `dist/feed.xml root element is "<${rootElements[0].name}>", expected "<rss>" — not well-formed`,
    )
  }

  return root
}

/**
 * Depth-first walk collecting every element named `name`, wherever it is
 * nested in the tree, in document order — throwing if one such element is
 * itself nested inside another of the same name (RSS's `<item>` is never
 * meant to nest).
 */
function collectElements(nodes: XmlNode[], name: string, insideSameName = false): XmlNode[] {
  const found: XmlNode[] = []
  for (const node of nodes) {
    if (node.type !== 'element') continue
    const isMatch = node.name === name
    if (isMatch && insideSameName) {
      throw new Error(`dist/feed.xml has a nested <${name}> — not well-formed`)
    }
    if (isMatch) found.push(node)
    found.push(...collectElements(node.children, name, insideSameName || isMatch))
  }
  return found
}

function elementText(node: XmlNode): string {
  if (node.type !== 'element') return ''
  return node.children
    .filter((child): child is Extract<XmlNode, { type: 'text' }> => child.type === 'text')
    .map((child) => child.value)
    .join('')
}

function childElement(node: XmlNode, name: string): XmlNode | undefined {
  if (node.type !== 'element') return undefined
  return node.children.find((child): child is Extract<XmlNode, { type: 'element' }> => child.type === 'element' && child.name === name)
}

function extractFeedItems(xml: string): FeedItem[] {
  const tree = parseXmlDocument(xml)
  const itemElements = collectElements(tree, 'item')
  return itemElements.map((item, index) => {
    const guidEl = childElement(item, 'guid')
    const pubDateEl = childElement(item, 'pubDate')
    if (!guidEl) {
      throw new Error(`dist/feed.xml <item> block ${index} has no <guid>`)
    }
    if (!pubDateEl) {
      throw new Error(`dist/feed.xml <item> block ${index} has no <pubDate>`)
    }
    return {
      guid: elementText(guidEl).trim(), pubDate: elementText(pubDateEl).trim(),
      title: htmlUnescapeAttr(elementText(childElement(item, 'title') ?? { type: 'text', value: '' })),
      description: htmlUnescapeAttr(elementText(childElement(item, 'description') ?? { type: 'text', value: '' })),
    }
  })
}

/** A correction's feed guid never has a trailing "/issues/<id>/" shape, so this is unambiguous either way. */
function isCorrectionGuid(guid: string): boolean {
  return guid.includes('/corrections/#')
}

export function checkFeedXmlExistsAndParses(
  distDir: string,
  issuesList: Issue[],
  correctionsList: Correction[] = [],
  factualGroups: readonly FactualCorrectionGroup[] = [],
  sources: CorrectionHistorySources = emptyCorrectionHistorySources,
): CheckResult {
  return runCheck('11d feed-xml-exists-and-parses', () => {
    const path = resolve(distDir, 'feed.xml')
    if (!existsSync(path)) {
      throw new Error('dist/feed.xml is missing')
    }
    const xml = readFileSync(path, 'utf8')
    if (!xml.startsWith('<?xml')) {
      throw new Error('dist/feed.xml does not start with an XML declaration')
    }
    if (!xml.includes('<rss version="2.0">') || !xml.includes('</rss>')) {
      throw new Error('dist/feed.xml is not a well-formed RSS 2.0 document')
    }

    const publishedIssues = feedIssuesNewestFirst(issuesList)
    const allParsedItems = extractFeedItems(xml) // throws on a nested/unbalanced <item>
    const parsedItems = allParsedItems.filter((item) => !isCorrectionGuid(item.guid))
    const correctionParsedItems = allParsedItems.filter((item) => isCorrectionGuid(item.guid))

    if (parsedItems.length !== publishedIssues.length) {
      throw new Error(
        `dist/feed.xml has ${parsedItems.length} issue <item> element(s), expected exactly one per published issue (${publishedIssues.length})`,
      )
    }

    const issueById = new Map(issuesList.map((issue) => [issue.id, issue]))
    const expectedGuids = new Set(publishedIssues.map((issue) => `${SITE_URL}/issues/${issue.id}/`))
    const actualGuids = new Set(parsedItems.map((item) => item.guid))
    const missingGuids = [...expectedGuids].filter((guid) => !actualGuids.has(guid))
    const extraGuids = [...actualGuids].filter((guid) => !expectedGuids.has(guid))
    if (missingGuids.length > 0 || extraGuids.length > 0) {
      throw new Error(
        `dist/feed.xml guid set does not equal the set of published issue permalinks — ` +
          `missing: [${missingGuids.join(', ')}], extra: [${extraGuids.join(', ')}]`,
      )
    }

    // Map each item's guid back to its issue and require the pubDate to
    // equal the RFC 822 form of that issue's published date — not merely a
    // syntactically valid RFC 822 string.
    for (const item of parsedItems) {
      const idMatch = item.guid.match(/\/issues\/([^/]+)\/$/)
      const issue = idMatch ? issueById.get(idMatch[1]) : undefined
      if (!issue) {
        throw new Error(`dist/feed.xml item guid "${item.guid}" does not map to a known issue id`)
      }
      if (issue.published === null) {
        throw new Error(`dist/feed.xml item guid "${item.guid}" maps to issue "${issue.id}", which has no published date`)
      }
      const expectedPubDate = toRfc822(issue.published)
      if (item.pubDate !== expectedPubDate) {
        throw new Error(
          `dist/feed.xml item "${item.guid}" pubDate is "${item.pubDate}", expected "${expectedPubDate}" ` +
            `(the RFC 822 form of issue "${issue.id}"'s published date "${issue.published}")`,
        )
      }
    }

    // --- Correction items (SEC-MARKET-FABLE-001 T6-13): same discipline as
    // above — exact count, exact guid set, and per-item pubDate identity —
    // applied to the separate, appended set of correction <item>s. ---------
    const factual = factualCorrectionHistory(factualGroups, sources, SITE_URL)
    const allCorrections = [...correctionsList, ...factual]
    if (correctionParsedItems.length !== allCorrections.length) {
      throw new Error(
        `dist/feed.xml has ${correctionParsedItems.length} correction <item> element(s), expected exactly one per correction (${allCorrections.length})`,
      )
    }

    const correctionById = new Map(allCorrections.map((correction) => [correction.id, correction]))
    const expectedCorrectionGuids = new Set(
      allCorrections.map((correction) => `${SITE_URL}/corrections/#${correction.id}`),
    )
    const actualCorrectionGuids = new Set(correctionParsedItems.map((item) => item.guid))
    const missingCorrectionGuids = [...expectedCorrectionGuids].filter(
      (guid) => !actualCorrectionGuids.has(guid),
    )
    const extraCorrectionGuids = [...actualCorrectionGuids].filter(
      (guid) => !expectedCorrectionGuids.has(guid),
    )
    if (missingCorrectionGuids.length > 0 || extraCorrectionGuids.length > 0) {
      throw new Error(
        `dist/feed.xml correction guid set does not equal the set of published corrections — ` +
          `missing: [${missingCorrectionGuids.join(', ')}], extra: [${extraCorrectionGuids.join(', ')}]`,
      )
    }

    for (const item of correctionParsedItems) {
      const idMatch = item.guid.match(/\/corrections\/#(.+)$/)
      const correction = idMatch ? correctionById.get(idMatch[1]) : undefined
      if (!correction) {
        throw new Error(`dist/feed.xml correction item guid "${item.guid}" does not map to a known correction id`)
      }
      const expectedPubDate = toRfc822(correction.date)
      if ('kind' in correction) {
        assert.equal(item.title, `Source-verified factual correction: ${correction.supplierName}`, 'factual correction feed title differs')
        assert.equal(item.description, factualCorrectionFeedText(correction), 'factual correction feed description differs')
      }
      if (item.pubDate !== expectedPubDate) {
        throw new Error(
          `dist/feed.xml correction item "${item.guid}" pubDate is "${item.pubDate}", expected "${expectedPubDate}" ` +
            `(the RFC 822 form of correction "${correction.id}"'s date "${correction.date}")`,
        )
      }
    }

    return `${parsedItems.length} issue <item>(s) + ${correctionParsedItems.length} correction <item>(s), guid sets and per-item pubDate verified`
  })
}

// --- 11e: sitemap.xml lists every route -------------------------------------

export function checkSitemapXmlListsEveryRoute(distDir: string, issuesList: Issue[]): CheckResult {
  return runCheck('11e sitemap-xml-lists-every-route', () => {
    const path = resolve(distDir, 'sitemap.xml')
    if (!existsSync(path)) {
      throw new Error('dist/sitemap.xml is missing')
    }
    const xml = readFileSync(path, 'utf8')
    if (!xml.includes('<urlset')) {
      throw new Error('dist/sitemap.xml is not a well-formed sitemap document')
    }
    const routesList = routesFor(issuesList)
    for (const routeEntry of routesList) {
      const loc = `<loc>${SITE_URL}${routeEntry.path}</loc>`
      if (!xml.includes(loc)) {
        throw new Error(`dist/sitemap.xml is missing an entry for route "${routeEntry.path}" (${loc})`)
      }
    }
    return `${routesList.length} route(s) present in sitemap.xml`
  })
}

// --- 11f: dist/issues/lock.json equals the source manifest (G1b) -----------

export function checkLockJsonMatchesSource(distDir: string, sourceLockPath: string): CheckResult {
  return runCheck('11f issues-lock-json-matches-source', () => {
    const path = resolve(distDir, 'issues/lock.json')
    if (!existsSync(path)) {
      throw new Error('dist/issues/lock.json is missing')
    }
    const distRaw = readFileSync(path, 'utf8').trim()
    const distManifest: Record<string, string> = distRaw === '' ? {} : JSON.parse(distRaw)

    const sourceRaw = existsSync(sourceLockPath) ? readFileSync(sourceLockPath, 'utf8').trim() : ''
    const sourceManifest: Record<string, string> = sourceRaw === '' ? {} : JSON.parse(sourceRaw)

    try {
      assert.deepStrictEqual(distManifest, sourceManifest)
    } catch (error) {
      throw new Error(
        `dist/issues/lock.json does not equal the source manifest at ${sourceLockPath}: ${
          error instanceof Error ? error.message : String(error)
        }`,
      )
    }
    return `dist/issues/lock.json matches the source manifest exactly, ${Object.keys(distManifest).length} entr${
      Object.keys(distManifest).length === 1 ? 'y' : 'ies'
    }`
  })
}

// --- 11g: per-route description / og:description / twitter:description (G8)

const META_PATTERNS = {
  description: /<meta\s+name="description"\s+content="([^"]*)"/,
  ogDescription: /<meta\b[^>]*?property="og:description"[^>]*?content="([^"]*)"/,
  twitterDescription: /<meta\b[^>]*?name="twitter:description"[^>]*?content="([^"]*)"/,
} as const

type MetaKey = keyof typeof META_PATTERNS

/** Decodes the handful of entities scripts/prerender.ts's escapeHtmlAttr can produce. `&amp;` last so it cannot re-decode an entity this function just produced. */
function htmlUnescapeAttr(value: string): string {
  return value
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&apos;/g, "'")
    .replace(/&amp;/g, '&')
}

function readMetaDescriptions(html: string, routeLabel: string): Record<MetaKey, string> {
  const result = {} as Record<MetaKey, string>
  for (const key of Object.keys(META_PATTERNS) as MetaKey[]) {
    const match = html.match(META_PATTERNS[key])
    if (!match) {
      throw new Error(`route "${routeLabel}": could not find a ${key} meta tag`)
    }
    result[key] = htmlUnescapeAttr(match[1])
  }
  return result
}

const ARCHIVE_DESCRIPTION = 'Every Security Market Pulse weekly issue, newest first, with its permalink.'

/**
 * Every non-front route's description / og:description / twitter:description
 * must equal its expected route-specific text (the archive's fixed blurb, or
 * an issue permalink's `read`) — HTML-unescaped, since prerender.ts writes
 * the attribute-escaped form — and must differ from the front page's, which
 * keeps its own hand-authored head verbatim (scripts/prerender.ts's
 * rewriteHead skips the front route entirely).
 */
export function checkRouteDescriptionMeta(distDir: string, issuesList: Issue[]): CheckResult {
  return runCheck('11g route-description-meta-identity', () => {
    const frontPath = resolve(distDir, 'index.html')
    if (!existsSync(frontPath)) {
      throw new Error('dist/index.html is missing')
    }
    const front = readMetaDescriptions(readFileSync(frontPath, 'utf8'), '/')

    let checkedCount = 0

    function checkRoute(path: string, expectedText: string, label: string): void {
      if (!existsSync(path)) {
        throw new Error(`route "${label}": HTML file is missing at ${path}`)
      }
      const actual = readMetaDescriptions(readFileSync(path, 'utf8'), label)
      for (const key of Object.keys(META_PATTERNS) as MetaKey[]) {
        if (actual[key] !== expectedText) {
          throw new Error(`route "${label}" ${key} is "${actual[key]}", expected "${expectedText}"`)
        }
        if (actual[key] === front[key]) {
          throw new Error(
            `route "${label}" ${key} equals the front page's ${key} ("${front[key]}") — expected route-specific text`,
          )
        }
      }
      checkedCount++
    }

    checkRoute(resolve(distDir, 'issues/index.html'), ARCHIVE_DESCRIPTION, '/issues/')
    for (const issue of issuesList) {
      checkRoute(resolve(distDir, 'issues', issue.id, 'index.html'), issue.read, `/issues/${issue.id}/`)
    }

    return `front page description confirmed distinct; ${checkedCount} non-front route(s) verified (description, og:description, twitter:description)`
  })
}

// --- 11h: every <link rel="alternate"> target exists in dist (agent-surface-spec.md §6.3) --

const ALTERNATE_LINK_TAG_PATTERN = /<link\b[^>]*\brel="alternate"[^>]*>/g
const HREF_ATTR_PATTERN = /\bhref="([^"]+)"/

/** A `<link rel="alternate">` href, resolved to the dist-relative file it should name. */
function alternateLinkFilePath(distDir: string, href: string): string {
  let path = href.startsWith(SITE_URL) ? href.slice(SITE_URL.length) : href
  if (!path.startsWith('/')) path = `/${path}`
  return path.endsWith('/') ? resolve(distDir, path.replace(/^\//, ''), 'index.html') : resolve(distDir, path.replace(/^\//, ''))
}

/**
 * Every route's `<link rel="alternate">` tags (RSS feed, JSON machine-surface
 * files) must point at a file that actually exists in `dist` — wired up per
 * agent-surface-spec.md §6.3 so a stale or broken machine link fails the
 * build instead of quietly 404ing for whatever program follows it. Extended
 * for SEC-MARKET-FABLE-001 T6-13: every route must also specifically
 * advertise `/corrections.json`, not merely have *some* alternate links that
 * happen to resolve — a build that silently dropped that one link target
 * would otherwise still pass. Extended again for AUTO-001 fix pass 4, item
 * 10: the same specific-advertisement requirement for `/tracker.json`.
 */
export function checkAlternateLinksResolve(distDir: string, issuesList: Issue[]): CheckResult {
  return runCheck('11h alternate-link-targets-exist', () => {
    const routesList = routesFor(issuesList)
    const correctionsJsonHref = `${SITE_URL}/corrections.json`
    const trackerJsonHref = `${SITE_URL}/tracker.json`
    let checkedCount = 0
    for (const routeEntry of routesList) {
      const path = routeHtmlPath(distDir, routeEntry.path)
      if (!existsSync(path)) {
        throw new Error(`route "${routeEntry.path}": HTML file is missing at ${path}`)
      }
      const html = readFileSync(path, 'utf8')
      const tags = html.match(ALTERNATE_LINK_TAG_PATTERN) ?? []
      if (tags.length === 0) {
        throw new Error(`route "${routeEntry.path}": no <link rel="alternate"> tags found`)
      }
      const hrefsSeen: string[] = []
      for (const tag of tags) {
        const hrefMatch = tag.match(HREF_ATTR_PATTERN)
        if (!hrefMatch) {
          throw new Error(`route "${routeEntry.path}": an alternate link tag has no href — ${tag}`)
        }
        const href = hrefMatch[1]
        hrefsSeen.push(href)
        const filePath = alternateLinkFilePath(distDir, href)
        if (!existsSync(filePath)) {
          throw new Error(
            `route "${routeEntry.path}": alternate link target "${href}" does not exist in dist (expected ${filePath})`,
          )
        }
        checkedCount++
      }
      if (!hrefsSeen.includes(correctionsJsonHref)) {
        throw new Error(
          `route "${routeEntry.path}": no <link rel="alternate"> advertises "${correctionsJsonHref}"`,
        )
      }
      if (!hrefsSeen.includes(trackerJsonHref)) {
        throw new Error(
          `route "${routeEntry.path}": no <link rel="alternate"> advertises "${trackerJsonHref}"`,
        )
      }
    }
    return `${checkedCount} alternate link target(s) verified across ${routesList.length} route(s), corrections.json and tracker.json links confirmed on every route`
  })
}

// --- 11i: dist/corrections.json exists and identity-matches the source data

/**
 * `dist/corrections.json` must exist, parse, and deep-equal the payload
 * `correctionsJsonPayload` builds from the source `corrections` array — the
 * same identity discipline check 11b applies to each issue's JSON copy.
 */
export function checkCorrectionsJsonExists(distDir: string, correctionsList: Correction[], factualGroups: readonly FactualCorrectionGroup[] = [], sources: CorrectionHistorySources = emptyCorrectionHistorySources): CheckResult {
  return runCheck('11i corrections-json-exists', () => {
    const path = resolve(distDir, 'corrections.json')
    if (!existsSync(path)) {
      throw new Error('dist/corrections.json is missing')
    }
    const parsed = JSON.parse(readFileSync(path, 'utf8'))
    if (!Array.isArray(parsed)) {
      throw new Error('dist/corrections.json does not parse to an array')
    }
    const expected = JSON.parse(JSON.stringify(publicCorrectionsJsonPayload(correctionsList, factualGroups, sources, SITE_URL)))
    try {
      assert.deepStrictEqual(parsed, expected)
    } catch (error) {
      throw new Error(
        `dist/corrections.json does not deep-equal the expected payload: ${
          error instanceof Error ? error.message : String(error)
        }`,
      )
    }
    return `${parsed.length} correction(s) present, well-formed, and identity-checked`
  })
}

export function checkFactualCorrectionsJsonExists(distDir: string, bundle: FactualCorrectionBundle): CheckResult {
  return runCheck('11k factual-corrections-json-exists', () => {
    const path = resolve(distDir, 'factual-corrections.json')
    if (!existsSync(path)) throw new Error('dist/factual-corrections.json is missing')
    assert.equal(readFileSync(path, 'utf8'), JSON.stringify(bundle, null, 2) + '\n', 'factual correction bundle bytes differ from admitted projection')
    return `${bundle.groups.length} group(s) match the gate projection`
  })
}

// --- 11j: dist/tracker.json exists and identity-matches the source data ----

/**
 * `dist/tracker.json` must exist, parse, and deep-equal the payload
 * `trackerJsonPayload` builds from the source tracker data — the same
 * identity discipline check 11i applies to corrections.json (AUTO-001 fix
 * pass 4, item 10).
 */
export function checkTrackerJsonExists(
  distDir: string,
  suppliers: TrackerSupplier[],
  domains: TrackerDomain[],
  evidenceByIdMap: Record<string, EvidenceRecord>,
  status: RunStatus,
): CheckResult {
  return runCheck('11j tracker-json-exists', () => {
    const path = resolve(distDir, 'tracker.json')
    if (!existsSync(path)) {
      throw new Error('dist/tracker.json is missing')
    }
    const parsed = JSON.parse(readFileSync(path, 'utf8'))
    const expected = JSON.parse(
      JSON.stringify(trackerJsonPayload(suppliers, domains, evidenceByIdMap, status)),
    )
    try {
      assert.deepStrictEqual(parsed, expected)
    } catch (error) {
      throw new Error(
        `dist/tracker.json does not deep-equal the expected payload: ${
          error instanceof Error ? error.message : String(error)
        }`,
      )
    }
    return `${parsed.figures.length} figure(s) across ${parsed.suppliers.length} supplier(s), well-formed, and identity-checked`
  })
}

// --- Script entry point: only runs when this file is executed directly -----

function isMainModule(): boolean {
  return process.argv[1] !== undefined && pathToFileURL(process.argv[1]).href === import.meta.url
}

const EXPECTED_CHECK_COUNT = 11

export function report(results: CheckResult[]): boolean {
  if (results.length !== EXPECTED_CHECK_COUNT) {
    throw new Error(
      `expected ${EXPECTED_CHECK_COUNT} check results, got ${results.length} — the run did not reach a verdict`,
    )
  }

  let anyFail = false
  for (const result of results) {
    if (result.pass) {
      console.log(`PASS  ${result.name}${result.detail ? ` — ${result.detail}` : ''}`)
    } else {
      anyFail = true
      console.error(`FAIL  ${result.name} — ${result.detail}`)
    }
  }
  return anyFail
}

if (isMainModule()) {
  try {
    const distDir = resolve(webRoot, 'dist')
    const results = [
      checkEveryRouteHtmlExists(distDir, issues),
      checkEveryIssueJsonExists(distDir, issues, evidenceById),
      checkIssuesIndexJsonExists(distDir, issues),
      checkFeedXmlExistsAndParses(distDir, issues, corrections, factualCorrectionGroups, { evidence: evidenceById, suppliers: trackerSuppliers, groupEvidenceIds: factualCorrectionSourceEvidenceIds }),
      checkSitemapXmlListsEveryRoute(distDir, issues),
      checkLockJsonMatchesSource(distDir, SOURCE_LOCK_PATH),
      checkRouteDescriptionMeta(distDir, issues),
      checkAlternateLinksResolve(distDir, issues),
      checkCorrectionsJsonExists(distDir, corrections, factualCorrectionGroups, { evidence: evidenceById, suppliers: trackerSuppliers, groupEvidenceIds: factualCorrectionSourceEvidenceIds }),
      checkFactualCorrectionsJsonExists(distDir, factualCorrectionBundle),
      checkTrackerJsonExists(distDir, trackerSuppliers, trackerDomains, evidenceById, runStatus),
    ]
    const anyFail = report(results)
    if (anyFail) {
      console.error('verify:dist FAILED')
      process.exit(1)
    }
    console.log('verify:dist passed')
  } catch (error) {
    const detail = error instanceof Error ? (error.stack ?? error.message) : String(error)
    console.error('verify:dist CRASHED before reaching a verdict:')
    console.error(detail)
    process.exit(1)
  }
}
