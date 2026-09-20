# Site quality rubric — Security Market Pulse

**Artifact ID:** `SEC-MARKET-FABLE-RUBRIC` v2.1
**Written by:** the run coordinator, 2026-09-20. v2.0 re-aims the instrument at
`docs/active/product-core.md`, the owner's statement of what the site is for. v1.2 measured a site
built around one standing thesis; the owner has said that is not the centre. Git history keeps v1.2.
**Used for:** the baseline in `score-baseline.md`, every build decision in Phase 4, and the
re-score in `score-after.md`.

## 1. What this instrument measures, and what it does not

This rubric measures the **quality of the website as a reading surface**, for a person and for a
machine. It produces thirteen dimension scores from 0 to 5 and a weighted composite from 0 to 100.

It does **not** measure whether the intelligence is useful, whether anybody has seen it, or whether
any decision changed. That is the job of the outcome instrument at
[`docs/active/project-scorecard.md`](../project-scorecard.md) (`SEC-MARKET-SCORE-001`), which
deliberately refuses a composite number for outcomes, and is right to. The two instruments are
kept apart on purpose:

- A high score here says the site is a well-made instrument. It says nothing about impact. As of
  2026-09-20 the outcome scorecard records an exposure denominator of one and an empty
  decision-impact log, and no score in this document changes that.
- This rubric also does not measure the quality of the market judgment itself, or shipping
  discipline (gates, tests, commit hygiene). Those are held elsewhere.
- Wherever this composite is quoted, quote the exposure denominator next to it.

## 2. How to score

**Evidence rule.** Every score cites evidence a second person can open: a capture file, a
measurement with the command that produced it, a quoted line of markup with its URL, or a quoted
line of page text. A score without evidence is void and is recorded as "not scored", never
guessed.

**What is scored.** The named deployment, as served, on the day stated. The front page `/` at
1440 by 900 and 390 by 844 carries most of the weight; `/issues/`, the newest issue permalink and
any thesis page are scored where a test names them. "First screen" means the first viewport at
those two sizes with no scrolling. Where a test names both widths, both must pass.

**Tests and levels.** Each dimension has an anchor for 0, a list of **level-3 tests** and a list
of **level-5 tests**. Each test is written to be answered yes or no. The score follows
mechanically:

| Score | Rule |
|---|---|
| 0 | No level-3 test passes. The 0 anchor is a description of what that usually looks like, not a separate test. |
| 1 | At least one level-3 test passes, but fewer than half. |
| 2 | At least half of the level-3 tests pass, but not all. |
| 3 | All level-3 tests pass, and fewer than half of the level-5 tests pass. |
| 4 | All level-3 tests pass and at least half of the level-5 tests pass, but not all. |
| 5 | All level-3 and all level-5 tests pass. |

Half is rounded up (two of three, three of five). A scorer records the result of every test, so
two scorers who disagree can find the test they read differently. Level-5 tests passed while a
level-3 test fails do not raise the score; note them as credit waiting.

**Honesty at small scale.** This rule applies to every dimension. The site has one signed issue.
No test rewards volume. Tests about history pass when the mechanism is visible and the real
history is shown truthfully, however short. A test that cannot be exercised with one issue (for
example, a past issue identifying itself as past) is scored on whether the mechanism exists in
the page as served, and fails if it does not.

**Defined terms.** *Link or control*: for a human reader, a button that reveals a source counts
the same as a link, provided what it reveals contains a real `href` to the source; machine
citability is scored only in D8. *Visible after at most one click*: the content itself is on
screen after one click or tap; arriving at a closed section that needs a second click does not
count. *Without expanding anything*: visible in the page's state after load with no interaction
other than scrolling. *Site chrome*: everything above the first line of page content, measured by
DOM as the top offset of the first content element.

**Composite.** Composite = sum over dimensions of (score ÷ 5 × weight). Weights sum to 100.

**Fit-for-purpose blockers.** These are checked before any score is quoted. If any one fails, the
result is reported as "not fit for purpose: <which blocker>" next to the composite, however high
the composite is.

1. *Factual meaning.* No figure on the page is wrong or mislabelled as to company or segment,
   metric, period or units. Checked by sampling at least ten figures against their sources.
