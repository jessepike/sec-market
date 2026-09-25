const SHORT_MONTHS = [
  'Jan',
  'Feb',
  'Mar',
  'Apr',
  'May',
  'Jun',
  'Jul',
  'Aug',
  'Sep',
  'Oct',
  'Nov',
  'Dec',
] as const

const LONG_MONTHS = [
  'January',
  'February',
  'March',
  'April',
  'May',
  'June',
  'July',
  'August',
  'September',
  'October',
  'November',
  'December',
] as const

/** Format an ISO calendar date as `16 Aug 2026`. */
export function formatShortDate(iso: string): string {
  const [year, month, day] = iso.split('-').map(Number)
  const monthLabel = SHORT_MONTHS[month - 1]
  if (!year || !monthLabel || !day) {
    return iso
  }
  return `${day} ${monthLabel} ${year}`
}

/**
 * Format an ISO calendar date as `September 16, 2026` — the long form used by
 * the site-wide "as of" stamp (meta.ts's LAST_UPDATED_DISPLAY, derived from
 * runStatus.lastChecked so every rendered date on the page shares one
 * source — AUTO-001 step 1 fix pass, item 2).
 */
export function formatLongDate(iso: string): string {
  const [year, month, day] = iso.split('-').map(Number)
  const monthLabel = LONG_MONTHS[month - 1]
  if (!year || !monthLabel || !day) {
    return iso
  }
  return `${monthLabel} ${day}, ${year}`
}

/** Calendar week ending on `iso`, formatted `11–17 Aug 2026`. */
export function formatWeekRange(iso: string): string {
  const [year, month, day] = iso.split('-').map(Number)
  if (!year || !month || !day) return iso
  const end = new Date(Date.UTC(year, month - 1, day))
  const start = new Date(end)
  start.setUTCDate(start.getUTCDate() - 6)
  const startLabel = `${start.getUTCDate()} ${SHORT_MONTHS[start.getUTCMonth()]}`
  const endLabel = `${end.getUTCDate()} ${SHORT_MONTHS[end.getUTCMonth()]} ${end.getUTCFullYear()}`
  return startLabel + '\u2013' + endLabel
}
