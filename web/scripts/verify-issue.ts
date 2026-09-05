import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { execFileSync } from 'node:child_process'
import { createHash } from 'node:crypto'
import { existsSync, readFileSync, writeFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { editions } from '../src/data/edition.ts'
import { evidenceById } from '../src/data/evidence.ts'
import { formatShortDate } from '../src/data/dates.ts'
import { securityDomains } from '../src/data/domains.ts'
import { issues, latestIssue } from '../src/data/issues/index.ts'
import {
  extractNumericTokens,
  isoWeekSunday,
  issueEvidenceIds,
  windowOf,
} from '../src/data/issueHelpers.ts'
import { AUTHOR_NAME } from '../src/data/meta.ts'
import type { Issue, Lane } from '../src/data/types.ts'
import { IssueHero } from '../src/components/IssueHero.tsx'
import { IssueLanes } from '../src/components/IssueLanes.tsx'
import { WeThink } from '../src/components/WeThink.tsx'
import { EvidenceProvider } from '../src/context/EvidenceProvider.tsx'

// Check 11 (dist output — permalinks, JSON copies, feed.xml, sitemap.xml)
// belongs to scripts/verify-dist.ts, a separate post-build script.

const LANE_ORDER: Lane[] = ['formation', 'absorption', 'prints', 'capital']

const __dirname = dirname(fileURLToPath(import.meta.url))
const WEB_ROOT = resolve(__dirname, '..')
const LOCK_PATH = resolve(__dirname, '../src/data/issues/issues.lock.json')
const LOCK_PATH_IN_REPO = 'web/src/data/issues/issues.lock.json'

type LockManifest = Record<string, string>

function readManifest(): LockManifest {
  if (!existsSync(LOCK_PATH)) return {}
  const raw = readFileSync(LOCK_PATH, 'utf8').trim()
  return raw === '' ? {} : (JSON.parse(raw) as LockManifest)
}

function hashIssue(issue: Issue): string {
  return createHash('sha256').update(JSON.stringify(issue)).digest('hex')
}

function publishedIssuesOf(list: Issue[]): Issue[] {
  return list.filter((issue) => issue.status === 'published')
}

/** True on a Vercel build of a protected branch — main or preview. */
function isProtectedBuild(): boolean {
  const ref = process.env.VERCEL_GIT_COMMIT_REF
  return ref === 'main' || ref === 'preview'
}

interface ParentManifest {
  sha: string
  manifest: LockManifest
}

interface GitAnchorResult {
  /**
   * True only when HEAD has at least one parent AND at least one of those
   * parents' lock manifest could actually be read. A depth-1 (shallow)
   * clone has zero parents (`git rev-parse HEAD^@` succeeds with empty
   * output) and is therefore unavailable, not "empty but available" — a
   * production build may legitimately lack a preview-only issue, so an
   * empty git anchor must never be treated as silent proof of append-only
   * history.
   */
  available: boolean
  /** Total parent count from `git rev-parse HEAD^@` (0 for a shallow clone). */
  parentCount: number
  /** Only the parents whose lock manifest was actually read, each kept
   * separate — never merged into one object, so one parent's entries can
   * never be shadowed by another's. */
  readableParents: ParentManifest[]
}

/**
 * Reads the lock manifest from every parent of HEAD, keeping each parent's
 * manifest separate (never `Object.assign`ed together — a merge would let
 * one parent silently overwrite another's conflicting hash for the same
 * id). HEAD's parent(s) are a real prior state, not the commit under test,
 * so they anchor "append-only" against something other than the working
 * tree itself. A shallow (depth-1) clone legitimately has no parent to
 * read — `git rev-parse HEAD^@` then succeeds with zero output — which
 * makes the git anchor unavailable outright; see readNetworkAnchor below
 * for the second, independent anchor that covers that case.
 */
function readGitParentAnchor(): GitAnchorResult {
  let parents: string[]
  try {
    const raw = execFileSync('git', ['rev-parse', 'HEAD^@'], {
      cwd: WEB_ROOT,
      stdio: ['ignore', 'pipe', 'ignore'],
    })
      .toString('utf8')
      .trim()
    parents = raw === '' ? [] : raw.split('\n')
  } catch {
    return { available: false, parentCount: 0, readableParents: [] }
  }

  const readableParents: ParentManifest[] = []
  for (const sha of parents) {
    try {
      const raw = execFileSync('git', ['show', `${sha}:${LOCK_PATH_IN_REPO}`], {
        cwd: WEB_ROOT,
        stdio: ['ignore', 'pipe', 'ignore'],
      })
        .toString('utf8')
        .trim()
      const manifest: LockManifest = raw === '' ? {} : JSON.parse(raw)
      readableParents.push({ sha, manifest })
    } catch {
      // No lock file at that ref yet (an early commit predating the lock
      // file), or the ref itself does not resolve — this parent contributes
      // nothing and is not counted as readable.
    }
  }

  return { available: readableParents.length > 0, parentCount: parents.length, readableParents }
}

type NetworkAnchorStatus = 'ok' | 'not-found' | 'error' | 'skipped'

interface NetworkAnchorResult {
  status: NetworkAnchorStatus
  manifest: LockManifest
  detail: string
  url: string | null
}

const DEFAULT_LOCK_URL = 'https://securitymarketpulse.com/issues/lock.json'
const NETWORK_ANCHOR_TIMEOUT_MS = 10_000
const ISSUE_ID_PATTERN = /^\d{4}-w\d{2}$/
const HEX64_LOWER_PATTERN = /^[0-9a-f]{64}$/

/**
 * Validates the shape of a parsed network-anchor body: a plain JSON object
 * (not an array, not null) whose keys all match the issue id pattern and
 * whose values are all lowercase 64-hex sha256 strings. Anything else is not
 * a manifest this build can trust as an anchor.
 */
function validateLockManifestShape(value: unknown): { ok: true } | { ok: false; reason: string } {
  if (typeof value !== 'object' || value === null || Array.isArray(value)) {
    return { ok: false, reason: 'response body is not a plain JSON object' }
  }
  for (const [key, val] of Object.entries(value as Record<string, unknown>)) {
    if (!ISSUE_ID_PATTERN.test(key)) {
      return { ok: false, reason: `key "${key}" does not match ^\\d{4}-w\\d{2}$` }
    }
    if (typeof val !== 'string' || !HEX64_LOWER_PATTERN.test(val)) {
      return { ok: false, reason: `value for "${key}" is not a lowercase 64-hex string` }
    }
  }
  return { ok: true }
}

/**
 * Fetches the live production manifest at `dist/issues/lock.json` (see
 * generate-feed.ts and verify-dist.ts, which publish and check it) as the
 * second append-only anchor — one that survives even a shallow clone with no
 * git history at all. Only an HTTP 200 whose body validates as a plain
 * manifest object counts as available: a redirect (fetched with
 * `redirect: 'manual'` so a 3xx is observed rather than silently followed),
 * a non-200/404 status, or a malformed body is treated as unavailable, with
 * the reason recorded in `detail`. `SMP_LOCK_BASE_URL` overrides the URL;
 * the literal value `"none"` skips the fetch entirely, for offline local
 * runs and this script's own perturbation tests.
 */
async function readNetworkAnchor(): Promise<NetworkAnchorResult> {
  const override = process.env.SMP_LOCK_BASE_URL
  if (override === 'none') {
    return { status: 'skipped', manifest: {}, detail: 'SMP_LOCK_BASE_URL=none', url: null }
  }
  const url = override && override.trim() !== '' ? override : DEFAULT_LOCK_URL

  const controller = new AbortController()
  const timeout = setTimeout(() => controller.abort(), NETWORK_ANCHOR_TIMEOUT_MS)
  try {
    const response = await fetch(url, { signal: controller.signal, redirect: 'manual' })
    if (response.type === 'opaqueredirect' || (response.status >= 300 && response.status < 400)) {
      return {
        status: 'error',
        manifest: {},
        detail: `redirect (HTTP ${response.status || 'opaque'}) — treated as unavailable`,
        url,
      }
    }
    if (response.status === 404) {
      return { status: 'not-found', manifest: {}, detail: '404 Not Found', url }
    }
    if (response.status !== 200) {
      return { status: 'error', manifest: {}, detail: `HTTP ${response.status}`, url }
    }
    const text = (await response.text()).trim()
    let parsed: unknown
    try {
      parsed = text === '' ? {} : JSON.parse(text)
    } catch {
      return { status: 'error', manifest: {}, detail: 'response body is not valid JSON', url }
    }
    const shape = validateLockManifestShape(parsed)
    if (!shape.ok) {
      return { status: 'error', manifest: {}, detail: `malformed manifest body — ${shape.reason}`, url }
    }
    return { status: 'ok', manifest: parsed as LockManifest, detail: 'HTTP 200', url }
  } catch (error) {
    const detail = error instanceof Error ? error.message : String(error)
    return { status: 'error', manifest: {}, detail, url }
  } finally {
    clearTimeout(timeout)
  }
}

interface AppendOnlyAnchors {
  git: GitAnchorResult
  network: NetworkAnchorResult
}

async function computeAppendOnlyAnchors(): Promise<AppendOnlyAnchors> {
  return { git: readGitParentAnchor(), network: await readNetworkAnchor() }
}

/**
 * Checks a working manifest's append-only property against both anchors.
 * An anchor that is unavailable contributes no entries and no violations —
 * it is simply absent from enforcement. If at least one anchor is
 * available, every available anchor is enforced and the check passes only
 * if all of them agree with the working manifest. If neither anchor is
 * available, the build fails on a protected branch (main/preview) and
 * otherwise prints one loud warning and passes. Returns violation messages
 * (empty = passes), informational lines to log regardless of pass/fail, and
 * a one-line summary naming each anchor and its state for the PASS line.
 */
function validateAppendOnly(
  workingManifest: LockManifest,
  anchors: AppendOnlyAnchors,
): { violations: string[]; infoLines: string[]; anchorSummary: string } {
  const violations: string[] = []
  const infoLines: string[] = []

  // --- Git-parent anchor: each readable parent validated separately. -------
  if (anchors.git.available) {
    for (const parent of anchors.git.readableParents) {
      const shortSha = parent.sha.slice(0, 8)
      for (const [id, hash] of Object.entries(parent.manifest)) {
        if (!(id in workingManifest)) {
          violations.push(
            `append-only violation: git parent ${shortSha} has entry "${id}" missing from the working manifest`,
          )
        } else if (workingManifest[id] !== hash) {
          violations.push(
            `append-only violation: git parent ${shortSha} entry "${id}" has hash ${hash}, working manifest has ${workingManifest[id]}`,
          )
        }
      }
    }
    const shas = anchors.git.readableParents.map((p) => p.sha.slice(0, 8)).join(', ')
    infoLines.push(
      `git-parent anchor: ${anchors.git.readableParents.length} parent manifest(s) read (${shas}).`,
    )
  } else {
    const reason =
      anchors.git.parentCount === 0
        ? 'HEAD has zero parents (shallow clone)'
        : `HEAD has ${anchors.git.parentCount} parent(s) but no parent manifest could be read`
    infoLines.push(`git-parent anchor unavailable: ${reason}.`)
  }

  // --- Network anchor. -------------------------------------------------
  if (anchors.network.status === 'ok') {
    for (const [id, hash] of Object.entries(anchors.network.manifest)) {
      if (!(id in workingManifest)) {
        violations.push(
          `append-only violation: network anchor (${anchors.network.url}) has entry "${id}" missing from the working manifest`,
        )
      } else if (workingManifest[id] !== hash) {
        violations.push(
          `append-only violation: network anchor (${anchors.network.url}) entry "${id}" has hash ${hash}, working manifest has ${workingManifest[id]}`,
        )
      }
    }
    infoLines.push(
      `network anchor: HTTP 200, ${Object.keys(anchors.network.manifest).length} entries from ${anchors.network.url}.`,
    )
  } else if (anchors.network.status === 'skipped') {
    infoLines.push(`network anchor unavailable (skipped): ${anchors.network.detail}.`)
  } else if (anchors.network.status === 'not-found') {
    infoLines.push(`network anchor unavailable (404): ${anchors.network.url} — not yet live.`)
  } else {
    infoLines.push(`network anchor unavailable (error): ${anchors.network.detail}.`)
  }

  // --- No anchor available at all. --------------------------------------
  // A network failure never fails the build when a git anchor is available
  // — this branch only fires when BOTH anchors are unavailable.
  const anyAvailable = anchors.git.available || anchors.network.status === 'ok'
  if (!anyAvailable) {
    if (isProtectedBuild()) {
      violations.push(
        `append-only violation: no anchor available — neither the git-parent anchor nor the network anchor could be read, on a protected build (VERCEL_GIT_COMMIT_REF="${process.env.VERCEL_GIT_COMMIT_REF}") — refusing to proceed without a history anchor.`,
      )
    } else {
      infoLines.push(
        'WARNING — no append-only anchor available (neither git-parent nor network); continuing because this is not a protected (main/preview) build.',
      )
    }
  }

  const gitState = anchors.git.available
    ? `${anchors.git.readableParents.length} parents read`
    : 'unavailable'
  const networkState =
    anchors.network.status === 'ok'
      ? `200 + ${Object.keys(anchors.network.manifest).length} entries`
      : anchors.network.status === 'not-found'
        ? '404'
        : anchors.network.status === 'skipped'
          ? 'skipped'
          : 'error'
  const anchorSummary = `git: ${gitState}; network: ${networkState}`

  return { violations, infoLines, anchorSummary }
}

interface CheckResult {
  name: string
  pass: boolean
  detail?: string
}

const results: CheckResult[] = []

/**
 * Runs one check; a thrown error becomes a FAIL with the error's message.
 * `fn` may be async — check 8's append-only gate fetches the network anchor.
 */
async function check(name: string, fn: () => string | void | Promise<string | void>): Promise<void> {
  try {
    const detail = await fn()
    results.push({ name, pass: true, detail: detail ?? undefined })
  } catch (error) {
    const detail = error instanceof Error ? error.message : String(error)
    results.push({ name, pass: false, detail })
  }
}

/** True iff `value` matches `^\d{4}-\d{2}-\d{2}$` and names a real calendar date. */
function isValidIsoDate(value: string): boolean {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(value)) return false
  const [year, month, day] = value.split('-').map(Number)
  const date = new Date(Date.UTC(year, month - 1, day))
  return (
    date.getUTCFullYear() === year && date.getUTCMonth() === month - 1 && date.getUTCDate() === day
  )
}

