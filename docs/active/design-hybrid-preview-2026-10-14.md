# Approved hybrid preview — 14 October 2026

Authority: D-82. Jesse selected the recommended October 2 bake-off hybrid and explicitly authorized implementing and pushing it to the existing Vercel preview. Production remains gated separately.

## Implementation

- `MarketDesk.tsx` mounts on `/` with Opus's hierarchy: dated change log, six event-count filters, timeline, public-supplier details and domain browser. No owner-read placeholder or median badge.
- The first screen adds Fable's neutral latest/prior revenue-growth plot, alphabetical by default with reader-selected numeric sorting. Company totals only; segments and ARR are excluded. Labels preserve source percentage strings and link to evidence; supplier records provide exact values, periods and sources.
- Sol's fact layout keeps labels, values, periods, as-of dates and source links together. Native supplier dialogs preserve exact SEC dollar values, derived-quarter flags, ownership announcement/close dates, event text, funding qualifiers and source links.
- Timeline monthly groups use native buttons (28px desktop, 40px phone minimum), visible focus, full accessible names and selectable dated/source-linked event lists. A complete chronological list is also available. Endpoint months are explicitly partial.
- Astra's phone economy: first four changes initially visible, full log available, compact growth view with all suppliers one tap away, collapsed public-supplier facts and a native domain selector. All twelve domains and every tracked supplier remain in the source-rendered page.

## Data boundary

The app imports repository tracker and generated filing data, not prototype JSON. The base has 74 suppliers, 12 domains, 116 events, 16 SEC filers and 18 public-company revenue comparison rows. Counts are derived, not typed into the UI. All recent events and latest filings survive grouping exactly once. Financial source data is unchanged. Snapshot date is 2 October 2026; no collection or freshness advancement is claimed.

## Validation

- Lint: zero warnings/errors. TypeScript and the complete `npm run build` validation chain pass.
- 255 data tests pass, including filing retention, exact growth values/negative growth, corrected filer inclusion and exhaustive event-lane checks.
- Browser checks cover 1440/390 layouts, horizontal page overflow, first-screen sourced content, neutral comparison/sorting, supplier dialog focus/Escape return, sources, keyboard timeline activation and full change-log expansion. Existing archive/correction/thesis checks are retained.
- Local built static server is used for QA: Vite preview serves its HTML fallback as the Vercel-edge analytics script, causing an unrelated parse error. A static 404 for this non-local asset avoids that local mismatch; deployed Vercel is verified after push.
- Pre-existing build warnings remain: five unreferenced evidence records, the archived `print-crwd-cloud` period ambiguity on its unverified list, and the large client chunk. No new financial validation failure.

Preview deployment and deployed-page confirmation are pending at this source commit. A deployment receipt follows the Git-triggered Vercel build reaching Ready.
