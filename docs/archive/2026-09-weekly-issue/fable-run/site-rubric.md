# Site quality rubric — Security Market Pulse

**Artifact ID:** `SEC-MARKET-FABLE-RUBRIC` v3.0
**Written by:** the run coordinator, 2026-09-26. v3.0 re-aims the instrument at the product the
site now is: a standing, twelve-domain supplier tracker that publishes sourced facts only, on its
own schedule, with no human approval step and no machine judgment (`intent.md` v1.4; D-76, D-77;
`docs/archive/2026-10-refresh-gate/autonomy-coverage-plan.md`, `SEC-MARKET-AUTO-001`, step 7). Every earlier version of
this rubric scored a site organized around a signed weekly judgment, a shape the site no longer
has. Git history keeps v2.2 and earlier; scores under v2.x are not comparable with scores under
this version.
**Used for:** the next production score and every score after it, until the product changes again.

## 1. What this instrument measures, and what it does not

This rubric measures the **quality of the tracker as a reading surface**, for a person and for a
machine. It produces eleven dimension scores from 0 to 5 and a weighted composite from 0 to 100.

It does **not** measure whether the underlying facts are correct beyond the sampling this rubric
itself does, whether anybody has seen the site, or whether any decision changed because of it.
That is the job of the outcome instrument at
[`docs/archive/2026-08-web-mvp/project-scorecard.md`](../../2026-08-web-mvp/project-scorecard.md) (`SEC-MARKET-SCORE-001`), which
deliberately refuses a composite number for outcomes, and is right to. The two instruments are
kept apart on purpose:

- A high score here says the tracker is a well-made instrument. It says nothing about impact, and
  nothing about whether the twelve declared domains and the supplier list are the right ones for a
  security leader — that is a coverage-design question, tracked in
  `docs/archive/2026-10-refresh-gate/autonomy-coverage-plan.md`, not a scoring question.
- This rubric does not measure shipping discipline (gates, tests, commit hygiene) or the accuracy
  of source-selection judgment behind which facts were worth collecting. Those are held elsewhere.
- Wherever this composite is quoted, quote the date of the scoring run next to it, because a
  facts-only tracker's quality can move day to day as figures age.

## 2. How to score

**Evidence rule.** Every score cites evidence a second person can open: a capture file, a
measurement with the command that produced it, a quoted line of markup with its URL, or a quoted
line of page text. A score without evidence is void and is recorded as "not scored", never
guessed.

**What is scored.** The named deployment, as served, on the day stated. The front page `/` at
1440 by 900 and 390 by 844 carries most of the weight, because it is now the tracker itself: the
run-status line, the "what changed" list, the coverage statement, and the market-by-domain tables.
`/corrections/` is scored where a test names it (chiefly D5). `/issues/` and any issue permalink,
and `/thesis/`, are the dated archive and are scored only where a test names them by name; they
are not assumed to carry live-page rules such as the ban on judgment language, because they are
explicitly the record of what was judged before the product changed. "First screen" means the
first viewport at 1440 and 390 with no scrolling. Where a test names both widths, both must pass.

**Tests and levels.** Each dimension has an anchor for 0, a list of **level-3 tests** and a list
of **level-5 tests**. Each test is written to be answered yes or no, and each is checkable by a
scorer who has never seen this repository, from the live site and from the public sources a test
sends them to. The score follows mechanically:

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

**Honesty at small scale.** This rule applies to every dimension. Some domains will have thin
distress or consolidation history, and some private suppliers will have only one public fact (a
funding round) to show. No test rewards volume. A test about a category of fact (distress, a
prior period, a dated event) passes when the mechanism is visible and truthfully shows what is
real, however little that is, and it fails outright when the mechanism does not exist at all — a
domain with nothing to show must still say so, not omit the section.

**Defined terms.** *Link or control*: for a human reader, a button that reveals a source counts
the same as a link, provided what it reveals contains a real `href` to the source. *Visible after
at most one click*: the content itself is on screen after one click or tap; arriving at a closed
section that needs a second click does not count. *Without expanding anything*: visible in the
page's state after load with no interaction other than scrolling. *Site chrome*: everything above
the first line of page content, measured by DOM as the top offset of the first content element.
*Judgment language*: any word or sentence that states a stance, a ranking, a forecast, or an
interpretation of what a fact means for a supplier's prospects — as distinct from a computed
figure (a percentage, a median, a count), which is a fact even when it invites a comparison.

