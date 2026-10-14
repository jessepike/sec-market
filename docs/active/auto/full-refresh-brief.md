# Full live-field refresh — owner authorized 14 October 2026

Read `docs/active/auto/collect-brief.md` and follow its sourcing, evidence, byte retrieval, hashing, no-judgment and no-git rules. The owner explicitly requests all live data points checked now and nightly. These amendments supersede narrower incremental scope in that brief.

Do not spawn helpers. Use the existing Claude subscription only. Do not read secrets, credential/config files or unrelated projects. Do not run deployment, git, package installation, scheduler or credential commands. Public sources only; never bypass source blocks. At most three attempts per URL.

## Required coverage

Check ALL 74 tracked suppliers, not just public SEC filers. For each supplier:

1. Check its current primary company/parent newsroom, IR/results page, funding/ownership announcements and the existing primary documents supporting its displayed facts. Use the existing fallback chain where needed. Look through today's date, not just the older snapshot window. Every retained headline metric, funding round and ownership claim needs a real source check. Check for newer disclosures; a successfully fetched old release alone does not establish that no newer disclosure exists.
2. Refresh `headlineMetric` with the company's own exact label/value/qualifiers/reporting period; `lastRound` with date, stage, amount, lead and valuation where disclosed; `ownership` with the exact relationship, buyer, announcement/close dates and consideration where disclosed. Never change a claim's publication date to today's check date. Missing new disclosure and failed retrieval are different outcomes.
3. For suppliers WITH `edgarId`, do not edit revenue: the deterministic SEC runner owns it. For the two public suppliers without quarterly XBRL coverage and for segments with separately reported revenue, check their primary reports and update `revenue.latest`/`prior` only when the actual labelled, comparable figures and supporting evidence exist. Never substitute a parent's whole-company figure for a security segment. Preserve raw precision and greater-than/approximately qualifiers. Do not manufacture growth when comparable periods are absent.
4. Check supplier name, ticker and ownership classification against primary sources. Update `name`, `ticker` or `kind` only for a sourced factual identity/ownership change, with an evidence record and explicit explanation in the coverage report. Do not change ids, domain membership, CIKs or `edgarId`.
5. Append all newly verified dated company events since the since-date to `tracker/events.ts`, with primary evidence. Append-only history stays intact. Do not relabel an old event as new. Existing locked issues and the archived thesis are historical records and outside the live refresh.

Allowed writes are the original brief's data paths and `.collect/` plus the factual supplier changes above. Do not edit code, generated EDGAR/filing files, workflows or generated coverage. Do not overwrite earlier evidence records; append a new version for a corrected or newer document.

## Mandatory coverage receipt

A submissions index is only a discovery aid. It never verifies a retained ARR/customer/funding/ownership claim by itself. For EVERY populated `headlineMetric`, `lastRound`, `ownership`, and non-EDGAR `revenue` group, fetch/read the specific existing primary document cited in that object's `evidenceIds`, confirm every retained property against it, and include its exact canonical URL plus actual body hash in `sourceChecks` and that field's `sourceUrls`. ALSO check the current company/parent newsroom or IR/results page for newer announcements, even for SEC filers. Record discovery URLs separately in `discoverySourceUrls` on that field. A private/acquired company may have an inactive historical SEC CIK: its empty submissions index does not establish its current identity, owner, metrics or new-event coverage. Search the company/parent's active primary sources. No readable current discovery source means `failed`, even if an old release is readable. `not-applicable` is permitted only for an absent field or a deterministic SEC-owned revenue group, never a populated live claim. If exact cited documents cannot be read, retain claims and mark `failed`; do not imply freshness from old filed-index silence.

Write `.collect/supplier-checks.json` as a JSON array with exactly one entry for each supplier, even if every source fails:

```
{
  "supplierId": "existing-id",
  "checkedAt": "actual ISO UTC timestamp",
  "sourceChecks": [
    {"url":"https://...", "checkedAt":"...", "status":"ok", "httpStatus":200, "sha256":"actual fetched-body SHA256"},
    {"url":"https://...", "checkedAt":"...", "status":"failed", "httpStatus":403, "reason":"blocked after three attempts"}
  ],
  "fields": [
    {"field":"identity", "status":"checked-no-change", "sourceUrls":["https://..."], "discoverySourceUrls":["https://.../newsroom"], "reason":"what was verified"},
    {"field":"headlineMetric", "status":"updated", "sourceUrls":["https://.../release", "https://.../newsroom"], "discoverySourceUrls":["https://.../newsroom"], "reason":"new disclosure, exact period"},
    {"field":"lastRound", "status":"checked-no-change", "sourceUrls":["https://.../funding-release", "https://.../newsroom"], "discoverySourceUrls":["https://.../newsroom"], "reason":"last round verified and newsroom checked for newer disclosures"},
    {"field":"ownership", "status":"failed", "sourceUrls":["https://..."], "reason":"could not verify; retained previous claim and period"},
    {"field":"revenue.latest", "status":"not-applicable", "sourceUrls":[], "reason":"owned by deterministic SEC runner for this edgarId"},
    {"field":"revenue.prior", "status":"not-applicable", "sourceUrls":[], "reason":"owned by deterministic SEC runner"},
    {"field":"events", "status":"checked-no-change", "sourceUrls":["https://.../newsroom"], "discoverySourceUrls":["https://.../newsroom"], "reason":"no new sourced events found through actual check date"}
  ]
}
```

Allowed field statuses: `updated`, `checked-no-change`, `unavailable`, `failed`, `not-applicable`. `unavailable` means sources were actually checked but this field is not publicly disclosed. A field with failed required checks is `failed`, with its old value retained. Do not mark an unchecked supplier or field as checked. Record exact failures, not an empty failure list just because no new event was found. Each successful field status must reference at least one successfully fetched source in its supplier receipt (except deterministic SEC-owned fields). Hash actual bytes, never an invented body or a URL string. Keep the required `failed-sources.json`, `candidates.json` and `summary.txt` too.

Work steadily through every supplier. Persist the receipt after EACH supplier, beginning with any completed checks from a resumed session. If you cannot finish, leave the partial per-supplier receipt intact and name all unchecked ids in the summary; missing coverage must remain visible to the pipeline.
