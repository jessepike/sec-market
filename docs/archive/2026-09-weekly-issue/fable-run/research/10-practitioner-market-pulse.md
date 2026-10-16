# T5-3: What a practitioner market read should look like

Research task for SEC-MARKET-FABLE-001. Written 2026-09-20. Covers five questions about who already
serves security practitioners with a market read, what CISOs actually want, how credible products
show vendor standing without sounding like investment advice, what makes a solo practitioner site a
trusted asset, and what cadence promise holds up. This round is aimed at practitioner-facing market
reads, not thesis-driven newsletters or paid data products, which the earlier research round
(files 01 to 09 and research-synthesis.md) already covered. I have not repeated that ground except
where a source needed a second, more specific look.

## What this means for the site

The first screen should say, in one plain sentence, what the site is and who it is for, and then
show this week's actual read, not a list of funding rounds. Every peer I opened gets this wrong in
the same way: Software Analyst Cyber Research, Return on Security, and Venture in Security all lead
with brand and a subscribe box rather than with a reader's question answered. The one thing that
consistently earns trust on a first screen, based on Return on Security's about page, is a plain
sentence about what the site refuses to do ("this isn't a place for threat feeds"). Security Market
Pulse should do the same for investment advice and daily news, on the first screen, not buried in a
method page.

The by-domain view should read like Gartner's "overall viability" criterion, not like a league
table: state the vendor's financial health, whether the business is still being invested in, and
say plainly what evidence that rests on (a filing, a funding round, a headcount count, a reported
estimate). Never write a domain-leader claim the way the CISO Whisperer piece does, with adjectives
and no sourcing and no disclosed relationship to the vendors named. For private companies with no
filings, follow IT-Harvest's practice of labelling a number as an estimate at the point it appears,
and RapidRatings' practice of a single plain label attached to an explicit statement that it is
operational risk information, not a credit rating and not investment guidance.

Distress and consolidation should be treated exactly the way the product core file already proposes
tracked facts: a dated funding round, an M&A filing, a layoff report, each with its own source and
its own date, kept separate from any posture judgment built on top of it. Pinpoint Search Group and
Momentum Cyber both do this well for the facts (dated, sourced, itemized) and both fail to say
anything a CISO can use about what a given round or deal means for a program; that gap is exactly
what this site is for.

Author presentation should be direct rather than modest. Every trusted solo practitioner I found
(Brian Krebs, Troy Hunt, Mike Privette, Patrick Gray) names himself plainly, states his background,
and either states or makes obvious what he does for a living. None of them hide the connection
between their day job and their public work; Privette says outright he is a former CISO. The
owner's advisory work and his employer should be stated on the site, not left implicit, because the
CISO Whisperer case shows what an undisclosed commercial tie costs a market-standing piece: no one
can tell whether the vendors named paid to be there.

The cadence promise should be a specific day and a specific scope, sized to what will actually keep
happening, and it should say the current age of the data next to the data itself. The newsletter
failure research is blunt on this point: newsletters that drift from "weekly" to "whenever" lose
their readers within a few missed issues, and a site cannot promise in week one a cadence it cannot
keep in week forty. Momentum Cyber's approach (infrequent, versioned, no stated schedule) is the
one credible counterexample, and it works only because the publisher already has industry-wide
reach; a new site does not have that option and should promise less, on a fixed day, and keep it.

## Question 1: who already serves practitioners with a market read

**Software Analyst Cyber Research.** https://www.softwareanalyst.io/. Opened 2026-09-20. Read on
the page. States it is for "CISOs and security practitioners" seeking vendor-independent research.
The first screen presents itself as a "modern cybersecurity analyst firm" with a call to explore
reports; it does not put a vendor-leadership view or a market call on the first screen. Reports are
titled market maps (for example, one on "the rise of UADP" and platform consolidation), but the
page itself does not show a ranked or labelled view of who leads a domain. The one named person is
Lawrence Pingree, "Head of Research," with ten years at Gartner; the founder Francis Odum (found
separately, see below) is not named on this particular page render. Report dates run from February
through September 2026, which reads as a steady but not strictly weekly cadence.

**Francis Odum, founder of SACR.** https://www.favikon.com/blog/who-is-francis-odum,
https://ca.linkedin.com/in/francis-odum-0a8673100. Opened 2026-09-20. Second-hand (a profile write-
up, not Odum's own page). Reported to have built a following of more than 60,000 people and to
teach paid bootcamps through Maven. The clearest example in the set of a market analyst whose
public research is also his professional identity, the shape the owner wants for himself.

