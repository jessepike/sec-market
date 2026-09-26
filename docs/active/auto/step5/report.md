# Step 5 report — the twelve-domain supplier tracker

SEC-MARKET-AUTO-001, step 5 of `docs/active/autonomy-coverage-plan.md`. Built on branch
`mon/tracker`, worktree `sec-market-wt/tracker`. Never pushed to `preview` or `main`.

## What shipped

- `web/src/data/tracker/domains.ts` — twelve declared domains plus a seven-line
  not-covered list.
- `web/src/data/tracker/suppliers.ts` — 74 suppliers.
- `web/src/data/tracker/events.ts` — 62 dated facts, all inside the trailing
  12-month window (2025-09-25 to 2026-09-25), rungs 1-4 only.
- 117 new evidence records appended to `web/src/data/evidence.ts`, each with a
  source URL and a retrieval date.
- `web/scripts/verify-tracker.ts`, a new build gate wired into `npm run build`
  right after `verify:prints`.
- `web/tests/tracker-data.test.ts`, 13 new tests wired into `npm run test:data`.
- `web/src/components/MarketByDomain.tsx`, `WhatChangedTracker.tsx`,
  `CoverageStatement.tsx`, `ArchiveLinks.tsx` — four new front-page sections
  that replace `MarketPicture`, `PrintGrid`, and the front page's own
  `IssueLanes` instance. None of the three old components was deleted; they
  just have no route rendering them on `/` any more, the same treatment the
  codebase already gives `DomainBoard`'s `TempoSection`.
- `web/src/data/method.ts` and `web/src/components/HowThisWorks.tsx` — added
  a sourcing-ladder table and rewrote the intro to lead with the tracker.
- `web/scripts/verify-integrity.ts` — extended to count the tracker's own
  evidence citations, so the pre-existing unreferenced-evidence gate does not
  false-positive on the new records.
