# Q4 two-source normal-intake design review

October 25, 2026. **PASS for the corrected design, conditional on the retained-template proof.** No open design finding remains in the current project specification. Implementation and activation remain blocked by the explicit evidence dependencies below. I would use this closed two-source route because the existing ordinary intake and inventory interfaces already support the required separation.

The reviewed project specification is /Users/jessepike/code/projects/sec-market-finish-20261022/docs/active/daily-pipeline/accuracy/q4-two-source-normal-intake-integration-spec-2026-10-25.md, SHA-256 e4d03c698dab7f9609561e447c2476139608698d687b2b4fbb1c6c8204ad0869. The corrected VM proposal is /var/tmp/smp-q4-normal-intake-design-20261025.md, SHA-256 fd1a539548f788321197ccc559f1bfee2dafe01b79eed684d4920eff66c30147. Its stale pending-primary wording is superseded by the project's two explicit corrections.

## Concrete issues resolved in the project specification

A proposed version change would fail the existing market-daily-v2 check in /Users/jessepike/code/projects/sec-market-finish-20261022/web/scripts/verify-daily.mjs:31. The corrected specification preserves market-daily-v2 and changes exactly the two source rows. The resulting whole-policy J hash already distinguishes the activation.

The existing primary verifier faithfully returns acceptedSamples=0 and proposalEvidenceComplete=false for actual run 40188161705. A requirement that this old report become successful would be impossible without rewriting history or changing its rule. The corrected specification preserves/replays those holds and requires a separate independently accepted retained-template proof over the already authenticated actual bodies. No new source fetch is needed to decide whether the observed Evergreen template supplies a sound scoped identity proof.

## Minimal implementation boundary

The exact H→J and J→H checks should bind the entire object, fixed source positions, original rows and only the two intended replacements. Store J's hash and transition authority outside any self-referential source-row hash. Unknown pairs, reordered sources, extra fields and origin substitutions must fail. All source/supplier/family/seed declarations, version, limits, collection semantics and 557 obligations remain exact.

Keep the old three-ID HTML authority and its original origin bytes. Under J, validate the exact inverse and call the existing H resolver against reconstructed H. The existing dispatch functions at source_qualification_origin.py:391 and :544 can route recognized J/Q4 predecessors while preserving the inventory-only interface consumed at retained_audit.py:442, :567 and :828. This requires no ancestry search, generic transitive bridge or semantic-context exception. Qualification supplies inventory/provenance only; it cannot supply a current receipt, review, audit cursor or transport head.

The H seed validator at ops/ci/html_qualification_seed.py:145 explicitly requires its exact H package and three origins. A separate exact-J dispatcher/package must validate it against reconstructed H in a read-only overlay, validate the new Q4 graph, and import only the fixed immutable union. Use the actual J session, lease and acknowledged checkpoint. All rejection preflight precedes writes. Repeated identical imports remain safe only with the required acknowledgement. A fabricated H session or copying an archive directory is unnecessary.

Use one explicit exact-API discovery branch through the ordinary request callback. The existing kind-independent bounded predicate at retained_audit.py:284 already includes the proposed Q4 kind. Selection and date partitions at selection.py:9 and :47 already accept date-only scheduling hints. Preserve every returned/historical URL and original literal date; retain uncertainty and malformed/incomplete outcomes. The Q4 parser should use each observation's original check clock on replay. A genuine later 304 uses its new actual check clock while retaining the older full-body origin and reuse chain. A diagnostic wrapper must never become a normal download head.

The engine's ordinary request path at engine.py:146 retains conditional transport, in-run sharing and the reviewed force-refresh behavior. No engine, generic Page, model-rule or retained-semantic relaxation is needed from the evidence reviewed. An actual counterexample must be reviewed before adding one.

The public baseline needs a separate closed H→J zero-credit migration, retaining the existing older-policy→H validator and complete superseded chain. The existing migration checks at daily_baseline_migration.mjs:146, :171 and :217 are specific to the old three-source transition; widening them into an arbitrary row-change mechanism is unnecessary. Independently check the exact two-source inverse in Python and JavaScript. Preserve original facts, identities, dates and reports; no J collection or renewed expiry follows from the projected baseline.

The correction stamp's outer market hash changes, but its six per-group policy hashes must remain exact. All six groups currently depend only on unchanged citation source rows; none depends on either Q4 official source. Both language implementations bind those dependencies, at corrections.py:126 and verify-factual-corrections.mjs:97. Replay the actual admissions and preserve the original baseline hash, groups, fact dates and evidence.

## Resource bound and remaining evidence

The conservative incremental bound is six logical fetch reservations: two indices and at most four selected body requests under the existing two-document-per-source cap. Existing wire retries remain applicable. Zero available model calls does not mean zero body fetches or document reservations: process_item fetches first, and the SubscriptionAgent path can reserve a document before its later shared call reservation fails. At the historical 38/40 document ledger, at most two new document reservations remain; the actual activation ledger must be reread. The current historical baseline is 869 fetches, 80 calls, 38 documents and two gates.

Immutable origin/seed replay uses zero market fetches and model calls. On a later day, four cold documents have a conservative upper bound of 64 model calls, from one extraction and at most 15 independent candidate reviews per document. The unchanged global 80-call/40-document limits, cancellation and earlier denials still bind. All remaining URLs stay represented; there is no 529-body fanout.

Before implementation, accept the versioned retained-template proof that keeps the original report held. Then derive the real J hash, fixed origin/transition/seed/baseline authority and immutable package pins. Require the planned adversarial inversion, old-three-origin, six-admission, seed rejection/idempotence/ack, ordinary 200/304, quiet/future/boundary and zero-call-capacity tests, independent implementation review and required application/render checks.

Later actual ordinary intake must prove the two checks and budget/lease continuity. Scheduled and public publication acceptance remain separate. Neither this review, the retained template proof, qualification inventory nor a zero-credit baseline supplies those receipts.

Twenty-two consulted files retain byte/size/mtime seals in the companion JSON. This review ran no source/model requests, runtime state writes, archive mutations or repository edits. Only this /var/tmp review pair was written.
