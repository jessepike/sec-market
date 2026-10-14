/**
 * Terms of art a locked issue's own headline (`issue.read`) might carry, each
 * with a plain-language note the front page adds beside the h1 — design-spec
 * v0.3 §3.5. The note is site copy rendered by a component, never written
 * into the issue data itself, so it can never enter an issue's JSON export or
 * the RSS feed (both of which serialise `issue.read` verbatim).
 *
 * Design-spec v0.3 §3.5 gives exact wording only for "the lag call"; the
 * fuller jargon list (content-inventory.md §7) explicitly "waits" for a later
 * pass, so this list stays intentionally short.
 */
export interface JargonNote {
  pattern: RegExp
  note: string
}

const JARGON_NOTES: JargonNote[] = [
  {
    pattern: /\blag call\b/i,
    note:
      "The lag call is this site's refusal to claim that infrastructure spending leads security " +
      'spending by a fixed interval.',
  },
]

/** The first jargon note whose term appears in `text` (case-insensitive), or null if none match. */
export function jargonNoteFor(text: string): string | null {
  for (const entry of JARGON_NOTES) {
    if (entry.pattern.test(text)) return entry.note
  }
  return null
}
