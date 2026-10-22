# Subscription-backed private GitHub runner

**Credential setup passed under D-109.** Dedicated login, refresh rotation/write-back and the
existing-project Vercel read probe and prebuilt staging are proved on fresh GitHub runners. Do not repeat login or
secret-entry requests. Publication and recurring collection remain disabled; full collection
acceptance and the production cutover are separate gates.

## Actual acceptance receipts

| Check | Actual result | Limit |
|---|---|---|
| Private host canary [39695166480](https://github.com/jessepike/sec-market/actions/runs/39695166480) | 20,035 archive files restored/hash-verified and current valid SEC response | Credential-free; no model or archive mutation |
| Dedicated account [39700686412](https://github.com/jessepike/sec-market/actions/runs/39700686412) | Official browser sign-in, encrypted login storage and real subscription call passed | Runner created its own login; no development auth copied |
| Official refresh [39701323872](https://github.com/jessepike/sec-market/actions/runs/39701323872) | Fresh-runner restore, `account/read` with `refreshToken: true`, actual token rotation, protected write-back and real subscription call passed | Not a collection or perpetual credential guarantee |
| Vercel access [39704072043](https://github.com/jessepike/sec-market/actions/runs/39704072043) | Existing project/team read passed using the saved token | Read-only; no deployment; production paths not yet controlled; publish permission not accepted |
| Durable staging [39797014280](https://github.com/jessepike/sec-market/actions/runs/39797014280) | Existing credential staged the archived prebuilt smoke payload; all 25 static files, including the detached receipt, matched byte for byte | Preview write permission passed; production unchanged; independent gate and production controls remain unaccepted |
| Corrected application [39704072065](https://github.com/jessepike/sec-market/actions/runs/39704072065) | Full application CI passed | Separate from the independent evidence-bound release gate |
| Bounded collection [39704072057](https://github.com/jessepike/sec-market/actions/runs/39704072057) | Finished 241/557, exit 2; 80 model calls; final archive independently restored and snapshot reproduced | Incomplete; no recurring trigger or publication |

[Publisher receipt](receipts/publisher-access-2026-10-21.json) ·
[durable prebuilt staging](receipts/publisher-stage-2026-10-22.json) ·
[collection and independent final verification](receipts/subscription-collection-2026-10-21.json) ·
[independent pre-work escrow verification](receipts/collection-escrow-2026-10-21.json).
The owner reports the GitHub secret-writer and Vercel tokens have no expiration.

## Diagnosed acceptance failures

Original Vercel probe [39701439701](https://github.com/jessepike/sec-market/actions/runs/39701439701)
collapsed every CLI error into one generic failure. Diagnostic rerun
[39703939654](https://github.com/jessepike/sec-market/actions/runs/39703939654) located failure in
user lookup before the project endpoint. The fixed request uses the known project ID plus explicit
`teamId` query and avoids `--scope` user discovery. The configured credential then passed without
replacement. The probe retains only fixed failure categories; remote response text and credentials
never enter logs or artifacts. Automatic CLI update checks are disabled.

First collector [39703939715](https://github.com/jessepike/sec-market/actions/runs/39703939715)
stopped in dependency setup because the current Ubuntu image lacked `pdftotext`. Neither models
nor archive operations began. The workflow now installs `poppler-utils`, checks the executable,
and initializes a nonsecret setup-failure receipt before dependency installation.

Earlier fresh-runner probe [39700921768](https://github.com/jessepike/sec-market/actions/runs/39700921768)
restored auth and called the subscription successfully but did not establish refresh rotation.
Aging `last_refresh` was insufficient in CLI 0.163.0. The corrected helper uses the official
app-server stdio `account/read` method, rather than calling OAuth endpoints directly. Its accepted
replacement is run 39701323872 above.

## Authorization and credential isolation

[OpenAI's account-auth CI guide](https://learn.chatgpt.com/docs/auth/ci-cd-auth) documents trusted
private ephemeral runners restoring managed account auth and persisting refreshes between serialized
runs. API-key and host-integration `chatgptAuthTokens` modes are rejected. D-109 supplies the
action-time approval required by D-83 for this dedicated CI setup.

| Protected repository secret | Purpose |
|---|---|
| `SMP_CODEX_AUTH_JSON` | Official dedicated runner login, refreshed by the official CLI |
| `SMP_AUTH_STORE_TOKEN` | Fine-grained repository-only Secrets read/write for refreshed-auth persistence |
| `VERCEL_TOKEN` | Existing `pikeholdings/security-market-pulse` publisher credential |

The workflow's ephemeral `GITHUB_TOKEN` supplies explicit code/evidence/Actions permissions and
cannot update Actions secrets. The development integration cannot administer secrets/billing;
its 403 responses are not evidence that the configured runner credentials are missing.
Never request credentials in chat, copy a development/local login or dump auth files/environment.

`ops/ci/auth_store.py` restores auth outside checkout with 0700 directories/0600 files and sends
only changed current auth bytes through stdin to `gh secret set`. No token enters argv or model
input. Failed persistence does not acknowledge or revert refreshed auth and stops further model
work. `GuardedRunner` checkpoints after every official execution, including failures. Bootstrap,
refresh and collection share one noncanceling account concurrency group and have no PR/fork
trigger. A crash between refresh and write-back can still require a new dedicated login.

The Vercel probe writes the owner-provided token to a fresh private temporary official CLI auth
file, strips unrelated credentials from child environment/argv and removes the file at exit.
The fixed endpoint verifies both pinned project and team IDs. Its successful receipt reports
`productionPathsControlled: false`, `publishPermissionAccepted: false` and no deployment.
Those are remaining cutover gates, not grounds to expand credentials or alter production now.

The October 22 staging probe uses the official CLI's cached team selector only after the pinned
project/team read passes. This avoids repeating the failing user discovery during `--scope`
resolution. Its temporary auth directory contains the token and nonsecret selector; deployment
children inherit no GitHub, account-auth or API credentials. The actual adapter uploads only the
retained prebuilt payload, checks all 25 static files and confirms the production receipt is
unchanged. The payload retains its old application revision and smoke-test authority. This
accepts the durable credential's preview write permission, not a fresh daily release or production
promotion. No project settings or aliases were changed and the archive was read only.

## Bounded collection and recovery

`subscription-collector.yml` accepts explicit private-preview requests/manual dispatch only.
It restores and hash-checks the latest remote evidence archive, acquires a remotely acknowledged
lease, then reserves remaining daily calls/documents/fetches in that archive before spending them.
A killed runner leaves the conservative full ceiling reserved; retries cannot reset capacity.
Normal completion checkpoints actual usage. Archive snapshots occur outside concurrent writes.

New reservations stop after twenty minutes; an in-flight request can finish within its existing
timeout. The full job has a 35-minute limit including restore/checkpoints. Each extraction and
semantic review uses a fresh isolated official CLI context, with no paid API fallback. Auth stays
outside archived state. Reconciliation retains unresolved work and writes a snapshot/matrix.
Final acknowledged archive releases the lease; incomplete coverage deliberately exits 2.
A green workflow is not required to retain an honest incomplete-coverage result.

## Remaining activation gates

1. Full collection acceptance remains incomplete: 241/557 complete, 301 not checked, 13 blocked,
   two failed; 8,557 pending URLs and 28 held claims. All 48 SEC tasks passed. Citation checks fell
   from 204 to 193 because five links returned 403, three returned 429, two 502 and one timed out.
   Actual usage was 80 calls, 39 document reservations and 412 fetches in about eleven minutes.
   Four historical source-backed events are retained in the unpublished snapshot; no supplier
   field patches. Every final archive file, reconciled receipt and rebuilt snapshot matched;
   the lease is released. Do not reset the October 22 UTC model budget for another acceptance run.
2. Complete missing source families, bounded backfill/current-claim audits, semantic delta efficiency
   and typed ownership/non-SEC financial adapters. Existing budgets do not clear the historical queue
   daily. Verify Actions usage and no-additional-charge limits before enabling recurring work.
3. Durable-credential prebuilt staging now passes. Exercise the actual independent GitHub
   exact-artifact gate and production acknowledgement/rollback,
   missed-worker alert and owner delivery. Sustain accurate daily operation. Review the concrete major
   cutover before promoting to readers or closing competing publication paths. Legacy SEC jobs stay.

The [October 22 independent collection diagnosis](receipts/collection-diagnosis-2026-10-22.json)
restored and verified all 22,468 files, reproduced the exact reconciliation and rebuilt the snapshot
using its original parent from archive history. It spent no model calls. The 8,557 pending
source/URL pairs represent 7,936 distinct URLs; Dragos's investor source alone contributes 3,256.
Twenty-seven of 28 held claims lack a usable source date. A parser correction now reads explicitly
labeled publication `<time datetime>` elements on five archived Mimecast pages and refreshes only
the affected extraction caches. Ambiguous listings, arbitrary event times and invalid dates remain
unclassified. No existing hold or coverage receipt is upgraded by that offline correction; fresh
independent model review must fit a later UTC day's retained budget.

The attempted native scheduler could not bind this repository/environment or guarantee fresh chats;
no tasks were saved or run. Do not repeat that failed UI handoff. The old environment correction
returned `stale_base`; its [portable proposal](environment-correction-2026-10-21.json) remains
unapplied and is independent of this CI route. The Mac/Linux worker remains a fallback.
