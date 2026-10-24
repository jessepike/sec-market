# Bounded candidate traversal implementation note

Status: implementation plan for an offline, explicitly selected diagnostic operation. It does not authorize a live request, change source registration, or establish a qualified source.

## Boundary

Add one separate schema-2 `bounded_candidate_traversal` operation to the existing leased source-probe path. Preserve schema 1's exact seven-target validation and execution unchanged. The exact plan keys are `schemaVersion`, `operation`, `marketSha256`, `maxRequests`, `maxIndexPagesPerSource`, `primarySamplesPerSource`, and `sources`. The plan binds the whole policy and exactly three ordered source rows for `ping-identity:official:1`, `delinea:official:1`, and `sonatype:official:1`; each row pins the current candidate declaration, the source-specific proposed adapter hash, and a `startProof` in the existing `qualification_observation` shape. Validate each admission, prior charged request, body reference, and literal canonical disclosure of the reconstructed index root before any transport. Missing or malformed schema-2 fields must fail closed; no generic policy-mismatch exception or implicit schema selection is allowed.

The operation branches before ordinary candidate root/robots/sitemap fanout and before the SEC diagnostic branch. It makes no model calls, source checks, coverage claims, registrations, semantic admissions, or facts. Its result is diagnostic evidence only, with explicit zero credit fields.

## Fixed limits and traversal

The plan fixes at most 60 sequential index requests per source and one primary-article shape sample per source: 183 requests total. Every request uses the current durable lease, reservation, before-fetch guard, and day/deadline checks. The caller follows only each retained response's source-specific validated literal `next` URL. It never constructs page URLs, accepts skipped pages, truncates a discovered inventory, or treats an unproved terminal as complete. An incomplete traversal retains all valid observations and inventory accumulated so far.

The parser API is `parse_source_html_index(source, url, body, highest_page, as_of)`. Its source-specific mode and exact source identity remain bound to the proposal. The sample URL must be selected from a card observed in that same traversal and requested under that candidate's paired source identity and allowed scope. The sample checks transport identity, canonical/article identity, readable primary content, and date-metadata shape only; it does not derive facts or semantic evidence. Missing or ambiguous metadata stays unknown.

The proposed adapter is reconstructed by code from the original candidate row with only its exact HTML index URL, `html_index` kind, and source-specific `htmlCompleteness` mode set; its hash is then compared with the plan. The receipt binds the raw and canonical plan hashes, whole-policy hash, original candidate source hashes, proposed adapter hashes, every request/response/body/time, literal pagination controls, inventory/date hints, sample, and durable reservation evidence. A pure verifier replays the parser over those bound bodies, proves sequential literal traversal and terminal state, reconstructs the complete or partial inventory, verifies sample selection and response identity, and checks the recorded reservation chain against the run's initial budget. A hash mismatch or malformed join is rejected; missing evidence cannot become success. No offline fixture may be treated as a live observation.

## Implementation and validation

Keep changes limited to `web/scripts/pipeline/onboarding.py`, focused `ops/ci` tests, and this note. Do not change the source registry, market policy, correction stamp, or existing schema-1 plan. Tests must cover schema-1 byte/behavior compatibility; exact three-source and adapter binding; preflight-before-transport; all three parser modes; sequential traversal and terminal proof; duplicates, changed bodies, redirects, unsafe URLs, missing pages, unknown dates, page/request caps, lease exhaustion, day rollover, deadline and cancellation; and explicit zero semantic/coverage/registration credit.

Use synthetic plans and immutable archived fixtures only. Preserve archived request IDs and times as historical fixture metadata; label any synthetic transport wrapper as fictional. No fresh market-source requests, model calls, publication, workflow dispatch, archive writes, or contract activation are part of this implementation. Root will prepare and review the actual plan separately after the verifier and tests are ready.
