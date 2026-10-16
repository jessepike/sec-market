# Blind score, rubric v3.0: Security Market Pulse preview

- **Deployment:** https://security-market-pulse-git-preview-pikeholdings.vercel.app/
- **Commit served:** `8fa5359` (the preview branch head. The served `/` has `last-modified: Sat, 26 Sep 2026 15:52:52 GMT`, 44 seconds after that merge was committed at 15:52:08Z.)
- **Scoring date:** 2026-09-26
- **Scorer:** Claude Opus 5.5 (`claude-opus-5-5`), blind
- **Rubric:** `docs/archive/2026-09-weekly-issue/fable-run/site-rubric.md`, `SEC-MARKET-FABLE-RUBRIC` v3.0
- **Evidence folder:** `docs/archive/2026-10-refresh-gate/auto-001/score2/opus/evidence/` (all paths below are relative to it)

**Blindness note.** I did not open any score file, RUN-STATE file, report under `docs/archive/2026-10-refresh-gate/auto-001/`, `decisions.md` or `status.md`. Blocker 4 tells the scorer to use commit history, and reading it exposed commit subjects that quote earlier composite numbers and one commit body that lists the earlier findings. I scored from the evidence below and not from those messages.

## Result

**Composite: 56.0 / 100 (2026-09-26). Not fit for purpose: blockers 1, 2, 3 and 4 fail.**

| # | Dimension | Weight | Score | Points |
|---|---|---|---|---|
| D1 | Freshness without fail | 22 | 2 (freshness cap applies: at most 3) | 8.8 |
| D2 | Coverage | 15 | 4 | 12.0 |
| D3 | Deciding a supplier's footing | 20 | 4 | 16.0 |
| D4 | Evidence legibility | 13 | 2 | 5.2 |
| D5 | Trust | 12 | 2 | 4.8 |
| D6 | Density and scanability | 4 | 2 | 1.6 |
| D7 | Phone | 4 | 2 | 1.6 |
| D8 | Accessibility | 4 | 4 | 3.2 |
| D9 | Performance | 3 | 2 | 1.2 |
| D10 | Machine legibility | 2 | 3 | 1.2 |
| D11 | Craft | 1 | 2 | 0.4 |
| | **Total** | 100 | | **56.0** |

**Caps.** The freshness cap applies to D1. Nozomi Networks shows no ownership fact and "0" events, but its own newsroom says Mitsubishi Electric completed the acquisition on 28 January 2026, which is 241 days before the scoring date. D1 scores below the cap anyway. The coverage-gap cap does not apply: all twelve domains list suppliers, and endpoint, identity and managed security are all covered.

## Fit-for-purpose blockers

| # | Blocker | Result | Reason |
|---|---|---|---|
| 1 | Mislabelled figure | **FAIL** | All 23 revenue, ARR and growth figures I checked match the filings. The failures are the "Events, 12 mo." counts, event labels and row names, listed below. |
| 2 | Stale beyond the line | **FAIL** | Nozomi's acquisition completed 28 Jan 2026 and is not shown (241 days). Rapid7's four board resignations were disclosed in an 8-K on 31 Aug 2026, but the row still reads "latest results, 10 Aug 26" (21 days past the shown fact). |
| 3 | Judgment on a live page | **FAIL** (strict reading) | `/corrections/` carries the sentence *"Watch whether it survives as a product or becomes a feature."*, presented as what three rows "now read". That sentence is a forecast about suppliers' prospects. |
| 4 | Run-status line misstates what happened | **FAIL** | The page says "Figures checked 26 Sep 2026 · every source collected." The record does not show a full collection on 26 Sep: see below. |
| 5 | Accessibility failure | PASS | axe found zero violations of any impact on `/` and `/corrections/` at 1440 and 390, and the keyboard pass reached every control with a visible 2px focus ring. |

### Blocker 1 detail: figures that are wrong or mislabelled on the page

Source: `home-1440-text.txt`, `sources.json` (every `src` control was clicked and its drawer recorded), `sources-table.txt`.

