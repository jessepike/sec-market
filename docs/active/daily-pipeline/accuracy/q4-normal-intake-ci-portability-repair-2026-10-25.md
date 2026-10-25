# Portable CI fixtures for the two-source intake tests

The hosted preview canary 40197621420 failed during unittest setup because two new classes
unconditionally opened a VM-local archive. The runtime canary step was not reached.

Only ops/ci/test_q4_normal_intake.py and ops/ci/q4_intake_fixtures.py change. The new committed
fixture reader authenticates the fixed 55-file package and every payload before use. The policy,
complete Q4 proof/529 URLs, baseline, ordinary 200/304, date/malformed cases and real zero-call
quota mechanics now run without an external archive. Quota mechanics use temporary writable
state. The seed lease/ack guard test keeps its explicit mocked-preflight boundary. The separate
unmocked full preflight and six real-admission positives remain local actual-archive tests and
explicitly skip when that archive is unavailable. No runtime, policy or seed bytes change.

The exact committed f32946c11f7db4bf3b63fc0380780ab9bf5d6836 snapshot plus these two test files
passes 14/14 focused and 935/935 full operational tests with local archives present. In a fresh
process with the retained fixture unavailable before discovery, 12 focused tests run and pass;
the two external positives skip. The complete suite discovers 935 tests: 896 pass, 39 skip
(37 existing external-archive skips and those two new positives), with no failures/errors.
The simulation denies retained-archive reads and recorded zero attempts. No archive was moved.

The first full simulation driver omitted its application cwd/sys.path, causing three loader
errors. Its raw output is retained separately. The corrected driver passes the complete suite.
The actual hosted rerun remains pending; local simulation does not prove GitHub CI success.

The receipt folder contains exact old/new hashes, the two-file diff, authenticated package and
unchanged other 81 implementation pins, fresh-process denial driver and lossless gzip logs.
All previous implementation/review/postcopy receipts remain exact. Independent review is pending
before copying these two files into the finish checkout. Root owns commit, push and activation.
