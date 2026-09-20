# Baseline score — production, 2026-09-20

**Instrument:** `docs/active/fable-run/site-rubric.md` v1.1
**Deployment scored:** production, https://securitymarketpulse.com, serving `main` at `aa04875`
**Scoring date:** 2026-09-20
**Scorers:** the run coordinator, and an independent `claude-sonnet-5` scorer working blind from
the same evidence (`evidence/baseline/independent-scores.md`)

## Which site was scored, and why

Production was scored, as the owner asked. At the start of the run `main` was one commit behind
`preview`, and that commit touched only documentation. The teardown confirmed the two deployments
render identically: every capture matched byte for byte, and the only difference in the HTML is
one invisible Vercel feedback script on preview. So this baseline is also the baseline for the
`preview` trunk as it stood at `a482fda`.

## What this number is not

**Composite: 33.0 out of 100. Exposure denominator: 1.** This composite measures the site as a
reading surface. It does not measure whether the intelligence is useful. The outcome instrument,
[`docs/active/project-scorecard.md`](../project-scorecard.md), records that one person has had a
real chance to use this work and that no decision is recorded as changed. Nothing below alters
that, and a higher number after the redesign will not alter it either.

## Result

| # | Dimension | Weight | Coordinator | Independent | Reconciled (v1.1) | Points |
|---|---|---|---|---|---|---|
| D1 | Thesis clarity | 12 | 0 | 1 | **0** | 0.0 |
| D2 | Thesis development | 12 | 2 | 2 | **2** | 4.8 |
| D3 | Reason to return weekly | 10 | 1 | 1 | **1** | 2.0 |
| D4 | First-screen decision value | 12 | 1 | 2 | **1** | 2.4 |
| D5 | Evidence legibility | 8 | 3 | 2 | **3** | 4.8 |
| D6 | Density and scanability | 8 | 1 | 2 | **2** | 3.2 |
| D7 | Wayfinding | 5 | 1 | 2 | **1** | 1.0 |
| D8 | Agent legibility | 10 | 2 | 2 | **2** | 4.0 |
| D9 | Performance | 5 | 2 | 2 | **2** | 2.0 |
| D10 | Accessibility | 7 | 4 | 4 | **4** | 5.6 |
| D11 | Conversion architecture | 3 | 0 | 0 | **0** | 0.0 |
| D12 | Trust and authority | 5 | 2 | 2 | **2** | 2.0 |
| D13 | Craft | 3 | 2 | 2 | **2** | 1.2 |
| | **Composite** | 100 | 31.4 | 37.2 | | **33.0** |

**Agreement.** The two scorers matched on eight dimensions and differed by one point on five. No
dimension differed by more than one, which meets the brief's requirement at rubric v1.0. Each
difference traced to one test read two ways; those tests were reworded in v1.1 and the reconciled
column applies the reworded tests to the same evidence. Where the independent scorer had better
evidence than the coordinator (D6: it read the live stylesheet), its answer was adopted. Where a
new measurement settled the matter (D4, D5: task T2-4), the measurement decided.

**The shape of the result.** The site is strong where engineering discipline shows (accessibility
4, evidence 3) and weak exactly where the brief is aimed: the thesis is not on the first screen
(D1 at 0), the first screen carries almost no decision value (D4 at 1), there is little reason to
come back (D3 at 1) and no visible way to follow at all (D11 at 0). The four dimensions the brief
cares most about (D1, D2, D3, D4) hold 46 of the 100 points and currently earn 9.2 of them.

## Evidence files

| Short name | Path under `docs/active/fable-run/` |
|---|---|
| M | `evidence/baseline/measurements.md` (section numbers cited as M§n) |
| X | `evidence/baseline/machine-extraction.md`, with the coordinator's correction note |
| T | `research/07-site-teardown.md` |
| I | `evidence/baseline/independent-scores.md` |
| E | `evidence/baseline/evidence-drawer.md` and `evidence/baseline/drawer/*.png` |
| V1440, V390 | `evidence/baseline/prod-home-1440-viewport.png`, `prod-home-390-viewport.png` |
| tiles 00 to 08 | `evidence/baseline/tiles/home-1440-0n.png`, the desktop front page in 1,800 px slices |
| A | `evidence/baseline/prod-issues-1440-full.png`, the archive page |

