/**
 * Tracked events — step 5 of the autonomy plan
 * (docs/active/autonomy-coverage-plan.md §4–5, D-76/D-77). Append-only,
 * trailing-12-month record of dated facts per supplier, each citing evidence
 * in evidence.ts with a real source URL. Only rungs 1–4 of the sourcing
 * ladder (docs/active/fable-run/research/11-distress-signal-sources.md §5)
 * publish here — a fact resting only on a single trade-press report (rung
 * 5) is excluded, per web/scripts/verify-tracker.ts.
 */

export type TrackerEventType =
  | 'funding'
  | 'acquisition'
  | 'layoff'
  | 'restructuring'
  | 'debt'
  | 'rating'
  | 'going-concern'
  | 'exec-change'
  | 'divestiture'
  | 'shutdown'
  | 'results'

export interface TrackerEvent {
  id: string
  supplierId: string
  date: string
  type: TrackerEventType
  text: string
  evidenceIds: string[]
  rung: 1 | 2 | 3 | 4 | 5
}

export const trackerEvents: TrackerEvent[] = [
  {
    "id": "EV-aqua-1",
    "supplierId": "aqua",
    "date": "2025-11-05",
    "type": "exec-change",
    "text": "Co-founder/CEO Dror Davidoff and co-founder/CTO Amir Jerbi stepped back to strategic advisors. Mike Dube became CEO; Nir Makowski became Chief Product & Technology Officer.",
    "evidenceIds": [
      "TR-aqua-2"
    ],
    "rung": 2
  },
  {
    "id": "EV-armis-1",
    "supplierId": "armis",
    "date": "2026-04-20",
    "type": "acquisition",
    "text": "ServiceNow closed its acquisition of Armis on April 20, 2026, and disclosed that Armis was expected to contribute approximately 125 basis points to ServiceNow's second-quarter and full-year 2026 subscription revenue growth, with integration-related headwinds of approximately 25 basis points to subscription gross margin, 75 basis points to operating margin, and 200 basis points to free cash flow margin.",
    "evidenceIds": [
      "TR-armis-1"
    ],
    "rung": 1
  },
  {
    "id": "EV-axonius-1",
    "supplierId": "axonius",
    "date": "2026-05-19",
    "type": "exec-change",
    "text": "Axonius named Joe Diamond permanent CEO; co-founder Dean Sysman moved to executive chairman.",
    "evidenceIds": [
      "TR-axonius-2"
    ],
    "rung": 1
  },
  {
    "id": "EV-cato-1",
    "supplierId": "cato",
    "date": "2026-02-24",
    "type": "results",
    "text": "ARR surpassed $350 million, +43% YoY, for full year 2025.",
    "evidenceIds": [
      "TR-cato-2"
    ],
    "rung": 2
  },
  {
    "id": "EV-checkpoint-1",
    "supplierId": "checkpoint-sase",
    "date": "2026-05-01",
    "type": "exec-change",
    "text": "Sherif Seddik appointed Chief Revenue Officer effective May 1, 2026, succeeding Itai Greenberg.",
    "evidenceIds": [
      "TR-checkpoint-3"
    ],
    "rung": 1
  },
  {
    "id": "EV-checkpoint-2",
    "supplierId": "checkpoint-sase",
    "date": "2026-07-30",
    "type": "debt",
    "text": "$2 billion in convertible senior notes issued during Q2 2026, ~$1.8 billion net proceeds.",
    "evidenceIds": [
      "TR-checkpoint-4"
    ],
    "rung": 1
  },
  {
    "id": "EV-checkpoint-3",
    "supplierId": "checkpoint-sase",
    "date": "2026-07-30",
    "type": "results",
    "text": "Q2 2026 revenue $674 million, +1% YoY; Security Subscriptions revenue $333 million, +12% YoY.",
    "evidenceIds": [
      "TR-checkpoint-1"
    ],
    "rung": 1
  },
  {
    "id": "EV-cloudflare-1",
    "supplierId": "cloudflare",
    "date": "2026-05-07",
    "type": "restructuring",
    "text": "Restructuring charge guided at $140.0-150.0 million ($105-110M cash, $35-40M non-cash), affecting approximately 1,100 employees, tied to shift to agentic AI-first operating model.",
    "evidenceIds": [
      "TR-cloudflare-3"
    ],
    "rung": 1
  },
  {
    "id": "EV-cloudflare-3",
    "supplierId": "cloudflare",
    "date": "2026-08-06",
    "type": "results",
    "text": "Q2 2026 revenue $696.1 million, +36% YoY.",
    "evidenceIds": [
      "TR-cloudflare-1"
    ],
    "rung": 1
  },
  {
    "id": "EV-cloudflare-2",
    "supplierId": "cloudflare",
    "date": "2026-08-13",
    "type": "debt",
    "text": "$2.5 billion aggregate principal of 0% Convertible Senior Notes due 2031 issued, ~$2,462.3 million net proceeds.",
    "evidenceIds": [
      "TR-cloudflare-4"
    ],
    "rung": 1
  },
  {
    "id": "EV-commvault-2",
    "supplierId": "commvault",
    "date": "2026-04-28",
    "type": "restructuring",
    "text": "Commvault disclosed two restructuring plans initiated during fiscal 2026 covering workforce reductions, technology transitions, and office lease closures, with total fiscal 2026 charges of $32.2 million, plus an additional $2.4 million recorded in the first quarter of fiscal 2027.",
    "evidenceIds": [
      "TR-commvault-2",
      "TR-commvault-1"
    ],
    "rung": 1
  },
  {
    "id": "EV-commvault-3",
    "supplierId": "commvault",
    "date": "2026-04-28",
    "type": "debt",
    "text": "Commvault disclosed that it issued $900 million in convertible notes during fiscal 2026, along with $99.6 million spent on related capped-call purchases.",
    "evidenceIds": [
      "TR-commvault-2"
    ],
    "rung": 1
  },
  {
    "id": "EV-commvault-1",
    "supplierId": "commvault",
    "date": "2026-07-28",
    "type": "results",
    "text": "Commvault reported Q1 FY2027 revenue of $314.1 million, up 11% year over year, and subscription ARR of $1,054 million, up 22% year over year, for the quarter ended June 30, 2026.",
    "evidenceIds": [
      "TR-commvault-1"
    ],
    "rung": 1
  },
  {
    "id": "EV-crwd-1",
    "supplierId": "crwd",
    "date": "2026-08-26",
    "type": "results",
    "text": "CrowdStrike reported Q2 FY2027 revenue of $1.47 billion, up 26% year over year, for the quarter ended 2026-07-31.",
    "evidenceIds": [
      "TR-crwd-1"
    ],
    "rung": 1
  },
  {
    "id": "EV-cyberark-1",
    "supplierId": "cyberark",
    "date": "2026-02-11",
    "type": "shutdown",
    "text": "CyberArk ceased to exist as an independent SEC filer and public entity, absorbed into Palo Alto Networks.",
    "evidenceIds": [
      "TR-cyberark-2"
    ],
    "rung": 1
  },
  {
    "id": "EV-cyera-3",
    "supplierId": "cyera",
    "date": "2026-04-23",
    "type": "acquisition",
    "text": "Cyera completed its acquisition of Ryft.",
    "evidenceIds": [
      "TR-cyera-3"
    ],
    "rung": 4
  },
  {
    "id": "EV-cyera-4",
    "supplierId": "cyera",
    "date": "2026-06-10",
    "type": "funding",
    "text": "Cyera raised $600 million led by Evolution Equity Partners at a $12 billion valuation.",
    "evidenceIds": [
      "TR-cyera-4"
    ],
    "rung": 4
  },
  {
    "id": "EV-cyera-2",
    "supplierId": "cyera",
    "date": "2026-09-03",
    "type": "acquisition",
    "text": "Cyera completed its acquisition of Oasis Security.",
    "evidenceIds": [
      "TR-cyera-2"
    ],
    "rung": 4
  },
  {
    "id": "EV-cyera-1",
    "supplierId": "cyera",
    "date": "2026-09-22",
    "type": "funding",
    "text": "Cyera announced a $400 million growth-equity investment from Goldman Sachs Alternatives at a valuation of over $12 billion.",
    "evidenceIds": [
      "TR-cyera-1"
    ],
    "rung": 4
  },
  {
    "id": "EV-delinea-1",
    "supplierId": "delinea",
    "date": "2026-09-23",
    "type": "exec-change",
    "text": "Timothy Regan appointed Chief Financial Officer of Delinea.",
    "evidenceIds": [
      "TR-delinea-3"
    ],
    "rung": 2
  },
  {
    "id": "EV-dragos-1",
    "supplierId": "dragos",
    "date": "2026-06-18",
    "type": "acquisition",
    "text": "Accenture disclosed an agreement to acquire a majority stake in Dragos, along with all of runZero and NetRise, in a filing accompanying its Q3 FY2026 earnings, dated June 18, 2026.",
    "evidenceIds": [
      "TR-dragos-1"
    ],
    "rung": 4
  },
  {
    "id": "EV-ghas-1",
    "supplierId": "github-advanced-security",
    "date": "2025-12-31",
    "type": "exec-change",
    "text": "GitHub CEO Thomas Dohmke, who announced in August 2025 that he would step down to become a founder again, completed his transition out of the role by the end of 2025, with no successor CEO named.",
    "evidenceIds": [
      "TR-ghas-1"
    ],
    "rung": 1
  },
  {
    "id": "EV-hiddenlayer-1",
    "supplierId": "hiddenlayer",
    "date": "2026-09-02",
    "type": "funding",
    "text": "HiddenLayer raised a $100 million Series B round led by Delta-v Capital, with participation from Ten Eleven Ventures, Morgan Stanley, M12, and Booz Allen Ventures, and reported signing more than 50 new platform customers.",
    "evidenceIds": [
      "TR-hiddenlayer-1"
    ],
    "rung": 4
  },
  {
    "id": "EV-jfrog-1",
    "supplierId": "jfrog",
    "date": "2026-08-06",
    "type": "results",
    "text": "JFrog reported Q2 2026 revenue of $163.8 million, up 29% year over year, including cloud revenue of $87.5 million, up 53% year over year and equal to 53% of total revenue.",
    "evidenceIds": [
      "TR-jfrog-1"
    ],
    "rung": 1
  },
  {
    "id": "EV-lakera-1",
    "supplierId": "lakera",
    "date": "2025-12-31",
    "type": "acquisition",
    "text": "Check Point Software Technologies completed its acquisition of Lakera AI during the fourth quarter of 2025, for approximately $190 million in net cash consideration.",
    "evidenceIds": [
      "TR-lakera-1"
    ],
    "rung": 1
  },
  {
    "id": "EV-mimecast-1",
    "supplierId": "mimecast",
    "date": "2026-06-25",
    "type": "exec-change",
    "text": "Ranjan Singh appointed CEO effective June 25, 2026, succeeding Marc van Zadelhoff.",
    "evidenceIds": [
      "TR-mimecast-2"
    ],
    "rung": 2
  },
  {
    "id": "EV-msft-defender-1",
    "supplierId": "msft-defender-o365",
    "date": "2026-07-29",
    "type": "results",
    "text": "FY2026 revenue $331.839 billion, +18% YoY.",
    "evidenceIds": [
      "TR-msft-defender-1"
    ],
    "rung": 1
  },
  {
    "id": "EV-msft-entra-1",
    "supplierId": "msft-entra",
    "date": "2026-07-29",
    "type": "results",
    "text": "FY2026 revenue $331.839 billion, +18% YoY.",
    "evidenceIds": [
      "TR-msft-entra-1"
    ],
    "rung": 1
  },
  {
    "id": "EV-netskope-2",
    "supplierId": "netskope",
    "date": "2026-06-03",
    "type": "exec-change",
    "text": "CFO Drew Del Matto disclosed intention to retire; remains CFO while successor is sought, then transitions to advisory.",
    "evidenceIds": [
      "TR-netskope-5"
    ],
    "rung": 1
  },
  {
    "id": "EV-netskope-1",
    "supplierId": "netskope",
    "date": "2026-09-02",
    "type": "restructuring",
    "text": "$3.5 million in restructuring costs recognized in Q2 FY2027 ended July 31, 2026.",
    "evidenceIds": [
      "TR-netskope-4"
    ],
    "rung": 1
  },
  {
    "id": "EV-netskope-3",
    "supplierId": "netskope",
    "date": "2026-09-02",
    "type": "results",
    "text": "Q2 FY2027 revenue $220.5 million, +29% YoY; ARR $899 million, +27% YoY.",
    "evidenceIds": [
      "TR-netskope-1"
    ],
    "rung": 1
  },
  {
    "id": "EV-okta-1",
    "supplierId": "okta",
    "date": "2026-08-24",
    "type": "results",
    "text": "Q4 FY2027 revenue $805 million, +11% YoY.",
    "evidenceIds": [
      "TR-okta-1"
    ],
    "rung": 1
  },
  {
    "id": "EV-optiv-2",
    "supplierId": "optiv",
    "date": "2026-05-08",
    "type": "debt",
    "text": "Optiv closed a lender agreement amending and extending its First Lien Credit Agreement to August 2028 and Second Lien to August 2029.",
    "evidenceIds": [
      "TR-optiv-3"
    ],
    "rung": 1
  },
  {
    "id": "EV-panw-1",
    "supplierId": "panw",
    "date": "2026-02-11",
    "type": "acquisition",
    "text": "Palo Alto Networks closed its acquisition of CyberArk Software Ltd. for approximately $25 billion in equity value.",
    "evidenceIds": [
      "TR-panw-3"
    ],
    "rung": 1
  },
  {
    "id": "EV-panw-2",
    "supplierId": "panw",
    "date": "2026-09-01",
    "type": "results",
    "text": "Palo Alto Networks reported Q4 FY2026 revenue of $3.41 billion, up 34% year over year, for the quarter ended 2026-07-31.",
    "evidenceIds": [
      "TR-panw-1"
    ],
    "rung": 1
  },
  {
    "id": "EV-qualys-1",
    "supplierId": "qualys",
    "date": "2026-08-04",
    "type": "results",
    "text": "Qualys reported Q2 2026 revenue of $182.2 million, up 11% year over year, for the quarter ended 2026-06-30.",
    "evidenceIds": [
      "TR-qualys-1"
    ],
    "rung": 1
  },
  {
    "id": "EV-rapid7-1",
    "supplierId": "rapid7",
    "date": "2026-06-01",
    "type": "exec-change",
    "text": "Rapid7 appointed Wael Mohamed as Chief Executive Officer. Corey Thomas, CEO for 13+ years, became executive chairman.",
    "evidenceIds": [
      "TR-rapid7-3"
    ],
    "rung": 1
  },
  {
    "id": "EV-rapid7-2",
    "supplierId": "rapid7",
    "date": "2026-08-07",
    "type": "restructuring",
    "text": "Rapid7 approved a workforce reduction of approximately 12% with estimated charges of $10 million to $11 million, primarily for severance and benefits.",
    "evidenceIds": [
      "TR-rapid7-4"
    ],
    "rung": 1
  },
  {
    "id": "EV-rapid7-3",
    "supplierId": "rapid7",
    "date": "2026-08-10",
    "type": "results",
    "text": "Rapid7 reported Q2 2026 revenue of $210.9 million, down 1.5% year over year, for the quarter ended 2026-06-30.",
    "evidenceIds": [
      "TR-rapid7-1"
    ],
    "rung": 1
  },
  {
    "id": "EV-rubrik-2",
    "supplierId": "rubrik",
    "date": "2026-02-06",
    "type": "exec-change",
    "text": "Rubrik announced that Brian McCarthy, President of Global Sales and Field Operations, resigned effective February 6, 2026, and promoted Jesse Green, previously President of Rubrik Americas, to Chief Revenue Officer.",
    "evidenceIds": [
      "TR-rubrik-3"
    ],
    "rung": 4
  },
  {
    "id": "EV-rubrik-1",
    "supplierId": "rubrik",
    "date": "2026-08-27",
    "type": "results",
    "text": "Rubrik reported Q2 FY2027 revenue of $427.3 million, up 38% year over year, and subscription ARR of $1.66 billion, up 33% year over year, for the quarter ended July 31, 2026.",
    "evidenceIds": [
      "TR-rubrik-1"
    ],
    "rung": 1
  },
  {
    "id": "EV-s1-1",
    "supplierId": "s1",
    "date": "2026-05-28",
    "type": "restructuring",
    "text": "SentinelOne disclosed an 8% workforce reduction and approximately $25 million in charges in an SEC filing dated 2026-05-28.",
    "evidenceIds": [
      "TR-s1-3"
    ],
    "rung": 1
  },
  {
    "id": "EV-s1-2",
    "supplierId": "s1",
    "date": "2026-08-27",
    "type": "results",
    "text": "SentinelOne reported Q2 FY2027 revenue of $292 million, up 21% year over year, for the quarter ended 2026-07-31.",
    "evidenceIds": [
      "TR-s1-1"
    ],
    "rung": 1
  },
  {
    "id": "EV-sailpoint-1",
    "supplierId": "sailpoint",
    "date": "2026-09-10",
    "type": "results",
    "text": "Q4 FY2027 revenue $308.8 million, +16.8% YoY; ARR $1,230.7 million, +25.3% YoY.",
    "evidenceIds": [
      "TR-sailpoint-1"
    ],
    "rung": 1
  },
  {
    "id": "EV-sonatype-1",
    "supplierId": "sonatype",
    "date": "2026-06-09",
    "type": "exec-change",
    "text": "Sonatype named three new C-suite executives: Casey Watson as Chief Revenue Officer, Jason McClelland as Chief Marketing Officer, and Sherri Manning as Chief Human Resources Officer.",
    "evidenceIds": [
      "TR-sonatype-2"
    ],
    "rung": 1
  },
  {
    "id": "EV-sophos-1",
    "supplierId": "sophos",
    "date": "2025-12-01",
    "type": "rating",
    "text": "S&P affirmed Sophos' B- credit rating and noted expected need to refinance 2027 maturities.",
    "evidenceIds": [
      "TR-sophos-2"
    ],
    "rung": 2
  },
  {
    "id": "EV-sophos-2",
    "supplierId": "sophos",
    "date": "2026-03-01",
    "type": "rating",
    "text": "Moody's downgraded Sophos to B3 from B2, with outlook revised to stable.",
    "evidenceIds": [
      "TR-sophos-3"
    ],
    "rung": 2
  },
  {
    "id": "EV-splunk-1",
    "supplierId": "splunk",
    "date": "2026-05-13",
    "type": "restructuring",
    "text": "Cisco disclosed a $1 billion restructuring charge in an 8-K filing, including charges related to Splunk integration.",
    "evidenceIds": [
      "TR-splunk-2"
    ],
    "rung": 1
  },
  {
    "id": "EV-surepath-1",
    "supplierId": "surepath",
    "date": "2026-06-15",
    "type": "acquisition",
    "text": "F5 completed its acquisition of SurePath AI for $50.1 million, recording $39.1 million of goodwill; F5 stated the transaction's impact on its operating results was immaterial.",
    "evidenceIds": [
      "TR-surepath-1"
    ],
    "rung": 1
  },
  {
    "id": "EV-tenable-2",
    "supplierId": "tenable",
    "date": "2026-07-29",
    "type": "results",
    "text": "Tenable reported Q2 2026 revenue of $268.5 million, up 8.6% year over year, for the quarter ended 2026-06-30.",
    "evidenceIds": [
      "TR-tenable-1"
    ],
    "rung": 1
  },
  {
    "id": "EV-tenable-1",
    "supplierId": "tenable",
    "date": "2026-09-15",
    "type": "debt",
    "text": "Tenable completed the issuance of $800 million of 0.25% convertible senior notes due 2031.",
    "evidenceIds": [
      "TR-tenable-2"
    ],
    "rung": 1
  },
  {
    "id": "EV-trend-1",
    "supplierId": "trend-micro",
    "date": "2026-08-13",
    "type": "restructuring",
    "text": "Trend Micro cut FY2026 operating-income guidance from ¥56.4 billion to ¥44.4 billion, citing rising artificial-intelligence and cloud-computing costs.",
    "evidenceIds": [
      "TR-trend-1"
    ],
    "rung": 1
  },
  {
    "id": "EV-varonis-2",
    "supplierId": "varonis",
    "date": "2025-10-29",
    "type": "layoff",
    "text": "Varonis announced a 5% headcount reduction, approximately 120 employees, disclosed with its Q3 2025 results; CEO Yakov Faitelson described it as reallocating resources toward the highest return on investment.",
    "evidenceIds": [
      "TR-varonis-2"
    ],
    "rung": 4
  },
  {
    "id": "EV-varonis-3",
    "supplierId": "varonis",
    "date": "2025-10-29",
    "type": "divestiture",
    "text": "Varonis disclosed plans to end-of-life its self-hosted, on-premises product effective December 31, 2026, as part of its Q3 2025 results commentary.",
    "evidenceIds": [
      "TR-varonis-2"
    ],
    "rung": 4
  },
  {
    "id": "EV-varonis-1",
    "supplierId": "varonis",
    "date": "2026-07-28",
    "type": "results",
    "text": "Varonis reported Q2 2026 revenue of $180.0 million, up 18.3% year over year, and total SaaS ARR of $726.0 million, up 52% year over year, for the quarter ended June 30, 2026.",
    "evidenceIds": [
      "TR-varonis-1"
    ],
    "rung": 1
  },
  {
    "id": "EV-veeam-1",
    "supplierId": "veeam",
    "date": "2025-12-11",
    "type": "acquisition",
    "text": "Veeam completed its acquisition of Securiti AI, a data security posture management and AI-governance company, for $1.725 billion; Securiti founder and CEO Rehan Jalil joined Veeam as President of Security and AI.",
    "evidenceIds": [
      "TR-veeam-2"
    ],
    "rung": 4
  },
  {
    "id": "EV-witnessai-1",
    "supplierId": "witnessai",
    "date": "2026-01-13",
    "type": "funding",
    "text": "WitnessAI raised a $58 million strategic funding round led by Sound Ventures, with participation from Fin Capital, Samsung Ventures, Qualcomm Ventures, Forgepoint Capital Partners, Silver Buckshot Ventures, and existing investors Google Ventures and Ballistic Ventures.",
    "evidenceIds": [
      "TR-witnessai-1"
    ],
    "rung": 4
  },
  {
    "id": "EV-wiz-1",
    "supplierId": "wiz",
    "date": "2026-03-11",
    "type": "acquisition",
    "text": "Acquisition closed by Google/Alphabet at $29.5 billion after purchase price adjustments.",
    "evidenceIds": [
      "TR-wiz-1"
    ],
    "rung": 1
  },
  {
    "id": "EV-zenity-1",
    "supplierId": "zenity",
    "date": "2026-08-03",
    "type": "funding",
    "text": "Zenity raised a $125 million Series C round led by Norwest, with participation from Qumra Capital, SoftBank Vision Fund 2, Hitachi Ventures, LG Technology Ventures, Vertex Ventures, Third Point Ventures, DTCP, and Intel Capital.",
    "evidenceIds": [
      "TR-zenity-1"
    ],
    "rung": 4
  },
  {
    "id": "EV-zscaler-1",
    "supplierId": "zscaler",
    "date": "2026-09-03",
    "type": "restructuring",
    "text": "Restructuring and other charges of $5.5 million in Q4 FY2026 and $10.3 million for full FY2026, described as severance and termination benefits.",
    "evidenceIds": [
      "TR-zscaler-3"
    ],
    "rung": 1
  },
  {
    "id": "EV-zscaler-3",
    "supplierId": "zscaler",
    "date": "2026-09-03",
    "type": "results",
    "text": "Q4 FY2026 revenue $898.2 million, +25% YoY; ARR $3,771 million, +25% YoY.",
    "evidenceIds": [
      "TR-zscaler-1"
    ],
    "rung": 1
  },
  {
    "id": "EV-zscaler-2",
    "supplierId": "zscaler",
    "date": "2026-09-24",
    "type": "exec-change",
    "text": "CRO Mike Rich stepped down effective October 1, 2026, succeeded by Ross Tackett. EVP Raj Judge resigned board seat effective April 16, 2026.",
    "evidenceIds": [
      "TR-zscaler-4"
    ],
    "rung": 1
  }
]
