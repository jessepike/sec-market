# Integrity pass — implementation specification

- **Spec ID:** `SEC-MARKET-INTEGRITY-001`
- **Version:** `v0.1`
- **Status:** accepted, ready to implement
- **Author:** CPO session, 2026-08-20
- **Governs:** `SEC-013` follow-on work in [BACKLOG.md](../../BACKLOG.md)
- **Intent trace:** [intent.md](../../intent.md) — "Claims preserve provenance, uncertainty, conflicting evidence, and credible alternatives" and "must label their confidence and basis"

## Why this exists

An alignment audit on 2026-08-19 found that Security Market Pulse states several things about
itself that are not true. The product's entire claim is that every mark on the page means
something checkable. Each item below is a place where a mark means nothing, contradicts another
mark, or would crash if used.

This is a correction pass, not a feature pass. Nothing here adds a domain, a source, a vendor, a
figure, or a section. Every change either removes a false statement or makes an existing true
statement enforceable.

## Non-goals — do not do these

Read this list before starting and do not exceed it.

1. **Do not author new content.** No new print cards, no new evidence records, no new domains, no
   new vendors, no new figures, no rewritten market call, no changed postures. If a change seems
   to require inventing a number, stop and report instead.
2. **Do not touch `web/src/data/evidence.ts`.** It is correct.
3. **Do not delete any CSS rule.** Item 2 removes a DOM element whose CSS class becomes unused.
   Leave the CSS alone. Deleting a rule because static analysis says it is unused is banned by
   [AGENTS.md](../../AGENTS.md) and has already caused one incident on this repository.
4. **Do not change any published figure, posture, horizon, confidence value, or market call.**
   Confidence not varying is a real defect and it is deliberately out of scope here — it is
   editorial judgment, and it belongs to the next pass.
5. **Do not commit or push to `main`.** See § Branch and delivery.

## Decisions already made

These are settled. Implement them as written; do not re-open them.

| # | Decision | Rationale |
|---|---|---|
| D-a | The "needs a source" provenance state is removed from the product, not populated | It has never once occurred in the data. A legend advertising a state that cannot happen is the same defect class as an unsourced figure. Re-adding it later is a small change and is expected when a real instance appears. |
| D-b | Section naming stops asserting a cadence and names its window instead | The method section says refresh is manual and event-driven, "not a weekly news cycle," while the nav and heading say "this week." The gather loop is weekly; the edition is not. Naming the window is true under either cadence and survives a skipped week. |
| D-c | Print lines on domain cards use full vendor names, matching every other card | The SecOps line uses ticker shorthand that resolves to nothing. Full names both fix the bug and match the existing convention. |
| D-d | The five unreferenced evidence records stay and are wired in a later pass | Dell, Vertiv, Broadcom, Meta and Oracle are real, sourced, and belong to the two thinnest signal families. Surfacing them requires authoring figures, which is content work with a fabrication risk. This pass adds a check so the count cannot silently grow. |

## Work items

### 1. The landscape eyebrow must derive from the data

**File:** `web/src/components/DomainBoard.tsx`

Line 39 hardcodes `<p className="eyebrow">The landscape · four domains</p>` while the cards below
are rendered from `landscapeDomains`. The two can disagree, and will the moment a fifth domain is
promoted.

Replace the hardcoded word with one derived from `landscapeDomains.length`. Add a small
number-to-word helper covering 1 through 10 and falling back to the digit above that. Singular
must read "domain", plural "domains".

**Acceptance:** changing `landscapeDomainIds` in `web/src/data/domains.ts` to hold three ids
changes the eyebrow to "three domains" with no other edit. Revert the experiment afterwards.

### 2. Remove the "needs a source" provenance state

Four files.

**`web/src/components/ProvenanceRail.tsx`** — delete the third `<li>`, the one containing
`NEEDS A SOURCE` and its `rail__state--unsourced` class. Leave the other two legend items exactly
as they are. Do not touch the stylesheet.

**`web/src/data/types.ts`** — delete the `UnsourcedClaim` interface, remove `'unsourced'` from the
`ProvenanceLayer` union, and remove `UnsourcedClaim` from the `Provenance` union. Update the
doc comment above `ProvenanceLayer` so it describes two layers rather than three.

**`web/tests/landscape-data.test.ts`** — line 15 carries `if (provenance.layer === 'unsourced') return []`.
That branch becomes unreachable. Delete the line.

**`web/tests/e2e/smoke.spec.ts`** — line 15 asserts `NEEDS A SOURCE` is visible. Delete that
assertion.

**Acceptance:** `tsc -b` passes with no unused-type or unreachable-branch complaints, and grepping
the whole of `web/src` and `web/tests` for `unsourced` returns nothing except any CSS rule, which
stays.

