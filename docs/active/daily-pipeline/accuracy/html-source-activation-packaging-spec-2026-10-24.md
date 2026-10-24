# Packaging the three HTML source activations

Status: proposal only. No source, policy, request plan, authority registry, archive, budget or public snapshot was changed for this document. The actual V5 qualification result and its external evidence are pending. A passing parser or a complete older Ping traversal cannot fill those fields.

## Recommendation

Package one closed three-source transition, its small immutable inventory objects and a fixed external-authority row in one reviewed application change. Import the new immutable objects inside the ordinary collector's existing lease, then require a successful archive checkpoint before the collector uses the new origins. Keep qualification diagnostics disabled under the new whole-policy hash. Start current-policy public intake at zero unless a separately validated actual collection supplies it.

The dormant origin helper already provides the required inventory union. It does not yet provide a production seed importer. The public baseline verifier also currently permits an uncollected migration only from a v1 snapshot, so the existing v2 baseline needs an explicit prospective-migration rule or an actual new-policy snapshot before the activation build can pass. These are the two necessary packaging changes identified here; neither is implemented by this proposal.

## Evidence and current boundary

The current whole market-policy hash is `79cdd19b962ee3adbb5d9e1a43cbc389b3c9196a6c0a2105ea455c8bd70f9f60`. Its repository file hash is `5b2b52dc2d17709f562b64ad6cb435086971ff8a6ccb9ce2fe95296a1ce1a7ff`. It has 74 suppliers, 303 source declarations and 557 required obligations. D112 daily intake and historical review remain separate.

Main V5 code was promoted as `a59f1fe64c86c95805792ed4dbd3e3b92c0b9d15`. Root reported actual diagnostic `40116695719` queued at `2026-10-24T17:33:53Z` on that revision. Its completion, result hashes and external artifact/archive pins remain pending here. The application promotion and queued run are not qualification results. `ACTIVATION_AUTHORITIES` in `web/scripts/pipeline/source_qualification_origin.py` remains empty; all three source declarations remain candidate.

This proposal uses the independently authenticated V4 archive only for feasibility:

- Archive commit: `e467ab000b8225931d6684eb6d0aa39bbba1f6c9`.
- Manifest hash: `ce989f357ecda7ef5a460ad96ceededf6a8f4b1cd566a408eb6ba79f3a4fad70`.
- VM root: `/var/tmp/smp-bounded-v4-probe-20261024/archive-e467ab00/jessepike-sec-market-e467ab000b8225931d6684eb6d0aa39bbba1f6c9`.
- Original V4 run: `40079036392`, attempt 1, application `4b5e5ec1669ddad052c6320ddf4a4dffdb9c1f5e`, checked at `2026-10-24T08:45:25.560536Z`.
- Original raw plan: `0353ec8ef62fedd09758cc44b1fcbe80bbe713e996432a3684f524acd66c6c55`, 5,338 bytes.

V4 used 63 fetches: 60 index pages and three primary samples. It moved the shared ledger from 1,375 to 1,438 fetches; 80 calls and 40 documents were unchanged. It granted no model, document, semantic, qualification or coverage credit. Ping's 25 pages were terminal-complete. Delinea's 25 pages lacked a proven terminal. Sonatype stopped at a rejected page-10 path. Therefore V4 cannot authorize this three-source transition.

## Exact contract transition

Use the helper's existing `three_html_source_qualification` transition, replacing only these original source-array slots without changing their order:

| Source ID | Starting index |
| --- | --- |
| `ping-identity:official:1` | `https://press.pingidentity.com/news-releases` |
| `delinea:official:1` | `https://delinea.com/news` |
| `sonatype:official:1` | `https://www.sonatype.com/press-releases` |

Derive each adapter with the actual original plan's selected source, index URL and revision-5 binding through `_candidate_adapter`. Do not reconstruct it from a newer global constant or reinterpret an earlier bounded report. The activation base is exactly that adapter with only `registration` changed to `verified`. Add its exact `qualificationOrigin`. No other source, supplier, alias, category, host, allowance, version, mode or array position may change. The helper independently reconstructs both the forward transition and its inverse against the original full contract.

