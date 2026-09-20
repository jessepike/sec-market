# Content inventory — Security Market Pulse against the product core

**Task:** T5-2, run SEC-MARKET-FABLE-001. Read-only survey of what the site's data already holds,
measured against `docs/active/product-core.md`. Every factual claim below cites a file and line.
Anything without a citation is my own inference and is labelled as such. Today's date for
freshness math is 2026-09-20, so "stale" means the newest record behind a claim is older than
2026-08-06.

All paths are relative to `/Users/jessepike/code/projects/sec-market/` unless given in full.

## 1. What the site knows about each vendor

Every vendor with a persistent record lives in `web/src/data/prints.ts` (the "scorecard," shown by
`PrintGrid`, `DomainBoard`, `PlatformPressure`, and `Hypotheses`) or in `web/src/data/activity.ts`
(the M&A/funding board, shown by `ActivityBoard`). A vendor can appear in both. The weekly issue
(`web/src/data/issues/2026-w36.ts`) holds a third, separate set of vendor mentions that does not
feed back into either file — see section 4.

| Vendor | Domain / print group | Metric held | Period / date | Evidence id | Shown by |
|---|---|---|---|---|---|
| Fortinet | Network & edge (network-sase) | Product revenue +52%, billings +33% | JUN '26 (2026-07-29) | C3 | PrintGrid, DomainBoard, PlatformPressure, MarketLayersChart |
| Cloudflare | Network & edge (network-sase) | Revenue +36%, current RPO +35% | JUN '26 (2026-08-06) | C5 | PrintGrid, DomainBoard |
| Zscaler | Network & edge (network-sase) | Organic ARR +21% (headline ARR +25% incl. Red Canary) | APR '26 (2026-05-26) | C4 | PrintGrid, DomainBoard, PlatformPressure, MarketLayersChart, Hypotheses |
| Check Point | Network & edge (network-sase) | Revenue +1%, subscriptions +12% | JUN '26 (2026-07-30) | C6a | PrintGrid, DomainBoard, PlatformPressure, MarketLayersChart |
| Cato Networks | Network & edge (network-sase) | 2025 ARR >$350M, +43% YoY (private) | 2025 (2026-02-24) | C11 | PrintGrid, DomainBoard, PlatformPressure |
| Netskope | Network & edge (network-sase) | ARR $811M, +31% YoY | FY26 (2026-03-11) | C12 | PrintGrid, DomainBoard, PlatformPressure |
| Wiz | Cloud security (cloud-security) | $32B, closed into Google Cloud — capital, not a growth rate | Closed Mar 2026 (announced 2025-03-18) | D5a, D13 | PrintGrid (coverage card), PlatformPressure (buying-in), DomainBoard, Hypotheses |
| CrowdStrike | Cloud security (Falcon Cloud segment) and SecOps | Falcon Cloud ending ARR >$800M, >35% YoY; separately, total ending ARR +24% | FY26 / APR '26 (2026-03-03 / evidence for C1 not individually re-checked here) | C13, C1 | PrintGrid, DomainBoard, PlatformPressure, MarketLayersChart |
| Upwind | Cloud security (cloud-security) | $1.5B private valuation, $250M Series B — capital, not a growth rate | JAN '26 | D30 | PrintGrid (coverage card) |
| Orca Security | Cloud security (cloud-security) | NA distribution deal with TD SYNNEX; no revenue/growth figure at all (flagged `NO-PRINT` in the August research pass) | APR '26 | C17, C18 | PrintGrid (coverage card) |
| Aqua Security | Cloud security (cloud-security) | Last disclosed equity is a 2024 Series E extension; no 2025-2026 figure (`NO-PRINT`) | JAN '24 | C19 | PrintGrid (coverage card) |
| Palo Alto Networks | Platform, Cloud security (secondary: AI runtime), SecOps (XSIAM), Identity (via CyberArk) | Organic revenue +14% (platform); Prisma AIRS 300+ customers (adoption count, not a growth rate); XSIAM segment ARR +100%, >$600M | Q3 FY26 (2026-06-02) | C2, C24, C25 | PrintGrid, PlatformPressure, DomainBoard |
| CyberArk | Identity (absorbed into Palo Alto) | $25B acquisition, closed — no standalone print after close | Closed Feb 2026 | D14, D5b, D36 | PrintGrid (coverage card), PlatformPressure (buying-in), Hypotheses |
| SentinelOne | SecOps (secops) | ARR +23%, revenue +21%, net-new ARR +55% | APR '26 | C9 | PrintGrid, DomainBoard. Not in PlatformPressure — it carries no `position` value |
| Cisco Security | SecOps (secops), and Platform / Infrastructure (networking) | FY2026 security revenue +2% (Q4 alone +14%) | FY26 (2026-08-12) | C6b | PrintGrid, DomainBoard, PlatformPressure |
| Tines | SecOps (secops) | $1.125B private valuation, $125M Series C — capital, not a growth rate | FEB '25 | C21 | PrintGrid (coverage card) |
| Torq | SecOps (secops) | $1.2B private valuation, $140M Series D — capital, not a growth rate | JAN '26 | D31 | PrintGrid (coverage card) |
| Rubrik | Data (data-ai-security) | Subscription ARR +32%, $1.57B | APR '26 | C8a | PrintGrid, DomainBoard, PlatformPressure |
| Varonis | Data (data-ai-security) | SaaS ARR ex-conversions +25% (headline +52% includes conversions) | JUN '26 | C8b | PrintGrid, DomainBoard, PlatformPressure |
| Cyera | Data (data-ai-security) | $12B private valuation, $600M Series G — capital, not a growth rate | JUN '26 | D8 | PrintGrid (coverage card), ActivityBoard |
| BigID | Data (data-ai-security) | ">$100M revenue" — company-stated, not audited ARR | 2025 | C14 | PrintGrid (coverage card) |
| Sentra | Data (data-ai-security) | $50M Series B; company states +300% revenue, not audited | APR '25 | C15 | PrintGrid (coverage card) |
| Securiti | Data (data-ai-security) | $1.725B acquisition by Veeam, closed | DEC '25 | C16 | PrintGrid (coverage card) |
| Okta | Identity (identity) | cRPO +12%, revenue +11% (deceleration noted) | APR '26 | C7 | PrintGrid, DomainBoard, PlatformPressure |
| SailPoint | Identity (identity) | Total ARR +28% (fiscal year, not aligned to the quarterly panel) | FY26 (fiscal year ended Jan 2026) | C10 | PrintGrid, DomainBoard, PlatformPressure |
| Oak | Identity (identity, secondary: AI runtime) | $60M seed — capital, not a growth rate | JUL '26 | D20 | PrintGrid (coverage card), ActivityBoard |
| Hush Security | Identity (identity, secondary: AI runtime) | $30M Series A — capital, not a growth rate | JUL '26 | D21 | PrintGrid (coverage card), ActivityBoard |
| Veza | Identity (identity) | Acquired by ServiceNow, closed, price undisclosed | MAR '26 | C23 | PrintGrid (coverage card) |
| Lumos | Identity (identity) | $35M Series B, last disclosed raise (2024) | 2024 | D10 | PrintGrid (coverage card), ActivityBoard |
| Zenity | AI runtime (ai-runtime) | $125M Series C — capital, not a growth rate | AUG '26 | D19 | PrintGrid (coverage card), ActivityBoard |
| Onyx | AI runtime (ai-runtime) | $113M Series B — capital, not a growth rate | JUL '26 | D18 | PrintGrid (coverage card), ActivityBoard |
| WitnessAI | AI runtime (ai-runtime) | $58M strategic round; company states +500% ARR, not audited | JAN '26 | C20 | PrintGrid (coverage card) |
| Lakera | AI runtime (ai-runtime) | Acquired by Check Point, terms undisclosed | SEP '25 | C22 | PrintGrid (coverage card) |
| Protect AI | AI runtime (absorbed into Palo Alto) | $634.5M acquisition, closed; filing calls acquired revenue immaterial | Closed Jul 2025 | D32, D33 | PrintGrid (coverage card) |
| CalypsoAI | AI runtime (absorbed into F5) | $145.2M acquisition, closed; revenue not material in the filing | Closed Sep 2025 | D34 | PrintGrid (coverage card) |
| SurePath AI | AI runtime (absorbed into F5) | $50.1M acquisition, closed, $39.1M of it goodwill | Closed Jun 2026 | D35 | PrintGrid (coverage card) |
| NVIDIA | Infrastructure (no domain) | Data Center revenue +92%, $75.25B | APR '26 | A1b | PrintGrid, MarketLayersChart, JudgmentBoard |
| Arista | Infrastructure (no domain) | Revenue +38%, $3.04B | JUN '26 | A3 | PrintGrid |

