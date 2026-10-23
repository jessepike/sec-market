# Daily pipeline activation receipts

The owner approved activation and verification, including the controlled rollback and restoration,
on October 22 Pacific time. The platform remains GitHub Actions and the existing Vercel project.
No Codex Cloud scheduler, paid model API fallback, purchase or pull request is used.

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
required. Local validation passed 75 operational, 99 pipeline and nine monitor tests; application
CI passed on `ae66ee5`.

The failed attempt remains charged to both gate and publication counters. No counter was reset.
The replacement scheduled publisher must still pass a fresh independent main gate.

## Actual scheduled acceptance

The normal daily collector window passed before owner approval. A temporary October 23 06:07 UTC
cron was added, with a UTC date guard to prevent annual reuse. The regular 05:17 UTC collector and
06:23/16:23 UTC publisher schedules remain unchanged. A manual dispatch is not scheduler evidence.

The rollback check also has a one-time GitHub callback after an authentic successful scheduled
publisher. A read-only preflight outside the shared writer group requires the actual archived
scheduled collector, checks for queued/running collection and any previous drill record, and expires
after October 23 UTC. Only the mutating job receives the Vercel credential and writer group. The
manual approved-release workflow remains available. No future daily rollback is authorized.

As of 06:39 UTC, GitHub has not emitted either new scheduled run. Actual scheduled collection,
new production acknowledgement, controlled rollback restoration and the final independent
monitor receipt remain pending. This document does not yet claim completion.

## Coverage boundary

The latest pre-activation source receipt completed 244 of 557 required tasks. Missing or blocked
sources remain incomplete, and ownership remains announced rather than closed for Varonis.
One successful execution or publication does not establish full source coverage or sustained
multi-day operation.