1. **Wrong event counts.** Torq ("Series D $140M · Jan 2026"), Upwind ("Series B $250M · Jan 2026"), Chainguard ("$280M · Oct 2025"), Claroty ("Growth equity $150M · Jan 2026") and Xage ("$15M · Dec 2025") each show a funding round inside the trailing twelve months, yet their "Events, 12 mo." cell reads **0**. Other rows count funding as an event, for example HiddenLayer "1 · latest funding, 2 Sep 26", Zenity and WitnessAI. Torq's own page (`src/torq.txt`) confirms the round closed on 12 Jan 2026.
2. **Wrong event type.** CyberArk shows "1 · latest **shutdown**, 11 Feb 26". The cited source is a Form 15-12G deregistration filed after Palo Alto Networks completed the acquisition. The company was acquired, not shut down.
3. **Row mislabelled as the company.** The Email security table has two rows named "Check Point" (`title="Check Point"` on both). One is the company, "1% Q Jun 26". The other is the Harmony Email product, labelled only "Segment".
4. **Nozomi Networks.** Ownership shows "–" and events show "0" (also counted under blocker 2).
5. **Smaller date mislabels.** Lakera shows "Acquired by Check Point · Sep 2025" beside "latest acquisition, **31 Dec 25**". Rubrik's prior-quarter drawer gives "Publication date 2026-04-30", which is the period end and not the date the results were published.

### Blocker 4 detail

- `web/src/data/runStatus.ts` says of the value: *"This is a static value today, hand-set at each publish."* It holds `lastChecked: "2026-09-26", state: "updated"`.
- `web/src/data/generated/edgarFacts.json` has `"generatedAt": "2026-09-25T22:51:28.098Z"`, and no commit changed it on 26 Sep.
- On 26 Sep, `git log` shows one collector "proof run" that added a single fact (Optiv, `cf9bbac`) and hand-edited fix passes (`b2bcfe5`). `gh run list` shows no collection workflow run.
- The served page itself dates 214 of its 216 source records "2026-09-25" and 2 "2026-09-26" (`grep` on the aria-labels in `raw_.html`).
- So the claim that every source was collected and checked on 26 Sep is not supported. The honest states were "no material change" dated 25 Sep, or "incomplete". If a run log exists that I could not see and it shows a full collection on 26 Sep, this blocker would flip to pass.

## Figure verification (23 figures, 18 public issuers)

Documents were fetched with the User-Agent `SecurityMarketPulse blind scorer <email>`. Text copies are in `src/*.txt`.

| Figure on page | Filing text | OK |
|---|---|---|
| CrowdStrike +26% Q Jul 26; ARR $5.84B | "Total revenue was $1.47 billion, a 26% increase"; "ARR grew 25% … to $5.84 billion" | yes |
| CrowdStrike prior +26% Q Apr 26 | Q1 FY27: "$1.39 billion, a 26% increase" | yes |
| Palo Alto +34%; NGS ARR $9.10B | "grew 34% … to $3.41 billion"; "NGS ARR … grew 63% … to $9.10 billion" | yes |
| Palo Alto prior +31% | "grew 31% … to $3.0 billion" | yes |
| SentinelOne +21%, prior +21%, ARR $1.218B | "$292 million, compared to $242 million"; Q1 "$277 million"; "ARR grew 22% to $1,218 million" | yes |
| Cloudflare 36%, $696.1M | "revenue totaled $696.1 million, … increase of 36%" | yes |
| Fortinet 26%; billings $2.37B | Total revenue 2,047.9 against 1,630.0 is +25.6%; "Billings grew 33% … to $2.37 billion" | yes |
| Netskope 29%; ARR $899M | "Q2 revenue increased 29%"; "ARR increased 27% … to $899 million" | yes |
| Zscaler 25%; ARR $3,771M | "Grew 25% … to $898.2 million"; "ARR … $3,771 million" | yes |
| Okta 11% Q Jul 26 | Total revenue 805 against 728 is +10.6% | yes |
| SailPoint 16.8%; ARR $1,230.7M; prior 21.5% | 308,813 against 264,359 is +16.8%; "ARR $1,230.7"; Q1 280,142 against 230,468 is +21.55% (the page rounds down, which is trivial) | yes |
| Commvault +11%, prior +13%, Sub ARR $1,054M | "$314,131 11%"; "$311,692 13%"; "Subscription ARR … $1,054 million" | yes |
| Rubrik +38%; Sub ARR $1.66B | "Total revenue was $427.3 million, a 38%…"; "ARR grew 33% … to $1.66 billion" | yes |
| Varonis +18.3%; prior +27% | $180.0M against $152.2M; six-month totals give Q1 173,126 against 136,423 = +26.9% (the drawer shows the Q2 period, not Q1) | yes |
| Qualys +11%; Rapid7 −1.5%, ARR $824M; Tenable +8.6% | "Q2 Revenue Growth of 11%"; "$211 million", "ARR of $824 million"; "$268.5 million, … 8.6%" | yes |
| Check Point 1%, $674M | "Total Revenues: $674 million, a 1 percent increase" | yes |
| Google SecOps drawer: Google Cloud +82%, $24.8B | "revenues increased 82% to $24.8 billion" | yes |

