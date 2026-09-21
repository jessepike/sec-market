import type { Issue } from '../src/data/types.ts'

/**
 * Quotes a string as this codebase's issue files do: single quotes by
 * default, double quotes only when the string itself contains a single quote
 * and no double quote (so an apostrophe in prose never needs escaping).
 */
function quoteString(value: string): string {
  const hasSingle = value.includes("'")
  const hasDouble = value.includes('"')
  const useDouble = hasSingle && !hasDouble
  const quote = useDouble ? '"' : "'"
  const escaped = value
    .replace(/\\/g, '\\\\')
    .replace(new RegExp(quote, 'g'), `\\${quote}`)
    .replace(/\n/g, '\\n')
  return `${quote}${escaped}${quote}`
}

/**
 * Renders any JSON-shaped value — which is what a signed `Issue` is — as a
 * TypeScript object/array literal: unquoted keys (every field name in this
 * data model is a plain identifier), 2-space indentation, trailing commas.
 * `undefined` values are dropped from an object the same way `JSON.stringify`
 * drops them, so an absent optional field (`vendors`, `domainId`, `quiet`,
 * ...) stays absent rather than becoming a literal `undefined`.
 */
export function tsLiteral(value: unknown, indent = 0): string {
  const pad = '  '.repeat(indent)
  const padInner = '  '.repeat(indent + 1)

  if (value === null) return 'null'
  if (typeof value === 'string') return quoteString(value)
  if (typeof value === 'number' || typeof value === 'boolean') return String(value)

  if (Array.isArray(value)) {
    if (value.length === 0) return '[]'
    const items = value.map((item) => `${padInner}${tsLiteral(item, indent + 1)},`).join('\n')
    return `[\n${items}\n${pad}]`
  }

  if (typeof value === 'object') {
    const entries = Object.entries(value as Record<string, unknown>).filter(([, v]) => v !== undefined)
    if (entries.length === 0) return '{}'
    const body = entries.map(([key, v]) => `${padInner}${key}: ${tsLiteral(v, indent + 1)},`).join('\n')
    return `{\n${body}\n${pad}}`
  }

  throw new Error(`sign-issue: cannot serialize a value of type "${typeof value}" into a TS literal`)
}

/** The `issue<id-without-dash>` export name convention every issue module follows. */
export function issueExportName(id: string): string {
  return `issue${id.replace('-', '')}`
}

/**
 * The complete `web/src/data/issues/<id>.ts` module source for a signed
 * issue, regenerated whole rather than patched — the lock manifest hashes
 * `JSON.stringify(issue)` at import time, not the file text, so a clean
 * regeneration is exactly as sound as an in-place edit and keeps the writer
 * simple. Matches `index.ts`'s `import { issueYYYYwNN } from './YYYY-wNN'`
 * convention and carries no import the file does not use, so it stays
 * lint-clean.
 */
export function renderIssueModule(issue: Issue, authorName: string): string {
  const exportName = issueExportName(issue.id)
  const lines = [
    "import type { Issue } from '../types'",
    '',
    '/**',
    ` * Signed by ${authorName} on ${issue.published}, by approval of the weekly pull`,
    ' * request (SEC-MARKET-PUBLISH-001 §2). Machine-authored: `read`, the four lane',
    ' * sections and `sources`. `proposed` is nulled on publish so the page carries',
    ` * one judgment, ${authorName}'s.`,
    ' */',
    `export const ${exportName}: Issue = ${tsLiteral(issue, 0)}`,
    '',
  ]
  return lines.join('\n')
}
