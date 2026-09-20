import type { Issue } from '../types'
import { issue2026w36 } from './2026-w36'
import { issue2026w37 } from './2026-w37'

/** Append-only issue history, newest last. */
export const issues: Issue[] = [issue2026w36, issue2026w37]

if (issues.length === 0) {
  throw new Error('Issue history is empty')
}

export const publishedIssues: Issue[] = issues.filter((issue) => issue.status === 'published')

export const latestIssue: Issue = issues[issues.length - 1]

export const issueById: Record<string, Issue> = Object.fromEntries(
  issues.map((issue) => [issue.id, issue]),
)
