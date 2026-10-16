# T1-8 — Thesis history inventory in the repository

**Output path:** `docs/archive/2026-09-weekly-issue/fable-run/research/08-thesis-history-inventory.md`

Read items: `decisions.md` (full), `web/src/data/edition.ts` (append-only editions array), `web/src/data/market.ts` (market call + context), `web/src/data/meta.ts` (constants), `docs/archive/2026-08-signals/signals-week-2026-08-16.md` (desk run, not published), `docs/archive/2026-08-signals/signals-week-2026-08-19.md` (desk run, owner-signed), `web/src/data/issues/2026-w36.ts` (first published issue, signed by Jesse Pike 2026-09-19).

Could not read: `docs/archive/2026-08-gate-chain/episode-002/` packet (permission or archive status); `decisions.md` fully read; market call and posture data fully read.

---

## Chronological thesis event table

| Date | Event | Verbatim quote | File path, line | Rendered on live site | Signed by person |
|------|-------|---|---|---|---|
| 2026-08-15 | Episode 002 question authorized | "Is the current infrastructure and AI-capex cycle producing a measurable leading signal for increased cybersecurity demand, over what horizon, and which security domains are likely to capture it first?" | decisions.md D-9 | Unknown | Owner: "agree. proceed." |
| 2026-08-15 | Episode 002 decision accepted | "Infrastructure and hyperscaler investment remain broadly accelerating. A stable infrastructure-to-security lag is `NO-CALL`... Domain momentum differs, but infrastructure causality and 'which domain captures first' remain `NO-CALL`." | decisions.md D-10 | Unknown | Independent review passed |
| 2026-08-16 | First published edition (no postures moved from baseline) | Six domains published with postures, tags, but no horizons. Network-sase: PREPARE. Data-ai-security: PREPARE. Cloud, identity, secops, ai-runtime: INVESTIGATE/WATCH. | web/src/data/edition.ts lines 26–42 | Yes (current state) | No person signature in edition record |
| 2026-08-17 | Postures dated with horizons (no move) | "Domain postures are now dated, with the decision horizon each one governs... No posture moved." | web/src/data/edition.ts lines 43–95; decisions.md D-45 | Yes (as historical record in edition array) | No person signature |
| 2026-08-28 | Evidence class changed, posture held | "No posture moved. The AI runtime rationale is now carried by filings rather than by funding rounds." Palo Alto/F5 AI acquisitions added with SEC filing source class. | web/src/data/edition.ts lines 96–149; decisions.md D-59 | Yes (as historical record in edition array) | No person signature |
| 2026-09-03 | Weekly issue model approved; intent v1.2 accepted | "approve the intent v1.2 text as written." Weekly issue becomes unit of product; autonomous agents gather and draft only; named person signs judgment. | decisions.md D-62, D-63 | Unknown (intent not on page) | Owner: "approve the intent v1.2 text as written" |
| 2026-09-19 | First published weekly issue (2026-w36); thesis verdict recorded | "Verdict: holds... Evidence of demand strength at the infrastructure/platform layer, not a change to the standing infrastructure-to-security lag call... medium confidence." | web/src/data/issues/2026-w36.ts lines 258–275 | Yes (issue rendered at https://securitymarketpulse.com/issues/2026-w36/) | Yes, signed by Jesse Pike, 2026-09-19 |

---

## Thesis statement and confidence

**Headline (market.ts, line 29):** "Infrastructure is running ahead. Security is splitting, not booming."

**Subhead (market.ts, line 30–31):** "Use infrastructure activation as an account qualification trigger — not as proof of a broad cybersecurity boom. A stable lag is still not measurable."

**Stated confidence (market.ts, line 53–54):** "High on infrastructure acceleration. High that 2025 security budgets did not follow. Medium on the 2026 domain split. No-call on a stable lag. High that platforms are acquiring AI security ahead of any disclosed revenue."

**Falsifiers, verbatim (market.ts, lines 44–49):**
- "Claiming a market-wide cybersecurity boom or a stable 0–8 quarter lag."
- "Reading headline security growth without stripping acquisitions."
- "Treating the 2025 Wiz or CyberArk announcements as this month's demand signal."
- "Reading AI-security acquisition prices as evidence of AI-security demand. The filings say the acquired revenue was not material."

**Change triggers that would move the call (market.ts, lines 61–66):**
- Realized security-budget growth and rebound in security share of IT
- Organic acceleration across a majority of comparable security vendors
- Expansion from AI pilots into consequential production workloads
- A registered infrastructure impulse followed by a registered security response under fixed cohort rules

---

## Gaps and missing dated events

The repository does not hold:
1. **Episode 001 thesis** — D-3, D-5, D-8 reference it but the frozen packet and its decision rationale are not in `docs/active/` or `docs/archive/2026-08-gate-chain/episode-002/`; D-8 states it "did not test the original core thesis" and was "reclassified as thematic validation," so no standing Episode 001 verdict exists.
2. **Dated domain-posture reversals** — All three editions (2026-08-16, 2026-08-17, 2026-08-28) show "no posture moved." No edition shows a posture changing from one tag to another, so no falsification or thesis reversal event is recorded as published.
3. **Unsigned weekly desk runs** — The two desk runs (2026-08-16, 2026-08-19) were compiled but marked "not for publication" and "signed by owner 2026-08-20" respectively. Neither desk run is rendered on the live site; only the final signed issue (2026-w36, 2026-09-19) publishes.
4. **Issue verdicts before 2026-w36** — No prior issues exist. The standing thesis has been tested against only one published weekly issue so far (2026-w36, which renders "holds, medium confidence").
5. **Dated confidence state changes** — Confidence is stated uniformly as "medium" on all six domains in editions (lines 2026-08-16 through current). No edition shows confidence moving between trust and distrust.
6. **Timestamp on published verdict records** — The only published thesis verdict (`weThink.verdict`) is in 2026-w36 (lines 262–268), dated 2026-09-19 by the signature; earlier desk runs carry verdicts but are unpublished.
