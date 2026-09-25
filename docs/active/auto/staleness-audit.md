# Vendor scorecard staleness audit — as of 2026-09-25

## What "period ended" actually means

The stale-report never looks at when the site collected a fact. It looks at the date the
underlying fact itself refers to — the end of the quarter, fiscal year, or funding round the
figure describes.

The mechanism, read from the code:

- `web/src/data/types.ts` — a `VendorPrint` (the scorecard card) carries a compact `period` tag
  ("JUN '26", "FY26", "2025", "Closed") and a list of `evidenceIds` pointing at `EvidenceRecord`s.
  Each `EvidenceRecord` carries its own `publicationDate` (when the source was published) and a
  free-text `economicPeriod` ("Quarter ended 2026-06-30", "Series G close", "Fiscal year ended
  2026-01-31") — the period the figure is *about*, not when anyone read it.
- `web/src/data/printPeriod.ts`, function `derivePeriodEndDate()`, is what the stale-report calls
  to turn a card's period tag into one ISO end date. If the card names a month-year ("JUN '26") or
  a bare year ("2025"), it computes that period's own last day directly — June 30, 2026, or
  December 31, 2025 — with no reference to today's date at all. Only when the card carries no date
  of its own ("FY26", "Q3 FY26", "Closed") does it fall back to the *newest* `publicationDate`
  among the print's cited evidence, on the stated theory that the most recently published document
  about that print is the closest available anchor — this fallback is a publication date, not a
  "when we added this card" date, and it is still tied to the underlying event, not to site
  activity.
- `web/src/data/staleReport.ts` then takes that end date and computes `daysBetween(periodEnd,
  asOf)`. A print older than 150 days is listed. This is the entire staleness rule — there is no
  separate "site build" or "gather run" clock anywhere in it.

So a print reading "Cato Networks — 2025 ARR +43%" is measured from December 31, 2025 (the end of
the calendar year the figure describes), not from whenever the page or the site itself was built.
The site launched recently, but that has no bearing on this calculation — the clock starts on the
fact's own date, which is often much older than the site. This is why all 19 flagged prints
predate the site: the rule was never about site age, it is about fact age, and several of these
facts (funding rounds, acquisition closes) were already old when the site went up.

One data-quality note found along the way: `web/src/data/printsUnverified.ts` already flags
`print-crwd-cloud` as a labelling ambiguity — the card says "FY26" but its cited evidence
(C13) is dated to the quarter ended 2026-01-31, and the file says the owner should confirm whether
that's an acceptable balance-metric label or should be relabelled "JAN '26" like the total
CrowdStrike ARR card is labelled "APR '26" rather than "FY26."

## Every print in prints.ts (44 total)

Kind legend: PUB = public-company earnings metric · PRIV-ROUND = private funding round ·
PRIV-VAL = private valuation · ACQ = acquisition price/close · CO-STATED = company-stated figure,
not an audited filing · COV = "coverage" surface (not a comparable growth print).

### Network & edge

**Fortinet** (`print-fortinet`) — product revenue +52% (revenue +26%, billings +33%), quarter
ended 2026-06-30. PUB. Age 87 days, not stale. Newer figure: no — Q3 2026 (calendar quarter ended
Sept 30, 2026) has not been reported; next release is Nov 4, 2026 guidance call.
[Fortinet Q2 2026 results](https://investor.fortinet.com/static-files/657dfcda-7367-4c36-8259-b0b43a535da1)

**Cloudflare** (`print-cloudflare`) — revenue +36%, current RPO +35%, quarter ended 2026-06-30.
PUB. Age 87 days. Newer: no — Q3 2026 due Oct 29, 2026.

**Zscaler** (`print-zscaler`) — organic ARR +21% (headline +25% incl. Red Canary), quarter ended
2026-04-30 (Q3 FY26). PUB. Age 148 days — under the 150-day threshold, so not flagged, but a
materially newer quarter already exists: Zscaler reported **Q4/full-year FY2026** (year ended
2026-07-31) on **2026-09-03**: total ARR **$3.8B, +25% YoY**; FY revenue **$3.4B, +25%**. Source:
[Zscaler Q4 FY2026 release](https://ir.zscaler.com/news-releases/news-release-details/zscaler-announces-strong-fourth-quarter-and-fiscal-2026), 2026-09-03.

**Check Point** (`print-checkpoint`) — revenue +1%, subscriptions +12%, quarter ended 2026-06-30.
PUB. Age 87 days. Newer: no — Q3 2026 due Nov 3, 2026 (confirmed via search; an earlier search hit
returning "Q3 2026 EPS $3.94" does not match a real Check Point release and should be disregarded).

**Cato Networks** (`print-cato`) — 2025 ARR +43%, >$350M. PRIV, CO-STATED (company milestone
release, not a filing). Period end 2025-12-31. **Flagged — 268 days.** **Newer figure exists and
was missed:** Cato announced ARR **exceeded $415M, +42% YoY**, on **2026-07-27** — a mid-2026
figure that supersedes the shown 2025 calendar-year number.
[Cato Networks, $415M ARR](https://www.catonetworks.com/news/cato-exceeds-415m-arr-fueled-42-yoy-growth-and-enterprise-demand/), 2026-07-27.

**Netskope** (`print-netskope`) — ARR +31%, $811M, fiscal year ended 2026-01-31 (card labelled
"FY26"; the parser's fallback anchors to the newest cited evidence's publication date, 2026-03-11).
PUB. **Flagged — 198 days.** **Newer figure exists and was missed:** Netskope reported **Q2
FY2027** (quarter ended ~2026-07-31) on **2026-09-02**: revenue **$220.5M, +29%**; ARR **$899M,
+27% YoY**. Source:
[Netskope Q2 FY2027 results](https://investors.netskope.com/news-releases/news-release-details/netskope-announces-strong-second-quarter-fiscal-2027-financial), 2026-09-02.

### Cloud security

**Wiz** (`print-wiz`) — $32B, inside Google Cloud, closed March 2026. ACQ, `surface: coverage`,
`position: absorbed`. **Flagged — 198 days** (parser anchors to the newest cited close-announcement
evidence, 2026-03-11). **No longer meaningful as a standalone print.** Wiz's results are now
folded into Google's consolidated Google Cloud segment with no separate disclosed Wiz line; this is
a structural limit of an acquired company, not a missed newer figure. (Secondary press has cited a
pre-close "$1B+ ARR" figure as of the deal closing, but that is a different fact from the $32B deal
price shown on the card and does not update it.)

**CrowdStrike Falcon Cloud** (`print-crwd-cloud`) — cloud ending ARR >35% YoY, >$800M, segment not
total; card labelled "FY26," evidence (C13) is quarter ended 2026-01-31. PUB, segment metric.
**Flagged — 206 days** (parser anchors to C13's publication date, 2026-03-03). **Unverified,
possibly missed:** CrowdStrike's Q1 FY2027 (ended 2026-04-30) and Q2 FY2027 (ended 2026-07-31,
reported 2026-08-26/31) releases discuss total ending ARR ($5.84B, +25% YoY, as of Q2) and Falcon
Flex ARR ($2.29B, +101% YoY), but this search did not turn up a restated "cloud security segment"
ARR figure in either quarter's release or call transcript excerpts. It is possible CrowdStrike
simply doesn't repeat that specific cut every quarter, in which case this is a structural
limitation rather than a miss — but it could not be confirmed either way in this pass, so it is
listed as unverified rather than assigned to either bucket.

**Upwind** (`print-upwind`) — $1.5B private valuation (Series B $250M), close 2026-01-26. PRIV-VAL.
**Flagged — 237 days.** **Newer figure exists and was missed:** Upwind closed a **Series C, $300M,
at a $3.8B valuation**, announced **2026-09-04** (roughly $2B higher than the January valuation).
Source:
[Bloomberg, Upwind $300M at $3.8B](https://www.bloomberg.com/news/articles/2026-09-02/upwind-raises-300-million-at-3-8-billion-valuation-for-ai-cloud-cybersecurity), 2026-09-02/04.

**Orca Security** (`print-orca`) — TD SYNNEX NA distribution deal, April 2026; last equity round Oct
2021 Series C, $1.8B. COV (distribution partnership, not a growth print). Age 148 days, not
flagged. Not independently re-checked for a newer funding round in this pass — Orca is not on the
19-item list or the named public-company list, and the card's own period tag is about the
distribution deal, not equity.

**Aqua Security** (`print-aqua`) — Series E extension, $60M, closing $1B+ valuation, Jan 2024.
PRIV-ROUND. **Flagged — 968 days**, by far the oldest print on the board that isn't a "no series"
placeholder. **Nothing newer published:** no funding, acquisition, or distress event found since
the January 2024 round; the ~$1B valuation appears effectively flat since a 2021 mention of "in
excess of $1 billion." Structural limit — the company simply has not put out a newer disclosed
number.

**Palo Alto Prisma AIRS customer count** (`print-panw-cloud`) — 300+ customers, "Q3 FY26" (parser
anchors to C24's publication date, 2026-06-02). PUB, adoption metric, `surface: coverage`. Age 115
days, not flagged. **Newer figure exists:** Palo Alto's **Q4 FY2026** results (year ended
2026-07-31, reported 2026-09-01) put Prisma AIRS at **~$120M ARR with 800+ customers** (more than
2x quarter-over-quarter), up from the 300 customers shown, no ARR figure at all on the current
card.
[Palo Alto Q4 FY2026 slides](https://www.investing.com/news/company-news/palo-alto-networks-q4-fy2026-slides-record-growth-margin-concerns-93CH-4884708), 2026-09-01/08.

### SecOps

**SentinelOne** (`print-s1`) — ARR +23%, quarter ended 2026-04-30. PUB. Age 148 days, not flagged.
**Newer figure exists:** Q2 FY2027 (ended 2026-07-31, reported 2026-08-27): **ARR $1.218B, +22%
YoY**, record net-new ARR $56M.
[SentinelOne Q2 FY2027](https://finance.yahoo.com/markets/stocks/articles/sentinelone-announces-second-quarter-fiscal-200500963.html), 2026-08-27.

**CrowdStrike total ARR** (`print-crwd`) — ending ARR +24%, quarter ended 2026-04-30. PUB. Age 148
days, not flagged. **Newer figure exists:** Q2 FY2027 (ended 2026-07-31, reported 2026-08-26/31):
ending ARR **$5.84B, +25% YoY**, record net-new ARR $333M, +51%.
[CrowdStrike Q2 FY2027 results](https://ir.crowdstrike.com/news-releases/news-release-details/crowdstrike-reports-second-quarter-fiscal-year-2027-financial), 2026-08-26.

**Cisco Security** (`print-cisco-secops`) — FY2026 security revenue +2% (Q4 +14%), fiscal year
ended 2026-07-31, published 2026-08-12. PUB, annual print. Age 44 days, not flagged. Newer: no —
this is already Cisco's latest full-year figure; next report is Q1 FY2027, due 2026-11-18.

**Tines** (`print-tines`) — $1.125B private valuation (Series C $125M), close Feb 2025. PRIV-VAL.
**Flagged — 574 days.** **Nothing newer published:** no funding round or valuation update found
since February 2025. Structural limit.

**Palo Alto XSIAM** (`print-panw-xsiam`) — segment ARR +100% YoY, >$600M, 740 customers, "Q3 FY26"
(parser anchors to C25's publication date, 2026-06-02). PUB, segment metric. Age 115 days, not
flagged. **Newer figure exists:** Q4 FY2026 (reported 2026-09-01): XSIAM ARR grew to **>$700M
(~70% YoY)** with **~1,000 customers** (more than 2x YoY) — both the dollar figure and the growth
rate have moved since the shown quarter.

**Torq** (`print-torq`) — $1.2B private valuation (Series D $140M), close Jan 2026. PRIV-VAL.
**Flagged — 237 days.** **Nothing newer published:** no funding update found since the January 2026
round (~300% 2025 revenue growth cited at the time, itself unaudited/company-stated).

### Data

**Rubrik** (`print-rubrik`) — subscription ARR +32%, quarter ended 2026-04-30. PUB. Age 148 days,
not flagged. **Newer figure exists:** Q2 FY2027 (ended 2026-07-31, reported 2026-08-27):
subscription ARR **$1.66B, +33% YoY**.
[Rubrik Q2 FY2027 results](https://www.nasdaq.com/press-release/rubrik-reports-second-quarter-fiscal-year-2027-financial-results-2026-08-27), 2026-08-27.

**Varonis** (`print-varonis`) — SaaS ARR ex-conversions +25% (headline 52% incl. conversions),
quarter ended 2026-06-30. PUB. Age 87 days, not flagged. Newer: no — Q3 2026 due Oct 27, 2026.

**Cyera** (`print-cyera`) — $12B private valuation (Series G $600M), close June 2026. PRIV-VAL,
`surface: coverage`. Age 87 days, not flagged, not independently re-checked (not on the 19-item or
named-company lists); note Cyera also has an agreement to acquire Oasis Security ($1B, announced
2026-07-28) that is a separate, not-yet-closed transaction and does not change Cyera's own $12B
print.

**Secuvy** (`print-secuvy`) — last disclosed raise, "Seed," 2023. PRIV-ROUND, `surface: coverage`.
**Flagged — 999 days**, the oldest print on the board. **Nothing newer published:** the most recent
funding activity found anywhere is the March 2023 round; the only 2026 activity found is a product
listing/partner-marketplace mention, not a financial event. Structural limit.

**BigID** (`print-bigid`) — company-stated revenue >$100M, "2025." CO-STATED, not audited. Card
period is the bare year "2025," but the underlying evidence is dated 2025-05-16 (a hiring
press release, not a year-end figure) — the card's own period label is broader than what its
evidence actually supports, a separate issue from staleness. **Flagged — 268 days.** **Nothing
newer published:** BigID's last funding round was February 2024; no revenue update beyond the
May 2025 ">$100M" milestone was found. Structural limit.

**Sentra** (`print-sentra`) — Series B, $50M, close April 2025 (>$100M total, +300% co-stated
revenue). PRIV-ROUND. **Flagged — 513 days.** **Nothing newer published:** no new round found for
the data-security "Sentra" since April 2025 (a same-named but unrelated company raised an unrelated
seed round in January 2026 — not this Sentra). Structural limit.

**Securiti** (`print-securiti`) — $1.725B acquisition price, acquired by Veeam, close Dec 2025.
ACQ, `surface: coverage`. **Flagged — 268 days.** **No longer meaningful as a standalone print.**
Veeam has since built products on the acquired technology (Agent Commander, Feb 2026; the Data AI
Command Platform), but no separate Securiti financial figure has been disclosed post-close.
Structural limit of an acquired company.

### Identity

**Okta** (`print-okta`) — cRPO +12%, quarter ended 2026-04-30. PUB. Age 148 days, not flagged.
**Newer figure exists:** Q2 FY2027 (ended 2026-07-31, reported 2026-08-26): revenue **$805M, +11%**,
cRPO **+14% YoY** (up from the shown +12%).
[Okta Q2 FY2027 results](https://www.okta.com/newsroom/press-releases/okta-announces-second-quarter-2027-financial-results/), 2026-08-26.

**SailPoint** (`print-sailpoint`) — ARR +28% (annual), fiscal year ended 2026-01-31 (parser anchors
to C10's publication date, 2026-03-18). PUB. **Flagged — 191 days.** **Newer figure exists and was
missed, twice over:** Q1 FY2027 (ended 2026-04-30, reported 2026-06-09) put ARR at $1.163B, +26%;
and **Q2 FY2027** (ended 2026-07-31, reported **2026-09-09**) put ARR at **$1.231B, +25% YoY**, SaaS
ARR $847M, +36%.
[SailPoint Q2 FY2027 results](https://www.nasdaq.com/press-release/sailpoint-announces-fiscal-second-quarter-2027-results-2026-09-09), 2026-09-09.

**CyberArk** (`print-cyberark`) — $25B, inside Palo Alto, closed Feb 2026. ACQ, `surface: coverage`,
`position: absorbed`. **Flagged — 214 days** (parser anchors to the deregistration filing D36,
2026-02-23). **No longer meaningful as a standalone print.** CyberArk formally deregistered from
SEC reporting after the close and was rebranded "Idira" in a phased transition starting May 2026;
no post-close standalone financial figure exists. (Its pre-close ARR had crossed $1B by early
2025, per secondary reporting — that is older context, not a newer figure, and does not update the
$25B deal-price card.)

**Lumos** (`print-lumos`) — $35M last disclosed raise (Series B, May 2024). PRIV-ROUND. **Flagged —
633 days.** **Nothing newer published:** no funding round found since May 2024; a March 2026
product launch (Identity Security Agents) is a product announcement, not a financial event.
Structural limit.

**Oak** (`print-oak`) — $60M seed round, July 2026. PRIV-ROUND. Age 56 days, not flagged, no newer
round expected or found.

**Hush Security** (`print-hush`) — $30M Series A, July 2026 (Akamai strategic). PRIV-ROUND. Age 56
days, not flagged, no newer round found.

**Veza** (`print-veza`) — closed, inside ServiceNow, price undisclosed, close March 2026. ACQ,
`surface: coverage`. **Flagged — 178 days.** **No longer meaningful as a standalone print.**
ServiceNow has integrated Veza's Access Graph into its AI Control Tower and core workflows through
2026, but no separate Veza financial figure has ever been disclosed (the deal itself was
~$1.2B per press reporting, though Palo Alto's own release left price undisclosed). Structural
limit of an acquired company.

**Entra / Ping / PE PAM** (`print-identity-no-series`) — "no public print," period "No series."
Non-comparable by design; not checked, not flagged, and not expected to ever carry a period.

### AI runtime

**Zenity** (`print-zenity`) — $125M Series C, Aug 2026. PRIV-ROUND. Age 25 days, not flagged.

**Onyx** (`print-onyx`) — $113M Series B, July 2026. PRIV-ROUND. Age 56 days, not flagged.

**WitnessAI** (`print-witnessai`) — $58M strategic round, Jan 2026 (+500% co-stated ARR growth).
PRIV-ROUND. **Flagged — 237 days.** **Nothing newer published:** no funding update found since the
January 2026 round. Structural limit.

**Lakera** (`print-lakera`) — undisclosed terms, Check Point acquisition agreement announced Sept
2025, expected to close Q4 2025. ACQ (agreement, not confirmed close in the cited evidence),
`surface: coverage`. **Flagged — 360 days.** **No longer meaningful as an "agreement announced"
print.** Later 2026 coverage describes Lakera as already integrated, forming "the foundation of
Check Point's Global Center of Excellence for AI Security" — implying the deal has closed since the
card was written — but this pass could not confirm an exact close date or price from a primary
source. Either way, no ongoing standalone Lakera figure exists to report; this is a structural
limit of an acquired/absorbed company, with the added wrinkle that the card's own "agreement
announced, not close" framing is itself now out of date.

**Protect AI** (`print-protect-ai`) — $634.5M acquisition price, inside Palo Alto, closed July 2025.
ACQ, `surface: coverage`, `position: absorbed`. **Flagged — 392 days.** **No longer meaningful as a
standalone print.** Protect AI's technology and CEO are now inside Palo Alto's Prisma AIRS
line, with no separate disclosed figure since the close. Structural limit.

**CalypsoAI** (`print-calypsoai`) — $145.2M, inside F5, closed Sept 2025 (per the F5 filing, though
the card's period tag anchors to F5's 2026-08-06 10-Q, not the 2025 close date). ACQ. Age 50 days,
not flagged. No newer figure expected — same structural situation as the other absorbed names,
just not yet past 150 days by this parser's anchor.

**SurePath AI** (`print-surepath`) — $50.1M, inside F5, closed June 2026. ACQ. Age 50 days, not
flagged.

### Platform

**Palo Alto Networks** (`print-panw`) — organic revenue +14% (headline +31% incl. CyberArk and
Chronosphere), quarter ended 2026-04-30 (Q3 FY26). PUB. Age 148 days, not flagged. **Newer quarter
exists:** Q4 FY2026 (ended 2026-07-31, reported 2026-09-01): headline revenue **+34% YoY** to
$3.41B, NGS ARR **$9.1B, +63%**. This search could not confirm the exact organic (ex-CyberArk/
Chronosphere) growth rate the current card format uses — Palo Alto tracks that cut in supplemental
materials this pass did not reach — so the newer quarter is confirmed to exist, but the
like-for-like organic figure is unverified rather than reported here.

**Cisco** (`print-cisco-platform`) — "Split": FY security +2% (the SecOps card) and Q4 networking
orders +40% (the Infrastructure card), period JUL '26, published 2026-08-12. PUB. Age 56 days, not
flagged. Newer: no — next report is Q1 FY2027, due 2026-11-18.

### Infrastructure

**NVIDIA** (`print-nvidia`) — Data Center revenue +92%, quarter ended 2026-04-26 (mapped to
2026-Q1 on the panel). PUB. Age 148 days, not flagged. Not independently re-checked in this pass
(NVIDIA was not on the named public-company list); NVIDIA's fiscal Q2 FY2027 would have covered
the quarter ending around late July 2026 and was likely reported in August 2026, which would make a
newer figure available, but this was not confirmed here.

**Arista** (`print-arista`) — revenue +38%, quarter ended 2026-06-30, published 2026-08-04. PUB.
Age 87 days, not flagged.

**Cisco** (`print-cisco-net`) — Q4 networking orders +40%, period JUL '26. PUB. Age 56 days, not
flagged. Same next-report date as the other two Cisco cards, 2026-11-18.

## Counts

Of the 19 flagged prints:

- **Genuinely outdated — a newer public figure exists that the pipeline missed:** 4 — Cato
  Networks (2025 ARR card vs. the July 2026 $415M figure), Upwind (January valuation vs. the
  September Series C), Netskope (FY26 annual card vs. Q2 FY2027), SailPoint (FY26 annual card vs.
  Q2 FY2027, reported just 16 days before this audit).
- **No longer meaningful — the company was acquired and no standalone figure exists to refresh
  it with:** 6 — Wiz, CyberArk, Protect AI, Veza, Securiti, Lakera.
- **Old because the company has published nothing newer — a structural limit of the metric
  chosen, not a pipeline miss:** 8 — Secuvy, Aqua Security, Lumos, Tines, Sentra, BigID, Torq,
  WitnessAI.
- **Unverified — could not confirm either way:** 1 — CrowdStrike Falcon Cloud (`print-crwd-cloud`);
  it's possible CrowdStrike hasn't restated that specific segment cut in a later quarter, which
  would make this structural rather than missed, but this pass could not establish that from the
  Q1/Q2 FY2027 materials it reached.

Beyond the 19 flagged prints, a second and separate finding: several prints for public companies
that report every 90 days are **not yet past the 150-day threshold but already sitting on a
superseded quarter**, because the site refreshes on its own gather cadence rather than on each
company's earnings calendar. Zscaler, Okta, CrowdStrike's total ARR, SentinelOne, Rubrik, and both
Palo Alto segment cards (Prisma AIRS, XSIAM) all have a newer quarter available now, some (like
Zscaler's Q4 FY2026 and SailPoint's Q2 FY2027) published within the last three weeks. This is not a
defect in the staleness rule as written — 150 days is a deliberate threshold, not a bug — but it
means "not flagged" should not be read as "current" for a fast-reporting public company.
