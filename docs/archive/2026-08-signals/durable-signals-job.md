# Durable signals job

## Control

- **ID:** `SEC-MARKET-SIG-OPS-001`
- **Status:** mapping — lead reviewed; M&A catalog lead reviewed
- **Authority:** D-33
- **Owner:** sec-market-lead

## Job

Design how Pulse stays current every week without a hero pull.

Path: gather public signals → synthesize → human check → post to the site.

This is an operating model. It is not a build.

## In scope

- Cadence (what runs weekly vs only when something material happens)
- Jobs and who does them (gatherer, synthesizer, human checker, poster)
- What can be durable first from the startup easy-set (Return on Security + Cybersecurity Ventures + a few VC pages)
- How M&A joins later as a second feed
- What “post” means on a static site (update data, open a review, then ship)
- What stays human: the market call, first-screen headlines, conflicting amounts

## Out of scope

- `web/`, Vercel, GitHub sync (other session owns that)
- Building collectors, scrapers, browsers, or schedulers
- Auto-publishing the scorecard judgment
- Databases or production infrastructure

## Output

`docs/archive/2026-08-signals/signals-operating-model.md`
