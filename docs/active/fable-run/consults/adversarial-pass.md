# Adversarial pass on the Phase 3 plan

**Artifact ID:** `SEC-MARKET-FABLE-ADVERSARY` v0.1. Task T3-3, an adversarial reviewer, 2026-09-20.
**Attacking:** the three v0.1 Phase 3 proposals, against `fable-run-brief.md`, `site-rubric.md` v1.1,
`score-baseline.md`, `intent.md` v1.2, `AGENTS.md`, `.claude/rules/constraints.md` and the code under
`web/`. Read-only; no file outside this one was changed.

## Verdict

The plan is a good diagnosis attached to a build three to four times larger than the diagnosis
justifies, and it rests on a state of the repository that is already false. A second session has an
unsigned draft issue `2026-w37` on a branch that will land on `preview`, and the whole first-screen
design assumes a signed newest issue with a verdict, a signature and a publication date. The design's
headline number, chrome falling from 221 pixels to 48, can only be reached by deleting two visible
elements that section 8 never lists. Decision D-3 changes the issue data model that
`weekly-issue-spec.md` governs under SEC-027, which the brief's section 10 forbids, then displays
condition statuses for a locked issue that cannot carry them. The monetization plan is the outside
consult transcribed, and it defers the one question that could stop the project, the employer's
outside-activity policy, to a stage nine months away when it plausibly bites today. What is good here
is small and cheap: reorder the front page, link the three JSON files that already exist, and fix one
sentence. I would keep roughly a quarter of Phase 4 and reject the rest for now.

## 1. A draft issue 2026-w37 is about to land and the whole design assumes a signed one

Claim attacked. `design-spec.md` section 3.1 draws the first screen around
`ISSUE 2026-W36 ... SIGNED 19 SEP 2026` and `HOLDS · medium confidence / judged 19 Sep 2026 by Jesse
Pike`, and `agent-surface-spec.md` section 3.2 publishes `"current": { "verdict": "holds", ...
"signedBy": "Jesse Pike" }`. Neither document mentions a second issue in flight.

Evidence. `git log preview..issue/2026-w37` shows commit `7647baa feat(web): draft issue 2026-w37
(unsigned)`, touching `web/src/data/evidence.ts`, `web/src/data/issues/2026-w37.ts` and
`web/src/data/issues/index.ts`, on a branch that exists locally and on `origin`. When it merges,
`latestIssue` becomes a draft. `web/src/components/IssueHero.tsx` lines 6 to 16 then renders "draft,
awaiting signature" and a `Draft. Not yet signed.` banner instead of a signature line.
`web/src/data/types.ts` line 282 makes `weThink.thesis` `ThesisScore | null` on a draft and line 284
makes `signedBy` nullable, so the panel has no verdict, no confidence and no signer to show, and
`web/scripts/verify-issue.ts` line 797 enforces the draft banner. Every worktree stream would also
conflict on `web/src/data/issues/index.ts` and `evidence.ts`.

Severity: fatal to Phase 4 as sequenced.

Change. Settle the order with the owner before any stream starts. Either `2026-w37` is signed and
merged first and the baseline re-measured against it, or Phase 4 branches from a named commit and
freezes. Specify every first-screen surface for two states, signed newest and draft newest, because
draft is now the more likely state on any given day. And say in the owner packet that the 33.0
baseline was measured against a site showing `2026-w36`.

## 2. The run is aimed at the wrong problem, and its own research says so

Claim attacked. `fable-run-brief.md` section 7 commits Phase 4 to five parallel worktrees
(`mon/thesis`, `mon/firstscreen`, `mon/agent`, `mon/wayfind`, `mon/convert`), and `design-spec.md`
section 12 concedes the case against itself then answers it with "it is built to stay honest if
cadence fails."

Evidence. `research-synthesis.md` section 5 states it: "All of it is decoration if the cadence does
not [start]." `score-baseline.md` records an exposure denominator of 1 and an empty decision-impact
log, and ranks the cheapest fixes as its items 1, 2 and 5: reorder, link what exists, fix one
sentence. `monetization-plan.md` section 9 lists M-1 (the gather runtime) as blocking "everything,
including the project itself" and M-2 (the pilot list) as blocking "every claim of value", and both
are owner actions outside this run.

