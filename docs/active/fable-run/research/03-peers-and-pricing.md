# T1-3: Security-market peers and the price umbrella

## What was researched and what could not be reached

Studied nine security market intelligence and research products: Return on Security, CB Insights, PitchBook, Gartner, Forrester, Cyberstarts, Momentum Cyber, and weekly newsletters (Software Analyst Cyber Research, Strategy of Security, Venture in Security, Decryption Digest).

Return on Security's subscribe page did not display pricing details when fetched (2026-09-20). Software Analyst Cyber Research, Strategy of Security, and Venture in Security Substack pages do not publish pricing on their home pages; pricing or paid tiers may exist on the subscription flow itself but were not accessible by fetching the public pages.

Cyberstarts is a venture capital firm, not a research publication; included for ecosystem context.

## Findings per product

**Return on Security.** Publishes a weekly 5-minute briefing ("Your Weekly Cyber Market Intelligence Edge") on cybersecurity funding, M&A, and market trends. For: security leaders, founders, investors. Free or paid tier exists; pricing not published on public pages as of 2026-09-20.

**CB Insights.** Platform for enterprise market intelligence, company data, deal tracking, and analyst briefings. For: enterprise corporations, investment firms. Published pricing: $50,000–$265,000+ per year depending on team size and modules. Median contract value $47,000/year per Vendr. No free plan (Vendr, 2026; easyvc.ai, 2026).

**PitchBook.** SaaS platform for venture capital, private equity, M&A data, deal sourcing, and financial analysis. For: VC/PE professionals, investors. Published pricing: $20,000–$124,000 per year across 114 verified buyer transactions; $15,000–$100,000+ per user depending on seats and modules. Does not publish official list; custom quotes only (pitchbook.com/pricing returned HTTP 403; Slidegenius, 2026; easyvc.ai, 2026).

**Gartner.** Enterprise analyst firm providing research, advisory, and consulting on technology and security. For: enterprise CTOs, security leaders, executives. Published pricing: $25,000–$60,000 annually for technology-specific research (1–5 named users); $100,000–$500,000+ for enterprise-wide subscriptions with advisory and consulting. Does not publish official list; pricing varies by negotiation and term length (Vendr, 2026).

**Forrester.** Enterprise analyst firm providing research, advisory, and leadership boards. For: enterprise security leaders, executives. Published pricing: $20,000–$50,000 per seat for research memberships; $15,000–$40,000 per seat for Leadership Boards; $5,000–$15,000 per day for consulting. Does not publish official list; discounts less common than at Gartner (Vendr, 2026; SalesHive, 2026).

**Momentum Cyber.** Investment bank and market map operator. CYBERscape 4.0 is a comprehensive taxonomy of 1,000+ cybersecurity companies across 62 sub-segments (including 300+ AI security companies). Publishes monthly market reviews free in partnership with Cyber Defense Magazine. Pricing for premium access not published (momentumcyber.com/cyberscape-4-0/, 2026-09-20; GlobeNewswire, 2026).

**Software Analyst Cyber Research (SACR).** Weekly newsletter on cybersecurity landscape for leaders, operators, and investors. Publishes to 17,000+ subscribers. Free newsletter available; paid analyst subscription offered but pricing not published on Substack public page (softwareanalyst.substack.com/, 2026-09-20).

**Strategy of Security.** Weekly newsletter analyzing the business and strategy of cybersecurity. Written by Cole Grolmus. Free newsletter exists; paid tier may exist but pricing not published on public page (strategyofsecurity.com/, 2026-09-20).

**Venture in Security.** Free weekly Substack newsletter by Ross Haleliuk covering the business side of security (startups, ecosystem, VC, markets). Published pricing: free (ventureinsecurity.net/, 2026; LinkedIn, 2026).

**Decryption Digest.** Daily cybersecurity briefing for SOC analysts and CISOs. Delivers threat intelligence, patch priorities, vendor moves, vulnerability priorities, Sigma rules, WAF configs, IOCs. Published pricing: free for 50,000+ security professionals, no credit card required (decryptiondigest.com/, 2026-09-20).