**Fiscal-period labels checked:** SailPoint Q2 FY2027 (fiscal year ends 31 Jan; its 10-Q is for the quarter ended 31 Jul 2026), Zscaler Q4 FY2026, Netskope Q2 FY2027, Commvault Q1 FY2027, and CrowdStrike "Second Quarter Fiscal 2027". All are correct. The "Q Jul 26" shorthand is the quarter-end month, which is correct. The Palo Alto "10-K (derived)" filing dated 10 Sep 26 matches EDGAR (a 10-K filed 2026-09-10).

**Every segment row** (`sources.json`):

| Row | Label | Correct? | Source quality |
|---|---|---|---|
| Microsoft Defender for Endpoint | Segment of Microsoft | yes | Links to `microsoft.com/en-us/investor`, an index page with nothing specific. The FY26 10-K does name the product. |
| Google SecOps | Segment of Alphabet | yes | Alphabet Q2 exhibit, which supports it. |
| Palo Alto Networks Cortex XSIAM | "Segment" | yes | Links to the `investors.paloaltonetworks.com/` home page. |
| Splunk | Segment of Cisco Systems | yes | Cisco exhibit 99.1, "Cisco Completes Acquisition of Splunk". |
| CrowdStrike Falcon Exposure Management | "Segment" | yes | Links to the CrowdStrike Q2 release, which does not mention Exposure Management. |
| Check Point (Email) | "Segment" | label is the company name (see blocker 1) | The Q2 release lists Email Security only in the product menu. |
| Microsoft Entra ID | Segment of Microsoft | yes | FY26 10-K, which never names Entra. |
| Microsoft Defender for Office 365 | Segment of Microsoft | yes | FY26 10-K, which never names Defender for Office 365. |

GitHub Advanced Security shows "–" for ownership, with no source and no "Segment of Microsoft" label.

**Staleness candidates** (EDGAR submissions API, `src/sub_*.json`, `src/later.txt`):

- No public issuer has filed results newer than the figure shown. That covers all 18 checked: CRWD, PANW, S, NET, FTNT, NTSK, ZS, OKTA, SAIL, CVLT, RBRK, VRNS, QLYS, RPD, TENB, FROG, CHKP and MSFT.
- **Nozomi Networks** is stale by 241 days. Its newsroom (`src/nozomi.txt`) reads: "January 28, 2026 Nozomi Networks Enters Next Phase of Growth as Mitsubishi Electric Completes Acquisition".
- **Rapid7** is stale by 21 days beyond the last shown event. Its 8-K, filed 2026-08-31, says four directors resigned on 27 Aug (`src/rpd_8k_0827.txt`).
- **Okta** filed an 8-K on 18 Sep about a director resignation. That is 8 days old, inside the 14-day line.
- **Commvault** filed an 8-K on 24 Sep about a director appointment. That is 2 days old, inside the line.
- **Ping Identity** (ARR "approaching $800M", Nov 2024) and **Abnormal** (ARR "over $200M", Aug 2024) could not be checked. Both newsrooms render with JavaScript, and web search was unavailable.

## Judgment-language grep (served text of every live route)

`home-1440-text.txt`, `corrections-1440-text.txt`, `issues*-text.txt`, `thesis-1440-text.txt`, searched with a stance, forecast and ranking word list:

- `/`: the only hit is Zenity's own-metric cell, "on track to triple again in 2026". It is marked company-stated, so I treated it as a reported claim and not the site's forecast. "Posture" appears only in domain definitions.
- `/corrections/`: "Watch whether it survives as a product or becomes a feature." This is the blocker 3 failure.
- The archive (`/issues/`, `/issues/2026-w36/`, `/thesis/`) is full of stance language, for example "the infra-to-security lag call holds", "strongest reacceleration" and "Rubrik and Varonis are accelerating". It is exempt, but see D5 level 5, test 3.
- The front page's closed "How this is built" section still carries method text from the retired judged product ("Date the posture; show the delta … Every domain posture carries the date it was set").

## D1: Freshness without fail, score 2 (cap: 3)

| Test | Result | Evidence |
|---|---|---|
| L3-1 Run status stated without expanding | yes | "Figures checked 26 Sep 2026 · every source collected." (`home-1440-fold.png`) |
| L3-2 Checked date on the first screen at both widths | yes | `home-1440-fold.png`, `home-390-fold.png` |
| L3-3 Sampled figures within 14 days of the company's newest | **no** | Nozomi 241 days; Rapid7 21 days (see above) |
| L3-4 Dated "what changed" list visible | yes | "What changed in the last 30 days", 27 dated items |
| L5-1 Fact date shown separately from the checked date | yes | Drawer shows "Publication date" and "Economic period"; the run-status line carries the checked date |
| L5-2 A failed source is named in plain language | no | The mechanism is not visible on the page |
| L5-3 Age of the newest fact readable without arithmetic | yes | "24 Sep 26" at the top of "what changed" |
| L5-4 Refresh cadence in one sentence, not contradicted | no | "Tracked figures arrive through the week as companies report them" is not a cadence, and `feed.xml` says "Weekly issues … one per ISO week" |

Three of the level-5 tests are credit waiting. **To raise it by one:** show Nozomi's acquisition and Rapid7's board change, so the sample finds nothing past the 14-day line.

## D2: Coverage, score 4

| Test | Result | Evidence |
|---|---|---|
| L3-1 Domain list, one sentence each, within one click | yes | "What this site covers" section, 12 one-line definitions |
| L3-2 Every domain lists a supplier | yes | 6 or 7 rows in each of the 12 tables |
| L3-3 "Not covered" list within one click | yes | Seven "Not covered" items |
| L3-4 A distress or consolidation place that says "nothing" | yes | The "Events, 12 mo." column shows "0" (its accuracy is a blocker 1 problem) |
| L5-1 Stable address for every domain and supplier | **no** | 12 `#domain-*` ids; no supplier ids (`grep id= raw_.html`) |
| L5-2 Counts stated | yes | "12 domains, 74 tracked suppliers." |
| L5-3 Inclusion is a data fact | yes | "being listed is not a recommendation and being absent is not a criticism" |
| L5-4 Untracked distinguishable from quiet | yes | A tracked supplier with no news shows 0; an untracked one is absent |

**To raise it by one:** give each supplier row a stable anchor id.

## D3: Deciding a supplier's footing from facts alone, score 4

| Test | Result | Evidence |
|---|---|---|
| L3-1 Same metric and period basis in one table | yes | "Rev. growth" is year-over-year GAAP revenue for the named quarter, stated above the tables |
| L3-2 Domain reachable in one click at both widths | yes | Jump links (keyboard stops 9–20 at 1440, 4–15 at 390); `jump-identity-*.png` |
| L3-3 One supplier's latest, prior, ownership and events in one place | yes | The Okta row at 1440 (`jump-identity-1440.png`) |
| L3-4 No ranking or judgment order | yes | Default sort is alphabetical ("Supplier ↑") |
| L5-1 Computed reference point in each domain | **no** | Medians show in 7 of 12 domains; SIEM, MDR, AppSec, Email and AI security have none and no note saying why |
| L5-2 Reader can re-order | yes | Sorting Identity by Rev. growth changes the order (`interact.json`) |
| L5-3 The supplier question in under a minute | yes | Jump link, then the row, then the `src` drawer |
| L5-4 Same number of interactions at 390 | **no** | At 390 each row is collapsed; prior quarter, ownership and events need a tap (`interact.json` visBefore/visAfter, `okta-expanded-390.png`) |

**To raise it by one:** show a median (or a line saying "no median: one public figure") in every domain, and show the facts at 390 without a tap.

## D4: Evidence legibility and reconstructability, score 2