The final contract hash, called `H` below, is pending. It depends on the actual V5 record and inventory manifest references. Do not use a guessed hash or treat `H` as a literal final plan value.

Each origin retains the existing closed fields: `schemaVersion`, `kind=bounded_html_qualification`, `originalContract`, `diagnostic`, `plan`, `sourceResultIndex`, `sourceResultSha256`, `originalSourceSha256`, `proposedAdapterSha256`, `activationBaseSha256` and `inventoryManifest`. Every immutable reference includes its exact key, raw hash and byte length. Origins contain no resulting policy hash, avoiding a circular hash dependency.

The descriptor is a separate immutable object with `schemaVersion=1`, `kind=three_html_source_qualification`, `originalContract`, `activatedContractSha256=H` and exactly three ordered changes. Each change binds the source ID, original source-array index and original, proposed, activation-base and origin hashes. The immutable metadata pointer is `source-qualification-transitions/H.json` and contains the exact descriptor reference. Its content is lookup metadata; the source-controlled authority row supplies the independent trust boundary.

## Finite external authority and historical inventory

Add no authority row until the actual main V5 diagnostic proves all three complete traversals and all three source-bound samples with no denial. Independently authenticate the real Actions run and attempt, event/ref, application revision, artifact, exact run record, raw plan, original full contract and archive manifest. Retain that external verification receipt. The pure historical replay API checks internal joins and bytes; it does not contact GitHub or establish external provenance.

The future fixed authority row must select `H` and bind the exact descriptor, original contract, main diagnostic and main raw plan. Its finite `diagnostics` list must pin each included record, original contract, raw and canonical plan hashes, run/attempt, application revision, external-verification receipt hash, artifact hash, archive commit and manifest hash. All actual V5 values are pending. No self-authored archive flag, matching metadata or new archive head may substitute for them.

For each source, produce a flat `qualification_inventory_manifest` containing the main V5 result exactly once, every required earlier accepted partial bounded result and every required source-scoped explicit HTML page. Sort unique entries by canonical digest. Authenticate all earlier diagnostics individually under their actual original policies and plans. Preserve original body, observation, charge and time joins, including the existing narrow D112 bridge where a schema-1 proof requires it.

Earlier bounded revisions retain their original parser, error, terminal and inventory results. Schema-1 explicit HTML observations asserted retained HTML and canonical/format structure, but no card-parser snapshot. After replaying their original proof, the helper may derive their card inventory through the independently approved main adapter's exact closed source family. This creates inventory with original observation provenance; it cannot renew a date or repair an older bounded failure.

The generic corporate XML diagnostics require a separate disclosure reconciliation. Do not invent raw-plan references for the first generic diagnostics, which did not have qualification plans, or force them into the bounded authority shape. Preserve their exact existing records and raw bodies in the archive. Bind the independently reviewed XML/card overlap analysis through the external verification receipt. If an unmatched relevant lead remains, resolve it explicitly before activation or design a separate narrowly typed inventory carrier; the current HTML origin helper cannot import arbitrary sitemap links.

## Actual historical XML and card reconciliation

The following counts come from read-only replay of authenticated V4 and earlier retained responses. They are source/URL pairs. They do not claim V5 coverage or article review.

| Source | V4 accepted cards | Earlier explicit card union | Combined accepted cards | Generic XML links | Structurally plausible article leads | Leads matched to cards | Unmatched plausible leads | Index-root links | Other corporate links |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Ping | 242 | 42 | 242 | 6 | 5 | 5 | 0 | 1 | 0 |
| Delinea | 290 | 36 | 290 | 7,106 | 281 | 281 | 0 | 1 | 6,824 |
| Sonatype | 144 | 45 | 157 | 6,849 | 205 | 157 | 48 | 1 | 6,643 |