Severity: fatal to the scope, not to the direction.

Change. Cut Phase 4 to one worktree and about a quarter of the work. Keep the front-page reorder that
puts the signed judgment and the standing call above the lanes, a compact thesis block built only
from data that exists today, the descriptor line, one owner-written cadence sentence, a visible feed
link, links from the HTML and the sitemap to the three JSON files and the lock manifest, and `author`
plus dates on the archive JSON-LD. Drop for now the `/thesis/` and `/method/` routes, the Markdown
copies, `llms.txt`, the typeface change, the D-3 model change and `mon/convert`. That subset needs no
new route, no new field and no owner gate beyond the copy, and it captures most of the available
score movement.

## 3. D-3 changes the weekly issue pipeline the brief forbids, and then displays data that cannot exist

Claim attacked. `design-spec.md` section 11, decision D-3: "Two new optional fields on the issue
model... `lead` on an item, and a status per change condition on the judgment... The gather job and
the draft pipeline are not changed; the signer types them in."

Evidence, part one. `fable-run-brief.md` section 10: "Do not change the gather job or the weekly
issue pipeline, those are SEC-027 and SEC-028 and they have their own specs."
`docs/active/weekly-issue-spec.md` line 9 records that it governs "SEC-027 (issue model, page,
gates)" and its section 3 at line 53 holds the `IssueItem` and `Issue` interfaces verbatim. Adding a
field to `IssueItem` (`web/src/data/types.ts` line 232) or to `ThesisScore` (line 253) amends that
specification, changes the signing step, and touches `web/scripts/verify-issue.ts` check 14.

Evidence, part two. The change conditions live on `marketCall` in `web/src/data/market.ts` lines 61
to 66, but D-3 puts their statuses on `weThink.thesis` inside the Issue, and `2026-w36` is locked, so
there are no statuses for the current issue. Yet section 3.1 draws a status column showing `no
movement` four times and `agent-surface-spec.md` section 3.2 publishes
`{ "id": "c1", "status": "no-movement", "asOf": "2026-09-19" }`, dated to the signing of the locked
issue. Either the locked issue is edited, which is forbidden, or the statuses are invented, or they
stay blank until `2026-w37` is signed, in which case the status column and D2 level-5 test 1 both
show nothing on the day the owner reviews the preview.

Severity: fatal to D-3 as written.

Change. Move the condition statuses out of the Issue and onto `marketCall` in
`web/src/data/market.ts`, as a current status with an `asOf` date the owner sets when he signs. That
needs no model change, touches no locked data, keeps the lock hash safe by construction rather than
by argument, and still passes D2 level-5 test 1. Drop the `lead` field for this pass, accept that D4
level-3 test 3 and D6 level-3 test 2 keep failing, and revisit it inside SEC-027.

## 4. The 48-pixel chrome figure requires two undisclosed deletions

Claim attacked. `design-spec.md` section 3.2: "Site chrome drops from 221 pixels (26.2 percent of the
viewport) to 48 pixels. The header loses its second row on phones." Section 8 opens with "Removing a
visible page section is an owner gate. Nothing below happens without a yes," then lists six items,
none of which is the provenance rail or the header date.

Evidence. `web/src/App.tsx` lines 130 to 134 render `<SkipLink />`, then `<ProvenanceRail />`, then
`<Header>`, all outside `<main>`. The 390 capture at
`docs/active/fable-run/evidence/baseline/prod-home-390-viewport.png` shows the rail as a dark band of
roughly 90 pixels carrying "AS OF 19 SEP 2026", "TRACKED · PUBLIC PRINTS, NO JUDGMENT" and "JUDGED ·
SIGNED AND DATED BY A PERSON". Below it the header carries the brand, a "September 19, 2026" stamp
from `web/src/components/Header.tsx` lines 119 to 122, and the Menu button. Together those are the
221 pixels, so a 48-pixel header means both the rail and the date stamp are gone. The rubric's own
definition of site chrome ("the top offset of the first content element") makes the rail chrome by
construction, so unlike the descriptor line it cannot be reclassified as content.

Severity: serious, and a governance failure rather than a design failure. The owner is asked to
approve D-1 without being told it deletes the tracked-versus-judged legend.

