# Intake note — category compression and platform ecosystem thesis

**Provenance:** exported by Jesse from chat sessions on 2026-09-09 and routed here by the advisor on the same day from the sandbox holding pen at `/Users/jessepike/code/sandbox/ideas/sec-category-compression`, which will be deleted once each destination has confirmed receipt.

**Confidence:** thin. Nothing in this directory has been checked against this project's evidence contract. Every vendor claim, revenue figure, acquisition, tier and hypothesis is an unverified input until a gather packet validates it or rejects it.

## What is here

- `ecosystem-intelligence-v3.md` — the most developed document. Ecosystem map with tiers, deep dives on Cloudflare, Fortinet, SentinelOne, Varonis and Rubrik, a segment-behaviour table, a twelve-item hypothesis register, a vendor scorecard field list and a source register of about twenty URLs.
- `market-futures-and-opportunity-map.md` — the market thesis in short form: barbell market, six continuous outcome loops, the four scarce assets (context, control, distribution, assurance).
- `platform-ecosystem-watchlist-v1.md` — the corrected ecosystem map with expansion theses per ecosystem.
- `category-compression-and-future-outcomes.md` — the forecasting argument: categories are artifacts of human constraints, so where a boundary exists only because humans cannot do adjacent tasks continuously, AI compresses it.
- `platform-convergence-map-v1.png` — a drawn map of the same structure.

## How it maps to Pulse

Two different kinds of thing are in here and they should be handled differently.

The vendor-level claims are gather input. They carry a source register, so they can enter the normal weekly loop and be validated, attributed and printed to the scorecard, or dropped. Cloudflare, Fortinet, SentinelOne, Varonis and Rubrik each already appear in `web/src/data/prints.ts` or `evidence.ts`, so these are candidate updates to existing cards rather than new coverage.

The structural lens is a judgment layer Pulse does not currently carry: the barbell shape, category compression into outcome loops, the ecosystem rather than the company as the unit of analysis, and the tier map. Under `SEC-MARKET-001` a machine may propose that and only a named person signs it. It is offered here as a proposed market read, not a call. The twelve hypotheses in `ecosystem-intelligence-v3.md` are the most reusable part and fit the method as a register of things the weekly loop could accumulate evidence for or against.

The "autonomous update loop for Codex" section in the v3 document is not a proposal for this project. Pulse already has its operating model and a proposed durability spec; that section is preserved for provenance only.

## Not authorized by this note

No scorecard change, no market-read change, no new lane, no data-model change. Triage is tracked as SEC-041 in `BACKLOG.md`.
