# Baseline score — production, 2026-09-20, rubric v2.0

**Instrument:** `docs/active/fable-run/site-rubric.md` v2.0 (re-aimed at `docs/active/product-core.md`)
**Deployment scored:** production, https://securitymarketpulse.com, serving `main` at `aa04875` (per `score-baseline.md`, same day, same deployment; the teardown confirmed production and `preview` render identically on 2026-09-20)
**Scoring date:** 2026-09-20
**Scorer:** independent `claude-sonnet-5` scorer, task T6-3 of run SEC-MARKET-FABLE-001, working from the evidence already collected under `docs/active/fable-run/evidence/baseline/` and `docs/active/fable-run/research/07-site-teardown.md`, without access to any other scorer's v2.0 answers.

This baseline is not comparable with the v1.2 number (33.0). Four dimensions were rewritten (D1 to
D4) and one more (D11) was reshaped; the other eight keep their v1.2 test wording, per the rubric's
own revision note.

## Coordinator reconciliation to rubric v2.1 (added 2026-09-20)

The scorer worked under rubric v2.0. While it was running, the rubric moved to v2.1 after the
external review. Everything below this section is the scorer's v2.0 record, left unedited. This
section restates the result under v2.1, which is the number to compare the rebuilt page against.

**Under v2.1, production is: not fit for purpose (blocker 1, factual meaning). Composite 32.8 out
of 100. Exposure denominator 1.**

Blocker 1 fails because the signed issue `2026-w36` labels two fourth-quarter revenue figures as
full-year figures (Zscaler $898.2M and Palo Alto $3.41B, `web/src/data/issues/2026-w36.ts` lines
168 and 208, against evidence records W36-15 and W36-19). Blocker 4 (accessibility) passes on the
scorer's D10 record. Blockers 2 and 3 were not checked by this scorer and are checked in the
re-score of the rebuilt page.

Two scores change because v2.1 changed level-3 tests. The level-5 changes (D1 test 1, D4 test 1,
D12 tests 4 and 5) do not move anything, because those dimensions do not pass level 3.

| Dimension | v2.0 score | v2.1 score | Why |
|---|---|---|---|
| D3 Freshness | 2 | 1 | Level-3 test 5 now asks that the period a figure covers, the date its source was published and the date it was last checked are kept apart and shown. Production shows one date badge per card. Two of five level-3 tests pass, which is fewer than half. |
| D12 Trust | 2 | 1 | New level-3 test 5 asks that the author's professional role and relevant commercial relationships are disclosed within one click. Production has no such disclosure. Two of five level-3 tests pass. |

| # | Dimension | v2.1 weight | Score /5 | Points |
|---|---|---|---|---|
| D1 | Market picture clarity | 10 | 1 | 2.0 |
| D2 | Look back, look ahead | 7 | 2 | 2.8 |
| D3 | Freshness and reason to return | 15 | 1 | 3.0 |
| D4 | Decision value for a security leader | 20 | 1 | 4.0 |
| D5 | Evidence legibility | 12 | 3 | 7.2 |
| D6 | Density and scanability | 4 | 2 | 1.6 |
| D7 | Wayfinding | 3 | 1 | 0.6 |
| D8 | Agent legibility | 3 | 2 | 1.2 |
| D9 | Performance | 4 | 2 | 1.6 |
| D10 | Accessibility | 8 | 4 | 6.4 |
| D11 | Follow and share | 3 | 0 | 0.0 |
| D12 | Trust and authority | 10 | 1 | 2.0 |
| D13 | Craft | 1 | 2 | 0.4 |
| | **Composite** | 100 | | **32.8** |

## What this number is not

**Composite: 37.2 out of 100. Exposure denominator: 1.** The project's own outcome scorecard,
`docs/active/project-scorecard.md`, records that exactly one person has had a real chance to use
this site and that no decision is logged as changed by it. This composite says nothing about that,
and neither would a higher number.

## Result

| # | Dimension | Weight | Score /5 | Arithmetic | Points |
|---|---|---|---|---|---|
| D1 | Market picture clarity | 14 | 1 | 1/5 × 14 | 2.8 |
| D2 | Look back, look ahead | 10 | 2 | 2/5 × 10 | 4.0 |
| D3 | Freshness and reason to return | 12 | 2 | 2/5 × 12 | 4.8 |
| D4 | Decision value for a security leader | 12 | 1 | 1/5 × 12 | 2.4 |
| D5 | Evidence legibility | 9 | 3 | 3/5 × 9 | 5.4 |
| D6 | Density and scanability | 8 | 2 | 2/5 × 8 | 3.2 |
| D7 | Wayfinding | 5 | 1 | 1/5 × 5 | 1.0 |
| D8 | Agent legibility | 7 | 2 | 2/5 × 7 | 2.8 |
| D9 | Performance | 5 | 2 | 2/5 × 5 | 2.0 |
| D10 | Accessibility | 7 | 4 | 4/5 × 7 | 5.6 |
| D11 | Follow and share | 3 | 0 | 0/5 × 3 | 0.0 |
| D12 | Trust and authority | 5 | 2 | 2/5 × 5 | 2.0 |
| D13 | Craft | 3 | 2 | 2/5 × 3 | 1.2 |
| | **Composite** | **100** | | sum of points | **37.2** |

