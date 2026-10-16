1. **Blocker — `web/src/App.tsx:51`**

   - **What:** The specified vendor lens is explicitly a placeholder; there is no filtering control or `lens.spec.ts`.
   - **Why:** SEC-MARKET-ISSUE-001 §5 and §9 require shareable `?vendors=` filtering for issue items and scorecard prints.
   - **Smallest fix:** Implement the specified control/filter and its desktop/phone tests before merging.

2. **Blocker — `web/src/data/evidence.ts:1538`**

   - **What:** All 23 `W36-*` records have `retrievedAt` but none has the required `retrieval: { finalUrl, sha256, fetchedAt, locator }`. The gather packet also records WebFetch usage at `docs/archive/2026-09-weekly-issue/issues/2026-w36-gather.md:26` and contains no hashes.
   - **Why:** This contradicts `gather-brief.md:14-19,74-76` and leaves the first issue without the byte-level provenance the recurring job promises.
   - **Smallest fix:** Re-fetch the cited documents with `curl`, calculate the real hashes, add receipts to all 23 records, and require receipts for evidence introduced by weekly issues.

3. **Blocker — `web/scripts/verify-issue.ts:44-94,295-320`**

   - **What:** The lock is self-consistency checking, not genuinely append-only. Changing a published issue and replacing its manifest hash in the same commit passes. Removing both an issue and its manifest entry also passes. Additionally, `--write` writes and exits before running any issue checks.
   - **Why:** Published history can be rewritten undetected, and an invalid issue can be frozen before validation.
   - **Smallest fix:** Compare the manifest with a trusted parent/base version and permit additions only. In write mode, validate the candidate issue first, write only after success, then run the complete check against the resulting manifest.

4. **Blocker — `web/scripts/verify-issue.ts:259-268`**

   - **What:** A draft may populate `weThink.summary`, `weThink.postureDeltas`, and `weThink.noCalls`; only its thesis and signature fields are checked.
   - **Why:** The Tuesday machine can write directly into human-judgment fields while all requested gates remain green, contrary to `intent.md:64` and the gather brief’s exact empty-draft shape.
   - **Smallest fix:** Require every draft’s summary to be empty and its posture-delta and no-call arrays to be empty.

5. **Blocker — `web/scripts/verify-issue.ts:224-268`; `web/scripts/generate-feed.ts:55-66`**

   - **What:** “Set” means merely non-null. `published: ''` and `signedOn: ''` pass verification; the former is then treated as false and omitted from RSS. Other invalid non-empty dates produce `Invalid Date` as `pubDate`.
   - **Why:** A nominally published issue can lack signature/publication dates and disappear from the feed while the production guard passes.
   - **Smallest fix:** Strictly validate all issue dates as real `YYYY-MM-DD` dates, require non-empty publication/signature dates, and reject feed generation when conversion is invalid.

6. **Should-fix — `web/scripts/verify-issue.ts:197-215`**

   - **What:** `background: true` exempts any outside-window date, including dates after `weekEnding`; date comparisons are also performed on unvalidated strings.
   - **Why:** A future-dated item can pass by being mislabeled “background.”
   - **Smallest fix:** Always reject dates after `weekEnding`; allow `background` only when the date is before `windowStart`, after validating the ISO date.

7. **Should-fix — `web/scripts/verify-dist.ts:50-100`; `web/tests/e2e/issue.spec.ts:60-89`**

   - **What:** The distribution gate checks JSON shapes and counts, not identities or contents, and does not actually parse XML. It would accept copied issue payloads under several filenames, duplicate/wrong index rows, or the wrong RSS items if the count matched. Tests exercise only the singleton/newest issue and a zero-item feed.
   - **Why:** The second and third issue paths are generated correctly today, but the release gates do not establish that each permalink, JSON copy, archive row, feed item, and `pubDate` corresponds to the correct issue.
   - **Smallest fix:** Parse RSS as XML and compare exact GUID/date sets with published issues; compare each JSON file’s issue ID and evidence-ID set; compare the exact ordered archive index; add a fixture with two published issues and one newest draft.

8. **Should-fix — `web/src/components/Header.tsx:11-18,50-57,82-90`**

   - **What:** Except for Archive, navigation links remain page-local hashes. On `/issues/`, the brand and all hash links are dead; on a permalink, Thesis, Landscape, Scorecard, Evidence, and Method are dead.
   - **Why:** Archive and permalink routing works, but their primary navigation does not.
   - **Smallest fix:** On non-front routes, point standing-reference links to `/#…` and avoid preventing default when the target is not in the current document.

9. **Should-fix — `web/scripts/prerender.ts:137-150`**

   - **What:** Machine-authored `issue.read` is inserted directly into quoted meta attributes without HTML-attribute escaping.
   - **Why:** A future read containing a quotation mark can corrupt description and Open Graph/Twitter tags while the build remains green.
   - **Smallest fix:** Escape dynamic attribute values before head replacement.

10. **Should-fix — `docs/archive/2026-09-weekly-issue/gather-job-spec.md:114`**

   - **What:** The owner ritual names `verify:issue --write`, but only an npm script exists and npm arguments require the separator.
   - **Why:** Following the documented signing procedure will not reliably update the manifest.
   - **Smallest fix:** Change it to `npm run verify:issue -- --write`.

11. **Should-fix — `web/scripts/verify-issue.ts:181-218`**

   - **What:** The gate does not enforce the brief’s maximum eight items per lane or the model’s 140-character read and 110-character headline limits.
   - **Why:** A malformed Tuesday draft can pass every named gather gate despite violating the page contract.
   - **Smallest fix:** Add those bounds to the per-issue/per-item checks.

Overall verdict: **do not merge**.  
The missing specified functionality, absent evidence receipts, and fail-open governance gates are blockers.
