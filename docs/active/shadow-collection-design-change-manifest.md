# Shadow Collection Design — Change Manifest

## Control

- **Manifest ID:** `SEC-MARKET-SHADOW-MAN-001`
- **Current design:** `SEC-MARKET-SHADOW-001` v0.2
- **Replay corpus:** `SEC-MARKET-SHADOW-CORPUS-001` v0.1
- **Lifecycle state:** `accepted`

## v0.1 candidate

Gate S0 failed.

Material findings:

- agent execution could issue `VERIFIED`;
- extractor, verifier, and promoter separation was not structurally enforced;
- blind bulk promotion and automated run closure had no blocking records;
- promotion lacked atomic accepted-evidence and evidence-version contracts;
- semantic idempotency keys were incomplete;
- event, origin, artifact, and retrieval identities were conflated;
- expected-but-missing metrics could disappear;
- definition and acquisition rules were prose-only;
- replay lacked a known-answer corpus;
- the first cycle covered too many entities and secondary facts;
- run, cycle, verdict, repair, and closure transitions were incomplete; and
- confidentiality response covered demotion but not already preserved data.

## v0.2 correction

The accepted design:

- limits S1–S3 to seven primary financial facts;
- supplies a canonical replay oracle and metric-definition seeds;
- pins publisher, origin, document family, period, value, locator, action, and limitation;
- requires human-only verification and a different human promotion authority;
- makes per-candidate source viewing and no-prior acknowledgement structural;
- separates reporting events, document origins, retrieval attempts, artifacts, extraction attempts, and canonical candidates;
- records expected observations and visible collection gaps;
- adds deterministic validation, acquisition quarantine, and definition-version rules;
- adds complete candidate, run, and slice-cycle transitions;
- writes append-only accepted evidence and supersession edges atomically;
- makes replay and adjudication semantically idempotent;
- defines confidentiality quarantine and lawful deletion handling;
- manually triggers S1–S3 with no scheduler;
- blocks S1 until two distinct humans are assigned; and
- keeps implementation, replay, live runs, posture, and publication unauthorized.

## Review result

- Architecture review: passed after correction
- Governance review: passed after correction
- Operator/builder review: accepted after correction
- Final verifier: passed after definition-hash, complete-coverage, candidate-identity, corpus-boundary, and change-record hardening

## Authority

Only `shadow-collection-design-v0.2.md` governs future shadow-process design.

`shadow-collection-design.md` v0.1 is retained as a failed candidate and is not implementation authority.