function windowsOverlap(
  a: { start: string; end: string },
  b: { start: string; end: string },
): boolean {
  return a.start <= b.end && b.start <= a.end
}

const LANE_HEADING_IDS: Record<Lane, string> = {
  formation: 'formation-heading',
  absorption: 'absorption-heading',
  prints: 'prints-this-week-heading',
  capital: 'capital-heading',
}

/**
 * Runs the full check suite, appending to the module-level `results` array.
 * Call `results.length = 0` first for a clean run. `includeLockManifest`
 * lets `--write` validate a candidate issue BEFORE the manifest is written —
 * check 8 by construction fails a freshly-drafted published issue that has
 * no manifest entry yet, so it is excluded from that pre-write pass and
 * included again in the full re-run against the manifest `--write` produces.
 */
async function runChecks({ includeLockManifest }: { includeLockManifest: boolean }): Promise<void> {
  // 1. Ordering, id format, weekEnding is the ISO week's Sunday, and both id
  //    and weekEnding are unique.
  await check('1 ordering-id-format-sunday-unique', () => {
    const seenIds = new Set<string>()
    const seenWeekEndings = new Set<string>()
    for (let i = 0; i < issues.length; i++) {
      const issue = issues[i]
      if (!/^\d{4}-w\d{2}$/.test(issue.id)) {
        throw new Error(`issue id "${issue.id}" does not match ^\\d{4}-w\\d{2}$`)
      }
      if (seenIds.has(issue.id)) {
        throw new Error(`duplicate issue id "${issue.id}"`)
      }
      seenIds.add(issue.id)
      if (seenWeekEndings.has(issue.weekEnding)) {
        throw new Error(`duplicate weekEnding "${issue.weekEnding}"`)
      }
      seenWeekEndings.add(issue.weekEnding)

      const expectedSunday = isoWeekSunday(issue.id)
      if (expectedSunday !== issue.weekEnding) {
        throw new Error(
          `issue "${issue.id}" weekEnding "${issue.weekEnding}" is not that ISO week's Sunday (expected "${expectedSunday}")`,
        )
      }
      if (i > 0 && !(issue.weekEnding > issues[i - 1].weekEnding)) {
        throw new Error(
          `issues out of order: "${issues[i - 1].id}" (${issues[i - 1].weekEnding}) is not before "${issue.id}" (${issue.weekEnding})`,
        )
      }
    }
  })

  // 2. Windows do not overlap.
  await check('2 windows-no-overlap', () => {
    for (let i = 0; i < issues.length; i++) {
      for (let j = i + 1; j < issues.length; j++) {
        const a = windowOf(issues[i])
        const b = windowOf(issues[j])
        if (windowsOverlap(a, b)) {
          throw new Error(
            `windows overlap: "${issues[i].id}" [${a.start}, ${a.end}] and "${issues[j].id}" [${b.start}, ${b.end}]`,
          )
        }
      }
    }
  })

  // 3. Exactly four sections, in Lane order, per issue.
  await check('3 four-sections-lane-order', () => {
    for (const issue of issues) {
      if (issue.sections.length !== 4) {
        throw new Error(`issue "${issue.id}" has ${issue.sections.length} sections, expected 4`)
      }
      for (let i = 0; i < LANE_ORDER.length; i++) {
        if (issue.sections[i].lane !== LANE_ORDER[i]) {
          throw new Error(
            `issue "${issue.id}" section ${i} has lane "${issue.sections[i].lane}", expected "${LANE_ORDER[i]}" (Lane order)`,
          )
        }
      }
    }
  })

  // 4. Every evidence id the issue cites resolves — items, weThink.thesis,
  //    weThink.postureDeltas[], and (on a draft) proposed.thesis — read
  //    through the same issueEvidenceIds() helper the site's evidence drawer
  //    and dist JSON copy use, so this check and the site cannot drift on
  //    what "cited" means. Every item date is inside the window unless
  //    background.
  await check('4 item-evidence-and-window', () => {
    for (const issue of issues) {
      const { start, end } = windowOf(issue)
      for (const section of issue.sections) {
        for (const item of section.items) {
          // A future-dated item fails outright — "background" only ever means
          // "dated before the window," never "dated after it," so it cannot be
          // used to exempt a date past weekEnding.
          if (item.date > end) {
            throw new Error(
              `issue "${issue.id}" item "${item.id}" is dated ${item.date}, after weekEnding ${end} — background does not exempt a future-dated item`,
            )
          }
          if (item.background) {
            if (!(item.date < start)) {
              throw new Error(
                `issue "${issue.id}" item "${item.id}" is marked background but dated ${item.date}, which is not before windowStart ${start}`,
              )
            }
          } else if (item.date < start) {
            throw new Error(
              `issue "${issue.id}" item "${item.id}" is dated ${item.date}, before windowStart ${start}, and is not marked background`,
            )
          }
        }
      }

      for (const id of issueEvidenceIds(issue)) {
        if (!evidenceById[id]) {
          throw new Error(`issue "${issue.id}" cites unresolved evidence id "${id}"`)
        }
      }
    }
  })

  // 5. Published issues are signed and complete; drafts are unsigned and unjudged.
  await check('5 publish-signature-consistency', () => {
    for (const issue of issues) {
      if (issue.status === 'published') {
        if (!issue.published || issue.weThink.signedBy === null || !issue.weThink.signedOn) {
          throw new Error(
            `issue "${issue.id}" is published but missing (or has an empty) published/signedBy/signedOn`,
          )
        }
        if (issue.weThink.signedBy !== AUTHOR_NAME) {
          throw new Error(
            `issue "${issue.id}" signedBy "${issue.weThink.signedBy}" does not equal AUTHOR_NAME "${AUTHOR_NAME}"`,
          )
        }
        if (issue.proposed !== null) {
          throw new Error(`issue "${issue.id}" is published but "proposed" is not null`)
        }
        if (issue.weThink.summary.trim() === '') {
          throw new Error(`issue "${issue.id}" is published but weThink.summary is empty`)
        }
        if (issue.weThink.thesis === null) {
          throw new Error(`issue "${issue.id}" is published but weThink.thesis is null`)
        }
        if (issue.weThink.thesis.basis.trim() === '') {
          throw new Error(`issue "${issue.id}" is published but weThink.thesis.basis is empty`)
        }
        if (issue.weThink.thesis.evidenceIds.length === 0) {
          throw new Error(`issue "${issue.id}" is published but weThink.thesis.evidenceIds is empty`)
        }
        if (!issue.weThink.thesis.confidence) {
          throw new Error(`issue "${issue.id}" is published but weThink.thesis has no confidence`)
        }
        for (const delta of issue.weThink.postureDeltas) {
          if (!delta.confidence) {
            throw new Error(
              `issue "${issue.id}" posture delta for "${delta.domainId}" has no confidence`,
            )
          }
        }
      } else {
        if (issue.published !== null || issue.weThink.signedBy !== null || issue.weThink.signedOn !== null) {
          throw new Error(
            `issue "${issue.id}" is a draft but has published/signedBy/signedOn set`,
          )
        }
        if (issue.weThink.thesis !== null) {
          throw new Error(`issue "${issue.id}" is a draft but weThink.thesis is not null`)
        }
        if (issue.weThink.summary !== '') {
          throw new Error(`issue "${issue.id}" is a draft but weThink.summary is not empty`)
        }
        if (issue.weThink.postureDeltas.length !== 0) {
          throw new Error(`issue "${issue.id}" is a draft but weThink.postureDeltas is not empty`)
        }
        if (issue.weThink.noCalls.length !== 0) {
          throw new Error(`issue "${issue.id}" is a draft but weThink.noCalls is not empty`)
        }
      }
    }
  })

  // 6. At most one draft, and it is the newest issue.
  await check('6 at-most-one-draft-newest', () => {
    const drafts = issues.filter((issue) => issue.status === 'draft')
    if (drafts.length > 1) {
      throw new Error(`${drafts.length} draft issues found: ${drafts.map((d) => d.id).join(', ')}`)
    }
    if (drafts.length === 1 && drafts[0].id !== issues[issues.length - 1].id) {
      throw new Error(`draft issue "${drafts[0].id}" is not the newest issue`)
    }
  })

  // 7. Production guard: on main, the newest issue must be published.
  await check('7 production-guard-main-published', () => {
    if (process.env.VERCEL_GIT_COMMIT_REF === 'main') {
      const newest = issues[issues.length - 1]
      if (newest.status !== 'published') {
        throw new Error(
          `VERCEL_GIT_COMMIT_REF is "main" but newest issue "${newest.id}" is status "${newest.status}", not "published"`,
        )
      }
    }
  })

  // 8. Published issues are append-only: the manifest must be internally
  //    self-consistent with the issues array AND every entry inherited from
  //    two independent anchors — HEAD's git parent(s) (plus origin/preview
  //    when it is not HEAD itself) and the live production manifest at
  //    https://securitymarketpulse.com/issues/lock.json — must still be
  //    present with an identical hash. Fails closed on a protected build
  //    (main/preview) when the network anchor errors, or when neither anchor
  //    could be read at all.
  if (includeLockManifest) {
    await check('8 issues-lock-manifest', async () => {
      const manifest = readManifest()
      const published = publishedIssuesOf(issues)

      for (const [id, hash] of Object.entries(manifest)) {
        const issue = issues.find((candidate) => candidate.id === id)
        if (!issue) {
          throw new Error(`manifest id "${id}" is missing from issues`)
        }
        const currentHash = hashIssue(issue)
        if (currentHash !== hash) {
          throw new Error(
            `published issue "${id}" hash differs from its manifest entry — data changed after publish`,
          )
        }
      }

      for (const issue of published) {
        if (!(issue.id in manifest)) {
          throw new Error(
            `published issue "${issue.id}" has no manifest entry — run "npm run verify:issue -- --write"`,
          )
        }
      }

      const anchors = await computeAppendOnlyAnchors()
      const { violations, infoLines, anchorSummary } = validateAppendOnly(manifest, anchors)
      for (const line of infoLines) {
        console.error(`verify:issue check 8: ${line}`)
      }
      if (violations.length > 0) {
        throw new Error(violations.join('; '))
      }
      return `anchors: ${anchorSummary}`
    })
  }

  // 9. Published PostureDeltas agree with securityDomains and editions.
  await check('9 posture-deltas-agree', () => {
    for (const issue of publishedIssuesOf(issues)) {
      for (const delta of issue.weThink.postureDeltas) {
        const domain = securityDomains.find((d) => d.id === delta.domainId)
        if (!domain) {
          throw new Error(`issue "${issue.id}" posture delta names unknown domain "${delta.domainId}"`)
        }
        if (domain.posture !== delta.to) {
          throw new Error(
            `issue "${issue.id}" posture delta for "${delta.domainId}" claims "to" = "${delta.to}", but securityDomains has posture "${domain.posture}"`,
          )
        }
        const confirmingEdition = editions.find((edition) => {
          if (issue.published !== null && edition.date < issue.published) return false
          const snapshot = edition.postures.find((p) => p.domainId === delta.domainId)
          return snapshot?.posture === delta.to
        })
        if (!confirmingEdition) {
          throw new Error(
            `issue "${issue.id}" posture delta for "${delta.domainId}" ("${delta.to}") has no edition dated on or after ${issue.published} carrying that posture`,
          )
        }
      }
    }
  })

  // 12. Every numeric token an item states in its headline or why must appear in
  //     at least one of that item's cited evidence excerpts.
  await check('12 numeric-tokens-cited', () => {
    for (const issue of issues) {
      for (const section of issue.sections) {
        for (const item of section.items) {
          const stated = new Set([
            ...extractNumericTokens(item.headline),
            ...extractNumericTokens(item.why),
          ])
          if (stated.size === 0) continue

          const cited = new Set<string>()
          for (const id of item.evidenceIds) {
            const record = evidenceById[id]
            if (!record) {
              throw new Error(
                `issue "${issue.id}" item "${item.id}" cites unresolved evidence id "${id}"`,
              )
            }
            for (const token of extractNumericTokens(record.excerpt)) cited.add(token)
          }

          for (const token of stated) {
            if (!cited.has(token)) {
              throw new Error(
                `issue "${issue.id}" item "${item.id}" states numeral "${token}" (from headline/why) not found in any cited evidence excerpt`,
              )
            }
          }
        }
      }
    }
  })

  // 13. Strict dates. Every date, weekEnding, windowStart, published and
  //     signedOn must match ^\d{4}-\d{2}-\d{2}$ and be a real calendar date.
  //     A non-null published/signedOn must also be non-empty.
  await check('13 strict-dates', () => {
    function assertDate(label: string, value: string): void {
      if (!isValidIsoDate(value)) {
        throw new Error(`${label} "${value}" is not a valid ^\\d{4}-\\d{2}-\\d{2}$ calendar date`)
      }
    }

    for (const issue of issues) {
      assertDate(`issue "${issue.id}" weekEnding`, issue.weekEnding)
      assertDate(`issue "${issue.id}" windowStart`, issue.windowStart)

      if (issue.published !== null) {
        if (issue.published === '') {
          throw new Error(`issue "${issue.id}" published is an empty string, not a valid date`)
        }
        assertDate(`issue "${issue.id}" published`, issue.published)
      }

      if (issue.weThink.signedOn !== null) {
        if (issue.weThink.signedOn === '') {
          throw new Error(`issue "${issue.id}" weThink.signedOn is an empty string, not a valid date`)
        }
        assertDate(`issue "${issue.id}" weThink.signedOn`, issue.weThink.signedOn)
      }

      for (const section of issue.sections) {
        for (const item of section.items) {
          assertDate(`issue "${issue.id}" item "${item.id}" date`, item.date)
        }
      }
    }
  })

  // 14. Bounds: at most eight items per lane; read <= 140 chars; headline <=
  //     110 chars; why non-empty. Each failure names the offending id and the
  //     measured length.
  await check('14 bounds', () => {
    const MAX_ITEMS_PER_LANE = 8
    const MAX_READ_LENGTH = 140
    const MAX_HEADLINE_LENGTH = 110

    for (const issue of issues) {
      if (issue.read.length > MAX_READ_LENGTH) {
        throw new Error(
          `issue "${issue.id}" read is ${issue.read.length} characters, exceeding the ${MAX_READ_LENGTH}-character limit`,
        )
      }
      for (const section of issue.sections) {
        if (section.items.length > MAX_ITEMS_PER_LANE) {
          throw new Error(
            `issue "${issue.id}" lane "${section.lane}" has ${section.items.length} items, exceeding the ${MAX_ITEMS_PER_LANE}-item limit`,
          )
        }
        for (const item of section.items) {
          if (item.headline.length > MAX_HEADLINE_LENGTH) {
            throw new Error(
              `issue "${issue.id}" item "${item.id}" headline is ${item.headline.length} characters, exceeding the ${MAX_HEADLINE_LENGTH}-character limit`,
            )
          }
          if (item.why.trim() === '') {
            throw new Error(`issue "${issue.id}" item "${item.id}" has an empty "why"`)
          }
        }
      }
    }
  })

  // 15. Every evidence record cited by any issue must carry a retrieval
  //     receipt: a 64-hex sha256 of the fetched bytes, a parseable fetchedAt,
  //     and a non-empty finalUrl. A citation with no receipt fails, naming
  //     the id, rather than letting an unreceipted claim ship silently.
  await check('15 evidence-receipts', () => {
    const SHA256_PATTERN = /^[0-9a-f]{64}$/
    const citedIds = new Set<string>()
    for (const issue of issues) {
      for (const id of issueEvidenceIds(issue)) citedIds.add(id)
    }
    for (const id of citedIds) {
      const record = evidenceById[id]
      if (!record) continue // unresolved ids are check 4's job, not this one's
      const retrieval = record.retrieval
      if (!retrieval) {
        throw new Error(`evidence record "${id}" is cited by an issue but carries no retrieval receipt`)
      }
      if (!SHA256_PATTERN.test(retrieval.sha256)) {
        throw new Error(
          `evidence record "${id}" retrieval.sha256 "${retrieval.sha256}" is not 64 lowercase hex characters`,
        )
      }
      if (retrieval.fetchedAt.trim() === '' || Number.isNaN(Date.parse(retrieval.fetchedAt))) {
        throw new Error(`evidence record "${id}" retrieval.fetchedAt "${retrieval.fetchedAt}" is not a valid date`)
      }
      if (retrieval.finalUrl.trim() === '') {
        throw new Error(`evidence record "${id}" retrieval.finalUrl is empty`)
      }
    }
  })

  // 10. Render check: renderToStaticMarkup of the issue view for the newest
  //     issue. Each lane heading's rendered item count equals items.length, the
  //     draft banner is present iff status === 'draft', and the signature line
  //     text matches the data.
  await check('10 render-check', () => {
    const markup = renderToStaticMarkup(
      createElement(
        EvidenceProvider,
        null,
        createElement(IssueHero, { issue: latestIssue }),
        createElement(IssueLanes, { issue: latestIssue }),
        createElement(WeThink, { issue: latestIssue }),
      ),
    )

    const hasDraftBanner = markup.includes('issue-draft-banner')
    if (latestIssue.status === 'draft' && !hasDraftBanner) {
      throw new Error(
        `newest issue "${latestIssue.id}" is a draft but no element with class "issue-draft-banner" rendered`,
      )
    }
    if (latestIssue.status === 'published' && hasDraftBanner) {
      throw new Error(
        `newest issue "${latestIssue.id}" is published but a "issue-draft-banner" element still rendered`,
      )
    }

    const headingPositions = latestIssue.sections.map((section) => {
      const marker = `id="${LANE_HEADING_IDS[section.lane]}"`
      const at = markup.indexOf(marker)
      if (at === -1) {
        throw new Error(`lane heading ${marker} not found in the rendered issue view`)
      }
      return { lane: section.lane, at, itemCount: section.items.length }
    })

    for (let i = 0; i < headingPositions.length; i++) {
      const start = headingPositions[i].at
      const end = i + 1 < headingPositions.length ? headingPositions[i + 1].at : markup.length
      const slice = markup.slice(start, end)
      const renderedCount = (slice.match(/class="issue-lane__item"/g) ?? []).length
      if (renderedCount !== headingPositions[i].itemCount) {
        throw new Error(
          `lane "${headingPositions[i].lane}" renders ${renderedCount} item(s) but the data has ` +
            `${headingPositions[i].itemCount}`,
        )
      }
    }

    if (latestIssue.status === 'published') {
      const expectedSignature = `Signed by ${latestIssue.weThink.signedBy}${
        latestIssue.weThink.signedOn ? ` · ${formatShortDate(latestIssue.weThink.signedOn)}` : ''
      }`
      if (!markup.includes(expectedSignature)) {
        throw new Error(
          `published newest issue "${latestIssue.id}" does not render the expected signature line "${expectedSignature}"`,
        )
      }
    } else {
      const expectedUnsignedLine = 'Unsigned draft. Nothing here is a judgment until a named person signs it.'
      if (latestIssue.proposed && !markup.includes(expectedUnsignedLine)) {
        throw new Error(
          `draft newest issue "${latestIssue.id}" with a proposal does not render the unsigned-draft line`,
        )
      }
    }
  })
}