Two claims in the teardown are superseded and must not be reused: that four `h2` elements are
empty (M§7 shows none are), and that the home page and the issue permalink are pixel-identical
(true of the first viewport only; the permalink is 31 KB of HTML against 216 KB for home, X T12).

## Per-dimension record

### D1 — Thesis clarity — 0

| Test | Result | Evidence |
|---|---|---|
| L3-1 thesis verbatim in first screen | No | V1440, V390: headline and funding cards only. Thesis text sits at y=5,269 of 15,022 at 1440 (5.85 screens) and y=7,455 of 17,715 at 390 (8.83 screens), M§8. |
| L3-2 distinct and labelled, in first screen | No | Not in the first screen at all. Further down it is a distinct block (tile 02 to 03), which v1.0 let one scorer count. |
| L3-3 no undecoded jargon on first screen | No | The h1 ends "the infra-to-security lag call holds" (V1440). |
| L3-4 one line saying what the site is and who signs | No | No such line rendered; the description exists only in JSON-LD (X T2). |
| L5-2 stable address for the thesis | Credit waiting | Nav "Thesis" goes to `/#read`, an anchored section (I, D1). |
| L5-3 no-call boundary near the thesis | Credit waiting | "We will not call" sits under the read (tile 03). |
| L5-4 cold reader test | Credit waiting | The independent scorer, shown only V1440, wrote a sentence matching the thesis in substance, because the headline mentions the call (I, D1). |

Raise by one: put the thesis sentence, labelled, on the first screen at both widths.

### D2 — Thesis development — 2

| Test | Result | Evidence |
|---|---|---|
| L3-1 dated verdict sequence, each linked to its issue | No | "Holds in 1 of 1 issues since 19 Sep 2026" is a plain paragraph with no link (tile 02; I, D2). |
| L3-2 "what changed since the last issue" without expanding | No | A "What changed" list is visible inside The read (tile 03) but it is undated and describes the August edition, not the step from the previous issue; the dated edition delta is inside a closed section (T). |
| L3-3 change conditions visible | Yes | "What would change the call", four conditions, open on the page (tile 03). |
| L3-4 past states dated and attributed | Yes | The one thesis state shown is signed and dated (tile 02). |
| L5-1 status per change condition | No | None shown; none recorded in the repository (`research/08`). |
| L5-2 full dated history on one surface | No | Edition records sit in a closed section; the verdict sits elsewhere. |
| L5-3 corrections record | No | The corrections block says "There is no form and no list" (tile 08). |
| L5-4 scoring method stated | No | Method covers signals, not what the four verdicts mean (I, D2). |
| L5-5 calibration view or statement | No | Absent. |

Raise by one: link the running score to the issue, and show a dated "since last issue" line in
the open.

### D3 — Reason to return weekly — 1

Cadence cap: newest issue published 2026-09-19, one day before scoring. Not applied. Note that the
issue covers the week ending 2026-09-06, so the content was thirteen days old on publication; the
cap keys on the publication date and would apply from 2026-10-04 if no further issue is signed.

| Test | Result | Evidence |
|---|---|---|
| L3-1 newest issue date and week in first screen | Yes | "ISSUE 2026-W36 · WEEK ENDING 6 SEP 2026 · PUBLISHED 19 SEP 2026" (V1440, V390). |
| L3-2 cadence stated, uncontradicted | No | No cadence sentence in the open; the closed method section says "Refresh is manual... Not a weekly news cycle" (live HTML, checked by the coordinator). |
| L3-3 what is new is identifiable | No | Nothing marks new against standing content. |
| L3-4 a visible way to be told of a new issue | No | No feed or follow link anywhere in the body; the feed is only a `link` tag in the head (coordinator grep of live HTML; I, D3). |
| L5-3 honest age at a glance | Credit waiting | Both dates are shown prominently. |

Raise by one: a visible feed link and one sentence of cadence that the rest of the site agrees with.

### D4 — First-screen decision value — 1

| Test | Result | Evidence |
|---|---|---|
| L3-1 first screen carries a statement of judgment | Yes | The h1 is this week's signed read (V1440, V390). |
| L3-2 what changed and do or avoid within two screens | No | They start about 5.2 screens down (M§8, tile 03). |
| L3-3 highest-consequence items ordered or marked | No | Lanes are chronological; a $2.6M pre-seed is the second item (V1440). |
| L3-4 phone order matches and chrome is a quarter or less | No | Chrome is 221 px of 844, 26.2 percent (E). |
| L5-2 judgment within 1,800 px | No | Signature at y=5,137 at 1440 and y=7,323 at 390 (M§8). |
| L5-4 nothing decorative on first screen | Credit waiting | I, D4. |

