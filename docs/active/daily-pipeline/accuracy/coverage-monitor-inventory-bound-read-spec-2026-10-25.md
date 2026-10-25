# Read the accepted coverage file within its authenticated size

October 25, 2026. Reliability repair under the already approved activation, verification and
failure-alert work. Main remains 6d5e87feba4ffbc75e50f35cb564cb8fd91708ca; no publisher, source,
gate, schedule, secret or allowance change is part of this repair.

## Actual defect

Manual monitor 40175735011 ran on exact main and updated issue 10. Its 20 guard tests passed,
but publication inspection ended with INDEPENDENT_PROBE_FAILED / ValueError. Exact-main
offline replay confirms GitHub gate authority, deployment acknowledgement and application/data
pairing pass before get_json rejects the coverage response at its fixed 1,000,000-byte bound.

Actual accepted `/daily-coverage.json` is 1,337,257 bytes, SHA-256
ac8068379c6c79760331711bfb7bb6387fbc639f9ab6f921713502c6982d47fc. This matches the accepted
artifact's authenticated inventory 0c645ba2977c3e7e3df04a99d2d677ed5e7149b8608d3b472af0ea0b0c810c36
(9,441 bytes). The current release is fc8bf0984dbeacbe79519574911837d8b638f42215f6547e31ae8968b29951e4.
The public source expiry is still October 26 at 12:45:29.479727 UTC. The combined incomplete-or-
overdue reason does not establish an expired public source.

## Narrow repair

Change only the watchdog reader and its meaningful regressions. After the existing accepted
release and gate authority checks, retrieve the artifact inventory through its existing archived
reference, verifying that reference and its canonical inventory hash against the accepted
artifact identity. Validate a single unambiguous `daily-coverage.json` entry with a strict
positive integer byte count and valid raw SHA-256. Reject missing/duplicate entries, malformed
references, boolean/negative/oversized counts, bad hashes and inconsistent artifact identities.
Do not borrow an inventory from preview, another release, an untrusted live header or an agent.

Permit the exact production coverage URL to use that authenticated expected size, subject to a
fixed absolute ceiling no higher than the existing 40,000,000-byte archive API ceiling. Read
expected bytes plus one, then require exact raw byte length and SHA-256 before JSON parsing or
coverage interpretation. A short, changed or oversized response must fail. A Content-Length
header cannot grant authority or substitute for checking actual bytes. Preserve the existing
status-200, unchanged-final-URL and timeout guards.

Every other health receipt retains its 1,000,000-byte limit. A larger reader without a valid
accepted coverage reference is forbidden. Do not weaken incomplete coverage, historical
processing, held claims, source expiry, correction inventory or scheduled-receipt alarms. No
coverage, review, timer, source or publication credit follows from fixing this reader.

## Verification

Retain the original failed run and actual issue update with complete safe logs. Reproduce the
old rejection and repaired read using the exact artifact-matched public coverage bytes and
accepted archive records. Use socket-denied fixtures and read-only adapters for frozen evidence;
never initialize LocalStore on an archived tree. Keep original dates, hashes and modification
times. The new read should reach the honest incomplete-intake/processing/history/held-claim and
pending-timer results without a generic probe failure. Do not convert those remaining gaps into
a healthy result.

Add meaningful tests for the actual >1 MB file, exact accepted size/hash, short/long/tampered
responses, missing/duplicate/wrong-release inventory, bad types or oversized bounds, redirect,
wrong status, invalid JSON and unchanged limits on all other receipts. Exercise the real HTTP
reader through a bounded fake opener and the complete publication inspection with actual pinned
inputs. Run the watchdog and operational suites and obtain independent focused review. Public
page data, code and appearance do not change; no new application build or render is needed for
this watchdog-only patch.

Keep the repair on preview while main is held for genuine timer acceptance and code-bound gate
availability. A separately authorized manual freshness workflow on preview may then exercise
the repaired read against actual accepted production and update the existing issue. That proves
the actual repaired check, not scheduled-main operation. Scheduled verification of the repaired
monitor remains pending until reviewed promotion and its genuine cadence execute.
