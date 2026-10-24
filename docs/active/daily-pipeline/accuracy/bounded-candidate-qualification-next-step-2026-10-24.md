# Bounded qualification for Ping, Delinea and Sonatype

Status: implementation proposal based on authenticated archived responses. This document does not authorize requests or qualify a source. Its machine-readable companion is `/Users/jessepike/code/projects/sec-market-finish-20261022/docs/active/daily-pipeline/accuracy/bounded-candidate-qualification-next-step-2026-10-24.json`.

## Decision

Build one source-specific, leased traversal operation for the three candidates, capped at 60 index pages and one nonsemantic primary article sample per source. Skip the generic candidate-probe fanout in that operation. Follow validated literal pagination through the actual terminal; do not deploy a new seven-page allowlist for each batch.

D112 permits daily intake to pass while historical article review remains unfinished. It still requires complete discovery of the declared source. The accepted specification explicitly preserves full pagination, and the current independent receipt replay runs the same discovery traversal again. The 30-day window appears in document scheduling, after discovery, and is not a discovery cutoff. Stopping Ping when a card becomes old, treating Delinea's ten-entry RSS as its whole archive, or accepting Sonatype's first dated page would change the completeness rule. That is outside this repair.

For the present full-index proposal, all currently advertised 25 Ping pages must be traversed; Sonatype needs all 13 if its actual terminal confirms that count; Delinea needs its actual terminal, which is still unknown. All are bounded at 60 pages. This means fetching their index pages, retaining their URLs and date hints, and proving the traversal. It does not mean fetching or semantically reviewing every historical article before intake can succeed. An unfinished traversal remains a gap. A complete traversal with pending article reviews has separate intake, processing and historical states under D112.

## Existing evidence and exact limits

This proposal uses current market policy `79cdd19b962ee3adbb5d9e1a43cbc389b3c9196a6c0a2105ea455c8bd70f9f60`, the accepted D112 specification, the seven-response review, and archive `20f8f6ee9b8113aea994d4251197221a6f64a005`. The archive manifest hash is `962f925f60c19aa47c368c80c80d80ad6680b736223e2ceab76e071198586d37`. Exact code, body, observation, policy and ledger hashes are in the JSON companion. Source content was inspected as untrusted data, without executing scripts.

| Source | Current evidence | Remaining completeness proof |
|---|---|---|
| `ping-identity:official:1` | Retained pages 1, 2, 3 and 25 contain 32 distinct cards. Page 25 has two cards, an exact page-1 start link and a disabled next span. | Pages 4–24 are absent. Finish the exact terminal parser and prove consecutive traversal. Page count may change in a fresh run. |
| `delinea:official:1` | Root index has 12 undated cards, matching head/visible next links and a numbered window through 5. Two full articles have exact canonical/H1 identity and visible datelines. | Pages 2 onward and the actual terminal are unobserved. Page 5 is not established as last. Keep card dates unknown. |
| `sonatype:official:1` | Root has 16 dated cards, next page 2 and an advertised page 13. One full article has exact canonical/H1 identity and a visible dateline. | Pages 2–13 are absent. Establish terminal structure and consecutive traversal. Never request the root's invalid Prev page-zero/fragment URL. |

The existing ordinary collector rejects candidates before requesting them. The generic source diagnostic probes roots, robots and selected XML endpoints; it does not qualify these HTML archives. The existing explicit seven-target path retains responses and deliberately leaves `qualified=false`. There is no existing operation whose successful execution alone can safely turn these three candidates into verified full-index bindings.

Preserve all 74 suppliers, all 557 obligations and all 9,914 existing source/URL references. Newly discovered candidate URLs increase retained pending evidence; they cannot replace old inventory. Dates in index cards remain scheduling hints. Delinea's undated cards remain unknown, even where a separate RSS item has a date. RSS and HTML titles differ in five of ten Delinea items and all ten Sonatype items, so those metadata strings must retain their own provenance. A visible article dateline does not admit a market fact or establish its effective date.

## The smallest runtime addition

Add a versioned plan operation such as `bounded_candidate_traversal` under the existing private `source_probe=true` input and lease profile. The plan names exactly these three current candidate IDs, their original source hashes, their proposed source-bound HTML adapter hashes, their already disclosed starting index URLs, and fixed traversal/sample bounds. It uses the current whole-policy hash. Validate the entire plan before escrow or transport. Preserve schema-1's exact seven-target validation and its original D112 bridge unchanged. Missing fields or a failed legacy plan must never select the new operation implicitly.

