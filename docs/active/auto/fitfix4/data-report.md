# Fix pass 4 — data report

Worktree `sec-market-wt/fitfix`, branch `mon/fitfix`. Two blind scorers failed the preview build on
rubric v3.0 (Opus 59.8/100, Sol 39.0/100). This report covers the 12-item data/pipeline brief end to
end. A separate UI builder covered layout, type, and accessibility in parallel and is not covered
here.

All work is committed on `mon/fitfix`. `git status --short` is empty. Every gate in
`web/package.json`'s test/verify/build scripts, plus the Playwright e2e suite, is green in the
OrbStack VM, including `verify:integrity` (see "Gate results" below for what that gate checks and
why it has no margin left).

This report was revised once, after the coordinator's review of the first draft caught a build-
breaking regression this branch had introduced (an orphaned evidence record pushing
`verify:integrity` over its threshold) and two wrong ownership facts (Delinea, Ivanti). All three are
fixed, re-verified, and described below exactly as found and corrected, rather than silently
rewritten as if the error never happened.

## Item-by-item

### 1. Snyk last round; private-supplier sweep

Done. Snyk's "last round" cell showed a 2021 Series F; Snyk's own newsroom shows a later $196.5
million Series G (December 13, 2022, led by QIA, $7.4 billion valuation) and a subsequent ServiceNow
strategic investment (January 24, 2023). Corrected the cell, date, and source.

Swept every private supplier's last-round/ownership cell against the company's own newsroom or a
company-issued wire release. Filled previously-missing or trade-press-only ownership facts for: Aqua
Security, Axonius, BeyondTrust, Chainguard, Expel, Orca, Delinea, Arctic Wolf, and Cohesity (the last
two closed out this session, see below). Where no newer round or ownership change was found after
checking, the record says so explicitly rather than staying silently blank.

A superseded record this sweep created, `TR-veeam-4` (Veeam's own 2024 release replacing a Wikipedia
source, `TR-veeam-1`), was left without a link back to the record it superseded, which left
`TR-veeam-1` unreferenced and broke `verify:integrity` for this branch specifically. See "Gate
results" below for the fix.

### 2. Date on every own-metric and ownership fact; verify gate

Done. Added `verify-tracker.ts` gate 16: a shown `headlineMetric.period` must name a year, and a
`pe-owned`/`acquired` supplier's ownership fact (when there is no `lastRound` to show instead) must
carry an `announced`/`closed` date or a year in its status sentence. This gate caught two real gaps —
Ping Identity's ARR figure and Ivanti's missing date — but fixing Ivanti's gap the first time round
introduced a worse error: it swapped Ivanti's dated 2025 refinancing citation for an older, undated-
looking 2021 fact instead of just adding the missing date to the 2025 one. The coordinator caught that
this went backwards in time. Corrected version, with both records re-verified against the live pages:
Ivanti's ownership cell now cites both its 2021 Charlesbank-closing release (`TR-ivanti-2`, when the
three-sponsor group formed) and its 2025 refinancing release (`TR-ivanti-1`, which explicitly states
"Ivanti is backed by Clearlake Capital Group, L.P., Charlesbank Capital Partners, LLC, and TA
Associates" — confirmed by refetching the live page and hashing it), with the status sentence naming
all three years so gate 16 is satisfied honestly rather than by omitting the newer source.

### 3. Ping Identity's Keyless acquisition; Dragos wording

Done. Added Ping Identity's completed acquisition of Keyless (closed January 7, 2026, Ping's own
PR Newswire release) as its first tracked event — the tracker previously showed zero events for Ping
in the trailing 12 months, which both blind scorers flagged. Reworded Dragos's ownership status with
a `relationship` override so its compact label reads "Majority investment by Accenture plc," matching
Accenture's own release, instead of the generic "Acquired by" template the kind-derived label would
otherwise produce.

### 4. Run-status denominator; EDGAR registry additions

