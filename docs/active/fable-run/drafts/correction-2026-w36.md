# Proposed correction — issue 2026-w36

**Status:** proposal for the owner. Nothing here is published. The issue is signed in his name, so
the correction is his to approve, in these words or his own.
**Written by:** the run coordinator, 2026-09-20, task T6-5 of run `SEC-MARKET-FABLE-001`.
**Found by:** the external review on `gpt-6-astra`
(`docs/active/fable-run/consults/external-review-astra.md`), then checked by the coordinator
against the issue file and the evidence records.

## 1. What is wrong

Two headlines in the signed, locked issue for the week ending 6 September 2026 describe a
fourth-quarter revenue figure as a full-year figure. Both are live on
https://securitymarketpulse.com today.

| Item | What the issue says | What the source says | Evidence record |
|---|---|---|---|
| `2026-w36-prints-2` (`web/src/data/issues/2026-w36.ts` line 168) | "Zscaler FY2026 revenue grows to $898.2M, +25% YoY; ARR grows to $3,771M, +25%" | Revenue of $898.2 million is for the quarter ended 31 July 2026, the company's fiscal fourth quarter. The ARR figure is correct as a point-in-time figure at that date | `W36-15`, `economicPeriod: 'Quarter ended 2026-07-31'` |
| `2026-w36-prints-6` (line 208) | "Palo Alto FY2026 revenue grows 34% to $3.41B; Next-Gen Security ARR $9.10B, +63%" | "Total revenue for the fiscal fourth quarter 2026 grew 34% year over year to $3.41 billion." The $3.41 billion is one quarter | `W36-19`, `economicPeriod: 'Quarter ended 2026-07-31'` |

The numbers and the growth rates are right. The period label is wrong. A reader would take the
companies to be roughly a quarter of their real size. The evidence records themselves are correct,
which is how the error was caught.

A second, smaller problem sits in the same item. The "why it matters" line for Palo Alto reads
"Next-Gen Security ARR growth of 63% is the fastest among this week's public-issuer prints." That
compares a company-defined recurring-revenue segment with other companies' total revenue growth.
Those are not like for like. Rubric v2.1 blocker 2 would fail it. The coordinator recommends the
correction note covers it too.

## 2. Proposed correction text

For the owner to edit. Written to say exactly what changed and nothing more.

> **Correction, [date approved].** In the issue for the week ending 6 September 2026, two headlines
> gave a quarterly revenue figure as a full-year figure. Zscaler's revenue of $898.2 million and
> Palo Alto Networks' revenue of $3.41 billion are each for the fiscal fourth quarter ended
> 31 July 2026, not for fiscal year 2026. The growth rates and the recurring-revenue figures were
> stated correctly. The same issue described Palo Alto's 63 percent growth in Next-Generation
> Security recurring revenue as the fastest of the week's results; that figure is a
> company-defined segment and is not comparable with other companies' total revenue growth, so the
> comparison is withdrawn. The original text is unchanged in the record. Jesse Pike.

## 3. How to publish it without breaking the lock

Published issues are hashed into an append-only manifest, and that is worth keeping: it is what
lets the site say an issue was never quietly edited. So the issue file does not change.

Recommended mechanism, the smallest that works:

1. A new append-only data file, `web/src/data/corrections.ts`. Each entry has an id, the date, the
   issue id, the item ids it applies to, the correction text, and the name of the person who
   approved it.
2. The issue page and the front page show a dated "Corrected" note beside each affected item, with
   the original headline left as it was and the corrected reading under it.
3. A corrections list with a stable address (`/corrections/`), which also satisfies rubric
   dimension 12, level-5 test 1. The block on the front page that today says "There is no form and
   no list" is reworded to link to it.
4. The three JSON files and the feed carry the correction, so a machine reader that took the wrong
   figure can find the right one.
5. A data test that fails the build if a correction names an issue or item that does not exist.

This is a small build, Layer A (building and shipping): about half a day of agent work including
tests and the visual review. It is not built. It needs the owner's yes, because it adds a page and
publishes a statement under his name.

## 4. How to stop it happening again

The gates today check that a number in a headline also appears in the cited source. They do not
check what the number means. The automation plan now carries this as a requirement: before any
figure publishes, a check confirms the company or segment, the metric, the period and the units
together, reading the period from the evidence record and comparing it with the words used in the
headline ("FY", "fiscal year", "quarter", "Q4"). A headline that says "FY" over an evidence record
whose period is a quarter would fail the build.

## 5. What the owner is asked

One decision: approve the correction text (edited as he likes) and the mechanism in section 3.
Until then the error stays live. The coordinator's recommendation is to approve both, and to
publish the correction in the same promotion as the rebuilt front page, so that the first thing a
new reader meets is a site that corrects itself in the open.