Weight check: 14+10+12+12+9+8+5+7+5+7+3+5+3 = 100.

Points sum: 2.8+4.0+4.8+2.4+5.4+3.2+1.0+2.8+2.0+5.6+0.0+2.0+1.2 = **37.2**.

**Caps applied.** Cadence cap (D3): not triggered. The newest signed issue published 2026-09-19,
one day before the scoring date, well inside the 14-day limit. Misstated-freshness cap (D12):
triggered, but it changes nothing, because D12's own tests already land it at 2. The site's closed
Method section states "Refresh is manual... Not a weekly news cycle" while the rest of the site
frames the one issue as a numbered week ("ISSUE 2026-W36 · WEEK ENDING 6 SEP 2026") — a cadence
statement that contradicts another statement on the site, which is exactly what the cap names.

**The shape of the result.** The four dimensions the product core cares about most (D1, D2, D3, D4)
carry 48 of the 100 weight and earn 14.0 of it. The site is strongest exactly where the v1.2
baseline already found it strong: evidence handling (D5 at 3) and accessibility (D10 at 4). Almost
everything that would move D1 and D4 already exists on the page, several thousand pixels lower than
the first screen — the domain landscape table, the "what changed / do / avoid" block, and the
signed thesis are all real, evidenced, well-built content that a redesign would reorder rather than
invent.

## Evidence key

| Short name | Path (all under `docs/active/fable-run/` unless given in full) |
|---|---|
| M§n | `evidence/baseline/measurements.md`, section n |
| X Tn | `evidence/baseline/machine-extraction.md`, task n, including the coordinator's correction note at the top |
| T | `research/07-site-teardown.md` |
| E | `evidence/baseline/evidence-drawer.md` |
| CI | `content-inventory.md` |
| TH | `research/08-thesis-history-inventory.md` |
| V1440 / V390 | `evidence/baseline/prod-home-1440-viewport.png` / `prod-home-390-viewport.png` |
| tile NN | `evidence/baseline/tiles/home-1440-NN.png`, the desktop front page in 1,800px slices (00 = 0–1800px, 01 = 1800–3600px, and so on) |
| issues-full | `evidence/baseline/prod-issues-1440-full.png` |
| issue-full | `evidence/baseline/prod-issue-w36-1440-full.png` |
| SB1 | `score-baseline.md` (v1.1), reused only for D5–D7, D9, D10, D12, D13, whose tests are unchanged in v2.0 |

Two claims in the teardown are superseded and were not reused: that four `h2` elements are empty
(M§7 shows none are), and that the home page and the issue permalink are identical (true only of
what renders in the first viewport; the permalink is 31,482 bytes of HTML against 216,418 for home,
X T12).

## Per-dimension record

### D1 — Market picture clarity — score 1 (weight 14)

| Test | Result | Evidence |
|---|---|---|
| L3-1: one plain line on the first screen, at both widths, says what the site is, who it is for, who writes it | No | V1440, V390: the first screen shows only the provenance bar, nav, and the week's headline. The line "An evidence-linked read on the cybersecurity market for security leaders..." exists only in JSON-LD (X T2), not rendered. |
| L3-2: the first screen at both widths carries this period's read as a statement about the market, not only a list of tracked items | Yes | The h1 itself states a market call — "the infra-to-security lag call holds" (V1440, V390) — before any tracked item appears. |
| L3-3: no term on the first screen needs another page to decode it | No | The h1 ends "...the infra-to-security lag call holds" and the section directly below is headed "Formation" (V1440) — both are the exact undecoded-jargon case the test names. |
| L3-4: within first screen plus one scroll at 1440 (under 1,800px), a by-domain picture is visible without expanding anything | No | tile 00 (0–1,800px) shows the headline and the start of the Formation lane only. No domain content appears before 1,800px. |
| L5-1: leading vendors named with a current, sourced figure and date, in a table for comparison | Yes | tile 04, "Who is holding, who is buying in, who is being outrun" — a table with Vendor / Position / Latest tracked print / Judged read columns; tile 05–07, "This period" scorecard cards grouped by domain, each dated. |
| L5-2: consolidation and distress each have a visible place of their own, saying "none recorded this period" when empty | No | "Absorption" is a real, populated lane (tile 00–01). Distress (debt, layoffs, shutdowns) has no section at all, not even a placeholder — confirmed by CI §3: "No distress signal of any kind exists in the data." |
| L5-3: cold reader test — shown the first-screen capture for ten seconds, a scorer writes what the site is for and one true thing about the market | No | The actual administered cold read (`evidence/baseline/independent-scores.md`, D1) used this same first-screen image and produced "the site argues infrastructure/AI-chip spending has outrun any broad cybersecurity spending boom, and that gap is holding" — a true market fact, but no statement of what the site is or who it's for, which the image does not supply. |
| L5-4: every domain and every vendor has a stable address that can be linked and forwarded | Not scored | No measurement in the evidence set confirms or denies per-domain or per-vendor anchor ids on the scorecard cards; the only ids/anchors actually measured are for issue lane items (X T6, independent-scores D7), a different set of elements. |

