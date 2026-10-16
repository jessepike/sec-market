# Vendor scorecard refresh — 2026-09-25

Step 0 of `docs/archive/2026-10-refresh-gate/autonomy-coverage-plan.md`. Source: the staleness audit at
`/private/tmp/claude-501/-Users-jessepike-code-projects-sec-market/d545f023-724a-49b3-b2e2-bec1492ffdae/scratchpad/staleness-audit.md`
(same date). Every figure below was fetched with `curl` and verified against the primary document
before being written to `web/src/data/prints.ts`; the underlying bytes' sha256 and the exact excerpt
are in the matching evidence record in `web/src/data/evidence.ts` (ids C26-C34).

## Prints updated

| Supplier | Old figure / period | New figure / period | Source | Released |
|---|---|---|---|---|
| Zscaler | organic ARR +21% - APR '26 | organic ARR +20% (headline +25% to $3.77B) - JUL '26 | [Zscaler Q4 FY2026 8-K EX-99.1](https://www.sec.gov/Archives/edgar/data/1713683/000171368326000156/zs-07312026_991.htm) | 2026-09-03 |
| Okta | cRPO +12% - APR '26 | cRPO +14%, revenue +11% to $805M - JUL '26 | [Okta Q2 FY2027 8-K EX-99.1](https://www.sec.gov/Archives/edgar/data/1660134/000166013426000068/okta-7312026_ex991.htm) | 2026-08-26 |
| CrowdStrike (total ARR) | ending ARR +24% - APR '26 | ending ARR +25% to $5.84B, net-new ARR $333M - JUL '26 | [CrowdStrike Q2 FY2027 8-K EX-99.1](https://www.sec.gov/Archives/edgar/data/1535527/000153552726000029/crwd-20260826xex991.htm) | 2026-08-26 |
| SentinelOne | ARR +23% - APR '26 | ARR +22% to $1.218B, revenue +21% to $292M - JUL '26 | [SentinelOne Q2 FY2027 8-K EX-99.1](https://www.sec.gov/Archives/edgar/data/1583708/000158370826000052/sentineloneq227exhibit991.htm) | 2026-08-27 |
| Rubrik | subscription ARR +32% ($1.57B) - APR '26 | subscription ARR +33% ($1.66B) - JUL '26 | [Rubrik Q2 FY2027 8-K EX-99.1](https://www.sec.gov/Archives/edgar/data/1943896/000194389626000055/rubrikinc-991pressrelease7.htm) | 2026-08-27 |
| Netskope | ARR (annual) +31% ($811M) - FY26 | ARR +27% ($899M), revenue +29% to $220.5M - JUL '26, now quarterly | [Netskope Q2 FY2027 8-K EX-99.1](https://www.sec.gov/Archives/edgar/data/2063196/000119312526380188/ntsk-ex99_1.htm) | 2026-09-02 |
| SailPoint | ARR (annual) +28% - FY26 | ARR +25% ($1.231B), SaaS ARR +36% ($847M) - JUL '26, now quarterly | [SailPoint Q2 FY2027 8-K EX-99.1](https://www.sec.gov/Archives/edgar/data/2030781/000162828026061015/sailpointinc-20260731x991x.htm) | 2026-09-09 |
| Cato Networks | 2025 ARR +43% (>$350M) - 2025 | ARR milestone +42% (>$415M, 4,800+ customers) - AUG '26 | [Cato blog, "Three Years as a Leader"](https://www.catonetworks.com/blog/three-years-as-a-leader-built-for-where-the-market-is-going/) (see note below on retrieval) | 2026-08-20 |

## Acquisitions

| Supplier | Change | Source |
|---|---|---|
| Lakera | Was "agreement announced Sept 2025, expected to close Q4 2025," value "Undisclosed." Now "Closed," metric "inside Check Point," ~$201.8M consideration, closed **2025-10-22** (confirmed), `position: absorbed` added. | [Check Point FY2025 Form 20-F](https://www.sec.gov/Archives/edgar/data/1015922/000117891326001932/zk2634942.htm), filed 2026-03-31 - "On October 22, 2025, the Company completed the acquisition of all outstanding shares of Lakera AI AG... for total consideration of approximately $201.8 [million]." |
| Veza | Already read "Closed / inside ServiceNow"; added `position: absorbed` for pattern consistency with Wiz/CyberArk/Protect AI. No new figure - existing evidence C23 (ServiceNow close, 2026-03-02) unchanged. | - |
| Securiti | Metric changed from "acquired by Veeam" to "inside Veeam" (matches the "inside <acquirer>" convention); added `position: absorbed`. No new figure - existing evidence C16 unchanged. | - |
| Wiz, CyberArk, Protect AI | Already correctly labelled "Closed," `position: absorbed`, "inside <acquirer>." No changes made. | - |

## Not verified / not changed

- **Palo Alto Networks - organic revenue (`print-panw`), Prisma AIRS (`print-panw-cloud`), XSIAM (`print-panw-xsiam`).** A newer quarter (Q4 FY2026, reported 2026-09-01) exists - headline revenue +34% to $3.41B, NGS ARR +63% to $9.1B - confirmed from the [SEC 8-K EX-99.1](https://www.sec.gov/Archives/edgar/data/1327567/000132756726000019/ex991q426earningsrelease.htm). But that filing does not disclose the organic (ex-CyberArk/Chronosphere) revenue split, Prisma AIRS ARR/customer count, or XSIAM ARR/customer count the three cards actually show - those numbers only appear in PANW's earnings-call materials. `investors.paloaltonetworks.com` returned connection failures on the first attempts and a 403 (Akamai bot block) on a later attempt; three separate attempts across the session did not get through. Left all three cards unchanged rather than guess.
- **CrowdStrike Falcon Cloud segment (`print-crwd-cloud`).** The Q2 FY2027 press release (fetched and read in full) does not restate a cloud-security-segment ARR figure the way the Q4 FY2026 release did. Consistent with the audit's own finding: could not confirm whether CrowdStrike still reports this specific cut. Left unchanged; it is already on `printsUnverified.ts`'s baseline list for an unrelated reason (a period-label ambiguity), which was not touched.
- **Upwind.** The audit cites a Bloomberg article (paywalled) for the Series C at $3.8B. Upwind's own newsroom listing showed no September 2026 entry as of this fetch (newest post: January 2026), its `/feed` and `/feed/` endpoints returned either the homepage or an empty item list, TechCrunch's search did not surface a matching article, and DuckDuckGo's HTML search returned no usable results. Left unchanged - no primary source reachable this session.

## Judged text

No domain stances, platform-pressure sentences, issue text, or hypotheses were touched. Only `web/src/data/prints.ts` (figures, periods, notes, `position` flags) and `web/src/data/evidence.ts` (new records C26-C34, appended; nothing deleted) were edited.

## Tests

Run in the OrbStack dev VM (`orb run -m dev`), from `web/`:

- `npm run verify:prints` - **44 pass, 1 on the unverified list (`print-crwd-cloud`, pre-existing), 0 fail** (both before and after this change; the unverified entry's own reason is unchanged).
- `npm test` (lint -> `test:data` unit tests -> full `build` including `verify:edition`/`verify:panel`/`verify:integrity`/`verify:issue`/`verify:prints`/`verify:dist` -> `test:e2e`) - **all green**: 37 Playwright tests passed, 1 skipped, 0 failed.

## Stale-report counts

`npm run report:stale`, both runs dated 2026-09-25 (0 judged claims stale in either run):

- **Before:** 19 scorecard prints over 150 days old.
- **After:** 16 scorecard prints over 150 days old.

Dropped off the stale list: `print-cato` (was 268 days), `print-netskope` (was 198 days), `print-sailpoint` (was 191 days). `print-lakera` stays on the list - its true period (closed 2025-10-22) is itself over 150 days old, which is correct: it's a structurally absorbed company with nothing newer to report, same as Wiz/CyberArk/Veza/Protect AI, which also remain on the list.

## Visual review

Captured at 1440px and 390px, full page and the `#market` section alone, before and after, using a
capture script mirroring `docs/archive/2026-09-weekly-issue/fable-run/evidence/baseline/capture.mjs` (`chromium.launch()`
with no channel, since the dev VM has no Google Chrome binary - `web/scripts/shot.mjs` itself was not
modified or committed). Files under `docs/archive/2026-10-refresh-gate/auto-001/step0/`: `before-*` / `after-*`, plus
`before-market-*` / `after-market-*` for the "market by domain" section specifically.

What visibly moved, in "The market by domain": Cato Networks (43%->42%, "2025 ARR - 2025" -> "ARR
milestone - AUG '26", its italic "older figure" flag disappeared), Netskope (31%->27%, "ARR (annual) -
FY26 - older figure" -> "ARR - JUL '26", flag disappeared), Zscaler (21%->20%, APR '26->JUL '26), Okta
(12%->14%, APR '26->JUL '26), SailPoint (28%->25%, "ARR (annual) - FY26 - older figure" -> "ARR - JUL
'26", flag disappeared), CrowdStrike (24%->25%, APR '26->JUL '26), SentinelOne (23%->22%, APR
'26->JUL '26), Rubrik (32%->33%, APR '26->JUL '26). CrowdStrike Falcon Cloud, Palo Alto XSIAM, and the
coverage-surface acquisition cards are unchanged in this section, as expected. Layout held at both
widths - the 390px column stacks the same seven domain cards with no overflow; full-page height moved
from 15,744px to 15,780px at 1440px, a 36px difference from slightly longer note text, not a layout
break.

No component, CSS rule, or export was touched - only data.