- Updated `web/scripts/prerender.ts` (front page's must-see section ids),
  `web/src/components/Header.tsx` (nav: "Scorecard" to "Market"),
  `web/tests/e2e/smoke.spec.ts`, `web/tests/e2e/lens.spec.ts`, and
  `web/tests/e2e/issue.spec.ts` (the front page's own lane-id list) to match
  the new composition.

## Domain and supplier counts

12 domains, 74 suppliers, 62 events, 117 evidence records.

| Domain | Suppliers |
|---|---|
| ai-security | 7 |
| appsec | 6 |
| cloud | 7 |
| data | 7 |
| email | 7 |
| endpoint-xdr | 6 |
| exposure | 7 |
| identity | 7 |
| managed-security | 7 |
| network-sase | 7 |
| ot-iot | 6 |
| secops | 7 |

Every domain clears the build gate's minimum of 3 suppliers by a wide margin.
Three domains (endpoint-xdr, appsec, ot-iot) sit at 6, the rest at 7.

## How the data was built, and where it needed a second pass

Three research passes (one per roughly four domains) each produced a JSON
extraction of suppliers, events, and evidence, plus their own excluded-fact
list. A merge script cross-checked ids, evidence references, dates, and
banned words before generating the final TypeScript. Two problems only
surfaced once real data hit that script, and both needed a second pass after
the first `verify:tracker` run:

**Palo Alto Networks and CrowdStrike were each researched independently by
more than one pass.** PANW appeared as three separate supplier rows (one
from each pass, covering different domain subsets: endpoint-xdr/secops,
network-sase/cloud, and ai-security), CrowdStrike as two. Consolidated onto
one supplier record per company, with `domainIds` merged across every domain
any pass had assigned it. The now-duplicate events and evidence for the
same underlying fact (the same Q4 FY2026 earnings release, the same CyberArk
acquisition close) were dropped, keeping the first pass's copy. One event
(`EV-panw-cloud-1`) was missed in the first consolidation sweep because it
referenced the deleted `panw-cloud` supplier id rather than `panw`, and was
caught only when `verify-tracker.ts` failed on an unknown-supplier reference;
fixed in a second pass.

**Two Microsoft segments (Entra ID, Defender for Office 365) had no
comparable prior-quarter revenue figure and no real EDGAR filer id.**
Microsoft does not break out either product's revenue in structured filings.
`SupplierRevenue.prior` and `FundingRound.lead` were both made optional
fields (previously required), and the invalid `edgarId: 'msft'` was dropped
from both suppliers — Microsoft as a whole is not one of the 14 companies
the generated `edgarFacts.json` covers, and a segment has no CIK of its own.
`revenue.latest` is unaffected and still cites its own evidence.

**Qualys and Tenable's `revenue.prior` was recorded as `"unverified"`** with
no evidence — a placeholder for a fact the research never actually located.
Dropped the field rather than publish a value marked unverified;
`revenue.latest` for both is sourced and unaffected.

**Three funding-round dates (Aqua Security, BigID, Xage Security) have only
month precision** in their sourced evidence — the press release says
"January 2024," not a specific day. Rather than fabricate a day,
`FundingRound.date` now accepts either a full ISO date or a `"YYYY-MM"`
month, and the display layer (`formatIsoDateOrMonth`) formats the month-only
case as "Jan 2024" instead of throwing on a missing day.

## Facts excluded and why

### At extraction time (42 items, chosen by the research passes before merge)

The great majority are rung-5-only facts (a single trade-press report, no
primary source) that the sourcing ladder does not allow to publish alone, or
figures the research explicitly flagged as unverified against any primary
source:

- **g1 (15 excluded):** SentinelOne's CFO departure, a Microsoft layoffs
  report, Palo Alto Networks post-CyberArk layoffs, Google Mandiant layoffs,
  an Arctic Wolf acquisition and a workforce reduction, Optiv's managed-
  services sale exploration, two Sophos refinancing reports, an eSentire CEO
  change, an Ivanti rating downgrade (internally inconsistent on S&P's own
  scale) plus three further Ivanti distress reports, and a forward-looking
  Tines revenue statement — all rung 5 or explicitly marked unverified in the
  research.
- **g2 (8 excluded):** a Zscaler workforce-reduction report, Palo Alto
  Networks post-acquisition cuts, a Fortinet layoffs rumor (forum chatter),
  an unretrievable CrowdStrike Falcon Cloud ARR figure, unretrievable
  CyberArk Q3 2025 figures, an unverified Delinea ARR figure, Microsoft's
  post-2023 security revenue (last disclosed figure is stale), and a
  BeyondTrust CVE that falls outside the eight distress categories.
- **g3 (19 excluded):** a Varonis stock-decline/litigation item (rung 5 plus
  a plaintiff-firm ad, not a filed case), an unconfirmed Varonis acquisition,
  unverified ARR/ownership figures for BigID, Veeam, and Cohesity (each
  sourced only to a secondary profile or Wikipedia), three unverified Snyk
  items, two suppliers (Checkmarx, Veracode's historic acquisition terms)
  dropped for having no citable source URL anywhere in the research, two
  funding events (Chainguard, Claroty) kept only in `lastRound` — which is
  not rung-gated — but excluded as tracked events, Semgrep dropped for
  having only rung-5 facts inside the window, two Dragos-related items,
  Xage's funding round kept in `lastRound` only, and CalypsoAI and Robust
  Intelligence both dropped to keep the ai-security domain inside range
  while favoring records with fewer unverified gaps.

### During merge and the second verify:tracker pass (30 items)

- 7 events dropped for falling outside the trailing 12-month window
  (2025-09-25 to 2026-09-25): Red Canary's acquisition close, Optiv's rating
  action, LevelBlue/Trustwave's acquisition close, ReliaQuest's funding
  round, Ping Identity's ARR milestone, Abnormal Security's Series D, and
  Barracuda's CEO appointment (also excluded for using the banned word
  "leading").
- 3 duplicate supplier rows (Palo Alto Networks x 2, CrowdStrike x 1) merged
  into one canonical record each, as described above.
- 4 duplicate events and 6 duplicate evidence records for the same
  underlying Palo Alto Networks / CrowdStrike facts, dropped with the
  duplicate suppliers.
- 3 evidence records (Optiv rating action, the deleted panw-cloud headline
  metric, Barracuda's second CEO-appointment source) left with nothing left
  to cite them once their events were dropped, pruned rather than published
  unused.
- 2 invalid `edgarId` fields (Microsoft segments) and 2 unverified
  `revenue.prior` placeholders (Qualys, Tenable) dropped, all described
  above.

None of these 72 total exclusions removed a supplier's `revenue.latest`,
`headlineMetric`, `lastRound`, or `ownership` field — only single dated
events, duplicate rows, or specific sub-fields that had no sourced value.

## What a reader sees

**Desktop (1440px).** The old three-card "market by domain" grid and the top
nav's "Scorecard" link are replaced by full sortable tables, one per domain,
each column a `<button>` with `aria-sort` and a visible sort glyph. Every
domain with two or more comparable public/segment suppliers gets a
median-growth footer row. Below the tables: "What changed in the last 30
days" (a merged, newest-first feed of tracker events and EDGAR filings, each
row sourced), "What this site covers" (domain list with scope lines, supplier
and domain counts, the not-covered list), and links to the issue archive,
thesis, evidence library, and method page. FollowLine and the landscape
section (DomainBoard) are unchanged and sit right after.

**Phone (390px).** Each table collapses to stacked cards — one card per
supplier, each field on its own line with a visible label above the value,
via a data-label/CSS pattern built for this (no existing codebase pattern
did this; the site's other tables use horizontal scroll instead). Confirmed
via screenshot: no horizontal page scroll, no cramped or truncated text,
evidence-source chips wrap inside their column.

**Page height.** Full-page screenshots: 1440px is 15,830px tall (vs. 11,661px
before); 390px is 45,462px tall (vs. 10,549px before). The phone-width
figure is the one worth flagging — stacking 74 suppliers times 6 fields each
into cards is far taller than the desktop table layout, and roughly four
times the phone page's previous height. The content itself is not cramped
or broken at either width (confirmed by direct inspection of the rendered
tables, the "what changed" feed, and the coverage section), but a reader on
phone now scrolls a long way to reach "What this site covers" and the
archive links. This is a real tradeoff of putting twelve full data tables on
one page rather than a defect in the stacking pattern itself — worth a
decision on whether some domains should collapse behind a details element at
phone width in a later pass, which was not built without it being asked for.

## Test results

- `npm run lint` — 0 warnings, 0 errors (130 files).
- `npm run test:data` — 235/235 tests pass, including all 13 new
  tracker-data.test.ts tests.
- `npm run build` — full chain green: verify:edition, verify:panel,
  verify:integrity (5 unreferenced evidence records, all pre-existing and
  under the allowed threshold of 5 — the tracker's own 117 evidence records
  are all referenced), verify:issue, verify:prints (1 pre-existing
  unverified-list warning unrelated to this work — print-crwd-cloud's period
  mismatch, present before this session), verify:tracker, tsc -b, client and
  server builds, prerender, SEO, feed, verify:dist — all pass.
- `npm run test:e2e` — 29/29 Playwright tests pass across chromium/desktop/
  phone projects, including the updated issue.spec.ts front-page composition
  check.
- `npm test` (lint + test:data + build + test:e2e) — full green run.

## Screenshots

In this directory: before-* (live preview URL,
security-market-pulse-git-preview-pikeholdings.vercel.app) and after-* (this
branch's local production build, served locally) — full-page and
first-viewport (-fold), each at 1440px and 390px.

## Uncertain / worth a decision

- The phone-width page height (45k px) is a genuine tradeoff, not a bug —
  flagged above rather than silently shipped.
- print-crwd-cloud's verify:prints warning is pre-existing (from before this
  session) and unrelated to the tracker; left untouched since PrintGrid
  itself is out of this task's scope.
- Three funding-round dates (Aqua, BigID, Xage) only have month precision in
  their source evidence. Handled by making the date field accept a
  "YYYY-MM" month rather than inventing a day — flagging the choice in case
  a different convention is preferred.

## Density pass (coordinator instruction, after this build)

The coordinator looked at `after-fold-1440.png` and the 390px page and called
the presentation too loose for a page meant to be scanned, and the 45,462px
phone page unacceptable. Six changes, all display-layer — no change to the
underlying supplier or event data.

1. **Compact evidence links.** Every cell that used to carry a full-legal-
   name-carrying evidence button now has a small mono "src" mark after the
   figure instead, on the same line. It opens the same evidence drawer; its
   accessible label names the source organization and a retrieval date,
   since the visible mark carries neither.
2. **Short display names.** A new `shortSupplierName()` helper
   (`src/data/tracker/derive.ts`) strips the trailing legal-entity suffix
   ("CrowdStrike Holdings, Inc." to "CrowdStrike") while leaving genuine
   brand words alone ("Palo Alto Networks", "Microsoft Defender for
   Endpoint"). It is a pure display function — `suppliers.ts` and
   `evidence.ts` still carry the full legal name, and the short name's
   `title` attribute exposes the full name on hover.
3. **One-line cells.** Growth reads "+26%" with a muted mono "Q Jul 26"
   period; the own-metric cell reads "ARR $5.84B · Q Jul 26"; ownership
   reads by kind — "Public · CRWD", "Segment of Microsoft", "PE-owned ·
   Thoma Bravo (2022)", "Acquired by ServiceNow · Apr 2026", or "Series D
   $300M · Sep 2026" for a private company's last round. A missing figure is
   an en dash, never a sentence. Column headers shortened to Supplier | Rev.
   growth | Prior q | Own metric | Ownership or last round | Events, 12 mo.
   Growth and prior-quarter figures are right-aligned in tabular numerals;
   row padding is tighter throughout.
4. **A domain index.** Twelve links with supplier counts sit at the top of
   "The market by domain," so a reader jumps straight to a domain instead of
   scrolling past eleven tables to reach the twelfth.
5. **Phone collapse/expand.** Below 640px, each supplier is one tappable row
   — short name plus its latest revenue growth, or its ownership state when
   there is no growth figure. Tapping reveals the rest of that supplier's
   cells in place. This is a real `<button aria-expanded>` with genuine
   React state (`DomainTable`'s `expanded` set in `MarketByDomain.tsx`), not
   a CSS-only trick, so it works by keyboard and is announced correctly to a
   screen reader — the button's accessible name includes both the supplier
   name and the summary figure, not just the name.
6. **"What changed" rows.** Each line is now a mono date, the short supplier
   name, the factual text, and a compact source link — the same treatment as
   the domain tables.

### Verification

- `npm run lint` — 0 warnings, 0 errors (fixed one unused-variable warning
  in a new date helper along the way).
- `npm run test:data` — 240/240 pass, including 5 new tests for the
  density-pass display helpers (`shortSupplierName`, the compact date/
  quarter formatters, `formatHeadlineCompact`, `formatOwnershipCompact`
  across all five ownership kinds).
- `npm run build` — full chain green, including `tsc -b` with no type
  errors.
- `npm run test:e2e` — 1 pre-existing test broke and was fixed, not
  skipped: `smoke.spec.ts`'s "opens attributed evidence" test matched
  `getByRole('button', { name: /Fortinet/ })` unscoped, which used to find
  only the Landscape section's evidence button. The tracker's own new
  per-row toggle button is also named "Fortinet ..." (its short name has no
  legal suffix to strip) and now sits earlier in the DOM, so the unscoped
  `.first()` started hitting the wrong button. Scoped the locator to
  `#landscape`, matching how the same file already scoped its assertions a
  few lines above. 29/29 pass after the fix.
- A second CSS pass was needed to hit the phone target: the collapsed-row
  pattern's `data-label` styling was printing a "SUPPLIER" label above every
  one of the 74 row-toggle buttons, which is redundant (the button is the
  row) and cost real height. Suppressing that one label brought the phone
  page from 15,262px to 13,837px.

### Page height

| | Before density pass | After density pass |
|---|---|---|
| 1440px, full page | 15,830px | 10,131px |
| 390px, full page | ~45,462px | 13,837px |

Both are well under the coordinator's phone target of 15,000px, and the
desktop page is also markedly shorter — the compact cells and tighter
padding do the same work at both widths.

### Screenshots

In this directory: `after2-1440.png`, `after2-390.png`, `after2-fold-
1440.png`, `after2-fold-390.png` — captured from a local production preview
of this branch's build (`vite preview`), same capture pattern as the
original `before-`/`after-` set.

### Data-quality note (not fixed, flagged instead)

One supplier's (Cyera) `lastRound.stage` field holds a full descriptive
sentence ("Growth-equity investment (reported as a Series G extension)")
rather than a short stage label like "Series D," so its ownership cell reads
as a full sentence rather than the compact form the other private
companies get. This is a pre-existing shape in the source data, not a
formatting bug — `formatOwnershipCompact()` renders whatever `stage` holds.
Fixing it means editing supplier data, which is outside this pass's
display-only scope; noting it here rather than touching the data.