Raise by one: put one plain sentence on the first screen, at both widths, saying what the site is,
who writes it, and who it's for.

### D2 — Look back, look ahead — score 2 (weight 10)

| Test | Result | Evidence |
|---|---|---|
| L3-1: "what changed since the last update" is visible without expanding anything, and says so plainly when nothing changed | Yes | tile 03, "The read" section: an open "WHAT CHANGED" numbered list of four dated items, not behind any disclosure. The accompanying paragraph states plainly that the pattern is "not a change to" the standing call. |
| L3-2: backward view — figures carry period and date, and a reader sees at least the previous period or direction of travel, not a single point | Yes | Every domain card in tile 03 carries a small direction glyph next to its name (an up-right arrow for Network/SASE and Data/AI Security, a different mark for Cloud Security and Identity), distinct per domain and consistent with each card's own posture text. |
| L3-3: a forward view exists, labelled as judgment, carries its confidence, and says what would change it | Yes | tile 02–03: "CONFIDENCE · MEDIUM" badge on the thesis block; "What would change the call," four conditions, open on the page. |
| L3-4: every past judgment shown is dated and attributed (signed by a named person, or marked as an unsigned record) | No | The one weekly verdict is dated and signed ("Signed by Jesse Pike · 19 Sep 2026," tile 02). The domain posture judgments carry only "JUDGED 16 AUG 2026" (tile 03) with no name or explicit unsigned marker at that instance; the sitewide legend defines what "JUDGED" means in general but does not attribute this specific judgment to a person where it appears. |
| L5-1: standing analyses each have a stable address with their dated record in order, distinguishing signed from unsigned | No | The thesis has an anchored address, but its dated history is split: the signed verdict sits in the open thesis block (tile 02) while the edition-by-edition record sits inside the closed "What moved: edition delta" disclosure (tile 08) — no single surface shows the ordered, signed-vs-unsigned record. |
| L5-2: each forward call lists its change conditions, each with a current status and a date | No | "What would change the call" (tile 03) is four plain bullets with no per-item status or date. |
| L5-3: a corrections record exists at a stable address, and says "none to date" when empty | No | The corrections block states outright "There is no form and no list" (tile 08) — the opposite of a record, not an empty one. |
| L5-4: how judgments are made and scored is stated once, in plain sentences, at a stable address | Yes | "How a posture is set," tile 08: "One strong print is a card. A domain posture needs more than one company and a reason the motion is not just share shift or M&A." This test carries no visibility constraint, so sitting behind a closed "How this is built" disclosure does not disqualify it. |
| L5-5: a calibration view compares stated confidence with outcomes, or says when there will be enough history to show one | No | No such statement found anywhere in the captured content; the nearest text ("No series exists to test it against yet," tile 05) addresses one hypothesis, not calibration generally. |

Raise by one: none needed to reach 3 — the site already clears all four level-3 tests once the
attribution reading above is granted; if scored the other way (see ambiguous tests), raise by one by
adding a name to each domain posture's "JUDGED" stamp.

### D3 — Freshness and reason to return — score 2 (weight 12)

Cadence cap: not triggered. Newest issue published 2026-09-19, scored 2026-09-20 — one day, well
inside 14.