// --- Report ---

const FULL_CHECK_COUNT = 14
const PRE_WRITE_CHECK_COUNT = FULL_CHECK_COUNT - 1 // everything but check 8

function printResults(): boolean {
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

/**
 * Everything in main() runs inside one try/catch so that a bug in the
 * reporting path itself — not just inside an individual `check()` — still
 * exits non-zero rather than falling through to a false "passed". An empty
 * or partial `results` array is treated the same way: it is not a pass.
 */
async function main(): Promise<void> {
  if (process.argv.includes('--write')) {
    // (a) Validate the candidate issue on every check that does not itself
    // depend on the manifest BEFORE writing anything. Check 8 is excluded
    // here on purpose: a freshly-drafted published issue has, by
    // construction, no manifest entry yet, and this is the pass that adds
    // one — running check 8 here would fail every legitimate --write.
    console.log('verify:issue --write: validating the candidate issue before writing the manifest...')
    results.length = 0
    await runChecks({ includeLockManifest: false })
    if (results.length !== PRE_WRITE_CHECK_COUNT) {
      console.error(
        `--write aborted: expected ${PRE_WRITE_CHECK_COUNT} pre-write check results, got ${results.length} — the run did not reach a verdict`,
      )
      process.exit(1)
    }
    const preWriteFailed = printResults()
    if (preWriteFailed) {
      console.error(
        '--write aborted: the candidate issue does not pass. Fix the failing check(s) above; nothing was written.',
      )
      process.exit(1)
    }
    console.log('Pre-write validation passed. Proceeding to write the manifest.')

    const manifest = readManifest()
    const published = publishedIssuesOf(issues)
    const nextManifest: LockManifest = { ...manifest }
    let refused = false

    for (const [id, hash] of Object.entries(manifest)) {
      const issue = issues.find((candidate) => candidate.id === id)
      if (!issue) {
        console.error(
          `--write refused: manifest entry "${id}" has no matching issue (would remove an existing entry)`,
        )
        refused = true
        continue
      }
      const currentHash = hashIssue(issue)
      if (currentHash !== hash) {
        console.error(
          `--write refused: manifest entry "${id}" would change from ${hash} to ${currentHash} (would alter an existing entry)`,
        )
        refused = true
      }
    }

    // (b) Append-only against both anchors, not just self-consistency: every
    // entry either anchor already carries must survive into the manifest
    // about to be written, unchanged.
    const anchors = await computeAppendOnlyAnchors()
    const { violations: anchorViolations, infoLines, anchorSummary } = validateAppendOnly(nextManifest, anchors)
    for (const line of infoLines) {
      console.error(`verify:issue --write: ${line}`)
    }
    console.log(`verify:issue --write: append-only anchors — ${anchorSummary}`)
    for (const violation of anchorViolations) {
      console.error(`--write refused: ${violation}`)
      refused = true
    }

    if (refused) {
      console.error(
        '--write aborted: existing manifest entries cannot be altered or removed. Edit issues.lock.json by hand in a reviewed commit if history must change.',
      )
      process.exit(1)
    }

    const added: string[] = []
    for (const issue of published) {
      if (!(issue.id in nextManifest)) {
        nextManifest[issue.id] = hashIssue(issue)
        added.push(issue.id)
      }
    }

    const sorted: LockManifest = {}
    for (const key of Object.keys(nextManifest).sort()) sorted[key] = nextManifest[key]

    writeFileSync(LOCK_PATH, `${JSON.stringify(sorted, null, 2)}\n`)
    console.log(`Wrote ${LOCK_PATH}`)
    console.log(
      added.length > 0
        ? `Added ${added.length} new entr${added.length === 1 ? 'y' : 'ies'}: ${added.join(', ')}`
        : 'No new published issues to add.',
    )

    // Re-run the complete check suite, including check 8, against the
    // manifest that was just written.
    console.log('Re-running the full check suite against the written manifest...')
    results.length = 0
    await runChecks({ includeLockManifest: true })
    if (results.length !== FULL_CHECK_COUNT) {
      console.error(
        `expected ${FULL_CHECK_COUNT} check results, got ${results.length} — the run did not reach a verdict`,
      )
      process.exit(1)
    }
    const postWriteFailed = printResults()
    if (postWriteFailed) {
      console.error('verify:issue FAILED after writing the manifest')
      process.exit(1)
    }
    console.log('verify:issue passed')
    return
  }

  results.length = 0
  await runChecks({ includeLockManifest: true })
  if (results.length !== FULL_CHECK_COUNT) {
    throw new Error(
      `expected ${FULL_CHECK_COUNT} check results, got ${results.length} — the run did not reach a verdict`,
    )
  }
  const anyFail = printResults()
  if (anyFail) {
    console.error('verify:issue FAILED')
    process.exit(1)
  }
  console.log('verify:issue passed')
}

try {
  await main()
} catch (error) {
  const detail = error instanceof Error ? (error.stack ?? error.message) : String(error)
  console.error('verify:issue CRASHED before reaching a verdict:')
  console.error(detail)
  process.exit(1)
}
