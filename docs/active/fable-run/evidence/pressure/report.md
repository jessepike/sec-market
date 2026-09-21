# T7-9 / SEC-054 — Platform pressure wording, visual review

This is a visible change: three rows in the Platform pressure table's "Buying in rather than
building" group read different sentences and show a different JUDGED date, and a new entry appears
at the top of `/corrections/`. Nothing else on the page moved except the site-wide "updated" date
stamp, which now reads 21 Sep 2026 instead of 20 Sep 2026.

## What changed, row by row

| Row | Acquirer | Target | Before | After |
|---|---|---|---|---|
| Protect AI | Palo Alto Networks | AI runtime (AI security) | "Cloud security absorbed into a hyperscaler. Watch what it does to the specialist gap." · JUDGED 17 Aug 2026 | "AI security absorbed into a platform vendor. Watch whether it survives as a product or becomes a feature." · JUDGED 21 Sep 2026 |
| CalypsoAI | F5 | AI runtime (AI security) | same as above · JUDGED 17 Aug 2026 | same new sentence · JUDGED 21 Sep 2026 |
| SurePath AI | F5 | AI runtime (AI security) | same as above · JUDGED 17 Aug 2026 | same new sentence · JUDGED 21 Sep 2026 |
| CyberArk | Palo Alto Networks | Identity | "Identity becomes a Palo Alto platform pillar. Capital, not customer spend." · JUDGED 17 Aug 2026 | unchanged |
| Wiz | Google | Cloud security | "Cloud security absorbed into a hyperscaler. Watch what it does to the specialist gap." · JUDGED 17 Aug 2026 | unchanged |

No row today falls outside the three cases the owner approved (D-75), so nothing was left
unreworded pending further owner wording.

## Screenshots

Captured with `capture.mjs` in this folder (adapted from
`docs/active/fable-run/evidence/baseline/capture.mjs`, since `web/scripts/shot.mjs` needs a Google
Chrome binary the OrbStack dev VM does not have). Crops only — the "Buying in rather than building"
pressure group, and the `/corrections/` page — at 1440px and 390px, before (`origin/preview` at
`f236360`) and after (this branch).

- `before-1440-pressure.png` / `after-1440-pressure.png`
- `before-390-pressure.png` / `after-390-pressure.png`
- `before-1440-corrections.png` / `after-1440-corrections.png`
- `before-390-corrections.png` / `after-390-corrections.png`

At both widths: the three reworded rows' body text and JUDGED date changed exactly as in the table
above; CyberArk and Wiz are pixel-identical to before. `/corrections/` gained one new card above the
2026-09-20 entry, dated 21 Sep 2026, with no "Issue ####" link (this correction has no `issueId`
since it corrects the standing Platform pressure table, not a published issue) and an "Approved by
Jesse Pike" line matching the existing entry's style. The 2026-09-20 entry's own markup is untouched.

## What did not change

A diff of the built `dist/index.html` between the `origin/preview` build and this branch's build,
normalized to one tag per line, contains exactly:

- the JS bundle's content-hashed filename (expected — the bundle's source changed)
- the site's "as of" / "updated" date, in the provenance rail, the header stamp, the masthead
  stamps line, and the JSON-LD `datePublished`/`dateModified`, all moving from 2026-09-20 to
  2026-09-21 (`LAST_UPDATED_ISO`, which the task asked to bump)
- the "How this works" paragraph's inline "updated September 20/21, 2026" date
- the three reworded rows' sentence and JUDGED date, once in the desktop table markup and once in
  the mobile stack markup (6 lines changed total, matching 3 rows × 2 responsive layouts)

Nothing else in `dist/index.html` differs. A parallel diff of `dist/issues/2026-w36/index.html`
contains only the bundle hash and the same as-of date bump — the issue's own content, including its
existing correction note, is byte-identical, confirming the new correction (no `issueId`) does not
attach to that issue's page or its `dist/issues/2026-w36.json` copy.

## Build and test evidence

`npm test` (lint, `test:data`, `build` with all `verify:*` steps, `test:e2e`) passes on this branch:
oxlint clean, 199 data tests passing (10 new: `tests/platform-pressure.test.ts`, plus one added to
`tests/corrections-data.test.ts`), `verify:issue`/`verify:prints`/`verify:dist` all PASS, and all 37
non-skipped Playwright e2e specs pass, including the pre-existing `tests/e2e/corrections.spec.ts`
suite unchanged.