| Test | Result | Evidence |
|---|---|---|
| L3-1: date of newest update and period it covers visible in the first screen | Yes | "ISSUE 2026-W36 · WEEK ENDING 6 SEP 2026 · PUBLISHED 19 SEP 2026" (V1440, V390). |
| L3-2: cadence stated as a sentence reached without expanding, uncontradicted | No | The only cadence sentence, "Refresh is manual... Not a weekly news cycle," sits inside the closed "How this is built" disclosure (T) — not reachable without expanding, so this test fails on reachability alone, before even reaching the contradiction question. |
| L3-3: what is new is identifiable on the front page without comparing pages by memory | Yes | The open "WHAT CHANGED" list (tile 03) states dated, specific developments without requiring the reader to hold a prior page in memory. |
| L3-4: at least one way to be told of a new update, visible without expanding | No | No visible feed/subscribe text anywhere in the rendered body (T: `grep` of the body for "subscribe", "newsletter", "rss" matches nothing); the feed exists only as an invisible `<link rel="alternate">` in `<head>` (X T1). |
| L3-5: every dataset on the front page shows its own "as of" date, and nothing over 45 days old is shown without saying how old it is | Yes | Every card in tiles 00–07 carries a dated badge (e.g., "JUN '26," "APR '26"); a shown date is itself the mechanism by which a reader can tell how old a figure is, even where CI §4 shows many of those dates are, in fact, well over 45 days old. |
| L5-1: if the promised cadence is missed, the site says so without hand-editing | No | No such mechanism found anywhere in the evidence; the site does not commit to a cadence explicit enough to be checkably "missed." |
| L5-2: the front page differs from the issue permalink in purpose — front page shows the current picture, permalink is the record of one period | Yes | X T12: the permalink is 31,482 bytes with 6 headings and no domain/vendor content; the home page is 216,418 bytes with 108 headings including the standing domain and vendor landscape. The permalink carries only the one period's lanes and thesis verdict; the standing picture lives only on the front page. |
| L5-3: the age of the newest update is honest at a glance | No | CI §4, "A freshness trap worth naming plainly": the header badge reads "September 19, 2026" because the site rebuilt to ship the issue, but the domain postures, platform-pressure reads and tracked hypotheses underneath were last reviewed 2026-08-16/17, over a month earlier, with nothing on the page marking that gap. |
| L5-4: a returning reader can see the last three updns' headlines from the front page, or as many as exist | No | The front page itself shows only the current issue's headline; a list of past headlines exists nowhere on the front page (only a single archive row on the separate `/issues/` page, issues-full). |

Raise by one: state the cadence sentence in the open (outside any disclosure), worded so it does not
contradict the weekly issue numbering.

### D4 — Decision value for a security leader — score 1 (weight 12)

| Test | Result | Evidence |
|---|---|---|
| L3-1: five seconds — the first screen at both widths carries a statement of judgment | Yes | The h1 states the call, not a raw headline of items (V1440, V390). |
| L3-2: thirty seconds — within two screens of scrolling at 1440, reach what changed and what it means, without expanding | No | "What changed" and "do/avoid" sit in tile 03, roughly screens 7–8 of scrolling (M§8 places the signature at 5.71 viewport-heights down), well past two screens. |
| L3-3: highest-consequence events ordered or marked as such | No | Formation lane items run in date order only: a $2.6M pre-seed sits ahead of nothing larger by any visual cue (tile 00; T notes a $2.5M round and a $96.2B print share one template). |
| L3-4: at 390, first screen matches desktop order, and site chrome is at most a quarter of viewport height by DOM | No | Chrome height at 390 is 221px of 844px, 26.2 percent of the viewport (E, "Measurement 2: Chrome Height") — over the quarter (25 percent) ceiling, even though content order otherwise matches. |
| L5-1: the vendor question answerable in under a minute, from one view, with a source behind every figure | Yes | The Platform Pressure table (tile 04) gives vendor, position, latest tracked print with a source link, and a judged read in one table; the "This period" scorecard (tiles 05–07) sources every figure. |
| L5-2: everything essential sits within the first 5,000px at 1440, by DOM | No | The signature sits at y=5,137 (M§8) and the domain landscape/vendor table extend well past it, to roughly 9,000px. |
| L5-3: the first screen names the reader it is written for | No | No such text exists on the first screen (same evidence as D1 L3-1). |
| L5-4: nothing on the first screen is decoration | Yes | Every element on the first screen is provenance, navigation, judgment, or a sourced item (V1440, V390) — nothing purely ornamental. |

Raise by one: none of the level-3 tests pass except the first, so raising to 2 needs at least one
more — the cheapest is trimming phone chrome under 211px (about 10px), which would also make the
390 order-and-chrome test pass outright.

### D5 — Evidence legibility — score 3 (weight 9, tests unchanged from v1.2)

| Test | Result | Evidence |
|---|---|---|
| L3-1: source named next to each item, with a link or control | Yes | Every card has a source chip (tile 00–01); the chip opens a drawer with a real "Canonical source" `href` to `https://www.returnonsecurity.com/p/security-funded-259` (E, Measurement 1a) — satisfies the rubric's own "link or control" definition. |
| L3-2: every judgment block shows the evidence it rests on, within one interaction | Yes | The thesis block has a "Sources" button opening an 11,918-character bibliography with 10 links (E, Measurement 1c). |
| L3-3: tracked and judged facts visually distinguishable wherever both appear | Yes | The top bar legend ("TRACKED · public prints, no judgment" / "JUDGED · signed and dated by a person," V1440) plus repeated TRACKED/JUDGED column labels in the platform-pressure table and domain cards (tile 03–04). |
| L3-4: dates of underlying events shown on items | Yes | Every card carries a `<time dateTime>` element; 92 on the home page (X T12). |
| L5-1: figures carry their evidentiary kind where they appear | No | Source class ("INDEPENDENT") is shown only inside the opened evidence drawer, not next to the figure on the card itself (E). |
| L5-2: publisher and date retrieved reachable in one interaction without losing place | No | The drawer shows publisher and publication date, but no explicit "retrieved" or "fetched" date, even though the underlying JSON holds `retrievedAt` (E; X T11). |
| L5-3: conflicting evidence shown next to the judgment, without expanding a closed section | No | "Limitations/confounds" text lives inside the drawer, which requires a click to open — not visible next to the judgment by default (E). |
| L5-4: a way to report a wrong figure is reachable from the evidence itself | No | Only one global mailto/"send a correction" control at the foot of the page (tile 08), not attached to individual evidence items. |