### 3. Stop asserting a weekly cadence

Three copy changes and one test change. The dated window stays visible; only the cadence claim goes.

**`web/src/components/Header.tsx`** line 6 — nav label `'This week'` becomes `'What moved'`. The
`href` stays `#moved`.

**`web/src/components/WhatMoved.tsx`** line 10 — the heading `What moved this week` becomes
`What moved`.

**`web/src/components/WhatMoved.tsx`** — the window label currently renders as `WEEK OF <range>`.
Change the literal `WEEK OF` to `WINDOW ·`. The range itself is unchanged and still comes from
`weekMoves.label`.

**`web/src/data/dates.ts`** — `formatWeekRange` keeps its name and behaviour. Do not rename it;
it genuinely formats a seven-day range.

**`web/tests/e2e/smoke.spec.ts`** line 16 — the assertion targets the heading text
`'What moved this week'`. Do not simply update the string. Replace the assertion so it targets the
section by its stable id or role rather than its editorial copy, matching the lesson already
recorded on this repository that tests pinned to edition prose break by design. Assert the region
with id `moved` is visible.

**`web/src/components/HowThisWorks.tsx`** — unchanged. The sentence "Not a weekly news cycle" is
the true statement and it stays.

### 4. Fix the SecOps print line before it crashes

**File:** `web/src/data/domains.ts`, the `secops` record.

`print` is currently `'S1 +23% · CRWD +24% · XSIAM +100% · Torq $1.2B'`.

`trackedPrintEvidenceIds()` tokenises that line and looks each token up against `vendorPrints`.
`S1` does not match `SentinelOne` and `CRWD` does not match `CrowdStrike`, so the function throws.
It does not throw today only because the function is called for landscape domains only, and SecOps
is not on the landscape. Promoting SecOps — which is under active consideration — breaks the page.

Change the line to `'SentinelOne +23% · CrowdStrike +24% · XSIAM +100% · Torq $1.2B'`.

Do not change the percentages or the Torq figure. Do not change any other domain's print line.
`XSIAM` already resolves against `Palo Alto XSIAM` via the suffix rule and stays as it is.

**Acceptance:** `trackedPrintEvidenceIds()` returns a non-empty array for all six domains in
`securityDomains`, not just the four on the landscape. Item 7 makes this permanent.

### 5. De-duplicate evidence ids in the moved-this-window section

**File:** `web/src/data/whatMoved.ts`

Three `flatMap` calls build evidence id arrays with no de-duplication. The M&A entry currently
produces eight ids of which four are distinct.

Add a module-local `uniq(ids: string[]): string[]` helper that preserves first-seen order, and
apply it to the `evidenceIds` of all three tracked moves — the print move, the capital move, and
both branches of the M&A move.

Order matters for display. Preserve first appearance; do not sort.

**Acceptance:** every `evidenceIds` array on `weekMoves.tracked` has no repeated member, and the
rendered evidence chip labels are unchanged apart from the removed duplicates.

### 6. Give the two judged rows a stated basis

**Files:** `web/src/data/whatMoved.ts` and `web/src/components/WhatMoved.tsx`

Both judged rows — the HELD/MOVED row and the WHY row — hardcode `evidenceIds: []`. They render
under a header reading "JUDGED · a person signed this" with no link, on a page where every other
judged claim carries one. Neither row is unsourced in truth: the HELD row's warrant is the
comparison of two frozen edition snapshots, and the WHY row quotes a method rule verbatim.

Extend the `WeekMove` interface with two optional fields:

```ts
basisHref?: string
basisLabel?: string
```

Set the HELD/MOVED row to `basisHref: '#domains'` with `basisLabel: 'Edition delta'`, and the WHY
row to `basisHref: '#method'` with `basisLabel: 'Method · breadth rule'`.

In `WhatMoved.tsx`, where a judged row currently renders its evidence link, render an ordinary
anchor to `basisHref` labelled with `basisLabel` when `evidenceIds` is empty and a basis is
present. When `evidenceIds` is non-empty, keep the existing evidence chip and ignore the basis.
Style it with the existing evidence-chip class so it does not need new CSS.

**Acceptance:** no judged row on the page renders with neither an evidence chip nor a basis link.
Item 7 makes this permanent.

### 7. New build gate — `verify:integrity`

The three defects above (items 2, 4 and 6) all share a shape: something was true when written and
nothing stopped it becoming false. Add a gate so they cannot recur silently. This follows the
existing `verify:edition` and `verify:panel` pattern.

**New file:** `web/scripts/verify-integrity.ts`

**New script** in `web/package.json`: `"verify:integrity": "tsx scripts/verify-integrity.ts"`,
added to the `build` chain immediately after `verify:panel` and before `tsc -b`.