**Composite.** Composite = sum over dimensions of (score ÷ 5 × weight). Weights sum to 100.

**Fit-for-purpose blockers.** These are checked before any score is quoted. If any one fails, the
result is reported as "not fit for purpose: <which blocker>" next to the composite, however high
the composite is. They replace the earlier version's blockers, which assumed a person signed every
judgment before it published; under D-76 nobody does, so the thing that must never be wrong is the
fact itself and the honesty of the page that carries it.

1. *Mislabelled figure.* No figure on a live page is wrong or mislabelled as to company, metric,
   period, or units. Checked by sampling at least ten figures against their cited public sources.
2. *Stale beyond the line.* No shown figure is more than 14 days older, as of the scoring date,
   than a newer figure the same company has itself made public. Checked by comparing at least ten
   figures against each company's own most recent filing, release, or public statement.
3. *Judgment on a live page.* No live page (the front page, a domain table, the "what changed"
   list, the coverage statement, `/corrections/`) carries judgment language as defined above. The
   dated archive (`/issues/`, an issue permalink, `/thesis/`) is exempt from this blocker, because
   it is explicitly the record of what was judged before the product changed.
4. *A run-status line that misstates what happened.* The state the front page claims (every source
   collected, no material change, or collection incomplete) matches what actually happened on the
   scoring date, checked against the run's own log or commit history where the scorer has access
   to it, or against plain inconsistency on the page itself where they do not.
5. *Accessibility failure.* Zero critical and zero serious axe violations on `/` and
   `/corrections/` at both widths, and the page can be operated by keyboard.

**What this instrument cannot show.** Two scorers agreeing proves the rubric is consistent, not
that the tracker is useful. A scorer imagining a security leader is not a security leader. The
check that matters is to put the page in front of three real security leaders facing a renewal or
a supplier decision and ask what they learned, what they would ask next, and what the facts alone
could not tell them. That is the owner's to arrange and is recorded in the project scorecard, not
here.

**Caps.** They exist so craft cannot paper over the product's real weaknesses, at a threshold
short of the fit-for-purpose blockers above.

- **Freshness cap.** If any tracked supplier's newest shown figure is more than 30 days older than
  the newest figure that company has itself published — whether or not it also trips blocker 2 —
  D1 cannot score above 3.
- **Coverage-gap cap.** If any declared domain lists zero tracked suppliers, or the stated "not
  covered" list is silent about an obvious major sub-market that a security leader would expect
  (for example endpoint, identity, or managed security, if any of those were missing), D2 cannot
  score above 2.

## 3. Weights

| # | Dimension | Weight | Why this weight |
|---|---|---|---|
| D1 | Freshness without fail | 22 | Intent's first-priority success measure: "if this is not true, nothing else counts." |
| D2 | Coverage | 15 | Intent's second-priority measure: each declared domain lists its declared suppliers, and gaps are stated. |
| D3 | Deciding a supplier's footing from facts alone | 20 | The product's working use: a security leader compares suppliers in a domain without the site telling them what to conclude. |
| D4 | Evidence legibility and reconstructability | 13 | Intent's fourth-priority measure: another person can trace every fact to its public source. |
| D5 | Trust | 12 | No judgment language may leak onto a live page; who runs the site and how coverage is chosen are disclosure questions this facts-only product depends on. |
| D6 | Density and scanability | 4 | House style, modest weight. |
| D7 | Phone | 4 | The tracker has to work at 390 pixels, not just look acceptable there. |
| D8 | Accessibility | 4 | WCAG 2.2 AA; also gated as a fit-for-purpose blocker regardless of this weight. |
| D9 | Performance | 3 | Hygiene. |
| D10 | Machine legibility | 2 | Still wanted, no longer a pillar of a facts-only product built for human decision-making first. |
| D11 | Craft | 1 | Low on purpose, so polish cannot carry the composite. |

Weights sum to 100.

Changes from v2.2: the four dimensions that scored a signed weekly judgment (market picture
clarity, look back/look ahead, decision value for a security leader, wayfinding, follow and share)
are retired or folded into the dimensions above — decision value survives as D3, re-aimed at
comparing facts rather than reading a stance; wayfinding's stable-address tests move into D2 and
D3; follow-and-share is dropped because measuring return visits and sharing is explicitly the
outcome scorecard's job, not this instrument's (see Section 1). Freshness rises from a shared
weight inside D3 to its own dimension at 22, first in the order, matching intent's stated
priority. Trust and evidence keep meaningful weight; density, accessibility, performance, and
craft move to modest weight as instructed, and a new Phone dimension is added because a fact
comparison that only works at desktop width fails the product's own reader.