Change. Add both items to the section 8 removal table with their own owner decision, and say where
the tracked-versus-judged distinction goes, because D5 level-3 test 3 depends on it. Then restate the
number: if the rail stays and only the header's second row goes, chrome is about 138 pixels, 16
percent of 844, which passes D4 level-3 test 4 comfortably. The test does not need the rail deleted.

## 5. The wireframe is drawn against copy that does not exist in the data

Claim attacked. `design-spec.md` section 3.1 shows the panel as
`DOES NOT CLAIM / A stable lag between infrastructure spending and security spending.` and
`WOULD CHANGE THE CALL / Security budgets grow and... / Organic acceleration across... / AI pilots
reach production... / Registered impulse then...`.

Evidence. None of those strings exist. `web/src/data/market.ts` line 56 has
`'Stable 0–8-quarter infrastructure-to-security lag'` and lines 62 to 65 hold the four real triggers,
measuring 67, 69, 64 and 103 characters. The right-hand panel is five of twelve columns, so after the
status column the text runs about 380 to 420 pixels wide and each trigger takes two to four lines at
14 pixels. Four triggers plus a heading plus the thesis, the verdict line and the running score do
not fit the 764 pixels left under the header, descriptor and issue line at 1440 by 900. The wireframe
resolves this by truncating each trigger to four words and an ellipsis, and a four-word stub is not
"the conditions that would change the call are visible" (D2 level-3 test 3). The real `read` is 138
characters, four lines at 32 pixels in a seven-column column, not the three the wireframe budgets.

Severity: serious. The first screen is the most important deliverable in the brief and its only
specification is a mock built from invented copy.

Change. Redraw section 3.1 from the exact strings in the data, with a stated font size, line height
and column width per block and a measured total. I would show the thesis sentence, the verdict line,
the running score and one line of "does not claim", and move the four change conditions just below
the fold, where D2 level-3 test 3 still passes.

## 6. The "late issue" label cannot work, and the design's honesty defence depends on it

Claim attacked. `design-spec.md` section 12: "it is built to stay honest if cadence fails. The issue
line shows both dates, the 'late' label appears on its own." Section 9: "any 'late' label [is]
computed from data at build time... and the build stream must say how a late label appears when no
build has run."

