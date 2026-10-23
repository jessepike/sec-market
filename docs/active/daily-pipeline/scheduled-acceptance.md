# Temporary actual scheduler acceptance

The owner approved cutover after the October 23 daily 05:17 UTC window.
The collector therefore includes an additional `7 6 23 10 *` trigger for an
actual scheduled acceptance at 06:07 UTC on October 23, 2026. A lightweight
guard checks the runner's actual UTC date before collection. This temporary
trigger cannot collect on another date or on its annual recurrence. The normal
05:17 UTC schedule and manual collection requests remain available.

This changes no collection policy or budget counters. Retain the real GitHub
schedule event and its archived collection-run receipt as acceptance evidence;
a dispatch is not a scheduled receipt. GitHub may delay the scheduled run.

Remove the temporary cron and its guard after the acceptance and active
publisher's pinned main gate finish. Do not move main during that gate: its
publisher requires the exact main revision that it started with. The normal
collector schedule continues after this temporary acceptance is removed.
