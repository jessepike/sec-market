# Data-dense public intelligence products — research for SEC-MARKET-FABLE-001

Written 2026-09-20 for the Security Market Pulse scoring rubric and design spec. Studies Cloudflare
Radar, Our World in Data, FRED, Trading Economics, Public Comps and Sacra: what the first screen
commits to, how density is made scannable, how freshness and provenance are shown, what can be
cited or embedded elsewhere, and what each does badly.

## What I looked at and what I could not reach

I fetched pages directly with WebFetch and, where that failed, WebSearch, and I quote below the
lines that came from an actual fetch. Today is 2026-09-20.

Cloudflare Radar's own site, `radar.cloudflare.com`, returned HTTP 403 on every path I tried
(homepage, `/about`, `/reports`), including through a `r.jina.ai` proxy, which returned "Enable
JavaScript and cookies to continue." This is a client-rendered app that blocks non-browser
fetchers, not a temporary block. I could not render its live first screen this run, and what
follows about Radar's layout and visual density is **from general knowledge, not verified this
run**, flagged inline. What I could verify came from Cloudflare's own developer docs and blog,
which cover the API, license and section list solidly.

Our World in Data's homepage, `/data` catalog page and `docs.owid.io` all fetched cleanly. FRED's
homepage fetched cleanly; its API reference pages returned only navigation stubs with no
substantive text, so I could not confirm whether the FRED API key is free — unverified this run,
stated neither way. Trading Economics' homepage fetched cleanly; its two pricing pages
(`/api/pricing.aspx`, `/analytics/pricing.aspx`) returned only a payment-methods sentence with no
numbers, so the two API prices below came from a third-party comparison site (`apis.io`) dated
June 2026, not from Trading Economics itself, and are marked as such. Public Comps' homepage
fetched cleanly with real pricing copy; its `/dashboard` path 404'd, so I never saw an actual comps
table rendered. Sacra's homepage, pricing page and one company report page (Gumroad) all fetched
cleanly with real numbers.

## Findings per product

### Cloudflare Radar

Unverified, from general knowledge: the first screen is a world map plus global stat tiles
(traffic change, top attacked countries, notable outages), with navigation into Traffic, Attacks,
Routing, Email, Adoption & Usage and more; figures read as large sans-serif numbers with a
percent-change chip, and charts are interactive rather than static images.

Verified by fetch: Cloudflare describes Radar as "a hub that showcases global Internet traffic,
attacks, and technology trends and insights," built from Cloudflare's own network telemetry and
anonymized 1.1.1.1 resolver data — not third-party sources, so there is no per-number source line;
the brand itself is the provenance. Its section list has grown from the 2020 trio (Internet
Insights, Domain Insights, IP Insights) to add Certificate Transparency, Network Layer Security,
Adoption & Usage, AI Insights and routing-anomaly alerts. Freshness is near-real-time for some
feeds: route-leak subscribers get alerted "via email or webhook when such an event is detected."
The API is free — "Radar's API is free, allowing academics, technology professionals, and other web
enthusiasts to investigate Internet usage across the globe" — under a CC BY-NC 4.0 license, gated
by a scoped account token rather than open access, and Cloudflare also ships an MCP server over
the same data for natural-language queries. What it does badly, unverified: scope has grown by
accretion, and Cloudflare's own blog frames navigability as a running problem it keeps having to
redesign around.

### Our World in Data

The homepage leads with a plain mission line, "Research and data to make progress against the
world's largest problems," plus two scale numbers — 14,095 charts, 126 topic pages — right at the
top: the promise is a large curated corpus, not a live dashboard. Below sit featured articles,
short "Data Insights" posts each with one embedded chart, a "Key Metrics" row, Data Explorers, and
a full topic index; charts on the homepage are static previews linking to interactive versions, so
the home page is a table of contents into density rather than dense itself. Freshness shows as
relative time per post ("Yesterday," "4 days ago"), not a page-level date, and each chart carries
its own named source (e.g. "World Bank"). Licensing is the most prominent line on the site: "All
free: open access and openly licensed," and on the reuse page, "All visualizations, data, and
articles produced by Our World in Data are completely open access under the Creative Commons BY
license... provided the source and authors are credited." Every chart has a data-download button
returning CSV and JSON metadata, and the docs site lists four programmatic surfaces — Charts,
Tables, Indicators and Search APIs, plus a Python wrapper — while noting "these APIs are under
active development." What it does badly: the homepage blurs whether OWID is a publication or a
database, deliberately.

