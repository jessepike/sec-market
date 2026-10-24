# Independent review of the dormant neutral SEC diagnostic

Date: 2026-10-24. Verdict: no remaining actionable issue found in the reviewed standalone unit after the final timestamp fix. Keep dispatch and source activation separate until their exact transitions and external run evidence are reviewed.

## Reviewed bytes

All paths below are relative to `/Users/jessepike/code/projects/sec-market-finish-20261022`.

| File | SHA-256 |
|---|---|
| `web/scripts/pipeline/neutral_sec_qualification.py` | `f9eb6f9c193d8a21a13573269606af6590e999853bb1175aae660e394166beab` |
| `ops/ci/test_neutral_sec_qualification.py` | `3802f9d0c9038ec1af31aba64a3e2a62df8180dfa3c8aa2f13476bb2e4c1755d` |
| `docs/active/daily-pipeline/accuracy/four-neutral-regulatory-targeted-probe-spec-2026-10-24.md` | `a716e38dc693222a2309fb3cc7bd8d655bcaf11edc4de5a2994259c21d15e62e` |
| `docs/active/daily-pipeline/accuracy/four-neutral-regulatory-bindings-spec-2026-10-24.json` | `9928884e5b0b9ec99811f09033fe1477ecde2353c012a634dd83317a63769526` |

## Resolved finding

The original module guarded before capturing its final timestamp, leaving a gap during that capture. An independent temporary fixture advanced the clock on the second outer clock call after both pairs finished. Monotonic expiry previously returned both pairs ready; UTC rollover instead raised an exception after four charged requests, losing the normal partial-report return.

The final code at lines 151–169 places the timestamp between two budget guards and records any denial before deriving readiness. Both exact counterexamples now return independently replayable partial reports with four original charges, a retained deadline or UTC-day denial, and both pairs incomplete. Cancellation after the first fetch retains one charge and incomplete evidence. No next-day reservation occurs. These checks used temporary fictional stores and fetchers.

## Guard review and verification

The closed plan requires exact integer limits, two ordered supplier pairs and the full original candidate contract. Both pairs' declarations must match the fixed reviewed proposal, including separate index/document source IDs, issuer CIK/name and parent relationship. The exact proposal bytes, original relationship observations, primary bodies and submissions identities are read before transport. A malformed second pair cannot permit requests for the first pair.

Report verification reconstructs fresh root/required older-page joins, issuer identity, the 365-day selection and each primary response/readable-text reference. It checks separate source partitions, original observation times, exact request order, the contiguous charged interval, source and operation caps, unchanged semantic counters, and independently derived readiness. A failed root or older page supplies no selected-document authority. Redirected, conditional, blocked or unreadable primary responses cannot complete evidence. The full selection remains recorded when the 100-body guard prevents requests. The maximum operation is 280 logical reserved fetches within the existing shared 5,500 cap; it does not measure individual HTTP retry exchanges.

The reviewer ran all 21 focused tests in OrbStack, with no skips. The actual relationship preflight exercised the fixed authority against the authenticated local 9c archive and checked all 35 selected entries' hashes, sizes and modification times before and after. It reproduced the original 12/17 primary selections using in-memory candidate declarations and the original `2026-10-23T11:34:15.010723Z` audit time. This check did not reauthenticate the entire archive or obtain current responses.

Thirteen additional independent temporary-fixture cases rejected float/bool substitutions in the closed plan, wrong issuer CIK/name, redirected and HTTP 304 primaries, a blocked older page, charge offsets, a floating-point zero counter and a missing body reference. The exact final-clock and cancellation cases were separately rerun. Historical replay in the focused suite retained the original raw plan after live-plan replacement and rejected altered run envelopes without transport or store writes.

The focused command was `orb run -m dev ... python3 -m unittest discover -s ops/ci -p test_neutral_sec_qualification.py -v`, with bytecode writing disabled. Runtime experiments wrote only temporary fictional fixtures. This review created only this document; it made no source, model, archive, quota, registry, plan, Git or publication change.

## Acceptance boundary

The fixed relationship proposal authorizes only the reviewed historical parent relationship. The standalone module does not authenticate external GitHub Actions provenance, perform the future whole-policy forward/inverse transition, register a source, preserve normal predecessor inventories across a new policy, or route its operation through the leased caller. Those are explicit later integration requirements in the spec. Its internal replay can establish consistent diagnostic evidence only; rehashing a report cannot authorize activation.

Before requests, integration must retain the exact original candidate contract and proposal object and route this operation exclusively through the existing leased reservation/CAS path. Before activation, it must independently authenticate a genuinely complete run, bind a positive SEC authority entry, preserve the old inventories/corrections/dates, and review the exact candidate-addition and activation policy changes. No actual complete SEC diagnostic or qualification was established here. All 557 obligations and existing coverage remain unchanged.
