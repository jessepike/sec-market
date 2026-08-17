# Overnight ledger — launch hardening

State file for the autonomous continuation loop. Every cycle reads this first and
updates it before ending. Keep it short and factual: what is done, what is running,
what is next, and what a human must decide.

| Field | Value |
|---|---|
| **Branch** | `pulse/launch-hardening` |
| **Goal** | Make https://securitymarketpulse.com hold up under a first public share |
| **Owner decisions pending** | Enable Web Analytics in the Vercel project settings (one toggle, not an agent's to make) |

## Standing rules

- Never invent a market figure, revenue number, ARR, funding amount, date, or company
  fact. Every claim traces to a real cited source. This outranks everything else.
- Do not modify `intent.md` or `.claude/rules/`.
- Builds run in the OrbStack dev VM, never on the host.
- Nothing merges to `main` until it passes a clean build, the Playwright suite, and an
  adversarial review. Deploy is local → GitHub → Vercel, commit email
  `jesse@keatingpike.com`.
- Cheaper models for mechanical and research work; top tier for adversarial review.
- Leave the tree clean at the end of every cycle.

## Done

| # | Item | Commit | Evidence |
|---|---|---|---|
| 1 | Static prerendering at build time | `9aaf386` | `dist/index.html` 1,103 → ~118,000 bytes; headline, prints, tempo, activity, and all 72 evidence records present as real text; no hydration warnings |
| 2 | Discoverability layer | `786188d` | OG/Twitter/canonical tags, `og.png` verified 1200×630 at 54KB, JSON-LD + `sitemap.xml` generated at build from `meta.ts`, `robots.txt`, Vercel Analytics mounted, reader CTA (`NextEdition`) |
| 3 | Polish pass | `197a000` `354d39e` `003ac24` `d7a1ebf` `2d55b19` | Dead components and the inert `artifactLinks` stub removed; accessibility fixes and a mobile horizontal-scroll bug; recharts code-split out of the initial bundle; stale smoke-test assertions repaired; orphaned signals data flagged to the backlog |

| 4 | Wave 2 verification | — | Independent clean-build check PASSED all 9 items. Adversarial review returned CLEAN on fabrication, overclaiming, correctness, and privacy; it simulated Vercel CI in a clean room (`git archive` + fresh install, `CI=1 VERCEL=1`) and all five build steps passed. Nothing blocked the merge. |

Bundle after the polish pass: initial JS **699KB → 311KB** (gzip 205KB → 94.5KB), with
recharts moved into a lazy 390KB chunk. The polish agent correctly refused `React.lazy`
here — it is unsupported by `renderToString` and reproducibly threw React #419 — and used
a `useEffect`-driven dynamic import instead so SSR and first client render start identical.

## Evidence audit result (the important finding of the night)

All 72 cited source URLs were independently fetched across six agents:

| Classification | Count | Meaning |
|---|---|---|
| VERIFIED | ~49 | Source resolves and supports the claim |
| UNREACHABLE | ~14 | Bot-mitigation (Cloudflare, Incapsula, Business Wire, SEC anonymous-UA blocks). A real browser reader is unaffected. |
| MISMATCH | 11 | **Source resolves but does not support the claim as cited** |
| DEAD | 0 | No broken links |

The 11 mismatches are the launch risk, because the site's promise is that every number
links to a public source. They split into wrong-document citations (D5b, C24, D11, A4,
B3, D12, D24 — the fact is true but the linked page does not contain it) and wrong
publicationDate fields (C6a off by a month, C23 off by 15 months, D26/D23/D28/D9 by days).
Plus A2 Cisco, where every figure is accurate but quarterly and full-year numbers sit one
sentence apart unlabelled.

## In flight

Wave 3, dispatched 2026-08-17 ~06:15 PT (`wf_e9caf1bf-e1a`): citation repair in two
groups, the adversarial hardening findings, then an independent re-verification of every
citation change plus a final pre-merge build.

Repair agents are constrained to three moves only — repoint a URL to the document that
actually contains the text, trim an unsupported clause, or correct a date to what the
source states. They may not add or strengthen any claim. The re-verify agent's primary
job is to catch OVERREACH against that constraint.

**Group B is committed (`c7a3b7f`) and spot-checked by the orchestrator.** Five dates
corrected — C6a 06-30→07-30, D23 and D28 07-20→07-27, D26 08-03→08-10, C23 2026-03-02→
2025-12-02 — each against the source's own stated dateline. D9 Secuvy was correctly left
alone because Business Wire is bot-blocked and the only contrary date came from a
syndicated mirror. The A2 Cisco fix added period labels and changed no number: $4B,
$9.3B, $7.5B, $9.791B, +28% and +40% are byte-identical before and after. No
out-of-scope record was touched.

**Group A, hardening, and both verification agents were still running at 06:15 PT.**

Next cycle: if re-verify says the evidence file is safe to publish and the build passes,
merge to `main`, push, confirm the Vercel deploy reaches Ready, then curl the live host
before calling it shipped. If it died on a session limit, resume with
`resumeFromRunId: wf_e9caf1bf-e1a`.

## Next, in order

1. Merge the verified launch-hardening slice to `main`, push, confirm the Vercel deploy
   is Ready, then curl the live host before calling it shipped.
2. Durability: split content out of TypeScript literals in `web/src/data/` into
   validated data files, so a weekly update is a data edit rather than a code change.
   This is the fix that makes the weekly loop survivable.
3. Edition + "what changed" model, so a returning reader has a reason to come back.
4. Sourced breadth into uncovered domains — application security, OT, and services —
   with hard source verification on every new claim.

## Known issues a human should see

- **Blocking before sharing:** Vercel Web Analytics is still off in the project settings.
  `<Analytics />` is mounted, so every page load currently 404s on
  `/_vercel/insights/script.js` and logs an error to the browser console. The first
  engineer who opens devtools on a page whose pitch is rigor will see it. Flip the toggle.
- `SEC-MARKET-SIG-SRC-*` artifact labels render inside the evidence drawer
  (`EvidenceDrawer.tsx:150`). Pre-existing, not a leak, but internal jargon on a public
  surface. Backlog.
- `jesse@keatingpike.com` is now in the prerendered static HTML as visible text and two
  `mailto:` links, so it is trivially scrapeable. Deliberate, but worth accepting knowingly.
- Nothing type-checks `web/scripts/` — `tsc -b` covers only `src` and `vite.config.ts`.
  Build-time scripts fail at runtime rather than at type-check. Fails safe. Backlog.
- `SEC-012` in `BACKLOG.md`: `data/signals.ts`'s `marketSignals` array lost its only
  consumer when `SignalFeed` was deleted. It is real evidence-linked content, so the polish
  agent logged it rather than deleting market data. Content call, needs an owner.
- An automated intelligence-layer process commits into this repo (`f59c62d`, and
  `.il-receipts` keeps showing up dirty). Worth deciding whether that continues now that
  the repo is about to be public-facing.
- RESOLVED: the `smoke.spec.ts` failure. Commit `d7a1ebf` fixed it and three other stale
  assertions that were already broken on pristine `main` — vendor names in the print table
  are `rowheader`, not `heading`.

## Lost time

The 2026-08-16 session limit (reset 10:40pm PT) killed 10 of 11 agents mid-wave and no
loop was scheduled, so roughly six hours passed with no work. The recurring continuation
job now exists to prevent a repeat. It is session-scoped and expires after seven days.
