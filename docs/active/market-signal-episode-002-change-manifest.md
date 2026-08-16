# Market Signal Episode 002 — Change Manifest

## Control

- **Manifest ID:** `SEC-MARKET-SIG-MAN-002`
- **Current packet:** `v0.2`
- **Research freeze:** `2026-08-15T19:03:08-07:00`
- **Review correction:** `2026-08-15T19:17:24-07:00`
- **Lifecycle state:** `accepted`

## Version history

### v0.1 — initial candidate

- **State:** failed independent review; never accepted
- **Material defects:**
  - memorable wording implied a four-to-eight-quarter lag while the analysis disposition was `NO-CALL`;
  - Cisco security used a stale quarter;
  - the IANS restatement and ETR source mapping were incomplete;
  - the quarterly panel contained incorrect or approximate cells;
  - source provenance was not atomic enough for a financial timing packet;
  - domain postures did not consistently enforce coverage thresholds;
  - PREPARE lacked account applicability, owners, and stop conditions;
  - H2 and H3 exceeded the causal evidence;
  - prospective test rules were not mechanically decidable; and
  - current-state handoff surfaces still described research as pending.

### v0.2 — corrected and accepted

- **Evidence corrections:**
  - updated Cisco to Q4/FY2026;
  - disclosed the IANS 2024 methodology restatement;
  - added the correct ETR page for 32/23 percent realized-tool use;
  - added Broadcom Q1 evidence and infrastructure organic/acquisition splits;
  - rebuilt and independently checked the sparse quarterly panel;
  - added atomic claim provenance and packet hashes; and
  - added explicit collection-gap and metric-definition controls.
- **Judgment corrections:**
  - removed every implied lag band;
  - made H1, H2, and H3 `NO-CALL` where causal evidence is insufficient;
  - separated observed domain momentum from infrastructure causality;
  - enforced `INSUFFICIENT COVERAGE` for cloud/CNAPP, identity/NHI, SecOps, and AI runtime;
  - conditioned PREPARE on account exposure;
  - added bounded CSP actions, owners, and stop conditions;
  - strengthened the common/independent-driver alternative; and
  - made the prospective test executable with fixed cohorts, metrics, formulas, quorums, definition-change rules, realized-spend thresholds, and prospective-only T0.

## Review record

- **Evidence review:** passed after correction
- **Strategy review:** passed after correction
- **CSP practitioner review:** accepted after correction
- **Final verifier:** passed the judgment and packet; follow-on authority and handoff corrections recorded in current-state files

## Authority

Only Episode 002 v0.2 may be used for posture or handoff.

The accepted decision is:

> Infrastructure acceleration is evidenced. A stable infrastructure-to-security lag and domain-level infrastructure causality remain `NO-CALL`. Use infrastructure activation as an account qualification trigger; do not claim a broad cybersecurity boom.

Integrity authority: [market-signal-episode-002-source-manifest.md](market-signal-episode-002-source-manifest.md).

