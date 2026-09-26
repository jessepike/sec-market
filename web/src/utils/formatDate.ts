/** Format YYYY-MM-DD without local timezone shift. */
export function formatIsoDate(dateStr: string): string {
  const [year, month, day] = dateStr.split('-').map(Number)
  return new Date(Date.UTC(year, month - 1, day)).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    timeZone: 'UTC',
  })
}

/**
 * Format a date that may only have month precision ("YYYY-MM") because the
 * sourced evidence never gave an exact day — e.g. a funding round covered
 * only by a press release that says "January 2024". Falls back to
 * formatIsoDate for a full "YYYY-MM-DD" value.
 */
export function formatIsoDateOrMonth(dateStr: string): string {
  if (/^\d{4}-\d{2}$/.test(dateStr)) {
    const [year, month] = dateStr.split('-').map(Number)
    return new Date(Date.UTC(year, month - 1, 1)).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      timeZone: 'UTC',
    })
  }
  return formatIsoDate(dateStr)
}
