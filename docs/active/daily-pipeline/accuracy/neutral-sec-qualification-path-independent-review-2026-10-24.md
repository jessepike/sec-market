# Neutral SEC qualification path: independent design review

Verdict: the local paired diagnostic implementation passes this bounded independent review after the fixes recorded below. The original design requirements are retained as review history. This review authorizes no request, registry change or qualification. Findings were sent directly to the implementer and root. The worker is changing an ignored copy; its draft is not the active runtime.

## Required corrections

1. **Use the real older-index layout.** SEC older submissions responses are flat filing-table arrays, without a root `cik`, `name` or `filings` wrapper. The inspected ignored draft required `document.cik` on older pages, which rejects actual retained bodies whenever such a page is required. Bind an older page to the exact validated root and its literal CIK-prefixed filename; validate its flat table, exact declared count and contained date range. Do not invent an issuer property absent from the payload. The current strict acceptance helper already follows this rule.

   Archived examples, with original bytes unchanged:

   - CrowdStrike `CIK0001535527-submissions-001.json`: body `ec42aac9136a82b721386b03207e592eb28f510d6fb815469e1e353972768e28`, 47,574 bytes, 306 rows.
   - Palo Alto `CIK0001327567-submissions-001.json`: body `27f17d2b43ee0fb41ca44b148c2da497fd9b305e9b3cf67d63d28829f5b84937`, 140,668 bytes, 908 rows.

   Both bodies are in the authenticated 9c archive. They currently lie outside the proposed 365-day window, so this observation does not request them again or add them to the next current request inventory. It establishes the continuation layout the path must handle if a current root requires it.

2. **Validate the complete index before selecting primary bodies.** Per-page table validation alone does not detect conflicting accession rows across pages. Apply the existing strict index rules across the whole ordered root/required-page set: full equal-length arrays, safe rows, exact issuer/root identity, unlisted/missing/duplicate pages, metadata counts/ranges, and identical-versus-conflicting accession duplicates. A conflict, missing page or cap stops body selection and leaves the diagnostic incomplete. Keep verified-only acceptance APIs strict. Share pure structural rules with a separately identified, non-admitting candidate diagnostic; do not copy `registration: verified` or weaken normal acceptance.

3. **Require an unambiguous pair and usable primary evidence.** Before requests, require one index and one document source in both join directions. Match the exact subject, full issuer object including legal name and relationship, ten-digit CIK, endpoint and lookback; validate each kind/family/host/scope declaration. A duplicate index must not run the same document source twice. Every selected primary observation must carry its actual `sec_documents` source ID, requested/final URL, original fetch time, nonempty archived body, index-selection provenance and charge. A missing, blocked, redirected, empty or unreadable body stays an explicit incomplete result. Retain the independently reproducible readable text needed by existing document coverage, without any claim extraction or semantic admission.

4. **Describe the bounds accurately.** In the existing normal collector, `maxPages` bounds submissions-index traversal; it is not an existing primary-body count limit. A separately reviewed diagnostic body guard of 100 can stop safely, but it must be labelled as that diagnostic bound and leave the complete selected inventory pending. Never truncate the selected list to obtain a complete result. The generic two-document/one-audit semantic cap does not replace neutral SEC primary retention. Every actual request retains the current shared 5,500-fetch ledger reservation, lease, escrow, UTC day/runtime guards and archive compare-and-swap. Use a fixed traversal window and reject a day/window crossing; final evidence times must bound every response, including the last one.

## Minimum qualification sequence

The existing archived primary filings establish the two product-to-parent relationships and exact CIK joins. They do not establish a new candidate's current transport or source-specific cache. Keep the four proposed rows as candidates and preserve 74 subjects and 557 obligations.

For each of the two exact pairs, obtain a fresh candidate index root and every currently required literal older page. Independently validate that complete 365-day index and derive the full eligible primary set using the existing forms and filing-date rules. Fetch all selected bodies under the paired candidate document ID, preserving every source/body/time/charge join. The historical 12 CrowdStrike plus 17 Palo Alto bodies are planning evidence, not a fixed current inventory. No parent cache or parent observation can stand in for a fresh candidate primary observation.

