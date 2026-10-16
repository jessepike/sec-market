# Independent baseline score — securitymarketpulse.com

Scorer: independent `claude-sonnet-5`, no access to `RUN-STATE.md`, `research-synthesis.md`, or
`score-baseline.md`. Deployment: production `https://securitymarketpulse.com/`, served 2026-09-20.
Rubric: `site-rubric.md` v1.0. Given facts: one signed issue, `2026-w36`, published 2026-09-19,
week ending 2026-09-06; scoring date 2026-09-20 (1 day after publication).

## Summary

| # | Dimension | Score /5 | L3 pass | L5 pass | Cap |
|---|---|---|---|---|---|
| D1 | Thesis clarity | 1 | 1/4 | 3/4 | none |
| D2 | Thesis development | 2 | 2/4 | 1/5 | none |
| D3 | Reason to return weekly | 1 | 1/4 | 2/4 | cadence cap not triggered (issue 1 day old) |
| D4 | First-screen decision value | 2 | 2/4 | 1/4 | none |
| D5 | Evidence legibility | 2 | 3/4 | 0/4 | none |
| D6 | Density and scanability | 2 | 2/4 | 1/4 | none |
| D7 | Wayfinding | 2 | 2/4 | 1/4 | none |
| D8 | Agent legibility | 2 | 3/5 | 0/6 | none |
| D9 | Performance | 2 | 3/4 | 2/4 | none |
| D10 | Accessibility | 4 | 5/5 | 3/5 | none |
| D11 | Conversion architecture | 0 | 0/3 | 2/4 | matches 0 anchor |
| D12 | Trust and authority | 2 | 2/4 | 1/4 | freshness cap ambiguous, moot (already at 2) |
| D13 | Craft | 2 | 2/4 | 1/3 | none |

**Composite: 37.2 / 100.**

---

## D1 — Thesis clarity — Score 1 (weight 12)

L3: (1) No — thesis text absent from both first screens; `measurements.md` §8 puts it at 5.85
viewport-heights/35.1% down at 1440 (`prod-home-1440/390-viewport.png`). (2) Yes — once reached,
"Thesis — holds:" sits in a distinct labelled callout with a confidence badge, separate from the H1
(`tiles/home-1440-02.png`). (3) No — the first-screen H1 itself contains "the lag call," the exact
undecoded-jargon example the rubric names. (4) No — no line states what the site is or who signs
it; that text is JSON-LD-only, not rendered.

L5: (1) No — verdict/confidence/date not in first screen. (2) Yes — nav "Thesis" → `/#read`, an
anchored, labelled section that states/defines the thesis and links its evidence via a "Sources"
button (`home.html`); flagged below as ambiguous (a same-page anchor whose content changes weekly).
(3) Yes — "We will not call" sits directly under the callout (`tiles/home-1440-03.png`). (4) Yes —
cold-reader test done honestly: from `prod-home-1440-viewport.png` alone, my one sentence is "the
site argues infrastructure/AI-chip spending has outrun any broad cybersecurity spending boom, and
that gap is holding." That matches the real thesis ("Infrastructure is running ahead. Security is
splitting, not booming.") in substance, because "the infra-to-security lag call holds" is on screen.

Raise by one: put the standing-thesis sentence itself, not just this week's headline, on both
first screens.

## D2 — Thesis development — Score 2 (weight 12)

L3: (1) No — "Holds in 1 of 1 issues..." is a bare `<p>`, no `<a>` (`home.html`). (2) No — "what
changed" sits only inside the closed `<details id="moved-depth">`. (3) Yes — "What would change the
call" is visible without expanding (`tiles/home-1440-03.png`). (4) Yes — the one state shown is
dated and signed ("Signed by Jesse Pike · 19 Sep 2026", `tiles/home-1440-02.png`).

L5: (1) No — no status/date per change condition. (2) Yes, under honesty-at-small-scale — the one
dated, signed state is shown on `/issues/` (`prod-issues-1440-full.png`). (3) No — the corrections
section says outright "There is no form and no list" — the opposite of a record. (4) No — Method
explains signal categories, never what the verdict labels mean or how the score is computed. (5)
No — no calibration view, no statement of when one becomes possible.

