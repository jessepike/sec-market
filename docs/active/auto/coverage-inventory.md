# Security Market Pulse — coverage inventory vs. product-core

Read-only survey. Today's date for freshness math: 2026-09-25. All paths relative to
`/Users/jessepike/code/projects/sec-market/` unless given in full. Governing statement:
`docs/active/product-core.md` v0.2.

## 1. Pages and sections a reader sees today

Routes come from `web/src/data/routes.ts`, rendered by `web/src/App.tsx`.

- `/` — front page. In order: `SiteMasthead` (one sentence stating what the site is, plus
  disclaimer and last-judged stamp), `IssueStrip` (this week's one-line read), `MarketPicture`
  (an alphabetical, unranked table of tracked domains and their reported vendor figures),
  `WeThink` (signed weekly summary, condensed thesis pointer), `IssueLanes` (the week's four
  lanes: formation, absorption, prints, capital), `FollowLine`, `DomainBoard` (four "landscape"
  cards only — see §2), `PlatformPressure`, `VendorLens` control, `PrintGrid` (the full vendor
  scorecard), `Hypotheses`, `ThesisPointer` (a short pointer to `/thesis/`), then collapsed
  `<details>` depth sections: What moved (edition delta), Domain tempo and M&A activity (all six
  domains plus the `ActivityBoard`), Market layers chart, Watch next, How this is built,
  Research & evidence (evidence library), a methodology note, and "next edition" copy.
- `/issues/` — archive: every issue, newest first, with id, week ending, read line, and
  published/draft status.
- `/issues/<id>/` — one issue's permalink: its hero, its four lanes, its signed "what we now
  think," and links back to the archive and the standing reference.
- `/thesis/` — the founding infrastructure-vs-security-spending thesis, now its own page: one
  framing paragraph, then the full `JudgmentBoard` (thesis running score, hero content, evidence).
- `/corrections/` — every published correction, newest first, plus an explanation of how a
  correction differs from a standing-table fix, and a mailto link to report an error.
- `/feed.xml`, `/issues/<id>.json`, `/issues/index.json` — machine-readable copies, no visible
  reader page.

**Note for the caller:** several gaps the run's own `content-inventory.md` (2026-09-20) flagged as
open have since been closed in the code — the masthead now carries an explicit "what this site is"
sentence (`SiteMasthead.tsx`), and the founding thesis has moved off the first screen to `/thesis/`
(`App.tsx` comments cite `SEC-MARKET-FABLE-001` T6-2 and T6-16). Content-inventory's gaps 4 and 5
are resolved; the rest of this report checks what is still open.

## 2. Domains and vendors tracked, and what's missing against a CISO budget

`web/src/data/domains.ts` defines six domains (`securityDomains`), but only **four** are shown as
front-page cards. `landscapeDomainIds` (`domains.ts:5-10`) is `network-sase`, `data-ai-security`,
`cloud-security`, `identity` — confirmed by `DomainBoard({ surface = 'landscape' })` at
`web/src/components/DomainBoard.tsx:259-260`, which renders `landscapeDomains` (the four) by
default and only shows all six under the collapsed "Domain tempo and M&A activity" `<details>`
(`surface="tempo"`, `App.tsx:91-99`). **SecOps and AI Runtime exist as tracked domains but do not
appear as landscape cards on the first screen a reader sees** — they are one click into a depth
disclosure. This is not called out explicitly in `content-inventory.md`, which was written before
this front-page restructuring; it is a fact I confirmed directly in the current code.

Vendors tracked per domain, from `web/src/data/prints.ts` (45 print records) as catalogued in
`content-inventory.md` §1-2, spot-checked against current `prints.ts` (last touched by the vendor
lens commit `b4413b5`, no scorecard content change since):

- **Network / SASE:** Fortinet, Cloudflare, Zscaler, Check Point, Cato Networks, Netskope — 6
  vendors, all with a growth-rate print. Strongest of the six domains.
- **Data / AI Security:** Rubrik, Varonis (growth-rate prints); Cyera, BigID, Sentra, Securiti
  (capital/M&A records only, no growth rate).
- **Cloud Security:** CrowdStrike (Falcon Cloud segment only); Wiz, Upwind, Orca, Aqua (capital or
  M&A records; Orca and Aqua have no public figure of any kind).
- **Identity:** Okta, SailPoint (growth-rate prints); CyberArk (absorbed, no standalone print),
  Oak, Hush, Veza, Lumos (capital/M&A only).
- **SecOps** (not a landscape card): SentinelOne, CrowdStrike, Cisco Security (growth-rate
  prints); Palo Alto XSIAM (a product segment, not company-level); Tines, Torq (capital only).
- **AI Runtime** (not a landscape card): zero vendors with a disclosed growth or revenue figure.
  Every record is a funding round or an acquisition price (Zenity, Onyx, WitnessAI, Lakera,
  Protect AI, CalypsoAI, SurePath AI).
- Palo Alto Networks and NVIDIA/Arista sit outside any domain ("Infrastructure" or multi-role).

**Major security spending categories with no home**, judged against a normal CISO budget
(endpoint, network, identity, data, cloud, SecOps/SIEM-SOAR, AppSec, vulnerability/exposure
management, email, OT, GRC, MSSP/MDR services):

- **Endpoint protection / EDR** has no distinct domain. CrowdStrike and SentinelOne — both
  endpoint-rooted platforms — are filed under "SecOps," which conflates XDR/SIEM/SOAR/automation
  with endpoint detection. A reader cannot ask "who leads endpoint" on the site today.
- **Managed security services / MDR** — no domain, no vendor. Product-core's own external-review
  section names this gap explicitly (`product-core.md:186`, item 3). `content-inventory.md`
  confirms Optiv — the named example of a distress signal the owner wants captured
  (`product-core.md:52-53`) — appears nowhere in `web/src/data/`.
- **Vulnerability / exposure management** — no domain, no tracked vendor. Tenable, Qualys,
  Rapid7's exposure line, and Axonius appear only in research files
  (`docs/active/domain-coverage-map.md`, "Exposure management" callout), never in `prints.ts`.
- **Application security / supply chain** — no domain, no tracked vendor (Snyk, Semgrep,
  Chainguard named only in the research callout, not live).
- **Email / human-layer security** — no domain, no tracked vendor (Abnormal Security named only
  in the research callout).
- **OT / industrial security** — no domain, no tracked vendor (Claroty, Dragos, Nozomi named only
  in the research callout).
- **Post-quantum / crypto-agility** — no domain, thin in research only.

`docs/active/domain-coverage-map.md` (2026-08-16, marked "not for publication") already did the
watch-list legwork for all of these callout domains plus a 20-name first-add list, but none of it
has been converted into a live print or posture in `prints.ts` or `domains.ts` — content-inventory
gap 9 makes the same point.

## 3. Signal types product-core names, one by one

Product-core §4 (`product-core.md:51-57`) names: earnings/growth by vendor, funding, M&A and
consolidation, shutdowns/layoffs/debt/distress, platform moves, per-domain leading vendors and
their footing, and AI security as a market (not as news).

| Signal | Collected weekly? | Shown on site? | Freshness | Source used |
|---|---|---|---|---|
| Earnings / growth by vendor | Yes — "prints" lane, per `gather-brief.md` §2 (EDGAR 8-K/10-Q, EX-99.1) | Yes — issue lanes, `PrintGrid`, `MarketPicture` | Issue lane figures are days old at publish; the separate `prints.ts` scorecard is stale (newest single print 2026-08-12, most entries 45-600+ days old per `content-inventory.md` §4) and the two never reconcile | SEC EDGAR primary filings |
| Funding rounds | Yes — "formation" lane | Yes — issue lanes, `ActivityBoard` (depth) | Weekly, but `activity.ts` (the separate funding/M&A board) is stale (newest 2026-08-03) and not updated by the issue pipeline | Return on Security, Cybersecurity Ventures, specialist VC pages, SecurityWeek |
| M&A / consolidation | Yes — "absorption" lane | Yes — issue lanes, `ActivityBoard` | Same split-freshness problem as above | SecurityWeek, EDGAR 8-K Item 1.01/2.01, acquirer press releases |
| Distress: debt, layoffs, shutdowns, ratings | **No.** Not in the gather brief's source manifest at all (`gather-brief.md` §2 has no distress row) and not in `verify-issue.ts`'s lane types (`Lane = 'formation' \| 'absorption' \| 'prints' \| 'capital'`, `weekly-issue-spec.md:59`) | **No.** Zero matches for layoff/bankrupt/debt/distress/going-concern/etc. anywhere in `web/src/data/` (confirmed by direct grep today) | N/A — no data exists | A full sourcing method exists on paper only: `docs/active/fable-run/research/11-distress-signal-sources.md`, a five-rung evidence ladder (SEC EDGAR filings and Item 2.05 disclosures down to trade-press reports), tested on three real cases (Allied Universal, Rapid7, PlaxidityX). Open question 12 in product-core (`product-core.md:146`) still marks this "Open. Needs research," even though the research now exists — it has not been wired into the gather job or `types.ts`'s `Lane` type |
| Platform moves (bundling, absorbing) | Yes — inferred from "absorption" lane items and PlatformPressure's own data | Yes — `PlatformPressure` component, e.g. Wiz/Google, CyberArk/Palo Alto | Tied to the same M&A freshness as above | Acquirer press releases, EDGAR |
| Per-domain leaders and their footing | Partial. `content-inventory.md` §2 found only Network/SASE, SecOps and (thinly) Data/Identity could honestly support a "leading vendors" claim; Cloud Security has one usable figure and AI Runtime has zero | Yes, as the alphabetical `MarketPicture` table (explicitly "not ranked," per the caption in `MarketPicture.tsx:24-27`) rather than a ranked leaderboard — this is a direct response to the external review's finding 2 (below) | Domain postures (`asOf`) are 40 days old today (2026-08-16); tracked prints behind them are older still | `prints.ts`, judged by hand |
| AI security as a market | Partial — heavy on the "formation" side (nearly every AI-security company in the data is a funding round: Zenity, Onyx, WitnessAI, Exein, HiddenLayer, AIR Security, etc.), essentially absent on the "footing" side | Yes, via the "AI Runtime" domain (depth-only, not a landscape card — see §2) and via issue lanes | Funding rounds are fresh (w38 draft has 8 in one week); footing evidence is nonexistent — zero AI-security vendor in the data has disclosed a growth or revenue figure (`content-inventory.md` §2) | Formation-lane sources only |

## 4. The weekly gather's actual output mix

**Issue 2026-w36** (published, signed 2026-09-19; window 2026-08-24 to 2026-09-03):
formation 7 items, absorption 6 items, prints 8 items, capital 2 items — 23 items total.
Formation and absorption together (13 items, 57%) are funding rounds and mostly-undisclosed M&A;
prints and capital together (10 items, 43%) are public-issuer earnings and infrastructure capex.
Every prints/capital item is a public company reporting a real, audited figure; every formation
item and five of six absorption items with a disclosed amount are private-company funding or
undisclosed-terms deals.

**Issue 2026-w38 draft** (unsigned, window 2026-09-14 to 2026-09-20, per
`git show origin/issue/2026-w38:web/src/data/issues/2026-w38.ts`): formation 8 items, absorption
1 item, prints **0** items ("None found this week"), capital **0** items ("None found this week")
— 9 items total. **100% of this draft's substantive content is early-stage AI-security funding
rounds** (AIUC, Eve Security, Exein, StrikeReady, MIND, Comp AI, QueryLift, TigerByte Cyber — all
seed through Series B) plus one disclosed acquisition (S&P Global/OpenZeppelin). No earnings print,
no capital/infrastructure item, and therefore no fresh evidence at all for any domain's posture,
footing, or the standing infrastructure-vs-security thesis; the draft's own `proposed.noCalls`
says as much ("no comparable earnings prints or capital-spend evidence landed in-window").

Across the two available weeks, the mix swings entirely on what companies happened to report that
week — w36 was earnings-heavy because several large public vendors reported in-window; w38 landed
in a quiet earnings week and is therefore almost pure early-stage funding. Neither week contains a
distress, debt, or layoff item, because none is collected (see §3).

## 5. What the site shows that product-core says it should not be

- **Small, single-founder funding rounds with no path to a growth print** make up the majority of
  both sampled weeks' item counts (7 of 23 in w36; 8 of 9 in w38). Product-core does not forbid
  funding coverage — funding is a named signal — but it does say the site "is not where I go for my
  security news" and should look back/ahead at what "actually happened" in filings and public
  numbers, not day-to-day announcements. A $60K pre-seed round (w36-formation-4, Opgate) or a $2.6M
  pre-seed (w36-formation-2, KAZIMI) reads closer to a funding-news ticker than a market-pulse
  signal a CISO would use for a vendor decision. This is consistent with the external review's
  finding 12 (below): cut the requirement to carry the full four-lane inventory on the front page,
  and let selected buyer-relevant developments lead instead.
- **The founding infra-vs-security thesis** no longer leads the first screen (moved to `/thesis/`,
  confirmed in `App.tsx`), so the site has already corrected the one item product-core flagged most
  directly (§5, "leaves the first screen"). This gap, open as of `content-inventory.md`, is closed.
- **Investor framing** is not present in the live site copy I read (no investment-advice language
  found in `SiteMasthead`, `MarketPicture`, or the issue text), consistent with product-core's "no
  investment advice" stance. I did not find an explicit "not investment advice" disclaimer either,
  which the practitioner-market research flags as something the closest peer (Return on Security)
  also omits without apparent harm to trust (`10-practitioner-market-pulse.md`, Question 5 /
  "What disagrees").
- **No sentence on the page discloses the owner's employer or advisory relationship to the vendors
  covered.** Product-core's own external-review section (§10.2, `product-core.md:181-183`) and the
  Codex `gpt-6-astra` review (finding 5, below) both call this out as unresolved; I found no such
  disclosure anywhere in `SiteMasthead.tsx`, `meta.ts`, or the corrections page.

## 6. What the external reviews and research recommend, in their own words

**Codex (`gpt-6-astra`) external review**, `docs/active/fable-run/consults/external-review-astra.md`
(2026-09-20), reviewing `product-core.md` v0.1, `site-rubric.md` v2.0, and `design-spec.md` v0.3:

- Finding 1: "The design postpones the content that would justify its primary audience... A
  security leader needs implications for supplier continuity, renewals, product support,
  consolidation, switching costs and alternative suppliers. These fit the stated scope without
  becoming product reviews."
- Finding 2: "Replace the growth leaderboard with a supplier comparison that does not declare
  winners... I would use an alphabetical 'Tracked suppliers' table within clearly defined
  purchasing categories" — this is exactly what `MarketPicture.tsx`'s caption now implements
  ("listed alphabetically... not ranked").
- Finding 3: "Make a dependable weekly account of material changes the recurring product... Lead
  with the few developments that matter most to buyers across all event types."
- Finding 4: the facts-vs-judgments boundary "leaks" — choosing vendors, metrics, and "why it
  matters" language is itself judgment, not mechanical fact.
- Finding 5: "The reseller relationship requires substantive editorial safeguards... Disclose the
  owner's employer and commercial role prominently."
- Finding 11: "The coverage promise exceeds both the taxonomy and the evidence... Six inherited
  domains do not establish coverage of the market a security program buys from. Endpoint and
  managed security services lack explicit homes."
- Finding 12: "Cut three things from the front page" — the growth podium, the thesis-centered
  headline, and the full four-lane inventory on the homepage.
- Verdict: "the core deserves to continue, but I would not approve v0.3 as the buyer-facing
  design... Lead with consequential changes, make vendor comparisons defensible, and prove the
  weekly service before promoting it."

**Practitioner-market research** (`10-practitioner-market-pulse.md`, 2026-09-20): recommends the
by-domain view read "like Gartner's 'overall viability' criterion, not a league table" — state
financial health and what evidence it rests on. Recommends treating distress the way product-core
already proposes: "a dated funding round, an M&A filing, a layoff report, each with its own source
and its own date, kept separate from any posture judgment." Recommends author disclosure be
"direct rather than modest" — every trusted solo practitioner examined states plainly who they are
and what they do for a living. Recommends a cadence promise sized to what can actually be kept:
"pick the slowest cadence you can guarantee, state it once, and never promise in week one a cadence
that will not still be true in week forty."

**Distress-signal research** (`11-distress-signal-sources.md`, 2026-09-20): recommends building on
free government/corporate-primary sources first (SEC EDGAR full-text search and company-facts JSON
APIs, confirmed working; state WARN Act notices, California confirmed machine-readable). States the
core safety rule: "never publish a claim about a named company's finances unless it restates, in
the source's own words with a link and a date, something a primary source actually said," and that
because the owner sells these vendors' products, "the editorial policy should probably require a
second, cited source before any headline-level distress claim goes live."

## 7. Sources read for this inventory

`docs/active/product-core.md`, `docs/active/fable-run/content-inventory.md`,
`docs/active/domain-coverage-map.md`, `docs/active/fable-run/research/10-practitioner-market-pulse.md`,
`docs/active/fable-run/research/11-distress-signal-sources.md`,
`docs/active/fable-run/consults/external-review-astra.md`,
`docs/active/fable-run/drafts/buyer-brief-network-sase.md`, `docs/active/weekly-issue-spec.md`,
`docs/active/gather-brief.md`, `web/src/data/domains.ts`, `web/src/data/prints.ts` (spot-checked),
`web/src/data/issues/2026-w36.ts`, `origin/issue/2026-w38:web/src/data/issues/2026-w38.ts` (via
`git show`), `web/src/App.tsx`, `web/src/data/routes.ts`, `web/src/components/DomainBoard.tsx`,
`web/src/components/MarketPicture.tsx`, `web/src/components/SiteMasthead.tsx`,
`web/src/components/Corrections.tsx`.
