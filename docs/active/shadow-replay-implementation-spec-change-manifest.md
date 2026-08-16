# Gate S1 Replay Implementation Specification — Change Manifest

## Control

- **Manifest ID:** `SEC-MARKET-SHADOW-S1-MAN-001`
- **Current specification:** `SEC-MARKET-SHADOW-S1-SPEC-001` v0.2
- **Lifecycle state:** `accepted`

## v0.1 candidate

Independent review failed.

Material defects included:

- one run was used where the design required seven issuer runs and one cycle;
- CLI actor aliases did not prove distinct humans;
- review interactions, closure, freeze, and promotion transactions were incomplete;
- immutable tables and failure-injection tests were incomplete;
- CrowdStrike rounding and issuer-specific locator recipes were absent;
- Amazon and Fortinet could not complete through `urllib`;
- config serialization and package execution were ambiguous; and
- the human/manual fallback path could bypass independent source confirmation.

## v0.2 accepted

The accepted specification adds:

- seven issuer runs plus one signed cycle;
- owner-attested actor IDs bound to SSH keys and a separate trust anchor;
- canonical signed payloads, nonce expiry, and atomic nonce consumption;
- per-candidate review interactions and signed verification, adjudication, closure, freeze, incident, and abort commands;
- exact corpus and definition hash recipes;
- native period headers, value normalization, and CrowdStrike half-up rounding;
- bounded network controls and signed two-person manual retrieval fallback;
- exact identity and idempotency keys;
- append-only and tamper-evident SQLite controls;
- atomic promotion with rollback injection tests;
- deterministic fixtures without committed source bytes;
- complete config/schema deliverables;
- 43+ negative, state, and bypass tests; and
- explicit prohibition on implementation, fixture capture, identities, replay, live collection, scheduling, posture, and publication.

## Review result

- Architecture review: passed after correction
- Security/governance review: passed after correction
- Builder/operator review: accepted after correction

## Authority

Only `shadow-replay-implementation-spec-v0.2.md` governs a future Gate S1 implementation.

`shadow-replay-implementation-spec.md` v0.1 is retained as a failed candidate and is not implementation authority.

