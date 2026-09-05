Since ExitPlanMode isn't available in this session, here's the review directly.

## 1. Prior findings — closed / open, with the closing commit

**Codex review**

1. Blocker, vendor lens missing — closed in `b4413b5`/`702edc3` (before this fix-pass range). See §3 for a fresh look at it.
2. Blocker, no retrieval receipts — closed by `dd0f120` + `838775a`. All 23 `W36-*` records now carry `retrieval` (finalUrl/sha256/fetchedAt/locator). I fetched two of the "corrected verbatim" sources live (HiddenLayer/SecurityWeek, Echo-Minimus/Return on Security) and both excerpts match exactly, including the source's own "and there assets thereof" typo, which the commit deliberately preserved rather than silently fixing.
3. Blocker, lock manifest not append-only, `--write` writes before validating — closed for `--write` itself (`9a108a3` now validates the candidate issue before writing, then re-validates after). Only partially closed for the build-time gate: the append-only comparison against history (`readBaseManifest`, `web/scripts/verify-issue.ts:58`) only runs if `origin/preview`, local `preview`, or `HEAD~1` resolves as a git ref. If none do, it prints a warning and passes anyway (`verify-issue.ts:396`). This is the exact check that runs on every `npm run build`, i.e. every Vercel build. See finding 1 below.
4. Blocker, draft can carry judgment fields — closed by `2a9041c`.
5. Blocker, empty published/signedOn dates pass, bad dates reach the feed — closed by `ce4fba8` plus the `generate-feed.ts` change (strict ISO date validation everywhere, `toRfc822` now throws on a bad date instead of emitting `Invalid Date`).
6. Should-fix, `background` doesn't check direction — closed by `ce4fba8`.
7. Should-fix, dist gate checks shape/count only — closed by `a371d99`. Real identity checks now: JSON copy id/evidence-set match, exact newest-first archive order, parsed RSS guid set and RFC 822 pubDate. `tests/dist-fixtures.test.ts` adds the two-published-plus-draft fixture Codex asked for.
8. Should-fix, header nav dead off the front page — closed by `1fcdfac`.
9. Should-fix, unescaped meta attributes — closed, but it took two commits. `a691212` added the escaping but its og:description/twitter:description regex only matched a single-line tag, and `index.html` wraps those tags across two lines, so both kept the front page's copy on every non-front route. `1deaa09` fixed the regex scope. See finding 2 below — nothing would have caught the first version's bug.
10. Should-fix, wrong `--write` command in the docs — closed by `ee39532`.
11. Should-fix, no lane/copy bounds — closed by `462f3d9`.

**Claude review**

1. Blocker, thesis/posture-delta evidence ids never resolved — closed by `e6a493f`. Check 4 now resolves all of them, and check 12 throws instead of silently skipping an unresolved id.
2. Should-fix, vendor lens not built — closed, same as Codex-1.
3. Should-fix, header nav dead on new routes — closed, same as Codex-8.
4. Nit, `background` direction — closed, same as Codex-6.
5. Nit, DomainBoard heading loses screen-reader domain navigation — open, unaddressed, not part of this fix pass.
6. Nit, no trailing-slash/404 handling for directory routes — open, unaddressed, `vercel.json` untouched.

## 2. New defects introduced by the fix pass

**Should-fix — `web/scripts/verify-issue.ts:58` (`readBaseManifest`) and `:396`.** The append-only history check that's supposed to close Codex-3 silently degrades to a warning-only no-op whenever `origin/preview`, local `preview`, and `HEAD~1` all fail to resolve — which is a plausible shape for a CI checkout, including Vercel's own build clone, which is the one environment this gate exists to protect. If that ref never resolves there, a commit that rewrites a published issue's data along with its manifest hash together would pass the build with only a console line nobody watches for. This tradeoff is candidly documented in `docs/active/weekly-issue-spec.md` §11 (F5) as accepted, but nobody has confirmed what a real Vercel build for this repo actually does. Smallest fix: check an actual build log for the "WARNING — could not read a base manifest" line; if it shows up, either fetch the needed ref explicitly in the build step or make the check fail-closed on `preview`/`main` builds instead of warning and continuing.

**Should-fix — `web/scripts/verify-dist.ts:42` and the rest of that file.** No gate anywhere, and no test, asserts the actual text of `og:description`/`twitter:description` in the built HTML. That's exactly the bug class that shipped in `a691212` and needed a second commit to fix, and it was only caught by manually building and grepping the output, not by anything automated. The same class of regression (say, a future reformat of `index.html`'s meta tags) could reintroduce it silently. Smallest fix: add a check that reads a built non-front route's HTML and asserts its og/twitter description content matches the expected per-route text.

**Nit — `web/scripts/verify-issue.ts:211` (check 4).** The evidence-id resolution logic is now hand-rolled inline instead of calling the existing `issueEvidenceIds()` helper (`web/src/data/issueHelpers.ts:137`) that `generate-feed.ts` and `verify-dist.ts` already share. They agree today, but it's the same drift risk that helper's own docstring warns about elsewhere.

I checked the real `2026-w36` draft data against every new bound by hand (couldn't run the script itself — the checked-out `node_modules` has a linux-arm64 `esbuild` binary on this darwin host, an environment issue, not a code issue): `read` is 138/140 characters, all 22 headlines are under 110, every lane is at or under the 8-item cap, and all 23 cited evidence ids resolve with valid-shaped receipts. No false positive. I also didn't find any e2e test that passes vacuously — `lens.spec.ts` and the new permalink-nav test both assert against real computed counts and URLs, not fixed constants.

## 3. Vendor lens (SEC-031)

Untouched by this fix pass, but assessed fresh as asked. It filters after hydration only — the provider starts at `null` and only reads the URL inside a `useEffect`, so prerendering never sees a filtered state, and the inactive render is structurally identical to the old placeholder. It handles unknown slugs cleanly (confirmed by code and by `lens.spec.ts`'s dedicated test). It round-trips the URL correctly for the normal case; one asymmetry that's likely intentional rather than a bug — navigating directly to `?vendors=` (present but empty) shows a filtered, zero-match state, while clearing the last chip in the UI collapses back to no parameter at all rather than to `?vendors=`. Worth a decision, not a defect. It's byte-identical with no parameter. Nothing breaks with a second issue: the provider always wraps whatever the current `latestIssue` is, and by explicit design the lens only ever appears on the front page — an issue permalink never gets a lens control, old or new. That scope limit is documented in the code and doesn't regress with more issues, but it's worth confirming that's the intended scope rather than an accepted gap.

**Verdict:** merge after the two should-fixes above — confirm what the append-only gate does on a real Vercel build, and add a content check for the meta descriptions. Do not merge as-is only because of that unverified gate; nothing else here blocks it.
