# Subscription-backed private GitHub runner: proposed replacement

The owner's October 21 screenshot confirms the native scheduler handoff failed. The scheduler
available in that chat supports prompts/times/timezones but cannot retain this repository and
published environment or guarantee fresh cloud chats. No task was saved or run. Do not send the
owner through that same setup again, or treat natural-language instructions as environment binding.

## Actual private-runner proof

[GitHub run 39695166480](https://github.com/jessepike/sec-market/actions/runs/39695166480)
passed in 37 seconds on commit `a9b0ad292fbd7b9e8d7d11e94d24b44343f47d21`.
Its actual log receipt confirms all 20,035 remote files were restored/hash-verified and a fresh
Cloudflare SEC companyfacts response returned HTTP 200 with valid CIK/facts. No model call,
credential transfer, archive mutation or deployment occurred. The archived full-site result remains
252/557 incomplete. [Bounded receipt](receipts/github-host-2026-10-21.json).
[Full application CI 39695166516](https://github.com/jessepike/sec-market/actions/runs/39695166516)
also passed. These prove hosting/source reachability, not subscription auth or daily activation.

## Documented mechanism and concrete credentials

[OpenAI's account-auth CI guide](https://learn.chatgpt.com/docs/auth/ci-cd-auth) explicitly covers
trusted private ephemeral runners: restore managed ChatGPT auth, run Codex using its subscription,
and persist the refreshed auth before the next serialized run. It excludes API-key and
`chatgptAuthTokens` host-integration auth. This requires a **dedicated official Codex account login**
for this job stream. Do not copy this development session's credentials or a concurrently used
local login.

The proposed store uses GitHub's encrypted Actions repository secrets:

| Secret | Purpose | Minimum scope |
|---|---|---|
| `SMP_CODEX_AUTH_JSON` | Created by a runner bootstrap after official browser/device sign-in, then refreshed by the CLI | This private worker only; never in Git, logs, caches or artifacts |
| `SMP_AUTH_STORE_TOKEN` | Write the refreshed login back to `SMP_CODEX_AUTH_JSON` | A fine-grained GitHub token restricted to `jessepike/sec-market`, repository Secrets read/write |
| `VERCEL_TOKEN` (publisher stage) | Durable authorization for the existing `pikeholdings/security-market-pulse` publisher | Minimum available scope for that existing project/team; protected GitHub secret |

The earlier Vercel browser approval proved management/staging in one interactive VM. Its temporary
auth directory is absent in the new session; it was not installed as unattended publisher auth.
The publisher credential must be separately provisioned and tested before automatic publication.
No new Vercel service, project or subscription is needed for that requirement.

The workflow's short-lived `GITHUB_TOKEN` handles code/evidence/Actions/alerts with explicit job
permissions. It cannot update Actions secrets. On October 21 the existing Codex GitHub integration
could read/push this private repository and inspect Actions runs, but both Actions permission
administration and the secret public-key endpoint returned **403 Resource not accessible by
integration**. Repository-level `admin: true` does not grant those missing integration scopes.

Owner approval is required before creating this login/token or placing credentials in CI.
[D-83](../../../decisions.md) explicitly says: "Do not copy local Max credentials to CI, create
tokens, add OAuth grants or expand material access without explicit action-time approval."
Later D-104/D-105/D-108 preserve this boundary. No such credential has been created or transferred.
After approval, the owner enters only the repo-restricted secret-writer token in GitHub's protected
Actions secret UI. A bootstrap runner then starts official Codex device sign-in; the owner approves
it in the browser, and that runner saves its own dedicated auth directly into `SMP_CODEX_AUTH_JSON`.
The owner never needs to handle or paste the auth JSON. The bootstrap/device flow itself must be
proved on the real runner; no such login has been started. Never paste a token or login file into chat. No new access is required merely to inspect the proposed code or canary.

## Prepared and testable implementation

- `ops/ci/auth_store.py` validates managed account auth, restores it into a private outside-checkout
  directory (0700/0600), and sends only changed, current auth bytes through stdin to the official
  `gh secret set` client. It never sends credentials on argv or into model input. A failed write
  does not acknowledge or revert refreshed auth and must stop further model work. Host-integrated
  auth, API-key mode, missing tokens, unsafe paths and symlinks are rejected. This helper is not yet
  wired into an active subscription worker. Its tests use fictional values only.
- `.github/workflows/subscription-runtime-canary.yml` is an actual bounded GitHub-hosted test,
  triggered by changes to its canary files on preview. It uses only GitHub's existing ephemeral
  read-only token to restore the real private evidence archive, verify every hash and probe one
  registered SEC source. It transfers no subscription credential, calls no model, changes no
  remote state and deploys nothing. Its small artifact explicitly records whether that test passed.
  A green host test is not subscription-worker acceptance or full-site coverage.

## Remaining activation sequence after approval

1. Verify the canary's actual GitHub receipt. Confirm Actions minutes and a spending limit that
   prevents additional charges; subscription model usage does not make runner CPU time unlimited.
   Billing/secret administration cannot be verified using the current integration's scopes.
2. Add the repo-restricted secret writer through GitHub's protected UI, then run a dedicated
   official device sign-in on the bootstrap runner and let it create the encrypted auth secret.
   Never copy a local/development login. Verify both protected secrets without exposing values. Use one workflow-wide concurrency group with
   `cancel-in-progress: false`, no PR/fork trigger and a reviewed exact code pin.
3. Wire the auth helper into the subscription adapter outside model subprocesses. Restore state
   and budgets first. Run one bounded real auth probe, save any refresh immediately, and checkpoint
   changed auth after model requests and on failure. If persistence fails, stop model work and alert;
   do not restore an obsolete bootstrap copy. A crash between refresh and write-back can still
   require reseeding; unattended auth is not promised to last forever.
4. Collect once daily, with reconciliation each run. Each extraction/review already uses a fresh
   isolated CLI context, so independent semantic review does not depend on native chat scheduling.
   Retain the separate deterministic GitHub release gate and outside freshness watcher. Start with
   a bounded canary before spending the full collection allowance; measure runtime/capacity before
   enabling a daily schedule within the account's existing Actions allowance.
5. Prove secure refresh write-back and restore from a second fresh runner, a deliberate failure/
   missed-run alert, complete source coverage, exact-artifact staging and rollback. Only then review
   the concrete major cutover. Publication stays disabled and legacy SEC jobs remain operational.

The scheduler failure is a new operational finding, not approval to transfer credentials or
purchase API usage/infrastructure. Current full-site collection remains incomplete at 252/557.


The old cloud environment draft also rejected the instruction correction with `stale_base`.
Its portable [complete proposed start-instruction change](environment-correction-2026-10-21.json)
is preserved here and is not applied. The GitHub host path does not depend on publishing this
old environment; do not send the owner through new onboarding merely to continue CI work.