Raise by one: none needed to reach 4 without more L5 passes — the cheapest is showing the source
class (filing / IR / independent / estimate) on the card face itself, next to the figure.

### D6 — Density and scanability — score 2 (weight 8, tests unchanged)

| Test | Result | Evidence |
|---|---|---|
| L3-1: at least eight items per 1440×900 screen, four per 390×844 | No | tile 00: roughly two to three Formation cards fit per 900px scrolled. |
| L3-2: items that differ greatly in consequence differ visibly | No | The Formation/Absorption/Prints/Capital lanes use one unvarying card template regardless of size — a $2.5M round and NVIDIA's $96.2B print carry identical visual weight (T; tile 00, 02). |
| L3-3: tabular figures align, metadata has consistent treatment distinct from prose | Yes | The Platform Pressure and This Period tables use aligned monospace figures with consistent date/metric labelling distinct from the prose sentences beneath (tile 04–07). |
| L3-4: body text at least 14px, prose line length 50–80 characters at 1440 | Yes | SB1 D6: `.issue-lane__why` measured at 14.4px; `--prose-max: 68ch`, inside the 50–80 range. |
| L5-1: front page under 6,000px at 1440 and 9,000px at 390, by DOM | No | 15,022px at 1440 and 17,715px at 390 (M§8) — both well over. |
| L5-2: any comparison of more than three entities is a table with fixed columns, not prose or cards | No | The "This period" scorecard (tiles 05–07) shows dozens of vendors as cards, not a fixed-column table; only the separate Platform Pressure section (tile 04) is a real table. |
| L5-3: row rhythm from spacing, not small type — no continuous reading text under 13px | Yes | Shortest continuous prose measured at 14.4px, above the 13px floor (SB1 D6, live stylesheet). |
| L5-4: a reader can scan one full lane without scrolling at 1440 | No | The Formation lane alone spans roughly two screens at 1440 (tile 00–01). |

Raise by one: none needed to reach 3 — all four level-3 tests would need to pass; the cheapest fix
is giving the highest-consequence items in each lane a visible size or weight cue, which would also
help D1 L3-3/D4 L3-3.

### D7 — Wayfinding — score 1 (weight 5, tests unchanged)

| Test | Result | Evidence |
|---|---|---|
| L3-1: every issue has a permanent URL; archive lists date and verdict as a distinct labelled field | No | issues-full shows one row with id, week, headline, signer, and date, but no separate verdict field — the word "holds" appears only inside the headline text, which the rubric explicitly disqualifies. |
| L3-2: current location indicated; a past issue says it is not the newest and links to the newest | No | issue-full (the full permalink page) ends with "Back to the archive · Standing reference" and carries no "this is/is not the newest issue" indicator or link to a newer one; with only one issue, the mechanism itself is absent, which the honesty-at-small-scale rule scores as a fail. |
| L3-3: main sections reachable by in-page navigation at both widths | Yes | Seven nav anchors (Issue, Archive, Thesis, Landscape, Scorecard, Evidence, Method) at 1440; the same behind a "Menu" toggle at 390 (M§3–4). |
| L3-4: every section heading and lane item has a linkable anchor | No | 0 of 23 issue lane items carry an `id` (independent-scores.md, D7, confirmed by grep of the live HTML). |
| L5-1: issues link to the previous and next issue | No | No such links anywhere on issue-full. |
| L5-2: standing analyses and dated issues cross-reference each other in both directions | No | issue-full links forward to "Standing reference," but the thesis's own running-score line on the home page ("Holds in 1 of 1 issues since 19 Sep 2026," tile 02) is plain text with no link back to the issue — only one direction of the cross-reference exists. |
| L5-3: a reader can filter or find items across issues by vendor or domain, discoverable from the page | Yes | A search/filter control ("Search organization, excerpt, or tag…", "Source class") exists inside the evidence library, discoverable by expanding it (independent-scores.md, D7). |
| L5-4: keyboard shortcuts for next/previous issue and jump to the market picture exist and are documented | No | No documented keyboard shortcuts found anywhere. |

Raise by one: none needed to reach 2 without a second level-3 pass — the cheapest is giving every
lane item and issue row a linkable `id`.

### D8 — Agent legibility — score 2 (weight 7)

