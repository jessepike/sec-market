# Company search and runner-efficiency Preview

## Scope

The November 2 owner request authorizes implementation of company search and runner reductions.
The exact delivery is built from latest `origin/preview` at `2aa87f5d`, preserving the original
dirty checkout and excluding every unactivated managed-runtime change. Local source, operational
and browser checks plus independent review passed. The visible search still requires owner
review of Preview before main under AGENTS.md. Prior daily activation approval remains in force.

Push one reviewed candidate to `preview`, verify its actual CI result and existing Vercel Preview,
then present that concrete result for the required owner review. Do not promote main until the
visible change has that review. Production publication still needs main's new code-bound gate
and matching accepted/public bytes. A push or green CI is not publication.

## Normal Preview cost bound

This is the requested site's normal development Preview, with the paid managed-runtime trial
remaining stopped. No proof-project build, Workflow, worker, lease, credential or trial-copy call
is permitted. Do not use the $0.30 approval as additional budget for this release.

The actual production reader's Basic setting applies to this project. The latest actual build
used two cores / 8 GB and charged $0.007. The current reported site subtotal is $0.01133548;
continuing proof storage remains separately counted, despite a missing partial-day row.

Permit one Preview build only. Observe the actual deployment immediately after push and cancel
it if its build class differs from Basic or the build has not completed within two minutes.
Reserve $0.014 for that build, $0.0042 for its complete additional thirty-day storage bound,
$0.0001 for the currently observed proof storage rate, and $0.015 for remaining traffic, lag and
tax uncertainty. Together with the observed subtotal this conservative planning total is about
$0.04464, below $0.05. This is a planning bound with a cancellation safeguard, not a provider
hard cap or a settled full-day bill. Unknown, missing or excess charges stop further paid work.
Do not make another build, retry or production deployment from that reserve. Later production
uses fresh actual cost evidence and its normal publication controls.

The existing completed Basic release supplies today's genuine scheduled-production proof;
this new Preview cannot substitute for it or establish a complete successful Basic operating day.

## Review evidence

Company-search renders at 1440px and 390px and exercised source/dialog/keyboard/empty/reset cases
are recorded in the company-search spec. Runtime reductions preserve the actual collector and
publisher authority, the independent artifact gate, budget counters and failure alerts.
The independent review and exact-delivery operational/watchdog checks are retained beside this
plan. Do not remove records or raise paid budgets to make the forecast fit.