| Test | Result | Evidence |
|---|---|---|
| L3-1 Source beside every figure | yes | 217 `src` controls; every shown figure has one |
| L3-2 Source resolves to a checkable document | **no** | Several go to index or home pages: Delinea CFO goes to `https://www.globenewswire.com/`; Delinea ARR and ownership go to `https://www.delinea.com/`; BeyondTrust goes to `beyondtrust.com/`; Cortex XSIAM and Defender for Endpoint go to IR home pages; Veeam goes to Wikipedia; BigID goes to Tracxn |
| L3-3 Method stated within one click | yes | The "How this is built" section, plus the sentence above the tables |
| L3-4 Fact date and checked date kept distinct | yes | Drawer publication date; run-status checked date |
| L5-1 Publisher and date in one interaction | yes | `okta-src-390.png` |
| L5-2 Says so when no like-for-like figure exists | no | Bare "–" (for example Qualys and Tenable prior quarter) with no reason |
| L5-3 Sourcing standard within one click | yes | "The sourcing ladder …" in "How this is built" |
| L5-4 Report-a-wrong-figure from the evidence | no | The drawer has no report link; only a general email exists |

The drawer also shows internal labels ("Packet label SEC-MARKET-AUTO-001-STEP5 / TR-okta-1"). **To raise it by one:** point every source at the specific document, not a newsroom or home page.

## D5: Trust, score 2

| Test | Result | Evidence |
|---|---|---|
| L3-1 No judgment language on a live page | **no** | `/corrections/`: "Watch whether it survives as a product or becomes a feature." |
| L3-2 Facts-only, automatic, no approver, stated within one click | yes | "published automatically — no human approval step, and no machine judgment" |
| L3-3 Corrections page with dates | yes | `/corrections/` lists entries dated 21 Sep and 20 Sep |
| L3-4 Contact visible without expanding | yes | "Send a correction or a question Jesse Pike · jesse@keatingpike.com" |
| L5-1 Operator and relationship to suppliers | no | Only "Run by Jesse Pike"; no relationship statement |
| L5-2 How suppliers are chosen; competitor and partner parity | no | Not found in the served text |
| L5-3 Archive visibly separated | no | `/thesis/` says "no longer updated", but it is stamped "UPDATED September 26, 2026" and the site banner on it says "No stances, rankings or forecasts" |
| L5-4 Corrected fact keeps its original wording | no | "The standing tables are different: a wrong entry there is fixed in place" |

**To raise it by one:** remove the quoted forecast from `/corrections/` or paraphrase it neutrally. If a second scorer reads the quotation as record-keeping, this test flips and D5 becomes 3.

## D6: Density and scanability, score 2

| Test | Result | Evidence |
|---|---|---|
| L3-1 At least 8 suppliers per screen, or the whole table | yes | Each table of 6–7 rows fits in one screen (`jump-identity-1440.png`) |
| L3-2 Tabular figures; distinct metadata treatment | yes | `.tracker-figure__value{font-variant-numeric:tabular-nums}`; periods set in mono |
| L3-3 Body text ≥14px and lines of 50–80 characters | **no** | Body is 16px, but the intro wraps at 90 characters per line and the method paragraph at 86 (`home-1440-fold.png`) |
| L3-4 Quiet and eventful suppliers differ | yes | "0" against "3 · latest debt, 30 Jul 26" |
| L5-1 Page under 6,000px | no | 8,755px (`measure.json`) |
| L5-2 Fixed-column tables | yes | |
| L5-3 No reading text under 13px | no | The banner tagline is 10px |
| L5-4 A full table visible without scrolling | yes | |

**To raise it by one:** cap the prose measure at about 70 characters.

## D7: Phone, score 2

| Test | Result | Evidence |
|---|---|---|
| L3-1 Run status and one domain on the first screen at 390 | **no** | The first screen ends at the method paragraph (`home-390-fold.png`) |
| L3-2 Chrome no more than a quarter of the viewport | yes | First content at 174px against 211px |
| L3-3 Every tap target ≥24×24 | **no** | Jump-list links are 20px tall; the footer data links are 15px (`measure.json` home-390) |
| L3-4 No horizontal scroll at 390 or 320 | yes | scrollWidth equals clientWidth at both |
| L5 (credit waiting) | 1 of 4 | Full facts need an extra tap; 11px and 9.75px text exists; the jump list works the same; rows are collapsed |

