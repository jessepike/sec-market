# Signals job

## Control

- **ID:** `SEC-MARKET-SIG-JOB-001`
- **Status:** authorized, not built
- **Authority:** D-28, 2026-08-16
- **Owner:** sec-market-lead
- **Worker:** sec-market-builder when implementation starts

## Job

Find public cybersecurity startup events, decide which ones matter, and turn them into intelligence the site can show.

This is how Pulse stays current. The site today is one frozen research edition about infrastructure spending. The startup section is a new feature on that same site, not another research paper.

## First slice — startups only

Owner direction 2026-08-16: do not work M&A yet. First question: where do new security startups and their funding show up in public, and which sources can we actually use?

M&A and public-company prints stay parked.

## What “done” looks like for this slice

A research packet that names the best public sources for new security startups, what each source actually gives us, and how we can collect it without breaking terms.

Catalog is done. Next: one cheap collection packet from the allowed first-week sources so we can judge value. No custom browser scraping, click-through skills, or collectors until that packet is useful in a real conversation or on the site.

Do not scrape a site that forbids it. Prefer official public pages, RSS, and filings. If a source is blocked, record the miss instead of inventing coverage.

## Hard rules

- Public, publishable sources only
- No made-up attribution
- No confidential ePlus data
- No investment advice
- No forced market call
- No auto-publish of the scorecard judgment

## First build slice

1. Research the top public sources for new security startups and funding. Write the catalog. **Done:** [startup-source-catalog.md](startup-source-catalog.md) (`SEC-MARKET-STARTUP-SRC-001`), lead reviewed.
2. Pick the first 8–10 we can actually collect from. **Done:** first-week set in the catalog.
3. Define the event record: company, what they do, date, round if any, source URL, excerpt, why it might matter.
4. Run one cheap collection packet from those sources. **In progress.**
5. Judge value from the packet. Only if it is useful, consider light automation of allowed pages. Custom browser scraping stays parked.

M&A source work is parked.

## Stop

This file authorizes the job. It does not authorize a database service, a scraper farm, or unattended publication.
