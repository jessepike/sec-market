import type { Reconfirmation } from '../src/data/types.ts'
import { tsLiteral } from './signIssueRender.ts'

/**
 * The complete `web/src/data/reconfirmations.ts` module source, regenerated
 * whole from the full list — existing entries plus any this run adds — the
 * same way `signIssueRender.ts#renderIssueModule` regenerates a signed
 * issue's module rather than patching it. A clean regeneration cannot
 * silently corrupt or reorder an earlier entry, which matters here because
 * the file is meant to be append-only.
 */
export function renderReconfirmationsModule(reconfirmations: Reconfirmation[]): string {
  const lines = [
    "import type { Reconfirmation } from './types'",
    '',
    '/**',
    ' * Append-only record of owner-approved reconfirmations',
    ' * (SEC-MARKET-PUBLISH-001 §4.3). Never edit or remove an entry once',
    ' * written — add a new one instead. Regenerated whole by',
    ' * scripts/sign-issue.ts (via scripts/reconfirmLogic.ts and',
    ' * scripts/reconfirmRender.ts) when the owner signs `reconfirm`; every',
    ' * existing entry above is carried forward unchanged.',
    ' */',
    `export const reconfirmations: Reconfirmation[] = ${tsLiteral(reconfirmations, 0)}`,
    '',
  ]
  return lines.join('\n')
}
