// AUTO-002 Phase 2 (D-91): an 8-K Item 2.03 event quotes the filing's own
// description of the obligation. Pure text extraction, no model: find the
// Item 2.03 section (or the Item 1.01 section it incorporates by reference),
// drop the item title and leading subheadings, join the hard-wrapped lines,
// and take the opening prose up to 450 characters. The
// quote is not certified and may not state an amount; the linked filing has
// the full text. Returns null when there is no such prose, and the caller
// falls back to the item label.

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
// Wrapped lines of the Item 2.03 / 1.01 titles, which are not description.
const TITLE = /Direct Financial Obligation|Off-Balance Sheet Arrangement|Entry into a Material Definitive Agreement/i
const isHeading = line => !/incorporated|of this (current )?report/i.test(line)

/** Body of a section: from its last heading line to the next heading line. */
function section(text, item) {
  const heads = [...text.matchAll(HEADING)].filter(m => isHeading(m[1])).map(m => ({ item: m[2], at: m.index + (m[0].startsWith('\n') ? 1 : 0), line: m[1] }))
  const mine = heads.filter(h => h.item === item).at(-1)
  if (!mine) return ''
  const next = heads.find(h => h.at > mine.at)
  return text.slice(mine.at + mine.line.length, next ? next.at : undefined)
}

/** Body lines with the item title, wrapped title lines and leading subheadings removed, joined into prose. */
function prose(body) {
  const lines = body.split('\n').map(l => l.trim()).filter(l => l && !TITLE.test(l))
  // A leading subheading ("Indenture and Notes") is short and has no closing punctuation.
  while (lines.length && lines[0].length < 80 && !/[.;:,)”’"]$/.test(lines[0])) lines.shift()
  return lines.join(' ').replace(/\s+/g, ' ').trim()
}

const REFERENCE = /incorporated (?:herein )?by reference/i

/**
 * The opening of the filing's own description of the obligation: the Item 2.03
 * text, or the Item 1.01 text when 2.03 only incorporates 1.01 by reference,
 * cut at the last sentence end within 450 characters (or at a word boundary).
 * Filings wrap lines mid-sentence, so lines are joined before anything is read.
 */
export function debtExcerpt(html) {
  const text = filingText(html)
  const own = section(text, '2.03')
  const joined = own.replace(/\s+/g, ' ')
  const ref = /Item\s*(\d\.\d{2})[^.]*?incorporated/i.exec(joined)
  let flat = ref || REFERENCE.test(joined) ? (ref?.[1] === '1.01' ? prose(section(text, '1.01')) : '') : prose(own)
  if (REFERENCE.test(flat.slice(0, 200))) return null
  flat = flat.replace(/[“”]/g, m => (m === '“' ? '‘' : '’'))
  if (flat.length < 60) return null
  if (flat.length <= 450) return flat
  const window = flat.slice(0, 450)
  const ends = [...window.matchAll(/[.;](?=\s+[A-Z‘"(])/g)].map(m => m.index + 1).filter(i => i >= 150)
  return ends.length ? window.slice(0, ends.at(-1)) : `${window.slice(0, window.lastIndexOf(' '))}…`
}
