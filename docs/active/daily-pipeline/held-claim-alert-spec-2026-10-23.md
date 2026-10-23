# Held claim alert wording

The actual scheduled monitor `40028529947` correctly reported 28 held claims, but named the
condition `OWNER_REVIEW_QUEUE_28`. The current investigation remains agent-owned; the count does
not establish a human factual decision. This repair changes that reason to `HELD_CLAIMS_28`, with
the count derived from the same archived review queue. Empty queues add no reason. Existing
coverage, execution, production-pair and correction-admission reasons remain independent.

This is an alert terminology change, with no queue mutation, claim acceptance, publication or
coverage credit. The existing GitHub issue update/recovery path remains unchanged. Historical
receipts retain their original reason string. Tests must show that held claims alone keep the
monitor unhealthy, an empty queue can pass when every other condition passes, and source gaps
remain visible alongside the renamed held-claim reason. Use fictional read-only fixtures only.

OrbStack validation passed all 15 monitor tests, including those three cases. The actual deployed
monitor still reports its historical reason until this candidate reaches main and the next real
scheduled monitor runs. No notification was sent by these tests.
