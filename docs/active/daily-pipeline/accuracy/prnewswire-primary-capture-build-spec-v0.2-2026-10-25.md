# PR Newswire two-current-primary capture v0.2

State: root accepted implementation scope on October 25, 2026. Actual requests, plan selection,
source qualification, normal intake, semantic admission and publication require separate units.
The original proposal is preserved byte for byte in
`prnewswire-primary-capture-original-proposal-2026-10-25.md`, SHA-256
`0fbe6cb4abf22fbaac28c3c8454cd1ee6f05e5283492650b6f57614336d7e96c`.

## Accepted amendments

Root accepts the proposal with these precise amendments. The operation permits at most two
logical GET calls. Each durable fetch charge occurs immediately before the existing guarded
transport, using the existing probe budget and escrow rules. A denied or unreached second call
is not represented as a request. Unused escrow release is not a refund of charged work.
The existing Fetcher is called with `attempt=2` to suppress automatic 5xx retries. Existing
bounded redirect handling remains, but any redirect or final URL mismatch holds the response.
No Fetcher, old parser, validator or runtime guard changes are authorized.

## Closed authority and inputs

The dormant canonical plan SHA-256 is
`01e468f5d73ddb28edbde014a0b725f7d202340a692964d01f6fd174faec7fb1`.
The active disabled plan remains SHA-256
`ef9ee1bab6cfe6202b62e8d5605393f045d11fd64bd42ea1bcea769de15c8a01`.
The accepted current policy is J
`47b9f22636f0e6ea79cf830ae90aab844d8f554d44110a5bb08f29f00266593a`.
The unchanged exact Q4 inverse reconstructs original H
`8b44bcbec679c178836408c4d98c7230a85572784b0257ef21d21d3b03b445db`.
Unchanged PRN derive_report and verify_report replay the original descriptor, both complete
original records/plans and all raw observation/body references before operation writes or charges.
A read/get adapter authenticates consumed reference bytes and lengths. The accepted descriptor
and retained report remain separately sealed. A later policy is rejected.

The only ordered targets are Cato page 1 card 1,
`https://www.prnewswire.com/news-releases/cato-networks-achieves-aws-security-competency-in-ai-security-302898714.html`,
written `Oct 06, 2026, 08:30 ET`, then Chainguard page 1 card 0,
`https://www.prnewswire.com/news-releases/introducing-chainguard-checks-reinventing-continuous-integration-for-the-agentic-era-302907718.html`,
written `Oct 14, 2026, 01:00 ET`. Both retain family `release_distribution`.

## Response and replay contract

Use unchanged PRN primary_shape plus an exact heading/card join. Required template identity,
canonical, issuer, HTTP 200, strict HTML decoding and every supplied publication date must agree.
No numeric offset is inferred from ET. All modification values remain as supplied. Missing
required identity, changed URL, redirect, unreadability or conflicting publication values holds.
Every actual returned raw body/status/failure remains retained where provided. Missing fields
remain unknown. Unreached targets receive explicit held result rows. Final reports bind the
archived raw plan, ordered requests, reservations, raw observations, bodies and completion clocks.
The existing caller binds actual app/run/attempt/event/main and finish checkpoint.

## Scope and unchanged state

Cato retains all 125 observed URLs and two older absent seeds, a 127-URL known union. Both seeds
predate September 25. Older pages 6–8 and source-wide history/recall remain unknown. Chainguard
retains all 47 URLs, five current records and its observed terminal. Neither current-primary
capture renews the original listing or primary-proof clock. Neither activates a source.

The small new module, focused tests, portable test readset and explicit collect dispatch are the
implementation boundary. No generic fanout, source policy, normal intake, seed/baseline/stamp,
request, workflow or proxy change belongs to this unit. Models, reviewed documents, gates,
coverage, semantic facts and publication credits remain zero. Existing 80 calls, 40 documents,
5,500 fetches and two gates per UTC day remain unchanged.

## Required verification

Portable tests exercise the exact consumed graph with sockets and frozen LocalStore denied,
all plan leaves/raw references, two calls at most, one wire attempt for each 503, charge truth,
success/partial/failure/unknown/denial/cancel/deadline behavior, report tampering and caller isolation.
Full original-H legacy traversal replay and continuity checks cover the eight pending request
bindings and six existing actual admissions. Run full operational tests with archive present and
freshly absent before discovery. Run full npm test, all 80 SEC claims and four production/local
1440/390 renders. Preserve initial failed logs and final passing logs outside the finish checkout.
Independent review and root acceptance precede copying, main selection or real requests.