Raise by one: trim phone chrome under 211 px, or bring "what changed" and "do / avoid" within two
screens.

### D5 — Evidence legibility — 3

| Test | Result | Evidence |
|---|---|---|
| L3-1 source named next to each item, with a link or control | Yes | Every item has a source chip; it opens a panel with a real "Canonical source" `href` (E; `drawer/evidence-open-1440.png`). |
| L3-2 judgment shows its evidence | Yes | The thesis callout carries an evidence chip and a Sources control (tile 02, 03). |
| L3-3 tracked and judged distinguishable where both appear | Yes | Tracked and judged columns and labels in the vendor table and domain cards (tile 03, 04). |
| L3-4 event dates on items | Yes | Every card has a `time` element (X T12). |
| L5-1 evidentiary kind where the figure appears | No | Source class shows only inside the panel ("INDEPENDENT"), not beside the figure (E). |
| L5-2 publisher and date retrieved in one interaction | No | Publisher, publication date, excerpt, interpretation and limitations are shown; a retrieved date is not, although the JSON holds `retrievedAt` (E; X T11). |
| L5-3 conflicting evidence next to the judgment | No | Limitations live in the panel; nothing sits beside the judgment. |
| L5-4 correction path from the evidence | No | One global mail link at the foot of the page (tile 08). |

The evidence panel is the best-made thing on the site: excerpt, interpretation, limitations, focus
moves in and returns on Escape (E).

### D6 — Density and scanability — 2

| Test | Result | Evidence |
|---|---|---|
| L3-1 eight items per 1440 screen, four per 390 | No | Two lane items fully visible in the first desktop viewport, one on phone (M§8); about five cards per 900 px in a pure lane stretch (tile 02). |
| L3-2 consequence differs visibly | No | One card template for a $2.5M round and a $96.2B print (T). |
| L3-3 tabular figures, consistent metadata | Yes | Monospace metadata throughout; stacked figures align in the vendor table (tile 04; I, D6). |
| L3-4 body 14 px or more, prose 50 to 80 characters | Yes | `.issue-lane__why` is 0.9rem, 14.4 px; `--prose-max: 68ch` (I, D6, from the live stylesheet). |
| L5-1 page under 6,000 / 9,000 px | No | 15,022 and 17,715 px (M§8). |

Raise by one: rows in place of cards.

### D7 — Wayfinding — 1

| Test | Result | Evidence |
|---|---|---|
| L3-1 permanent URLs; archive shows date and verdict field | No | The archive row has id, week, headline, signer and date, but no verdict field (A). |
| L3-2 location indicated; past issue says so | No | The permalink carries no marker distinguishing it from the front page and no link to "newest" (T; I, D7). |
| L3-3 in-page navigation at both widths | Yes | Seven nav anchors; Menu toggle at 390 (M§3, M§4). |
| L3-4 anchors on headings and lane items | No | 0 of 23 lane items carry an `id` (I, D7). |

### D8 — Agent legibility — 2

| Test | Result | Evidence |
|---|---|---|
| L3-1 content in served HTML | Yes | X T1, T3. |
| L3-2 JSON discoverable without guessing | No | `/issues/2026-w36.json`, `/issues/index.json` and `/issues/lock.json` all return 200 (coordinator curl) and nothing links to them; the cold agent found one by guessing and never found the other two (X T1 and correction note). |
| L3-3 issue JSON carries evidence with source URLs | Yes | 23 records with `canonicalUrl`, `sourceClass`, `retrievedAt`, hash and locator (X T6, T11). |
| L3-4 JSON-LD with type, author and dates on every route | No | `CollectionPage` on `/issues/` has no author and no dates (I, D8). |
| L3-5 feed with autodiscovery | Yes | X T1. |
| L5-1 to L5-6 | No, all | Thesis only in prose; no claim anchors; `.md` and `Accept: text/markdown` return nothing; no `@id`, no licence; lock manifest unlinked; `robots.txt` is a default `Allow: /` (X T3 to T10). |
| L5-7 no empty headings, no duplicate ids | Credit waiting | X T12, M§7. |

Raise by one, cheaply: link the three JSON files from the HTML and the sitemap, and add author and
dates to the archive JSON-LD. That alone reaches 3.