2. *Comparison validity.* Nothing is ranked, ordered or described as leading, accelerating or
   slowing on the strength of figures that are not like for like.
3. *Tracked and judged.* Nothing assembled by a machine is presented as the author's opinion, and
   every judgment carries a name and a date.
4. *Accessibility.* Zero critical and zero serious axe violations, and the page can be operated
   by keyboard.

**What this instrument cannot show.** Two scorers agreeing proves the rubric is consistent, not
that the site is useful. A scorer imagining a security leader is not a security leader. The check
that matters is to put the page in front of three real security leaders facing a renewal or a
supplier decision and ask what they learned, what they would ask next, and what the evidence does
not establish. That is the owner's to arrange and is recorded in the project scorecard, not here.

**Two caps.** They exist so craft cannot paper over the product's real weaknesses.

- **Cadence cap.** If the newest signed issue was published more than 14 days before the scoring
  date, D3 cannot score above 2, whatever its tests say.
- **Misstated freshness cap.** If any text on the site, including text inside a closed section,
  states a cadence or freshness that contradicts either the publishing record or another statement
  on the site, D12 cannot score above 2.

## 3. Weights

| # | Dimension | Weight | Why this weight |
|---|---|---|---|
| D1 | Market picture clarity | 10 | The product core: a security leader should see what is happening in the market they buy from. |
| D2 | Look back, look ahead | 7 | The owner's method: three to six months of evidence behind, a labelled view ahead. Holds the standing analyses, including the founding thesis. |
| D3 | Freshness and reason to return | 15 | "If it is not updated flawlessly with accurate, fresh information, it is worthless." Capped by real cadence. |
| D4 | Decision value for a security leader | 20 | Includes the owner's own use: which vendors in a domain are on solid footing. |
| D5 | Evidence legibility | 12 | Trust is the asset. Every figure traceable. |
| D6 | Density and scanability | 4 | House style. |
| D7 | Wayfinding | 3 | Domains, vendors, issues and analyses each need an address. |
| D8 | Agent legibility | 3 | Still wanted, no longer a pillar. |
| D9 | Performance | 4 | Hygiene. |
| D10 | Accessibility | 8 | WCAG 2.2 AA is a design input, and dense designs break it. |
| D11 | Follow and share | 3 | Sales teams forwarding it is a stated success signal. Public email is held until 2026-10-08. |
| D12 | Trust and authority | 10 | Named author, method, corrections, separation of fact from opinion. |
| D13 | Craft | 1 | Low on purpose, so polish cannot carry the composite. |

Changes from v1.2: D1 was "thesis clarity" and D2 "thesis development" (24 points on one analysis);
they now measure the market picture and the look back and ahead. D3 rises from 10 to 12 and gains a
per-dataset freshness test. D4 gains the owner's real use case as a test. D5 rises by one. D8 falls
from 10 to 7. D11 drops its paid-offer tests, because monetization is parked, and gains sharing.
No test anywhere rewards volume of traffic.

v2.1 weights follow the external review (`consults/external-review-astra.md`, finding 9): decision
value and trust were under-weighted, and density, agent legibility and craft were over-weighted
for a site whose purpose is to be trusted by buyers.

## 4. The dimensions

### D1 — Market picture clarity (10)

*Can a security leader say, after ten seconds, what this site is and one thing that is happening
in the market they buy from?*

**0:** The first screen does not say what the site is, and the market picture cannot be reached
without expanding a section or scrolling more than three screens.

**Level 3**
1. One plain line on the first screen, at 1440 and at 390, says what the site is, who it is
   written for and who writes it.
2. The first screen at both widths carries this period's read as a statement about the market,
   not only a list of tracked items.