Return explicit diagnostic evidence and zero qualification, source-check, fact, model or admission credit. A separate review can then justify changing registration; only the later real normal collection can earn current collection checks. The normal unqualified collector cannot produce this qualification evidence because it returns `SOURCE_BINDING_UNVERIFIED` before transport.

## Coordinated policy dependencies

Candidate addition and later verified activation are separate substantive policy changes. Adding the four rows also appends exactly two source IDs to each of the two segment subjects. Later activation changes only the justified registration states. Each transition needs an exact current-policy request plan and independently retained predecessor proof; neither fits the existing two-field D-112 bridge. Do not rewrite old diagnostic policies, dates or charges or introduce a general old-policy bypass.

Regenerate the factual-correction outer policy stamp with each final global contract and replay its projection. The existing six per-group review hashes, accepted admissions, public rows and dates must remain exact unless a substantive dependency actually changes. Earlier in-memory review confirmed that simply adding the four rows while retaining the existing stamp fails `Correction build policy manifest differs`.

No new owner policy decision is identified. These are agent-owned proof and integration requirements under the existing coverage scope. Root owns any eventual integration, activation and real leased dispatch.

## Review limits

This is a design and ignored-draft review, not final acceptance of unfinished implementation. The draft's paired full-issuer join is suitable. Final implementation still needs positive flat-table continuation and full-primary fixtures, plus conflicting duplicate, missing/failed body, ambiguous pair, wrong issuer/host, future/window-crossing, cap, exhausted ledger and provenance-tampering cases. Actual retained bodies and immutable hashes remain unchanged; no source, network, model, archive/state, Git or publication action ran. The only output is this review file.


## Independent archived structural replay and current implementation findings

The candidate-only pure validator was replayed on the original archived bytes at `2026-10-23T11:34:15.010723Z`. The executed module pin was `fb4e4f4c37ae53f4440ed180c22fd0e935236303b71f555d939d39f4b990770d`. No source registration was copied to verified and no candidate transport observation was synthesized.

| Proposed subject | Actual 365-day root rows | Selected retained primary bodies | Additional flat-table structural fixture |
|---|---:|---:|---:|
| `crwd-exposure` | 1001 | 12 | 1307 unique filings |
| `panw-xsiam` | 1000 | 17 | 1908 unique filings |

All 29 parent primary bodies passed hash, original parent-observation/date and readable-text checks. Those parent observations remain parent evidence; they are not fresh candidate requests. The flat older-table fixture changes only an in-memory candidate lookback to 3,650 days so the authentic old tables become required. It is explicitly outside the proposed 365-day declaration and grants no current coverage. Under the actual 365-day declaration those extra old pages correctly reject.

Twelve negative cases across both issuers reject: wrong exact root name, an unneeded older page under the actual window, missing required continuation under the structural fixture, truncated arrays, conflicting accession rows across pages and a wrong-CIK continuation URL. The complete 9c archive content, file modification times and directory modification times were identical before and after. No source, network, model or archive/state write occurred.

The restored runtime addressed the earlier flat-table, cross-page-conflict, full-pair identity and readable-primary requirements. Independent review then found these three implementation cases, sent directly to the implementer and root for correction:

- A last primary response followed by a 1,200-second deadline overrun leaves source rows and the probe report marked completed despite the reservation context recording a deadline denial. The document row can retain its success reason and complete-body flag. The outer workflow repeats its guard and would hold, but the diagnostic row itself must be consistent.
- At a fully spent 5,500-fetch ledger, no reservation or request occurs, yet the source denial claims `reservationCharged: true`. Distinguish a denied reservation from a charge already returned before a later guard failure; preserve uncertainty only for persistence failure.
- An ambiguous SEC pair in a mixed contract records pair errors but still fetches an unrelated ordinary candidate's root, robots file and sitemap. Root's acceptance boundary requires full pair preflight before any source transport.

These three findings were open at that review pass. Their exact counterexamples have now passed independent retesting, as recorded below. They changed no existing source status, actual charged allowance, retained date or publication result.


## Final implementation verdict

The three implementation findings above are validated fixed in local `onboarding.py` SHA-256 `5ac7885955548848f2abc96f57da42bf3068e4d9fb8170fb97150e70d3456983`. No remaining actionable finding was found in this bounded review. The initial requirements remain useful acceptance criteria; they are no longer open implementation defects.

