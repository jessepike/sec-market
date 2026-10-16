---
id: SEC-MARKET-AUTO-002-P2
version: 0.1
state: in build
created: 2026-10-16
parent: SEC-MARKET-AUTO-002
decisions: D-88 (auto-promote data), D-89 (certified tier), D-90/D-97 (byline), D-91 (filed events), D-93 (weekly issue retired), D-96 (cadence), D-100 (wording)
authority: owner, 2026-10-16: "promote. then continue until complete"
---

# Phase 2: production renders the certified tier

## Goal

The public site shows the tracker, not the frozen legacy snapshot. SEC figures for the certified filers are labelled as re-derived from SEC filings and carry the date of the last certified change. Everything else keeps its own source and date and is labelled as not re-checked automatically. All run-status and diagnostic panels leave the page.

## Changes

### Release (web/scripts/app-release.mjs)

- New release kind `certified`, selected when `refreshPublication.json` has `snapshotMode: "certified"`. Production and preview both build the tracker app. No diagnostic root and no `/published-preview/`.
- Build gate: `certify-gate.ts --at-certification` evaluates the committed proofs at their own certification time and re-derives every claim from the build inputs (drift check). Wall-clock freshness is enforced by `certified-refresh.yml` every 4 hours, not at build time, because data commits happen only on change (D-96).
- `web/published-app` stays in the repo unchanged as the legacy record. It is no longer the production root.

### Dates

- `runStatus.lastChecked` becomes the SEC refresh date. The laptop collector is retired, so the earlier `min(collector, SEC)` rule would freeze the event window at 2026-10-14.
- New `src/data/tracker/certification.ts`: `certifiedAt` (from `certifiedCoverage.json` `checkedAt`), certified supplier ids, certified-event test, and the contract's `notCertified` list.
- `verify-tracker.ts` funding/ownership event gate checks the retained record, not the display window, so a moving window cannot fail the build.

### Page

- Remove: diagnostic banner, "Latest attempt" kicker, "Last complete data refresh" lines, `RunStatus` failure list, `RefreshCoverage` section, header "Data refresh: not established".
- Add, in the `#overview` slot: one certification line. "SEC figures for N public companies are re-derived from their SEC filings and pass a 100% check before they publish. Last certified change: <date, UTC>. Checked every 4 hours. Other figures keep their own source and date and are not re-checked automatically." Link to the method and to `/certified-coverage.json`.
- Header, rail and masthead show "SEC figures certified <date>".
- Supplier record: a line stating which of its facts are certified. SEC-sourced events of certified suppliers carry "SEC filing, date checked". Growth chart note names the non-SEC suppliers.
- Feed and footer: link the certification receipt instead of the legacy coverage report.

### Method page

- Rewrite "How this is built" for the two tiers, the 4-hour check, the 100% gate, publish-on-change, the reproducibility limit (D-100), the not-certified list, and filed-event rules (D-91).
- Byline and interests statement (D-90, D-97).

### Filed events (D-91)

- New event type `late-filing` for NT 10-K and NT 10-Q, in the generator and the verifier, counted under restructuring and distress.
- 8-K Item 2.03 events quote the first sentence of the filing's Item 2.03 section, which states the amount and purpose, instead of the generic label.

### Workflows

- `promote-certified.yml` gets a daily schedule.
- `certified-refresh.yml` and `promote-certified.yml` allowlists unchanged.

### Governance docs

- AGENTS.md production section: add the D-88 data-only auto-promotion path; mark the D-73 weekly-issue exception retired.

## Not in Phase 2

Email (D-92 workstream, separate), a second revenue oracle, removal of retired workflows (awaiting owner).