### FRED (Federal Reserve Economic Data)

The homepage opens with "Your trusted source for economic data since 1991" and a search box with
trending terms (GDP, CPI, unemployment) beneath it — the promise is lookup, not argument. Below
that: an "At a Glance" panel with three sparkline charts, a "Latest Releases" list of ten recently
updated series, and separate news and blog feeds. Freshness is explicit and granular per release —
"updated 15 hours ago," "updated 3 hours ago" — which matters given FRED's real publication lags
and revisions. Access channels advertised on the homepage include an Excel add-in, API docs,
mobile apps and embeddable widgets, but I could not fetch a quoted line on API pricing or key
requirements. What it does badly, directly visible: the layout is "text-heavy with minimal visual
hierarchy," navigation is "scattered across multiple menu levels," and the News/Blog and Latest
Releases sections effectively repeat each other on the same page. There is no single visible
"download the data" button on the front page — a reader has to drill into a specific release
first, the clearest case here of strong data undermined by an interface that hasn't kept pace.

### Trading Economics

The homepage centers on a live tabular block: rows for roughly a dozen major economies, columns
for GDP, GDP growth, interest rate, inflation, jobless rate, budget, debt/GDP, current account and
population — nine dense, monospace-aligned columns per country. Above it sits a conventional
financial-media nav and a scrolling list of dated news items. This is the most information-per-
pixel first screen in the set, because every cell is a single number in a fixed grid position, pure
lookup with no prose. Freshness shows at the article level but not next to individual indicator
cells, and I found no source citation on the indicator grid itself — Trading Economics presents
numbers as its own aggregated product rather than attributing each cell. Monetization is visible
everywhere ("DATA PLANS," "API GATEWAY"), but I could not get exact prices from Trading Economics'
own pages — only a payment-methods line and a trial-limits line ("trial users are limited to
100000 data points and 100 requests for data"). A third-party comparison site, dated June 2026,
lists a Standard tier at $149/month and Professional at $299/month billed yearly; **marked as
third-party, not fetched from Trading Economics directly**. What it does badly: the free tier has
essentially no source transparency, and pricing stays opaque until account creation.

### Public Comps

The homepage shows no actual comps data — it's a marketing page for a workflow, opening with
"Don't go through another SEC filing for SaaS metrics" and a "Go to our Free Dashboard" button,
then a four-step illustrated flow (Search → Visualize → Compare → Trace) using conceptual graphics
rather than live tables. The one idea worth taking is "Trace": you can "click on a bar chart and
see the underlying formula and data source" — provenance built into the interaction itself, not a
footnote. Sourcing is tied to SEC filings plus a named partnership for analyst estimates ("Zacks").
Pricing is fully published: Free ($0, basic metrics), Pro ($99/month, full comps tables, Trace,
CSV export), Enterprise (contact sales, adds API access and unlimited historicals). I could not
reach the actual dashboard (404) to see real table density or per-metric freshness. What it does
badly: the marketing page volunteers nothing about how current the underlying filings-derived data
is, which matters more here than elsewhere since SaaS metrics used for investing go stale fast.

### Sacra

The homepage is one value line — "The private markets research you need to be a better investor"
— a signup button, and six investor testimonials; no data table, chart or dated content before the
fold. This is the most editorial, least dashboard-like product here: Sacra sells analyst judgment
on named private companies (Gumroad, Beacon, WeWork are cited examples), pitched at "the depth
typically produced by hedge fund analysts, made accessible to a broader audience." A fetched
company report (Gumroad) shows the real pattern: large headline numbers up top ($12.18M revenue,
$100M valuation, $16.10M funding), then fixed narrative sections (Revenue, Valuation & Funding,
Product, Business Model, Competition, TAM Expansion, Risks). Sources are named inline down to the
method: "Sacra estimates that Gumroad hit $21M in revenue in 2023, up 96% from $11M in 2022,"
alongside a link to a primary filing dated February 22, 2024 — the clearest case here of telling
the reader, in the sentence itself, whether a number is fact or estimate. Most of the report sits
behind a "Standard membership required" gate after a short free excerpt. Pricing is a seat-and-
usage model: Standard $50/month (1 seat, 500 tasks), Pro $350/month and "Popular" (5 seats, 3,500
tasks), Platform $1,500/month (20 seats, 25,000 tasks), Enterprise custom; all tiers share the same
feature set and differ only on seats and a metered "tasks" unit. What it does badly: the homepage
gives almost no sense of what's inside before payment — no sample chart, no freshness signal,
nothing dated — so the whole trust burden sits on testimonials and covered-company names.

## Patterns that repeat across products

Products that are primarily a database (Radar, OWID, FRED, Trading Economics) put a search box or
a live table at the very top, not prose — the homepage functions as an index, not an argument.
Products that are primarily paid research (Sacra) or paid tooling (Public Comps) do the opposite:
homepages are almost entirely marketing copy, with dense content one click and usually one paywall
away.

Freshness shows two ways and never both at once in what I fetched: a relative timestamp on content
items (FRED's "updated 15 hours ago," OWID's "4 days ago") or an update-triggered alert (Radar's
route-leak notices). None of the six show a page-level "as of" banner the way a financial terminal
would — freshness lives at the level of the individual chart or release, not the page.

Provenance splits into three models. OWID cites an external named source per chart, because it
aggregates other institutions' data. Radar cites nothing per number, because the data is
Cloudflare's own telemetry — the brand is the source. Sacra and Public Comps cite a method per
number (estimate versus filing) because their value is judgment applied to messy primary sources,
so the reader needs to know which kind of number they're looking at. A weekly, single-author site
combining filings, funding data and a standing thesis needs Sacra's method-labeling more than
OWID's external citation, because the site is making a judgment call the way Sacra does, not
aggregating someone else's clean series.

Every product with an API treats it as its own product with its own page and pricing, never bolted
onto the same page as the human-readable content, and the free-versus-paid line for the API tracks
the free-versus-paid line for the human product in every case I could confirm. Only Public Comps'
"Trace" pattern makes provenance interactive rather than a static caption next to the number.

## What transfers and what does not

Transfers: OWID's per-chart named source, since this site already draws on funding databases and
vendor filings and a reader needs to know at a glance which claim came from where. Sacra's inline
method-labeling ("estimate" versus "filing" versus a named document) transfers directly and matters
more here than for Sacra, since the site's central mechanic — scoring a standing thesis holds,
weakens, strengthens or no-call each week — is itself a judgment call needing the same discipline.
FRED's practice of a freshness stamp next to the specific content unit, not just the page, fits a
weekly cadence ("signed Monday," "verdict posted Tuesday"). Trading Economics' fixed-grid table,
one row per entity with a consistent column set, is the right shape for comparing several vendors'
prints or deals side by side, since aligned columns read faster than prose.

Does not transfer: Radar's and FRED's institutional-scale data pipelines — a single author signing
one issue a week shouldn't try to look like a real-time dashboard, since it isn't one, and
pretending otherwise is a credibility risk the moment a reader checks the as-of date against the
real publish cadence. Trading Economics' opacity-until-signup pricing contradicts a site whose
differentiator is being evidence-first and named. Public Comps' and Sacra's seat- and task-metered
pricing assumes a team-sized buyer and a content library large enough to meter against — neither
exists yet for one weekly issue and a small archive, so that pricing shape would be premature.

## Design and product moves

1. Put a single, page-level "as of" line at the top of the front page and the issue page, next to
   the market-thesis verdict, so a reader can see how current the judgment is before reading a word.
2. Label every number in the weekly issue with its evidentiary kind, Sacra-style ("filing," "vendor
   disclosure," "our estimate"), so a reader can tell in the sentence whether a figure is sourced or
   judged.
3. Build a Public-Comps-style "trace" interaction on key figures — clicking a number in the market-
   call table reveals the source URL and the date it was pulled — so provenance is one click away.
4. Add a fixed-column comparison table (Trading-Economics style: one row per vendor or deal, same
   metric columns every row) for any section comparing more than three entities, so a reader scans
   instead of reading paragraphs.
5. Ship a `.csv` and `.json` export for the market-call history and each week's evidence table, via
   a direct URL suffix like OWID's rather than a separate download portal, so a reader or an agent
   can pull the numbers without asking.
6. State the data license on every exported file and on the page describing the export, the way OWID
   and Cloudflare both do explicitly, so a reader knows on sight whether they can republish a number.
7. Never hide pricing behind a signup wall once the site sells anything, unlike Trading Economics,
   since an evidence-first brand loses credibility the moment it asks for an account just to see a
   price.
8. Give the front page a search box or an index into past issues and past thesis verdicts before
   asking a first-time reader to read prose, since a returning reader's first instinct is to check
   what changed, not read the newest issue top to bottom.
9. Show update cadence on the front page itself ("signed weekly, most recent: [date]"), not just on
   the individual issue, since FRED's homepage shows that burying freshness one level down reads as
   staleness even when the content is current.
