# Evidence Drawer — Measurement Report

Taken 20 Sep 2026 at production site https://securitymarketpulse.com/

## Measurement 1: Evidence Control Interaction

All evidence buttons opened a drawer-type element in the right column. Focus moved into the drawer content (text and links were accessible). Drawer closed with Escape; focus returned to the button. Page scroll position remained unchanged.

### 1a. First evidence button ("Return on Security")

Evidence drawer title: "Evidence"

Button label: "View evidence: Return on Security" (for Secure Series E funding announcement)

Drawer content: 539 characters of structured data showing publication source, date, source classification, and packet identifier.

External link: Yes. "Canonical source" links to `https://www.returnonsecurity.com/p/security-funded-259`

Metadata shown: Publisher (Return on Security), publication date (2026-08-24), source kind (INDEPENDENT), economic period (Security, Funded #259 week), packet label (SEC-MARKET-ISSUE-001 / W36-01)

Quoted excerpt: Shown in a grey box under "EXCERPT / LOCATOR" heading: "Secure, a United States-based digital identity verification and fraud prevention platform, raised a $156.0M Series E from Summit Partners."

Interpretation: Provided under "INTERPRETATION" heading: "A large-dollar identity-fraud round in an otherwise thin funding week."

Limitations/confounds noted: "Aggregator-sourced round description; not the company's own release."

Correction control: None visible (no "report problem" or feedback button).

Screenshots at 1440×900 and 390×844 in drawer/ directory.

### 1b. CrowdStrike / Palo Alto evidence button

Button label: "View evidence: Palo Alto Networks & TechCrunch"

Drawer content: 730 characters.

External link: Yes (1 link found, text not extracted in measurement).

This button was found and opened successfully at both viewport widths.

### 1c. Sources button

Button label: "Sources"

Drawer content: 11,918 characters.

External links: Yes (10 links found).

This panel contains the full source bibliography for the issue.

## Measurement 2: Chrome Height

Site chrome (everything above the eyebrow line "ISSUE 2026-W36") occupies measurable vertical space at both widths.

| Viewport | Eyebrow Y | Chrome height | Percent of viewport |
|----------|-----------|----------------|-------------------|
| 1440×900 | 113 px | 113 px | 12.6% |
| 390×844 | 221 px | 221 px | 26.2% |

The H1 headline sits below the eyebrow on both widths (138.6 px at 1440, 264.2 px at 390).

## Summary

**Does the evidence panel carry a real external link?** Yes. The "Canonical source" link points to the actual publication source.

**Does it show source kind and retrieval date?** Yes. Source class (INDEPENDENT) and publication date (2026-08-24) are both displayed. No explicit "retrieved" or "fetched" date is shown.

**Does focus management work?** Yes. Focus enters the drawer on open and returns to the button on Escape.

**Chrome height at 390 as percent:** 26.2%
