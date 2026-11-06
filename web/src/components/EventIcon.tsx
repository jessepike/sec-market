/** A small fixed icon per event type, paired with the type's hue. Decorative; the label carries the meaning. */
const PATHS: Record<string, string> = {
  // two arrows merging
  ownership: 'M2 3h4l3 5-3 5H2M14 8H9',
  // coin stack
  funding: 'M3 5c0-1.1 2.2-2 5-2s5 .9 5 2-2.2 2-5 2-5-.9-5-2zm0 0v6c0 1.1 2.2 2 5 2s5-.9 5-2V5M3 8c0 1.1 2.2 2 5 2s5-.9 5-2',
  // bar chart
  results: 'M3 13V8M8 13V4M13 13V6M2 13h12',
  // scissors-like cut: descending step
  restructuring: 'M2 4h4v4h4v4h4',
  // document with lines
  debt: 'M4 2h6l3 3v9H4zM6 8h5M6 11h5',
  // person
  leadership: 'M8 7a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5zM3 14c0-2.8 2.2-5 5-5s5 2.2 5 5',
}
export function EventIcon({ group }: { group: string }) {
  const d = PATHS[group]
  if (!d) return null
  return <svg className="event-icon" viewBox="0 0 16 16" width="14" height="14" aria-hidden="true" focusable="false"><path d={d} fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" /></svg>
}