**Cyberstarts.** Venture capital firm investing $2M–$25M+ from seed through growth in cybersecurity companies. Flagship Sunrise Program provides operational support and CISO network access. Not a research publication; included for ecosystem context (crunchbase.com, 2026; startupintros.com, 2026).

## Patterns across products

**Enterprise tier ($20K–$500K+).** Gartner, Forrester, CB Insights, and PitchBook do not publish official pricing. All require direct sales engagement and offer custom quotes based on seats, modules, and negotiation. Annual commitments standard. Security-specific research within Gartner and Forrester sits in the mid-range ($25K–$60K for small teams; $100K–$500K+ enterprise-wide).

**Weekly newsletter tier (free to $50+/month).** Software Analyst Cyber Research, Strategy of Security, and Venture in Security operate as free Substack newsletters with optional paid tiers (Substack standard model: free + paid supporter option, typically $5–$20/month). Return on Security follows a similar pattern but pricing specifics not published.

**Free daily/market tier.** Decryption Digest (daily briefing, free, 50,000+ users) and Momentum Cyber's CYBERscape 4.0 (free market map, monthly reviews free via partner) both operate as free public goods. Momentum Cyber monetizes through investment banking and research services, not the map itself.

**Venture finance tier.** Cyberstarts (VC firm, not a publication) provides market maps and deal flow insight as part of investor relations, not as standalone products sold to other publishers.

None of the studied products publish a signed weekly scorecard of their own past market calls.

## What transfers to a small weekly evidence-first site

**Transfers:** Free newsletter entry point (Substack or equivalent) with optional paid supporter tier ($5–$15/month) works at scale (17,000+ subscribers for SACR, 50,000+ for Decryption Digest). Public market maps and ecosystem resources (Momentum Cyber's free CYBERscape, Decryption Digest's free briefing) demonstrate that free-with-optional-paid is viable for market intelligence at the weekly cadence. Named sources and signed judgment (which none of the competitors prominently display) is a differentiation opportunity.

**Does not transfer:** The $20K–$500K enterprise tier depends on sales teams, long contract cycles, and multi-seat licensing. The investment in Gartner/Forrester/CB Insights is about access to analysts and custom research, not about publishing. A solo, single-author weekly publication cannot replicate that economics. PitchBook's data-integration economics (which drives its pricing) do not apply to a narrative-driven editorial product.

## Concrete moves for design and product

1. **Do publish a scorecard of past calls in an always-visible "thesis history" section** so a returning reader can see at a glance which calls held, weakened, strengthened, or were wrong. None of the competitors publish this; the site already scores weekly, so rendering the history is a product move that costs nothing and differentiates sharply.

2. **Do surface the evidence trail (source links + quoted lines) on the first screen of each assertion**, not buried in footnotes or a separate research section. Decryption Digest ships Sigma rules and IOCs with every post; this site can ship the URL and the quoted line that supports each market claim.

3. **Do offer a free Substack entry point with an optional $8–$12/month paid tier**, matching the proven Substack conversion (5–15% of free subscribers typically convert to paid). Return on Security, SACR, Strategy of Security, and Venture in Security all use this model; it works at scale and requires no payment infrastructure beyond Substack.

4. **Do not attempt to sell data modules, multi-seat licenses, or enterprise access** until the publication has 10,000+ weekly readers and demonstrable influence on market conversations (category, pricing, deal flow). CB Insights and PitchBook succeeded in that tier because they own proprietary data; a narrative publication's moat is audience and voice, not data.

5. **Do publish a downloadable "market thesis" PDF quarterly**, versioned and dated, so a reader can cite the publication's position over time. Gartner and Forrester use versioned reports; a solo publication can do this at a much lower cost per issue and signal rigor.

6. **Do include a "this is what I got wrong last quarter" section in a quarterly review**, signed by the author. Visible error correction is nearly absent from competitor publications and builds trust sharply. Returns on Security, SACR, and Forrester all claim to track their calls, but none show the evidence publicly.

7. **Do create a weekly "market signals" API endpoint (JSON) with title, date, URL, source, quoted evidence, confidence level (hold/strengthen/weaken/no-call), and category (funding/M&A/product/capital)**. AI agents and researchers can then cite the publication programmatically. None of the competitors offer this; it costs little to build and makes the publication machine-readable.

