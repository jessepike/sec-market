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

/** Format an ISO calendar date as `16 Aug 2026`. */
export function formatShortDate(iso: string): string {
  const [year, month, day] = iso.split('-').map(Number)
  const monthLabel = SHORT_MONTHS[month - 1]
  if (!year || !monthLabel || !day) {
    return iso
  }
  return `${day} ${monthLabel} ${year}`
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
