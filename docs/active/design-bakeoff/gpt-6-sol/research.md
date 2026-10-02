# Design research for Security Market Pulse

Research reviewed on October 2, 2026. These are interface patterns, not sources for market facts. The prototype's market facts come from the repository tracker and its linked evidence records.

## References and useful patterns

- [Cloudflare Radar overview](https://radar.cloudflare.com/) and [Data Explorer](https://radar.cloudflare.com/explorer): a broad dataset becomes navigable through a stable set of subjects, a visible date range, and a focused view for each subject. Its report index also separates recent reports from the deeper data surface. I take the clear scope and time frame, plus the idea of moving from overview to detail. I reject a wall of mini charts: our sources are sparse and heterogeneous, so continuous chart lines would imply comparability we do not have.
- [Cloudflare Radar reports](https://radar.cloudflare.com/outage-center/reports): dates and subject labels make a large archive scannable. I take this pattern for a chronological disclosure list with source access on every entry. I reject report tiles for each item; the 30-day list is a factual ledger and should scan faster than cards.
- [Stripe 2025 annual letter](https://stripe.com/annual-updates/2025): one large opening statement gives a reader a way into dense material, then the page reveals more detail. I take its visual hierarchy and deliberate whitespace. I reject the promotional narrative and giant standalone number because this site cannot turn selected figures into a machine-authored market conclusion.
- [Linear changelog](https://linear.app/changelog): dates, concise headlines, and a persistent content rhythm make a long stream readable. I take the dated stream and restrained separators. I reject the long editorial summaries and algorithmic priority treatment: the tracker must show the complete 30-day window without machine-selected importance.
- [Koyfin watchlists](https://www.koyfin.com/features/watchlists/): stable columns and user-controlled grouping help people compare many companies. I take the explicit domain selector and alphabetic supplier order. I reject a finance-terminal default view and rank-style sorting, which would be noisy for security leaders and would imply judgment.
- [Financial Times Visual Vocabulary](https://github.com/Financial-Times/chart-doctor/blob/main/visual-vocabulary/README.md): chart form should follow the relationship in the data. This tracker has unlike measures across public and private firms, so text led rows with period and source are more truthful than a common-axis growth chart. A chart can be added later only for genuinely comparable series.

## Direction before building

Palette: cloud white `#F7F9F8`, paper `#FFFFFF`, deep ink `#183136`, quiet text `#5A7073`, tidal teal `#086D71`, line `#DCE8E6`. Teal marks navigation and source access; it never codes company performance.

Type: Plus Jakarta Sans for headings and controls, IBM Plex Sans for facts and running text. The visual signature is the open, large headline beside a compact dated disclosure rail. The rest uses one consistent row rhythm.

At 1440 pixels, the opening is two columns: context at left, recent disclosures at right. The domain browser follows as a narrow subject selector beside one full supplier list. At 390 pixels, these become a single column, and the domain selector becomes a native select control. Alignment stays left throughout.

The design spends its visual emphasis on the date-led disclosure rail. The supplier browser remains quiet so source, period, and gaps are easy to read. A muted collection-status disclosure is visible without leading the page.