3. No term on the first screen needs another page to decode it (no internal labels such as "the
   lag call", "prints", "formation", episode numbers or ids).
4. Within the first screen plus one scroll at 1440 (under 1,800 pixels), a by-domain picture is
   visible without expanding anything: each covered domain with its direction or stance in plain
   words.

**Level 5**
1. For each covered domain, the tracked suppliers are shown with sourced figures, each labelled
   with its metric and period, in a form that does not rank them on figures that are not like for
   like.
2. Consolidation and distress (acquired, taken private, shut down, debt, layoffs) have a visible
   place of their own, which says "none recorded this period" when empty.
3. Cold reader test: a scorer shown only the first-screen capture for ten seconds, asked to
   answer as a security leader, writes what the site is for and one true thing it says about the
   market.
4. Every domain and every vendor has a stable address (a page or an anchored section) that can
   be linked and forwarded.

### D2 — Look back, look ahead (7)

*Can a reader see what happened over the last three to six months, what the site expects next,
and how past expectations held up?*

**0:** Figures carry no period, nothing looks forward, and past calls cannot be found.

**Level 3**
1. "What changed since the last update" is visible without expanding anything, and says so
   plainly when nothing changed.
2. Backward view: tracked figures carry their period and date, and for a vendor or a domain a
   reader can see at least the previous period or the direction of travel, not a single point.
3. A forward view exists, is labelled as judgment and not as fact, carries its confidence, and
   says what would change it.
4. Every past judgment shown is dated and attributed (signed by a named person, or marked as an
   unsigned record).

**Level 5**
1. Standing analyses (the founding infrastructure-and-security thesis is one) each have a stable
   address with their dated record in order, distinguishing signed judgments from unsigned ones.
2. Each forward call lists its change conditions, each with a current status and a date.
3. A corrections record exists at a stable address, and says "none to date" when empty.
4. How judgments are made and scored is stated once, in plain sentences, at a stable address.
5. A calibration view compares stated confidence with outcomes, or a plain statement says when
   there will be enough history to show one.

### D3 — Freshness and reason to return (15)

*Is there something here this week that was not here last week, is that visible without hunting,
and can a reader tell how old everything is?* Subject to the cadence cap.

**0:** Nothing on the site indicates when it last changed or when it will change again.

**Level 3**
1. The date of the newest update and the period it covers are visible in the first screen.
2. The publishing cadence is stated as a sentence somewhere a reader reaches without expanding
   anything, and no other text on the site contradicts it.
3. What is new since the previous update is identifiable on the front page without comparing
   pages by memory.
4. At least one way to be told about a new update is visible without expanding anything (a feed
   link counts).
5. Dates are kept apart and shown: the period a figure covers, when its source was published, and
   when a judgment was last reviewed. A page-level "updated" date never stands in for them.

**Level 5**
1. If the promised cadence has been missed, the site says so without anyone editing it by hand.
2. The front page differs from a dated issue's permalink in purpose: the front page shows the
   current picture, the permalink is the record of one period.
3. The age of the newest update is honest at a glance: a reader cannot mistake a three-week-old
   read for this week's.
4. A returning reader can see the last three updates' headlines from the front page, or as many
   as exist.

### D4 — Decision value for a security leader (20)

*What does someone running a security program learn in five seconds, thirty seconds, three
minutes? Can the owner's own question be answered from it?*

**0:** The first screen carries no judgment: navigation, a headline and raw items only.

**Level 3**
1. Five seconds: the first screen at both widths carries a statement of judgment about the
   market (a headline that states the read counts).
2. Thirty seconds: within two screens of scrolling at 1440, a reader reaches what changed and
   what it means for someone running a program or advising one, without expanding anything.
3. The highest-consequence events of the period are ordered or marked as such; a reader is not
   left to infer importance from a chronological list.
4. At 390, the first screen carries the same things in the same order as desktop, and site
   chrome takes no more than a quarter of the viewport height, measured by DOM.

**Level 5**
1. The supplier question: starting from the front page, a reader can find, for a named supplier,
   in under a minute and from one view: what it last reported (with metric and period), what
   changed recently, the author's stance on its domain, and what is not publicly disclosed. The
   view keeps commercial momentum, continuity evidence and unknowns apart.
2. Three minutes: everything essential (the read, the by-domain picture, the period's main
   events and the forward view) sits within the first 5,000 pixels at 1440, by DOM.
3. The first screen names the reader it is written for, so a security leader knows it is for
   them.
4. Nothing on the first screen is decoration: every element is navigation, provenance, judgment
   or evidence.

### D5 — Evidence legibility (12)

*Can a claim be traced to a named source without leaving the flow of reading?*

**0:** Claims carry no sources, or sources are only listed in bulk elsewhere.

**Level 3**
1. Every tracked item on the front page names its source next to the item, with a link or
   control (see defined terms) that reaches the source.
2. Every judgment block shows the evidence it rests on, or links to it directly, within one
   interaction.
3. Tracked facts and signed judgments are visually distinguishable wherever both appear, not only
   in a legend at the top.
4. Dates of the underlying events are shown on the items.

**Level 5**
1. Figures carry their evidentiary kind where they appear (filing, company disclosure, database,
   press report, the site's own estimate).
2. A reader can get from a figure to its source record, including publisher and date retrieved,
   in one interaction, without losing their place.
3. Conflicting evidence and credible alternatives are shown next to the judgment they qualify,
   without expanding a closed section.
4. A way to report a wrong figure is reachable from the evidence itself.

### D6 — Density and scanability (4)

*Real information per screen, at the Zed standard, without becoming a wall.*

**0:** Fewer than three information items per desktop screen in list sections, or an
undifferentiated wall of text with no structure.

**Level 3**
1. List sections show at least eight items per 1440 by 900 screen and at least four per 390 by
   844 screen, counted from a capture.
2. Items that differ greatly in consequence differ visibly (size cue, amount column, ordering or
   grouping), so a small round and a major print do not look alike.
3. Numbers that stack use tabular figures and align; metadata (dates, ids, amounts) has a
   consistent treatment distinct from prose.
4. Body text is 14 pixels or larger and line length in prose blocks stays within about 50 to 80
   characters at 1440.

**Level 5**
1. The front page with everything essential visible is under 6,000 pixels tall at 1440 and under
   9,000 at 390, by DOM measurement, with no essential content hidden in a closed section.
2. Any comparison of more than three entities is a table with fixed columns, not prose or cards.
3. Row rhythm comes from spacing, not small type: no continuous reading text under 13 pixels.
4. A reader can scan one full lane (all items of one kind for the week) without scrolling at
   1440.

### D7 — Wayfinding (3)

*Archive, search, permalinks, cross-references, "where am I in this".*

**0:** One long page with no working navigation to past material.

**Level 3**
1. Every issue has a permanent URL, and the archive lists every issue with its date and with its
   verdict as a distinct labelled field (a verdict word inside a headline does not count).
2. The current location is indicated (which issue, current or past), and a past issue says it is
   not the newest and links to the newest.
3. Main sections of a long page are reachable by in-page navigation that works at both widths.
4. Every section heading and every lane item has a linkable anchor.

**Level 5**
1. Issues link to the previous and next issue.
2. Standing analyses and dated issues cross-reference each other: each verdict links to its issue
   and each issue links to the analysis it judged.
3. A reader can filter or find items across issues by vendor or domain (the vendor lens counts
   if it is discoverable from the page, not only by editing the URL).
4. Keyboard shortcuts for next and previous issue and jump to the market picture exist and are documented on
   the page.

### D8 — Agent legibility (3)

*Can a machine reader parse, cite precisely, and come back for structured data?* Scored from the
cold-agent extraction test (method in `evidence/baseline/machine-extraction.md`): a program given
only the home URL, with no rendering.

**0:** Content is not present in the served HTML, or no structured data of any kind exists.

**Level 3**
1. All content is in the prerendered HTML; the cold agent extracts the week's headline and items
   without executing scripts.
2. The archive and each issue are available as JSON, discoverable from the home page or the
   sitemap without guessing URLs.
3. Each issue's JSON carries its evidence records with source URLs.
4. Valid JSON-LD on every route identifies the page type, author and dates.
5. A feed exists and is advertised by an autodiscovery link.

**Level 5**
1. The cold agent gets the current read, its confidence, author and date, and the by-domain
   picture, from structured data (a JSON endpoint or JSON-LD), without parsing prose.
2. Each claim or lane item has a stable anchor id, so a single claim can be cited by URL, and the
   id appears in the JSON.
3. A plain-text or Markdown representation of each route exists and is advertised
   (`rel="alternate"` or equivalent).
4. The publisher is a resolvable entity (`Organization` and `Person` with stable `@id`), and a
   licence or terms statement for content and data is machine-discoverable.
5. Immutability is discoverable and explained: the lock manifest is linked from the issue data,
   and a machine-readable statement says published issues do not change.
6. A crawler policy is stated deliberately (whatever the owner decides), not left as a default.
7. The HTML has no empty headings and no duplicate ids on any route.

### D9 — Performance (4)

*Core Web Vitals on a real network, measured not assumed.* Lab medians of three Lighthouse runs on
the front page; field data replaces lab data when it exists.

**0:** Mobile LCP over 6 seconds or the page does not become usable on a throttled phone profile.

**Level 3**
1. Mobile lab LCP at or under 2.5 seconds.
2. CLS at or under 0.1 at both profiles.
3. Mobile lab TBT at or under 300 milliseconds.
4. Desktop lab LCP at or under 1.5 seconds.

**Level 5**
1. Mobile lab LCP at or under 1.8 seconds and TBT at or under 150 milliseconds.
2. Total transfer for the front page at or under 500 KB and JavaScript at or under 200 KB
   compressed.
3. The HTML document is at or under 100 KB compressed.
4. No render-blocking third-party request on the front page.

### D10 — Accessibility (8)

*WCAG 2.2 AA, verified by tooling and by keyboard.*

**0:** Critical axe violations on the front page, or the page cannot be operated by keyboard.

**Level 3**
1. Zero critical and zero serious axe violations on `/`, `/issues/` and the newest issue at both
   widths.
2. Every interactive element is reachable by keyboard and shows a visible focus indicator
   (SC 2.4.7), and focus is never hidden under sticky content (SC 2.4.11).
3. No text fails 4.5:1 contrast, including small metadata (SC 1.4.3).
4. The page reflows at 320 CSS pixels with no horizontal scroll (SC 1.4.10).
5. No empty headings; heading levels do not skip.

**Level 5**
1. Zero axe violations of any impact on the three routes at both widths.
2. Every pointer target is at least 24 by 24 CSS pixels or meets a listed exception (SC 2.5.8).
3. A skip link is the first focus stop, and the signed judgment is reachable within 15 Tab
   presses.
4. Every chart has a text or table alternative that is reachable without a pointer.
5. Landmarks and `time` elements with `datetime` are used throughout.
6. Non-text contrast meets 3:1 (SC 1.4.11), measured by sampling the computed colours of
   control borders, focus indicators and chart marks against their backgrounds; this test fails
   as "not measured" until that sample exists.

### D11 — Follow and share (3)

*Can a reader follow it, and can someone forward it to a client without embarrassment?* Scored
against what the project's governance allows on the scoring date. While public email is held
(SEC-029), "follow" means the feed and any owner-approved pilot path.

**0:** No way to follow the site is visible anywhere.

**Level 3**
1. A way to follow the site is visible on the front page without expanding anything, at both
   widths.
2. The follow prompt says what the reader will get and how often.
3. The prompt appears at a moment of value (after the read), not only in a footer.

**Level 5**
1. Whatever capture path the owner has authorized works end to end and has been tested.
2. Every route has its own title, description and social card, so a forwarded link previews as
   what it is.
3. A way to reach the author with a request or a correction is visible without expanding
   anything.
4. Nothing on the site implies a paid offer while none exists.

### D12 — Trust and authority (10)

*Named author, visible method, corrections record, calibration of past calls.* Subject to the
misstated freshness cap.

**0:** Anonymous, undated, with no method.

**Level 3**
1. A named person signs the judgment, with a date, visibly.
2. The method is visible after at most one click from the front page and says how evidence
   becomes a call.
3. The site says what it will not call and why.
4. Who the author is, in one or two lines beyond a name and an address, is visible after at most
   one click.
5. The author's professional role and the commercial relationships relevant to the coverage are
   disclosed, visible after at most one click.

**Level 5**
1. A corrections record with a stable address exists.
2. The record of past calls is public and complete, including any that aged badly.
3. The site states that published issues are immutable and links the proof.
4. How suppliers are chosen for coverage is stated, and says that partners and competitors are
   held to the same evidence standard.
5. The boundary statements are present and findable: public information only, not investment
   advice, a machine drafts and a named person signs.

### D13 — Craft (1)

*Typography, restraint, colour discipline, the feeling of a well-made instrument.*

**0:** Default styling or visibly broken layout at either width.

**Level 3**
1. One sans family and at most one monospace family; a consistent type scale of no more than six
   sizes on the front page.
2. One accent colour on a neutral scale, light theme only, and colour carries meaning wherever it
   appears.
3. Spacing follows a consistent scale; nothing collides, clips or overflows at 1440, 390 or 320.
4. No decoration that carries no information.

**Level 5**
1. Removing the accent colour would not break comprehension (checked on a greyscale capture).
2. Every repeated pattern (item row, source chip, verdict pill, date) is identical everywhere it
   appears.
3. The page reads as one instrument: a scorer comparing it side by side with the Linear, Zed and
   Radar reference captures finds no element that looks like marketing chrome.

## 5. Scoring record format

For each dimension record: the score; each test with yes or no; the evidence for each (file path,
command, or quoted line with URL); and one sentence on what would raise the score by one. Record
the deployment URL, the commit it serves, the date, and the scorer. Record caps applied.

## 6. Agreement check

The brief requires that a different agent could score the site and land within one point on every
dimension. The baseline is therefore scored twice, by the coordinator and by an independent
`claude-sonnet-5` scorer working from the same evidence without seeing the coordinator's scores.
Any dimension where the two differ by more than one point is a defect in the rubric's wording,
not in a scorer: the test that was read two ways is rewritten, the rubric version is bumped, and
the change is recorded here.

### Revision record

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-09-20 | First version, from the brief's thirteen dimensions revised against Phase 1 research. |
| 1.1 | 2026-09-20 | After the agreement check. Two scorers landed within one point on all thirteen dimensions at v1.0 (five dimensions differed by one). Every test they read differently was reworded: the 0 rule is now "no level-3 test passes" (D1's anchor overlapped its first test); D1 test 2 is tied to the first screen; D4 test 1 says a headline stating the read counts; "link or control", "visible after at most one click", "without expanding anything" and "site chrome" are defined once; D7 test 1 requires the verdict as a labelled field; D8 level-5 test 6 and D10 level-5 test 4 were each split in two; the freshness cap names which contradictions trigger it; the small-scale rule is stated as general. |
| 1.2 | 2026-09-20 | After the adversarial pass on the Phase 3 specs (`consults/adversarial-pass.md`, finding 8). D4 level-5 test 1 read "within the first 40 percent of page height or within 5,000 pixels, whichever is smaller", which no short page can pass and which pulled against D6 level-5 test 1 (a page under 6,000 pixels). It is now a flat 5,000 pixels. The baseline is unaffected: D4 fails at level 3, so no level-5 test changes its score. |
| 2.0 | 2026-09-20 | Re-aimed at `docs/active/product-core.md` after the owner restated the purpose: a practitioner's market pulse for security leaders, with the founding thesis as one standing analysis. D1 to D4 and D11 rewritten, weights changed (section 3), D8 level-5 test 1 reworded. D5 to D7, D9, D10, D12 and D13 tests unchanged. The v1.2 baseline of 33.0 is not comparable with v2.0 scores; the baseline is re-scored under v2.0 from the same evidence in `score-baseline-v2.md`. |
| 2.1 | 2026-09-20 | After the external review by Codex on `gpt-6-astra`. Weights changed toward decision value (20), freshness (15), evidence (12) and trust (10). Fit-for-purpose blockers added, so a high composite cannot hide a mislabelled figure, an unsupported comparison, machine content posing as judgment, or an accessibility failure. D1 level-5 test 1 and D4 level-5 test 1 no longer reward a ranked vendor table. D3 level-3 test 5 asks for separate dates in place of a 45-day threshold. D12 gains a disclosure test at level 3 and an inclusion-rules test at level 5. A statement of what the instrument cannot show was added. Not yet addressed from the review: double counting between D1 and D4 and between D3 and D11, and replacing D6's item counts with a scanning task. |
