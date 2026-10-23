# Daily pipeline activation receipts

Owner: "Approve activation and verification". D-110 records this approval for the reviewed daily
facts pipeline, including controlled rollback and restoration, on October 22 Pacific time.
The platform remains GitHub Actions and the existing Vercel project.
No Codex Cloud scheduler, paid model API fallback, purchase or pull request is used.

## Current checkpoint: October 23, 07:02 UTC

Canonical `main` and `preview` are both `7bd94ec77e99462c068f254e134235a894585cbb`.
Production remains `54590be4d91113a50879a8fb5d180441e7d149f4`. No actual new scheduled
collector or publisher event had been emitted by GitHub at this checkpoint. This record does not
claim live daily publication, successful controlled rollback or sustained operation.

The current operational suite passed 83 tests in OrbStack. Application runs
[39914573163](https://github.com/jessepike/sec-market/actions/runs/39914573163) and
[39914570279](https://github.com/jessepike/sec-market/actions/runs/39914570279), and fresh-runner
canary [39914569790](https://github.com/jessepike/sec-market/actions/runs/39914569790), passed.
Fresh read probe [39909753143](https://github.com/jessepike/sec-market/actions/runs/39909753143)
confirmed the installed Vercel production-path controls.

## Completed cutover steps

- Disabled the legacy certified refresh and automatic main-promotion workflows.
- Set Vercel automatic custom-domain assignment to false and installed the production Git-build
  ignore command. The live legacy application receipt stayed unchanged during the main advance.
- Fast-forwarded main from the reviewed preview. Main gate
  [39908495114](https://github.com/jessepike/sec-market/actions/runs/39908495114) passed 389 tests
  on application revision `0c85b9dadc2769a6b12275964795e849439ae2c2`.
- The exact production-target upload became READY at
  `https://security-market-pulse-2g3go58lw-pikeholdings.vercel.app`, deployment
  `dpl_H8u33zorXBd6TZ8tgaG8YADYJBUQ`. Its artifact SHA-256 is
  `1094bd40eea0ffc1570aa12e54f308435e8ae72b9ba622139d88ab4726ad0d3a`.

## First production attempt and correction

Publisher [39908275916](https://github.com/jessepike/sec-market/actions/runs/39908275916) failed
after its exact upload and remote pre-promotion checkpoint. Production remained at
`54590be4d91113a50879a8fb5d180441e7d149f4`. The assigned-owner publisher alert is
[issue 9](https://github.com/jessepike/sec-market/issues/9).

The pinned official CLI routes its high-level promotion and rollback commands through account
lookup. The adapter now uses the official project API routes with the existing explicit team ID,
checks that each immutable target is READY and belongs to this project, and waits for the live
application receipt before accepting an alias change. Error receipts retain fixed phase and failure
categories. Alias changes also verify the pinned project controls, restoring only automatic domain
assignment to false if Vercel enables it. The immutable target, existing ignore rule and team remain
required. Later validation is recorded in the current checkpoint above.

The failed attempt remains charged to both gate and publication counters. No counter was reset.
The replacement scheduled publisher must still pass a fresh independent main gate.

## Actual scheduled acceptance

The normal daily collector window passed before owner approval. Temporary October 23 06:07 and
07:07 UTC crons were added, with a UTC date guard to prevent annual reuse. The regular 05:17 UTC collector and
06:23/16:23 UTC publisher schedules remain unchanged. A manual dispatch is not scheduler evidence.

The initial publisher holds until an actual completed-success scheduled main collector has an
immutable run-and-attempt receipt matching the current contract, GitHub identity/revision and
latest reconciled source coverage. This waiting hold consumes no independent-gate attempt. A
verified `workflow_run` callback from genuine scheduled collection can start the publisher after
its read-only concurrency preflight. No callback is relabelled as a scheduled publisher event.

For the temporary acceptance expressions only, a later real timer may verify and reuse prior
successful scheduled source work from the same UTC day. It checks the archived receipts and
replays reconciliation while retaining the original source check time and coverage hash. It makes
no model or source-fetch call and changes no budget or latest collection head. The new immutable
clock explicitly reports `source_work_reused` and the source GitHub run ID. Normal daily and manual
collection behavior is unchanged. [Acceptance details](scheduled-acceptance.md).

The rollback check also has a one-time GitHub callback after an authentic successful publisher
from either its scheduled event or its genuine-source callback. A read-only preflight outside the shared writer group requires the actual archived
scheduled collector, checks for queued/running collection and any previous drill record, and expires
after October 23 UTC. Only the mutating job receives the Vercel credential and writer group. The
manual approved-release workflow remains available. No future daily rollback is authorized.

As of 07:02 UTC, GitHub has not emitted either new scheduled run. Actual scheduled collection,
new production acknowledgement, controlled rollback restoration and the final independent
monitor receipt remain pending. This document does not yet claim completion.

## Coverage boundary

The latest pre-activation source receipt completed 244 of 557 required tasks. Missing or blocked
sources remain incomplete, with 254 missing family bindings and 28 held claims. Ownership remains
announced rather than closed for Varonis. The October 23 ledger retains 80 charged model calls,
40 document reservations and 5,367 of the explicit 5,500 fetch ceiling. Cancelled-run reservations
and the failed gate/publication attempt were not refunded or reset.
One successful execution or publication does not establish full source coverage or sustained
multi-day operation.