Use at most three workers under the existing maximum of four. Every request uses the existing shared durable fetch reservation, before-fetch day/deadline guard, lease, cancellation and checkpoint path. The operation must branch before generic root/robots/sitemap probing. It follows only a literal next link whose source-specific current/previous/numbered controls agree with the response being retained. A 60-page boundary without a proved terminal is incomplete. Do not construct undisclosed page URLs or replay old body hashes as fresh transport.

Factor the pure parser and traversal so both the typed qualification operation and normal collector can use it. Keep normal `discover`'s verified-registration guard. Do not temporarily assign `registration=verified`, introduce a generic bypass flag, or reinterpret a diagnostic as a normal source task. The qualification caller has a distinct, narrow proposed-binding context and produces distinct evidence with zero collection credit.

For Ping, finish the observed exact `wd_page_start` and disabled-next controls while keeping numeric offsets, date order, card sizes, canonical identity, host/path rules and duplicate checks. Delinea needs an exact title-anchor/card rule, unknown card dates, consistent head/visible next controls and moving-window validation. Sonatype needs exact title/link/date regions, numeric query and active/next agreement, the known invalid root Prev control handled without a request, and a newly observed validated terminal rule. Unknown terminal layouts hold. No current root response proves Delinea's or Sonatype's last-page markup.

The bounded operation also takes one primary article shape sample per source from a literal card in that same actual walk. These three fetches check request/final/canonical identity, readable primary content and date metadata shape. They perform no candidate extraction or model review. The existing full Delinea and Sonatype responses are useful offline fixtures; the sample URL in an actual run must come from its current retained index body. The existing publication parser produces no structured publication date for those three inspected full articles, so new date rules need explicit source-bound fixtures and ambiguity checks. A missing dateline can remain unknown; it must not be repaired with transport `Last-Modified` or an unrelated index timestamp.

## Qualification proof and inventory continuity

Produce a sealed qualification receipt binding the original full policy and candidate source, exact proposed HTML binding and adapter/code context, every request/observation/body/time, literal pagination controls, complete or partial URL/date-hint inventory, primary shape samples, and every durable reservation. An independent pure verifier reconstructs traversal and the inventory from those bodies. It rejects omitted pages, changed bodies, wrong source/host/path, conflicting terminal controls, time/context drift, newer failed or equal-time conflicting transport, and fabricated reservation success.

Keep `coverageCredit=false`, `sourceChecksCredited=0`, `qualifiedSources=0`, `semanticAdmission=false`, `facts=[]` and no `newFactIds`. A derived `registrationReady` result can describe complete evidence for a later declaration; it does not change the actual candidate registration. Partial failure retains every observed URL and its unresolved state. Neither partial inventory nor a mutable ready flag counts as a successful intake.

At eventual registration, an independently replayed inventory-only predecessor can carry URLs observed in the qualification receipt into normal full inventory, including any that disappear before first collection. This requires a typed qualification-origin adapter in the existing predecessor replay, with exact source and proposed-binding joins. It must supply no semantic review, audit cursor or intake authority. Preserve original observation dates and all existing predecessor, hold and fact references. Ordinary daily discovery must still freshly traverse on its own. This prevents a delayed activation or a rolling index from dropping known URLs.

## Contract transition and dependent artifacts

Keep market policy and registrations unchanged during qualification. Proposed HTML bindings belong in the typed qualification plan. Their exact starting URLs are:

- Ping: `https://press.pingidentity.com/news-releases`.
- Delinea: `https://delinea.com/news`.
- Sonatype: `https://www.sonatype.com/press-releases`.

After actual complete qualification and separate integration review, make one atomic contract transition for those same three source IDs. Change only the justified index URL, kind, source-specific completeness mode, verified registration and immutable qualification-origin pointer. Keep suppliers, hosts, families, required flags, page caps, categories and the complete obligation inventory. The receipt hashes the proposed binding before its own origin pointer is added, avoiding a self-referential hash. It also retains the original whole contract and exact candidate source; it never rewrites them to the activated policy.

This source qualification is a substantive source transition. The historical-probe bridge permits only the earlier two-field D112 change and must not be widened to pass these new declarations. Unrelated accepted facts can retain original review proof only after their actual pinned old/current source and semantic contexts match. A changed candidate binding cannot borrow review from a citation source or a different supplier.

