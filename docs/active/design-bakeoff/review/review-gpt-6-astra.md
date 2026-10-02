# Security Market Pulse: blind design review

| Design | First screen ×3 | Look ×3 | Density ×2 | Constraints ×2 | Phone ×1 | Weighted total /110 |
|---|---:|---:|---:|---:|---:|---:|
| A | 8 | 8 | 8 | 3 | 5 | 75 |
| B | 9 | 7 | 9 | 3 | 6 | 78 |
| C | 6 | 9 | 6 | 4 | 6 | 71 |
| D | 7 | 9 | 7 | 9 | 8 | 88 |

The total is first screen ×3 + look ×3 + density ×2 + constraints ×2 + phone. Clear hard-constraint breaches cap A, B and C below 5 for constraints.

This assessment uses the supplied desktop and phone screenshots, including all four full phone pages, and the prototypes' HTML, CSS, JavaScript and embedded data. Interaction findings come from code inspection; this is not a completed browser accessibility audit. All four embed the same 74 supplier records and 95 event records across 12 domains. That establishes consistency between these prototypes, not independent verification against the original tracker or external source documents.

## A

The six event totals and adjacent twelve-month timeline give the desktop reader a broad picture of recorded activity before asking them to inspect individual companies. The warm background, restrained blue marks and consistent card edges make several kinds of information coexist without looking like separate applications. The alphabetical public-supplier table adds revenue, growth, periods and company metrics in a useful comparison structure.

The introduction and empty “Owner’s read” consume too much of the phone opening: the first event starts around 690 pixels down, and the domain browser sits behind the event feed, timeline, funding, ownership and public-company sections. The supplied full phone page is 11,352 pixels tall, the longest of the four. The timeline conveys collection volume more readily than supplier business conditions, so its prominent desktop space produces less decision value than B’s reported-growth comparison.

Constraint findings in [A’s prototype](/Users/jessepike/code/projects/sec-market/docs/active/design-bakeoff/review/designs/A/index.html):

- In “The twelve domains,” `renderDomains()` prints “Median reported revenue growth,” including Endpoint and XDR’s +26%, without a source link or stated constituent periods. This breaches section 4.2. An arithmetic median is not automatically a judgment, but presenting mixed-period company figures as a domain summary needs an explicit derivation and scope that this view does not provide.
- The same section promises “the one fact that best describes where it stands on the record.” That is interpretive wording about supplier standing, even though `oneFact()` actually follows a fixed field-selection rule. It conflicts with section 4.1; describe the displayed fields without claiming they establish standing.
- In “Latest collection run,” the text claims SEC filings are “complete for all 16” quarterly filers. The embedded SEC set has 14 entries, and the prototype itself identifies Commvault and JFrog as “SEC series not yet collected” through `REGISTRY_NOT_IN_FACTS`. This is an internally contradicted completeness claim under section 4.3.
- In `renderTimeline()`, clickable circles have radius 4, giving 8-pixel targets, and have neither keyboard focus nor a keyboard activation handler. This clearly breaches section 4.5. The small supplier buttons and inline figure links also lack a guaranteed 24-pixel target.

The blue marks do not encode good or bad performance, and the supplier default is alphabetical. The reserved owner slot contains no market opinion or owner name.

## B

“Reported revenue growth, latest quarter” is the most useful first-screen comparison in the set: named suppliers share a common scale, with filled and hollow marks separating the latest and preceding quarters. Its alphabetical default and reader-selected “By value” option provide comparison without imposing a supplier ranking. Alongside the dated event list, it lets a security leader see both reported business performance and corporate changes in one desktop screen.

The lower “Board” gives almost every line similar visual weight, with small monospaced metadata competing against company facts. It is dense, but the twelve expanded desktop domains approach the spreadsheet-like presentation the brief asked to leave behind. On the phone, collection details occupy a conspicuous block before any event, while the useful growth chart is pushed below the entire event feed; the full page is 6,090 pixels tall.

Constraint findings in [B’s prototype](/Users/jessepike/code/projects/sec-market/docs/active/design-bakeoff/review/designs/B/index.html):

- `usd()` rounds SEC values with `toFixed(2)` for billions and `toFixed(1)` for millions. The supplier detail’s “Reported revenue by quarter, from EDGAR” and sparkline tooltip therefore turn CrowdStrike’s embedded $1,010,178,000 into $1.01B. Section 4.7 explicitly prohibits different rounding; the method text’s claim that figures are otherwise shown as reported does not hold here.
- `windowEvents()` uses only `D.events`. Consequently “What changed” exposes 17 events and omits the eight latest-quarter SEC filing records available in the embedded data and shown by A, C and D. The count accurately describes B’s event subset, but it does not satisfy the complete “what changed” list required by section 4.7. Those filings should remain distinguishable from results rather than silently disappearing.
- The prior-quarter dots in `renderDots()` are non-focusable spans with mouse-only tooltip access and no source link. A reader must open a supplier record and then its prior-quarter source. The chart therefore fails section 4.2’s one-click source requirement for those plotted figures and does not provide equivalent keyboard access to their exact values and periods.
- `.src a`, `.name` and several inline fact links have no 24-pixel minimum; the source-link styling specifies a 12-pixel font with 1.6 line height and no padding. These controls breach section 4.5’s minimum target size.

The chart’s monochrome marks avoid sentiment colouring. “By value” is an explicit reader choice, so it is not a prohibited default ranking.

## C

The teal palette, strong type hierarchy and generous separation make this the most distinctive visual identity. The domain browser keeps the twelve categories available while showing one manageable supplier list, and the selected AI-security panel separates revenue, company metrics, funding and ownership into labelled facts. Direct source links and adjacent periods are considerably easier to understand than a generic row of unexplained numbers.