Evidence. The site is a static prerender with no scheduler: `web/vercel.json` has no cron and
`.claude/rules/constraints.md` line 19 lists a scheduler as not authorized. A label computed at build
time is computed before the issue is late, so it never appears. The only mechanism that works is a
client-side date comparison after hydration, which section 9 forbids in the same paragraph ("no dates
read from the clock during render"). The design states a constraint, states a feature that violates
it, hands the contradiction to the builder, and then leans on that feature to answer the strongest
case against the whole plan.

Severity: serious.

Change. Either accept a client-side label from a `useEffect`, say plainly that it is invisible to a
non-JavaScript reader and to the cold-agent test, and remove it from section 9's build-time list; or
drop it, mark D3 level-5 test 1 unachievable here, and rewrite section 12's defence. I would drop it.
D3 still reaches 4 without it.

## 7. The projected composite does not reconcile with its own table, and D9 at 3 is not credible

Claim attacked. `design-spec.md` section 10: "**Composite** | **33.0** | **about 75 to 83** | **about
58 to 64**", and in the same table "D9 Performance (5) | 2 | 3".

Evidence. Applying the rubric's own formula (score divided by 5, times weight) to the "every decision
is a yes" column gives 77.8 to 87.6, not 75 to 83, and to the "all no" column gives 59.8 to 66.8, not
58 to 64; the stated ranges look like midpoints rather than endpoints. That matters because
`site-rubric.md` section 6 and the brief's definition of done both require a different agent to land
within one point, and the headline number is not reproducible from the table above it. On D9,
`score-baseline.md` records mobile lab LCP of 4,356 milliseconds with FCP at 3,857; a 3 requires
mobile LCP at or under 2,500, a 43 percent cut, and the design offers one lever, self-hosting the
fonts, while adding a panel and a route and stating in section 8 that nothing is deleted. JavaScript
is already 229 KB against a 200 KB level-5 threshold and will not shrink.

Severity: serious, because the projection is what the owner is being asked to buy.

Change. Recompute both columns from the table and publish the arithmetic. Hold D9 at 2 and say
performance is not addressed beyond the font change. Put the exposure denominator in the same
sentence as the projected composite.

## 8. D4 level-5 test 1 is unpassable, and the design quotes only half of it

Claim attacked. `design-spec.md` section 4.1: "That puts the judgment, the change conditions, the
postures and all of the week's evidence inside 4,400 pixels, against D4 L5-1's limit of 5,000."

Evidence. `site-rubric.md` D4 level-5 test 1 reads "within the first 40 percent of page height or
within 5,000 pixels, **whichever is smaller**". The design targets a page "near 8,000 pixels", so
3,200 binds, not 5,000, and at 4,400 the test fails. Worse, the clause makes the test unpassable for
any short page: at 6,000 pixels the limit is 2,400 and the first screen alone is 900 with the
judgment and standing call adding 1,600. D6 level-5 test 1 rewards a page under 6,000 pixels while D4
level-5 test 1 punishes it. This is the clearest symptom of the same agent writing the instrument and
the thing it scores: the conflict is invisible until you try to satisfy both, and the author never
did.

Severity: serious as a rubric defect, minor as a score effect, since D4 still reaches 4 on the other
three level-5 tests.

Change. Rewrite D4 level-5 test 1 as a flat pixel limit, bump the rubric to v1.2, record it in the
revision table, and restate section 4.1 against the corrected test.

## 9. The design's constraint list omits the one test D-2 breaks

Claim attacked. `design-spec.md` section 9: "`tests/e2e/smoke.spec.ts` asserts the summary text of
`#moved-depth`, the id `#market-call-heading`, the `#research-depth` reveal and the evidence dialog."

Evidence. `web/tests/e2e/smoke.spec.ts` line 38 also asserts
`expect(page.locator('#method summary')).toHaveText('How this is built')`, and D-2 moves the method
section off the front page, so that is the one smoke assertion section 9 leaves out and the one D-2
breaks. Two pointer errors alongside it: `web/scripts/verify-issue.ts` holds no section id lists, so
section 6's instruction to update "the id lists in `scripts/verify-issue.ts`" names the wrong file
(they are in `web/scripts/prerender.ts`), and a new route needs `RouteKind` in
`web/src/data/routes.ts` line 4 widened plus a branch in `web/scripts/generate-seo.ts` at lines 145
and 158, or it silently inherits front-page JSON-LD.

Severity: serious for the D-2 gate, minor for the pointer errors.

Change. Re-derive section 9 from the spec files rather than from memory, and list every assertion
each decision breaks beside that decision in section 11.

## 10. The employment question is gated nine months away and it bites today

Claim attacked. `monetization-plan.md` section 9, M-3: the employment question is listed as blocking
"every direct-revenue model", and section 8 says "Stages 0 to 3 need **no** amendment."

Evidence. `consults/monetization-consult.md` section 6 frames the first of the three questions as
"whether the outside-business-activity policy requires disclosure or approval of a personally-owned
publication covering the market the employer sells into". That is about publishing, not payment. The
site is already live, already names the author, and already renders verdicts on segments containing
vendors the employer resells, so if disclosure or approval is required it is required now, and the
stage 0 to 3 plan proceeds on an unverified assumption that it is not.

Severity: serious. This is the single question that could stop the project and the one the plan
defers furthest.

Change. Move M-3 next to M-1 and M-2 at the front of the owner list, say plainly that its first part
gates publishing rather than payment, and ask it in writing this week.

## 11. The monetization plan is the consult with a cover sheet

Claim attacked. `monetization-plan.md` header: "Built on: `consults/monetization-consult.md` (an
outside commercial read, consulted once)".

Evidence. The plan reproduces the consult's conclusion, its nine-model ranking as a "what not to do"
list, its $3,000 price and $2,400 to $6,000 range, its 90-day and 12-month stage structure, its
twelve-month arithmetic table line for line, its intent amendments A, B and C verbatim, its
independence-policy text nearly verbatim, and eight of its nine owner decisions. The one item the
plan presents as its own judgment, cutting `mon/convert`, is also the consult's. Nowhere does the
coordinator disagree with its single source, and the brief's section 4 makes the judgment calls the
coordinator's job. On the price: the two fetched anchors, Signal Pro at $2,388 a year and The
Information Pro at $999 a year, are individual subscriptions being used to price an organizational
licence, and the only organizational anchor in either document is Forrester seats at $20,000 to
$50,000, labelled second-hand. So $3,000 is bounded by nothing in either direction while the range is
presented as if it were.

