# Security Market Pulse: a market desk

The front page opens with dated changes to the companies behind a security program. Readers can then move into any security domain, find a supplier, and inspect its reported figures and source documents without navigating twelve stacked tables.

## Information architecture

The first desktop screen contains the snapshot date, the four newest records, their sources, a categorical filter with counts, and the entrance to supplier exploration. The phone shows three recent records and a compact filter. The complete 25-record change window is available through “Read all”: 17 events plus eight latest-quarter SEC filings, using the existing inclusive 30-day rule for 27 August–26 September 2026. Results announcements and filings remain separate records, explicitly labelled.

Below that, one persistent workspace holds all twelve domains and all 74 suppliers. Endpoint and XDR, the first domain in the declared model, is the initial selection. Domain navigation and supplier lists are alphabetical. Search spans the whole supplier set; the full list is paginated. A supplier dialog holds latest and prior revenue, company metrics, funding, ownership and its recorded events. Collection details stay accessible from the introduction and footer.

## Visual system

Manrope, cool white surfaces and a pale blue-grey background create a quiet reading environment. Dark slate carries facts; blue identifies links and selected controls. Colour never expresses supplier performance. Financial figures use tabular numerals and the original value strings. Broad margins separate the two reading tasks; compact rows keep facts, periods and evidence together. On phones the rows reflow, and the domain rail becomes a native select.

## Hard constraints

| Requirement | Implementation |
|---|---|
| Facts only | Supplied factual text; no scores, forecasts, stances, rankings or invented owner commentary. Categories and counts describe the embedded record. |
| Sources and dates | Linked figures open their source documents directly. Events carry dates and document links. Revenue keeps its fiscal period, quarter-end and reported date; full records preserve prior periods and other metrics. |
| Honest gaps | Missing financial data is described as missing from this collection. Coverage reports 28 distinct suppliers with access or confirmation gaps; duplicate failure entries are grouped. Unsupported claims inside diagnostic text are not displayed. |
| Light only | Explicit light colour scheme, also checked with a dark operating-system preference. |
| Desktop and phone | Rendered at 1440 and 390 pixels with no horizontal page overflow. Visible targets meet 24 × 24 pixels. Native buttons, selects and dialogs support keyboard use, Escape and return of focus. |
| Identity and disclaimer | No owner byline in the hero. “Not a news site and not investment advice.” remains visible in the footer. |
| Real data | Embedded JSON extracted from tracker domains, suppliers, events, referenced evidence records, EDGAR facts and collection state. All twelve domains, 74 suppliers, 95 historical events and the full recent-change list are included. No fact values were rounded or rewritten. |

## Validation and limits

The supplied host screenshot command failed because Chrome aborted in the sandbox (`SIGABRT`; process cleanup reported `EPERM`). Rendering succeeded with the already-installed Playwright Chromium in the OrbStack dev VM. Both full-page images and first-screen images were opened and visually inspected. The final initial page is 1,866 pixels tall at 1440 and 2,439 pixels at 390. Screenshots sit beside this file as `shot-1440.png`, `shot-390.png`, `shot-fold-1440.png` and `shot-fold-390.png`.

Interaction checks covered every domain, all suppliers through pagination, search and empty results, all change filters, 25 source links in the complete change record, supplier details, dialog keyboard dismissal and focus restoration. No page errors occurred. The data also rendered with external requests blocked and a fallback font. Linked documents were not independently revalidated; the prototype preserves the supplied snapshot and does not imply that September's collection ran in October.

With more time, I would test whether practitioners prefer the chronological opening or choosing their domain first, then add shareable supplier/domain URLs and a screen-reader review. The interface copy is drafted for external readers and is ready for the manager's required Claude Code writing-cleanup pass before publication. This submission changes no production files and is not deployed.