| Test | Result | Evidence |
|---|---|---|
| L3-1: all content in prerendered HTML; cold agent extracts the week's headline and items without executing scripts | Yes | X T1, T3 — curl alone recovers the full page. |
| L3-2: archive and each issue available as JSON, discoverable from the home page or sitemap without guessing | No | `sitemap.xml` lists only the three HTML URLs; `/issues/2026-w36.json` and `/issues/index.json` both return 200 (X T1, coordinator correction) but nothing on the site links to either. |
| L3-3: each issue's JSON carries its evidence records with source URLs | Yes | 23 evidence records, each with `canonicalUrl`, `sourceClass`, `retrievedAt` and a retrieval hash (X T6, T11). |
| L3-4: valid JSON-LD on every route identifies page type, author, and dates | No | The `/issues/` page's `CollectionPage` JSON-LD carries neither `author` nor date fields, unlike the `Report` and `Article` blocks on home and the issue page (independent-scores.md, D8, curl-confirmed). |
| L3-5: a feed exists and is advertised by an autodiscovery link | Yes | `<link rel="alternate" type="application/rss+xml">` on the home page (X T1). |
| L5-1: the cold agent gets the current read, confidence, author, date, and the by-domain picture from structured data, without parsing prose | No | The guessed JSON gives verdict, confidence, `signedBy`, `signedOn` (X T4) — but the by-domain picture (postures, tags, horizons) is not present in that JSON or in any JSON-LD; it exists only as rendered markup driven by `domains.ts`, which the cold agent never reaches. |
| L5-2: each claim/lane item has a stable anchor id, citable by URL, appearing in the JSON | No | The issue page has zero `<a href>` elements; evidence ids (e.g. `W36-14`) are not dereferenceable as URLs (X T6, T11). |
| L5-3: a plain-text or Markdown representation of each route exists and is advertised | No | `Accept: text/markdown` is ignored; `.md` guesses all 404 (X T10). |
| L5-4: the publisher is a resolvable entity with a stable `@id`; a licence/terms statement is machine-discoverable | No | Only the `Report` itself carries an `@id`; `Person` and `Organization` do not. No licence file exists (X T2, T9). |
| L5-5: immutability is discoverable and explained; the lock manifest is linked from the issue data | No | `/issues/lock.json` returns 200 (coordinator correction note) but is not linked from the issue JSON or the HTML; only a prose freeze statement exists on the page (X T8). |
| L5-6: a crawler policy is stated deliberately | No | `robots.txt` is a blanket `Allow: /` for `User-agent: *` with no named-crawler rules (X T9) — reads as a default, not a decision. |
| L5-7: no empty headings, no duplicate ids on any route | Yes | Confirmed 0 empty headings, 0 duplicate ids across all three routes (X T12, M§7). |

Raise by one: link the three working JSON files from the HTML and the sitemap — cheap, and alone
would flip L3-2.

### D9 — Performance — score 2 (weight 5, tests unchanged)

Lab medians of three Lighthouse runs, one VM location, not field data (M§1).

| Test | Result | Evidence |
|---|---|---|
| L3-1: mobile lab LCP ≤ 2.5s | No | 4,356ms median (M§1). |
| L3-2: CLS ≤ 0.1 at both profiles | Yes | 0 (mobile) and 0.00056 (desktop). |
| L3-3: mobile lab TBT ≤ 300ms | Yes | 45ms. |
| L3-4: desktop lab LCP ≤ 1.5s | Yes | 859ms. |
| L5-1: mobile lab LCP ≤ 1.8s and TBT ≤ 150ms | No | LCP fails outright (4,356ms); TBT alone passes. |
| L5-2: total transfer ≤ 500KB and JS ≤ 200KB compressed | No | Total 371,455 bytes passes; JS is 229,021 bytes, over the 200KB cap. |
| L5-3: HTML document ≤ 100KB compressed | Yes | 24,823 bytes. |
| L5-4: no render-blocking third-party request | Yes | No third-party script/stylesheet loads found (M§1). |

Raise by one: none needed to reach 3 — all four level-3 tests must pass; the mobile LCP gap (4.4s
against the 2.5s bar) is the only one failing, and the LCP element is the h1 itself, so first paint
is the lever.

### D10 — Accessibility — score 4 (weight 7, tests unchanged)