Severity: serious.

Change. Say which parts are the consult's and which are the coordinator's, state that $3,000 rests on
no organizational comparable rather than on a range, and stop refining it, because research will not
settle that number.

## 12. The agent surface recommends the irreversible option while rejecting a reversible one on irreversibility grounds

Claim attacked. `agent-surface-spec.md` section 4 recommends option A, allow everything including
training crawlers, listing "Cannot be undone for crawls already made" as the argument against it.
Section 5 rejects Creative Commons because "A Creative Commons grant cannot be withdrawn" and
recommends bespoke terms, all rights reserved with permission to quote, cite and index.

Evidence. The two apply opposite standards to the same risk. Allowing training crawlers is the
genuinely unrecoverable choice; a Creative Commons grant is irrevocable only for copies already
taken, which is the same exposure with attribution attached. Second, D8 level-5 test 4 asks for "a
licence or terms statement for content and data [that] is machine-discoverable", and bespoke prose at
`/method/#terms` is discoverable but not interpretable while an SPDX identifier or a Creative Commons
URL is both, so the recommendation satisfies the letter of the test and defeats its purpose. And "all
rights reserved" beside a `robots.txt` saying `ai-train=yes` is a mixed signal no crawler resolves in
the author's favour.

Severity: serious, and careless in one way. Granting public machine-training and commercial-use
permission over the owner's judgments about the market his employer sells into, before M-3 has been
asked, is the wrong order.

Change. Ask M-3 first. Then state a policy either way, because stating one is what the test needs,
and if the owner wants maximum reach use `CC BY 4.0` with an SPDX identifier in the JSON-LD.

## 13. Feeding agents the thesis sentence strips the labels intent requires

Claim attacked. `agent-surface-spec.md` section 3.2 publishes `/thesis.json` with
`"statement": "Infrastructure is running ahead. Security is splitting, not booming."` as a top-level
string, and section 1 sets the goal that an agent can "learn what the site currently believes".

Evidence. `intent.md` under "Must remain true": "Claims preserve provenance, uncertainty, conflicting
evidence, and credible alternatives" and judgments "must label their confidence and basis." A JSON
document exposing a quotable one-sentence market position as a top-level string, with `meaning`,
`doesNotClaim` and `confidence` as siblings no consumer is obliged to read, makes the unlabelled form
the easiest thing to quote. An answer engine restating "Infrastructure is running ahead, security is
splitting" without the medium confidence, the four no-call boundaries or the signature is the exact
failure mode intent was written to prevent, and it is the predictable outcome of optimising for agent
ingestion. Neither spec mentions it, and this is the sharpest intent conflict in the run.

Severity: serious.

Change. Do not publish a bare `statement` field. Make the smallest quotable unit carry its own
labels, for example a `position` object whose value cannot be read without `confidence`, `asOf`,
`signedBy` and `doesNotClaim`, and ask in the terms that any restatement carry the confidence and the
signer.

## 14. Two corrections surfaces that contradict each other

Claim attacked. `design-spec.md` section 4.1 row 11: "Next edition | `next` | Kept. Agrees with the
issue line." Section 5 adds a corrections block at `/thesis/#corrections` reading "None to date."

Evidence. `web/src/components/NextEdition.tsx` is not a next-edition section. The component rendering
`id="next"` is the corrections and contact block and its body reads "There is no form and no list."
The design keeps that text and adds a second surface presenting corrections as a dated list, so the
site would say both things; `score-baseline.md` scored D2 level-5 test 3 as No citing that exact
sentence. There is also nothing in `#next` for the issue line to "agree" with, since it carries no
date. Section 4.1 was written without opening the components.

Severity: minor. Change: fold the existing copy into the new surface, or leave corrections where they
are and drop the `/thesis/#corrections` block. One statement, one address.

## 15. Two smaller defects