The twelve vendors named in the task:

- **Check Point** — present, print-checkpoint, C6a (row above).
- **Fortinet** — present, print-fortinet, C3 (row above).
- **Palo Alto Networks** — present, in four different roles at once (platform organic revenue,
  Prisma AIRS adoption count, XSIAM segment ARR, and the CyberArk acquirer). No single print
  states one Palo Alto "growth number" a reader could use for comparison.
- **CrowdStrike** — present, two different metrics under two different groups (Falcon Cloud
  segment ARR under Cloud security, total ending ARR under SecOps).
- **Zscaler** — present, print-zscaler, C4.
- **Okta** — present, print-okta, C7.
- **SentinelOne** — present, print-s1, C9, but excluded from `PlatformPressure` because it has no
  `position` value (`web/src/data/prints.ts:166-175`; the filters in `platformPressure.ts:26-34,
  164-174` all key off `position`).
- **Cloudflare** — present, print-cloudflare, C5, but also excluded from `PlatformPressure` for
  the same reason (no `position` set), and absent from the `MarketLayersChart` security-median
  index, which only tracks CrowdStrike, Okta, Fortinet, Zscaler and Check Point
  (`web/src/data/panelRaw.ts` series list; `market.ts:86`).
- **Netskope** — present, print-netskope, C12.
- **Wiz** — present, but only as a closed-acquisition capital record, never a revenue or growth
  figure (row above).
