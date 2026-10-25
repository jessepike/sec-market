# Independent review of the bounded Q4 controller capture

October 25, 2026. Verdict: **pass for dormant future preview work**. Two review passes
found three material draft defects; all three are fixed and independently retested.
There are no open material findings. This review does not authorize a real capture,
promotion, source qualification, publication or scheduled-acceptance claim.

## Scope and evidence

Reviewed the governing specification, the new capture module, the small source-probe
caller diff, the dormant plan and focused tests. Only the review Markdown and companion
JSON were written by this reviewer. All Python ran in OrbStack dev. No market/model
request, lease, dispatch, archive write, actual budget reservation, commit or push occurred.

The specification's premise is supported by the actual seven-source archive. The
unchanged historical proof helpers accept all three original charged parent rows from
diagnostic 40131875060. Each authentic JFrog, Rapid7 and Rubrik HTML body contains one
literal declaration for each permitted script, with no HTML base. The original prior
plan, source digest, supplier, request/final URL, body and fetched-at clocks remain bound.
No script contents or downstream data endpoint are established by those parent bodies.

The module permits exactly three ordered candidate sources and six ordered literal
URLs. Closed plan and proof shapes, exact H/source hashes and original charged-request
replay prevent borrowing another source or proof. The parser rejects duplicate,
unquoted, encoded, extra or conflicting attributes, inert contexts, self-closing inert
tags, inline bodies and HTML bases. There is no generic URL equivalence or inferred Q4
endpoint authority. See `q4_controller_capture.py:59`, `:111` and `:154`.

`collect.py:249` performs the complete Q4 preflight before the operation's writes or
reservation. Its route uses the existing bound budget, lease, escrow acknowledgement,
Fetcher retry/redirect behavior and stop guards. It bypasses generic candidate fanout.
The whole operation has six logical fetch reservations; existing transport retries and
redirect observations are not a six-wire-request guarantee. Existing bootstrap and
rejected-plan failure receipts remain available. The ordinary schema-1, disabled and
Orca routes retain their previous behavior.

Raw observations and bounded bodies are retained before content classification. A
captured controller requires exact final URL, HTTP 200, no observed redirect, ordered
same-day response time, explicit JavaScript MIME and nonempty UTF-8 bytes. Failed MIME,
decode, HTML/JSON/empty content and known unexpected HTTP status remain inspectable;
unknown network/HTTPError metadata stays unknown. No code executes or recurses. These
checks establish capture plausibility, not controller semantics or source completeness.
See `q4_controller_capture.py:165`, `:191` and `:255`.

Report replay reconstructs the exact targets, observation bindings, body references,
reservation sequence, denial counts and counters. Every result keeps qualification,
semantic admission and coverage false, zero credited checks/model calls and empty
facts. Completion rechecks day, deadline and cancellation at module and caller seals.
A reservation stays charged after a later denial. Before-invocation denial has no
request time; a real failed attempt retains its actual ordered request time.

## Review passes and resolved findings

Pass one checked the specification against actual retained proof and the existing
onboarding/caller contracts. The specification was clarified to distinguish
operation-specific preflight writes from existing bootstrap/failure receipts and to
preserve unknown failure fields rather than manufacture response metadata.

Pass two reviewed and exercised the stable implementation, then repeated focused checks
after each material fix. The following findings are closed:

| ID | Draft defect | Verified repair |
|---|---|---|
| Q4-IR-01, major | The verifier indexed `maxRuntimeSeconds`, which actual H omits. | It uses the existing 7200-second contract default. Actual H passes execute, caller finalization and replay. |
| Q4-IR-02, major | Failed-transport attempt times and backwards completion could escape replay validation. | Every actual attempt requires ordered same-day clocks; completion cannot precede start. Forged-clock mutations fail. |
| Q4-IR-03, major | Midnight between the last guard and request marker stopped transport but could make denial reconstruction fail. | The uninvoked marker is cleared; one charge, genuine completion time and repeated denials survive module/caller sealing. Zero wire calls occur. |

The implementation worker also rejected self-closing inert HTML contexts after spotting
the browser/parser ambiguity. The final focused tests cover this stricter behavior.

