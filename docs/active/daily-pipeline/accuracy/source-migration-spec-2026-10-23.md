# Historical source inventory migration

Prepared October 23, 2026. This repairs offline reproduction of the frozen 177-record source
audit after the original manual data moved from TypeScript arrays into `originals.json`.
It does not audit the effective corrected view or admit any factual correction.

## Contract and plan

Keep the original benchmark inventory, three review ledgers, source-binding input manifest,
historical source hashes and verdicts byte-identical. The existing mode continues to require
the historical TypeScript file hashes and decode those arrays without executing TypeScript.
It fails when those files have changed; there is no automatic migration fallback.

Add an explicit `--source-migration-manifest` option together with the required
`--source-migration-sha256` raw file pin. The new migration manifest independently pins the
unchanged historical input manifest, current original JSON bytes and factual baseline bytes.
Both arguments are required together. All migration input paths resolve inside the supplied
repository root.

The migration verifier must check the exact schemas and all canonical before-value hashes for
all 97 original events, 74 suppliers and 273 evidence records against the pinned baseline. It
then derives the historical benchmark from those original events and non-SEC supplier fields,
compares all 177 benchmark records exactly with the pinned frozen inventory, and compares every
one of its 144 relevant complete evidence objects with the original JSON. Missing, extra,
duplicate, changed or forged records fail. The original review/source proof checks continue
unchanged after that binding. No effective projection or TypeScript runtime is consulted.

The actual pins verified before implementation are:

- `web/src/data/tracker/originals.json`: `7d164cb81003db0a66eccbb25c2e8605e33b853b9a6e20cb2c6900794822b4a3`.
- `contracts/factual-baseline.json`: `ab3bca0e49a38495d310021857ee2c1a3ca6ebe7979593d1e8b36437cb2a294e`.
- Historical input manifest: `1f692bfd905abf999249e811a28ad047fe48a21fc07d766f862f3b73ca4a29ca`.

## Verification and receipt

Add adversarial tests for altered migration pins, original and baseline bytes, every inventory
class, untouched records, benchmark and relevant evidence substitution, missing/duplicate IDs,
changed historical inputs, explicit option pairing and continued old-mode failure. Run Python
only in OrbStack, then run the actual CLI against the restored read-only archive with the
explicit pinned migration manifest. Write a new report with distinct migration metadata,
`semanticAdmission: false` and the unchanged 90 supported, 71 insufficient, five contradicted
and 11 missing-primary-source findings. Do not rewrite the historical reports or their inputs.

No network, model call, quota change, source timestamp renewal, archive write, publication or
Git operation is part of this migration.

## Actual verification result

The migration manifest raw SHA-256 is
`2824776f6c739161f93a6fe8107a1599eeacaff968ce29e9ad2ea55ee65240a6`.
All 24 targeted Python tests passed in OrbStack, including the retained old-mode checks,
adversarial migration tests and a real-repository regression using the exact committed migration
manifest SHA without archive access. The actual explicit CLI replay against the restored archive wrote
`source-migration-bindings-2026-10-23.json` and its Markdown companion. It verified all 177
records and reproduced the unchanged 90 supported, 71 insufficient, five contradicted and
11 missing-primary-source findings. Every output record, verdict counter, partition, historical
input pin and historical source hash equals the earlier binding report. The original inventory,
three ledgers and input manifest retain their original raw byte hashes.

The report retains historical application revision `7bd94ec77e99462c068f254e134235a894585cbb`.
Its old TypeScript source hashes remain metadata about that historical reviewed application;
migration mode does not claim those hashes describe the current refactored TypeScript files.
The separately pinned current original JSON and baseline, all 444 before-value object hashes,
177 exact benchmark records and 144 complete relevant evidence objects establish the migration
binding. `semanticAdmission` is false. The current effective corrected facts are not audited.

The old CLI mode was also exercised against the current checkout. It exited 2 with
`Dataset hash differs: web/src/data/tracker/events.ts` and wrote no report. No automatic format
fallback or renewal of source retrieval dates occurred.
