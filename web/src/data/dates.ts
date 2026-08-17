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