The script must exit non-zero with a readable message on any of these:

1. **Print lines resolve for every domain.** Call `trackedPrintEvidenceIds()` for all six entries
   in `securityDomains`, not only `landscapeDomains`. Any throw or empty result fails the build.
2. **Every judged claim has a warrant.** For every entry in `weekMoves.judged`, require either a
   non-empty `evidenceIds` or a non-empty `basisHref`.
3. **No duplicate evidence ids.** For every array of evidence ids reachable from `weekMoves`,
   `securityDomains`, `platformPressure` and `hypotheses`, require that the array has no repeated
   member.
4. **Every referenced evidence id exists.** Every id referenced anywhere in the data resolves to a
   record in `evidenceRecords`.
5. **Unreferenced evidence records are reported, not fatal.** Count records in `evidenceRecords`
   that nothing references, print their ids and titles, and fail only if the count exceeds five.
   Five is the count as of 2026-08-20: A4 Dell, A5 Vertiv, A6 Broadcom, B4 Meta, B5 Oracle. The
   threshold is a ratchet — it may be lowered when those are wired in, never raised.

**Prove each gate fails closed.** For every one of the five checks, temporarily perturb the data so
the check should fire, run the build, confirm it refuses, then revert. A gate nobody has watched
fire is a comment. Report in the handoff which perturbation you used for each.

### 8. Derive the evidence-library filter options from the records

**File:** `web/src/components/EvidenceLibrary.tsx`

`ALL_CLASSES` at line 7 is a hardcoded list of all eight `SourceClass` values. One of them,
`VENDOR-SURVEY`, matches zero of the 72 records, so the filter offers a choice that always returns
an empty list.

Replace the constant with a value derived from `evidenceRecords` — the distinct set of
`sourceClass` values actually present, sorted so the order is stable across builds. Keep the
`All classes` option at the top.

**Acceptance:** the dropdown contains no option that yields zero results, and adding a record with
a previously unused source class makes that option appear with no further edit.

## Acceptance criteria for the whole pass

Given the repository on branch `preview`, when this specification is fully implemented, then:

1. `npm run test` passes from `web/` — that chain is lint, data tests, the full build including
   all three verify gates, and the Playwright end-to-end suite.
2. Grepping `web/src` and `web/tests` for `unsourced` returns only a CSS rule, if anything.
3. Grepping `web/src` for `this week` returns nothing outside `HowThisWorks.tsx`.
4. `trackedPrintEvidenceIds()` returns a non-empty array for all six domains.
5. Every one of the five checks in item 7 has been observed to fail the build when its input was
   perturbed, and to pass once reverted.
6. The rendered page differs from production in exactly these visible ways and no others: the
   third legend chip is gone from the top rail, the nav item reads "What moved", the section
   heading reads "What moved", the window label reads "WINDOW ·", the two judged rows carry a
   basis link, and the source-class dropdown has one fewer option. Everything else is pixel
   identical.
7. No figure, posture, horizon, confidence value, evidence record, or market-call sentence has
   changed.

## Visual verification — mandatory

This is a `web/` change, so [AGENTS.md](../../AGENTS.md) § Visual review before publish applies in
full. A passing build is not a rendered page.

From `web/`, capture both widths for production and for the preview build:

```
node scripts/shot.mjs https://securitymarketpulse.com/ /tmp/prod
node scripts/shot.mjs <preview-url> /tmp/preview
```

Compare them at 1440px and 390px and state plainly what moved. The expected diff is item 6 of the
acceptance criteria. **Anything else that moved is a regression and must be reported, not
explained away.** Pay particular attention to the top rail, which loses a flex child, and to the
"What moved" section on a phone, where the heading gets shorter and the window label longer.

## Branch and delivery

1. Work on a short-lived branch off `preview`, named `integrity/pass-one`.
2. Commit atomically — one commit per numbered work item, conventional format
   (`fix(rail): remove the unsourced legend state`).
3. Merge into `preview` and push `preview`. Vercel rebuilds the stable preview URL at
   https://security-market-pulse-git-preview-pikeholdings.vercel.app
4. **Do not push to `main`. Do not merge to `main`. Do not run `vercel --prod`.** Production moves
   only when the owner says so, and that is a separate act. The pre-push hook will refuse a direct
   push to `main`; do not work around it.
5. Commit email must be `jesse@keatingpike.com` or the Vercel deploy fails.

## Handoff report required

When finished, report:

- which of the eight items landed, with the commit hash for each;
- the perturbation used to prove each of the five build gates fails closed;
- the before-and-after screenshots at both widths, and a plain statement of what moved;
- anything found that is not in this specification — report it, do not fix it.