Raise by one: link "Holds in 1 of 1 issues" to the issue that set it; open "What moved" by default.

## D3 — Reason to return weekly — Score 1 (weight 10)

Cadence cap: issue published 2026-09-19, scored 2026-09-20 — 1 day, inside 14. **Not triggered.**

L3: (1) Yes — "ISSUE 2026-W36 · WEEK ENDING 6 SEP 2026 · PUBLISHED 19 SEP 2026" on first screen at
both widths. (2) No — no visible cadence sentence exists outside the closed Method disclosure, and
that hidden sentence ("Not a weekly news cycle") itself contradicts the weekly-looking "w36"
framing. (3) No — "what's new" sits only in the closed "What moved" disclosure. (4) No — grep of
`home.html` `<body>` finds no "feed.xml", "rss", or "subscribe" text; the feed is an invisible
`<link>` in `<head>` only.

L5: (1) No — no next-issue-expected date. (2) No — `07-site-teardown.md` confirms the home page and
issue permalink are byte-identical, not differentiated in purpose. (3) Yes — the real publish date
is shown prominently. (4) Yes, under honesty-at-small-scale — the one issue that exists is shown.

Raise by one: state a real cadence (or explicitly "no fixed cadence") outside any disclosure.

## D4 — First-screen decision value — Score 2 (weight 12)

L3: (1) Yes — the first-screen H1 is a judgment call, not a raw item (`prod-home-1440-viewport.png`).
(2) No — "what changed"/"do-avoid" sit at 5.20 viewport-heights (`measurements.md` §8), past two
screens. (3) No — `07-site-teardown.md`: a $2.5M raise and NVIDIA's $96.2B print carry identical
visual weight. (4) Yes — at 390px, chrome is roughly the top 190 of 844px (under a quarter), same
content order as desktop (`prod-home-390-viewport.png`).

L5: (1) No — essential content extends past the 5,000px cap on a 15,022px-tall page. (2) No —
judgment sits at y=5,137, past the 1,800px ceiling. (3) No — no decision-horizon or audience
statement in visible text. (4) Yes — nothing on the first screen reads as pure decoration.

Raise by one: move "what changed"/"do-avoid" ahead of the four evidence lanes.

## D5 — Evidence legibility — Score 2 (weight 8)

L3: (1) No — each source control is a `<button aria-label="View evidence: ...">` with no `href`;
evidence data lives only in the JS bundle (`home.html`; `machine-extraction.md` T6). (2) Yes — the
thesis callout has a "Sources" button, one interaction (`tiles/home-1440-03.png`). (3) Yes — a
"TRACKED"/"JUDGED" legend and a repeated tracked/judged table-column split make the two visually
distinct (`prod-home-1440-viewport.png`; `tiles/home-1440-04.png`). (4) Yes — every card shows a
`<time dateTime>` event date.

L5: (1) Not determinable — evidence kind (`sourceClass`) exists in JSON but no capture of an opened
evidence modal exists to confirm it's shown to a reader; scored fail. (2) Not determinable, same
reason; scored fail. (3) No — no conflicting-evidence content found next to the thesis. (4) No —
correction path is one global mailto in the footer, not attached to each evidence item.

Raise by one: make evidence controls real `<a href>` links.

## D6 — Density and scanability — Score 2 (weight 8)

L3: (1) No — the rubric's own D6 weight rationale states current lanes show "about three items a
screen" (`site-rubric.md` §3), well under the required 8/1440-screen; `tiles/home-1440-00.png`
confirms roughly 2 cards per 900px scrolled. (2) No — `07-site-teardown.md`: a $2.5M raise and a
$96.2B print use the identical template, no size cue. (3) Yes — `.issue-lane__meta` (dates) uses
`font-family: var(--font-mono)` at 0.75rem, distinct from `.issue-lane__why` prose at 0.9rem sans
(`style.css`). (4) Yes — `.issue-lane__why{font-size:.9rem}` = 14.4px ≥14px; `--prose-max:68ch` is
inside 50–80 (`style.css`).

