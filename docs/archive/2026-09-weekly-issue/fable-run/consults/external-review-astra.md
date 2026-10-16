# External review — Codex, gpt-6-astra

**Task:** T6-1 of SEC-MARKET-FABLE-001, 2026-09-20. The owner asked for an outside review by this
model by name. Run read-only with `codex exec -m gpt-6-astra -s read-only`. Reviewed:
`docs/archive/2026-09-weekly-issue/product-core.md` v0.1, `site-rubric.md` v2.0, `design-spec.md` v0.3.
The text below is the reviewer's final message, unedited apart from making file links relative.
What the coordinator did with each finding is recorded in `design-spec.md` section 10.

---

The core is viable, but v0.3 still serves the advisor more clearly than the security leader. I would keep the concept and change the proposed front page. Findings 1–3 are the three highest-value design changes.

1. The design postpones the content that would justify its primary audience.  
   Files: [Product core, §§2–4](docs/archive/2026-09-weekly-issue/product-core.md:18) and [Design specification, §5](docs/archive/2026-09-weekly-issue/fable-run/design-spec.md:135).

   Building the owner’s reputation through useful public work is a coherent purpose. The problem is treating the owner’s vendor-attention decision as a substitute for a buyer’s decision. Deciding which vendor deserves an account-team meeting differs from deciding whether to renew a critical service.

   The design explicitly excludes “what this means if you run a security program.” That is the missing product. A security leader needs implications for supplier continuity, renewal negotiations, product support, consolidation, switching costs and alternative suppliers. These fit the stated scope without becoming product reviews.

   Put a short, owner-approved buyer brief first. Each selected development should explain who is affected, what changed, what remains unknown and what question to ask the supplier. Include “no action warranted” when appropriate. Most CISOs will ignore small funding rounds, practice-building advice and infrastructure-spending hypotheses unless those facts affect a decision they face.

