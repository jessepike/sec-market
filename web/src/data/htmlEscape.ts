/**
 * Escapes the five characters that matter inside an HTML attribute value or
 * text node — `&`, `<`, `>`, `"`, `'` — in that order, so `&` is escaped
 * first and never double-escapes the entities this function itself just
 * inserted. Used by scripts/prerender.ts to make every dynamic value
 * (an issue's `read`, its id, the site URL) safe to splice into `<title>`
 * and `<meta content="...">` — free text can otherwise carry a `"` that
 * closes the attribute early or a `<`/`&` that breaks the parse.
 */
export function escapeHtmlAttr(value: string): string {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}
