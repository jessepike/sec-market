# Company search stays visible

## Brief specification

Keep the existing company search available in the page's opening header without an expand/collapse step. Render the existing semantic search landmark, label, input, conditional clear button, help text and matching results directly. Preserve the current name, ticker and alias matching, record-opening behavior, result count, empty state, keyboard operation and Escape/clear behavior. Do not add auto-focus, a keyboard popup, sticky viewport behavior, navigation, a service, dependencies, data, or supplier-roster changes.

The search input must be visible on first page load at desktop (1440px) and phone (390px) widths, without clicking. Keep the label visible on desktop and available to assistive technology on phone. At both widths, verify search behavior and ensure the document does not overflow horizontally. Keep Varonis's dated record and source URL assertions.

## Implementation and evidence

The disclosure element and its summary were removed. The existing search landmark, visible desktop label, input, clear button, helper text, match count, results, and empty state now render directly. The mobile layout keeps the input visible and keeps its label and helper text available to assistive technology. No search behavior, source data, roster, dependency, service, or navigation changed.

The browser case checks the search landmark and labeled field on the first page load at both 1440px and 390px, before interaction. It retains name, ticker, alias, Varonis date/source URL, keyboard activation, Escape, clear/refocus, empty result, no-overflow, and phone-layout coverage.

Verification ran in the OrbStack dev VM using the existing dependency tree. `npm test` passed, including lint, data tests, 115 pipeline tests, the certified build, and 44 browser tests (one skipped). Lint reported one existing warning in `scripts/ensure-test-browser.mjs` about assigning to a caught exception. The local build's certified gate passed 80/80 against the committed fixture. `SMP_LOCK_BASE_URL=none` kept the build offline; no live SEC certification or source fetch ran. A focused rerun of the company-search and hybrid browser cases passed 4/4.

Visual captures are in ignored scratch at `.ctx/always-visible-search-2026-11-02/`: production and local full-page captures at 1440px and 390px, plus first-screen captures at both sizes. Production was captured from `https://securitymarketpulse.com/` on November 2 and shows the November 2 actual publication. The local preview is `http://127.0.0.1:38263/`; it shows the committed October 21 build fixture. Their figures and records differ, so the visual comparison is limited to layout: the local preview keeps the search field visible in the page header on both screen sizes without a click, while the production page has the prior collapsed/absent search presentation. The local run does not represent November 2 production data.