“Structurally plausible” uses the approved literal article-path grammar to find leads; it is not independent release-scope authority. The unmatched Sonatype URL-list canonical hash is `ca17f294dc75e70edd23a2f68fe667d96b964c7395bdcd0599447829243e5197`. Its 48 entries numerically equal three pages of 16 cards, but that observation cannot establish that V5 will include them. The actual V5 reconciliation must compare literal URL sets and retain any earlier card that has rolled out of the current index.

The old Ping RSS has five entries, all covered by the 242 accepted HTML cards. Preserve its original RSS dates and channel metadata as historical source values; they grant neither a complete RSS history nor fresh intake. XML `lastmod` and card date values remain observed scheduling hints, not independently verified article publication dates. The generic root responses that resolved to homepages cannot be relabeled as qualified index responses.

Useful exact raw-body pins from the original `40069462824` generic observations are:

| Body | SHA-256 | Bytes |
| --- | --- | ---: |
| Delinea sitemap | `5030752f92d33b100ec65b801fc448b3efa69c2a9dc07e2c38fb4f518ee9d5a7` | 10,303,377 |
| Ping RSS | `906b1656404e95d8ed52082ecfd40d738e2ff24368ab6638cda810d4e38055a8` | 2,460 |
| Ping sitemap | `0e9e4ce942726c5c0723dce8646983339e80b679f497e6084bc397cbf0377692` | 503 |
| Sonatype sitemap | `974401d7a3cf7c8fd9ba1172a85aae833359ae81fe324baf09919eb9df4f2ec2` | 8,604,999 |

If every plausible lead is present in the actual V5-plus-retained-card union, keep the reconciliation as external evidence; no generic XML runtime extension is needed. If some remain, do not silently exclude them as old or unrelated. Their archived dates are not sufficient scope decisions. A proposed carrier must authenticate the original whole policy, source, record, body, time and charge; classify scope from actual content or another approved source; add only literal relevant URLs; and supply no semantics, audit cursor or intake credit.

## Build the object graph without circular references

Assemble the package in this order, offline from authenticated original bytes:

1. Verify the actual V5 archive and all required older immutable references. Complete the XML/card reconciliation and external run/artifact verification.
2. Generate three flat inventory manifests and the three source origins. Derive their activation bases from the exact main V5 plan.
3. Generate the complete three-row candidate contract and calculate `H`. Independently prove the closed forward/inverse comparison.
4. Generate the descriptor and `source-qualification-transitions/H.json` pointer, then the fixed authority row selected by `H`.
5. Generate the new disabled qualification plan, outer correction stamp and prospective public baseline. Verify every dependent projection before promotion.
6. Generate a small source-controlled seed manifest and its exact new immutable payloads. Original HTML/XML bodies, plans and diagnostic records remain in the data archive; do not duplicate large source bodies in application Git.

The seed format is a proposed new implementation surface. Use a closed schema containing a version/kind, `activatedContractSha256`, the authenticated proof-archive commit and manifest hash, and unique entries containing an exact archive key, raw hash, byte length and repository payload path. Permit only the predetermined new `objects/<sha256>` entries, the exact transition pointer and canonical `contracts/H.json`. Reject paths escaping the bundle, duplicated keys, arbitrary heads, budget/lease objects, normal attempts, coverage receipts and publication objects. Require raw bytes and canonical object addresses to agree before writing anything. Recheck existing immutable archive entries rather than replacing them.

The exact archived original daily snapshot head also needs to be frozen as an immutable object when that object does not already exist. The V4 head is canonical, 1,085,815 bytes, raw hash `8c7c2c5ff19ea6c1e39ac555a80760714f37cdc2208070d08f07b70a66d1166a`, and its corresponding object was absent. This makes seven permitted payloads: three inventory manifests, the descriptor, the activated contract, the transition pointer and one exact original snapshot object. The actual package must use the latest authenticated scheduled snapshot, rather than assuming this V4 head remains current. Its original bytes/date and fixed manifest pin authorize the new object; no snapshot head may be replaced by the seed.