| Test | Result | Evidence |
|---|---|---|
| L3-1: zero critical/serious axe violations on `/`, `/issues/`, the newest issue, both widths | Yes | 0 violations of any impact across all six page/width combinations (M§2). |
| L3-2: every interactive element keyboard-reachable with visible focus; focus never hidden under sticky content | Yes | 80 of 80 focus stops show a visible focus indicator; no sticky/fixed header found to hide any stop (M§3). |
| L3-3: no text fails 4.5:1 contrast, including small metadata | Yes | 0 of 1,219 sub-14px text nodes fail 4.5:1 (M§6). |
| L3-4: page reflows at 320px with no horizontal scroll | Yes | `scrollWidth` equals viewport width at 320×640; no page-level horizontal scroll (M§5). |
| L3-5: no empty headings; heading levels do not skip | Yes | 108 headings, 0 empty, 0 level skips (M§7). |
| L5-1: zero axe violations of any impact, three routes, both widths | Yes | Same measurement as L3-1, all impact levels (M§2). |
| L5-2: every pointer target ≥ 24×24 CSS px or a listed exception | Yes | 0 of 239 eligible targets under 24×24px; smallest is 57.5×44px (M§4). |
| L5-3: a skip link is the first focus stop, and the signed judgment is reachable within 15 Tab presses | No | Skip link is stop 1 (M§3), but nothing in the signed-judgment region is itself focusable — keyboard focus jumps from stop 33 (y=5,002) to stop 34 (y=5,558), passing over the signature at y=5,137 entirely (M§3). |
| L5-4: every chart has a text or table alternative reachable without a pointer | Yes | A "View data table (accessible alternative)" disclosure exists and is keyboard-reachable (T). |
| L5-5: landmarks and `time` elements with `datetime` used throughout | Yes | One `<main>` per page, correctly nested `<section>`/`<article>` landmarks, 92 `<time dateTime>` elements on the home page (X T12). |
| L5-6: non-text contrast meets 3:1, measured by sampling computed colours | No | No such sampling exists anywhere in `measurements.md`; per the rubric's own wording, this test fails as "not measured" until that sample exists. |

Raise by one: none needed to reach 5 — two level-5 tests fail; the cheaper of the two is making the
signed-judgment region itself keyboard-focusable so it lands within 15 Tab presses.

### D11 — Follow and share — score 0 (weight 3)

Matches the 0 anchor directly: no way to follow the site is visible anywhere.

| Test | Result | Evidence |
|---|---|---|
| L3-1: a way to follow the site is visible on the front page without expanding, at both widths | No | T: a body-text grep for "subscribe", "newsletter", "rss", "email...sign" matches nothing; the only feed reference is the invisible `<link rel="alternate">` in `<head>` (X T1). |
| L3-2: the follow prompt says what the reader will get and how often | No | No prompt exists to describe. |
| L3-3: the prompt appears at a moment of value, not only in a footer | No | No prompt exists anywhere on the page. |
| L5-1: whatever capture path the owner has authorized works end to end and has been tested | No | No capture path exists; public email capture is held by governance until 2026-10-08 per the rubric's own dimension note. |
| L5-2: every route has its own title, description and social card, so a forwarded link previews correctly | Not scored | The three routes carry distinct JSON-LD types (`Report`, `Article`, `CollectionPage`, X T1) and the home page has a full Open Graph/Twitter card set, but no measurement in the evidence set confirms whether `/issues/` and the issue permalink each carry their own distinct social-card image and description. |
| L5-3: a way to reach the author with a request or correction, visible without expanding | Yes | "Send a correction or a question" button plus "Jesse Pike · jesse@keatingpike.com," both in the open footer, not behind any disclosure (tile 08). |
| L5-4: nothing on the site implies a paid offer while none exists | Yes | No pricing or paid-offer language found anywhere in the captured content. |

Raise by one: not possible — the score is set by the 0 anchor regardless of level-5 credit; the
cheapest way to leave 0 is turning the existing RSS `<link>` into a visible on-page link, which
alone would clear L3-1.

### D12 — Trust and authority — score 2 (weight 5, tests unchanged)

Misstated-freshness cap: triggered. The closed Method section's "Not a weekly news cycle" contradicts the weekly-numbered issue framing shown elsewhere on the site (T). This does not change the score, since the natural score is already 2.

| Test | Result | Evidence |
|---|---|---|
| L3-1: a named person signs the judgment, with a date, visibly | Yes | "Signed by Jesse Pike · 19 Sep 2026," visible without expanding (tile 02). |
| L3-2: the method is visible after at most one click and says how evidence becomes a call | No | Nav "Method" scrolls to a closed `<details>`; the content itself needs a second click (independent-scores.md, D12). |
| L3-3: the site says what it will not call and why | Yes | "We will not call," visible without expanding (tile 03). |
| L3-4: who the author is, in one or two lines beyond a name and address, visible after at most one click | No | The footer shows only "Jesse Pike · jesse@keatingpike.com" — a bare signature, no bio anywhere (tile 08). |
| L5-1: a corrections record with a stable address exists | No | "There is no form and no list" (tile 08) — states the opposite of a record. |
| L5-2: the record of past calls is public and complete, including any that aged badly | Yes | Under honesty-at-small-scale: the one call's public record is on `/issues/` (issues-full); nothing is hidden. |
| L5-3: the site states that published issues are immutable and links the proof | No | Only a prose freeze statement ("Frozen from SEC-MARKET-SIG-002 v0.2...", tile 08); no "immutable" wording and no linked manifest, even though `/issues/lock.json` exists unlinked (X T8, T1 correction). |
| L5-4: the boundary statements are present and findable: public information only, not investment advice, a machine drafts and a named person signs | No | "Public sources only. Not investment advice." is present (tile 08), but no statement anywhere says a machine drafts and a named person signs — the test requires all three. |

