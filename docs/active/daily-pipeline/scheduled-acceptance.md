# Temporary actual scheduler acceptance

The owner approved cutover after the October 23 daily 05:17 UTC window.
The collector therefore includes additional `7 6 23 10 *` and `7 7 23 10 *`
triggers for actual scheduled acceptance at 06:07 and 07:07 UTC on October 23, 2026. A lightweight
guard checks the runner's actual UTC date before collection. This temporary
trigger cannot collect on another date or on its annual recurrence. The normal
05:17 UTC schedule and manual collection requests remain available.

This changes no collection policy or budget counters. Retain the real GitHub
schedule event and its archived collection-run receipt as acceptance evidence;
a dispatch is not a scheduled receipt. GitHub may delay the scheduled run.

Actual collection `39946689429` and verification-only retry `39954446259` passed. The accepted
main gate and production acknowledgement also passed. Both gate/publication slots for October 23
UTC are consumed, so keep main on the accepted production revision for that day; a documentation
or cleanup promotion would otherwise request an unnecessary third gate. Remove temporary triggers
with the next ordinary code promotion. Their UTC date guards prevent source work on a later date
or annual recurrence. The normal collector schedule remains active.

For these two temporary expressions only, a later scheduled runner may reuse
source work already completed successfully by an actual scheduled main collector
on the same UTC day. It must verify the prior GitHub identity and revision, the
immutable clock receipt's current policy, the latest archived coverage and
collector summary, and replay reconciliation from hash-checked evidence. Source
age must remain within 30 hours and current reconciliation must preserve the
coverage verdict. Manual work cannot supply this scheduled proof.

Reuse runs before account-auth restoration or budget escrow. It makes no model
or source-fetch request and changes no budget, latest collection head or source
check time. The new runner records `source_work_reused`, the prior scheduled
GitHub run ID, original coverage receipt hash and original check time. This
proves the new real timer executed its verification; it does not claim another
source fetch. Normal daily and manual runs keep their existing behavior.