The oversized “What security companies reported” introduction delays the useful content, especially on the phone, where the results card begins around 540 pixels down. The three headline counts do little to explain supplier conditions, and the selected domain has no search facility for someone arriving with a particular company in mind. After that compact browser, the complete 25-record change list becomes another long reading task; the full phone page is 7,995 pixels tall.

Constraint findings in [C’s prototype](/Users/jessepike/code/projects/sec-market/docs/active/design-bakeoff/review/designs/C/index.html):

- Domain facts created by `fact()` use ordinary inline anchors inside `.fact-value`, which is ultimately styled at 13 pixels with 1.38 line height and no target padding or minimum height. Single-line figures such as AI security → Palo Alto Networks → “+34%” therefore fall below the explicit 24-pixel target requirement in section 4.5. The separate “Source” links have a 27-pixel minimum, so the defect is specifically in the figure links.
- The hero’s “25 dated records,” “6 reported results” and “3 acquisition events” do not visibly state their window alongside the figures. “30-day record” exists as an accessible label, and the adjacent results card says “Last 30 days,” but the counts need their own visible period to make section 4.2 unambiguous.

The preview explicitly declares its selection rule as “Two latest results and two latest other events.” I do not count that disclosed, mechanical sample as an unsupported claim about which events matter most. Domains and suppliers default to alphabetical order, figures retain their embedded wording, and the dark footer is a local colour treatment rather than a dark page theme.

## D

“What changed” gives each event enough space to be read, with the company, event type, source organisation and source date held in a consistent structure. The domain browser then provides a clear next action through supplier search, an alphabetical list and a record button, while the full event list remains available in a dialog. This produces a 2,439-pixel default phone page without discarding the underlying records.

The opening gives a readable account of recent changes but a relatively narrow market picture: two leadership items and an acquisition occupy most of the phone screen, with no visible comparison of reported business figures. On desktop, the large event card and separate filter rail consume space that could show some supplier evidence sooner. In the default Endpoint and XDR panel, Microsoft Defender and Sophos get “Ownership source available” instead of the useful parent or ownership fact already present in their records.

Constraint findings in [D’s prototype](/Users/jessepike/code/projects/sec-market/docs/active/design-bakeoff/review/designs/D/index.html):

No clear section 4 breach was established in the inspected default states or rendering code. `changesDialog()` retains all 25 records and distinguishes 17 events from eight filings; `supplierFact()` preserves the embedded figure wording, periods and direct source links. The domain and supplier lists are alphabetical, the event list is chronological, blue indicates controls rather than good or bad performance, and the native dialog supplies a sound basis for keyboard interaction.

The default “Endpoint and XDR” selection is explained in the coverage dialog and does not claim superiority. Collection incompleteness is available through the opening “Sources & coverage” control and stated in the lower coverage section, although a short visible qualifier beside the snapshot would communicate it better. The score of 9 reflects strong inspected compliance, not certification of every expanded state.

## Winner and runner-up

I would choose **D**. It best combines readable facts, clear paths into the records and a manageable phone page, while requiring fewer corrections to the hard constraints. Its main remaining design problem is substantive: the opening needs more evidence of supplier business conditions.

**B is the runner-up.** Its growth comparison does the best job of answering the market question on the first desktop screen. The dense board, phone ordering and concrete data and accessibility defects keep it behind D overall.

## What to borrow for D

- From A, borrow the compact event-type totals with an explicit time window. Keep filings separate from results and link each total to the matching records; do not import the unlinked domain medians.
- From B, borrow the common-scale, alphabetical latest/prior growth comparison. Give each mark an accessible exact value, reporting period and direct source, and let the reader choose any value sort.
- From C, borrow the clearly separated labels for reported revenue, company metrics, funding and ownership. Use those labels to surface the actual ownership fact in D’s sparse rows, and preserve C’s quiet treatment of collection status.

## Five fixes D needs before it ships

1. **Rework the first screen around both changes and supplier evidence.** Reduce the desktop event card’s height and place a compact, sourced growth comparison beside it or bring the selected domain’s first rows into view. On the phone, reduce introductory space and the event preview so the first supplier row appears on the first screen, as section 6a requires; use the existing full-list control to retain access to every change.
2. **Show the useful fact when revenue is absent.** Replace “Ownership source available” with the sourced parent or owner and its as-of date. In the default domain this means showing Microsoft as Defender’s parent and the recorded Sophos ownership information; keep collection gaps explicitly separate from claims about company disclosure.
3. **Make collection status visible beside the snapshot.** Add a quiet “Collection incomplete” link next to “26 Sept 2026,” retain the detailed dialog, and keep the long explanation out of the opening. A checked date alone should not look like complete coverage.
4. **Rebuild against every section 6a data requirement.** Retain computed growth to one decimal, dated company metrics and ownership facts with the missing-date build gate, named segment parents, derived status counts and the generated `/tracker.json`. Preserve original reported values in their evidence records, and keep the distinction between the 17 events and eight filing entries explicit.
5. **Complete runtime and visual acceptance at both widths.** Verify every domain, supplier search, pagination, type filter and dialog for overflow, source access, keyboard operation, focus restoration and 24-pixel targets. Preserve section 6a’s self-hosted fonts, stable desktop layout, hidden-sort-button keyboard fix and archive-tagline fix during the rebuild; the supplied screenshots and code review do not establish those production checks.

All four supplied default phone screenshots fit their captured width without visible horizontal spill, but that does not prove every interactive state is free of page overflow. None puts a supplier-browser row on the first phone screen. I treat that shared section 6a carry-forward requirement as a mandatory rebuild fix rather than retroactively treating it as a section 4 breach.