2. Replace the growth leaderboard with a supplier comparison that does not declare winners.  
   Files: [Design specification, §§2–3.3](docs/archive/2026-09-weekly-issue/fable-run/design-spec.md:24) and [Rubric, D4](docs/archive/2026-09-weekly-issue/fable-run/site-rubric.md:190).

   “Leading vendors by latest reported growth” implies a defensible comparison. The proposed data cannot support that implication. A small business can grow faster than a large one while adding less revenue. Acquisitions, hardware replacement cycles, subscription conversions and changed metric definitions can move percentages without indicating stronger customer demand. Company-wide growth also does not establish leadership in a particular security domain.

   The caption acknowledges these problems but preserves the ranking that creates them. “Not a recommendation” cannot undo the prominence and exclusion decisions embodied in a top-three list. Growth also cannot answer the rubric’s question about “solid footing.”

   I would use an alphabetical “Tracked suppliers” table within clearly defined purchasing categories. Show the latest material development, reported business scale, the exact growth metric and period, and a comparable prior observation where available. Put acquisition effects and missing disclosures beside the number. Separate company totals from product segments.

   On the supplier detail view, add public evidence relevant to continuity: cash generation, liquidity, debt maturities, ownership changes and announced product-support changes, where disclosed. Do not turn these into an opaque health score. Private-company gaps should say “not disclosed,” without implying weakness.

   Allow numerical sorting only within compatible metric groups. The SEC’s guidance on defining metrics and explaining calculation changes provides useful disclosure discipline here, although it governs issuer reporting rather than this website. [SEC metric guidance](https://www.sec.gov/files/rules/interp/2020/33-10751.pdf).

3. Make a dependable weekly account of material changes the recurring product.  
   Files: [Product core, §§6–7](docs/archive/2026-09-weekly-issue/product-core.md:78) and [Design specification, §§3.1, 3.4–3.5](docs/archive/2026-09-weekly-issue/fable-run/design-spec.md:41).

   Quarterly growth tables are reference material. They provide little reason to return every week. A security leader returns to learn whether something changed about a supplier they depend on, whether an earlier concern resolved, and whether a forthcoming decision needs attention.

   Lead with the few developments that matter most to buyers across all event types. Follow each through subsequent weeks. Show what was resolved, what remains open and the next public milestone worth checking. Provide vendor and domain links so readers can return directly to their interests.

   Publish a dated weekly checkpoint even when the conclusion is “no material change found within our coverage.” Distinguish that from “collection incomplete” and “owner’s interpretation pending.” The proposed “most weeks” promise, feed link and fresh figures do not yet deliver this recurring value.

4. The facts-versus-judgments split is sound in principle, but the proposed boundary leaks.  
   Files: [Product core, §6](docs/archive/2026-09-weekly-issue/product-core.md:78), [Design specification, §2](docs/archive/2026-09-weekly-issue/fable-run/design-spec.md:24), and [Published issue source](web/src/data/issues/2026-w36.ts).

   Mechanical execution does not make an editorial choice factual. Choosing the vendors, choosing each vendor’s metric, calling them leaders, assigning them to domains and deciding which events matter are judgments. A factual source can also contain an unverified company claim.

   The existing event rows demonstrate the problem. Their “why” text includes interpretations such as growth being consistent with a platformizing market or reinforcing a vendor’s position. Those statements belong to the approved interpretation, even when attached to factual earnings figures. The current issue is signed; copying that pattern into an automatically published facts feed would remove that protection.

   Approve collection and presentation rules in advance. Automatically publish bounded observations with explicit attribution and validated units, periods and event status. Require review for new interpretations, changed comparison methods, consequential ambiguity and claims of distress. “A company announced an acquisition” must remain distinct from “the acquisition closed.”

   Approval should cover the exact text and evidence version. When material evidence changes, an old judgment should visibly await review rather than appear freshly endorsed beside new facts.

5. The reseller relationship requires substantive editorial safeguards.  
   Files: [Product core, §§2, 8](docs/archive/2026-09-weekly-issue/product-core.md:18) and [Design specification, §9](docs/archive/2026-09-weekly-issue/fable-run/design-spec.md:174).

   The table is not reputationally safe merely because its sort is mechanical. Readers can reasonably interpret inclusion as endorsement and exclusion as disapproval. Vendors can reasonably ask why a competitor’s favorable metric was selected. Coverage of distress at competing service providers creates an especially obvious credibility test.

   Disclose the owner’s employer and commercial role prominently, and identify relevant relationships on affected coverage. Publish consistent inclusion rules, apply the same evidence standards to partners and competitors, and explain how corrections and vendor responses are handled. State whether sponsorship or commercial relationships can affect coverage.

   The outside-activity policy can remain a separate owner decision. The reader’s need to understand the author’s interests cannot. The rubric currently has no adequate conflict-of-interest test.

6. Refreshing the figures is not enough; their meaning needs validation.  
   Files: [Design specification, §4](docs/archive/2026-09-weekly-issue/fable-run/design-spec.md:114), [Vendor figures](web/src/data/prints.ts), and [Evidence records W36-15 and W36-19](web/src/data/evidence.ts:1793).

   Step B treats previously published figures as suitable inputs and emphasizes checking that numbers appear in excerpts. That catches some transcription errors, but not wrong periods or misleading comparisons.

   For example, the issue headlines describe Zscaler and Palo Alto figures as FY2026 revenue, while their evidence records identify the amounts as quarterly revenue. The old Zscaler entry uses organic ARR growth; the newer issue reports total ARR growth. Those observations cannot establish acceleration without reconciling the basis.

   Validate the company or segment, metric definition, period, units and acquisition treatment together. A number appearing in a source is insufficient. Keep historical observations, but derive current views from one authoritative set of records. Two different rates on a page are legitimate when their periods and definitions are clear.

7. The rubric is a useful presentation checklist, but an inadequate test of product purpose.  
   File: [Rubric, §§1–2 and D4–D5](docs/archive/2026-09-weekly-issue/fable-run/site-rubric.md:10).

   The rubric correctly separates audience impact from website quality. However, it explicitly excludes intelligence usefulness while naming a dimension “Decision value for a security leader.” Its tests mostly establish that material is present and reachable. They do not establish that the material supports the decision implied.

   Keep impact measurement separate, but add mandatory checks for factual meaning, comparison validity, buyer relevance, coverage limitations and conflict disclosure. Material failure in these areas should block a “fit for purpose” conclusion regardless of the composite score.

   Test the page with actual security leaders facing a renewal or supplier decision. Ask what they learned, what they would ask next, and what the evidence does **not** establish. A scorer asked to imagine being a CISO is not an adequate substitute. Agreement between two agents demonstrates scoring consistency, not product validity.

8. Several tests reward this author’s chosen design rather than the reader’s task.  
   File: [Rubric, D1–D13](docs/archive/2026-09-weekly-issue/fable-run/site-rubric.md:105).

   D1 level-5 test 1 rewards the proposed vendor table before establishing comparability. D4 level-5 test 1 invites a sourced growth display to stand in for supplier stability. Replace both with a reader task that distinguishes commercial momentum, continuity evidence and unknowns.

   D6’s eight desktop items, four mobile items and one-screen lane encourage short, low-value entries and omitted context. Its mandatory table rule measures format compliance. Replace these with successful scanning and comprehension tasks.

   D1 and D4 repeatedly award credit for the same headline and audience label. D3 and D11 repeatedly reward a feed link. D2 and D12 repeat corrections and history mechanisms. Reduce this double counting.

   Empty corrections records and promises of future calibration earn substantial credit without testing correction handling or forecast evaluation. Exercise those mechanisms with test cases and report untested capabilities separately.

   D7’s keyboard shortcuts and D13’s exact font, color and light-theme rules are house preferences. They should not determine product quality. A critical accessibility defect should also be a release blocker, rather than merely one failed test among otherwise passing tests.

9. Reweight the rubric toward decision usefulness and trust.  
   File: [Rubric, §3](docs/archive/2026-09-weekly-issue/fable-run/site-rubric.md:81).

   Agent legibility receives seven points while trust receives five. Density receives eight, despite the absence of a demonstrated reader preference for the specified density. I would use these weights after correcting the tests:

   | Dimension | Current | Recommended |
   |---|---:|---:|
   | Market picture clarity | 14 | 10 |
   | Look back, look ahead | 10 | 7 |
   | Freshness and reason to return | 12 | 15 |
   | Decision value for a security leader | 12 | 20 |
   | Evidence legibility | 9 | 12 |
   | Density and scanability | 8 | 4 |
   | Wayfinding | 5 | 3 |
   | Agent legibility | 7 | 3 |
   | Performance | 5 | 4 |
   | Accessibility | 7 | 8 |
   | Follow and share | 3 | 3 |
   | Trust and authority | 5 | 10 |
   | Craft | 3 | 1 |

   These sum to 100. The increased decision-value weight is justified only if it measures demonstrated comprehension and useful next questions.

10. Freshness needs a reporting schedule and coverage statement, not a universal age threshold.  
    Files: [Rubric, §2 and D3](docs/archive/2026-09-weekly-issue/fable-run/site-rubric.md:28), [Design specification, §3.4](docs/archive/2026-09-weekly-issue/fable-run/design-spec.md:92), and [Content inventory, §4](docs/archive/2026-09-weekly-issue/fable-run/content-inventory.md:159).

    A quarterly result can be more than 45 days old and still be the latest available. Conversely, a recently published issue can describe events several weeks old. The signed-issue cap can reward repackaged old information while penalizing a well-maintained factual service.

    Show the economic period, source publication date, last successful check and judgment review date separately. Mark a figure overdue when a newer expected disclosure is missing. Measure publication delay and collection completeness. A successful run that found nothing and a failed run must never produce the same empty-state message.

11. The coverage promise exceeds both the taxonomy and the evidence.  
    Files: [Product core, §§3–4](docs/archive/2026-09-weekly-issue/product-core.md:38) and [Content inventory, §§1–3](docs/archive/2026-09-weekly-issue/fable-run/content-inventory.md:11).

    Six inherited domains do not establish coverage of the market a security program buys from. Endpoint and managed security services lack explicit homes. Broad Identity and Data categories combine vendors that may address different purchasing needs. Distress is central to the promise but absent from the inventory.

    Publish a bounded coverage list, including exclusions and last checks. Define peer groups by purchasing problem before comparing vendors. Start with a smaller set the owner can maintain reliably.

    Also correct the inventory’s distinction between missing and unsuitable evidence. It lists WitnessAI’s reported ARR growth, then says no AI-security vendor has disclosed a growth figure. Its Identity discussion calls the available figures comparable despite listing Okta revenue and SailPoint ARR. Say precisely which disclosures exist and why they cannot support a particular comparison. More searching will not necessarily make private-company disclosures comparable.

12. Cut three things from the front page.  
    Files: [Design specification, §§3.1, 3.5, 7](docs/archive/2026-09-weekly-issue/fable-run/design-spec.md:41) and [Product core, §5](docs/archive/2026-09-weekly-issue/product-core.md:66).

    First, cut the growth-based “leading vendors” podium. Replace it with the supplier comparison in finding 2.

    Second, cut the thesis-centered headline and its explanatory “lag call” note. The proposed headline still comes from an issue centered on that thesis. Moving the analysis section down does not remove it from the first screen. Preserve the historical issue and write a separately approved current homepage introduction.

    Third, cut the requirement to carry the complete four-lane event inventory on the homepage. Show selected buyer-relevant developments there and link to the full record. Minor funding announcements should not compete with consequential supplier developments merely because both exist in the dataset.

13. The operating promise needs a smaller editorial commitment.  
    Files: [Product core, §§4, 6](docs/archive/2026-09-weekly-issue/product-core.md:49) and [Rubric, D2](docs/archive/2026-09-weekly-issue/fable-run/site-rubric.md:137).

    Broad market coverage, reliable distress reporting, three-to-six-month forecasts and a glance once or twice weekly are in tension. Automation can collect observations cheaply. Reviewing ambiguous acquisitions, accounting changes and adverse claims takes attention.

    I would begin with a declared supplier set and one short weekly buyer brief. Use conditional watchpoints where a forecast would be weak. Give each forecast an observable outcome and review date; “medium confidence” alone cannot support meaningful calibration. Provide a clear reduced-service state when the owner cannot review.

    That narrower promise is more likely to earn trust than broad coverage whose most consequential claims receive hurried approval.

My verdict: the core deserves to continue, but I would not approve v0.3 as the buyer-facing design. It improves presentation while deferring the buyer value. Lead with consequential changes, make vendor comparisons defensible, and prove the weekly service before promoting it.
