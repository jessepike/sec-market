import type { EvidenceRecord, Issue, ThesisScore } from './types'

/**
 * ISO 8601 week id (`2026-w36`) for a given date. Weeks run Monday–Sunday;
 * week 1 is the week containing the year's first Thursday. Round-trips with
 * `isoWeekSunday`.
 */
export function isoWeekId(date: Date | string): string {
  const source = typeof date === 'string' ? new Date(`${date}T00:00:00Z`) : date
  const target = new Date(
    Date.UTC(source.getUTCFullYear(), source.getUTCMonth(), source.getUTCDate()),
  )
  const dayNr = (target.getUTCDay() + 6) % 7 // Mon=0 .. Sun=6
  target.setUTCDate(target.getUTCDate() - dayNr + 3) // nearest Thursday

  const firstThursday = new Date(Date.UTC(target.getUTCFullYear(), 0, 4))
  const firstDayNr = (firstThursday.getUTCDay() + 6) % 7
  firstThursday.setUTCDate(firstThursday.getUTCDate() - firstDayNr + 3)

  const weekNumber =
    1 + Math.round((target.getTime() - firstThursday.getTime()) / (7 * 24 * 3600 * 1000))

  return `${target.getUTCFullYear()}-w${String(weekNumber).padStart(2, '0')}`
}

/**
 * The ISO date (Sunday) that closes the ISO week named by `id` (`2026-w36`).
 * Round-trips with `isoWeekId`.
 */
export function isoWeekSunday(id: string): string {
  const match = /^(\d{4})-w(\d{2})$/.exec(id)
  if (!match) {
    throw new Error(`Invalid ISO week id: ${id}`)
  }
  const year = Number(match[1])
  const week = Number(match[2])

  const jan4 = new Date(Date.UTC(year, 0, 4))
  const jan4DayNr = (jan4.getUTCDay() + 6) % 7
  const week1Monday = new Date(jan4)
  week1Monday.setUTCDate(jan4.getUTCDate() - jan4DayNr)

  const targetMonday = new Date(week1Monday)
  targetMonday.setUTCDate(week1Monday.getUTCDate() + (week - 1) * 7)

  const sunday = new Date(targetMonday)
  sunday.setUTCDate(targetMonday.getUTCDate() + 6)

  return sunday.toISOString().slice(0, 10)
}

/** The issue's evidence window as ISO date bounds, inclusive on both ends. */
export function windowOf(issue: Issue): { start: string; end: string } {
  return { start: issue.windowStart, end: issue.weekEnding }
}

/**
 * Running thesis score over published issues only. A `no-call` verdict is not
 * a judgment about the thesis, so it counts toward neither `holds` nor
 * `total`. `since` is the `published` date of the earliest issue counted.
 */
export function thesisRunningScore(issues: Issue[]): {
  holds: number
  total: number
  since: string | null
} {
  type PublishedWithThesis = Issue & {
    published: string
    weThink: Issue['weThink'] & { thesis: ThesisScore }
  }

  const published = issues
    .filter(
      (issue): issue is PublishedWithThesis =>
        issue.status === 'published' && issue.published !== null && issue.weThink.thesis !== null,
    )
    .slice()
    .sort((a, b) => a.published.localeCompare(b.published))

  const counted = published.filter((issue) => issue.weThink.thesis.verdict !== 'no-call')
  const holds = counted.filter(
    (issue) =>
      issue.weThink.thesis.verdict === 'holds' || issue.weThink.thesis.verdict === 'strengthens',
  ).length

  return {
    holds,
    total: counted.length,
    since: counted.length > 0 ? counted[0].published : null,
  }
}

/** Lower-case, hyphenated, ASCII slug for a vendor name — the vendor lens key. */
export function vendorSlug(name: string): string {
  return name
    .normalize('NFKD')
    .replace(/[\u0300-\u036f]/g, '') // strip diacritics
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
}