8. **Do design the first screen to show one standing thesis statement and the current posture (hold/strengthen/weaken)** without scrolling, so a new visitor understands what the site argues in five seconds. Gartner and Forrester hide their actual thesis in prose; this site can show it as a card on the home page.

9. **Do not gate the issue archive behind payment** (SACR, Return on Security, and Venture in Security all publish freely). Gartner and Forrester gate archives; a solo publication's advantage is transparency and discoverability. Free archives drive SEO, discovery, and citation.

10. **Do measure "time to next market move" (how many issues before a call changed)** and publish it alongside the thesis history. None of the competitors track this metric. It answers "how responsive is this analyst to market drift?" and is a leading indicator of publication quality.

## Pricing umbrella (free to enterprise)

| Tier | Product | Cadence | Free | Price (Published) | Audience |
|------|---------|---------|------|------------------|----------|
| Free daily | Decryption Digest | Daily | Yes | Free forever | SOC analysts, CISOs |
| Free monthly | Momentum Cyber CYBERscape | Monthly reviews | Yes | Free | Investors, founders, security teams |
| Free weekly | Venture in Security | Weekly | Yes | Free | CISO, founders, investors |
| Freemium weekly | SACR | Weekly | Yes | Paid tier not published | Security leaders, operators, investors |
| Freemium weekly | Strategy of Security | Weekly | Yes | Paid tier not published | Cybersecurity professionals |
| Freemium weekly | Return on Security | Weekly | Likely | Not published | Security leaders, founders, investors |
| Paid monthly (Substack est.) | Weekly newsletter (typical) | Weekly | No | ~$10–$15/month estimate | Subscribers |
| Paid annual (small team) | PitchBook | Continuous | No | $20K–$124K/yr | VC/PE professionals |
| Paid annual (small team) | CB Insights | Continuous | No | $50K–$265K+/yr | Enterprise corporations, investors |
| Paid annual (small team) | Gartner security | Continuous | No | $25K–$60K/yr | Enterprise security teams |
| Paid annual (small team) | Forrester security | Continuous | No | $20K–$50K/yr | Enterprise security teams |
| Paid annual (enterprise) | Gartner enterprise-wide | Continuous | No | $100K–$500K+/yr | Fortune 500 enterprises |
| Paid annual (enterprise) | Forrester enterprise | Continuous | No | $80K–$400K+/yr | Fortune 500 enterprises |
| Investment bank | Cyberstarts (VC) | Deal flow | N/A | $2M–$25M check sizes | Portfolio companies |

## Differentiation: where this site is unique and where it is not

**Unique:** A signed, solo-authored weekly publication that scores its own thesis publicly against real market events, with an always-visible history of past calls and their accuracy. Gartner and Forrester do analyst calls and estimates; they do not publish a weekly verdict or scorecard. SACR and Venture in Security publish analysis but do not score a standing thesis. Return on Security publishes briefings but does not show a call history. Decryption Digest publishes threat briefings, not market thesis work.

**Not unique:** Being free or mostly-free. Six of the nine studied products offer free entry points. Substack free + paid model is standard and expected.

**Not unique:** Weekly cadence. SACR, Strategy of Security, Venture in Security, Return on Security, and the typical security newsletter all publish weekly.

**Not unique:** Covering security market moves (funding, M&A, vendor, capital). That is the core market intelligence category; everyone does it.

**Not unique:** Publishing on the web. Enterprise analyst research is published to PDFs and gated dashboards; a web publication is standard for newsletters and markets analysis.

**Differentiation opportunity (not yet occupied):** Publishing a thesis scorecard and showing what the author got wrong—with evidence. None of the competitors do this visibly. The site already has the data (weekly postures across five domains); rendering that history and adding quarterly error analysis would be a sharp differentiator and would build trust faster than anything else on this list.

---

**Read-only note:** This file documents the state of the security market intelligence market as of 2026-09-20. Pricing and publication details reflect what was discoverable on public-facing pages at that time. Return on Security, SACR, Strategy of Security, and Venture in Security pricing specifics could not be verified by fetching; URLs either did not display pricing or were behind Substack subscription flows. Momentum Cyber's premium access pricing is request-only (not published).