Claim attacked, first. `agent-surface-spec.md` section 3.4 calls the `Accept: text/markdown` rewrite
"a stretch item" while section 6 makes Markdown copies a hard build check. Evidence:
`web/vercel.json` has no `rewrites` block and sets `"trailingSlash": true`; a header-conditioned
rewrite serves two bodies at one URL and the CDN cache key is the URL, so without an explicit `Vary`
the first cached response wins for everyone. The spec flags it and proposes a preview check, which is
right, but it has bolted a fail-closed gate onto a mechanism it does not yet know works. Change: if
Markdown copies are built at all, write the files and advertise them with `rel="alternate"`, which is
what the rubric test asks for, but do not negotiate on `Accept`.

Claim attacked, second. All three proposals treat the live site as authorized ground. Evidence:
`.claude/rules/constraints.md` line 19 says "Production collectors, database, scheduler, website,
digest, and autonomous pipeline are not authorized", while `intent.md` v1.1 promoted the website to
Decided and v1.2 keeps it. The two have disagreed since 2026-08-16 with the site in production
throughout, and no Phase 3 document notices, although the brief told the coordinator to read that
file in full. Change: ask the owner to amend line 19, and do not edit it, because line 12 forbids it.

Severity: minor, both.

## What survives

I tried to break these and could not. The lock hash is safe from new optional fields:
`web/scripts/verify-issue.ts` line 45 hashes `JSON.stringify(issue)` and `web/scripts/verify-dist.ts`
lines 95 and 108 compare `JSON.parse(JSON.stringify(issue))` on both sides, and `JSON.stringify`
drops `undefined` properties, so an optional field absent on `2026-w36` changes neither the hash nor
the deep-equality check. `design-spec.md` section 9 is correct, and my objection to D-3 is the
specification boundary, not the lock.

No gate or test asserts front-page section order. `MUST_SEE_SECTION_IDS` in
`web/scripts/prerender.ts` lines 57 to 72 asserts presence and the absence of a `details` ancestor
but not order, and the three e2e specs select by id and class, so the reorder is safe. The one e2e
test that does break is correctly identified: `web/tests/e2e/issue.spec.ts` lines 92 to 106 asserts
that clicking "Thesis" from a permalink navigates to `/#read`, and section 6 names it.

Duplicate ids are not a real risk from putting item ids on front-page rows. The front page and the
permalink are separate routes, `web/src/App.tsx` lines 43 to 97 render `IssueLanes` once, and
`PrintGrid` draws from `web/src/data/prints.ts`. Keeping the issue JSON bodies unchanged and deriving
addresses by rule (`agent-surface-spec.md` section 3.3) keeps the immutability proof simple.

The diagnosis is right. The signed judgment really does sit at y=5,137 on a 15,022 pixel page, three
working JSON files and a lock manifest really are linked from nowhere, and "Not a weekly news cycle"
really is at `web/src/components/HowThisWorks.tsx` lines 23 to 24.

The refusal to gate content survives, because a track record nobody can check is worth nothing.
`monetization-plan.md` section 4 is sound, including the permanent refusal of vendor sponsorship, and
section 10 argues the case against monetizing at full strength.

The honesty-at-small-scale rule is real and applied: `site-rubric.md` section 2 and `design-spec.md`
principle 3 both commit to showing one row and saying so, the projection keeps the exposure
denominator at 1 in every column, and I looked for padding and found none.

## If I were the owner

I would say no to Phase 4 as written and yes to about a quarter of it, in one worktree: the
front-page reorder, a compact thesis block built only from data that exists, the descriptor line, a
cadence sentence I write myself, a visible feed link, and links from the HTML and the sitemap to the
three JSON files and the lock manifest. I would reject D-3, the `/thesis/` and `/method/` routes, the
Markdown copies, `llms.txt`, the typeface change and `mon/convert`, and revisit them after four
issues have been signed. I would approve no crawler policy and no terms text until I have asked my
employer the outside-activity question, in writing, this week. I would settle `2026-w37` before any
branch is cut, and ask for section 3.1 redrawn with the real strings and a measured height before
approving a first screen at all. And I would spend the time saved on the gather runtime, because all
of the above is worth nothing if there is no second issue.