The exact last-inflight deadline and UTC rollover counterexamples now mark both paired source rows and the report incomplete with the denial reason, preserving all three fictional charges. A fully exhausted ledger starts zero requests and correctly reports no returned reservation; a denial after reservation preserves its one charge. Invalid SEC pairs suppress ordinary and explicit source transport too.

The final focused suite passed 20 tests in OrbStack. Independent adversarial retests also passed:

| Case | Fictional requests | Result |
|---|---:|---|
| last-deadline | 3 | Held or rejected correctly; `SOURCE_PROBE_DEADLINE_EXCEEDED` |
| last-utc | 3 | Held or rejected correctly; `SOURCE_PROBE_UTC_DAY_CHANGED` |
| pre-reservation-exhausted | 0 | Held or rejected correctly; `FETCHES_BUDGET_EXHAUSTED` |
| post-reservation-deadline | 0 | Held or rejected correctly; `SOURCE_PROBE_DEADLINE_EXCEEDED` |
| mixed-preflight | 0 | Held or rejected correctly; `SEC_DIAGNOSTIC_EXACT_ONE_TO_ONE_SOURCE_JOIN_REQUIRED` |
| blocked-primary | 3 | Held or rejected correctly; `SEC_DIAGNOSTIC_PRIMARY_BODY_RESPONSE_INVALID` |
| redirected-primary | 3 | Held or rejected correctly; `SEC_DIAGNOSTIC_PRIMARY_BODY_RESPONSE_INVALID` |
| empty-primary | 3 | Held or rejected correctly; `DOCUMENT_HAS_NO_READABLE_TEXT` |
| http200-block-page | 3 | Held or rejected correctly; `SOURCE_BLOCK_PAGE` |
| future-body-time | 3 | Held or rejected correctly; `SEC_DIAGNOSTIC_FETCH_TIME_OUTSIDE_LEASED_WINDOW` |
| primary101-guard | 2 | Held or rejected correctly; `SEC_DIAGNOSTIC_PRIMARY_BODY_GUARD_EXCEEDED` |
| index-page-cap | 1 | Held or rejected correctly; `SEC_DIAGNOSTIC_PAGE_CAP_EXCEEDED` |

The 101-primary fixture retains all 101 selected URLs and stops before primary transport, reporting the explicitly named diagnostic body guard. It does not truncate the inventory or claim completeness. The existing `maxPages` field continues to bound index pages. Failed HTTP responses, redirects, empty bodies, HTTP200 block pages and future response timestamps cannot complete primary retention. The checks add no semantic validation or facts.

A final actual-byte replay against the same unchanged archive repeated the two 365-day candidate declarations and all 29 readable parent primary bodies under this final code pin. Candidate registration remained unchanged; no copied verified declaration or synthesized candidate observation was used. The authentic flat older tables again passed only the explicitly hypothetical 3,650-day structural fixture. The full archive seal remained:

- Content: `cc1862a947ef7b54017c86a1c653c3a03298271a816f0ff982ccbce6c6d45309`.
- File modification times: `a6ac93a7720f819bbf25bc66073ce03295759e9d7d208a33915d63e55d7f642a`.
- Directory modification times: `36bd1a13a1885c95303ecccb789f5573a537316dc1ae5bd0560ef996c90c2434`.

The durable four-row proposal is `/Users/jessepike/code/projects/sec-market-finish-20261022/docs/active/daily-pipeline/accuracy/four-neutral-regulatory-bindings-spec-2026-10-24.json`, raw SHA-256 `9928884e5b0b9ec99811f09033fe1477ecde2353c012a634dd83317a63769526`. Its historical wording about a normal collector providing preactivation proof is superseded by the dedicated candidate diagnostic in the current qualification-path specification. Candidate addition, later verified activation, exact probe-plan provenance transitions and the factual-correction outer stamp remain separate integration prerequisites.

This is local implementation and archived structural evidence. It does not establish that any fresh candidate root or primary body has been requested, that four sources are qualified, that a scheduled collector ran, or that anything was published. Broader integrated application checks remain root's responsibility. This review changed only its assigned document.
