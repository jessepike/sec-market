# Retain unexpected opened HTTP responses in diagnostics

## Actual defect

Seven-source diagnostic 40131875060 retained Check Point's exact error, "Unexpected source
response status", but lost the numeric status and response observation. The fetcher raises after
opening the response, validating its final host, reading within its size limit and before archiving
or returning the observation. The numeric status is unknown; do not infer 206. Trend's separate
HTTP 200 HTML response is already retained and is outside this defect.

## Narrow correction

Add a strict-boolean, default-off unexpected_status_diagnostics keyword to Fetcher. Only the
already validated schema-1 source-probe caller opts in. Ordinary collection, Orca's separate
redirect diagnostic and other diagnostic schemas retain their current construction/behavior.
The operational plan stays disabled ad1 and main stays fixed at 6d5e87fe during current-H
scheduled collection and production acceptance. This patch is prepared on preview only.

After the existing final-host and complete bounded-body checks, an opted-in opened response
whose status differs from 200 returns a failed observation with its exact requested/final URLs,
actual numeric status, fetchedAt, existing contentType field, complete content-addressed body
reference and fixed UNEXPECTED_HTTP_STATUS errorCode. Existing source/host/DNS/TLS, maximum
body size, header handling, rate limit, HTTPError/304 behavior, retries and request counts remain.
Do not follow another URL, read again, archive an oversized prefix as complete, copy arbitrary
headers, catch a policy error or relax successful-response acceptance. With the option off, the
existing exception remains byte-for-byte equivalent in behavior and no failed body is stored.

The caller already archives returned observations and stops before discovery parsing when
status is failed or HTTP status is not 200. Failed bytes cannot supply successful proof, source
qualification, source-check credit, facts, semantic processing or publication. Original failed
receipts remain unchanged. This correction adds no observation to the old Check Point request.

## Verification and ownership

Worker owns fetcher.py, the narrow schema-1 caller in ops/ci/collect.py and a new focused
operational test module. The one pre-existing schema-1 constructor assertion in the Orca
diagnostic test module may be renamed and updated to expect this intended opt-in; all its other
cases remain. Preserve concurrent edits; no other code, contract, plan, workflow,
source authority, budget, state or Git mutation is part of implementation. All runtime/tests
run in OrbStack with fictional HTTPS responses and temporary state, without source/model calls.

Prove default parity for successes and unexpected opened responses; actual opted-in status,
URL/time/body identity; strict boolean; zero changed wire/retry counts; unchanged HTTPError/304
behavior; unsafe and oversized responses still reject before retention; only schema 1 opts in;
failed observations are retained by the actual diagnostic loop with zero credit and rejected as
request proof. Run focused tests and the complete operational suite. Return a concise handoff
with file hashes, tests and limitations, then stop writes for independent review. Root owns
preview review/build/render verification and any later promotion after actual H acceptance.