## Independent checks

* All 18 focused tests pass with zero skips, including both actual-archive tests. Command:
  `orb run -m dev env PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s ops/ci -p test_q4_controller_capture.py -v`.
* Eight selected previous-route tests pass with zero skips: exact disabled plan,
  unknown schema-2 rejection, literal schema-1 proof, last-target preflight failure,
  leased Orca/escrow preservation, midnight reservation stop and existing diagnostic
  opt-in selection. A first invocation named one nonexistent test; the corrected
  eight-test invocation passes. This was a selection error, not a code failure.
* An independent in-memory overlay uses the **unpatched** actual historical proof
  helpers and dormant plan through execute, caller finalization and report replay.
  Six synthetic responses increase only synthetic fetches 100 to 106; calls stay 80
  and documents 40. Its only mutable head is the synthetic daily-budget head. Socket
  connection attempts are denied. No LocalStore is constructed on the actual archive.
* An additional 33 mutations fail: every required plan/source/proof field omission,
  nearby port/trailing-dot/query/fragment URLs, request and completion clocks, extra
  request fields, wrong source, boolean runtime/counts, shifted charges and model-call
  counter changes.
* All six actual old admission objects replay unchanged against their original review
  policy hashes. All 44 consulted archive files preserve bytes, size and mtime. The
  authenticated manifest stays `895213b31bb9f75814acc9484cad9aabd3719e07ddd72c621275a9b2568a1e5c`.
  The sorted consulted-file inventory seal in the companion JSON is
  `e6004b7e9f5e4428bfc7e668a9bf531d1fa65566c423410f62dc6b87920ead41`.

The independent scratch result is `/var/tmp/smp-q4-independent-final-20261025.json`
inside OrbStack, raw SHA-256
`436307273fbc42ea3e848e0535b8ac832fc5782d0fa7822f8e0a8013a858535f`.
The companion review JSON retains its complete consulted-file, admission and code pins.

The implementation worker's final full checks report 858 operational tests plus lint,
377 data tests, 115 pipeline tests, build and 42 browser tests passing, with one existing
browser fixture skip. The worker reports unchanged local pixels at both widths. Those
full suites and renders were not duplicated by this reviewer; their receipts remain
under `accuracy/receipts/q4-controller-capture-2026-10-25/`.

## Reviewed seals and limits

| File | Raw SHA-256 |
|---|---|
| `web/scripts/pipeline/q4_controller_capture.py` | `8720cd8bed0c533201c24565ca28b23198f99f8a352213e07774f6f05f15ffb3` |
| `ops/ci/collect.py` | `87565d7855266777297fb7de11e94756ffbf9e1b38bbb4f92be2f6f0a557d007` |
| `ops/ci/test_q4_controller_capture.py` | `d7cd0ba331ba8206daec855db742ad91e1fca6e475eec33dd656ad39d6942aa7` |
| `q4-controller-diagnostic-spec-2026-10-25.md` | `23ac26f55528ca81e174679407147747cbc1c8885ce25468710f253cb001ee18` |
| `q4-controller-capture-plan-2026-10-25.json` | `007f1f940d48727da9a921d0c1138f27e5249870dd5ed6aaa3da3e844582ba91` |

Plan canonical SHA-256 is
`e787c1c94704dd3a21ff4e71ffaf35dac1ac18f9d3ea2b0a7e16690da3561600`.
H remains canonical `8b44bcbec679c178836408c4d98c7230a85572784b0257ef21d21d3b03b445db`.
The operational plan stays disabled and raw
`ad1c5cc234fe4fa69cbceb5370ac74825a37dc80b08528ca908d14b1352e53b4`.
Freshness engine, Fetcher, correction contracts/projector policy, original facts,
baseline and workflow pins remain unchanged; exact hashes are in the companion JSON.

I would retain this patch dormant on preview. It creates the narrow six-script capture
needed to learn what these controllers contain while preserving the existing source and
admission boundaries. Actual controller bytes, scope/pagination completeness, readable
primary samples, source qualification and actual scheduled/public acceptance remain
separate evidence still to obtain. Nothing here moves frozen main or grants production
acceptance credit.