**Return on Security.** https://www.returnonsecurity.com/ and
https://www.returnonsecurity.com/about. Opened 2026-09-20. Read on the page. States it is for
"cybersecurity operators, founders, and investors." The first screen is a subscribe box under the
line "the business of the cyber industry, with zero fluff." It runs a weekly section called
"Security, Funded" for funding, M&A, and what it calls "category movement that actually moved the
industry." It does not present a ranked view of who leads a domain; instead it frames pieces
around what a category's investor and practitioner interest says about which platforms are likely
to survive (a piece on the AI-era GRC market was framed as "what investors fund, what practitioners
need, and which platforms survive"). On the about page, Mike Privette identifies himself as "a
former CISO turned creator, market analyst," states plainly "this isn't a place for threat feeds or
zero-day alerts," and does not carry an explicit "not investment advice" disclaimer despite the
funding and M&A focus.

**IT-Harvest.** https://it-harvest.com/. Opened 2026-09-20. Read on the page. States it serves
"investors, M&A teams, marketers, and security architects," a wider audience than the other
practitioner-facing sources. It tracks more than 4,000 vendors and 11,000 products with profiles
covering headcount, growth, funding, revenue estimates, M&A relationships, and framework mapping
(NIST CSF, MITRE ATT&CK). It explicitly instructs that claims sourced from its dashboard be
attributed with a link, and calls its market counts "time-sensitive Dashboard observations rather
than permanent market totals," which is a clean example of a freshness caveat stated at the point
of use. Data refreshes on a stated quarterly cycle: "re-ingests product data from roughly 4,100
vendors every quarter," with continuous monitoring for events like acquisitions and shutdowns
between refreshes. The page does not name Richard Stiennon or otherwise disclose authorship.

**IT-Harvest's Cyber 150.** https://cyber150.com/IT-harvest-dashboard/. Opened 2026-09-20. Read on
the page, but it is a promotional landing page for the dashboard rather than the list itself; it
names the Cyber 150 list of fastest-growing companies but shows none of its methodology and states
no update schedule. I did not chase a separate URL and am not claiming to know how the ranking is
built.

**Richard Stiennon and IT-Harvest, background.** https://pulse2.com/it-harvest-profile-richard-
stiennon-interview/, https://www.linkedin.com/in/stiennon/. Opened 2026-09-20. Second-hand
(interview and profile pages, not IT-Harvest's own site). Stiennon founded IT-Harvest in 2005 after
time at Gartner, Webroot, and Fortinet, and also publishes an annual print Security Yearbook. A
twenty-year build, which matters for the cadence-and-trust question below.

**Pinpoint Search Group.** https://pinpointsearchgroup.com/cybersecurity-industry-reports/. Opened
2026-09-20. Read on the page. Pinpoint is a cybersecurity executive search firm that publishes
monthly, quarterly, and annual funding and M&A briefs going back to 2020, and in mid-2026 launched a
live funding database tracking more than 2,600 transactions. The August 2026 brief shown on the page
displays raw counts ($1.27B raised, 20 rounds, 16 M&A) with the underlying itemized data reserved
for paid subscribers. The page states plainly that the recruiting firm runs this as a lead-
generation and credibility tool for its search business, which is an honest and visible version of
exactly the dynamic the owner is trying to create for his own advisory work.

**Momentum Cyber, CYBERscape.** https://momentumcyber.com/cyberscape-4-0/. Opened 2026-09-20. Read
on the page. CYBERscape 4.0 maps 1,562 companies across 12 sectors and 62 subsectors. It does not
rank individual vendors; instead it names structural patterns such as "platform control points
where power is consolidating," "capital concentration zones," and "M&A hotspots." No update
schedule is stated; the version numbering (1.0 through 4.0) implies infrequent, large rebuilds
rather than a running cadence. Momentum Cyber is an investment bank that arranges cybersecurity
M&A, and the page does not soften that: this is a lead-generation map built by a party with a direct
financial stake in the deals it maps.

**tl;dr sec.** https://tldrsec.com/. Opened 2026-09-20. Read on the page. Curated by Clint Gibler
for a claimed 90,000-plus subscribers, in roughly seven minutes a week. This is almost entirely
technical security research and tooling content (vulnerability research, hardening guides, AI
security techniques); it carries essentially no coverage of vendor funding, growth, or market
consolidation. It confirms the product-core distinction the owner already draws: this is a security
news and research digest, not a market pulse, and it is a useful negative example of the category
this site should not become.

**The Cyber Why, Tyler Shields.** https://www.thecyberwhy.com/. Opened 2026-09-20. Read on the
page. Weekly, aimed at readers who already have "informed perspectives on cybersecurity," and
explicitly promises "zero tolerance for vendor spin." I could not see, from the page I opened, how
it actually presents which vendors are leading a category or how it treats distress; the page shown
was mostly branding and a testimonial. It carries no visible employer disclosure or bias statement
for Tyler Shields himself on this page.

**Venture in Security, Ross Haleliuk.** https://ventureinsecurity.net/. Opened 2026-09-20. Read on
the page, but the render I got was mostly the Substack masthead (title, subscriber count over
22,000, three endorsement quotes) rather than article content, so I cannot say from this render how
it treats domain leadership or distress. It states it serves "security practitioners, entrepreneurs,
investors and executives." Haleliuk presents as an independent author rather than as speaking for an
employer.

**Gartner Magic Quadrant, as the incumbent mental model.** I could not open
https://www.gartner.com/en/methodology/magic-quadrants-critical-capabilities directly; the request
returned HTTP 403. What follows on Gartner's methodology is second-hand, from search-result
summaries of Gartner's own published methodology language, not from a page I opened myself. Gartner
scores vendors on two axes, "ability to execute" and "completeness of vision," and one named
component of "ability to execute" is "overall viability": an assessment of the vendor's financial
health, the health of the specific business unit behind the product, and the likelihood that the
business keeps investing in that product. This is the closest existing model to "which two or three
vendors are on solid footing and why," and it is the model most CISOs already carry in their heads,
which is why the site should either use compatible language or explicitly say where it differs.

**Gartner Peer Insights, as a contrast to analyst opinion.** Second-hand, from search-result
summaries of Gartner's own vendor-portal FAQ pages (I did not open gpivendorresources.gartner.com
directly). Peer Insights scores are stated to be a straight average of end-user reviews, explicitly
labelled as customer opinion rather than fact, with the disclosure line "should not be construed as
statements of fact, nor do they represent the views of Gartner." That disclosure pattern, stating in
plain words that a number is opinion and not fact, is a pattern worth copying.

**CISO Whisperer, "11 vendors leading the shift."**
https://www.prnewswire.com/news-releases/ciso-whisperer-names-11-vendors-leading-the-shift-from-
tools-to-outcomes-at-rsa-conference-2026-302718849.html. Opened 2026-09-20. Read on the page. This
is a practitioner-branded voice naming specific vendors as leaders, grouped by theme ("platform
consolidation takes hold," "securing critical infrastructure"), with reasoning that is entirely
qualitative: a vendor is described by its positioning language, not by any growth, funding, or
customer number. There is no stated methodology, no disclosure of which vendors paid for
inclusion or have a commercial relationship with the author, and no mention of vendors considered
and excluded. This is the clearest anti-pattern in everything I opened for this task: a market-
leadership claim, published as a press release, made by a practitioner-facing voice, with zero of
the evidence discipline the owner's own product core asks for.

**CyberScoop op-ed on AI reshaping the cybersecurity market.**
https://cyberscoop.com/ai-cybersecurity-market-trends-2026-op-ed/. Opened 2026-09-20. Read on the
page. Written by venture capitalists, explicitly framed for investors and founders, arguing the
market is becoming "binary" between AI-native companies "built to scale" and legacy companies "built
to sell." This is investor market commentary dressed as industry analysis, exactly the framing the
owner has said the site is not for.

**Dark Reading, layoffs coverage.** https://www.darkreading.com/cybersecurity-analytics/
cybersecurity-firms-chase-ai-vc-market-skyrockets and
https://www.darkreading.com/careers-and-people/layoffs-mount-cybersecurity-vendors-hunker-down.
Could not open; both returned HTTP 403. Second-hand, from search-result snippets only: Dark Reading
and CSO Online both run occasional business-of-security pieces (layoffs, VC funding) inside a
primarily news-and-vulnerability publication, not as a standing, dated market section.

## Question 2: what a CISO actually wants from a market read

**TechTarget, "CISO's guide to security vendor consolidation."**
https://www.techtarget.com/searchsecurity/tip/CISOs-guide-to-security-vendor-consolidation. Opened
2026-09-20. Read on the page. This is analyst and practitioner guidance, not a first-hand survey. It
recommends shorter contracts with smaller or lesser-known vendors and holding startups to roadmap
commitments contractually, as a hedge against a vendor's future health. It does not offer any actual
method for assessing financial health up front; the caution is entirely contractual, after the
purchase decision.

**Vendor viability and financial-stability signals for private companies.** From search-result
summaries of Security Boulevard, ProcessUnity, and Safe Security, not the full pages, so second-
hand. Recurring advice: track a private vendor's funding runway, investor quality, and path to
sustainability, on the reasoning that "a drop in a vendor's financial stability often precedes a
drop in their security investments." This matches the product-core file's instinct that a slowdown
in a vendor's growth relative to peers is itself a signal worth surfacing, even without a filing.

**CISO survey data on vendor consolidation.** Second-hand, from search-result snippets of
digital-chiefs.de and a Splunk 2026 CISO report press summary; I could not open either report in
full (the RH-ISAC CISO Benchmark PDF I fetched returned only binary structure, no readable text, so
I am treating it as could not open despite the fetch succeeding technically). The recurring figure
across secondary sources is that roughly two-thirds of technology and security leaders are actively
trying to consolidate vendors, and that vendor concentration risk is called out as an underweighted
risk. I would not put a specific percentage into the site from this evidence.

## Question 3: presenting vendor standing without sounding like investment advice

**Gartner's "overall viability" criterion.** Second-hand, as above. The pattern worth copying is
naming the criterion plainly (is this business financially healthy, and will it keep funding this
product) rather than producing a single opinionated rank.

**Gartner Peer Insights' disclosure line.** Second-hand, as above. The pattern worth copying is a
one-line disclaimer, placed next to the data itself, stating plainly that a number is opinion or
estimate and not verified fact.

**RapidRatings.** https://en.wikipedia.org/wiki/RapidRatings. Opened 2026-09-20. Read on the page.
RapidRatings sells a single "Financial Health Rating" on a 0 to 100 scale, aimed at procurement,
supply-chain risk, and third-party risk teams, not investors. The Wikipedia summary states the
company has deliberately chosen not to register as a Nationally Recognized Statistical Rating
Organization, specifically to avoid the liability and disclosure obligations that come with being
an investment-grade credit-rating agency. This is the cleanest example I found of a company that
wanted to score financial standing for buyers, not investors, and structured itself so the score
could never be mistaken for one. It is a strong precedent for how the site can score "on solid
footing" without drifting into investment-grade language.

**Momentum Cyber's structural framing.** As above. Naming "where power is consolidating" and "M&A
hotspots" instead of ranking named vendors says something about domain dynamics without a per-vendor
score, though it is also vaguer and less directly useful to a CISO deciding about one vendor.
**IT-Harvest's attribution and freshness instruction**, as above, labels a number as a "time-
sensitive Dashboard observation" at the point where it is shown rather than in a separate methods
page, a pattern worth copying directly. **CISO Whisperer, as the negative example**, as above, shows
what makes a vendor-standing claim read as promotional: no criteria, no sourcing, no disclosed
relationship, no acknowledgment of what was left out.

## Question 4: what makes a solo practitioner's site a credibility asset

**Brian Krebs, KrebsOnSecurity.** https://krebsonsecurity.com/about/. Opened 2026-09-20. Read on
the page. Krebs states his fourteen years at The Washington Post and describes his sourcing as
"direct access to some of the smartest and most clueful geeks on the planet." The page does not
explain a formal method for separating fact from opinion; the credibility instead rests on a long,
visible track record of stories nobody else had. This matters for the cadence question: Krebs's
authority was built by years of output, not by a single well-designed page.

**Troy Hunt, Have I Been Pwned.** https://haveibeenpwned.com/About. Opened 2026-09-20. Read on the
page. Hunt runs the site with his wife handling operations and one part-time engineer; he names
himself, states his Microsoft Regional Director credential, and explains plainly where the
underlying data comes from ("breaches where data is exposed to persons that should not have been
able to view it"). The page states no data-freshness cadence and no formal verification procedure;
trust rests on a decade of the tool doing one useful thing correctly, plus agencies like the FBI
visibly relying on it (reported second-hand from an ABC News profile, not the About page itself).

**Mike Privette, Return on Security.** As above. States his background as a former CISO up front,
which is the single clearest disclosure move in the set: readers know immediately what kind of
authority is behind the opinions.

**Patrick Gray, Risky Business.** https://risky.biz/about/, read only through search-result
snippets, so this is second-hand. Running since 2007, with two spun-off newsletters written by named
staff. The search summary describes his differentiator as "actual sources and explicit opinions
about which incidents matter," where most competitors summarize press releases. Nearly twenty years
of continuous output is itself the credibility asset here.

**What kills a solo credibility site.** https://calibrational.substack.com/p/i-analyzed-50-failed-
newsletters and https://howtogrowanewsletter.substack.com/p/burnout-will-kill-your-newsletter.
Opened 2026-09-20. Read on both pages, though both are general newsletter-growth advice, not
security-specific. The failure-analysis piece reports that of fifty failed newsletters studied,
thirty-four "started weekly, then went to 'whenever I feel like it,'" while the newsletters that
survived published "on the same day, same time, every week" with "zero missed issues" over a year.
The second piece states the mechanism plainly: "one missed issue becomes two, two becomes a hiatus,
a hiatus becomes the end," and warns against setting "a cadence in week one that you will not be
able to maintain in week forty." Neither is security-specific, so I treat these as a pattern, not a
security-market fact, but the pattern matches what the project's own scorecard already found.

## Question 5: the right cadence promise

**IT-Harvest.** As above. States a specific, honest cadence: full re-ingestion roughly every
quarter, with continuous monitoring for named events (acquisitions, shutdowns) in between. This is
an example of a site that is explicit about being "mostly still, occasionally refreshed" rather than
claiming to be live.

**Pinpoint Search Group.** As above. Monthly briefs, on a visible monthly rhythm since 2020, each
one dated and itemized. This is the cleanest example of "the same day, roughly the same format,
every time" in the set.

**Momentum Cyber's CYBERscape.** As above. No stated schedule; four major versions over what
appears to be years. This works for Momentum Cyber because the brand already has industry-wide
distribution and each release is itself an event people wait for. It would not work for a site
without that distribution yet, which is this site's actual position today.

**Return on Security.** As above. Weekly, with a named "Security, Funded" section that appears to
run on its own weekly rhythm distinct from the main briefing, which is a workable model for this
site's split between tracked facts and judged calls: two cadences, each honestly labelled, rather
than one blended promise.

**General newsletter cadence research.** As above. The clearest, most transferable finding: pick
the slowest cadence you can guarantee, state it once, and never promise in week one a cadence that
will not still be true in week forty.

## Could not open

- https://www.gartner.com/en/methodology/magic-quadrants-critical-capabilities (HTTP 403)
- https://gpivendorresources.gartner.com/en/articles/6746287-voice-of-the-customer-methodology (not
  fetched directly; only reached through search-result summaries)
- https://www.darkreading.com/cybersecurity-analytics/cybersecurity-firms-chase-ai-vc-market-
  skyrockets (HTTP 403)
- https://www.darkreading.com/careers-and-people/layoffs-mount-cybersecurity-vendors-hunker-down
  (HTTP 403)
- https://rhisac.org/wp-content/uploads/CISO-Benchmark-2026_CLEAR.pdf (fetched but returned only PDF
  binary structure, no readable text)
- https://risky.biz/about/ (reached only through search-result snippets, not a direct page read)

## What disagrees with the recommendations above

The two pieces that traveled furthest in this research, the CISO Whisperer press release and the
CyberScoop investor op-ed, are also the two with the least evidence discipline. Neither cites a
method, a source, or a caveat, and both still reached a wide, named audience (one through paid
distribution on PR Newswire, one through a mainstream security-business outlet). That is a real
argument against the recommendation above: heavy sourcing, labelled caveats, and "what this does not
tell you" notes may cost the site some of the confident, quotable, shareable quality that gets a
market-standing claim repeated by other people. The owner's own goal, sales teams sharing this
nationally, may be in some tension with the evidence discipline his product core also asks for. The
resolution is probably to keep the evidence discipline in the detail and let the top-line verdict
read as plainly confident as CISO Whisperer's, without borrowing its lack of sourcing.

Momentum Cyber's infrequent, versioned cadence is a working counterexample to "pick a cadence you
can sustain and never miss it." It succeeds without a predictable schedule because the publisher
already commands attention independent of any single release. This site does not have that
condition yet, so the counterexample does not transfer today, but it suggests that once the site has
real standing, an occasional large release (an annual state-of-the-market edition, for instance)
could sit credibly alongside the steady weekly cadence rather than replacing it.

Return on Security, the peer closest to this site's audience and voice, carries no explicit
"not investment advice" disclaimer anywhere on its about page despite running weekly funding and M&A
coverage, and it appears to be the most trusted and most cited of the practitioner-facing peers
studied here. That is some evidence that an explicit disclaimer may matter less to real trust-
building than the recommendation above assumes. The project's own governance still requires the
disclaimer regardless of what peers do, since it is a constraint set by the owner and by
`intent.md`, not a design choice this research can override.
