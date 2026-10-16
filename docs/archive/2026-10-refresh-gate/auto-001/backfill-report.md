# Full-year backfill verification report

Verifies the automated collector run described in `docs/archive/2026-10-refresh-gate/auto-001/collect-brief.md`, run as
seven sequential batches (`.collect` receipts `receipt-1.json` through `receipt-7.json`, stamped
2026-09-26T17:05Z through 2026-09-26T17:30Z) covering all 74 declared suppliers with a since-date of
2025-09-26. This report is the human-facing record of that verification pass, done against the
branch `data/collect-backfill` in the worktree at `sec-market-wt/backfill`.

## What was checked

For every new or changed field in `web/src/data/tracker/events.ts`, `web/src/data/tracker/
suppliers.ts`, and `web/src/data/evidence.ts` (25 new events, 23 new evidence records, one supplier
ownership update for Dragos, one supplier headline-metric update for Okta), the evidence URL was
fetched directly with `curl` (SEC filings with the required descriptive User-Agent) or, where a
site's bot protection blocked `curl` outright (GlobeNewswire), with a single independent fetch used
only to confirm wording and date, never to author new text. Every fetched document was checked
against the tracker's text for: does the source say what the event text says, is the date right, is
the event type right, is the URL the specific document rather than a home page or index, is the
source's rung (1 SEC filing, 4 confirmed primary corporate action) allowed to publish alone, and
does the text carry no interpretation.

## Result: 25 verified, 0 fixed, 0 removed

Every one of the 25 new events and their 23 supporting evidence records checked out exactly against
the primary source — same facts, same dollar figures, same dates, same names. Specific checks worth
noting:

- All 15 rung-1 events (SEC 8-Ks, a 6-K, a 10-Q, and a 10-K note) matched their filings word for
  word on the quoted language, and every filing date was independently confirmed against EDGAR's own
  filing-index page, not just the document's internal date.
- The three Zscaler acquisitions (SPLXAI $40.6M, SquareX $112.8M, Symmetry Systems $152.9M) and the
  Zscaler exec-change event correctly share evidence records the way the brief allows when one
  primary document supports multiple facts — confirmed each dollar figure and restricted-stock
  amount against the 10-K's Note 6 text directly.
- The 10 rung-4 events (company press releases and newsroom posts) all matched their source's exact
  wording. One evidence record (Delinea/StrongDM completion, GlobeNewswire) could not be fetched
  with `curl` — GlobeNewswire returned no response after three attempts, a known bot-protection
  block — and was instead confirmed through a single independent fetch, which returned the same
  opening sentence and date the tracker already carried.
- No event used a rung-5 (trade-press-only) source, no event or evidence text contained any of the
  ten banned judgment words, no event id or evidence id collided with an existing one, and every
  `evidenceIds` reference in the new events resolves to a real evidence record with a URL and a
  retrieval date.
- The Okta headline-metric update correctly switched from GAAP revenue (which belongs to the EDGAR
  runner) to the company's own cRPO figure, and both the $2.585 billion cRPO and $4.858 billion RPO
  figures, with their 14% and 17% growth rates, matched Okta's Q2 FY2027 results release exactly.
- The Dragos ownership update's closing date (September 16, 2026) matched Accenture's own release
  note exactly, and has a matching acquisition event in events.ts, satisfying the build gate that
  requires a trailing-12-month ownership change to also appear as an event.

No fact required a wording, type, or date fix, and no fact was removed.

## Recall spot-check: no gaps found

Checked eight suppliers across eight different domains — Rapid7 (exposure), Sophos (endpoint-xdr),
Optiv (managed-security), Cyera (data), Armis (ot-iot), CyberArk (identity), Fortinet (network-sase),
and Snyk (appsec) — for material facts (funding, acquisitions, layoffs, ratings actions, CEO/CFO
changes, divestitures) from the last 12 months, independent of what the collector run already wrote.

- **Rapid7**: confirmed against EDGAR directly — no 8-K after August 31, 2026 (already the tracker's
  newest event); nothing missing.