## Production seed and acknowledgement path

`ops/ci/collect.py` currently restores and leases the archive, loads the contract, attempts scheduled reuse, then constructs the collector and runs it. `Pipeline.run` retains the current contract and run plan, but it cannot manufacture the externally approved transition descriptor or inventory manifests. `source_qualification_origin.py` fails closed when the transition pointer is absent. Merely committing the activated source declarations therefore cannot work against a restored archive that lacks those new objects.

Add one narrow seed hook after `bootstrap` and current-contract validation, before scheduled reuse, authentication/model setup, budget release or collector construction. It must require the current lease and a positive fixed authority row for `H`, validate the entire closed package first, then import only its exact allowed immutable entries with `write_once`. Resolve all three inventory origins against the resulting store and check the old-pair preservation before requesting acknowledgement.

Use the existing normal collector `checkpoint`/`GitArchive.push` path with an explicit seed phase, such as `qualification_seeded`. That path compares the restored or last acknowledged archive commit, pushes a manifest containing all prior immutable objects and the new seed, and records the acknowledgement only after the push succeeds. The source-probe checkpoint profile has a different closed envelope and should not be used for this normal collector seed. Stop before source/model work if the acknowledgement fails. A retry must be byte-identical and idempotent; an existing key with different bytes must fail. Preserve all existing budgets and mutable heads except the ordinary lease/checkpoint bookkeeping. Do not create a fake normal receipt or reset a source cursor.

The proof archive is an authenticated origin, not an assertion that every future restored head must equal that old commit. A later authenticated archive may be a verified superset containing those same immutable references. The existing restore verification and compare-and-swap push protect the actual current head; the trusted authority row and raw reference replay protect qualification provenance.

No current production importer or seed checkpoint is claimed to exist. This is a small required runtime integration, to be implemented and independently tested before activation. A manual side archive push or a state object authored after the source declaration becomes active would leave the dependency unreviewable and is not the recommended path.

The runtime canary remains strict: `coverage.contractSha256` must equal the live whole-contract hash. Importing qualification objects does not change old `79cdd…` coverage into `H` coverage. The expected sequence is pure package preflight and an explicitly uncollected preview; deliberate main activation under the existing owner authority; ordinary collector seed import and acknowledged archive checkpoint; actual `H` collection and independent receipt replay; then an actual `H` canary receipt. The public historical projections remain unchanged by activation. Do not claim a green new-policy canary from seeded objects or weaken its guard because the old receipt still exists. This is the same post-activation normal-collection boundary used for D112.

## Disable the diagnostic operation under the new policy

The new live `contracts/source-qualification-probes.json` must use exactly the closed disabled schema-2 form:

```json
{"marketSha256":"H","maxRequests":0,"operation":"disabled_qualification_probe","schemaVersion":2,"sources":[]}
```

Replace `H` with the derived final whole-policy hash and retain the exact canonical bytes, raw hash and byte length in the implementation evidence. Use canonical serialization without an added newline if raw and canonical hashes are intended to match. The historical actual V5 plan remains immutable under the original `79cdd…` policy and is replayed by `replay_bounded_candidate_diagnostic`; replacing the live plan must not change that historical replay. The disabled dispatcher must produce zero requests and suppress both generic fanout and the HTML diagnostic operation. Ordinary source collection still uses its existing independent path and limits.

## Six correction groups and public baseline

The correction stamp's outer hash is derived from the whole market hash, request-policy hash and baseline hash. The three source replacements change that outer hash. Regenerate only the required outer `policySha256` binding in `web/src/data/tracker/factualCorrectionPolicy.json`; independently prove its `groupIds`, `targetIds`, `sourceEvidenceIds` and six `reviewPolicySha256ByGroup` values unchanged. Preserve each admission, row, note, target, original date and public before/after projection. This transition grants no new correction admission or SEC claim.

An isolated three-activation-base comparison against the V4 original policy preserved all six group review hashes:

| Group | Review-policy SHA-256 |
| --- | --- |
| `FC-20261023-checkpoint-sase` | `36bc23722c1131f94ab3c2db1c553505539987aa55738cfa9bb72dfa3871ad6f` |
| `FC-20261023-expel` | `d1ea72b754450e603d89092cc38d9fa81d165575af2a36745e5938220fd82087` |
| `FC-20261023-optiv` | `4f9e7feb90232a3aafe2cd84265c2e8202c9e009229e7592c5ab87373f64bcf5` |
| `FC-20261023-splunk` | `270b7c7a1f7180b3fef2896b7633a87bf0667b9f4a3c75593fa72b959ecb87f6` |
| `FC-20261023-zscaler` | `dc8522069fc87cbf0371e0ea29ec80fbf647c1dd7ce816e02a7fb4a94b35a390` |
| `XAGE-SOURCE-CLASS-20261023` | `c01560dba484aa5aa5696c8bfe5b44acefc6337ee1cebe0cd96751849e15646a` |

Recompute and compare these against the final actual contract too; this feasibility check did not include a future origin or imply its approval.

The committed `dailyMarket.json` is currently an explicitly uncollected v2 prospective baseline, `0/557`, under `79cdd…`, preserving older facts and dates in `supersededPolicy`. `verify-daily.mjs` rejects a whole-policy mismatch and currently requires the superseded snapshot to have a coverage schema other than 2. Thus the current migration rule cannot simply wrap this v2 baseline for `H`.

The recommended small build change is a closed v2-to-v2 prospective migration selected by the independently validated three-source transition. Use a static positive migration-authority row that pins the exact original whole contract, resulting `H`, transition reference, original snapshot canonical hash, original fixture raw file hash/length and original seal. Do not add an override argument, a generic policy-repin option or a permissive fallback when an authority is missing. Reject a fourth source edit, a different original snapshot, a stripped superseded chain or a type-only change even if an attacker recomputes local seals.

Retain the exact entire old policy and snapshot, including their seals and nested historical reports, without changing original source, collection, fact or correction dates. Preserve the prior raw fixture and seal as immutable package assets, and require any embedded parsed snapshot and full superseded chain to be canonically equal to those exact original bytes. This makes byte preservation independently checkable without requiring JSON whitespace to survive embedding. Require the new public baseline to have no evaluated current-policy intake, processing or historical-review totals and zero successful tasks across the unchanged 557 obligations; retain the static facts and exact existing correction projections. Do not merely repin previously measured success to `H`. Recompute the new snapshot and file seals. Keep this build-only prospective authority separate from the normal collector, preview/cloud execution rules and actual collection policy; an actual new-policy receipt still requires the ordinary independent replay.

Alternatively, an actual independently replayed new-policy normal collection can supply a new snapshot, but that requires the acknowledged seed first and must not be fabricated to make the build green.

The transition does not replace the production legacy 244/557 report or the older 121/244 reports with qualification credit. All historical reports remain attached to their original policy, measure and dates until an actual separately admitted deployment changes what is public.

## Preservation checks and first normal collection

The archived ordinary coverage used for this feasibility analysis has run `f484565fc865f03670ad413a1e4bd5ccb4c6b6b571b5a314f4bc251d591638b0`, clock `2026-10-24T05:41:33.131823Z`, and coverage object `8dff4c5ca6a07568efaa26d1f9dd88656c83ff095c3d3eab9a5de9c6bab0eab1` (1,052,058 bytes).