**To raise it by one:** move the run status and the jump list into the 390 first screen, and make the jump links 24px tall.

## D8: Accessibility, score 4

| Test | Result | Evidence |
|---|---|---|
| L3-1 No critical or serious axe violations | yes | `axe-home-1440.json`, `axe-home-390.json`, `axe-corrections-1440.json`, `axe-corrections-390.json`, all `[]` (axe-core 4, wcag2a/aa, 21, 22aa and best-practice tags) |
| L3-2 Keyboard reachable with visible focus | yes | `keyboard.json`: every stop has a `solid 2px rgb(11,107,94)` outline; sort, row and `src` controls are all reachable |
| L3-3 Contrast | yes | No color-contrast violations |
| L3-4 Reflow at 320 | yes | |
| L5-1 Zero violations of any impact | yes | |
| L5-2 Targets ≥24 or a listed exception | yes | `src` buttons are 27×19, but table rows are 34px apart, so the spacing exception holds; footer links fall under the inline exception |
| L5-3 Skip link first; market within 15 Tabs | yes | Tab 1 is the skip link; tab 5 is "Market" at 1440, and tab 4 is the first domain link at 390 |
| L5-4 Landmarks and `time[datetime]` throughout | **no** | 24 `time` elements, but the 40 event dates in the tables are plain text |

**To raise it by one:** wrap the table event dates in `<time datetime>`.

## D9: Performance, score 2

Lighthouse, three runs each, with the Chromium bundled with Playwright inside the OrbStack VM (`lh-m*.json`, `lh-d*.json`).

- **Mobile:** LCP 4,041 / 4,092 / 4,091 ms (median 4.09s); TBT about 63ms; CLS 0.
- **Desktop:** LCP 984 / 983 / 1,217 ms; TBT 0; **CLS 0.177**.

| Test | Result |
|---|---|
| L3-1 Mobile LCP ≤2.5s | **no** |
| L3-2 CLS ≤0.1 at both profiles | **no** (desktop 0.177) |
| L3-3 Mobile TBT ≤300ms | yes |
| L3-4 Desktop LCP ≤1.5s | yes |

The level-5 tests are credit waiting: 279–337 KB total, 142–165 KB of JavaScript, and no render-blocking resources. **To raise it by one:** find the desktop layout shift and the cause of the 4-second mobile LCP.

## D10: Machine legibility, score 3

| Test | Result | Evidence |
|---|---|---|
| L3-1 Figures are in the prerendered HTML | yes | |
| L3-2 JSON-LD with page type, publisher and date | yes | A valid `Report` with a `publisher` Organization and `dateModified` 2026-09-26 |
| L3-3 Feed or index discoverable from home | yes | `<link rel="alternate">` to the RSS feed and JSON; `robots.txt` lists the sitemap |
| L3-4 No empty headings or duplicate ids | yes | |
| L5-1 Structured tracker endpoint | no | `/tracker.json` returns 404; the JSON on offer is archive data |
| L5-2 Per-figure anchors | no | |
| L5-3 Publisher is a resolvable entity | yes | Organization with a `url` |
| L5-4 Deliberate crawler policy | no | `User-agent: * Allow: /` |

**To raise it by one:** publish the tracker as JSON with per-figure ids.

## D11: Craft, score 2

| Test | Result | Evidence |
|---|---|---|
| L3-1 One sans, one mono, no more than 6 sizes | **no** | IBM Plex Sans plus Archivo plus IBM Plex Mono; 14 sizes on the front page |
| L3-2 One accent, light theme only | yes | No `prefers-color-scheme` rule |
| L3-3 No collisions, clipping or overflow | yes | Captures at 1440, 390 and 320 |
| L3-4 No decoration without information | yes | |
| L5-2 Repeated patterns identical | no | Signs vary ("+26%" against "1%", "11%"); column widths differ per table; `src` wraps below the value in some cells |

**To raise it by one:** drop Archivo and collapse the type scale to six sizes.

## Other observations (not scored)

- The GitHub `web` workflow failed on `8fa5359` (run 36253436535).
- Palo Alto Networks' whole-company figure appears in five domains, and CrowdStrike's in three.
- The drawer and the "what changed" list show internal wording: "Packet label", and "filed its 10-K (derived)".