- **Optiv**: checked Optiv's own newsroom; the only unrecorded items were a Chief Revenue Officer
  appointment (outside the CEO/CFO category asked for) and stories already covered by the tracker's
  debt and divestiture events.
- **Cyera**: checked Cyera's full press-release archive; found two acquisitions (Otterize, Trail
  Security) and two board appointments (Steffan Tomlinson, Frank Slootman) not in the tracker, but
  both acquisitions predate the trailing-12-month window (mid-2025 and 2024) and both board seats are
  not CEO/CFO changes at Cyera itself. Nothing missing inside the window.
- **CyberArk**: checked every PANW 8-K mentioning CyberArk since the acquisition closed; the only one
  beyond what's tracked is a boilerplate convertible-note default-settlement notice, not a material
  fact in the requested categories. Nothing missing.
- **Fortinet**: checked EDGAR directly — every 8-K in the last 12 months is an earnings release
  (Item 2.02) or a shareholder-meeting result (Item 5.07); no acquisition, layoff, or exec-change
  filing exists. The tracker's zero events for Fortinet in this window is accurate, not a gap.
- **Snyk**: checked Snyk's news archive; the only acquisition found (Invariant Labs) is dated June
  2025, before the window. The tracker's zero events for Snyk in this window is accurate.
- **Sophos**: sophos.com and news.sophos.com refused every connection attempt (HTTP/2 stream errors,
  matching what the collector run itself hit on other Akamai-protected sites). Checked Sophos's
  owner Thoma Bravo's press page as a near-primary alternate; found only pre-window Secureworks
  acquisition items (October 2024, February 2025). Could not independently confirm there is nothing
  newer directly from Sophos — flagging this as an open gap in the recall check itself, not a known
  missing fact.
- **Armis**: armis.com returned HTTP 403 on every attempt. The tracker's two Armis events (ServiceNow's
  announced intent and closed acquisition) are both sourced from ServiceNow's own SEC filings, the
  strongest available source, so this block did not cost a fact — but, as with Sophos, direct
  confirmation from Armis's own site was not possible.

No new fact was added as a result of this check, because nothing found inside the trailing-12-month
window had an allowed primary source that the tracker was missing.

## `collectState.json`

Set to record that this run, taken as the union of all seven batches, covered all 74 declared
suppliers (the seven `collectOnly` lists partition the full supplier roster exactly, with no gaps
and no overlaps) with no restriction in effect: `lastSuccessfulCollectDate` is `2026-09-26`,
`restrictedTo` is `null`, and `lastRunAt`/`collectorRun.at` carry the seventh and final batch's
timestamp.

`collectorRun.failedSources` carries the union of the 30 raw failures logged across the seven
receipts, minus the 5 that the run itself recovered by reading a different copy of the same
disclosure (Check Point's SEC 6-K in place of its blocked investor site; BigID's site map in place
of its blocked press-release path; company-hosted copies of the Exabeam and Cyera releases in place
of a blocked Business Wire mirror; Zscaler's own 10-K in place of its blocked IR press release; and
Zenity's site map in place of its blocked newsroom index) — each of those facts is published and
sourced from the recovered copy, so listing the original blocked URL as an outstanding failure would
overstate what's actually missing. The remaining 25 entries are sources where no allowed alternate
was found and, in several cases, a candidate fact (Ivanti's reported S&P downgrade, a Proofpoint
layoff report, a Proofpoint term-loan amendment, an Upwind Series C round) was accordingly left
unpublished rather than sourced to trade press alone.

## Test status

`npm test` (lint, `verify:tracker`, full build including prerender/SEO/feed generation, `verify:dist`,
and the 30-test Playwright e2e suite across desktop/phone/chromium projects) passed clean on the
second run. The first run's one e2e failure (`smoke.spec.ts` expecting the new unrestricted run-status
line but finding an old restricted-run message) was a stale `serve -l 4173 dist` process left running
in the OrbStack VM from an earlier session, reused by Playwright's `reuseExistingServer: true`
setting rather than a defect in this data; killing that process and rerunning produced a clean pass
with no code or data change.
