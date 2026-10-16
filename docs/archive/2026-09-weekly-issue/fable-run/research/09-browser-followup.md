# Browser follow-up: Cloudflare Radar and rendered pricing pages

Captured with Playwright's bundled Chromium (no Google Chrome channel available in the
OrbStack dev VM) using a desktop Chrome user agent, at 1440x900 and 390x844, waiting for
network idle plus a settle period. Screenshots and DOM text dumps are in
`docs/archive/2026-09-weekly-issue/fable-run/evidence/reference/`. No login, form submission, email entry, or
CAPTCHA-solving was attempted anywhere.

## What loaded and what was blocked

Cloudflare Radar's homepage and its Application Layer Security inner page both rendered
fully at both viewport sizes, with real chart data. Return on Security's homepage,
sponsorship page, upgrade/backer page, and its separate data product ("The Signal," plus
its pricing page and its MCP-server marketing page) all rendered publicly with real
numbers. The Information's `/subscribe` page rendered fully once I waited for `load`
rather than `networkidle` (its trackers never go idle). Platformer's homepage rendered,
but its actual price sits inside a client-side Ghost "portal" overlay; clicking the
Subscribe link did not surface readable price text on the page, so I did not chase it
further with more clicks. Latent Space and Software Analyst Cyber Research subscribe
pages are plain Substack email-capture boxes with no visible price. SemiAnalysis is
fully blocked: both `/` and `/subscribe` returned HTTP 403 with a "Confirm you are
human" challenge page, and I did not attempt to pass it.

## Radar findings

The first screen commits to one hero panel: a "Traffic trends" line chart (Total &
HTTP bytes) with a "Protocols" donut breakdown beside it, both governed by a single
global "Worldwide" location selector and one "Last 7 days" date-range control in the
page's top-right corner — there is no per-chart date picker. Below the hero the layout
becomes a three-column card grid (Traffic, Adoption & Usage, Last observed outage; then
Security & Attacks, 1.1.1.1 Resolver, and a text-only "Last observed outage" style
panel; then TLD popularity, Domain popularity, Internet services popularity), closed
out by one full-width "Top browsers & user agents" chart before the footer. On the
1440px viewport before any scroll, only the hero panel and the top few pixels of the
second row are visible. On the 390px phone viewport before scroll, the entire screen is
controls and chrome — hamburger menu, "Overview" heading, the "Worldwide" and "Last 7
days" selectors each on their own full-width row, one promo banner, and just the top of
the Traffic trends chart; no data below the fold is visible yet.

A real finding from the full-page capture: several below-the-fold charts (Mobile vs.
Desktop, Layer 3/4 and Layer 7 attack types, DNS query type, TLD/Domain/Internet-service
popularity, Top browsers) were still rendering as grey loading-skeleton bars in the
screenshot, taken more than two seconds after network idle — these clearly lazy-load
on scroll or visibility rather than all painting at once.

No chart carries a visible "last updated" or freshness timestamp anywhere I checked, on
either page. Freshness is implied only by each chart's own x-axis, which ends at the
current date ("Sep 13" through "Sep 19," the capture date). Source and citation are not
shown inline either; the only place either appears is behind each chart's own action
menu. Every chart title has two small icons next to it, with tooltips "Share this..."
and "More actions...". I clicked "More actions..." on the Traffic trends chart and it
opened a menu with exactly four items, quoted verbatim: "Explain with AI," "View in Data
Explorer," "Generate citation," and "Notify me of traffic anomalies or Internet
outages." There is no direct "download PNG," "download CSV," or "embed" action in that
menu — the closest things to export are the raw-data explorer link and the citation
generator.

Quoted caption lines pulled straight from the DOM: "Bytes transferred over the selected
time period" (Traffic trends), "Insight into HTTP requests distribution" (Traffic
card), "Insight into adoption and usage of key protocols" (Adoption & Usage),
"Internet disruptions observed in analysis of Cloudflare traffic" (Last observed
outage), and on the inner page, "Relative change from previous period" and "Layer 7
attack volume trends over time." The only sitewide attribution text on either page is
"© 2026 Cloudflare, Inc." in the footer, next to links for Privacy Policy, Terms of
Use, Disclosure, Trust & Safety, Trademark, and Support — no per-chart or per-dataset
licence string appears anywhere in the rendered text.

The palette is restrained: two data hues (a dark navy and a lighter cyan/teal) carry
almost every chart, with a single Cloudflare-orange accent reserved for the small "→"
link-out arrows next to card titles, one promo-banner headline, and the sidebar's
active-item highlight. The inner page's WAF/DDoS donut adds orange as a genuine third
data colour, which is the most I saw anywhere. I checked computed font-family on five
percentage figures (72.9%, 60.9%, and others) and on two AS-number labels (AS27725,
AS112 Project); all of them resolve to the page's base font, `system-ui, sans-serif` —
Radar does not use monospace anywhere I sampled, not even for numbers or identifiers.

## Pricing table