Raise by one: none needed to reach 3 without a second level-3 pass — the cheapest is a one- or
two-line author bio reachable in one click.

### D13 — Craft — score 2 (weight 3, tests unchanged)

| Test | Result | Evidence |
|---|---|---|
| L3-1: one sans family, at most one monospace, a type scale of six sizes or fewer | No | Two sans families (`Archivo`, `IBM Plex Sans`) plus one monospace, and more than seventeen distinct font-size values in the stylesheet (SB1 D13, live stylesheet). |
| L3-2: one accent colour on a neutral scale, light theme only, colour carries meaning | No | Three semantic hues in use (`--color-accent` teal, `--color-alert` pink, `--color-warning` olive) plus three dark panels on an otherwise light site (SB1 D13; tiles 02, 03, 08). |
| L3-3: spacing follows a consistent scale; nothing collides, clips, or overflows at 1440, 390, or 320 | Yes | No collisions observed across any tile; reflow at 320px shows no horizontal scroll (M§5). |
| L3-4: no decoration that carries no information | Yes | Icons on evidence buttons and posture cards read as functional (document icon = source link, direction glyph = posture trend), not decorative. |
| L5-1: removing the accent colour would not break comprehension, checked on a greyscale capture | Not scored | No greyscale rendering exists anywhere in the evidence set. |
| L5-2: every repeated pattern is identical everywhere it appears | Yes | Source chips, date stamps, and posture/verdict badges use one consistent style across every tile (00 through 08). |
| L5-3: the page reads as one instrument next to Linear, Zed, and Radar reference captures | Not scored | Reference captures exist under `evidence/reference/` (e.g. `radar-home-1440-full.png`), but no side-by-side comparative judgment against this site was recorded in this evidence set. |

Raise by one: none needed to reach 3 without a second level-3 pass — the cheapest is collapsing to
one accent colour and cutting the type scale to six sizes or fewer.

## Tests I found ambiguous

**D2 L3-4, attribution of the domain-posture judgments.** The site's top-bar legend defines
"JUDGED" sitewide as "signed and dated by a person." Each domain card carries only "JUDGED 16 AUG
2026," with no name repeated at that instance. I read the test literally — "every past judgment
shown is dated and attributed... signed by a named person, or marked as an unsigned record" — as
requiring the attribution at the instance itself, not by reference to a legend printed once,
elsewhere on the page. I scored it No. A scorer who treats the sitewide legend as satisfying
attribution for every "JUDGED" instance would score it Yes, which would raise D2 to 4/4 level-3
tests passing and lift the dimension from 2 to 3 (a 2.0-point swing in the composite).

**D2 L3-1, "what changed since the last update."** The open "WHAT CHANGED" list under "The read"
describes market developments within the current window (Cisco's orders, the Fortinet/Zscaler
split, the Rubrik/Varonis acceleration, the Palo Alto/F5 AI deals) rather than an explicit diff
against the prior issue or edition, which instead sits inside the closed "What moved: edition
delta" disclosure. I read the visible list as satisfying "what changed," since it is genuinely new,
dated content presented without expansion. A stricter reading — that "since the last update" means
specifically the delta from the prior published state, which is the closed section — would fail
this test instead.

**D2 L5-4, "at a stable address."** This test, unlike D12's parallel test, carries no "at most one
click" qualifier. I read a closed `<details>` element as still being "a stable address" (it has a
fixed anchor and is always there), so the method explanation counts even though it is not visible
by default. A scorer who imports D12's visibility standard into this test would score it No.

**D3 L3-5, "says how old it is."** I read a plain calendar date on each card (e.g., "JUN '26") as
itself satisfying "saying how old it is," since a reader can compute the age from it. A stricter
reading would require an explicit age or staleness flag (e.g., "45+ days old"), which nothing on
the site provides, and would fail this test.

**D3 L5-2 / D7, whether the front page and the permalink "differ in purpose."** The permalink omits
the standing domain and vendor landscape and is a fifth the size of the home page, which I read as
a genuine difference in purpose (current picture vs. one period's record) for D3. But the permalink
still repeats the week's headline and all four lanes verbatim from the home page, which is why I
scored D7's narrower "current-vs-archived" tests No — those ask about explicit self-identification,
which does not exist, rather than about structural content differences.

**D4 L5-1, "under a minute."** I read the one-minute bound as describing how quickly the answer can
be understood once the relevant table is in view, not how long it takes to scroll roughly eight
screens to reach it. A reading that folds scroll time into the one-minute budget would fail this
test, since the Platform Pressure table sits close to 8,000px down the page.

**D12, misstated-freshness cap.** Whether "Not a weekly news cycle" (inside a closed section)
counts as contradicting the weekly-numbered issue framing elsewhere on the open page is the same
ambiguity the v1.1 independent scorer flagged for the old rubric. I applied the cap, consistent with
the coordinator's v1.1 reading, though it does not change D12's score here either way.
