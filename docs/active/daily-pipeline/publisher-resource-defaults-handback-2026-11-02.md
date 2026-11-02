# Raw resource defaults diagnostic amendment handback

Exact source `d5eec6481c624d59af9e8fd0f777925c1b9c3cba` is ready for independent review.
The governing amendment specification was committed first. There has been no push or dispatch.
Only the assigned probe, focused test file and existing workflow fictional test command changed.

The receipt still exposes the original buildMachineType, buildMachineSelection and override
elasticConcurrencyEnabled fields. It now also exposes only these whitelisted diagnostics:

| Field | Meaning of the raw observation |
| --- | --- |
| resourceConfigPresent / resourceConfigType | Key presence and JSON type of the native project override object. |
| elasticConcurrencyEnabledPresent / elasticConcurrencyEnabledType | Flag key presence/type inside a valid override object. |
| defaultResourceConfigPresent / defaultResourceConfigType | Key presence and JSON type of the native default object. |
| defaultElasticConcurrencyEnabled | Native default flag only when actually boolean; otherwise null. |
| defaultElasticConcurrencyEnabledPresent / defaultElasticConcurrencyEnabledType | Flag key presence/type inside a valid default object. |

JSON types are missing, null, object, array, string, boolean or number. An invalid parent object
makes nested presence null and nested type unavailable. Absent and malformed fields remain
unknown. No raw object or unrelated native field is returned. No effective setting is inferred
from either object, default precedence, omitted keys or the SDK optional type. The staging guard
continues requiring explicit false under its existing exact rules and would still reject the
first actual null receipt.

The only workflow delta is the existing fictional credential-isolation step's test pattern:
`test_*.py` becomes `test_publisher_probe.py`. Private-repository condition, fixed read endpoint,
secrets, permissions, pinned actions, stage condition, artifacts, retention, timeout and cleanup
remain exact. Full operational guards remain in web CI. Prior hosted full-suite evidence is
retained by the parent and is not replaced by this focused run.

OrbStack verification passed 12 focused probe cases and 13 existing exact-CI guard cases with
zero skips. The existing actionlint binary passed the single modified workflow. The focused
suite covers credential/environment/caller/error handling plus the native type whitelist,
missing/null/malformed override/default combinations and workflow guard boundaries. Its first
run had a test-only wrong workflow filename (`web-ci.yml` instead of actual `web.yml`); the
failed log remains, and corrected checks pass. No production behavior changed for that fix.

The boundary receipt checks every other preexisting tracked file against `1e6aa6f97`. K source,
UI, stage adapter and strict stage guard remain exact. It also reconstructs the old workflow by
undoing only the focused pattern and requires complete byte equality. Evidence and exact hashes
are under `docs/active/daily-pipeline/receipts/publisher-resource-defaults-2026-11-02/`.

Actual first read probe 41520910334 still reports Basic/fixed/null. Its original receipt is
pinned by hash in the boundary receipt and was never edited. The parent's actual skipped stage,
credential cleanup, artifact and unchanged three-deployment inventory remain their own evidence.
A second genuine read is still needed to learn raw override/default presence and values. The
new diagnostic fields have no native proof yet. No guard relaxation follows from these fixtures.

The parent owns independent review, fresh explicit intent, the later same disabled-branch push,
native suppression watch and any read-only workflow dispatch. That workflow still skips staging
for manual events and still consumes runner/CLI setup time; this local change grants no new
spending allocation. No provider setting, token, environment, source request, archive, deployment,
main, model budget or production state changed. The paid trial remains stopped. This amendment
records the operator state here without editing the separately owned status surface.
