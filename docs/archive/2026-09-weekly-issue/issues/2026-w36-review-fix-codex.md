## 1. Earlier-finding disposition

- Codex 1 — closed — vendor lens implemented by `b4413b5`; e2e coverage added by `702edc3`.
- Codex 2 — closed — receipts added by `dd0f120`; the two invalid excerpts were correctly restored by `838775a`.
- Codex 3 — partially closed — pre-write validation and historical comparison landed in `9a108a3`, but Finding 1 below leaves the lock bypassable.
- Codex 4 — closed — `2a9041c`.
- Codex 5 — closed — strict dates and feed-date rejection landed in `ce4fba8`.
- Codex 6 — closed — `ce4fba8`.
- Codex 7 — partially closed — identity checks landed in `a371d99`, but Finding 3 remains.
- Codex 8 — closed — `1fcdfac`.
- Codex 9 — closed — escaping landed in `a691212`; multiline OG/Twitter replacement was repaired by `1deaa09`.
- Codex 10 — closed — `ee39532`.
- Codex 11 — closed — `462f3d9`.
- Claude 1 — closed — `e6a493f`.
- Claude 2 — closed — `b4413b5` and `702edc3`.
- Claude 3 — closed — `1fcdfac`.
- Claude 4 — closed — `ce4fba8`.
- Claude 5 — open, nit — [DomainBoard.tsx](/Users/jessepike/code/projects/sec-market/web/src/components/DomainBoard.tsx:94) still removes domain names from the heading hierarchy. Smallest fix: include the domain name in the card heading.
- Claude 6 — open, nit — [vercel.json](/Users/jessepike/code/projects/sec-market/web/vercel.json:1) still has no explicit slash/404 policy. Smallest fix: configure and test canonical directory routing.

## 2. New or remaining defects

1. **Blocker — [verify-issue.ts](/Users/jessepike/code/projects/sec-market/web/scripts/verify-issue.ts:58)** — The append-only gate trusts `origin/preview` first, even when that ref resolves to the commit being verified; on a direct `preview` build it therefore compares the manifest with itself. When no candidate resolves, lines 393–399 merely warn and pass. A published issue and its hash can consequently be rewritten together without a historical comparison. Smallest fix: compare against a guaranteed ancestor/PR merge base distinct from `HEAD`, and fail closed on protected-branch builds when no prior manifest is available.

2. **Should-fix — [verify-issue.ts](/Users/jessepike/code/projects/sec-market/web/scripts/verify-issue.ts:123)** — The numeric-token regex treats digits embedded in names as figures. The real draft’s valid `M12` reference triggered this false positive and was rewritten as “Microsoft’s venture fund” at [2026-w36.ts](/Users/jessepike/code/projects/sec-market/web/src/data/issues/2026-w36.ts:72). Smallest fix: reject matches adjacent to letters while retaining explicit `M`/`B` suffixes.

3. **Should-fix — [verify-dist.ts](/Users/jessepike/code/projects/sec-market/web/scripts/verify-dist.ts:67)** — Dist identity remains incomplete: issue JSON bodies are not compared with their source issues, archive rows check only `id/status`, and RSS `pubDate` is validated only syntactically rather than against its GUID’s issue. The regex extractor also is not an XML parse. The helper fixture at [dist-fixtures.test.ts](/Users/jessepike/code/projects/sec-market/web/tests/dist-fixtures.test.ts:11) never runs the writer or verifier, so it cannot catch emitted-output disagreement. Smallest fix: compare complete expected payloads, exact GUID-to-date mappings, parse XML, and run the real dist pipeline against the multi-issue fixture.

4. **Should-fix — [lens.spec.ts](/Users/jessepike/code/projects/sec-market/web/tests/e2e/lens.spec.ts:5)** — Lens e2e coverage hard-codes week-36 vendors and asserts only the self-reported “Showing N of M” text, not the rendered item/card set. When a second issue lacks those vendors, the lane half becomes a zero-match test and can pass vacuously. Smallest fix: derive a nonzero slug from the newest issue and assert the actual visible item/card identities or counts.

## 3. Vendor lens

- No additional implementation defect found: [VendorLensProvider.tsx](/Users/jessepike/code/projects/sec-market/web/src/context/VendorLensProvider.tsx:15) activates only after hydration, preserves unknown slugs, round-trips and clears the URL, and leaves the no-parameter React/SSR markup unchanged. The runtime follows `latestIssue`, so a second issue does not break filtering; its test coverage does, as Finding 4 describes.

**Verdict: do not merge.**  
The append-only publication-history gate must be made non-self-referential and fail-closed first.