/**
 * Parses the `vendors` query parameter (SEC-031, the vendor lens) out of a
 * `location.search` string, e.g. `"?vendors=crowdstrike,zscaler"`. Returns
 * `null` when the parameter is absent — the lens is inactive and the caller
 * must render unfiltered. Returns an array (possibly empty, when the
 * parameter is present but empty or holds only blank entries) otherwise;
 * an unrecognised slug in that array is not an error, it just matches
 * nothing. Round-trips with `serializeVendorsParam`.
 */
export function parseVendorsParam(search: string): string[] | null {
  const params = new URLSearchParams(search)
  if (!params.has('vendors')) return null
  const raw = params.get('vendors') ?? ''
  return raw
    .split(',')
    .map((slug) => slug.trim())
    .filter((slug) => slug.length > 0)
}

/**
 * Serialises active vendor slugs back into a `vendors` query parameter value.
 * Returns `null` for `null` or an empty list, signalling the caller to drop
 * the parameter entirely rather than write `?vendors=`. Round-trips with
 * `parseVendorsParam`.
 */
export function serializeVendorsParam(slugs: string[] | null): string | null {
  if (slugs === null || slugs.length === 0) return null
  return slugs.join(',')
}

/**
 * Every evidence id an issue cites: lane items, posture deltas, the signed
 * thesis when set, and the machine proposal's thesis when still on a draft.
 */
export function issueEvidenceIds(issue: Issue): string[] {
  const ids = new Set<string>()
  for (const section of issue.sections) {
    for (const item of section.items) {
      for (const id of item.evidenceIds) ids.add(id)
    }
  }
  for (const delta of issue.weThink.postureDeltas) {
    for (const id of delta.evidenceIds) ids.add(id)
  }
  if (issue.weThink.thesis) {
    for (const id of issue.weThink.thesis.evidenceIds) ids.add(id)
  }
  if (issue.proposed) {
    for (const id of issue.proposed.thesis.evidenceIds) ids.add(id)
  }
  return [...ids]
}

/**
 * Archive/index entries for every issue, newest first — the exact ordering
 * `dist/issues/index.json` and the `/issues/` archive page use. Pure: it
 * takes the metadata straight off each issue, with no dependency on `dist`
 * or a site URL, so it is testable without touching the built output.
 */
export function archiveEntriesNewestFirst(
  issues: Issue[],
): Array<Pick<Issue, 'id' | 'weekEnding' | 'published' | 'status' | 'read'>> {
  return issues
    .slice()
    .reverse()
    .map((issue) => ({
      id: issue.id,
      weekEnding: issue.weekEnding,
      published: issue.published,
      status: issue.status,
      read: issue.read,
    }))
}

/**
 * The issues that belong in the RSS feed, newest first by `published`. A
 * draft, or a published issue whose `published` is somehow still null, is
 * never a feed item — this is the one function both `generate-feed.ts` and
 * `verify-dist.ts` should call so "which issues are feed items, in what
 * order" cannot drift between the writer and its own checker.
 */
export function feedIssuesNewestFirst(issues: Issue[]): Issue[] {
  return issues
    .filter((issue): issue is Issue & { published: string } => issue.status === 'published' && issue.published !== null)
    .slice()
    .sort((a, b) => b.published.localeCompare(a.published))
}

/**
 * The `{ issue, evidence }` shape written to `dist/issues/<id>.json`: the
 * issue plus every evidence record it cites, resolved through
 * `issueEvidenceIds` so the JSON copy can never cite a different evidence
 * set than the page itself considers cited.
 */
export function issueJsonCopy(
  issue: Issue,
  evidenceById: Record<string, EvidenceRecord>,
): { issue: Issue; evidence: EvidenceRecord[] } {
  const evidence = issueEvidenceIds(issue).map((id) => {
    const record = evidenceById[id]
    if (!record) {
      throw new Error(`issue "${issue.id}" cites evidence id "${id}" which does not resolve`)
    }
    return record
  })
  return { issue, evidence }
}