| Item | Required preservation and observed feasibility |
| --- | --- |
| Old ordinary inventory | Exactly 9,914 source/URL pairs across 17 nonempty sources; pair-list hash `105fd717e7e5dc14543daca8704c792c01f166ade5d688e4d0da59dcd9371b45`. All 17 semantic source contexts were unchanged by an isolated three-base patch. |
| Reviewed bindings | Preserve all 24 original bindings, their original semantic times and full review dispositions. New qualification inventory adds none. |
| Existing review queue | Exact 32-entry queue matched the prior transition audit; canonical hash `e83deaa4f0d454ccfa391118c5d0e86ec7881ba3f87a5efef81cf3b0dc93dfe7`. Do not replace it with an empty queue. |
| Ordinary facts | Preserve the four exact original references; reference-list hash `5e2ade4b589834638b2b6b52cc9175482754d6aebdff234e1cba8cfdd632bb70`. Existing independent semantic replay remains required; this feasibility check did not rerun it. |
| Older quarantines | Preserve all four existing quarantines from the audited projection. A reviewed historical document can still have held claims. |
| Candidate ordinary inventory | All three prior ordinary manifests were empty. Qualification URLs must enter through the new typed predecessor, never a fabricated prior ordinary receipt. |

The existing `AuditIndex.predecessors`, `predecessor_inventory`, engine discovery/failure branches and independent receipt replay already union typed qualification inventory with ordinary inventory and require exact full-inventory equality. No engine change is needed for the main, earlier bounded or explicit-card entries supported today. Never let the qualification predecessor enter `resolve_origin` as a semantic origin or populate an audit cursor. The first ordinary collection must freshly traverse each source for intake credit and process eligible current/changed documents within the unchanged per-source and global limits. All remaining qualified URLs stay explicit pending history, carrying original scheduling hints and source provenance.

After actual V5 success, rerun the preservation comparison against that exact archive and the current restored superset. Independently replay the first real new-policy receipts, including partial/failed index cases, and compare source/URL sets and all fact/hold projections. New URLs increase inventory; they do not make historical review complete. A terminal-complete diagnostic also does not prove that every current article has undergone semantic review.

## Required implementation and review before activation

1. Actual V5 completeness, external run/artifact/archive authentication and full old-lead reconciliation; no invented pending pins.
2. Offline package construction, exact three-row forward/inverse proof, final disabled-plan and six-group correction-stamp projection checks.
3. Narrow leased immutable-seed importer and acknowledgement gate, including missing/corrupt object, archive race, interrupted checkpoint and idempotent retry tests.
4. Closed prospective v2-to-v2 baseline migration or a genuine new-policy snapshot; preserve facts, dates and all historical reports with zero invented current credit.
5. Independent review of authority additions, package and complete first-collection replay; then the existing preview/render/owner-promotion path.

Adversarial tests must reject an archive-authored authority row, wrong app/run/artifact/archive pin, omitted earlier card/partial result, arbitrary sitemap URL, altered original date/charge/body, wrong parser revision, extra fourth policy edit, copied verified declaration, missing transition pointer, seed path traversal, mutable-head payload, changed existing immutable bytes and collector execution before remote seed acknowledgement. The prospective migration tests must independently reject a valid-looking but unlisted v2 original/current pair, changed old fixture/seal, missing nested historical report, nonzero new intake, evaluated history/processing, refreshed date and any bypass of normal collection replay. Confirm unchanged ordinary source semantics, 9,914 old pairs, 24 original reviews, 32 queue entries, four facts, four quarantines, six correction projections, all 80 existing SEC claims, all current-fact projections, 557 obligations and the original daily budgets. Run the existing full build/current-facts/SEC checks and required rendered preview comparisons before any later promotion. No implementation or actual activation is included in this proposal.

## Dormant seed implementation addendum

The separately authorized inactive implementation is `ops/ci/html_qualification_seed.py`, its focused test module and a two-line ordinary-collector hook immediately after contract validation. The hook precedes scheduled reuse, account-auth restoration, model setup and collector construction. It does nothing, including no file/state/context lookup, when the current contract has no qualification origins. Both fixed positive registries remain empty in this implementation; no actual package or activation authority is added.

The root integration interface is:

```python
validate_seed(repo, store, contract, at)
# Pure overlay validation; None for a contract without origins.
# Otherwise: files{key: raw_bytes}, manifestSha256, contractSha256,
# preservation summary and per-source inventory counts/hashes/original completion.

seed_before_collection(repo, root, store, session, contract, session_runtime)
# Requires the existing private reviewed-main ordinary session/lease.
# Validates the full package, imports the exact immutable files, checkpoints
# qualification_seeded, verifies the ACK against runtime remote-archive metadata,
# then returns zero-credit result + archive ACK. Any failure stops the caller.
```

`SEED_PACKAGES` is a fixed empty tuple. Each future reviewed row has exactly `contractSha256` and `manifest`, where `manifest` contains exact `path`, `sha256` and integer `bytes`. Repository paths are restricted to `contracts/html-qualification-seeds/`; traversal and symlinks reject. The existing independent `ACTIVATION_AUTHORITIES` row is also required and must select the same contract and transition.

The seed manifest is canonical JSON, with exactly:

```text
schemaVersion: 1
kind: three_html_qualification_seed
activatedContractSha256: exact H
transition: immutable descriptor reference
proofArchive: {commit, manifestSha256}
files: sorted unique array of {key, sha256, bytes, path}
preservation: {
  coverage: exact existing immutable original coverage reference,
  snapshot: exact original snapshot object reference,
  protectedReferences: canonically ordered unique immutable JSON references,
  summary: exact derived summary below
}
```

`proofArchive` must equal the authenticated main diagnostic's archive pins in the independent authority row. The file-key set is exactly the seven derived keys described above. Every payload is canonical and raw-hash/size checked. Existing immutable bytes must match exactly. The imported original snapshot must retain its original content seal. The overlay fully replays all three qualification origins before any real write. Original normal coverage, facts and protected objects must already exist; only the exact original snapshot object may be supplied by the package for preservation replay.

The preservation summary has exactly `inventoryPairs`, `inventoryPairsSha256`, `retainedInventoryPairs`, `retainedInventoryPairsSha256`, `retainedBindings`, `retainedBindingsSha256`, `factReferences`, `factReferencesSha256`, `reviewQueueEntries`, `reviewQueueSha256`, `snapshotSha256` and `protectedReferencesSha256`. Derive all pairs from the complete union of each original receipt's item, pending and retained inventories; separately derive retained pairs from the retained inventory manifests. Preserve all original validated-fact references, which also include existing SEC facts; the four ordinary facts are a subset, not an assertion that the entire coverage has only four facts. Protected references must include the separately authenticated older quarantine projection/evidence objects needed by the eventual package. The summary proves byte retention and unchanged subject context; it grants no fresh semantic admission and does not replace independent original semantic replay.

Actual scheduled archive `04181beb9a26b9dee7a8bf2a853da4fea43397a8` was used for a later pure preservation check under a write/network/subprocess-denying audit hook. All 36,770 files retained their byte hashes, sizes and mtimes. Its complete source inventory includes SEC and totals 26,969 source/URL pairs; all 24 retained bindings, 52 validated-fact references and the original 32-entry queue were preserved. The archived snapshot differs from V4: its exact canonical bytes hash to `720f42ac3dffc4527140f61cea739e556321ed9ee19b4f7f0f189e4ed69afc7b` (1,085,815 bytes), with content seal `d603dd383f0654e85f54b1e5706e4d4fbf70a27a355fb32ab3610f7f7dfd0052`. This remains an original-policy feasibility result, not an activation or an actual new-policy receipt.

The ordinary seed wrapper requires the exact private repository, main ref, scheduled/manual ordinary collection event, run/attempt/session, application SHA and retained session equality. It checks the existing lease before preflight, again before import, before checkpoint and after ACK. It verifies the returned checkpoint's phase, session, application, role, contract and result, as well as the archive commit/manifest format and equality with the actual runtime acknowledgement head. Failed acknowledgement leaves only the already validated immutable imports; an identical retry is safe and still requires acknowledgement. No head, budget, normal receipt, publication or source timestamp is authored by the importer.

This addendum is an implementation handoff, not an actual activation receipt. Actual V5/H/package pins, current-scheduled continuity and independent review remain required before populating either authority registry.