The same activation must update the diagnostic plan. The old seven-target plan is bound to the original policy and requires candidate sources. It cannot remain operational after those sources become verified. The smallest safe disposition is an explicit current-policy schema-2 disabled operation with no candidate targets or requests, until a separately reviewed candidate plan is needed. Preserve the existing raw plan objects and original diagnostic records unchanged. Do not make absence, an empty legacy plan or a stale hash silently disable checks.

Also regenerate the enclosing factual-correction policy stamp and projection for the new global contract only after independently proving all six group review policies, admissions, rows and original dates remain exact. Subject changes affecting a correction require their own review. These dependent changes belong in the same activation candidate so a registry repair cannot repeat the earlier stale-plan/stamp failure.

An actual normal run under the new declarations can then earn daily intake through independently replayed fresh complete discovery. The current engine/reconciliation selection and D112 public measures remain in place. Full history may still be pending, and no new fact is admitted without its normal current primary-source and independent semantic review.

## Fixed-budget comparison

Diagnostic `40066513321` charged 124 requests for seven explicit targets. Its other 117 requests were generic probes. Repeating that overhead is avoidable; 117 is the observed cost of that run, not a promise about every future generic run.

On the currently archived layouts, missing discovery pages total `21 Ping + 12 Sonatype + (P_d - 1) Delinea = 32 + P_d`. Delinea's numbered window establishes at least five pages; its declared cap is 60, but its terminal is unknown. If Ping remains 25 pages and Sonatype's terminal confirms 13, that is 37–92 missing pages. Exact seven-target batches would need 6–14 further plan executions, including the currently proposed next batch. Holding the observed generic overhead constant, that spends 702–1,638 requests on generic work, and 42–98 on explicit slots, or **744–1,736 total**. The final batch's unused slots cannot be silently removed from an exact-seven schema.

A dedicated fresh traversal of the three whole indexes costs `25 + 13 + P_d`, plus three primary shape samples: **46–101 requests** on those conditional layouts. The unconditional hard bound is **183**: three sources × 60 index pages, plus three samples. It has no generic fanout and no model work. If fresh page counts grow past a source's 60-page cap, the operation stops incomplete rather than exceeding that cap or calling an older terminal current.

The first subsequent normal collection has an upper bound of 180 index requests plus six selected primary document requests for these three sources, or **186**. Selection may use fewer, and semantic processing remains bounded at two documents per source, with one ordinary historical audit. Qualification plus first normal collection therefore has a conservative combined ceiling of **369 requests**. These are source-specific estimates; they exclude other sources and assume no unbounded retries. Every real request still needs a live reservation, and a timeout, budget limit or midnight crossing can leave useful partial evidence without success.

The authenticated archive's October 24 ledger contains 1,111 charged fetches out of 5,500, leaving a nominal 4,389. Model calls are already 80/80 and semantic documents 40/40. The proposed qualification operation fits that archived fetch headroom without any model or semantic-document capacity. This does not reserve capacity or assert what the later live ledger will contain. It cannot create semantic admissions from today's exhausted model/document budgets. Normal daily collection still needs its own lease and current allowance.

## Offline work and acceptance

Offline work can finish exact-source parsing, traversal and terminal fixtures; plan validation; typed receipt production and independent replay; inventory-only continuity; budget/lease failures; and the prospective atomic contract/plan/stamp migration checks. The archived bodies support deterministic fixtures with their original bytes and dates. No offline result supplies a missing page, current qualification or an actual intake receipt.

Before implementation acceptance, test legacy seven-target compatibility and mode downgrade rejection; all observed Ping controls and missing intermediate pages; Delinea page windows growing beyond five; Sonatype's invalid page-zero Prev and unproved terminal; pagination/body/host/canonical/date conflicts; duplicates; future or unknown dates; full inventory retention after rollover; exact candidate/source/binding joins; lease/day/cap cancellation; and complete normal intake with unfinished history. Test that normal collector registration stays closed and a qualification receipt cannot inject facts, borrowed semantic proof or copied audit times.

Actual missing evidence still requires the bounded fresh walks and their three literal primary samples, followed by a separately justified registration and normal collection. No new primary-source, workflow, model or network request was made for this specification. Only this new document and its JSON companion were written.