L5: (1) No — document is 15,022px (1440) / 17,715px (390), both over the 6,000/9,000px caps. (2)
No — the "This period" scorecard shows dozens of vendors as cards, not a table
(`tiles/home-1440-05/06.png`), though the separate "Who is holding..." section is a real table. (3)
Yes — shortest continuous prose (14.4px) clears 13px; the 12px text is a short date stamp, not
continuous prose. (4) No — the Formation lane alone spans roughly two screens at 1440.

Raise by one: give the highest-consequence items in each lane a visible size or weight cue.

## D7 — Wayfinding — Score 2 (weight 5)

L3: (1) Yes — `/issues/2026-w36/` is permanent, and `/issues/` lists it with date and read
(`prod-issues-1440-full.png`). (2) No — `07-site-teardown.md`: home page and permalink are
pixel-identical, nothing marks either as current/archived. (3) Yes — in-page nav anchors work at
both widths, confirmed keyboard-reachable via the "Menu" toggle (`home.html`; `measurements.md`
§3). (4) No — 0 of 23 `<li class="issue-lane__item">` elements carry an `id` (grep of `home.html`).

L5: (1) No — no "previous/next issue" text on the issue permalink (`issue.html`). (2) No — no link
between the thesis section and the issue that set it. (3) Yes — a filter UI ("Search organization,
excerpt, or tag…", "Source class") exists inside the evidence library, discoverable by expanding it
(`home.html`). (4) No — no documented keyboard shortcuts anywhere.

Raise by one: give every lane item and issue row a linkable `id`.

## D8 — Agent legibility — Score 2 (weight 10)

Method: `machine-extraction.md` (cold, home URL only, curl, no rendering), cross-checked with curl
this session.

L3: (1) Yes — all content is prerendered HTML; extracted via curl alone (`machine-extraction.md`
T1/T3). (2) No — `/issues/2026-w36.json` and `/issues/index.json` both return 200 but only by
guessing; sitemap lists just the three HTML URLs; coordinator note: "nothing on the site links to
any of them" (`sitemap.xml`, curl this session). (3) Yes — the guessed JSON's evidence records
carry `canonicalUrl`, `sourceClass`, `retrievedAt` (`machine-extraction.md` T6/T11). (4) No — the
`/issues/` `CollectionPage` JSON-LD has no `author` and no date fields, so not every route
identifies both (curl this session vs. `home.html`/`issue.html`, which do). (5) Yes — RSS
autodiscovery `<link>` exists.

L5: all 6 No — (1) verdict/confidence/signer require the undiscoverable guessed JSON
(`machine-extraction.md` T3/T4); (2) 0 external links on the issue page, no citable anchor id
(T6); (3) `Accept: text/markdown` ignored, `.md` guesses 404 (T10); (4) no `@id` on Person/
Organization, no licence file (T2/T9); (5) only a prose freeze statement, no linked manifest (T8);
(6) `robots.txt` is a default `Allow: /` with no named-crawler rules — reads as default, not a
deliberate stance, even though headings/ids are clean (double-barrelled, flagged below).

Raise by one: link the per-issue JSON from the HTML so it's discoverable without guessing.

## D9 — Performance — Score 2 (weight 5)

L3: (1) No — mobile lab LCP 4,356ms, over 2,500ms. (2) Yes — CLS 0/0.00056, both ≤0.1. (3) Yes —
mobile TBT 45ms ≤300ms. (4) Yes — desktop LCP 859ms ≤1,500ms. (all `measurements.md` §1.)

L5: (1) No — mobile LCP fails the 1,800ms bar outright. (2) No — total transfer 371,455B (≤500KB,
passes) but JS is 229,021B, over the 200KB cap; test requires both. (3) Yes — HTML transfer
24,823B, under 100KB. (4) Yes — no third-party script/stylesheet loads; Google Fonts `preconnect`
tags are unused (`home.html`; `style.css` has no `@import` or font URL).

Raise by one: close the mobile LCP gap (4.4s vs. 2.5s bar); LCP element is the H1
(`measurements.md` §1).

## D10 — Accessibility — Score 4 (weight 7)

L3, all 5 Yes: 0 critical/serious axe violations across all routes/widths; 80/80 keyboard stops
show visible focus, no sticky-header hiding; 0 of 1,219 sub-14px nodes fail 4.5:1; reflow at 320px
has no page-level horizontal scroll; 0 empty headings, 0 level skips (`measurements.md` §§2,3,5,6,7
— §7 supersedes `07-site-teardown.md`'s "empty H2" claim per its own coordinator note).

L5: (1) Yes — 0 axe violations at any impact level, all 6 combinations (`measurements.md` §2). (2)
Yes — smallest target 57.5×44px, 0 of 239 under 24×24px (`measurements.md` §4). (3) No — skip link
is stop 1, but the signed judgment isn't reachable within 15 Tab presses; it lands between presses
33–34 (`measurements.md` §3). (4) Not determinable/fail — a text/table chart alternative exists and
is keyboard-reachable, but non-text contrast (SC 1.4.11) wasn't separately measured (flagged
below). (5) Yes — 92 `<time dateTime>` elements, consistent landmark use throughout
(`machine-extraction.md` T12).

Raise by one: get the signed judgment reachable within 15 Tab presses (needs test 3 alone; test 4
also unresolved).

## D11 — Conversion architecture — Score 0 (weight 3)

Matches the 0 anchor directly: no visible way to follow the site exists anywhere. RSS is an
invisible `<link rel="alternate">` in `<head>` only; grep of `<body>` for "feed.xml"/"rss"/
"subscribe"/"newsletter" returns nothing (`home.html`).

L3, all 3 No: no visible follow control at either width; no follow prompt exists to describe
frequency; no prompt exists at any point on the page.

L5: (1) No — no capture path to test end to end. (2) No — no "what's free and stays free"
statement found. (3) Yes — no paid offer exists and nothing implies one. (4) Yes, vacuously —
governance (SEC-029) hasn't approved an org contact path, and none is shown.

Raise by one: make the existing RSS `<link>` a visible on-page link — that alone clears test 1.

## D12 — Trust and authority — Score 2 (weight 5)

Misstated-freshness cap: the only cadence statement ("Not a weekly news cycle," inside the closed
Method section) is accurate, not misstated, and the weekly-looking issue numbering isn't
contradicted by any historical record (one issue exists). **Not clearly triggered**; moot since the
natural score is already 2. Flagged below as an ambiguity.

L3: (1) Yes — "Signed by Jesse Pike · 19 Sep 2026" is visible outside any disclosure
(`tiles/home-1440-02.png`). (2) No — nav "Method" lands on a still-closed `<details id="method">`;
a second click reveals the content (`home.html`). (3) Yes — "We will not call" is visible without
expanding. (4) No — no one/two-line author bio anywhere; "Jesse Pike" is a bare signature name.

L5: (1) No — corrections section states "There is no form and no list." (2) Yes, under
honesty-at-small-scale — the one call's public record is on `/issues/`. (3) No — only a prose
freeze statement, no "immutable" wording or linked proof. (4) No — "Public sources only" and "Not
investment advice" both present, but no "a machine drafts and a named person signs" statement; the
test requires all three.

Raise by one: add a one/two-line author bio reachable in one click.

## D13 — Craft — Score 2 (weight 3)

L3: (1) No — two sans families in use (`--font-display:"Archivo"`, `--font-sans:"IBM Plex Sans"`)
plus one monospace, and 17+ distinct `font-size` values in `style.css`, well over six. (2) No —
three distinct accent hues used semantically: `--color-accent:#0b6b5e` (teal-green),
`--color-alert:#8e2f5e` (pink), `--color-warning:#6b5c28` (olive) (`style.css`). (3) Yes — no
clipping/collision observed; reflow at 320px has no horizontal scroll (`measurements.md` §5). (4)
Yes — icons on evidence buttons/posture arrows read as functional, not decorative.

L5: (1) Not determinable — no greyscale rendering exists in the evidence set; scored fail. (2) Yes
— evidence chips, date stamps, and verdict badges look identical everywhere across the tiles. (3)
Not determinable — the Linear/Zed/Radar reference captures needed for this comparison aren't in the
evidence set; scored fail.

Raise by one: collapse to one accent colour and cut the type scale to six sizes or fewer.

---

## Composite arithmetic

Composite = Σ (score ÷ 5 × weight)

D1 1/5×12=2.4 · D2 2/5×12=4.8 · D3 1/5×10=2.0 · D4 2/5×12=4.8 · D5 2/5×8=3.2 · D6 2/5×8=3.2 ·
D7 2/5×5=2.0 · D8 2/5×10=4.0 · D9 2/5×5=2.0 · D10 4/5×7=5.6 · D11 0/5×3=0.0 · D12 2/5×5=2.0 ·
D13 2/5×3=1.2

Weight check: 12+12+10+12+8+8+5+10+5+7+3+5+3 = 100.

Sum: 2.4+4.8+2.0+4.8+3.2+3.2+2.0+4.0+2.0+5.6+0.0+2.0+1.2 = **37.2**

**Composite: 37.2 / 100.**

---

## Rubric wording problems

1. **D1's 0 anchor overlaps level-3 test 1.** The anchor ("thesis not reached without scrolling
   more than three screens") is nearly the negation of test 1, but the site passes test 2 (labelled,
   distinct callout once reached). Unclear whether a literal anchor match should override the
   test-count table when one test still passes. I used the test-count table (score 1); a literal
   anchor reading gives 0. Fix: state that the 0 anchor applies only when zero level-3 tests pass.