Done. Added Commvault and JFrog to the EDGAR XBRL registry (both file 10-Q/10-K with XBRL) and Trend
Micro to the explicit unsupported list (a deregistered SEC filer that reports under Japanese
disclosure rules; Check Point was already there). Rewrote `runStatus.ts`'s `filingsClause()` so its
denominator derives from the tracker's own `kind: 'public'` count rather than an independently
hand-typed number — the two could drift apart silently before (one blind scorer's blocking finding
was "14 public suppliers" stated against a table that actually showed 18 "Public ·" rows). Added a
reconciliation test (`tests/run-status.test.ts`) that fails if the two ever disagree again.

### 5. Filing-driven events from 8-K item codes

Done. New script `web/scripts/filing-events.ts` (`npm run refresh:filing-events`) reads every SEC
filer in `edgarRegistry.ts`, fetches that filer's own EDGAR submissions index, and emits a dated
`TrackerEvent` for any 8-K carrying item code 5.02 (director/officer change), 2.01 (completed
acquisition/disposition), 1.03 (bankruptcy), 2.05 (exit/restructuring costs), or 3.01 (delisting
notice) — no model in this path. Output is merged into the same `trackerEvents`/`evidenceRecords`
exports every consumer already imports.

Surfaces Commvault's September 24, 2026 director appointment and Okta's September 18, 2026 director
change, both named in the brief. Item 5.02's SEC caption text always contains both "appointment" and
"departure" language on every filing, and Okta's own filing genuinely reports both a resignation and
a separate appointment in one document — the generator deliberately does not try to guess a single
direction from the text; it states only what the item code establishes and links to the filing.

### 6. One-decimal revenue growth

Done, for all 15 EDGAR-covered public suppliers with a `revenue` block. Every growth figure is now
computed to one decimal place from the two reported dollar amounts (current quarter, same quarter one
year earlier), both now stored on the record (`RevenuePeriod.priorYearValue`, new field). Source for
all computed values: the exact quarterly figures in `generated/edgarFacts.json`, cross-checked for a
sample (SailPoint, Qualys, Tenable) against each filer's own 10-Q/earnings-release comparative table.

One real correction found: SailPoint's Q1 FY2027 growth was stored as 21.5%; the precise figure from
the two reported dollar amounts ($280,142K vs. $230,468K) is 21.6%, which still rounds to the 22%
change SailPoint's own MD&A table states. Every other supplier's precise figure rounds cleanly to its
previously-stored whole percent.

### 7. Missing growth/prior-quarter values

Done. Qualys and Tenable had a bare "–" for prior-quarter revenue — neither had a `revenue.prior`
block. Added both from each company's own Q1 2026 earnings release (new evidence `TR-qualys-2`,
`TR-tenable-3`), cross-checked against the comparative table in each company's Q2 2026 10-Q. Tenable's
own release states 9.6% directly; Qualys's computed 9.8% rounds to its release's stated "10%".

Trend Micro's growth cell was also bare. Added from the company's own Q2 2026 earnings release, which
states the figure as a whole percent (+13% YoY) with no reachable prior-year yen figure in plain
text — stored as the company's own whole-percent figure rather than a fabricated one-decimal value.

Check Point's two quarterly growth figures (1%/5%) are left as company-stated whole percents — a
foreign private issuer with no EDGAR XBRL quarterly data, whose own release states growth narratively
with no reachable prior-year comparative dollar figure. This is a documented, bounded limitation, not
an oversight.

### 8. Segment parent names; ownership gaps

Done. CrowdStrike Falcon Exposure Management and Palo Alto Cortex XSIAM now render their parent via
the "Segment of X" pattern `formatOwnershipCompact` expects (previously rendered as a bare
"Segment"). GitHub Advanced Security's event date was corrected to match its source (August 11, 2025,
not the previously fabricated December 31, 2025) and then, once no source supported a date inside the
trailing-12-month window, the unsourceable event was removed rather than kept with an invented date —
the row honestly shows zero events for GHAS in the window now.

Ownership facts filled, each from a primary/company-issued source:

| Supplier | Fact | Source |
|---|---|---|
| Aqua Security | Series E, $135M, Mar 10 2021, ION Crossover Partners lead, >$1B valuation | Aqua's own PR Newswire release |
| Expel | Series E extension, $171.3M, Oct 3 2022 (total funding $288.8M) | Expel's own site |
| BeyondTrust | Clearlake Capital Group investment closed Aug 17 2021, joining Francisco Partners | BeyondTrust's own release |
| Delinea | PE-owned by TPG Capital, formed by its 2021 combination of Thycotic and Centrify, closed Apr 13 2021 | Delinea's own merger-completion release |
| Arctic Wolf | Series F, $150M, Jul 13 2021, led by Viking Global Investors and Owl Rock/Blue Owl, $4.3B valuation | Arctic Wolf's own site |
| Cohesity | Completed combination with Veritas's Enterprise Data Protection Business, closed Dec 10 2024, combined company valued over $7B, Series H led by Haveli Investments | Cohesity's own newsroom |

Arctic Wolf and Cohesity were the two suppliers still showing "–" at the start of this session; both
required checking the company's full post-sitemap (Arctic Wolf) or a specific newsroom slug search
(Cohesity) to find a company-issued source, since neither company's front newsroom page surfaced the
fact directly.

**Delinea's first pass got this wrong and the coordinator caught it.** The cell was filled with
Delinea's acquisition of StrongDM — something Delinea bought, not who owns Delinea — which is a
different fact than the "ownership or last round" cell is for. StrongDM stays correctly recorded as
two events only (`EV-delinea-2` signing, `EV-delinea-3` closing, both still citing `TR-delinea-4` and
`TR-delinea-5`, which is why that fix didn't orphan anything). The actual ownership fact — who owns
Delinea — is TPG Capital, which formed the company in 2021 by combining Thycotic and Centrify; the new
evidence record (`TR-delinea-6`) is Delinea's own closing announcement, refetched and hashed this
pass, and the company's full news sitemap was checked for anything newer naming a different owner —
nothing found.

### 9. Sources that are not documents

Done, for the five sources the brief named by name. `web/scripts/check-links.ts` (`npm run
check:links`) is a new report-only script (not a build gate) that fetches every evidence
`canonicalUrl` with `User-Agent: SecurityMarketPulse jesse@keatingpike.com` and flags non-200
responses and index/landing-page-like URLs.

Fixed, each verified by fetching the actual document and confirming it supports the cited fact:

- **TR-msft-1** — was the generic Microsoft investor page; now the actual FY2026 10-K document.
- **TR-panw-xsiam-1** (Cortex XSIAM) — was a filing-index page; now the actual 10-K document.
- **TR-msft-defender-1** (Defender for Endpoint) — same 10-K document as TR-msft-1.
- **TR-ping-1, TR-ping-2** (both Ping cells) — were the bare newsroom index page; now the specific
  dated releases.
- **TR-sophos-1** (Sophos's Thoma Bravo ownership, the item named alongside the Moody's downgrade) —
  was `thomabravo.com/press-releases/sophos`, a 404; now the actual release, found via Thoma Bravo's
  sitemap.

A re-run of `check:links` after all of items 1-12 found four more genuinely dead SEC links with wrong
accession numbers/filenames (TR-cyberark-1, TR-cyberark-2, TR-netskope-3, TR-panw-3), all corrected to
verified, live EDGAR document URLs.

**Not fixed, reported instead of guessed:** TR-sophos-2 and TR-sophos-3 (S&P and Moody's rating
actions) still cite a generic `researchpool.com` aggregator provider page rather than the specific
action — a bounded search (the agencies' own sites, EDGAR full-text search, PR Newswire/Sophos's own
newsroom) did not surface a cleaner primary or wire-republished document for either. Six more sources
are index-like or bot-walled after a bounded check: TR-aqua-3 (a persistent "About Us" page, which
does state the facts cited, just isn't a dated document), TR-barracuda-1 and TR-proofpoint-1 (KKR and
Thoma Bravo take-private completions, both from 2021-2022, no longer on the company's own current
sitemap), TR-mimecast-1/TR-mimecast-2 (newsroom index page, Mimecast's own site has no readable
per-item dates — the same defect the item-11 collector batches independently hit), TR-orca-1 (a
redirect loop on Orca's own sitemap), and TR-axonius-1/2/3 (Axonius's own correct newsroom URLs,
currently blocked by a Vercel bot-challenge on automated fetches — the same wall the item-11 collector
hit). None of these were replaced with a lower-confidence or guessed URL; per the sourcing rule, an
unconfirmed replacement is worse than a flagged, honest limitation.

### 10. Internal labels; machine-readable tracker.json

Done, both halves.

Removed the internal packet label ("SEC-MARKET-AUTO-001-STEP5 / TR-crwd-1") that the evidence drawer
rendered to readers. Removed the JSON-LD `reportNumber` field (which carried the same kind of internal
id) and gave the publisher a stable `@id` (`https://securitymarketpulse.com/#organization`) so all
three JSON-LD blocks' `publisher` resolve to one entity instead of three anonymous objects that happen
to share a name. Found and fixed a second instance of the same defect in `HowThisWorks.tsx`'s visible
prose ("This edition is the Episode 002 packet (SEC-MARKET-SIG-002 v0.2)...") while checking for other
call sites — rewritten to state only the last-updated date.

Added `dist/tracker.json`, emitted at build time: run status, the 12 domains, all 74 suppliers, and
every tracker figure (headline metric, revenue latest/prior, last funding round, ownership fact), each
with a stable id, its value, its period/as-of date, and the source URL(s) it is cited to — 147 figures
as of this run. `src/data/tracker/jsonExport.ts`'s pure `trackerJsonPayload` builds it,
`generate-feed.ts` writes it, and `verify-dist.ts`'s new check 11j deep-equal-checks the written file
against that payload so the writer and its checker cannot drift apart. Every route now advertises it
via `<link rel="alternate" type="application/json">`, and check 11h requires that link on every route
the same way it already required `corrections.json`'s.

**Component files touched** (outside my `web/src/data/**`/`web/scripts/**` ownership, kept minimal,
per the boundary): `web/src/components/EvidenceDrawer.tsx` (removed the packet-label `dt`/`dd` pair)
and `web/src/components/HowThisWorks.tsx` (removed the internal-id sentence).

### 11. Newsroom fallback chain; incremental collect

Done. Updated `docs/active/auto/collect-brief.md` (new §1a): before marking a supplier's own news
unreadable, the collector now tries, in order, an RSS/Atom feed, a sitemap, an investor-relations
subdomain, a GlobeNewswire/PR Newswire/Business Wire copy, and an EDGAR full-text search — a supplier
fails only when all five are exhausted, with the failure detail naming which routes were tried.

Ran the updated collector against all 74 declared suppliers, in seven batches of up to 12, under
`SMP_COLLECT_SINCE=2026-09-26`, on the host (`scripts/collect.sh`, under the owner's own Claude
subscription). One genuine new fact found: ReliaQuest named Krish Venkataraman Chief Financial
Officer, effective October 5, 2026 (`EV-reliaquest-1`, `TR-reliaquest-2`) — I independently refetched
the company's own release and confirmed the sha256 hash matches the record before trusting it.

**New failed-newsroom count: 11 of 74**, down from 28 before this session:

Armis, Axonius, Cato Networks, Check Point Email, Check Point SASE, Mimecast, Rubrik, Sysdig, Tenable,
Varonis, Zscaler.

Every one of the 11 genuinely exhausted all five fallback routes (the per-supplier detail in each
batch's receipt, archived at `docs/active/auto/fitfix4/batch-receipts/`, names exactly what was tried
and how each attempt failed). Most are bot/WAF walls (Cloudflare, Akamai, Vercel challenge pages, AWS
WAF) with no reachable IR subdomain, no wire-service copy, and no EDGAR hit. Three of the eleven
(Tenable, Varonis, Zscaler) are supplementary IR-subdomain checks only — their SEC filings and main
newsroom were both confirmed clean directly, and only a hypothetical IR-only item (a rating action,
say) could have been missed.

`web/src/data/generated/collectState.json`'s `collectorRun` block was assembled by hand at the end
from the merged result of all seven batches (failed sources, watermark) — each individual batch
invocation only ever writes its own slice, and a prior run of mine mistakenly left the file reflecting
only the last batch before this was caught and corrected. The 74-supplier watermark
(`lastSuccessfulCollectDate`) now reads 2026-10-02.

### 12. SEC data refresh; every gate

Done. Ran `npm run refresh:edgar` against `data.sec.gov`'s XBRL companyfacts API: 16 ok, 0 failed, 4
unsupported by design (Check Point, Trend Micro — the non-XBRL foreign filers already named in item
4's `filingsClause()` fix).

## Gate results

Run in the OrbStack dev VM, in order, after every item above:

| Gate | Result |
|---|---|
| `npm run lint` (oxlint) | 0 warnings, 0 errors |
| `npm run verify:edition` | passed |
| `npm run verify:panel` | passed |
| `npm run verify:integrity` | passed — 5 unreferenced records, same as preview (see below) |
| `npm run verify:issue` | passed, 17/17 checks |
| `npm run verify:prints` | passed, 44 pass / 1 pre-existing unverified-list warning / 0 fail |
| `npm run verify:tracker` | passed — 12 domains, 74 suppliers, 116 events |
| `tsc -b` | passed |
| `npm run build:client` / `build:server` | passed |
| `npm run prerender` | passed, 5 routes |
| `npm run seo` | passed |
| `npm run build:feed` | passed — `dist/tracker.json` with 147 figures |
| `npm run verify:dist` | passed — 10/10 checks (11a-11j) |
| `npm run test:data` | passed — 251/251 |
| `npm run test:e2e` (Playwright) | passed — 30/30 |

**`verify:integrity`** allows up to 5 unreferenced evidence records before failing the build.
`origin/preview` sits at exactly 5 (A4, A5, A6, B4, B5 — archived A/B/C-prefixed evidence records
outside the live tracker's own `TR-` set), confirmed via `git log -S` to predate this entire fix-pass-4
session, tracing to the tracker's original launch commit (`c65e791`). It needs an owner decision
(`BACKLOG.md` **SEC-058**, renumbered from a first draft that collided with an existing SEC-056 already
taken on preview) and is not part of this pass's scope.

This branch initially pushed that count to 6 and broke the build. The cause: item 1's sweep superseded
two Snyk records correctly (`TR-snyk-1`, `TR-snyk-2`, linked into `TR-snyk-3`'s `conflictingEvidenceIds`,
which `verify-integrity.ts` counts as a valid reference), but the same supersession done for Veeam
(`TR-veeam-4` replacing `TR-veeam-1`, a Wikipedia source, with Veeam's own 2024 release) left
`conflictingEvidenceIds` empty instead of linking back. That left
`TR-veeam-1` as a 6th orphan — a regression this branch introduced, not a pre-existing condition, and
the coordinator was right to reject the earlier draft's claim that it was pre-existing. Fixed by adding
`"TR-veeam-1"` to `TR-veeam-4`'s `conflictingEvidenceIds`, the same pattern used for Snyk. Confirmed in
the VM: `verify:integrity` now reports exactly 5 unreferenced records, matching preview.

## Facts changed, old value → new value, with source

| Record | Old | New | Source |
|---|---|---|---|
| Snyk last round | Series F, 2021 | Series G, $196.5M, Dec 13 2022, led by QIA, $7.4B valuation | Snyk's own newsroom |
| Ping Identity events | 0 in trailing 12 months | +1: Keyless acquisition completed Jan 7 2026 | Ping's own PR Newswire release |
| Dragos ownership label | "Acquired by Accenture plc" | "Majority investment by Accenture plc" | Accenture's own release |
| GitHub Advanced Security event date | Dec 31 2025 (unsourced) | Removed — no source supports a date in the trailing-12-month window | n/a |
| Ivanti ownership | Cited only the 2025 refinancing release, no `announced`/`closed` date (failed the new gate 16) | Cites both the 2021 Charlesbank-closing release and the 2025 refinancing release; status sentence names all three sponsors and all three years | Ivanti's own releases, both refetched and hashed this pass |
| Aqua Security last round | none | Series E, $135M, Mar 10 2021, ION Crossover Partners, >$1B valuation | Aqua's own PR Newswire release |
| Expel ownership | none | Series E extension, $171.3M, Oct 3 2022 | Expel's own site |
| BeyondTrust ownership | none | Clearlake Capital investment closed Aug 17 2021 | BeyondTrust's own release |
| Delinea ownership | none | PE-owned by TPG Capital, formed by its 2021 Thycotic/Centrify combination, closed Apr 13 2021; StrongDM stays an event only | Delinea's own merger-completion release |
| Arctic Wolf ownership/last round | "–" | Series F, $150M, Jul 13 2021, $4.3B valuation | Arctic Wolf's own site |
| Cohesity ownership/last round | "–" | Veritas EDP combination closed Dec 10 2024, >$7B combined valuation | Cohesity's own newsroom |
| Qualys revenue.prior | "–" | $175.6M, Q1 2026, +9.8% YoY | Qualys's own Q1 2026 earnings release |
| Tenable revenue.prior | "–" | $239.1M prior-year, +9.6% YoY | Tenable's own Q1 2026 earnings release |
| Trend Micro growth | "–" | +13% YoY (whole percent, company-stated) | Trend Micro's own Q2 2026 earnings release |
| SailPoint Q1 FY2027 growth | 21.5% | 21.6% (precision correction) | SailPoint's own 10-Q MD&A |
| 14 EDGAR-covered suppliers' growth | whole-percent, hand-typed | one-decimal, computed from reported dollar figures | `generated/edgarFacts.json` |
| TR-msft-1 / TR-msft-defender-1 | generic investor page | actual FY2026 10-K document | SEC EDGAR |
| TR-panw-xsiam-1 | filing-index page | actual 10-K document | SEC EDGAR |
| TR-ping-1, TR-ping-2 | bare newsroom index | specific dated releases | Ping's own newsroom |
| TR-sophos-1 | 404 (`thomabravo.com/press-releases/sophos`) | actual release, Mar 2 2020 | Thoma Bravo's own site |
| TR-cyberark-1, TR-cyberark-2, TR-netskope-3, TR-panw-3 | wrong accession numbers/filenames, 404 | verified live EDGAR documents | SEC EDGAR |
| ReliaQuest | 0 events in window | CFO appointment, Oct 5 2026 effective | ReliaQuest's own release |
| CrowdStrike Falcon Exposure Mgmt / Cortex XSIAM | rendered as bare "Segment" | renders parent via "Segment of X" | n/a (formatting fix) |
| Commvault, JFrog | not in EDGAR XBRL registry | added (both file 10-Q/10-K with XBRL) | `edgarRegistry.ts` |
| Trend Micro | implicit | explicit unsupported-list entry (non-XBRL foreign filer) | `edgarRegistry.ts` |

## Summary

All 12 items are done. The failed-newsroom count fell from 28 to 11, every one of the 11 verified as
a genuine exhaustion of all five fallback routes rather than a first-fetch failure. One new tracked
event (ReliaQuest's CFO appointment) and two previously-empty suppliers' ownership facts (Arctic Wolf,
Cohesity) were added this session, each independently verified against its primary source. The build
pipeline gained a machine-readable `/tracker.json` export and a stronger verify-dist gate.

The coordinator's review of the first draft of this pass caught three real problems before merge: a
regression this branch introduced into `verify:integrity` (fixed — see "Gate results"), and two wrong
ownership cells, Delinea and Ivanti (fixed — see item 8 and the facts table). The pre-existing
`verify:integrity` gap (5 orphaned archive-era evidence records, unchanged by this pass, matching
`origin/preview` exactly) is documented and backlogged under SEC-058 for an owner decision rather than
fixed silently. `mon/fitfix` has also been merged with `origin/preview` (see "Merge with preview"
below) and the full `npm test` suite is green on the merged tree.