| Publication | Tier | Price | What it buys | URL | Quoted line |
|---|---|---|---|---|---|
| Return on Security | RoS Backer, monthly | $12.00/month | Voluntary support, no extra perks | returnonsecurity.com/upgrade | "RoS Backer $12.00 /month ... No extra perks, just a shared belief that this work should exist in the world." |
| Return on Security | RoS Backer, annual | $120.00/year | Same, discounted | returnonsecurity.com/upgrade | "17% cheaper than subscribing monthly" |
| Return on Security | RoS Backer, one-time | $250.00 once | Symbolic one-time support | returnonsecurity.com/upgrade | "This one-time boost goes beyond support, it plants a flag." |
| The Signal (ROS's data platform) | Free | $0/month | Weekly dashboards, 180 AI lookups/day | signal.returnonsecurity.com/pricing | "Free $0/month ... Explore the market" |
| The Signal | Pro | $199/month | Full company/investor data, exit scoring, native MCP, 400 AI calls/day | signal.returnonsecurity.com/pricing | "Pro $199/month Full market intelligence + AI-native access" |
| The Signal | Enterprise | Custom | Bulk export, included API, dedicated support | signal.returnonsecurity.com/pricing | "Enterprise Custom Programmatic access & support" |
| The Signal | API add-on | $79/month | REST access add-on, available on Pro | signal.returnonsecurity.com/pricing | "$79/MO ... Available on Pro" |
| Return on Security | Sponsorship | no rate published | Newsletter ad placement, quoted by email | returnonsecurity.com/sponsorship | "Package options and the onboarding process can be made available by emailing sponsorships@returnonsecurity.com." |
| SemiAnalysis | — | no public price rendered | Blocked by a Cloudflare human-check wall on both `/` and `/subscribe` | semianalysis.com | — |
| The Information | Pro | $749 first year, $999/year renewal | AI-powered search, 60+ org charts, 12+ proprietary databases | theinformation.com/subscribe | "The Information Pro $749 $999 Annually ... 12 Proprietary databases" |
| The Information | Annual | $399 first year, $499/year renewal | Journalism, 8+ newsletters, charts library, TITV show, app | theinformation.com/subscribe | "Access to articles, briefings, newsletters, and events. Billed $399 now. Renews annually at $499 until canceled online." |
| The Information | Young Professional (30 or under) | $225/year for 2 years, then $399/year | Same access as Annual | theinformation.com/subscribe | "Billed $225 each year for 2 years, $399 annually after." |
| Platformer | Paid | no public price rendered | Price sits behind a client-side Ghost portal overlay that a click did not surface | platformer.news | — |
| Latent Space | Paid | no public price rendered | Substack email-capture box only, no tier shown | latent.space/subscribe | — |
| Software Analyst Cyber Research | Paid | no public price rendered | Substack email-capture box only, no tier shown | softwareanalyst.substack.com/subscribe | — |

Return on Security's full paid-product lineup, since it is the closest peer: a
voluntary newsletter "Backer" tier at three price points ($12/mo, $120/yr, $250 once,
no extra perks either way); a separate data product, The Signal, with a free company
lookup tier, a $199/month Pro tier, a custom Enterprise tier, and a $79/month API
add-on on top of Pro; and a sponsorship page with no published rate card — only a
"contact us and we'll quote you" line. I found no separate paid "reports" product; the
free Data Methodology and Market Eras pages are editorial content, not a paid report
line.

## Takeaways for a dense, light-theme, evidence-first weekly site

Radar governs freshness with one clock, not many: a single global date-range control
sets every chart at once, and recency is read off each chart's own x-axis rather than a
"last updated" badge repeated on every card. That is a lower-chrome way to signal
freshness than badging every widget, and worth copying.

The per-chart action menu is not an export menu the way I expected — no direct
download or embed option — it is "Explain with AI," "View in Data Explorer," "Generate
citation," and an anomaly-alert subscribe. That is a citation-first, alert-first
pattern, which fits an evidence-first weekly better than a generic download button
would.

Radar's visual restraint is real and measurable, not just impression: two data hues
plus one brand accent, and literally no monospace anywhere, including on AS numbers and
percentages. Density does not require a busy palette or a technical typeface to read as
rigorous.

The one peer with a genuine paid data product, Return on Security's Signal, prices its
serious analytical tools (exit-readiness scoring, consolidation signals, forecasting)
at $199/month behind a Pro tier while keeping basic company and investor lookups free,
with a $79/month API add-on on top. That is a usable reference point if a paid data or
API tier is ever considered.

Most of the newsletter peers checked here render nothing useful to an anonymous
browser: SemiAnalysis is fully walled off, Platformer's real price is hidden behind a
client-side overlay, and two more show only an email box with no tier or price. The
Information and Return on Security are the exceptions — both are fully transparent
about price to a first-time visitor. Any peer-pricing comparison the site publishes
should say plainly which numbers were actually visible versus which had to be inferred
or left blank.