### D9 — Performance — 2

| Test | Result | Evidence |
|---|---|---|
| L3-1 mobile LCP 2.5 s or less | No | 4,356 ms, median of three, simulated throttling (M§1). The LCP element is the h1; FCP is 3,857 ms, so first paint is the problem. |
| L3-2 CLS, L3-3 TBT, L3-4 desktop LCP | Yes | 0 and 0.00056; 45 ms; 859 ms (M§1). |
| L5-2 transfer 500 KB and JS 200 KB | No | 371 KB total passes; JavaScript is 229 KB (M§1). |
| L5-3 HTML 100 KB, L5-4 no blocking third party | Credit waiting | 24.8 KB compressed; no third-party requests (I, D9). |

Lab numbers from one location, not field data.

### D10 — Accessibility — 4

All five level-3 tests pass: zero axe violations of any impact on three routes at two widths;
80 of 80 focus stops visibly focused and none obscured; 0 of 1,219 small-text nodes under 4.5:1;
no page-level horizontal scroll at 320; no empty headings, no skipped levels (M§2, 3, 5, 6, 7).
Level 5: zero violations (yes), all 239 targets at least 24 by 24 (yes, smallest 57.5 by 44, M§4),
landmarks and `time` elements throughout (yes, X T12); the signed judgment is not reachable within
15 Tab presses because nothing in it takes focus, and focus passes it between stops 33 and 34
(no, M§3); chart alternative reachable (yes, a "View data table" control exists, T); non-text
contrast not measured (fails as not measured). Four of six, so 4.

### D11 — Conversion architecture — 0

No level-3 test passes: nothing visible lets a reader follow the site, at either width (coordinator
grep of live HTML; I, D11). This is scored against what governance allows today, and a visible
feed link is allowed today.

### D12 — Trust and authority — 2

Freshness cap: applies under v1.1. The closed method section says "Not a weekly news cycle" while
the first screen presents a numbered weekly issue with a week-ending date. The natural score is
also 2, so the cap changes nothing today; it will matter after the redesign if the line stays.

| Test | Result | Evidence |
|---|---|---|
| L3-1 named signature with date, visible | Yes | "Signed by Jesse Pike · 19 Sep 2026" (tile 02). |
| L3-2 method visible after at most one click | No | Nav "Method" lands on a closed section (I, D12). |
| L3-3 says what it will not call | Yes | tile 03. |
| L3-4 who the author is | No | A name and an address only (tile 08). |
| L5-4 boundary statements | No | "Public sources only" and "Not investment advice" are present; "a machine drafts, a named person signs" is not stated on the page (I, D12). |

### D13 — Craft — 2

| Test | Result | Evidence |
|---|---|---|
| L3-1 one sans, one mono, six sizes | No | Two sans families (`Archivo`, `IBM Plex Sans`) plus a mono, and more than seventeen font sizes in the stylesheet (I, D13). |
| L3-2 one accent, light only | No | Three semantic hues (teal `#0b6b5e`, pink `#8e2f5e`, olive `#6b5c28`) and three dark panels on a light site: the top bar, the thesis block, the posture block (tiles 02, 03, 08). |
| L3-3 consistent spacing, nothing collides | Yes | M§5; tiles. |
| L3-4 no empty decoration | Yes | I, D13. |

## What the baseline says about where to work

Ordered by points available for the least change:

1. **Reorder, do not rebuild.** The signed read, "what changed", "do" and "avoid", "we will not
   call", "what would change the call" and four dated domain postures already exist, well written,
   between 4,700 and 7,000 px down (tiles 02 and 03). Moving them above the lanes moves D1 and D4,
   which hold 24 points and currently earn 2.4.
2. **Link what exists.** Three working JSON surfaces, a lock manifest and a feed are unlinked. A
   visible feed link, links to the JSON, and archive JSON-LD fields lift D8, D3 and D11 together.
3. **Rows for cards.** The lanes cost roughly 4,000 px for 23 items.
4. **Give the thesis its history and its trigger status.** D2 holds 12 points and the mechanism is
   half present.
5. **Fix one sentence.** "Not a weekly news cycle" caps D12 and fails a D3 test.
6. **First paint on phones.** Mobile FCP of 3.9 s is the only engineering weakness measured.

Accessibility is the thing to protect. A denser design is exactly what breaks target size and
focus rules, and the site currently passes both without exception.