## 4. The dimensions

### D1 — Freshness without fail (22)

*Is every figure current against what the companies themselves have published, does the
run-status line tell the truth, and is the newest tracked fact days old rather than weeks?*
Subject to the freshness cap.

**0:** No statement of run status appears anywhere on the front page, and no date is shown near
any tracked figure.

**Level 3**
1. The front page states, without expanding anything, one of three things: every declared source
   was collected this run, the run completed with no material change found, or collection is
   incomplete and names which sources failed.
2. The date collection was last checked is visible on the first screen, at both 1440 and 390.
3. Sampling ten tracked figures at random against each company's own most recent public filing or
   release finds no figure more than 14 days older than what the company has itself published as
   of the scoring date.
4. A dated list of what changed recently (a "what changed" section or equivalent) is visible
   without expanding anything, and states plainly when nothing has changed.

**Level 5**
1. Each tracked figure carries the date the underlying fact was itself published or reported,
   shown separately from the date the site last checked it.
2. If a declared source failed to collect, the page names which one in plain language a reader
   could act on, not an error code or an internal label.
3. A reader can tell how old the newest fact on the page is without doing arithmetic — an explicit
   date or a plain phrase, not only a raw timestamp.
4. The site states its refresh cadence in one sentence reachable without expanding anything, and
   no other text on the site contradicts it.

### D2 — Coverage (15)

*Does each declared domain list its declared suppliers with current footing facts, and does the
site say plainly what is not covered?* Subject to the coverage-gap cap.

**0:** No list of domains exists, or which suppliers are tracked cannot be found without leaving
the site's own pages.

**Level 3**
1. A list of every declared domain is visible after at most one click from the front page, each
   with one plain sentence describing what it covers.
2. Every domain shown has at least one tracked supplier listed under it.
3. A stated list of what the site does not cover is visible after at most one click.
4. Distress or consolidation facts (acquired, shut down, debt, layoffs, a leadership exit) have a
   visible place of their own for a given supplier, and it says plainly when there is nothing to
   show, rather than omitting the section.

**Level 5**
1. Every domain and every tracked supplier has a stable, linkable address that can be forwarded
   and lands in the same place on return.
2. The count of tracked domains and tracked suppliers is stated as a number on the page, not left
   for a reader to tally.
3. The page reads inclusion as a data fact rather than a judgment: no ranking or evaluative
   language is attached to which suppliers are tracked in a domain.
4. A reader can tell, for a domain they know, whether a supplier they expected is simply not
   tracked (found in the "not covered" statement or absent with no comment) versus tracked with no
   recent news to show.

### D3 — Deciding a supplier's footing from facts alone (20)

*Starting from the front page, can a security leader compare suppliers in one domain on a like
basis, find the domain they care about quickly, and read one supplier's footing facts in one
place, without the site telling them what to conclude?*

**0:** Figures for different suppliers in the same domain are never shown together, or cannot be
compared without leaving the page.

**Level 3**
1. Within one domain, every tracked supplier's headline growth or footing figure is shown on the
   same named metric and the same kind of period, in one table or list, without navigating to a
   separate page per supplier.
2. A reader can go from the front page to a named domain's suppliers in one click or one scroll,
   at both widths.
3. For one named supplier, its latest reported figure, its prior period, its ownership or last
   funding round, and its recent dated events are all visible in one place without further clicks.
4. No comparison on the page ranks suppliers, orders them by a judgment, or labels one as leading,
   accelerating, or slowing; figures are shown, not interpreted.

**Level 5**
1. Each domain's table shows a computed reference point (for example the domain's median or
   average growth) alongside the individual figures, so a reader can see where a supplier sits
   without the site naming a winner.
2. A reader can re-order a domain's suppliers themselves by any shown figure; the site does not
   fix one order for them.
3. The supplier question end to end: starting from the front page, a reader reaches, for a named
   supplier, its metric and period, its prior period, its ownership state, and its most recent
   dated event, in under a minute and without losing their place.