- **Rubrik** — present, print-rubrik, C8a.
- **Optiv** — **absent**. A repo-wide search of every file under `web/src/data/` for "optiv" (case
  insensitive) returns no matches. Product-core section 4 names "a large security services firm's
  debt problems" as exactly the kind of distress signal the owner wants captured
  (`docs/active/product-core.md:53`); nothing resembling it exists anywhere in the data today,
  named or unnamed.

## 2. What the site knows about each domain

`web/src/data/domains.ts:12-119` defines six domains. Every domain's `posture`, `tag` and `horizon`
have been unchanged across all three published editions to date (`web/src/data/edition.ts:26-150`;
the 2026-08-28 entry's own summary says so at line 101: "No posture moved"). The `asOf` date on
every domain is 2026-08-16 (`domains.ts:19,40,57,74,91,108`), which is also the date the tracked
prints behind each posture were last reviewed as a set.

| Domain | Posture / horizon | Tracked basis (file:line) | Judged basis | Last changed | Vendors with a current growth-rate print |
|---|---|---|---|---|---|
| Network / SASE | PREPARE, this quarter | `domains.ts:14-33`, prints C3/C4/C5/C11/C12 | "Refresh is live... a split, not a new SASE wave" (`domains.ts:24`) | 2026-08-16 | 6: Fortinet, Cloudflare, Zscaler, Check Point, Cato, Netskope |
| Data / AI Security | PREPARE, this planning cycle | `domains.ts:35-50`, prints C8a/C8b/D8/D9/C14-16 | "Selected data vendors are accelerating. Not a broad realized series yet" (`domains.ts:46`) | 2026-08-16 | 2: Rubrik, Varonis |
| Cloud Security | INVESTIGATE, next 1-4 quarters | `domains.ts:52-67`, prints D5a/D7/C13/C17-19/C24/D30 | "Qualify residual gaps when capacity goes live" (`domains.ts:63`) | 2026-08-16 | 1: CrowdStrike (Falcon Cloud segment only) |
| Identity | INVESTIGATE, next 1-4 quarters | `domains.ts:69-84`, prints C10/D5b/D10/D11/D20/D21/C23 | "Use identity as a qualification topic where machine identities go live" (`domains.ts:80`) | 2026-08-16 | 2: Okta, SailPoint |
| SecOps | INVESTIGATE, next 1-4 quarters | `domains.ts:86-101`, prints C9/C1/C6b/C21/C25/D31 | "Share shift and platformization, not a new SecOps cycle" (`domains.ts:97`) | 2026-08-16 | 3-4: SentinelOne, CrowdStrike, Cisco Security, plus Palo Alto's XSIAM segment (a product line, not a company total) |
| AI Runtime | INVESTIGATE, next 1-4 quarters | `domains.ts:103-118`, prints D19/D18/C20/C22/D2/D3/D32-35 | "Do not run a specialist-platform motion from survey intent alone" (`domains.ts:114`) | 2026-08-16 | 0: every AI Runtime print is a funding round or an acquisition price; none is a company reporting a revenue or ARR growth rate |

Whether each domain could honestly support a "leading vendors by reported growth" table today:

- **Network / SASE** could support one now, and the strongest of the six. Six vendors all report a
  percentage growth figure, though the metrics are not like-for-like — Fortinet's is product
  revenue, Zscaler's is organic ARR, the others are total revenue or ARR — so a table would need a
  footnote on what each percentage actually measures, not just a ranked list.
- **Data / AI Security** could support a thin one: two rows (Rubrik, Varonis). Everything else in
  the group is a valuation or an acquisition price, not a rate.
- **Identity** is the same shape: two rows (Okta, SailPoint), both public and comparable.
- **SecOps** could support three clean company-level rows (SentinelOne, CrowdStrike, Cisco
  Security); a fourth, Palo Alto XSIAM, is a product segment rather than the whole company and
  would need to be labelled as such rather than placed next to company totals.
- **Cloud Security** cannot support one today. Only CrowdStrike's Falcon Cloud segment has a growth
  rate; Wiz, Upwind, Orca and Aqua are all capital or M&A records, and Orca and Aqua have no public
  number of any kind (`docs/active/domain-vendor-signals-2026-08.md:63-67`, `132-142`, flagging
  both `NO-PRINT`).
- **AI Runtime** cannot support one at all. Every record under this domain is a private funding
  round or an acquisition price. No AI-security vendor in the data has disclosed a revenue or ARR
  growth figure. This is not a gap in the site's research; the domain-vendor-signals pass explicitly
  went looking (`docs/active/domain-vendor-signals-2026-08.md:115-127`) and found only capital
  events — the underlying companies are mostly private and don't report one yet.

## 3. Consolidation, funding and distress

M&A closes or announcements on file: Wiz/Google ($32B, closed Mar 2026, `activity.ts:234-245`),
CyberArk/Palo Alto ($25B, closed Feb 2026, `activity.ts:247-258`), Protect AI/Palo Alto ($634.5M,
closed Jul 2025, `activity.ts:286-297`), CalypsoAI/F5 ($145.2M, closed Sep 2025, `activity.ts:299-
310`), SurePath AI/F5 ($50.1M, closed Jun 2026, `activity.ts:312-323`), Astrix/Cisco (undisclosed,
completed Jun 2026, `activity.ts:169-180`), Portkey/Palo Alto (undisclosed, closed May 2026,
`activity.ts:182-193`), Symmetry Systems/Zscaler (intent only, not closed, `activity.ts:195-206`),
Securiti/Veeam ($1.725B, closed Dec 2025, `prints.ts:307-317`), Veza/ServiceNow (undisclosed,
closed Mar 2026, `domain-vendor-signals-2026-08.md:93-96`), Lakera/Check Point (undisclosed,
agreement Sep 2025, `activity.ts` via C22), Cyera/Oasis Security (~$1B, letter of intent only,
not closed, `activity.ts:50-62`). The weekly issue adds five more, all fresh but small or
undisclosed: Palo Alto/Console ($500M reported, not confirmed by Palo Alto,
`issues/2026-w36.ts:94-102`), ePlus/Daymark, Echo/Minimus, Ampcus/smarterd, Trace3/Calian's US
business, and Integrity360/CyberIAM, all "undisclosed amount"
(`issues/2026-w36.ts:103-149`).

Funding rounds: Zenity, Oak, Hush, Onyx, Cathedral, Horizon3.ai, Glow, Neo Security, Arcade,
CodeIntegrity, Zafran, Above Security (`activity.ts:6-232`), plus seven more first-appearing in the
weekly issue's formation lane: Socure ($156.0M), KAZIMI, CYBERA, Opgate, DetectifAI, HiddenLayer
($100M), AIR Security ($50M) (`issues/2026-w36.ts:20-89`).

**No distress signal of any kind exists in the data.** A case-insensitive search of every file
under `web/src/data/` for layoff, bankrupt, debt, insolvency, wind-down, shutdown, distress,
default, restructuring, Chapter 11 or receivership returns zero matches outside a handful of
unrelated substrings inside investor-relations URLs (`investor.cisco.com`, and similar). Product-
core section 4 names debt and distress at a named large security services firm as a first-class
example of what the site should capture (`docs/active/product-core.md:52-53`); the mechanism for
finding, sourcing or publishing that kind of signal does not exist yet in this codebase, and open
question 12 in product-core says as much ("How are distress signals... sourced reliably from
public information? Open. Needs research," `product-core.md:135`).

## 4. Freshness

Ages are measured against 2026-09-20; the 45-day cutoff falls on 2026-08-06.

| Dataset | File | Newest record | Age | How it updates |
|---|---|---|---|---|
| Weekly issue | `issues/2026-w36.ts` | Published 2026-09-19; item dates 2026-08-24 to 2026-09-03 (`issues/2026-w36.ts:14, 74-84`) | 1 day since publish; 17-27 days on the events themselves | By hand, one issue at a time; signed by the owner on publish (`issues/2026-w36.ts:3-9`) |
| Evidence library (W36 batch) | `evidence.ts` (W36-01 to W36-23) | 2026-08-24 to 2026-09-03 | 17-27 days | Added alongside the weekly issue that cites it |
| Evidence library (pre-W36, ~90 records) | `evidence.ts` | Ranges from C6b (2026-08-12) down to C19 (2024-01-03) | 39 days to over 600 days | By hand, only when a new print or activity item is added |
| Vendor scorecard | `prints.ts` | Newest single tracked print is Cisco Security, C6b, 2026-08-12 | 39 days on the newest entry; most entries (Fortinet, Zscaler, Okta, SentinelOne, Rubrik, CrowdStrike, SailPoint, and all coverage-only names) are 45-600+ days old | **Never** updated by the weekly issue pipeline — confirmed by inspection: the file's own file-history comment says the vendor-lens edit on 2026-09-19 changed no values, only added a derived slug field (`prints.ts:15-20`) |
| Domain postures | `domains.ts` | `asOf: '2026-08-16'` on all six domains | 35 days | By hand, in step with an edition |
| Platform pressure reads | `platformPressure.ts` (derived) | `judgedOn` = `JUDGED_AS_OF_ISO` = 2026-08-17 (`meta.ts:23`) | 34 days | By hand, only when the underlying prints or activity change |
| Tracked hypotheses | `hypotheses.ts` | Tracking date 2026-08-17; NO-CALL items frozen 2026-08-15 (`meta.ts:3,23`) | 34-36 days | By hand |
| M&A / funding board | `activity.ts` | Newest items 2026-08-03 (Zenity, Above Security) | 48 days | By hand; **not** fed by the weekly issue's own, separate absorption/formation lanes |
| Edition history | `edition.ts` | 2026-08-28 (`edition.ts:97`) | 23 days | By hand, one entry per edition, append-only |
| Quarterly chart panel | `panelRaw.ts` | 2026-Q1 (NVIDIA's quarter ended 2026-04-26, `prints.ts:535`) | About 5 months | By hand, one quarter column at a time |
| Site "last updated" badge | `meta.ts:14-16` | September 19, 2026 | 1 day | Moves whenever the site ships, regardless of whether any judgment was reviewed |

**Flagged as stale (older than 45 days):** the entire vendor scorecard except the single Cisco
Security print; the M&A/funding board; nearly the whole pre-W36 evidence library; the quarterly
chart panel.

**A freshness trap worth naming plainly.** The header badge (`Header.tsx:124-126`) reads
"September 19, 2026" because the site rebuilt to ship the new issue. A reader has no way to tell
from that badge that the domain postures, the platform-pressure reads and the tracked hypotheses
were actually last reviewed on 2026-08-16/17, over a month earlier — `meta.ts`'s own comment warns
against exactly this conflation (`meta.ts:9-13`) and it still happens, because the badge reads off
`LAST_UPDATED_DISPLAY` alone. **Inferred, not cited to a specific line:** a reader comparing the
issue's fresh CrowdStrike, Zscaler, SentinelOne, Okta, Rubrik and Palo Alto numbers (all dated
2026-08-26 to 2026-09-03, `issues/2026-w36.ts:158-213`) against the scorecard's older numbers for
the same six companies (all dated 2026-04-26 to 2026-06-04, rows in section 1 above) would see two
different growth rates for CrowdStrike, Zscaler, SentinelOne, Okta, Rubrik and Palo Alto side by
side on the same page, because the issue and the scorecard are two separate, unreconciled data
stores that both cover the same vendors.

## 5. What a security leader's first screen can be built from today

**(a) One sentence saying what the site is.** No sentence matching product-core section 1 exists
in the data or copy today. `Hero.tsx:18-21` and `HeroContent()` render "Infrastructure is running
ahead. Security is splitting, not booming" as the masthead headline — that is the founding thesis,
which product-core section 5 says must leave the first screen (`product-core.md:71-73`). This
needs new copy, a decision the owner has already made in principle; it is not a data problem.

**(b) This week's read.** `issue.read` (`issues/2026-w36.ts:16`) and `issue.weThink.summary`
(`issues/2026-w36.ts:259-260`) already exist and are exactly this: a signed, one-line and one-
paragraph read of the week, dated and attributed. This is **judged**, not tracked — it carries
`signedBy: 'Jesse Pike'` and `signedOn: '2026-09-19'` (`issues/2026-w36.ts:273-274`).

**(c) A by-domain market picture with leading vendors and direction.** Partially buildable. The
posture/tag/horizon per domain is judged fact, already on the page (`domains.ts`, shown by
`DomainBoard`). A leading-vendors-by-growth row per domain is tracked fact where it exists at all
(section 2's count column), but two of six domains (Cloud Security, AI Runtime) cannot honestly
carry one yet, and the metrics that do exist are not consistently the same kind of number
(revenue vs. ARR vs. a product segment), so a table built naively from what exists today would
read as more comparable than it is unless captioned carefully.

**(d) The most consequential events of the period.** Buildable now, and the data already has a
consequence-ranking mechanism built in that a redesign would not need to invent. `ActivityItem`
carries a `surface: 'lead' | 'more' | 'background'` field and an optional `leadOrder` sort key
(`types.ts:209-224`); `ActivityBoard.tsx:33-38` already uses both to put six items first, in a set
order, ahead of everything else. That is tracked fact (each item cites an evidence id) with a thin
layer of judgment sitting on top of it (someone decided which six are `lead` and in what order).
The weekly issue's four lanes (formation, absorption, prints, capital,
`issues/2026-w36.ts:17-256`) are a second, independent way of surfacing "what happened this
week," also tracked, also already ordered by lane and by date.

**(e) A forward look.** Buildable from what exists, and already labelled as judgment rather than
fact. `watchItems` (`watch.ts:3-40`) is a hand-written list of what would change the read, each
with a reason; `weThink.noCalls` and the thesis verdict (`issues/2026-w36.ts:270-275`) are the
same kind of forward statement, signed. Nothing here would need new data gathering, only a
different page position and framing.

Across all five, the print-level `surface?: 'print' | 'coverage'` field (`types.ts:180`) is the
other quiet marking mechanism worth knowing about: it is what already separates "this is a real,
comparable number" from "this is a valuation or a headline with no comparable series," and any
redesign that builds a vendor table should read this field rather than re-deriving the distinction.

## 6. Gaps against the product core

Ordered by how much each matters to a security leader.

1. **No distress or debt signal exists anywhere in the data**, and product-core names this as a
   first-class thing the site should cover (`product-core.md:52-53`). **Needs new data gathering.**
   There is no existing record to rearrange; nobody has sourced this kind of signal yet, and
   product-core's own open-questions register says the sourcing method itself is still unresearched
   (`product-core.md:135`).
2. **AI Runtime and Cloud Security cannot support a "leading vendors by growth" claim today.**
   AI Runtime has zero comparable growth figures; Cloud Security has one. **Needs new data
   gathering** for AI Runtime, since the underlying companies are mostly private and don't report a
   number yet; **needs new data gathering, but a smaller amount,** for Cloud Security, where the
   gap is two named vendors (Orca, Aqua) with no public number at all, already identified in
   `docs/active/domain-vendor-signals-2026-08.md:64-67`.
3. **The scorecard and the weekly issue disagree on how current six major vendors' numbers are, on
   the same page, at the same time**, because the issue pipeline does not write back into
   `prints.ts`, `domains.ts` or `activity.ts`. **Needs a decision from the owner** on which store is
   authoritative going forward, since fixing this is an architecture change, not a data fix.
4. **The founding thesis still leads the first screen** (`Hero.tsx`, `market.ts`), which product-
   core says must change (`product-core.md:71-73`). **Fixable by rearranging what exists** — the
   thesis's own section, its own evidence, and its own running score (`ThesisRunningScore.tsx`)
   already exist as a self-contained block; moving it off the first screen does not require new
   data.
5. **No sentence on the page states what the site is**, for a first-time reader who is not already
   oriented. **Needs a decision from the owner** on the exact wording, since product-core section 1
   already supplies the substance; someone still has to turn it into page copy.
6. **Growth metrics across a domain are not always the same kind of number** (product revenue vs.
   total revenue vs. ARR vs. a product segment's ARR), which would make a naive "leading vendors"
   table look more rigorous than it is. **Fixable by rearranging what exists** — every print
   already states its own `metric` field (`prints.ts`), so a table built from this data can and
   should carry that label rather than hiding it.
7. **The M&A/funding board (`activity.ts`) is stale relative to the weekly issue's own, fresher
   absorption and formation lanes**, and the two never merge. **Needs a decision from the owner**,
   for the same reason as gap 3 — this is part of the same underlying architecture question.
8. **The site's "last updated" badge can read as fresher than the judgments underneath it actually
   are** (section 4). **Fixable by rearranging what exists** — the site already has separate,
   correctly-dated constants for the judged reads (`JUDGED_AS_OF_ISO`) and the site-build stamp
   (`LAST_UPDATED_DISPLAY`) in `meta.ts`; the badge just doesn't currently show the more relevant
   one.
9. **Twelve domains named in the startup-watch research (`docs/active/domain-coverage-map.md`)
   have no corresponding live print or posture** — for example most of the Network/SASE watch list
   (Twingate, Tailscale, Island, Elisity) and most of the Cloud Security watch list (Sysdig,
   Lacework, Blockaid) never made it from that research into `prints.ts` or `domains.ts`. **Needs
   new data gathering** to convert a watch-list name into an actual tracked print, one vendor at a
   time.

## 7. Jargon list

Terms a security leader would not recognize, with where they appear and a plain alternative.
Anything inside the published, locked issue (`issues/2026-w36.ts`, protected by
`issues.lock.json`, see `docs/active/fable-run/codebase-map.md` section 8) cannot be edited without
breaking the build's append-only guarantee; site copy in the components can be changed freely.

| Term | Where it appears | Locked or editable | Plain alternative |
|---|---|---|---|
| "Lag call" / "the lag" | `market.ts:25,29`, `Hero.tsx:30`, `hypotheses.ts:35-49` | Editable (site copy and standing data, not the issue) | "Whether security spending is catching up to infrastructure spending" |
| "Episode" / "Episode 002" | `HowThisWorks.tsx:10`, `MethodologyNote.tsx:7`, `meta.ts:1-2`, `NextEdition.tsx` (posture rule text) | Editable | Drop it, or say "this edition's method" |
| "Prints" / "print" | Page heading "This period" but eyebrow text "N prints across N domains" (`PrintGrid.tsx:78-79`); "Scorecard" nav label (`Header.tsx:18`) | Editable | "Reported figures" or "results" |
| "Formation" / "Absorption" | Issue lane titles, `IssueLanes.tsx:8-9`, and inside the locked issue data (`issues/2026-w36.ts`) | Lane titles are editable in `IssueLanes.tsx`; the underlying lane values (`'formation'`, `'absorption'`) are locked as data keys inside the published issue | "New companies" and "Bought or absorbed" |
| "Posture" labels: PREPARE, INVESTIGATE, NO-CALL | `types.ts:14`, shown on every `DomainBoard` card and the Tempo table | Editable (site copy); the underlying enum is a data-model decision | "Act now," "Watch closely," "Not enough evidence to say" |
| "Tempo" / tag WATCH | `DomainBoard.tsx` (`#domains` section, "Tempo" heading), `types.ts:16` | Editable | "Status" or "Direction" |
| "TRACKED" / "JUDGED" stamps | Throughout: `DomainBoard.tsx:104,109`, `PlatformPressure.tsx:30`, `WhatMoved.tsx:16,30` | Editable | "Reported fact" and "Our call" |
| "No-call" | `market.ts:25`, `hypotheses.ts`, `NextEdition.tsx` postureRule, inside locked issue text (`issues/2026-w36.ts:270-271`) | Mixed: site copy editable, issue's own no-call sentence locked | "Not enough evidence yet to say" |
| "Coverage" (as in a print's `surface: 'coverage'`) | Visible in card class names and the eyebrow's "N covered" count, `PrintGrid.tsx:134-137` | Editable | Drop the word from the visible eyebrow; keep it internally |
| "Vendor lens" | `VendorLens.tsx:28`, nav-adjacent UI | Editable | "Filter by vendor" |
| "Borrowed" (a print counted under a second domain) | `PrintGrid.tsx:169`, "also counted under X" | Editable | "Also relevant to X" |
| "Signal families" / "reasoning steps" | `HowThisWorks.tsx` headings, `method.ts` | Editable | "What we count as evidence" / "How we reach a call" |
| "Freeze" (research freeze date) | `MethodologyNote.tsx:7`, `WatchList.tsx:8` ("before the next freeze") | Editable | "As of" |

Deferred to backlog: this task was read-only survey work with one bounded output file, exactly as
scoped, so there was no in-flight expansion to defer. Two things surfaced worth flagging for
someone else to pick up rather than act on here: the mismatch between the weekly issue's vendor
numbers and the scorecard's older numbers for the same six companies (item 3 above) is an
architecture decision, not something this survey should resolve; and the missing Optiv/distress
signal (item 1) needs a sourcing method that does not exist yet, which product-core already marks
as an open research question rather than something to start building unprompted.
