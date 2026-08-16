# Signals job

## Control

- **ID:** `SEC-MARKET-SIG-JOB-001`
- **Status:** authorized, not built
- **Authority:** D-28, 2026-08-16
- **Owner:** sec-market-lead
- **Worker:** sec-market-builder when implementation starts

## Job

Find public cybersecurity market events, decide which ones matter, and turn them into intelligence the site can show.

This is how Pulse stays current. Episodes 001 and 002 were one-time research. They are not a feed.

## What “done” looks like for the first cut

A named person or agent can, on a repeatable cadence:

1. pull public startup, funding, and M&A events;
2. keep the source, date, and a short excerpt for each event;
3. say what changed and why it matters, or say we do not know;
4. hand a human a publish packet for the site;
5. leave a trail so someone else can check the work.

The site then shows the new intelligence. A human still signs the market call.

## First feeds to stand up

| Feed | Why | First sources to try |
|---|---|---|
| Security startups and funding | Owner asked for a regular read on new companies | Public pages of a defined top-20/30 security-relevant VC set; Crunchbase/PitchBook-class public pages only where terms allow |
| M&A | Deals change who matters and what got absorbed | Public 8-Ks, issuer IR, and reputable deal notices |
| Public company prints | Already on the site; must stay current | SEC EDGAR and issuer IR |

Do not scrape a site that forbids it. Prefer official public pages, RSS, and filings. If a source is blocked, record the miss instead of inventing coverage.

## Hard rules

- Public, publishable sources only
- No made-up attribution
- No confidential ePlus data
- No investment advice
- No forced market call
- No auto-publish of the scorecard judgment

## First build slice

1. Write the top VC list and the M&A/filings source list.
2. Define the event record: who, what, date, source URL, excerpt, why it might matter, confidence.
3. Run one manual week of collection against that record.
4. Only then automate retrieval for sources that are allowed and stable.

## Stop

This file authorizes the job. It does not authorize a database service, a scraper farm, or unattended publication.