4. At 390 pixels wide, the footing facts reachable at 1440 are reachable in the same number of
   interactions, not hidden behind a desktop-only feature.

### D4 — Evidence legibility and reconstructability (13)

*Can a claim be traced to a named public source without leaving the flow of reading, and could a
second person rebuild the figure from what is shown?*

**0:** Figures carry no sources, or sources are listed only in bulk somewhere else on the site.

**Level 3**
1. Every tracked figure on a domain table names or links its source next to the figure itself.
2. The source link resolves to a real, checkable public document (a filing, a press release, a
   company disclosure), not to the site's own page about itself.
3. The method by which a figure is defined — for example, what "revenue growth" means and where
   it comes from — is stated once, in plain sentences, reachable after at most one click.
4. The date the underlying fact happened or was filed, and the date the site last checked it, are
   shown as two distinct dates, never merged into one.

**Level 5**
1. A reader can get from a shown figure to its source's publisher and date in one interaction,
   without losing their place on the page.
2. Where a figure cannot be shown on a like-for-like basis (a company reports no comparable
   metric), the page says so rather than approximating or silently omitting it.
3. A stated sourcing standard exists — what kind of source is strong enough to publish a distress
   or consolidation fact on its own, and what is not — reachable after at most one click.
4. A way to report a wrong figure is reachable from the evidence itself, not only from a general
   contact address.

### D5 — Trust (12)

*Is there any judgment language on a live page, does the site say who runs it and how coverage is
chosen, and does a corrections record exist and work?* Subject to fit-for-purpose blocker 3.

**0:** No statement of who operates the site exists anywhere, and no corrections mechanism exists.

**Level 3**
1. No word or phrase on any live page states a stance, a ranking, a forecast, or an interpretation
   of what a fact means for a supplier's prospects, checked against the definition of judgment
   language in Section 2.
2. A plain statement exists, reachable after at most one click, that the site publishes facts
   only, automatically, with no person approving each figure before it appears.
3. A corrections page exists at a stable address, lists any corrections with their dates, and
   states plainly when there are none.
4. A way to reach whoever runs the site with a question or a correction is visible without
   expanding anything.

**Level 5**
1. The site states, reachable after at most one click, who operates it and what their relationship
   to the tracked suppliers is (for example, employment by a reseller or integrator of some of the
   suppliers shown).
2. The site states how suppliers are chosen for coverage, and says plainly whether competitors and
   partners of the operator are held to the same evidence standard.
3. The dated archive (the standing thesis and any earlier signed material) is visibly and
   explicitly separated from the live tracker, so a reader cannot mistake an old judgment for a
   current fact.
4. The site states plainly that a corrected fact keeps its original wording in the historical
   record with the fix noted beside it, rather than being silently edited away.

### D6 — Density and scanability (4)

*Real information per screen, at the Zed standard, without becoming a wall.*

**0:** Fewer than three tracked suppliers visible per desktop screen in a domain table, or an
undifferentiated wall of text with no structure.

**Level 3**
1. A domain table shows at least eight tracked suppliers per 1440-by-900 screen, or the whole
   table if the domain has fewer than eight, counted from a capture.
2. Numbers that stack use tabular figures and align; metadata (dates, sources, ownership state)
   has a consistent treatment distinct from prose.
3. Body text is 14 pixels or larger, and line length in prose sections stays within about 50 to 80
   characters at 1440.
4. A supplier with no recent events and one with several recent events differ visibly (an amount,
   a count, or a visible absence), so a quiet supplier and an eventful one do not look identical.

**Level 5**
1. The front page with the run status, the coverage statement, and at least one full domain
   visible is under 6,000 pixels tall at 1440, by DOM measurement, with no essential content
   hidden in a closed section.
2. Every domain comparison is a table with fixed columns, not prose or cards.
3. Row rhythm comes from spacing, not small type: no continuous reading text under 13 pixels.
4. A reader can scan one full domain's supplier table without scrolling, at 1440.

### D7 — Phone (4)

*Does the 390-pixel-wide page carry the same substance as desktop, without a wall of scrolling or
unreadable text?*

**0:** Content available at 1440 is missing, reordered beyond recognition, or unusable at 390.

**Level 3**
1. The run-status line and at least one domain's suppliers are visible on the first screen at 390
   without expanding anything.
2. Site chrome takes no more than a quarter of the viewport height at 390, measured by DOM.
3. Every tap target is at least 24 by 24 CSS pixels.
4. No horizontal scroll exists at 390 or at 320.

