# Company search

## Scope and authority

The owner requested company search on November 2, 2026. This unit adds a search field near the
top of the front page, inside a native "Search for a company" disclosure. Keeping the field
collapsed initially preserves the first visible market event on a phone. It searches the existing
74-supplier roster by name, ticker and aliases
already recorded in `contracts/market.json`. Matching is case-insensitive and ignores punctuation
and extra spaces. All words must match the same name, ticker or registered alias.

Selecting a result opens the existing supplier record, including dated events and source links.
The result count counts each supplier record once even when it appears in multiple domains.
Separately tracked business segments retain their own named result. An empty
query shows no result list. A clear button resets the query and keeps focus on the field. An empty
result explains that only the tracked roster is searched. Search never implies complete coverage
or changes a fact, date, source, certification or supplier classification.

This is client-side search with no service, package, credential or recurring cost. Broad event-text
and evidence search and ownership/funding navigation remain separate backlog work. This visible
change needs owner review of a preview before production under the repository deployment policy.

## Acceptance

Check name, case, ticker, registered alias, whitespace and punctuation matching, and a query that
matches nothing. At 1440px and 390px, verify keyboard operation, clear/reset, result count,
opening Varonis with its original announcement and source, dialog Escape/focus return, no page
overflow and no JavaScript errors. Capture full-page production and local renders at both widths.
Run the repository's required `npm test` in OrbStack. Do not push or deploy from this unit.

## Verification

Implemented with no data or dependency changes. The search uses the existing supplier dialog.
The daily-status browser assertion now selects its named disclosure, since the hero contains two
disclosures; its underlying coverage assertion is unchanged.

Actual full `npm test` in the OrbStack dev VM passed on November 2: 384 data checks, 115 Python
pipeline checks, the certified build and all eleven output checks, and 44 browser checks. The
existing future-deadline browser case skips because this committed historical snapshot has no
`validUntil`. Lint reports its existing `ensure-test-browser.mjs` warning and no errors. Both new
company-search browser cases passed at 1440px and 390px, including keyboard opening, name/ticker/
alias results, Varonis primary-source link and original October 15 date, dialog focus return,
empty result, clear/focus and no page overflow or runtime errors. Four search data cases passed.

The isolated VM copy is `/tmp/smp-company-search-nov2`. It uses the existing VM dependency tree;
no package was installed. Its command was `npm test` from that copy's `web/` directory. Final raw
output and full-page production/local captures were copied into the owning checkout's ignored
`/Users/jessepike/.codex/worktrees/market-managed-runtime/sec-market/.ctx/company-search-2026-11-02/`.
The log is `npm-test4.log`; images are `production-1440.png`, `production-390.png`, `local-1440.png`
and `local-390.png`. Additional `local-fold-1440.png`, `local-fold-390.png`, `search-1440.png`,
`search-390.png`, `varonis-1440.png` and `varonis-390.png` show the initial screen and exercised
search/record states. `interaction-readback.json` records the one-result search and exact viewport
width at both sizes.

Both pairs of full-page renders were visually inspected. The visible source change adds the
compact search disclosure and its expanded field/results near the top; it preserves the existing
market views and the first market event inside the 390x844 initial screen. Production carries
newer collected data than the committed historical local fixture, so their figures, dates and
event ordering differ. This comparison does not claim equal data or that search is deployed.

No preview or production publication occurred in this unit. Owner preview review and the existing
exact-artifact production gate remain necessary. Broad event/evidence text search and company-type
navigation remain unfinished.
