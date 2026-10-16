# AI security coverage

**ID:** `SEC-MARKET-AI-001` · **Version:** v0.1 · **Opened:** 2026-08-25

## Why

A reader told the owner the site's AI security coverage is too thin. Measured, they are right twice.
Seven AI-relevant items exist across the 42-print scorecard. Six are capital: Zenity $125M, Onyx
$113M, WitnessAI $58M, Oak $60M, Hush $30M, and the Check Point agreement for Lakera. Exactly one is
buyer behaviour, Palo Alto Prisma AIRS at 300-plus customers up from 100, and it is filed under Cloud
security.

Three of the seven sit under other domains and none of them is misfiled. Oak's own note calls it an
AI-native identity operating system, Hush is agentic identity, and Prisma AIRS is AI runtime security
sold by a cloud platform vendor. Each print carries exactly one `group` string, so the model cannot
say a print belongs to two domains. That is the defect.

## Part 1 — a print may carry a secondary domain

### Change

1. `VendorPrint` gains `secondaryGroup?: (typeof printGroups)[number]`.
2. Set it on exactly three existing prints. Nothing else changes in the data.
   - Palo Alto Prisma AIRS: primary `Cloud security`, secondary `AI runtime`
   - Oak: primary `Identity`, secondary `AI runtime`
   - Hush Security: primary `Identity`, secondary `AI runtime`
3. `PrintGrid` renders a print under a group when `group === g || secondaryGroup === g`.

### The integrity requirement, which is not cosmetic

The eyebrow says "42 prints across eight domains". Once a print appears in two groups, the group
counts sum to 45. A reader who adds them up must not conclude the board double-counts.

- The eyebrow keeps counting **distinct** prints. It stays 42 across eight domains.
- A card rendered in its **secondary** group carries a visible label naming its primary group, worded
  plainly, for example `also counted under Cloud security`. Without that label this change inflates
  the board, which is the opposite of what the project is for.
- The group header count must distinguish the two. A group's count line states its primary prints and
  its borrowed ones separately rather than merging them into one number.

### Gate

`verify:integrity` gains checks that fail the build when:

- a `secondaryGroup` value is not in `printGroups`;
- `secondaryGroup === group`;
- a print carries a `secondaryGroup` and the rendered output for that group does not contain the
  primary-group label for it.

Each new check must be observed to fail under a deliberate perturbation and then pass once reverted.
A gate nobody has watched fire is a comment.

### Acceptance

- Build passes `verify:edition`, `verify:panel`, `verify:integrity`, `tsc`, lint.
- Rendered at 1440 and 390: the AI runtime group shows its own prints plus the three borrowed ones,
  every borrowed card names its primary group, and the eyebrow still reads 42 and eight.
- The three prints still appear under their primary groups, unchanged.
- No figure, note, evidence id, or date is edited anywhere. This change adds a field and a label.

## Part 2 — bounded gather for buyer-side AI security evidence

Capital is already well covered and every round says the same thing. What cannot improve without new
evidence is the read itself, which currently says the money is venture money and buyer spend is not
visible.

### Three lanes

- **B1 buyer-side signal.** Revenue, ARR, customer counts, attach or adoption figures for AI security
  products. Public filings, earnings calls, investor decks, official releases.
- **B2 absorption.** Which AI security companies have been acquired by platform vendors, with dates
  and disclosed terms. This lane doubles as a live test of the tracked hypothesis that platforms
  absorb adjacent categories rather than compete with them, which currently rests only on Wiz and
  CyberArk.
- **B3 vendor sweep.** AI-native security vendors carrying any public number we do not already hold.

### Rules, all lanes

1. **No premises are supplied and none may be assumed.** Find and verify. Do not set out to confirm
   anything. A prompt that hands an agent a conclusion gets that conclusion back with fresh evidence
   attached, which is harder to catch than an obvious error, and it has already happened twice here.
2. Every claim needs a primary-source URL a reader can open plus a verbatim excerpt containing the
   figure. A secondary write-up is not a source.
3. Company-stated growth is labeled as company-stated. Never as audited or as ARR unless the source
   says so.
4. Distinguish buyer-side evidence from capital explicitly on every row.
5. Report what could not be verified rather than dropping it. An empty lane is a real result.
6. Write nothing into the repository. Return findings only.

### Acceptance

Findings are returned structured and are verified again by the lead against the primary documents
before anything reaches `preview`. Nothing is published on a subagent's report alone.

## Not authorized by this work

Changing any published posture, market call, or confidence value. Adding a domain card. Changing the
landscape frame. Presentation decisions wait until the coverage is known.