**Level 5**
1. A supplier's full footing facts (figure, prior period, ownership, events) are reachable at 390
   in the same number of taps as the clicks it takes at 1440.
2. Body text stays 14 pixels or larger at 390, and dates and sources remain legible without
   zooming.
3. A domain index or jump list, if one exists at 1440, works the same way at 390.
4. A reader can scan one full domain's supplier list at 390 without a collapsed row hiding the
   figures that matter.

### D8 — Accessibility (4)

*WCAG 2.2 AA, verified by tooling and by keyboard.* Subject to fit-for-purpose blocker 5.

**0:** Critical axe violations on the front page, or the page cannot be operated by keyboard.

**Level 3**
1. Zero critical and zero serious axe violations on `/` and `/corrections/` at both widths.
2. Every interactive element (a sortable column, an evidence link, a domain jump link) is reachable
   by keyboard and shows a visible focus indicator.
3. No text fails 4.5:1 contrast, including small metadata.
4. The page reflows at 320 CSS pixels with no horizontal scroll.

**Level 5**
1. Zero axe violations of any impact on `/` and `/corrections/` at both widths.
2. Every pointer target is at least 24 by 24 CSS pixels or meets a listed exception.
3. A skip link is the first focus stop, and the market-by-domain section is reachable within 15
   Tab presses.
4. Landmarks and `time` elements with `datetime` are used throughout the tracker.

### D9 — Performance (3)

*Core Web Vitals on a real network, measured not assumed.* Lab medians of three Lighthouse runs on
the front page; field data replaces lab data when it exists.

**0:** Mobile LCP over 6 seconds, or the page does not become usable on a throttled phone profile.

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

### D10 — Machine legibility (2)

*Can a machine reader parse the tracker and come back for structured data, without needing to
guess where anything lives?* Scored from a cold read of the home URL with no rendering.

**0:** Content is not present in the served HTML, and no structured data of any kind exists.

**Level 3**
1. All tracked figures are in the prerendered HTML; a cold read extracts a domain's suppliers and
   their figures without executing scripts.
2. Valid JSON-LD on the front page identifies the page type, publisher, and last-updated date.
3. A feed or machine-readable index of the site's routes exists and is discoverable from the home
   page, without guessing URLs.
4. The HTML has no empty headings and no duplicate ids.

**Level 5**
1. A structured endpoint (JSON or JSON-LD) exposes the run-status state, the domain list, and each
   supplier's latest figure without a machine having to parse prose.
2. Each tracked figure has a stable anchor id that appears in both the HTML and any structured
   data, so one fact can be cited by URL.
3. The publisher is a resolvable entity (an `Organization` or `Person` with a stable identifier).
4. A crawler policy is stated deliberately, not left as a default.

### D11 — Craft (1)

*Typography, restraint, colour discipline, the feeling of a well-made instrument.*

**0:** Default styling or visibly broken layout at either width.

**Level 3**
1. One sans family and at most one monospace family; a consistent type scale of no more than six
   sizes on the front page.
2. One accent colour on a neutral scale, light theme only, and colour carries meaning wherever it
   appears.
3. Spacing follows a consistent scale; nothing collides, clips, or overflows at 1440, 390, or 320.
4. No decoration that carries no information.

**Level 5**
1. Removing the accent colour would not break comprehension, checked on a greyscale capture.
2. Every repeated pattern (a table row, a source link, a run-status line, a date) is identical
   everywhere it appears.
3. The page reads as one instrument: nothing on it looks like marketing chrome.

## 5. Scoring record format

For each dimension record: the score; each test with yes or no; the evidence for each (file path,
command, or quoted line with URL); and one sentence on what would raise the score by one. Record
the deployment URL, the commit it serves, the date, and the scorer. Record caps and any
fit-for-purpose blocker applied.

## 6. Agreement check

The brief requires that a different agent could score the site and land within one point on every
dimension. Every score is produced by two independent blind scorers working from the same
evidence, neither seeing the other's scores or any earlier score file: Claude Opus 5.5
(`claude-opus-5-5`) and GPT-6 Sol (`codex exec -m gpt-6-sol`). The owner chose this pair on
2026-09-25 (D-77); this rule carries forward unchanged from v2.2. The coordinator reconciles but
does not score. Any dimension where the two differ by more than one point is a defect in the
rubric's wording, not in a scorer: the test that was read two ways is rewritten, the rubric
version is bumped, and the change is recorded here.

