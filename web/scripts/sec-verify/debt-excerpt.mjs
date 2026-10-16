// AUTO-002 Phase 2 (D-91): an 8-K Item 2.03 event quotes the filing's own
// description of the obligation, which states its amount and purpose. Pure
// text extraction, no model: find the Item 2.03 section (or the section it
// incorporates by reference), take its first sentence that names a dollar
// amount. Returns null when no such sentence exists, and the caller falls back
// to the item label.

const ENTITIES = { '&amp;': '&', '&nbsp;': ' ', '&#160;': ' ', '&#8217;': '’', '&rsquo;': '’', '&#8220;': '“', '&#8221;': '”', '&ldquo;': '“', '&rdquo;': '”', '&#8212;': '—', '&mdash;': '—', '&#8211;': '–', '&ndash;': '–', '&quot;': '"', '&#36;': '$' }

export function filingText(html) {
  return html
    .replace(/<(script|style)[\s\S]*?<\/\1>/gi, ' ')
    .replace(/<br\s*\/?>|<\/(p|div|tr|li|h\d)>/gi, '\n')
    .replace(/<[^>]+>/g, ' ')
    .replace(/&[#a-z0-9]+;/gi, m => ENTITIES[m.toLowerCase()] ?? ' ')
    .replace(/[ \t ]+/g, ' ')
    .replace(/\s*\n\s*/g, '\n')
    .trim()
}

const HEADING = /(?:^|\n)(Item\s*(\d\.\d{2})[^\n]{0,160})(?=\n|$)/gi
const isHeading = line => !/incorporated|of this (current )?report/i.test(line)

/** Body of a section: from its last heading line to the next heading line. */
function section(text, item) {
  const heads = [...text.matchAll(HEADING)].filter(m => isHeading(m[1])).map(m => ({ item: m[2], at: m.index + (m[0].startsWith('\n') ? 1 : 0), line: m[1] }))
  const mine = heads.filter(h => h.item === item).at(-1)
  if (!mine) return ''
  const next = heads.find(h => h.at > mine.at)
  return text.slice(mine.at + mine.line.length, next ? next.at : undefined)
}

/**
 * The opening of the filing's own description of the obligation: body lines
 * after the section title and short subheadings, cut at the last sentence end
 * within 450 characters (or at a word boundary). It states the purpose and,
 * usually, the amount; the linked filing has the rest.
 */
export function debtExcerpt(html) {
  const text = filingText(html)
  let body = section(text, '2.03')
  const ref = /Item\s*(\d\.\d{2})[^\n]*?incorporated/i.exec(body)
  if (ref && ref[1] !== '2.03') body = section(text, ref[1])
  const prose = body.split('\n').map(l => l.trim()).filter(l => l.length >= 60).join(' ').replace(/\s+/g, ' ')
  if (prose.length < 60) return null
  if (prose.length <= 450) return prose
  const window = prose.slice(0, 450)
  const ends = [...window.matchAll(/[.;](?=\s+[A-Z“"(])/g)].map(m => m.index + 1).filter(i => i >= 150)
  return ends.length ? window.slice(0, ends.at(-1)) : `${window.slice(0, window.lastIndexOf(' '))} …`
}
