# Research and design direction

Researched 2 October 2026. This is a standalone bake-off prototype, based on the working repository snapshot. The brief and product-core.md were read in full. Other contestants' work was not consulted.

## References

| Reference | Specific pattern observed | Take into this design | Leave behind |
|---|---|---|---|
| [Cloudflare Radar overview](https://radar.cloudflare.com/) | Persistent subject navigation, an explicit date range, scoped measures, and local links explaining each measure. | Keep the reporting window visible; let readers move between domains without traversing a long document. Put evidence access beside the fact. | Radar's many chart modules and global toolbars would overwhelm this much smaller dataset. No AI-answer box. |
| [Stripe's 2025 annual update](https://stripe.com/annual-updates/2025) | A short overview leads into named subjects and detailed supporting material. Financial numbers retain explanatory context. | A restrained introduction followed immediately by actual information. Use whitespace to separate tasks and keep period labels close to numbers. | The promotional voice, large marketing hero, and company-success narrative are unsuitable for a neutral supplier tracker. |
| [Linear's March 2026 interface refresh](https://linear.app/changelog/2026-03-12-ui-refresh) and [2024 redesign](https://linear.app/changelog/2024-03-20-new-linear-ui) | Consistent headers and controls, quieter navigation, and clearer separation between content and metadata. The changelog keeps dated entries individually addressable. | A quiet domain rail, shared controls, stable row structure, and chronological changes. One accent indicates interaction, never business performance. | No dark theme, app-like shortcut burden, decorative launch imagery, or animation required to understand a fact. |
| [Koyfin watchlists](https://www.koyfin.com/features/watchlists/) | Grouped company lists and configurable views allow many entities to occupy one useful workspace. | Search within the supplier universe, alphabetical rows, and a focused detail view. | Price tickers, red/green changes, rankings, investment framing, and a dense grid of mostly empty financial columns. |
| [Datawrapper's responsive table design](https://www.datawrapper.de/blog/new-table-tool-barcharts-fixed-rows-responsive-2) and [table guidance](https://www.datawrapper.de/blog/guide-what-to-consider-when-creating-tables) | Tables can switch to labelled records on narrow screens; fewer columns make comparisons easier. | Reflow the same supplier record on mobile. Keep evidence and dates usable by touch. | Horizontal table scrolling and sparklines without enough comparable history. Two quarterly figures do not justify a smooth trend line. |

These observations come from live web search and reading the linked pages. An attempted in-app visual inspection was unavailable because that browser surface was not enabled; no visual inspection of those reference sites is claimed.

## Proposed composition, before implementation

The design is a market desk with two jobs: read the latest recorded changes, then inspect the suppliers in a security domain. The first screen shows actual event text; a compact adjacent index shows the composition of the change record and filters it. These counts describe this collection, not the whole market.

```text
Brand                                  Changes   Suppliers   Coverage
The business of security.              Snapshot date
Short purpose line                     Source / coverage access
┌ What changed: most recent first ────────────┬ In this record ┐
│ Dated, sourced events                      │ Type filters   │
│ Read all changes                           │ + counts       │
└────────────────────────────────────────────┴────────────────┘
Explore a security domain                          Supplier search
┌ Alphabetical domain navigation ┬ Selected domain, scope and rows ┐
│                                │ Supplier | reported facts       │
└────────────────────────────────┴─────────────────────────────────┘
Coverage, collection status and limitations
```

On a phone the change index becomes a compact filter; domains become a native select. The full change record opens in an accessible dialog and every supplier is reachable without expanding twelve stacked sections. The prototype includes all twelve domains and all 74 suppliers.

## Visual plan

- Paper `#FFFFFF` for records; mist `#F5F7FB` for the working surface; ink `#202A3B` for content; slate `#58657A` for secondary text; blue `#365BCB` for actions; pale blue `#EDF2FF` for the selected state. No colours indicate a supplier's prospects.
- Manrope provides an open, contemporary heading and interface face. System sans-serif is the offline fallback. Use tabular numerals within the same family for financial facts, with no tiny monospace data labels.
- Content is left aligned. The desktop uses a 1200-pixel reading area, broad gutters, and a small number of large surfaces. The phone uses 18-pixel side margins and labelled rows. A 4-pixel spacing unit supports 12, 16, 24 and 32-pixel groups.
- The most distinctive element is the linked change index: actual records paired with a compact categorical count view. It serves navigation and reveals the composition of the evidence. It is not a decorative scorecard.

## Critique against the brief

An early idea used a large hero and four metric cards. That would spend the first screen describing the product instead of showing the market. The revised layout keeps the introduction short and gives that space to dated events. A chart comparing every supplier's latest growth was also rejected: periods and business scopes differ, and such a chart would invite a ranking the product is forbidden to make. The selected domain starts at Endpoint and XDR, the first domain in the declared data model; suppliers and domain navigation are alphabetical.

The page will state that the snapshot is dated, preserve the 30-day helper's inclusive boundary, distinguish press results from SEC filings, and describe missing revenue as a gap in this collection. No copy will claim that an absent figure proves the company does not disclose it.