### Revision record

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-09-20 | First version, from the brief's thirteen dimensions revised against Phase 1 research. |
| 1.1 | 2026-09-20 | After the agreement check. Two scorers landed within one point on all thirteen dimensions at v1.0 (five dimensions differed by one). Every test they read differently was reworded: the 0 rule is now "no level-3 test passes" (D1's anchor overlapped its first test); D1 test 2 is tied to the first screen; D4 test 1 says a headline stating the read counts; "link or control", "visible after at most one click", "without expanding anything" and "site chrome" are defined once; D7 test 1 requires the verdict as a labelled field; D8 level-5 test 6 and D10 level-5 test 4 were each split in two; the freshness cap names which contradictions trigger it; the small-scale rule is stated as general. |
| 1.2 | 2026-09-20 | After the adversarial pass on the Phase 3 specs (`consults/adversarial-pass.md`, finding 8). D4 level-5 test 1 read "within the first 40 percent of page height or within 5,000 pixels, whichever is smaller", which no short page can pass and which pulled against D6 level-5 test 1 (a page under 6,000 pixels). It is now a flat 5,000 pixels. The baseline is unaffected: D4 fails at level 3, so no level-5 test changes its score. |
| 2.0 | 2026-09-20 | Re-aimed at `docs/archive/2026-09-weekly-issue/product-core.md` after the owner restated the purpose: a practitioner's market pulse for security leaders, with the founding thesis as one standing analysis. D1 to D4 and D11 rewritten, weights changed (section 3), D8 level-5 test 1 reworded. D5 to D7, D9, D10, D12 and D13 tests unchanged. The v1.2 baseline of 33.0 is not comparable with v2.0 scores; the baseline is re-scored under v2.0 from the same evidence in `score-baseline-v2.md`. |
| 2.1 | 2026-09-20 | After the external review by Codex on `gpt-6-astra`. Weights changed toward decision value (20), freshness (15), evidence (12) and trust (10). Fit-for-purpose blockers added, so a high composite cannot hide a mislabelled figure, an unsupported comparison, machine content posing as judgment, or an accessibility failure. D1 level-5 test 1 and D4 level-5 test 1 no longer reward a ranked vendor table. D3 level-3 test 5 asks for separate dates in place of a 45-day threshold. D12 gains a disclosure test at level 3 and an inclusion-rules test at level 5. A statement of what the instrument cannot show was added. Not yet addressed from the review: double counting between D1 and D4 and between D3 and D11, and replacing D6's item counts with a scanning task. |
| 2.2 | 2026-09-25 | Scorers changed to Claude Opus 5.5 and GPT-6 Sol, both blind (D-77). No test changed. The rubric still scored a signed-judgment product; under `intent.md` v1.4 and D-76 (facts only, published automatically) it needed re-aiming before the next score, which was step 7 of `docs/archive/2026-10-refresh-gate/autonomy-coverage-plan.md`. |
| 3.0 | 2026-09-26 | Re-aimed at the facts-only supplier tracker (AUTO-001 step 7). The site no longer publishes a signed judgment on any live page, so every dimension and every fit-for-purpose blocker that assumed one is retired or rewritten. Eleven dimensions replace thirteen: D1–D5 follow intent v1.4's success order — freshness without fail (22), coverage (15), deciding a supplier's footing from facts alone (20), evidence legibility and reconstructability (13), and trust (12) — and D6–D11 (density, phone, accessibility, performance, machine legibility, craft) hold modest weight, with a new Phone dimension added because the tracker has to work at 390 pixels, not just look acceptable there. Follow-and-share and the old wayfinding dimension are dropped as separate dimensions: follow-and-share measured audience return, which Section 1 already excludes as the outcome scorecard's job, and wayfinding's stable-address tests move into D2 and D3. The fit-for-purpose blockers are replaced with five that fit a machine that publishes no judgment: a mislabelled figure, a figure stale by more than 14 days against the company's own newer report, judgment language on a live page, a run-status line that misstates what happened, and an accessibility failure. The cadence cap and the misstated-freshness cap from v2.x are replaced with a freshness cap and a coverage-gap cap sized to this product. Scores under v2.x are not comparable with scores under this version; the site has to be scored fresh under v3.0. |
