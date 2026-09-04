import type { Issue } from '../types'

/**
 * Opening issue. Skeleton only — four empty lanes, unsigned, drafted before the
 * first real gather. A later task fills it in from a real gather; this file's
 * shape is what `verify:issue` and the issue components are built against.
 */
export const issue2026w36: Issue = {
  id: '2026-w36',
  weekEnding: '2026-09-06',
  windowStart: '2026-08-24',
  published: null,
  status: 'draft',
  read: 'Opening issue. Draft, awaiting the gather.',
  sections: [
    { lane: 'formation', items: [] },
    { lane: 'absorption', items: [] },
    { lane: 'prints', items: [] },
    { lane: 'capital', items: [] },
  ],
  weThink: {
    summary: '',
    postureDeltas: [],
    thesis: null,
    noCalls: [],
    signedBy: null,
    signedOn: null,
  },
  proposed: null,
  sources: { readable: 0, unreadable: [] },
}