2. **"Working link" is undefined against a JS-modal `<button>`.** D5 test 1 doesn't say whether a
   `<button>` that opens a source in a JS modal counts as "a working link." I read "link" literally
   (needs an `href`) and failed it; a looser reading passes it. Fix: define "link" once in section 2.

3. **"Reachable in one interaction" doesn't say whether landing on a closed `<details>` counts as
   reached.** D12 test 2's "Method" nav link scrolls to a closed summary; the content itself needs
   a second click. I scored this as failing. Fix: say "visible after at most one click," not
   "reachable in one interaction."

4. **D8 level-5 test 6 is double-barrelled** — "crawler policy stated deliberately" and "no empty
   headings or duplicate ids" are unrelated claims joined by "and." The site passes one half, fails
   the other. I failed the compound test. Fix: split into two tests.

5. **D10 level-5 test 4 is double-barrelled** ("text/table alternative... and non-text contrast
   meets 3:1"), and its second half has no corresponding measurement anywhere in the evidence set —
   there is no way to answer it with the tools this instrument specifies. Fix: split it, and if
   non-text contrast should be scored, name a measurement method for it in `measurements.md`.

6. **The misstated-freshness cap doesn't say whether one page's own text can contradict another
   part of the same page, or only whether a claim is disproven by outside fact.** The site's weekly
   issue-numbering implies a cadence that its own (hidden) Method text disclaims. Both readings of
   the cap are defensible and produce different answers about whether it fires. Fix: state which
   kind of contradiction triggers it.

7. **The "honesty at small scale" note sits inside D2's text but reads as a general rule.** I
   applied it by analogy to a D12 level-5 test and a D7 level-3 test, but the rubric doesn't say
   whether its scope is D2 alone. Fix: move it to section 2 (general scoring rules).

8. **D7 test 2's "past issue says it is not the newest" cannot be exercised with one issue** —
   the newest and only issue are the same object, so there is no way to observe self-identification
   as archived. I scored it failing (no such indicator exists, and the permalink and front page are
   indistinguishable per the teardown), but honesty-at-small-scale could instead treat it as
   unscored. Fix: say whether that exception extends to wayfinding tests or is limited to D2.

9. **D4 test 4's "quarter of the viewport height" at 390px has no corresponding DOM measurement**
   in `measurements.md`, unlike every other pixel-based test in this rubric. I estimated it visually
   from the capture. Fix: add chrome-height-at-390 to the measurement set.
