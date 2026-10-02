import type { EvidenceRecord } from './types'
import generatedFilingEvidence from './generated/filingEvidence.json' with { type: 'json' }

const handWrittenEvidenceRecords: EvidenceRecord[] = [
  {
    id: 'A1a',
    title: 'NVIDIA Q1 FY24 Financial Results',
    organization: 'NVIDIA',
    publicationDate: '2023-05-24',
    economicPeriod: 'Quarter ended 2023-04-30',
    canonicalUrl:
      'https://investor.nvidia.com/news/press-release-details/2023/NVIDIA-Announces-Financial-Results-for-First-Quarter-Fiscal-2024/',
    excerpt:
      'The computer industry is going through two simultaneous transitions — accelerated computing and generative AI… We are significantly increasing our supply to meet surging demand. Quarterly Data Center revenue: $4.28 billion.',
    sourceClass: 'IR',
    interpretation: 'Earliest compute-supply impulse in the observed sequence.',
    limitations: 'Data Center includes non-GenAI workloads.',
    conflictingEvidenceIds: [],
    artifactLabel: 'SEC-MARKET-SIG-SRC-002 / A1a',
    tags: ['infrastructure', 'supplier', 'compute'],
  },
  {
    id: 'A1b',
    title: 'NVIDIA Q1 FY27 Financial Results',
    organization: 'NVIDIA',
    publicationDate: '2026-05-20',
    economicPeriod: 'Quarter ended 2026-04-26',
    canonicalUrl:
      'https://www.sec.gov/Archives/edgar/data/1045810/000104581026000052/nvda-20260426.htm',
    excerpt:
      'Data Center revenue was $75.25 billion, up 92% from a year ago and up 21% sequentially.',
    sourceClass: 'FILING',
    interpretation: 'Compute demand remains elevated in absolute dollars; infrastructure cycle still accelerating.',
    limitations:
      'China restrictions and product transitions affect quarter-to-quarter comparability. Data Center is not a deployed-workload measure.',
    conflictingEvidenceIds: ['D1', 'LAG-NO-CALL'],
    artifactLabel: 'SEC-MARKET-SIG-SRC-002 / A1b',
    tags: ['infrastructure', 'supplier', 'compute'],
  },
  {
    id: 'A2',
    title: 'Cisco Q4 and FY2026 Earnings',
    organization: 'Cisco',
    publicationDate: '2026-08-12',
    economicPeriod: 'Quarter ended 2026-07-25',
    canonicalUrl:
      'https://investor.cisco.com/news/news-details/2026/CISCO-REPORTS-FOURTH-QUARTER-AND-FISCAL-YEAR-2026-EARNINGS/default.aspx',
    excerpt:
      '$4 billion of Q4 AI-infrastructure orders from hyperscalers, bringing the cumulative FY 2026 AI-infrastructure order total to $9.3 billion. Delivered approximately $4 billion of AI-infrastructure revenue from hyperscalers in FY 2026; $7.5 billion expected in FY 2027. Q4 Networking revenue $9.791 billion, +28 percent; Q4 networking product orders +40 percent.',
    sourceClass: 'IR',
    interpretation: 'Networking joined the AI cycle after the initial compute impulse.',
    limitations: 'Orders are concentrated and are not revenue; Splunk distorts total-company comparability.',
    conflictingEvidenceIds: ['C6a', 'C6b'],
    artifactLabel: 'SEC-MARKET-SIG-SRC-002 / A2',
    tags: ['infrastructure', 'supplier', 'networking'],
  },
  {
    id: 'A3',
    title: 'Arista Networks Financial Results',
    organization: 'Arista Networks',
    publicationDate: '2026-08-04',
    economicPeriod: 'Quarter ended 2026-06-30',
    canonicalUrl:
      'https://investors.arista.com/Communications/Press-Releases-and-Events/Press-Release-Detail/2026/Arista-Networks-Inc--Reports-Second-Quarter-2026-Financial-Results/default.aspx',
    excerpt:
      'Revenue rose from $1.351 billion (period ended 2023-03-31) to $3.036 billion; latest YoY growth 37.7 percent.',
    sourceClass: 'IR',
    interpretation: 'Cloud and AI networking broadened the supplier cycle.',
    limitations: 'Total revenue is not an AI-only series.',
    conflictingEvidenceIds: [],
    sourceAttributions: [
      {
        organization: 'Arista Networks',
        publicationDate: '2026-08-04',
        economicPeriod: 'Quarter ended 2026-06-30',
        canonicalUrl:
          'https://investors.arista.com/Communications/Press-Releases-and-Events/Press-Release-Detail/2026/Arista-Networks-Inc--Reports-Second-Quarter-2026-Financial-Results/default.aspx',
      },
      {
        organization: 'Arista Networks',
        publicationDate: '2023-05-01',
        economicPeriod: 'Quarter ended 2023-03-31',
        canonicalUrl: 'https://www.arista.com/en/company/news/press-release/17252-pr-20230501',
      },
    ],
    artifactLabel: 'SEC-MARKET-SIG-SRC-002 / A3',
    tags: ['infrastructure', 'supplier', 'networking'],
  },
  {
    id: 'A4',
    title: 'Dell Q1 FY27 Financial Results',
    organization: 'Dell Technologies',
    publicationDate: '2026-05-28',
    economicPeriod: 'Quarter ended 2026-05-01',
    canonicalUrl:
      'https://investors.delltechnologies.com/static-files/b63ffff9-b729-403b-a231-c6af05667759',
    excerpt:
      'We booked $24.4 billion in AI orders and recognized $16.1 billion of AI server revenue. We\'re increasing our AI server revenue expectations for FY27 to $60 billion. AI-server backlog $51.3 billion.',
    sourceClass: 'IR',
    interpretation: 'Demand is still converting into capacity; orders materially exceed recognized revenue.',
    limitations: 'Memory cost and supply affect dollars and timing. Company-defined AI-server metric.',
    conflictingEvidenceIds: [],
    artifactLabel: 'SEC-MARKET-SIG-SRC-002 / A4',
    tags: ['infrastructure', 'supplier', 'servers'],
  },
  {
    id: 'A5',
    title: 'Vertiv Q4 2025 and Q2 2026 Results',
    organization: 'Vertiv',
    publicationDate: '2026-07-29',
    economicPeriod: 'Quarter ended 2026-06-30',
    canonicalUrl:
      'https://www.sec.gov/Archives/edgar/data/1674101/000162828026050323/q22026exhibit991vrt07292026.htm',
    excerpt:
      'Organic orders up approximately 252%; book-to-bill ratio was ~2.9x and backlog increased to $15.0 billion. Q2 2026 sales growth 24 percent: 18 percent organic, 5 percent acquisitions, 1 percent FX.',
    sourceClass: 'FILING',
    interpretation: 'Physical support infrastructure inflected after compute and server demand.',
    limitations: 'Quarterly order disclosure later changed; backlog is not deployed capacity.',
    conflictingEvidenceIds: [],
    sourceAttributions: [
      {
        organization: 'Vertiv',
        publicationDate: '2026-07-29',
        economicPeriod: 'Quarter ended 2026-06-30',
        canonicalUrl:
          'https://www.sec.gov/Archives/edgar/data/1674101/000162828026050323/q22026exhibit991vrt07292026.htm',
      },
      {
        organization: 'Vertiv',
        publicationDate: '2026-02-11',
        economicPeriod: 'Quarter ended 2025-12-31',
        canonicalUrl:
          'https://www.sec.gov/Archives/edgar/data/1674101/000167410126000006/exhibit991vrt02112026.htm',
      },
    ],
    artifactLabel: 'SEC-MARKET-SIG-SRC-002 / A5',
    tags: ['infrastructure', 'supplier', 'power-thermal'],
  },
  {
    id: 'A6',
    title: 'Broadcom Q1–Q2 FY26 Financial Results',
    organization: 'Broadcom',
    publicationDate: '2026-06-03',
    economicPeriod: 'Quarter ended 2026-05-03',
    canonicalUrl:
      'https://www.broadcom.com/company/news/financial-releases/64371',
    excerpt:
      'Q1 AI revenue of $8.4 billion grew 106% year-over-year; Q2 semiconductor revenue from AI of $10.8 billion grew 143% year-over-year.',
    sourceClass: 'IR',
    interpretation: 'Custom AI silicon accelerated alongside merchant compute.',
    limitations: 'Short company-defined AI revenue series.',
    conflictingEvidenceIds: [],
    artifactLabel: 'SEC-MARKET-SIG-SRC-002 / A6',
    tags: ['infrastructure', 'supplier', 'semiconductor'],
  },
  {
    id: 'B1',
    title: 'Microsoft FY2026 Q4 Earnings',
    organization: 'Microsoft',
    publicationDate: '2026-07-29',
    economicPeriod: 'Quarter ended 2026-06-30',
    canonicalUrl:
      'https://www.microsoft.com/en-us/Investor/earnings/FY-2026-Q4/press-release-webcast',
    excerpt:
      'Cash-flow table: Additions to property and equipment $(35,802) million for the quarter; $(115,948) million for FY2026. Customer demand continues to exceed available capacity.',
    sourceClass: 'IR',
    interpretation: 'Hyperscaler capex breadth and continuing capacity constraint.',
    limitations:
      'Finance-to-operating-lease reclassification changes reported capex without equivalent reduction in build intent.',
    conflictingEvidenceIds: [],
    sourceAttributions: [
      {
        organization: 'Microsoft',
        publicationDate: '2026-07-29',
        economicPeriod: 'Quarter ended 2026-06-30',
        canonicalUrl:
          'https://www.microsoft.com/en-us/Investor/earnings/FY-2026-Q4/press-release-webcast',
      },
      {
        organization: 'Microsoft',
        publicationDate: '2026-07-29',
        economicPeriod: 'FY2026 Q4 earnings call',
        canonicalUrl: 'https://aka.ms/transcriptfy26q4',
      },
    ],
    artifactLabel: 'SEC-MARKET-SIG-SRC-002 / B1',
    tags: ['hyperscaler', 'capex'],
  },
  {
    id: 'B2',
    title: 'Amazon Q2 2026 Results',
    organization: 'Amazon',
    publicationDate: '2026-07-30',
    economicPeriod: 'Quarter ended 2026-06-30',
    canonicalUrl:
      'https://ir.aboutamazon.com/news-release/news-release-details/2026/Amazon-com-Announces-Second-Quarter-Results/',
    excerpt:
      'Free cash flow decreased… driven primarily by a year-over-year increase of $66.1 billion in purchases of property and equipment… primarily reflects investments in artificial intelligence. Q2 purchases of property and equipment $54.208 billion.',
    sourceClass: 'IR',
    interpretation: 'Hyperscaler investment remains elevated; capacity insufficient through 2027.',
    limitations: 'Company capex includes non-AWS uses; guide increase includes memory inflation.',
    conflictingEvidenceIds: [],
    artifactLabel: 'SEC-MARKET-SIG-SRC-002 / B2',
    tags: ['hyperscaler', 'capex'],
  },
  {
    id: 'B3',
    title: 'Alphabet Q2 2026 Results',
    organization: 'Alphabet',
    publicationDate: '2026-07-22',
    economicPeriod: 'Quarter ended 2026-06-30',
    canonicalUrl:
      'https://www.sec.gov/Archives/edgar/data/1652044/000165204426000066/googexhibit991q22026.htm',
    excerpt:
      'Purchases of property and equipment $44.924 billion for Q2 2026 and $80.598 billion for H1 2026. The increase in the range is primarily due to an acceleration in the delivery of capacity to meet growing demand.',
    sourceClass: 'FILING',
    interpretation: 'Broad hyperscaler capacity acceleration.',
    limitations: 'Capex is not an AI-only metric; 2023 quarterly figures are reconstructed.',
    conflictingEvidenceIds: [],
    sourceAttributions: [
      {
        organization: 'Alphabet',
        publicationDate: '2026-07-22',
        economicPeriod: 'Quarter ended 2026-06-30',
        canonicalUrl:
          'https://www.sec.gov/Archives/edgar/data/1652044/000165204426000066/googexhibit991q22026.htm',
      },
      {
        organization: 'Alphabet',
        publicationDate: '2026-07-22',
        economicPeriod: 'Q2 2026 earnings call',
        canonicalUrl:
          'https://s206.q4cdn.com/479360582/files/doc_events/2026/Jul/22/2026_Q2_Earnings_Transcript.pdf',
      },
    ],
    artifactLabel: 'SEC-MARKET-SIG-SRC-002 / B3',
    tags: ['hyperscaler', 'capex'],
  },
  {
    id: 'B4',
    title: 'Meta Q2 2026 Results',
    organization: 'Meta',
    publicationDate: '2026-07-29',
    economicPeriod: 'Quarter ended 2026-06-30',
    canonicalUrl:
      'https://investor.atmeta.com/investor-news/press-release-details/2026/Meta-Reports-Second-Quarter-2026-Results/default.aspx',
    excerpt:
      'Capital expenditures, including principal payments on finance leases, were $31.08 billion for the quarter.',
    sourceClass: 'IR',
    interpretation: 'First-party AI infrastructure remains elevated.',
    limitations: 'Internal ads and AI infrastructure is a weak enterprise-cloud demand proxy.',
    conflictingEvidenceIds: [],
    artifactLabel: 'SEC-MARKET-SIG-SRC-002 / B4',
    tags: ['hyperscaler', 'capex'],
  },
  {
    id: 'B5',
    title: 'Oracle FY2026 Results',
    organization: 'Oracle',
    publicationDate: '2026-06-10',
    economicPeriod: 'Fiscal year ended 2026-05-31',
    canonicalUrl:
      'https://investor.oracle.com/investor-news/news-details/2026/Oracle-Announces-Record-Q4-and-FY-2026-Results-Driven-by-Cloud-Infrastructure--Cloud-Applications/',
    excerpt:
      'RPO… $638 billion, up 363%; prepaid and customer supplied hardware portions of our large AI contracts now total $75 billion. FY2026 capital expenditures $55.663 billion.',
    sourceClass: 'IR',
    interpretation: 'Large contracted-capacity demand with strong concentration caveat.',
    limitations: 'RPO concentration and customer-supplied hardware; poor diversified-enterprise-demand proxy.',
    conflictingEvidenceIds: [],
    artifactLabel: 'SEC-MARKET-SIG-SRC-002 / B5',
    tags: ['hyperscaler', 'capex', 'contracted-capacity'],
  },
  {
    id: 'C1',
    title: 'CrowdStrike Q1 FY27 Results',
    organization: 'CrowdStrike',
    publicationDate: '2026-06-03',
    economicPeriod: 'Quarter ended 2026-04-30',
    canonicalUrl:
      'https://www.sec.gov/Archives/edgar/data/1535527/000153552726000022/crwd-20260603xex991.htm',
    excerpt:
      'Revenue $1.39 billion; ending ARR $5.51 billion, +24 percent; net-new ARR $255.8 million.',
    sourceClass: 'FILING',
    interpretation: 'Selected platform-vendor re-acceleration after slower period.',
    limitations: 'Recovery from 2024 outage and platform share capture; not sufficient for category breadth.',
    conflictingEvidenceIds: ['C6a', 'C6b', 'D1'],
    artifactLabel: 'SEC-MARKET-SIG-SRC-002 / C1',
    tags: ['security-vendor', 'secops', 'platform'],
  },
  {
    id: 'C2',
    title: 'Palo Alto Networks Q3 FY26 Results',
    organization: 'Palo Alto Networks',
    publicationDate: '2026-06-02',
    economicPeriod: 'Quarter ended 2026-04-30',
    canonicalUrl:
      'https://www.sec.gov/Archives/edgar/data/1327567/000132756726000012/ex991q326earningsrelease.htm',
    excerpt:
      'Total revenue… grew 31%… This includes $388 million from CyberArk and Chronosphere. Approximately 14 percent revenue, 28 percent NGS ARR, and 22 percent RPO growth excluding those acquisitions.',
    sourceClass: 'FILING',
    interpretation: 'Positive organic demand with acquisition-heavy headline growth.',
    limitations: 'Platformization and M&A deliberately alter period comparability.',
    conflictingEvidenceIds: ['C6a', 'C6b', 'D1'],
    sourceAttributions: [
      {
        organization: 'Palo Alto Networks',
        publicationDate: '2026-06-02',
        economicPeriod: 'Quarter ended 2026-04-30',
        canonicalUrl:
          'https://www.sec.gov/Archives/edgar/data/1327567/000132756726000012/ex991q326earningsrelease.htm',
      },
      {
        organization: 'Palo Alto Networks',
        publicationDate: '2026-06-02',
        economicPeriod: 'Q3 FY2026 earnings call investor deck',
        canonicalUrl:
          'https://investors.paloaltonetworks.com/static-files/67ce9226-4fe0-43cd-b83e-42efb035f38c',
      },
    ],
    artifactLabel: 'SEC-MARKET-SIG-SRC-002 / C2',
    tags: ['security-vendor', 'platform', 'm-and-a'],
  },
  {
    id: 'C3',
    title: 'Fortinet Q2 2026 Results',
    organization: 'Fortinet',
    publicationDate: '2026-07-29',
    economicPeriod: 'Quarter ended 2026-06-30',
    canonicalUrl:
      'https://investor.fortinet.com/news-releases/news-release-details/fortinet-reports-strong-second-quarter-2026-financial-results',
    excerpt: 'Revenue grew 26%… Product revenue grew 52%… Billings grew 33%.',
    sourceClass: 'IR',
    interpretation: 'Current network/firewall demand is real; strongest realized network-security acceleration in the panel.',
    limitations: 'Refresh, pricing, and share shift may explain part of the result independently of AI infrastructure.',
    conflictingEvidenceIds: ['C6a', 'C6b', 'D1', 'LAG-NO-CALL'],
    artifactLabel: 'SEC-MARKET-SIG-SRC-002 / C3',
    tags: ['security-vendor', 'network', 'firewall'],
  },
  {
    id: 'C4',
    title: 'Zscaler Q3 FY26 Results',
    organization: 'Zscaler',
    publicationDate: '2026-05-26',
    economicPeriod: 'Quarter ended 2026-04-30',
    canonicalUrl:
      'https://www.sec.gov/Archives/edgar/data/1713683/000171368326000095/zs-04302026_991.htm',
    excerpt: 'ARR grew 25%, or 21%, excluding the contribution from the Red Canary acquisition.',
    sourceClass: 'FILING',
    interpretation: 'Sustained SASE demand, not a clean new inflection.',
    limitations: 'Red Canary affects headline ARR; subscription timing differs from product vendors.',
    conflictingEvidenceIds: ['C6a', 'C6b'],
    artifactLabel: 'SEC-MARKET-SIG-SRC-002 / C4',
    tags: ['security-vendor', 'sase'],
  },
  {
    id: 'C5',
    title: 'Cloudflare Q2 2026 Results',
    organization: 'Cloudflare',
    publicationDate: '2026-08-06',
    economicPeriod: 'Quarter ended 2026-06-30',
    canonicalUrl:
      'https://www.cloudflare.com/en-gb/press/press-releases/2026/cloudflare-announces-second-quarter-2026-financial-results/',
    excerpt:
      'Second quarter revenue totaled $696.1 million, representing an increase of 36% year-over-year… Delivered Current RPO year-over-year growth of 35%.',
    sourceClass: 'IR',
    interpretation: 'Edge, connectivity, and SASE-related platform momentum improved.',
    limitations:
      'Consolidated revenue includes developer and compute activity and is not security-pure; cannot carry a security-category or lag claim.',
    conflictingEvidenceIds: [],
    artifactLabel: 'SEC-MARKET-SIG-SRC-002 / C5',
    tags: ['security-vendor', 'sase', 'edge'],
  },
  {
    id: 'C6a',
    title: 'Check Point Q2 2026 Results',
    organization: 'Check Point',
    publicationDate: '2026-07-30',
    economicPeriod: 'Quarter ended 2026-06-30',
    canonicalUrl:
      'https://www.checkpoint.com/downloads/investor/check-point-software-second-quarter-2026-financial-results.pdf',
    excerpt:
      'Check Point revenue grew approximately 1 percent while security subscriptions grew 12 percent and product/license revenue declined.',
    sourceClass: 'IR',
    interpretation: 'Near-flat total revenue. Blocks a uniform network-security acceleration call.',
    limitations: 'One vendor. Subscription growth is not product-cycle proof.',
    conflictingEvidenceIds: ['C1', 'C2', 'C3', 'C4', 'A2'],
    artifactLabel: 'SEC-MARKET-SIG-SRC-002 / C6',
    tags: ['security-vendor', 'counter-evidence'],
  },
  {
    id: 'C6b',
    title: 'Cisco Security Q4 and FY2026 Results',
    organization: 'Cisco',
    publicationDate: '2026-08-12',
    economicPeriod: 'FY2026 and quarter ended 2026-07-25',
    canonicalUrl:
      'https://investor.cisco.com/news/news-details/2026/CISCO-REPORTS-FOURTH-QUARTER-AND-FISCAL-YEAR-2026-EARNINGS/default.aspx',
    excerpt:
      'Cisco Security revenue $2.226 billion, +14 percent for Q4; $8.232 billion, +2 percent for FY2026.',
    sourceClass: 'IR',
    interpretation: 'Quarterly momentum improved; full-year security breadth remained weak.',
    limitations: 'Splunk is embedded in Cisco security segment; not an organic Cisco-security measure. FY +2% is an annual print, not a quarterly series.',
    conflictingEvidenceIds: ['C1', 'C2', 'C3', 'C4', 'A2'],
    artifactLabel: 'SEC-MARKET-SIG-SRC-002 / C6',
    tags: ['security-vendor', 'counter-evidence'],
  },
  {
    id: 'C7',
    title: 'Okta Q1 FY27 Results',
    organization: 'Okta',
    publicationDate: '2026-05-28',
    economicPeriod: 'Quarter ended 2026-04-30',
    canonicalUrl:
      'https://www.sec.gov/Archives/edgar/data/1660134/000166013426000050/okta-4302026_ex991.htm',
    excerpt:
      'Revenue $765 million, +11 percent; cRPO $2.499 billion, +12 percent; DBNRR 107 percent.',
    sourceClass: 'FILING',
    interpretation: 'Identity demand positive but not broadly accelerating.',
    limitations: 'cRPO is sensitive to contract duration and sales timing.',
    conflictingEvidenceIds: ['D5b'],
    sourceAttributions: [
      {
        organization: 'Okta',
        publicationDate: '2026-05-28',
        economicPeriod: 'Quarter ended 2026-04-30',
        canonicalUrl:
          'https://www.sec.gov/Archives/edgar/data/1660134/000166013426000050/okta-4302026_ex991.htm',
      },
      {
        organization: 'Okta',
        publicationDate: '2026-05-28',
        economicPeriod: 'Q1 FY2027 posted commentary',
        canonicalUrl:
          'https://s205.q4cdn.com/566291348/files/doc_financials/2027/q1/Q1FY27PostedCommentary.pdf',
      },
    ],
    artifactLabel: 'SEC-MARKET-SIG-SRC-002 / C7',
    tags: ['security-vendor', 'identity'],
  },
  {
    id: 'C8a',
    title: 'Rubrik Q1 FY27 Results',
    organization: 'Rubrik',
    publicationDate: '2026-06-04',
    economicPeriod: 'Quarter ended 2026-04-30',
    canonicalUrl:
      'https://ir.rubrik.com/news-events/press-releases/news-details/2026/Rubrik-Reports-First-Quarter-Fiscal-Year-2027-Financial-Results/default.aspx',
    excerpt: 'Subscription ARR was up 32% year-over-year, growing to $1.57 billion.',
    sourceClass: 'IR',
    interpretation: 'Selected data-security acceleration.',
    limitations: 'Short public history and material-rights accounting.',
    conflictingEvidenceIds: [],
    artifactLabel: 'SEC-MARKET-SIG-SRC-002 / C8a',
    tags: ['security-vendor', 'data-security'],
  },
  {
    id: 'C8b',
    title: 'Varonis Q2 2026 Results',
    organization: 'Varonis',
    publicationDate: '2026-07-28',
    economicPeriod: 'Quarter ended 2026-06-30',
    canonicalUrl:
      'https://www.sec.gov/Archives/edgar/data/1361113/000117184326004948/exh_991.htm',
    excerpt: 'SaaS ARR excluding conversions growth of 25%.',
    sourceClass: 'FILING',
    interpretation: 'Selected data/AI-security demand.',
    limitations: 'Headline 52 percent SaaS ARR includes conversions.',
    conflictingEvidenceIds: [],
    artifactLabel: 'SEC-MARKET-SIG-SRC-002 / C8b',
    tags: ['security-vendor', 'data-security'],
  },
  {
    id: 'D1',
    title: 'IANS Security Budget Benchmark (2023–2025)',
    organization: 'IANS Research',
    publicationDate: '2025-08-05',
    economicPeriod: 'Calendar years 2023–2025',
    canonicalUrl:
      'https://sf-cdn.iansresearch.com/sitefinity/docs/default-source/reports/2025-security-budget-benchmark-summary-report_08_05_2025.pdf?sfvrsn=43097214_2',
    excerpt:
      'Average security budget increase of 6% (2023), risen from 6% in 2023 to 8% (2024), average annual security budget growth plunged to 4% (2025). Security share of IT: 11.6% (2023), 11.9% (2024 restated), 10.9% (2025).',
    sourceClass: 'INDEPENDENT',
    interpretation:
      'No simultaneous broad security-budget acceleration; security lost share of IT as AI and cloud IT spending rebounded.',
    limitations:
      'Self-reported survey; 2024 contemporaneous report said 13.2%; 2025 restated methodology. AI/cloud attribution is IANS interpretation.',
    conflictingEvidenceIds: ['C1', 'C2', 'C3', 'D2', 'A1b'],
    artifactLabel: 'SEC-MARKET-SIG-SRC-002 / D1',
    tags: ['buyer', 'budget'],
  },
  {
    id: 'D2',
    title: 'ETR Enterprise Security Priorities 2026',
    organization: 'Enterprise Technology Research',
    publicationDate: '2026-04-29',
    economicPeriod: '2026 planned spending',
    canonicalUrl:
      'https://research.etr.ai/etr-data-drop/what-are-enterprise-security-priorities-in-2026',
    excerpt:
      'Fifty-nine percent… plan to increase spending on LLM/GenAI protection… up from 50% in 2025. Already spending on AI security tools reached 32% in 2026, up from 23% in 2025.',
    sourceClass: 'INDEPENDENT',
    interpretation: 'Category intent strengthened later in the sequence; not broad realized spend.',
    limitations: 'Intent and self-reported tool use are not realized market spend.',
    conflictingEvidenceIds: ['D1', 'LAG-NO-CALL'],
    artifactLabel: 'SEC-MARKET-SIG-SRC-002 / D2',
    tags: ['buyer', 'intent', 'ai-security'],
  },
  {
    id: 'D3',
    title: 'McKinsey State of AI 2025',
    organization: 'McKinsey & Company',
    publicationDate: '2025-11',
    economicPeriod: 'Calendar year 2025',
    canonicalUrl:
      'https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai',
    excerpt:
      '88 percent report regular AI use in at least one business function… the majority are still in the experimenting or piloting stages.',
    sourceClass: 'INDEPENDENT',
    interpretation: 'Workload activation can trail capex and broad AI use.',
    limitations: 'Self-reported definitions of use and scale differ across surveys.',
    conflictingEvidenceIds: [],
    artifactLabel: 'SEC-MARKET-SIG-SRC-002 / D3',
    tags: ['buyer', 'deployment', 'ai'],
  },
  {
    id: 'D4',
    title: 'ISC2 Cybersecurity Workforce Study 2024',
    organization: '(ISC)²',
    publicationDate: '2024-09-11',
    economicPeriod: 'Calendar year 2024',
    canonicalUrl:
      'https://www.prnewswire.com/news-releases/growth-of-cybersecurity-workforce-slows-in-2024-as-economic-uncertainty-persists-302244585.html',
    excerpt:
      'The workforce was holding at an estimated 5.5 million people (a 0.1% year-on-year increase).',
    sourceClass: 'INDEPENDENT',
    interpretation: 'Security headcount did not accelerate with 2024 infrastructure investment.',
    limitations: 'Workforce estimates do not measure software or services bookings.',
    conflictingEvidenceIds: [],
    artifactLabel: 'SEC-MARKET-SIG-SRC-002 / D4',
    tags: ['buyer', 'hiring'],
  },
  {
    id: 'D5a',
    title: 'Alphabet / Wiz Acquisition 8-K',
    organization: 'Alphabet',
    publicationDate: '2025-03-18',
    economicPeriod: 'Transaction announcement',
    canonicalUrl:
      'https://www.sec.gov/Archives/edgar/data/1652044/000165204425000027/goog-20250318.htm',
    excerpt: 'Approximately $32 billion all-cash transaction for Wiz.',
    sourceClass: 'FILING',
    interpretation: 'Strategic capital moved into cloud security.',
    limitations: 'Platform share strategy is an alternative to category expansion; not proof of customer spend.',
    conflictingEvidenceIds: [],
    artifactLabel: 'SEC-MARKET-SIG-SRC-002 / D5a',
    tags: ['investment', 'cloud-security', 'm-and-a'],
  },
  {
    id: 'D5b',
    title: 'Palo Alto / CyberArk Acquisition 8-K',
    organization: 'Palo Alto Networks',
    publicationDate: '2025-07-30',
    economicPeriod: 'Transaction announcement',
    canonicalUrl:
      'https://www.sec.gov/Archives/edgar/data/1327567/000119312525168821/d67702dex992.htm',
    excerpt: 'Approximately $25 billion equity value for CyberArk.',
    sourceClass: 'FILING',
    interpretation: 'Identity became a platform priority for strategic capital.',
    limitations: 'Acquisition does not establish organic category demand.',
    conflictingEvidenceIds: ['C7'],
    artifactLabel: 'SEC-MARKET-SIG-SRC-002 / D5b',
    tags: ['investment', 'identity', 'm-and-a'],
  },
  {
    id: 'D6',
    title: 'SEC Cyber Disclosure Rule / DORA / Marsh Cyber Insurance Update',
    organization: 'SEC / EIOPA / Marsh',
    publicationDate: '2023-07-26',
    economicPeriod: '2023–2026 regulatory context',
    canonicalUrl: 'https://www.sec.gov/files/rules/final/2023/33-11216.pdf',
    excerpt:
      'SEC requires disclosure of material cyber incidents and risk-management governance; DORA entered into application on 17 Jan 2025; Marsh reported US cyber-insurance rates declined while twelve hygiene controls were treated as essential.',
    sourceClass: 'OFFICIAL',
    interpretation:
      'Governance, identity, resilience, and third-party requirements can move independently of infrastructure.',
    limitations: 'Requirements and insurance controls do not establish product spending.',
    conflictingEvidenceIds: [],
    sourceAttributions: [
      {
        organization: 'SEC',
        publicationDate: '2023-07-26',
        economicPeriod: 'Final rule effective 2023-12-18',
        canonicalUrl: 'https://www.sec.gov/files/rules/final/2023/33-11216.pdf',
      },
      {
        organization: 'EIOPA (DORA)',
        publicationDate: '2025-01-17',
        economicPeriod: 'Application date',
        canonicalUrl: 'https://www.eiopa.europa.eu/digital-operational-resilience-act-dora_en',
      },
      {
        organization: 'Marsh',
        publicationDate: '2026-07-17',
        economicPeriod: 'US insurance rates, Q2 2026',
        canonicalUrl:
          'https://www.marsh.com/en/services/international-placement-services/insights/us-insurance-rates.html',
      },
      {
        organization: 'Marsh',
        publicationDate: '2022-03',
        economicPeriod: 'Twelve key cybersecurity controls',
        canonicalUrl:
          'https://www.marsh.com/my/services/cyber-risk/insights/cyber-resilience-twelve-key-controls-strengthen-your-security.html',
      },
    ],
    artifactLabel: 'SEC-MARKET-SIG-SRC-002 / D6',
    tags: ['regulation', 'insurance'],
  },
  {
    id: 'D7',
    title: 'Snowflake and DeepSeek Incident Research',
    organization: 'Mandiant / Wiz',
    publicationDate: '2024-06',
    economicPeriod: '2024–2026 incidents',
    canonicalUrl:
      'https://cloud.google.com/blog/topics/threat-intelligence/unc5537-snowflake-data-theft-extortion',
    excerpt:
      'Mandiant tied tenant compromise to stolen customer credentials and absent MFA; Wiz found a publicly accessible ClickHouse database containing chat history, secret keys, and backend details.',
    sourceClass: 'VENDOR-RESEARCH',
    interpretation: 'Identity, posture, and data-security need can be incident-driven.',
    limitations: 'Vendor-authored research and selected incidents are not a representative loss series.',
    conflictingEvidenceIds: [],
    sourceAttributions: [
      {
        organization: 'Mandiant',
        publicationDate: '2024-06',
        economicPeriod: 'Snowflake tenant compromise',
        canonicalUrl:
          'https://cloud.google.com/blog/topics/threat-intelligence/unc5537-snowflake-data-theft-extortion',
      },
      {
        organization: 'Wiz',
        publicationDate: '2025-01-29',
        economicPeriod: 'DeepSeek exposed database',
        canonicalUrl: 'https://www.wiz.io/blog/wiz-research-uncovers-exposed-deepseek-database-leak',
      },
    ],
    artifactLabel: 'SEC-MARKET-SIG-SRC-002 / D7',
    tags: ['incident', 'identity', 'data-security'],
  },
  {
    id: 'LAG-NO-CALL',
    title: 'Lag Hypothesis Disposition — Episode 002 Baseline',
    organization: 'SEC-MARKET-SIG-BL-002',
    publicationDate: '2026-08-15',
    economicPeriod: '2023-Q1 through 2026-Q1 analysis window',
    canonicalUrl: '',
    excerpt:
      'H1 Infrastructure leads cybersecurity demand: NO-CALL — later sequence observed, not validated. H2 Domain-specific lag: NO-CALL. H3 AI compresses lag: NO-CALL. At most fourteen aligned quarters; eight-quarter lag leaves six raw pairs.',
    sourceClass: 'OWN_ANALYSIS',
    interpretation:
      'The evidence supports a descriptive sequence, not a constant infrastructure-to-security lag.',
    limitations:
      'One broad mature infrastructure impulse; later wave still deploying at freeze; incompatible metric definitions across vendors.',
    conflictingEvidenceIds: ['A1b', 'C3', 'D2'],
    artifactLabel: 'SEC-MARKET-SIG-BL-002',
    tags: ['lag', 'no-call', 'methodology'],
  },
  {
    id: 'C9',
    title: 'SentinelOne Q1 FY27 Results',
    organization: 'SentinelOne',
    publicationDate: '2026-05-28',
    economicPeriod: 'Quarter ended 2026-04-30',
    canonicalUrl:
      'https://investors.sentinelone.com/press-releases/news-details/2026/SentinelOne-Announces-First-Quarter-Fiscal-Year-2027-Financial-Results/default.aspx',
    excerpt:
      'Total revenue grew 21% to $277 million. Annualized recurring revenue (ARR) grew 23% to $1,163 million. Quarterly net new ARR $44 million, +55% year-over-year.',
    sourceClass: 'IR',
    interpretation: 'Endpoint/XDR and emerging-platform re-acceleration. Second public SecOps print beside CrowdStrike.',
    limitations: 'Net-new ARR is a growth-rate print, not category breadth. Q2 FY27 results were not yet released at this update.',
    conflictingEvidenceIds: ['C6a', 'C6b', 'D1'],
    artifactLabel: 'Surface refresh / C9',
    tags: ['security-vendor', 'secops', 'endpoint'],
  },
  {
    id: 'C10',
    title: 'SailPoint FY2026 Results',
    organization: 'SailPoint',
    publicationDate: '2026-03-18',
    economicPeriod: 'Fiscal year ended 2026-01-31',
    canonicalUrl:
      'https://www.sec.gov/Archives/edgar/data/2030781/000162828026019034/sailpointinc-20260131x991x.htm',
    excerpt:
      'Total ARR was $1.125 billion, an increase of 28% year-over-year. SaaS ARR was $746 million, an increase of 38% year-over-year. Full-year revenue $1.071 billion, +24%.',
    sourceClass: 'FILING',
    interpretation: 'IGA demand is accelerating while workforce-IAM (Okta) decelerated. Identity is splitting, not one category.',
    limitations: 'Annual print; not a quarterly series aligned to the Episode 002 panel.',
    conflictingEvidenceIds: ['C7'],
    artifactLabel: 'Surface refresh / C10',
    tags: ['security-vendor', 'identity', 'iga'],
  },
  {
    id: 'D8',
    title: 'Cyera Series G announcement',
    organization: 'Cyera',
    publicationDate: '2026-06-10',
    economicPeriod: 'Series G close',
    canonicalUrl:
      'https://www.cyera.com/press-releases/cyera-raises-600-million-at-12-billion-valuation-to-continue-building-the-trust-layer-for-the-ai-era',
    excerpt:
      'Latest funding round of $600 million, quadrupling the company’s valuation over the last 18 months to $12 billion. Led by Evolution Equity Partners. Total funding over $2 billion.',
    sourceClass: 'IR',
    interpretation: 'Strategic capital into DSPM / AI-data security. Category formation signal, not realized customer spend.',
    limitations: 'Private company. Valuation and raise are not ARR or bookings.',
    conflictingEvidenceIds: ['D1'],
    artifactLabel: 'Surface refresh / D8',
    tags: ['investment', 'data-security', 'private'],
  },
  {
    id: 'D9',
    title: 'Secuvy funding and 2026 positioning',
    organization: 'Secuvy',
    publicationDate: '2023-03-10',
    economicPeriod: 'Last disclosed raise; 2026 product/partner signals',
    canonicalUrl:
      'https://www.businesswire.com/news/home/20230310005374/en/Secuvy-Announces-New-Investments-from-Dell-Technologies-Capital-and-WestWave-Capital-to-Modernize-Data-Privacy-and-Security',
    excerpt:
      'Funding round led by Dell Technologies Capital and WestWave Capital, with participation from Z5 Capital. Amount undisclosed. 2026 site notes Forrester Landscape recognition and Armada Bridge Marketplace listing.',
    sourceClass: 'IR',
    interpretation: 'Named data-security specialist in the partner set. No public ARR or growth series.',
    limitations: 'Last disclosed financing is 2023. Do not infer current demand from an old seed round.',
    conflictingEvidenceIds: [],
    sourceAttributions: [
      {
        organization: 'Secuvy / Business Wire',
        publicationDate: '2023-03-10',
        economicPeriod: 'Seed-stage financing',
        canonicalUrl:
          'https://www.businesswire.com/news/home/20230310005374/en/Secuvy-Announces-New-Investments-from-Dell-Technologies-Capital-and-WestWave-Capital-to-Modernize-Data-Privacy-and-Security',
      },
      {
        organization: 'Secuvy',
        publicationDate: '2026-05',
        economicPeriod: 'Armada Bridge Marketplace listing',
        canonicalUrl: 'https://secuvy.ai/',
      },
    ],
    artifactLabel: 'Surface refresh / D9',
    tags: ['investment', 'data-security', 'private'],
  },
  {
    id: 'D10',
    title: 'Lumos Series B and 2026 identity-agent launch',
    organization: 'Lumos',
    publicationDate: '2024-05-23',
    economicPeriod: 'Series B; March 2026 product launch',
    canonicalUrl:
      'https://www.businesswire.com/news/home/20240523314788/en/Lumos-Secures-%2435M-Series-B-Funding-to-Unify-the-SaaS-and-Identity-Management-Industries',
    excerpt:
      'Lumos announced $35M Series B led by Scale Venture Partners. March 24, 2026: launched Identity Security Agents on its Autonomous Identity platform. No public ARR disclosed.',
    sourceClass: 'IR',
    interpretation: 'IGA / SaaS-identity specialist with agent-identity product language. Capital and product formation, not a spend series.',
    limitations: 'Private. Series B is two years old. Product launch is not bookings.',
    conflictingEvidenceIds: ['C7'],
    sourceAttributions: [
      {
        organization: 'Lumos / Business Wire',
        publicationDate: '2024-05-23',
        economicPeriod: 'Series B',
        canonicalUrl:
          'https://www.businesswire.com/news/home/20240523314788/en/Lumos-Secures-%2435M-Series-B-Funding-to-Unify-the-SaaS-and-Identity-Management-Industries',
      },
      {
        organization: 'Lumos / PR Newswire',
        publicationDate: '2026-03-24',
        economicPeriod: 'Identity Security Agents launch',
        canonicalUrl:
          'https://www.prnewswire.com/news-releases/lumos-launches-identity-security-agents-that-turn-intelligence-into-enhanced-security-posture-at-scale-302722638.html',
      },
    ],
    artifactLabel: 'Surface refresh / D10',
    tags: ['investment', 'identity', 'private'],
  },
  {
    id: 'D11',
    title: 'Microsoft FY2026 Q4 — Entra not disclosed separately',
    organization: 'Microsoft',
    publicationDate: '2026-07-29',
    economicPeriod: 'Quarter ended 2026-06-30',
    canonicalUrl: 'https://www.sec.gov/Archives/edgar/data/789019/000119312526323632/msft-ex99_1.htm',
    excerpt:
      'Microsoft reports Productivity and Business Processes, Intelligent Cloud, and More Personal Computing. Entra is discussed on the call as part of E7 / Copilot / Agent 365. No Entra or identity-security revenue line is disclosed.',
    sourceClass: 'FILING',
    interpretation: 'Largest identity installed base. Unusable as a domain financial print.',
    limitations: 'Bundled into Microsoft 365 Commercial and security suites. Cannot carry an identity-category growth call.',
    conflictingEvidenceIds: [],
    sourceAttributions: [
      {
        organization: 'Microsoft',
        publicationDate: '2026-07-29',
        economicPeriod: 'Quarter ended 2026-06-30',
        canonicalUrl: 'https://www.sec.gov/Archives/edgar/data/789019/000119312526323632/msft-ex99_1.htm',
      },
      {
        organization: 'Microsoft',
        publicationDate: '2026-07-29',
        economicPeriod: 'FY2026 Q4 earnings call',
        canonicalUrl: 'https://aka.ms/transcriptfy26q4',
      },
    ],
    artifactLabel: 'Surface refresh / D11',
    tags: ['identity', 'platform', 'no-segment'],
  },
  {
    id: 'D12',
    title: 'Ping, BeyondTrust, and Delinea — private identity platforms',
    organization: 'Ping Identity / BeyondTrust / Delinea',
    publicationDate: '2026-08-16',
    economicPeriod: 'Current private status as of surface refresh',
    canonicalUrl: 'https://www.thomabravo.com/press-releases/thoma-bravo-completes-acquisition-of-ping-identity',
    excerpt:
      'Ping Identity was taken private by Thoma Bravo in 2022. BeyondTrust and Delinea are PE-owned privileged-access / identity platforms. None currently disclose a public quarterly revenue or ARR series.',
    sourceClass: 'IR',
    interpretation: 'Material identity competitors exist off-public-markets. Absence of prints is a coverage fact, not a demand fact.',
    limitations:
      'The 2021-2022 press releases document three different transactions, not one common one: Ping Identity’s completed take-private by Thoma Bravo, Clearlake Capital closing an investment in BeyondTrust alongside existing owner Francisco Partners, which had acquired it in 2018, and Delinea’s formation and rebrand out of the Thycotic/Centrify merger under TPG Capital. None of them speak to current financial reporting. Ping Identity and Delinea homepages, checked 2026-08-17, show no stock ticker or investor-relations section, supporting the no-public-ARR claim for those two as of that check. BeyondTrust’s current disclosure status was not independently re-verified in this pass.',
    conflictingEvidenceIds: [],
    sourceAttributions: [
      {
        organization: 'Ping Identity',
        publicationDate: '2022-10-18',
        economicPeriod: 'Thoma Bravo take-private',
        canonicalUrl:
          'https://www.thomabravo.com/press-releases/thoma-bravo-completes-acquisition-of-ping-identity',
      },
      {
        organization: 'Ping Identity',
        publicationDate: '2026-08-17',
        economicPeriod: 'Current homepage check',
        canonicalUrl: 'https://www.pingidentity.com',
      },
      {
        organization: 'BeyondTrust',
        publicationDate: '2021-08-17',
        economicPeriod: 'Clearlake / Francisco Partners transaction',
        canonicalUrl:
          'https://www.beyondtrust.com/press/beyondtrust-completes-transaction-with-clearlake-capital-and-francisco-partners',
      },
      {
        organization: 'Delinea',
        publicationDate: '2022-02-01',
        economicPeriod: 'Rebrand from Thycotic/Centrify merger',
        canonicalUrl: 'https://www.thomabravo.com/press-releases/centrify-now-delinea',
      },
      {
        organization: 'Delinea',
        publicationDate: '2026-08-17',
        economicPeriod: 'Current homepage check',
        canonicalUrl: 'https://delinea.com',
      },
    ],
    artifactLabel: 'Surface refresh / D12',
    tags: ['identity', 'private'],
  },
  {
    id: 'D13',
    title: 'Google completes Wiz acquisition',
    organization: 'Google',
    publicationDate: '2026-03-11',
    economicPeriod: 'Transaction close',
    canonicalUrl:
      'https://blog.google/innovation-and-ai/infrastructure-and-cloud/google-cloud/wiz-acquisition/',
    excerpt:
      'Google LLC today announced the completion of its acquisition of Wiz, a leading cloud and AI security platform. Wiz will join Google Cloud and maintain its brand and commitment to securing customers across all cloud environments. This deal was initially announced in March 2025.',
    sourceClass: 'IR',
    interpretation: 'Close of the announced cloud-security platform deal. Capital event, not a customer-spend print.',
    limitations:
      'Close announcement does not restate consideration. Use D5a for the ~$32B 8-K. Not proof of category demand.',
    conflictingEvidenceIds: [],
    artifactLabel: 'Surface refresh / D13',
    tags: ['investment', 'cloud-security', 'm-and-a'],
  },
  {
    id: 'D14',
    title: 'Palo Alto Networks completes CyberArk acquisition',
    organization: 'Palo Alto Networks',
    publicationDate: '2026-02-11',
    economicPeriod: 'Transaction close',
    canonicalUrl:
      'https://www.paloaltonetworks.com/company/press/2026/palo-alto-networks-completes-acquisition-of-cyberark-to-secure-the-ai-era/',
    excerpt:
      'Palo Alto Networks today announced the completion of its acquisition of CyberArk, establishing Identity Security as a core pillar of its platformization strategy. Under the terms of the agreement, CyberArk shareholders are entitled to receive $45.00 in cash and 2.2005 shares of Palo Alto Networks common stock for each CyberArk ordinary share.',
    sourceClass: 'IR',
    interpretation: 'Identity becomes a PANW platform pillar. Capital allocation, not organic identity demand.',
    limitations:
      'Close is not a growth print. Use D5b for the announced ~$25B equity value. Subsequent PANW prints include CyberArk.',
    conflictingEvidenceIds: ['C7'],
    artifactLabel: 'Surface refresh / D14',
    tags: ['investment', 'identity', 'm-and-a'],
  },
  {
    id: 'D15',
    title: 'Palo Alto Networks completes Portkey acquisition',
    organization: 'Palo Alto Networks',
    publicationDate: '2026-05-29',
    economicPeriod: 'Transaction close',
    canonicalUrl:
      'https://www.paloaltonetworks.com/company/press/2026/palo-alto-networks-completes-acquisition-of-portkey-to-secure-ai-agents',
    excerpt:
      'Palo Alto Networks today announced it has closed the acquisition of Portkey, a pioneer in AI Gateways. This acquisition establishes the AI Gateway as a mission-critical control plane for the enterprise. Portkey becomes the core AI Gateway for Prisma AIRS.',
    sourceClass: 'IR',
    interpretation: 'AI-runtime tuck-in into Prisma AIRS. Control-plane bet, not a demand series.',
    limitations: 'Terms not disclosed. Not a customer-spend or ARR print.',
    conflictingEvidenceIds: [],
    artifactLabel: 'Surface refresh / D15',
    tags: ['investment', 'ai-runtime', 'm-and-a'],
  },
  {
    id: 'D16',
    title: 'Cisco completes Astrix Security acquisition',
    organization: 'Cisco',
    publicationDate: '2026-06-29',
    economicPeriod: 'Intent announced; completed 2026-06-29',
    canonicalUrl: 'https://blogs.cisco.com/news/cisco-announces-intent-to-acquire-astrix-security',
    excerpt:
      'June 29, 2026 Update: We have completed the acquisition of Astrix Security. Astrix is described as a pioneer in Non-Human Identity (NHI) Security, focused on API keys, service accounts, and OAuth tokens. Cisco plans to integrate the capabilities into Cisco Identity Intelligence.',
    sourceClass: 'IR',
    interpretation: 'NHI / agent-identity tuck-in into Cisco Security. Platform assembly, not a category growth print.',
    limitations:
      'Cisco did not disclose terms. Same page carries both intent and the completion update. Do not treat secondary price rumors as a primary figure.',
    conflictingEvidenceIds: [],
    artifactLabel: 'Surface refresh / D16',
    tags: ['investment', 'identity', 'm-and-a'],
  },
  {
    id: 'D17',
    title: 'Zscaler announces intent to acquire Symmetry Systems',
    organization: 'Zscaler',
    publicationDate: '2026-05-21',
    economicPeriod: 'Transaction intent — not close',
    canonicalUrl:
      'https://ir.zscaler.com/news-releases/news-release-details/zscaler-acquire-symmetry-systems-combining-zero-trust-and-access',
    excerpt:
      'Zscaler today announced the intent to acquire Symmetry Systems, Inc., a pioneer in identity mapping and data access for AI security. Symmetry Systems’ access graph maps how human and non-human identities, applications, and data connect across the enterprise.',
    sourceClass: 'IR',
    interpretation: 'Data/identity access-graph tuck-in. Intent is a capital signal, not a close and not buyer spend.',
    limitations: 'Intent, not close. Terms not disclosed.',
    conflictingEvidenceIds: [],
    artifactLabel: 'Surface refresh / D17',
    tags: ['investment', 'data-security', 'm-and-a'],
  },
  {
    id: 'D18',
    title: 'Onyx Security raises $113M Series B',
    organization: 'Onyx Security',
    publicationDate: '2026-07-29',
    economicPeriod: 'Series B',
    canonicalUrl:
      'https://www.onyx.security/press-release/onyx-security-raises-113m-series-b-to-control-advanced-ai-quadrupling-revenue-since-stealth-launch-four-months-ago',
    excerpt:
      'Onyx Security announced a $113 million Series B funding round led by Bessemer Venture Partners. This brings the company’s total funding to $153M. The company said revenue grew fourfold in the four months since leaving stealth.',
    sourceClass: 'IR',
    interpretation: 'AI-control-plane formation capital. Category bet, not a disclosed ARR series.',
    limitations:
      'Private-company press. Company-stated revenue growth is not a public ARR or bookings print. Do not convert the raise into demand.',
    conflictingEvidenceIds: [],
    artifactLabel: 'Surface refresh / D18',
    tags: ['investment', 'ai-runtime', 'private'],
  },
  {
    id: 'D19',
    title: 'Zenity Series C funding announcement',
    organization: 'Zenity',
    publicationDate: '2026-08-03',
    economicPeriod: 'Series C close',
    canonicalUrl:
      'https://zenity.io/company-overview/newsroom/company-news/zenity-raises-125-million-to-secure-the-era-of-1-billion-ai-agents',
    excerpt:
      'Zenity today announced a $125 million Series C led by Norwest. Return on Security reported an $115.0M Series C from Norwest and an additional $10.0M Secondary Market in the same week.',
    sourceClass: 'IR',
    interpretation:
      'Largest agent-governance capital print in the window. $125M total equals $115M primary plus $10M secondary — not a source conflict.',
    limitations:
      'Private company. Company PR states $125M Series C; RoS splits primary and secondary. Neither raise nor valuation is ARR.',
    conflictingEvidenceIds: [],
    artifactLabel: 'Activity edition / D19',
    tags: ['investment', 'ai-runtime', 'private'],
  },
  {
    id: 'D20',
    title: 'Oak seed funding announcement',
    organization: 'Oak',
    publicationDate: '2026-07-15',
    economicPeriod: 'Seed round; stealth exit',
    canonicalUrl:
      'https://www.prnewswire.com/news-releases/oak-raises-60m-in-seed-funding-to-build-the-ai-native-identity-operating-system-302826349.html',
    excerpt:
      'Oak emerged from stealth today with $60 million in seed funding to build the security industry\'s Identity Operating System. The round was co-led by Accel, Greylock Partners, and CRV.',
    sourceClass: 'IR',
    interpretation: 'Mega-seed in AI-native identity. Capital heat signal, not disclosed buyer spend.',
    limitations: 'Private company. Seed size is exceptional; do not infer ARR from round size.',
    conflictingEvidenceIds: [],
    artifactLabel: 'Activity edition / D20',
    tags: ['investment', 'identity', 'private'],
  },
  {
    id: 'D21',
    title: 'Hush Security Series A with Akamai strategic',
    organization: 'Hush Security',
    publicationDate: '2026-07-28',
    economicPeriod: 'Series A',
    canonicalUrl:
      'https://www.ylventures.com/news/hush-security-raises-30m-to-close-the-ai-agent-governance-gap-with-akamai-joining-as-strategic-investor',
    excerpt:
      'Hush Security announced a $30 million Series A funding round, with Akamai Technologies joining as a strategic investor alongside existing investors Battery Ventures and YL Ventures.',
    sourceClass: 'IR',
    interpretation:
      'Strategic platform investor on the cap table for NHI / agent identity. Capital and positioning, not a demand series.',
    limitations: 'Private company. Akamai strategic is a supply-side signal, not proof of enterprise buyer spend.',
    conflictingEvidenceIds: [],
    artifactLabel: 'Activity edition / D21',
    tags: ['investment', 'identity', 'private'],
  },
  {
    id: 'D22',
    title: 'Cyera agreement to acquire Oasis Security',
    organization: 'Cyera / SecurityWeek',
    publicationDate: '2026-07-28',
    economicPeriod: 'LOI announced; not close',
    canonicalUrl:
      'https://www.securityweek.com/cyera-acquiring-oasis-security-in-1-billion-deal/',
    excerpt:
      'Cyera announced it has entered into an agreement to acquire agentic access management provider Oasis Security. Cyera confirmed to SecurityWeek this is a $1 billion deal. The announcement comes just weeks after Cyera raised $600 million at a $12 billion valuation.',
    sourceClass: 'INDEPENDENT',
    interpretation:
      'Raise-then-acquirer pattern in data/identity. LOI is capital intent, not close and not buyer spend.',
    limitations:
      'Agreement, not completed close. Value is press-reported unless filing confirms. Do not treat as ARR.',
    conflictingEvidenceIds: [],
    artifactLabel: 'Activity edition / D22',
    tags: ['investment', 'identity', 'm-and-a'],
  },
  {
    id: 'D23',
    title: 'Cathedral venture round',
    organization: 'Return on Security',
    publicationDate: '2026-07-27',
    economicPeriod: 'Security, Funded #254 week',
    canonicalUrl: 'https://www.returnonsecurity.com/p/security-funded-254',
    excerpt:
      'Cathedral, a United States-based autonomous red teaming platform for military cyber operations, raised a $160.0M Venture Round from Andreessen Horowitz and Sequoia Capital.',
    sourceClass: 'INDEPENDENT',
    interpretation: 'Defense-oriented autonomous red teaming at scale. Capital signal for dual-use accounts, not enterprise agent governance.',
    limitations: 'Newsletter-sourced. Private company. Round is not disclosed revenue.',
    conflictingEvidenceIds: [],
    artifactLabel: 'Activity edition / D23',
    tags: ['investment', 'exposure', 'private'],
  },
  {
    id: 'D24',
    title: 'Glow emergence funding announcement',
    organization: 'Glow',
    publicationDate: '2026-07-22',
    economicPeriod: 'Stealth exit',
    canonicalUrl: 'https://www.glow.io/news/glow-emerges-from-stealth-with-180-million',
    excerpt: 'Glow emerged from stealth with $180 million in funding at a $1.2 billion valuation.',
    sourceClass: 'IR',
    interpretation: 'AI endpoint prevention capital. Funding amount and valuation as stated by the company at stealth exit.',
    limitations: 'Private company. Valuation and raise are not ARR. Company PR does not label a round type (e.g., Series A/B).',
    conflictingEvidenceIds: [],
    artifactLabel: 'Activity edition / D24',
    tags: ['investment', 'endpoint', 'private'],
  },
  {
    id: 'D25',
    title: 'Neo launch funding announcement',
    organization: 'Neo Security',
    publicationDate: '2026-07-20',
    economicPeriod: 'Stealth exit',
    canonicalUrl:
      'https://www.globenewswire.com/news-release/2026/07/20/3329638/0/en/Neo-Launches-with-100M-to-Secure-AI-Software-Across-the-Enterprise.html',
    excerpt:
      'Neo emerged from stealth with $100M in funding from Andreessen Horowitz and Bessemer Venture Partners. Return on Security reported a $75.0M Series A from the same investors in the same window.',
    sourceClass: 'IR',
    interpretation:
      'Agentic software control capital at launch. $100M total at emergence vs $75M Series A is round-vs-cumulative framing, resolved by company PR.',
    limitations: 'Private company. Total funding at launch is not ARR or bookings.',
    conflictingEvidenceIds: [],
    artifactLabel: 'Activity edition / D25',
    tags: ['investment', 'ai-runtime', 'private'],
  },
  {
    id: 'D26',
    title: 'Horizon3.ai Series E',
    organization: 'Return on Security',
    publicationDate: '2026-08-10',
    economicPeriod: 'Security, Funded #256 week',
    canonicalUrl: 'https://www.returnonsecurity.com/p/security-funded-256',
    excerpt:
      'Horizon3.ai, a United States-based autonomous penetration testing and threat exposure management platform, raised a $250.0M Series E from NightDragon and New Enterprise Associates.',
    sourceClass: 'INDEPENDENT',
    interpretation: 'Autonomous testing scale-up check. Large but mature-category capital, not agent-governance formation.',
    limitations: 'Newsletter-sourced. Scale-up, not a new-name formation signal for the agent cluster.',
    conflictingEvidenceIds: [],
    artifactLabel: 'Activity edition / D26',
    tags: ['investment', 'exposure', 'private'],
  },
  {
    id: 'D27',
    title: 'SYN Ventures 2026 agent-runtime portfolio',
    organization: 'SYN Ventures',
    publicationDate: '2026-08-16',
    economicPeriod: '2026 portfolio entries',
    canonicalUrl: 'https://www.synventures.com/portfolio',
    excerpt:
      'Series A, 2026 — Arcade is the secure action layer for production AI agents. Seed, 2026 — CodeIntegrity is the runtime control layer for AI agents.',
    sourceClass: 'IR',
    interpretation: 'Unpriced formation discovery. VC portfolio page only — no public amount or exact date.',
    limitations: 'Single source. Year-only dating. Do not promote to lead without press confirmation.',
    conflictingEvidenceIds: [],
    artifactLabel: 'Activity edition / D27',
    tags: ['investment', 'ai-runtime', 'private'],
  },
  {
    id: 'D28',
    title: 'Zafran Security strategic round from Cisco Investments',
    organization: 'Return on Security',
    publicationDate: '2026-07-27',
    economicPeriod: 'Security, Funded #254 week',
    canonicalUrl: 'https://www.returnonsecurity.com/p/security-funded-254',
    excerpt:
      'Zafran Security, a United States-based threat and risk prioritization platform, raised an undisclosed Venture Round from Cisco Investments.',
    sourceClass: 'INDEPENDENT',
    interpretation: 'Platform strategic investment in exposure/risk prioritization. Part of platform-absorption pattern.',
    limitations: 'Undisclosed amount. Newsletter-sourced. Not buyer spend.',
    conflictingEvidenceIds: [],
    artifactLabel: 'Activity edition / D28',
    tags: ['investment', 'exposure', 'private'],
  },
  {
    id: 'D29',
    title: 'Above Security venture round from CrowdStrike Falcon Fund',
    organization: 'Return on Security',
    publicationDate: '2026-08-03',
    economicPeriod: 'Security, Funded #256 week',
    canonicalUrl: 'https://www.returnonsecurity.com/p/security-funded-256',
    excerpt:
      'Above Security, an Israel-based agent-driven insider threat platform, raised an undisclosed Venture Round from CrowdStrike Falcon Fund.',
    sourceClass: 'INDEPENDENT',
    interpretation: 'CrowdStrike strategic fund bet on agent-driven insider threat. Platform seeding pattern.',
    limitations: 'Undisclosed amount. Newsletter-sourced.',
    conflictingEvidenceIds: [],
    artifactLabel: 'Activity edition / D29',
    tags: ['investment', 'ai-runtime', 'private'],
  },
  {
    id: 'C11',
    title: 'Cato Networks 2025 ARR milestone',
    organization: 'Cato Networks',
    publicationDate: '2026-02-24',
    economicPeriod: 'Calendar year 2025',
    canonicalUrl:
      'https://www.catonetworks.com/news/cato-surpasses-350-million-arr-with-43-yoy-growth-in-2025/',
    excerpt:
      'Its 2025 annual recurring revenue (ARR) surpassed $350 million, an increase of 43% year-over-year (YoY) compared to 2024.',
    sourceClass: 'IR',
    interpretation: 'Private SASE scale print. Fills the Network/SASE bench beside public SSE vendors.',
    limitations: 'Private company. Company-stated ARR, not audited filing. Threshold is >$350M, not an exact figure.',
    conflictingEvidenceIds: [],
    artifactLabel: 'D-39 vendor signals / C11',
    tags: ['security-vendor', 'sase', 'network'],
  },
  {
    id: 'C12',
    title: 'Netskope FY2026 Results',
    organization: 'Netskope',
    publicationDate: '2026-03-11',
    economicPeriod: 'Fiscal year ended 2026-01-31',
    canonicalUrl:
      'https://investors.netskope.com/news-releases/news-release-details/netskope-announces-strong-fourth-quarter-and-fiscal-year-2026',
    excerpt: 'ARR grew 31% year-over-year to $811 million as of January 31, 2026.',
    sourceClass: 'IR',
    interpretation: 'Public SSE/SASE bellwether now on investor relations. Strong growth at scale.',
    limitations: 'Annual print; not a quarterly series aligned to the Episode 002 panel.',
    conflictingEvidenceIds: [],
    artifactLabel: 'D-39 vendor signals / C12',
    tags: ['security-vendor', 'sase', 'network'],
  },
  {
    id: 'C13',
    title: 'CrowdStrike Q4 FY2026 Results — Falcon Cloud segment',
    organization: 'CrowdStrike',
    publicationDate: '2026-03-03',
    economicPeriod: 'Quarter ended 2026-01-31',
    canonicalUrl:
      'https://ir.crowdstrike.com/news-releases/news-release-details/crowdstrike-reports-fourth-quarter-and-fiscal-year-2026',
    excerpt:
      'For the first time, our cloud business exceeded $800 million in ending ARR… grew more than 35% year over year.',
    sourceClass: 'IR',
    interpretation: 'Cloud-security segment ARR at scale. Distinct from total ending ARR on the SecOps card.',
    limitations:
      'Earnings-call metric, not a filing line item. Segment definition is company-defined. Use C1 for total CrowdStrike ARR.',
    conflictingEvidenceIds: ['C1'],
    artifactLabel: 'D-39 vendor signals / C13',
    tags: ['security-vendor', 'cloud-security', 'secops'],
  },
  {
    id: 'D30',
    title: 'Upwind Series B funding announcement',
    organization: 'Upwind',
    publicationDate: '2026-01-26',
    economicPeriod: 'Series B close',
    canonicalUrl: 'https://www.securityweek.com/upwind-raises-250-million-at-1-5-billion-valuation/',
    excerpt:
      'Upwind today announced raising $250 million in a Series B funding round… valuation to $1.5 billion… total raised… $430 million.',
    sourceClass: 'INDEPENDENT',
    interpretation: 'First Cloud-domain CNAPP capital signal on the prints board. Category formation, not buyer spend.',
    limitations:
      'Company-quoted via SecurityWeek; official Upwind press paths returned 404 on fetch. Valuation and raise are not ARR.',
    conflictingEvidenceIds: [],
    artifactLabel: 'D-39 vendor signals / D30',
    tags: ['investment', 'cloud-security', 'private'],
  },
  {
    id: 'D31',
    title: 'Torq Series D funding announcement',
    organization: 'Torq',
    publicationDate: '2026-01-12',
    economicPeriod: 'Series D close',
    canonicalUrl: 'https://torq.io/news/torq-seriesd/',
    excerpt:
      'Closed a massive $140 million Series D funding round, propelling its valuation to $1.2 billion and total funding to $332M.',
    sourceClass: 'IR',
    interpretation: 'SOAR / agentic SecOps scale capital. Platform bet, not a disclosed ARR series.',
    limitations: 'Private company. Valuation and raise are not ARR or bookings.',
    conflictingEvidenceIds: [],
    artifactLabel: 'D-39 vendor signals / D31',
    tags: ['investment', 'secops', 'private'],
  },
  {
    id: 'C14',
    title: 'BigID revenue milestone',
    organization: 'BigID',
    publicationDate: '2025-05-16',
    economicPeriod: 'Company-stated revenue',
    canonicalUrl:
      'https://www.prweb.com/releases/bigid-expands-global-partner-strategy-with-appointment-of-ian-williamson-as-svp-of-global-channel--alliances-302454829.html',
    excerpt:
      'BigID is the first data security posture management (DSPM) platform to surpass $100M in revenue.',
    sourceClass: 'IR',
    interpretation: 'DSPM scale signal from company PR. Not audited ARR or a quarterly series.',
    limitations: 'Single company-stated milestone in a hire release. Not filing-backed.',
    conflictingEvidenceIds: [],
    artifactLabel: 'Domain vendor pass / C14',
    tags: ['security-vendor', 'data-security', 'private'],
  },
  {
    id: 'C15',
    title: 'Sentra Series B funding announcement',
    organization: 'Sentra',
    publicationDate: '2025-04-22',
    economicPeriod: 'Series B close',
    canonicalUrl:
      'https://sentra.io/news/sentra-closes-50-million-series-b-amid-surging-demand-for-securing-data-for-ai-adoption',
    excerpt:
      'Sentra announced it has closed a $50 million Series B funding round… total investment to more than $100 million, following a more than 300% year-over-year increase in revenue.',
    sourceClass: 'IR',
    interpretation: 'DSPM capital with company-stated revenue growth. Raise is not buyer spend.',
    limitations: 'Private company. Revenue growth is company-stated, not public ARR.',
    conflictingEvidenceIds: [],
    artifactLabel: 'Domain vendor pass / C15',
    tags: ['security-vendor', 'data-security', 'private'],
  },
  {
    id: 'C16',
    title: 'Veeam completes acquisition of Securiti AI',
    organization: 'Veeam / Securiti',
    publicationDate: '2025-12-11',
    economicPeriod: 'Acquisition close',
    canonicalUrl: 'https://www.veeam.com/company/press-release/veeam-acquires-securiti-ai.html',
    excerpt:
      'Veeam today announced the completion of its $1.725 billion acquisition of Securiti AI, the recognized leader in Data Security Posture Management (DSPM).',
    sourceClass: 'IR',
    interpretation: 'Data-security platform consolidation. Capital event, not customer spend.',
    limitations: 'Close announcement. Purchase price disclosed; not ARR.',
    conflictingEvidenceIds: [],
    artifactLabel: 'Domain vendor pass / C16',
    tags: ['security-vendor', 'data-security', 'm-and-a'],
  },
  {
    id: 'C17',
    title: 'Orca Security TD SYNNEX distribution partnership',
    organization: 'Orca Security',
    publicationDate: '2026-04-13',
    economicPeriod: 'North America distribution agreement',
    canonicalUrl:
      'https://orca.security/resources/press-releases/orca-security-td-synnex-partnership/',
    excerpt:
      'Orca Security announced a strategic distribution agreement for North America with TD SYNNEX… designed to accelerate new logo acquisition while providing the infrastructure necessary for partners to drive deep adoption of Orca Security’s AI-powered cloud security platform.',
    sourceClass: 'IR',
    interpretation: '2026 go-to-market scale signal for CNAPP. Not revenue or new equity.',
    limitations: 'Partnership announcement only. Last disclosed equity round remains Oct 2021 Series C.',
    conflictingEvidenceIds: [],
    artifactLabel: 'Domain vendor pass / C17',
    tags: ['security-vendor', 'cloud-security', 'private'],
  },
  {
    id: 'C18',
    title: 'Orca Security Series C extension',
    organization: 'Orca Security',
    publicationDate: '2021-10-05',
    economicPeriod: 'Series C extension',
    canonicalUrl:
      'https://orca.security/resources/press-releases/orca-security-series-c-550-million-announcement/',
    excerpt:
      'Orca Security announced that it has raised $550 million in its extended Series C fundraising round… valuation… to $1.8 Billion.',
    sourceClass: 'IR',
    interpretation: 'Last disclosed Orca equity print. Context for CNAPP bench; not current-year revenue.',
    limitations: '2021 round. No 2025–2026 ARR or revenue series from issuer.',
    conflictingEvidenceIds: [],
    artifactLabel: 'Domain vendor pass / C18',
    tags: ['security-vendor', 'cloud-security', 'private'],
  },
  {
    id: 'C19',
    title: 'Aqua Security Series E extension',
    organization: 'Aqua Security',
    publicationDate: '2024-01-03',
    economicPeriod: 'Series E extension',
    canonicalUrl: 'https://www.aquasec.com/news/60m-additional-funding/',
    excerpt:
      'Aqua Security announced it has secured $60M in funding… an extension of the company’s Series E round, placing Aqua’s valuation above $1B. Aqua has now raised $325 million since its founding in 2015.',
    sourceClass: 'IR',
    interpretation: 'Last disclosed Aqua equity print. CNAPP/CWPP bench context; not 2026 revenue.',
    limitations: 'Jan 2024 funding. No 2025–2026 ARR or revenue series from issuer on checked releases.',
    conflictingEvidenceIds: [],
    artifactLabel: 'Domain vendor pass / C19',
    tags: ['security-vendor', 'cloud-security', 'private'],
  },
  {
    id: 'C20',
    title: 'WitnessAI strategic funding announcement',
    organization: 'WitnessAI',
    publicationDate: '2026-01-13',
    economicPeriod: 'Strategic round',
    canonicalUrl:
      'https://witness.ai/resources/witnessai-raises-58-million-for-global-expansion-and-announces-new-ways-to-secure-ai-agents/',
    excerpt:
      'WitnessAI announced strategic funding of $58 million… the company experienced over 500% growth in ARR and scaled employee headcount by 5x in the past 12 months.',
    sourceClass: 'IR',
    interpretation: 'AI-runtime security capital with company-stated ARR growth. Not audited revenue.',
    limitations: 'Private company. ARR growth is company-stated.',
    conflictingEvidenceIds: [],
    artifactLabel: 'Domain vendor pass / C20',
    tags: ['security-vendor', 'ai-runtime', 'private'],
  },
  {
    id: 'C21',
    title: 'Tines Series C funding announcement',
    organization: 'Tines',
    publicationDate: '2025-02-11',
    economicPeriod: 'Series C close',
    canonicalUrl:
      'https://www.prnewswire.com/news-releases/tines-secures-125m-in-series-c-financing-bringing-total-valuation-to-1-125b-302372726.html',
    excerpt:
      'Tines secured $125 million in Series C financing, valuing the company at $1.125 billion… total capital raised to $272 million.',
    sourceClass: 'IR',
    interpretation: 'Workflow automation / SOAR-adjacent scale capital. Not disclosed ARR.',
    limitations: 'Private company. Valuation and raise are not bookings or ARR.',
    conflictingEvidenceIds: [],
    artifactLabel: 'Domain vendor pass / C21',
    tags: ['security-vendor', 'secops', 'private'],
  },
  {
    id: 'C22',
    title: 'Check Point agreement to acquire Lakera',
    organization: 'Check Point / Lakera',
    publicationDate: '2025-09-16',
    economicPeriod: 'Agreement announced',
    canonicalUrl:
      'https://www.checkpoint.com/press-releases/check-point-acquires-lakera-to-deliver-end-to-end-ai-security-for-enterprises/',
    excerpt:
      'Check Point entered into an agreement to acquire Lakera… expected to close in Q4 2025.',
    sourceClass: 'IR',
    interpretation: 'AI-runtime security tuck-in by a public platform. Terms undisclosed.',
    limitations: 'Agreement, not necessarily close at time of site update. No purchase price disclosed.',
    conflictingEvidenceIds: [],
    artifactLabel: 'Domain vendor pass / C22',
    tags: ['security-vendor', 'ai-runtime', 'm-and-a'],
  },
  {
    id: 'C23',
    title: 'ServiceNow acquisition of Veza',
    organization: 'ServiceNow',
    publicationDate: '2025-12-02',
    economicPeriod: 'Acquisition announcement',
    canonicalUrl:
      'https://newsroom.servicenow.com/press-releases/details/2025/ServiceNow-to-Expand-Security-Portfolio-With-Acquisition-of-Vezas-Leading-AI-native-Identity-Security-Platform/default.aspx',
    excerpt:
      'ServiceNow announced its intent to acquire Veza… The Veza acquisition closed on March 2, 2026.',
    sourceClass: 'IR',
    interpretation: 'Identity / NHI platform absorption. Close confirmed; price undisclosed.',
    limitations: 'Purchase price not disclosed in ServiceNow release checked.',
    conflictingEvidenceIds: [],
    artifactLabel: 'Domain vendor pass / C23',
    tags: ['security-vendor', 'identity', 'm-and-a'],
  },
  {
    id: 'C24',
    title: 'Palo Alto Networks Prisma AIRS customer count',
    organization: 'Palo Alto Networks',
    publicationDate: '2026-06-02',
    economicPeriod: 'Q3 FY26 earnings call',
    canonicalUrl:
      'https://investors.paloaltonetworks.com/static-files/ea18c9ae-cbe6-4b5d-aa7c-65a6b9aeb2e2',
    excerpt:
      'We have over 300 Prisma AIRS customers as of Q3, up from just 100 at the end of Q2.',
    sourceClass: 'TRANSCRIPT',
    interpretation: 'Cloud / AI-security adoption metric. Customer count, not ARR.',
    limitations: 'Earnings call metric. Not a standalone cloud revenue series.',
    conflictingEvidenceIds: [],
    artifactLabel: 'Domain vendor pass / C24',
    tags: ['security-vendor', 'cloud-security', 'public'],
  },
  {
    id: 'C25',
    title: 'Palo Alto Networks XSIAM ARR',
    organization: 'Palo Alto Networks',
    publicationDate: '2026-06-02',
    economicPeriod: 'Q3 FY26 earnings call',
    canonicalUrl:
      'https://investors.paloaltonetworks.com/static-files/ea18c9ae-cbe6-4b5d-aa7c-65a6b9aeb2e2',
    excerpt:
      'We ended third quarter with more than $600 million in ARR, representing 100% year-over-year increase across a growing base of 740 customers.',
    sourceClass: 'TRANSCRIPT',
    interpretation: 'SecOps platform ARR segment. Distinct from headline PANW organic revenue print.',
    limitations: 'Segment ARR on earnings call; verify each quarter.',
    conflictingEvidenceIds: [],
    artifactLabel: 'Domain vendor pass / C25',
    tags: ['security-vendor', 'secops', 'public'],
  },
  {
    id: 'D32',
    title: 'Palo Alto Networks acquisition of Protect AI — price and allocation',
    organization: 'Palo Alto Networks',
    publicationDate: '2025-08-29',
    economicPeriod: 'Fiscal year ended 2025-07-31',
    canonicalUrl:
      'https://www.sec.gov/Archives/edgar/data/1327567/000132756725000027/panw-20250731.htm',
    excerpt:
      'On July 22, 2025, we completed our acquisition of Protect AI, Inc. (“Protect AI”), a privately-held cyber security company focused on AI security. The total purchase consideration for the acquisition of Protect AI was $634.5 million… Goodwill $515.8M · Identified intangible assets $70.0M · Cash $50.5M · Net liabilities assumed $(1.8)M · Total $634.5M. The single identified intangible is developed technology at $70.0M over 5 years. There is no customer-relationships intangible.',
    sourceClass: 'FILING',
    interpretation:
      'Palo Alto put $515.8M of the $634.5M price into goodwill and $70.0M into developed technology, with no value assigned to customer relationships. The same filing allocates IBM QRadar’s $476.0M of intangibles as $464.0M customer relationships and $12.0M developed technology — a direct contrast in how the two deals were valued.',
    limitations:
      'An absent customer-relationships intangible is a valuation judgment about separable customer-contract value, not a count of Protect AI’s customers.',
    conflictingEvidenceIds: [],
    artifactLabel: 'SEC-MARKET-AI-002 / D32',
    tags: ['ai-runtime', 'm-and-a', 'filing'],
  },
  {
    id: 'D33',
    title: 'Palo Alto Networks FY2025 acquisitions immateriality statement',
    organization: 'Palo Alto Networks',
    publicationDate: '2025-08-29',
    economicPeriod: 'Fiscal year ended 2025-07-31',
    canonicalUrl:
      'https://www.sec.gov/Archives/edgar/data/1327567/000132756725000027/panw-20250731.htm',
    excerpt:
      'Pro forma results of operations have not been presented because the effects of the acquisitions were not material to our consolidated statements of operations.',
    sourceClass: 'FILING',
    interpretation:
      'Palo Alto states its fiscal-year acquisitions, Protect AI included, did not move its consolidated results. Bounds the acquired revenue from above; does not disclose it.',
    limitations:
      '"Not material" is an accounting threshold relative to Palo Alto’s own size — an upper bound on the acquired revenue, not a statement that it is zero, and a larger bound than the same phrase would carry at a smaller acquirer. The sentence covers the fiscal year’s acquisitions collectively; it does not name Protect AI alone.',
    conflictingEvidenceIds: [],
    artifactLabel: 'SEC-MARKET-AI-002 / D33',
    tags: ['ai-runtime', 'm-and-a', 'filing'],
  },
  {
    id: 'D34',
    title: 'F5 acquisition of CalypsoAI — close, price, allocation and immateriality',
    organization: 'F5',
    publicationDate: '2026-08-06',
    economicPeriod: 'Quarter ended 2026-06-30',
    canonicalUrl:
      'https://www.sec.gov/Archives/edgar/data/1048695/000104869526000067/ffiv-20260630.htm',
    excerpt:
      'On September 26, 2025, the Company closed on a transaction for the acquisition of CalypsoAI Corp. (“CalypsoAI”), a provider in enterprise AI security for $145.2 million in cash… Other net tangible assets acquired, at fair value $14,151K · Identifiable intangible assets, developed technology $16,900K · Goodwill $114,156K. The pro forma financial information, as well as the revenue and earnings generated by CalypsoAI, were not material to the Company\'s operations for the periods presented.',
    sourceClass: 'FILING',
    interpretation:
      'F5 assigned $16,900K of the $145.2M price to developed technology and $114,156K to goodwill, with no value assigned to customer relationships — the same allocation pattern as Protect AI at Palo Alto.',
    limitations:
      '"Not material" is an accounting threshold relative to F5’s own size — an upper bound on CalypsoAI’s acquired revenue, not a statement that it is zero, and a smaller bound in absolute dollars than the same phrase carries at Palo Alto’s larger revenue base. An absent customer-relationships intangible is a valuation judgment about separable customer-contract value, not a count of CalypsoAI’s customers.',
    conflictingEvidenceIds: [],
    artifactLabel: 'SEC-MARKET-AI-002 / D34',
    tags: ['ai-runtime', 'm-and-a', 'filing'],
  },
  {
    id: 'D35',
    title: 'F5 acquisition of SurePath AI — close, price and immateriality',
    organization: 'F5',
    publicationDate: '2026-08-06',
    economicPeriod: 'Quarter ended 2026-06-30',
    canonicalUrl:
      'https://www.sec.gov/Archives/edgar/data/1048695/000104869526000067/ffiv-20260630.htm',
    excerpt:
      'On June 15, 2026, the Company closed on a transaction for the acquisition of SurePath AI, Inc. (“SurePath”), a provider of network-based AI discovery, intent classification, and shadow AI detection for $50.1 million… The acquired assets and assumed liabilities of the acquisition were not material and the Company recorded $39.1 million of goodwill as a result of the acquisition. The acquisition did not have a material impact to the Company\'s operating results.',
    sourceClass: 'FILING',
    interpretation:
      'F5 paid $50.1M for SurePath and recorded $39.1M of that price as goodwill — the third AI security close in the sequence with no disclosed buyer-spend figure attached to it.',
    limitations:
      '"Not material" is an accounting threshold relative to F5’s own size — an upper bound on SurePath’s acquired revenue and results, not a statement that either is zero.',
    conflictingEvidenceIds: [],
    artifactLabel: 'SEC-MARKET-AI-002 / D35',
    tags: ['ai-runtime', 'm-and-a', 'filing'],
  },
  {
    id: 'D36',
    title: 'CyberArk Software Ltd. Form 15-12G — deregistration',
    organization: 'CyberArk Software Ltd.',
    publicationDate: '2026-02-23',
    economicPeriod: 'Deregistration filing',
    canonicalUrl:
      'https://www.sec.gov/Archives/edgar/data/1598110/000110465926018360/tm266096d1_1512g.htm',
    excerpt:
      'CERTIFICATION AND NOTICE OF TERMINATION OF REGISTRATION UNDER SECTION 12(g) OF THE SECURITIES EXCHANGE ACT OF 1934 OR SUSPENSION OF DUTY TO FILE REPORTS UNDER SECTIONS 13 AND 15(d) OF THE SECURITIES EXCHANGE ACT OF 1934… Commission File Number 001-36625. EDGAR now returns no ticker for this filer.',
    sourceClass: 'FILING',
    interpretation:
      'CyberArk formally terminated its SEC reporting obligation after its close by Palo Alto — the filing behind print-cyberark’s "no standalone series after close."',
    limitations:
      'A deregistration filing; it does not itself state a revenue or valuation figure.',
    conflictingEvidenceIds: [],
    artifactLabel: 'SEC-MARKET-AI-002 / D36',
    tags: ['identity', 'm-and-a', 'filing'],
  },
  {
    id: 'C26',
    title: 'Zscaler Q4 and Fiscal 2026 Results',
    organization: 'Zscaler',
    publicationDate: '2026-09-03',
    economicPeriod: 'Quarter and fiscal year ended 2026-07-31',
    canonicalUrl:
      'https://www.sec.gov/Archives/edgar/data/1713683/000171368326000156/zs-07312026_991.htm',
    excerpt:
      'ARR: Grew 25% year over year to $3,771 million, of which $246 million was net new ARR during the fourth quarter of fiscal 2026. Excluding the acquisition of Red Canary, which contributed ARR of $141 million, ARR grew 20% to $3,630 million and net new ARR grew 17%.',
    sourceClass: 'FILING',
    interpretation: 'Organic ARR growth held near the prior quarter; headline growth unchanged at 25% including Red Canary.',
    limitations: 'Red Canary affects headline ARR; subscription timing differs from product vendors.',
    conflictingEvidenceIds: ['C6a', 'C6b'],
    artifactLabel: 'Scorecard refresh 2026-09-25 / C26',
    tags: ['security-vendor', 'sase'],
    retrievedAt: '2026-09-25',
    retrieval: {
      finalUrl: 'https://www.sec.gov/Archives/edgar/data/1713683/000171368326000156/zs-07312026_991.htm',
      sha256: 'fa5040e5d9b5bde2ca1fe4c4bb9f137b26c2ab69c64513e0edc0aa37521b351e',
      fetchedAt: '2026-09-25T22:45:00Z',
      locator: 'Fourth Quarter Fiscal 2026 Results — ARR bullet',
    },
  },
  {
    id: 'C27',
    title: 'Cato Networks ARR milestone update',
    organization: 'Cato Networks',
    publicationDate: '2026-08-20',
    economicPeriod: 'ARR milestone referenced in company blog, August 2026 (originally announced 2026-07-27)',
    canonicalUrl:
      'https://www.catonetworks.com/blog/three-years-as-a-leader-built-for-where-the-market-is-going/',
    excerpt:
      'Cato’s momentum continues to accelerate. We recently surpassed $415 million in annual recurring revenue, growing 42% year over year, and now serve more than 4,800 customers worldwide.',
    sourceClass: 'IR',
    interpretation: 'Supersedes the prior $350M/2025 ARR print with a materially larger, more recent company-stated milestone.',
    limitations:
      'Company-stated, not an audited filing. The originating 2026-07-27 press release (catonetworks.com/news/) returned an Incapsula bot challenge on every fetch attempt this session; this record instead cites the same figure as restated in Cato’s own blog, retrieved via its public RSS feed (which was not gated) rather than the blog page directly. No exact "as of" date is stated beyond "recently."',
    conflictingEvidenceIds: [],
    artifactLabel: 'Scorecard refresh 2026-09-25 / C27',
    tags: ['security-vendor', 'sase', 'network'],
    retrievedAt: '2026-09-25',
    retrieval: {
      finalUrl: 'https://www.catonetworks.com/feed/',
      sha256: '85a1177d8d3b51fb02a1c26e864fc8cc9ea36e2d98fce195c69d6600ec226c25',
      fetchedAt: '2026-09-25T23:05:00Z',
      locator: 'RSS item "Three Years as a Leader. Built for Where the Market Is Going.", pubDate 2026-08-20',
    },
  },
  {
    id: 'C28',
    title: 'Okta Q2 FY27 Results',
    organization: 'Okta',
    publicationDate: '2026-08-26',
    economicPeriod: 'Quarter ended 2026-07-31',
    canonicalUrl:
      'https://www.sec.gov/Archives/edgar/data/1660134/000166013426000068/okta-7312026_ex991.htm',
    excerpt:
      'Total revenue was $805 million, an increase of 11% year-over-year… cRPO, which represents subscription backlog expected to be recognized over the next 12 months, was $2.585 billion, up 14% compared to the second quarter of fiscal 2026.',
    sourceClass: 'FILING',
    interpretation: 'cRPO growth reaccelerated from the prior quarter; revenue growth held flat.',
    limitations: 'cRPO is sensitive to contract duration and sales timing.',
    conflictingEvidenceIds: ['D5b'],
    artifactLabel: 'Scorecard refresh 2026-09-25 / C28',
    tags: ['security-vendor', 'identity'],
    retrievedAt: '2026-09-25',
    retrieval: {
      finalUrl: 'https://www.sec.gov/Archives/edgar/data/1660134/000166013426000068/okta-7312026_ex991.htm',
      sha256: '7f24a587996c005cae99c57a2b6bbe4dbffeacd838503cd9c2ea4622079d32c7',
      fetchedAt: '2026-09-25T22:50:00Z',
      locator: 'Financial Highlights — Revenue and RPO bullets',
    },
  },
  {
    id: 'C29',
    title: 'CrowdStrike Q2 FY27 Results',
    organization: 'CrowdStrike',
    publicationDate: '2026-08-26',
    economicPeriod: 'Quarter ended 2026-07-31',
    canonicalUrl:
      'https://www.sec.gov/Archives/edgar/data/1535527/000153552726000029/crwd-20260826xex991.htm',
    excerpt:
      'Annual Recurring Revenue (ARR) grew 25% year-over-year to $5.84 billion as of July 31, 2026, of which $332.8 million was net new ARR added in the quarter.',
    sourceClass: 'FILING',
    interpretation: 'Continued platform-vendor re-acceleration; record net-new ARR in dollar terms.',
    limitations: 'This release does not restate a separate cloud-security-segment ARR figure; see C13 for that segment cut, last stated in Q4 FY2026.',
    conflictingEvidenceIds: ['C6a', 'C6b', 'D1'],
    artifactLabel: 'Scorecard refresh 2026-09-25 / C29',
    tags: ['security-vendor', 'secops', 'platform'],
    retrievedAt: '2026-09-25',
    retrieval: {
      finalUrl: 'https://www.sec.gov/Archives/edgar/data/1535527/000153552726000029/crwd-20260826xex991.htm',
      sha256: '505d3b329c0b4b8581c810a020227a340e3a6f5ff67be2fa2b24406023e95662',
      fetchedAt: '2026-09-25T22:55:00Z',
      locator: 'Financial Highlights — Annual Recurring Revenue bullet',
    },
  },
  {
    id: 'C30',
    title: 'SentinelOne Q2 FY27 Results',
    organization: 'SentinelOne',
    publicationDate: '2026-08-27',
    economicPeriod: 'Quarter ended 2026-07-31',
    canonicalUrl:
      'https://www.sec.gov/Archives/edgar/data/1583708/000158370826000052/sentineloneq227exhibit991.htm',
    excerpt:
      'Total revenue grew 21% to $292 million, compared to $242 million. Annualized recurring revenue (ARR) grew 22% to $1,218 million as of July 31, 2026.',
    sourceClass: 'FILING',
    interpretation: 'Endpoint/XDR re-acceleration continues; second consecutive strong quarter.',
    limitations: 'This release does not restate a separate net-new-ARR dollar or growth-rate figure the way the prior quarter did.',
    conflictingEvidenceIds: ['C6a', 'C6b', 'D1'],
    artifactLabel: 'Scorecard refresh 2026-09-25 / C30',
    tags: ['security-vendor', 'secops', 'endpoint'],
    retrievedAt: '2026-09-25',
    retrieval: {
      finalUrl: 'https://www.sec.gov/Archives/edgar/data/1583708/000158370826000052/sentineloneq227exhibit991.htm',
      sha256: '828c760f9ed86239221825cf0c60785e99540daa0696a1121aa66a054bfbde7a',
      fetchedAt: '2026-09-25T22:58:00Z',
      locator: 'Second Quarter Fiscal Year 2027 Highlights — revenue and ARR bullets',
    },
  },
  {
    id: 'C31',
    title: 'Rubrik Q2 FY27 Results',
    organization: 'Rubrik',
    publicationDate: '2026-08-27',
    economicPeriod: 'Quarter ended 2026-07-31',
    canonicalUrl:
      'https://www.sec.gov/Archives/edgar/data/1943896/000194389626000055/rubrikinc-991pressrelease7.htm',
    excerpt:
      'Subscription Annual Recurring Revenue (ARR): Subscription ARR grew 33% year-over-year to $1.66 billion as of July 31, 2026 with net new Subscription ARR up 35% year-over-year.',
    sourceClass: 'FILING',
    interpretation: 'Continued data-security acceleration.',
    limitations: 'Short public history and material-rights accounting.',
    conflictingEvidenceIds: [],
    artifactLabel: 'Scorecard refresh 2026-09-25 / C31',
    tags: ['security-vendor', 'data-security'],
    retrievedAt: '2026-09-25',
    retrieval: {
      finalUrl: 'https://www.sec.gov/Archives/edgar/data/1943896/000194389626000055/rubrikinc-991pressrelease7.htm',
      sha256: 'c14a3f117f685361cc0d91f774d5d338fa1c0b1c219c4008ee120372837f2119',
      fetchedAt: '2026-09-25T23:00:00Z',
      locator: 'Financial Highlights — Subscription ARR bullet',
    },
  },
  {
    id: 'C32',
    title: 'Netskope Q2 FY27 Results',
    organization: 'Netskope',
    publicationDate: '2026-09-02',
    economicPeriod: 'Quarter ended 2026-07-31',
    canonicalUrl:
      'https://www.sec.gov/Archives/edgar/data/2063196/000119312526380188/ntsk-ex99_1.htm',
    excerpt:
      'Annual Recurring Revenue (ARR): ARR grew 27% year-over-year to $899 million as of July 31, 2026. Revenue: Q2 revenue was $220.5 million, an increase of 29% year-over-year.',
    sourceClass: 'FILING',
    interpretation: 'Now a quarterly-reporting public company; supersedes the FY2026 annual print with a quarterly series aligned to the panel.',
    limitations: 'Second quarter as a public reporting company; short comparability history.',
    conflictingEvidenceIds: [],
    artifactLabel: 'Scorecard refresh 2026-09-25 / C32',
    tags: ['security-vendor', 'sase', 'network'],
    retrievedAt: '2026-09-25',
    retrieval: {
      finalUrl: 'https://www.sec.gov/Archives/edgar/data/2063196/000119312526380188/ntsk-ex99_1.htm',
      sha256: 'a5d2eb90e98aa3ce55b63aa64026bbd906f9afb658ae89f59d18288bcb5d72f3',
      fetchedAt: '2026-09-25T23:02:00Z',
      locator: 'Second Quarter Fiscal 2027 Financial Highlights — ARR and revenue bullets',
    },
  },
  {
    id: 'C33',
    title: 'SailPoint Q2 FY27 Results',
    organization: 'SailPoint',
    publicationDate: '2026-09-09',
    economicPeriod: 'Quarter ended 2026-07-31',
    canonicalUrl:
      'https://www.sec.gov/Archives/edgar/data/2030781/000162828026061015/sailpointinc-20260731x991x.htm',
    excerpt:
      'Total ARR was $1.231 billion, an increase of 25% year-over-year. SaaS ARR was $847 million, an increase of 36% year-over-year.',
    sourceClass: 'FILING',
    interpretation: 'Now a quarterly-reporting print aligned to the panel, superseding the FY2026 annual figure; IGA demand remains ahead of workforce-IAM (Okta).',
    limitations: 'Second consecutive quarterly print since the FY2026 annual figure; SaaS ARR mix continues shifting from term-license ARR.',
    conflictingEvidenceIds: ['C7'],
    artifactLabel: 'Scorecard refresh 2026-09-25 / C33',
    tags: ['security-vendor', 'identity', 'iga'],
    retrievedAt: '2026-09-25',
    retrieval: {
      finalUrl: 'https://www.sec.gov/Archives/edgar/data/2030781/000162828026061015/sailpointinc-20260731x991x.htm',
      sha256: '1f42b25769276b33bcfe8e30eb7c8cf4669b00b00a52d904c6971f086f48624b',
      fetchedAt: '2026-09-25T23:08:00Z',
      locator: 'Financial Highlights — ARR bullet',
    },
  },
  {
    id: 'C34',
    title: 'Check Point FY2025 Form 20-F — Lakera acquisition close',
    organization: 'Check Point Software Technologies Ltd.',
    publicationDate: '2026-03-31',
    economicPeriod: 'Acquisition closed 2025-10-22',
    canonicalUrl:
      'https://www.sec.gov/Archives/edgar/data/1015922/000117891326001932/zk2634942.htm',
    excerpt:
      'On October 22, 2025, the Company completed the acquisition of all outstanding shares of Lakera AI AG ("Lakera"), a privately-held Swiss company… The Company acquired Lakera for total consideration of approximately $201.8 [million].',
    sourceClass: 'FILING',
    interpretation: 'Confirms the Lakera deal closed (the card previously showed "agreement announced, expected to close Q4 2025") and discloses a purchase price not stated in the original 2025-09-16 announcement.',
    limitations: 'Purchase price is a preliminary allocation figure as reported in the annual filing; no separate standalone Lakera figure exists post-close.',
    conflictingEvidenceIds: [],
    artifactLabel: 'Scorecard refresh 2026-09-25 / C34',
    tags: ['security-vendor', 'ai-runtime', 'm-and-a'],
    retrievedAt: '2026-09-25',
    retrieval: {
      finalUrl: 'https://www.sec.gov/Archives/edgar/data/1015922/000117891326001932/zk2634942.htm',
      sha256: 'e5c66423cc59b916bdbcf8e95c789612fd6ce287756f6b4438128f3e48e3ca33',
      fetchedAt: '2026-09-25T23:12:00Z',
      locator: 'Note on business combinations — Lakera AI AG acquisition, consideration and closing date',
    },
  },
  {
    id: 'W36-01',
    title: 'Socure Series E funding announcement',
    organization: 'Return on Security',
    publicationDate: '2026-08-24',
    economicPeriod: 'Security, Funded #259 week',
    canonicalUrl: 'https://www.returnonsecurity.com/p/security-funded-259',
    excerpt:
      'Socure, a United States-based digital identity verification and fraud prevention platform, raised a $156.0M Series E from Summit Partners.',
    sourceClass: 'INDEPENDENT',
    interpretation: 'A large-dollar identity-fraud round in an otherwise thin funding week.',
    limitations: 'Aggregator-sourced round description; not the company’s own release.',
    conflictingEvidenceIds: [],
    artifactLabel: 'SEC-MARKET-ISSUE-001 / W36-01',
    tags: ['investment', 'identity', 'private'],
    retrievedAt: '2026-09-03',
    retrieval: { finalUrl: 'https://www.returnonsecurity.com/p/security-funded-259', sha256: '28ceedf3b9fd2795594b02e73401a4177f7d5cb2454eb4f28487ee83ce4dc05b', fetchedAt: '2026-09-04T16:31:56Z', locator: 'Security, Funded #259 — Product Companies list, Socure entry' },
  },
  {
    id: 'W36-02',
    title: 'KAZIMI Pre-Seed funding announcement',
    organization: 'Return on Security',
    publicationDate: '2026-08-24',
    economicPeriod: 'Security, Funded #259 week',
    canonicalUrl: 'https://www.returnonsecurity.com/p/security-funded-259',
    excerpt:
      'KAZIMI, a Germany-based anti-bot platform for mobile applications, raised a $2.6M Pre-Seed from Market One Capital.',
    sourceClass: 'INDEPENDENT',
    interpretation: 'Small early-stage formation in mobile anti-bot protection.',
    limitations: 'Aggregator-sourced round description; not the company’s own release.',
    conflictingEvidenceIds: [],
    artifactLabel: 'SEC-MARKET-ISSUE-001 / W36-02',
    tags: ['investment', 'private'],
    retrievedAt: '2026-09-03',
    retrieval: { finalUrl: 'https://www.returnonsecurity.com/p/security-funded-259', sha256: '28ceedf3b9fd2795594b02e73401a4177f7d5cb2454eb4f28487ee83ce4dc05b', fetchedAt: '2026-09-04T16:31:56Z', locator: 'Security, Funded #259 — Product Companies list, KAZIMI entry' },
  },
  {
    id: 'W36-03',
    title: 'CYBERA Venture Round funding announcement',
    organization: 'Return on Security',
    publicationDate: '2026-08-24',
    economicPeriod: 'Security, Funded #259 week',
    canonicalUrl: 'https://www.returnonsecurity.com/p/security-funded-259',
    excerpt:
      'CYBERA, a United States-based SD-WAN platform with integrated network security for distributed enterprises, raised a $2.5M Venture Round.',
    sourceClass: 'INDEPENDENT',
    interpretation: 'Small-dollar formation bet on network security bundled with SD-WAN.',
    limitations: 'Aggregator-sourced round description; not the company’s own release. Lead investor not disclosed.',
    conflictingEvidenceIds: [],
    artifactLabel: 'SEC-MARKET-ISSUE-001 / W36-03',
    tags: ['investment', 'network', 'private'],
    retrievedAt: '2026-09-03',
    retrieval: { finalUrl: 'https://www.returnonsecurity.com/p/security-funded-259', sha256: '28ceedf3b9fd2795594b02e73401a4177f7d5cb2454eb4f28487ee83ce4dc05b', fetchedAt: '2026-09-04T16:31:56Z', locator: 'Security, Funded #259 — Product Companies list, CYBERA entry' },
  },
  {
    id: 'W36-04',
    title: 'Opgate Pre-Seed funding announcement',
    organization: 'Return on Security',
    publicationDate: '2026-08-24',
    economicPeriod: 'Security, Funded #259 week',
    canonicalUrl: 'https://www.returnonsecurity.com/p/security-funded-259',
    excerpt:
      'Opgate, a United States-based runtime security and policy enforcement for AI agents, raised a $60.0K Pre-Seed.',
    sourceClass: 'INDEPENDENT',
    interpretation: 'Very small formation-stage capital in AI-agent runtime security.',
    limitations: 'Aggregator-sourced round description; not the company’s own release. Investor not disclosed.',
    conflictingEvidenceIds: [],
    artifactLabel: 'SEC-MARKET-ISSUE-001 / W36-04',
    tags: ['investment', 'ai-runtime', 'private'],
    retrievedAt: '2026-09-03',
    retrieval: { finalUrl: 'https://www.returnonsecurity.com/p/security-funded-259', sha256: '28ceedf3b9fd2795594b02e73401a4177f7d5cb2454eb4f28487ee83ce4dc05b', fetchedAt: '2026-09-04T16:31:56Z', locator: 'Security, Funded #259 — Product Companies list, Opgate entry' },
  },
  {
    id: 'W36-05',
    title: 'DetectifAI Seed funding announcement',
    organization: 'Return on Security',
    publicationDate: '2026-08-24',
    economicPeriod: 'Security, Funded #259 week',
    canonicalUrl: 'https://www.returnonsecurity.com/p/security-funded-259',
    excerpt:
      'DetectifAI, a United States-based AI deepfake voice detection platform, raised an undisclosed Seed round from Josh Constine and Manohar Kamath.',
    sourceClass: 'INDEPENDENT',
    interpretation: 'Small angel-backed formation round in deepfake voice detection.',
    limitations: 'Aggregator-sourced round description; not the company’s own release. Round size undisclosed.',
    conflictingEvidenceIds: [],
    artifactLabel: 'SEC-MARKET-ISSUE-001 / W36-05',
    tags: ['investment', 'private'],
    retrievedAt: '2026-09-03',
    retrieval: { finalUrl: 'https://www.returnonsecurity.com/p/security-funded-259', sha256: '28ceedf3b9fd2795594b02e73401a4177f7d5cb2454eb4f28487ee83ce4dc05b', fetchedAt: '2026-09-04T16:31:56Z', locator: 'Security, Funded #259 — Product Companies list, DetectifAI entry' },
  },
  {
    id: 'W36-06',
    title: 'HiddenLayer Series B funding announcement',
    organization: 'HiddenLayer',
    publicationDate: '2026-09-03',
    economicPeriod: 'Series B close',
    canonicalUrl: 'https://www.securityweek.com/hiddenlayer-raises-100-million-for-ai-runtime-security/',
    excerpt:
      'AI security company HiddenLayer on Wednesday announced raising $100 million in a Series B funding round that brings the total raised by the company to over $155 million.',
    sourceClass: 'INDEPENDENT',
    interpretation: 'A large, well-syndicated round for AI runtime security, the biggest formation print this window.',
    limitations: 'Reported via SecurityWeek, not the company’s own release page.',
    conflictingEvidenceIds: [],
    artifactLabel: 'SEC-MARKET-ISSUE-001 / W36-06',
    tags: ['investment', 'ai-runtime', 'private'],
    retrievedAt: '2026-09-03',
    retrieval: { finalUrl: 'https://www.securityweek.com/hiddenlayer-raises-100-million-for-ai-runtime-security/', sha256: '438ad41abf3a8f71c3c5926a77f5aa7a0ea9da6fd3a572fbe43d87e73d7634f0', fetchedAt: '2026-09-05T03:14:47Z', locator: 'Article body, opening paragraph' },
  },
  {
    id: 'W36-07',
    title: 'AIR Security stealth-exit funding announcement',
    organization: 'AIR Security',
    publicationDate: '2026-09-03',
    economicPeriod: 'Stealth-exit funding close',
    canonicalUrl:
      'https://www.securityweek.com/ai-agent-firewall-startup-air-security-emerges-from-stealth-with-50-million/',
    excerpt:
      'AIR Security is emerging from stealth with $50 million funding...led by Sequoia Capital and Greenoaks together with...prominent individual industry angels.',
    sourceClass: 'INDEPENDENT',
    interpretation: 'A second large AI-agent-security formation round the same week as HiddenLayer.',
    limitations: 'Reported via SecurityWeek, not the company’s own release page.',
    conflictingEvidenceIds: [],
    artifactLabel: 'SEC-MARKET-ISSUE-001 / W36-07',
    tags: ['investment', 'ai-runtime', 'private'],
    retrievedAt: '2026-09-03',
    retrieval: { finalUrl: 'https://www.securityweek.com/ai-agent-firewall-startup-air-security-emerges-from-stealth-with-50-million/', sha256: '49ba1583879378c9799ea3856cb0e20d375730e24c3890b26ce89f044f845cc7', fetchedAt: '2026-09-04T16:31:56Z', locator: 'Article body, funding paragraph' },
  },
  {
    id: 'W36-08',
    title: 'Palo Alto Networks reported acquisition of Console',
    organization: 'Palo Alto Networks / TechCrunch',
    publicationDate: '2026-09-02',
    economicPeriod: 'Deal reported, not confirmed by acquirer',
    canonicalUrl:
      'https://techcrunch.com/2026/09/02/palo-alto-networks-paid-500m-for-thrive-backed-console-sources-say/',
    excerpt:
      'Palo Alto Networks paid $500 million in cash and stock to acquire Console, a two-year-old startup that uses AI agents to automate routine IT help desk tasks.',
    sourceClass: 'INDEPENDENT',
    interpretation: 'The week’s largest reported M&A figure, but sourced only to unnamed people familiar with the deal.',
    limitations:
      'Press-sourced and unconfirmed by the acquirer. Palo Alto’s own press page did not surface a matching release; the figure is carried at reported, not confirmed, confidence.',
    conflictingEvidenceIds: [],
    artifactLabel: 'SEC-MARKET-ISSUE-001 / W36-08',
    tags: ['investment', 'm-and-a'],
    retrievedAt: '2026-09-03',
    retrieval: { finalUrl: 'https://techcrunch.com/2026/09/02/palo-alto-networks-paid-500m-for-thrive-backed-console-sources-say/', sha256: 'c7448145fa3a830cae2d434b65b236dc7fe61bd2f8ba54b21062d2faafc54151', fetchedAt: '2026-09-04T16:31:56Z', locator: 'Article body, opening paragraph' },
  },
  {
    id: 'W36-09',
    title: 'ePlus acquisition of Daymark Solutions',
    organization: 'Return on Security',
    publicationDate: '2026-08-24',
    economicPeriod: 'Security, Funded #259 week',
    canonicalUrl: 'https://www.returnonsecurity.com/p/security-funded-259',
    excerpt: 'Daymark Solutions was acquired by ePlus for an undisclosed amount.',
    sourceClass: 'INDEPENDENT',
    interpretation: 'A quiet, undisclosed-value tuck-in acquisition.',
    limitations: 'Aggregator-sourced description; deal value not disclosed.',
    conflictingEvidenceIds: [],
    artifactLabel: 'SEC-MARKET-ISSUE-001 / W36-09',
    tags: ['investment', 'm-and-a'],
    retrievedAt: '2026-09-03',
    retrieval: { finalUrl: 'https://www.returnonsecurity.com/p/security-funded-259', sha256: '28ceedf3b9fd2795594b02e73401a4177f7d5cb2454eb4f28487ee83ce4dc05b', fetchedAt: '2026-09-04T16:31:56Z', locator: 'Security, Funded #259 — M&A list, ePlus / Daymark Solutions entry' },
  },
  {
    id: 'W36-10',
    title: 'Echo acquisition of Minimus (formerly Gutsy)',
    organization: 'Return on Security',
    publicationDate: '2026-08-24',
    economicPeriod: 'Security, Funded #259 week',
    canonicalUrl: 'https://www.returnonsecurity.com/p/security-funded-259',
    excerpt:
      'Minimus (formerly Gutsy) and there assets thereof, an Israel-based secure-by-design container image company, was acquired by Echo for an undisclosed amount.',
    sourceClass: 'INDEPENDENT',
    interpretation: 'A quiet, undisclosed-value container-security tuck-in.',
    limitations: 'Aggregator-sourced description; deal value not disclosed.',
    conflictingEvidenceIds: [],
    artifactLabel: 'SEC-MARKET-ISSUE-001 / W36-10',
    tags: ['investment', 'cloud-security', 'm-and-a'],
    retrievedAt: '2026-09-03',
    retrieval: { finalUrl: 'https://www.returnonsecurity.com/p/security-funded-259', sha256: 'ec12cebefd1811fd7d105e98083244748680e209bad69180e22bdf3eb69200bd', fetchedAt: '2026-09-05T03:14:47Z', locator: 'Security, Funded #259 — M&A list, Echo / Minimus entry' },
  },
  {
    id: 'W36-11',
    title: 'Ampcus acquisition of smarterd',
    organization: 'Return on Security',
    publicationDate: '2026-08-24',
    economicPeriod: 'Security, Funded #259 week',
    canonicalUrl: 'https://www.returnonsecurity.com/p/security-funded-259',
    excerpt:
      'smarterd, a United States-based IT asset management and risk prioritization platform, was acquired by Ampcus for an undisclosed amount.',
    sourceClass: 'INDEPENDENT',
    interpretation: 'A quiet, undisclosed-value IT asset management tuck-in.',
    limitations: 'Aggregator-sourced description; deal value not disclosed.',
    conflictingEvidenceIds: [],
    artifactLabel: 'SEC-MARKET-ISSUE-001 / W36-11',
    tags: ['investment', 'm-and-a'],
    retrievedAt: '2026-09-03',
    retrieval: { finalUrl: 'https://www.returnonsecurity.com/p/security-funded-259', sha256: '28ceedf3b9fd2795594b02e73401a4177f7d5cb2454eb4f28487ee83ce4dc05b', fetchedAt: '2026-09-04T16:31:56Z', locator: 'Security, Funded #259 — M&A list, Ampcus / smarterd entry' },
  },
  {
    id: 'W36-12',
    title: "Trace3 acquisition of Calian's U.S. Commercial IT Business",
    organization: 'Return on Security',
    publicationDate: '2026-08-24',
    economicPeriod: 'Security, Funded #259 week',
    canonicalUrl: 'https://www.returnonsecurity.com/p/security-funded-259',
    excerpt:
      "Calian's U.S. Commercial IT Business, a United States-based managed security services provider (MSSP), was acquired by Trace3 for an undisclosed amount.",
    sourceClass: 'INDEPENDENT',
    interpretation: 'A quiet, undisclosed-value MSSP consolidation.',
    limitations: 'Aggregator-sourced description; deal value not disclosed.',
    conflictingEvidenceIds: [],
    artifactLabel: 'SEC-MARKET-ISSUE-001 / W36-12',
    tags: ['investment', 'secops', 'm-and-a'],
    retrievedAt: '2026-09-03',
    retrieval: { finalUrl: 'https://www.returnonsecurity.com/p/security-funded-259', sha256: '28ceedf3b9fd2795594b02e73401a4177f7d5cb2454eb4f28487ee83ce4dc05b', fetchedAt: '2026-09-04T16:31:56Z', locator: 'Security, Funded #259 — M&A list, Trace3 / Calian\'s U.S. Commercial IT Business entry' },
  },
  {
    id: 'W36-13',
    title: 'Integrity360 acquisition of CyberIAM',
    organization: 'Return on Security',
    publicationDate: '2026-08-24',
    economicPeriod: 'Security, Funded #259 week',
    canonicalUrl: 'https://www.returnonsecurity.com/p/security-funded-259',
    excerpt:
      'CyberIAM, a United Kingdom-based professional services firm focused on Identity and Access Management (IAM) consulting, was acquired by Integrity360 for an undisclosed amount.',
    sourceClass: 'INDEPENDENT',
    interpretation: 'A quiet, undisclosed-value IAM consulting consolidation.',
    limitations: 'Aggregator-sourced description; deal value not disclosed.',
    conflictingEvidenceIds: [],
    artifactLabel: 'SEC-MARKET-ISSUE-001 / W36-13',
    tags: ['investment', 'identity', 'm-and-a'],
    retrievedAt: '2026-09-03',
    retrieval: { finalUrl: 'https://www.returnonsecurity.com/p/security-funded-259', sha256: '28ceedf3b9fd2795594b02e73401a4177f7d5cb2454eb4f28487ee83ce4dc05b', fetchedAt: '2026-09-04T16:31:56Z', locator: 'Security, Funded #259 — M&A list, Integrity360 / CyberIAM entry' },
  },
  {
    id: 'W36-14',
    title: 'CrowdStrike Q2 FY2027 Financial Results',
    organization: 'CrowdStrike',
    publicationDate: '2026-08-26',
    economicPeriod: 'Quarter ended 2026-07-31',
    canonicalUrl:
      'https://www.sec.gov/Archives/edgar/data/1535527/000153552726000029/crwd-20260826xex991.htm',
    excerpt:
      'Total revenue was $1.47 billion, a 26% increase, compared to $1.17 billion in the second quarter of fiscal 2026. / Delivers record net new ARR of $333 million, accelerates growth to 51% year-over-year',
    sourceClass: 'FILING',
    interpretation: 'A strong beat with accelerating net-new ARR, consistent with the standing infra-to-security lag call.',
    limitations: 'Total-company revenue and ARR; not a single-product or single-domain series.',
    conflictingEvidenceIds: [],
    artifactLabel: 'SEC-MARKET-ISSUE-001 / W36-14',
    tags: ['security-vendor', 'secops', 'public'],
    retrievedAt: '2026-09-03',
    retrieval: { finalUrl: 'https://www.sec.gov/Archives/edgar/data/1535527/000153552726000029/crwd-20260826xex991.htm', sha256: '55bfc3ec3d51b325dcc39a3b1d23a2ef7a56d9b9d216c456a3d39b50083fdfcb', fetchedAt: '2026-09-04T16:31:56Z', locator: 'EX-99.1, revenue and net-new-ARR paragraph' },
  },
  {
    id: 'W36-15',
    title: 'Zscaler Announces Strong Fourth Quarter and Fiscal 2026 Financial Results',
    organization: 'Zscaler',
    publicationDate: '2026-09-03',
    economicPeriod: 'Quarter ended 2026-07-31',
    canonicalUrl:
      'https://www.sec.gov/Archives/edgar/data/1713683/000171368326000156/zs-07312026_991.htm',
    excerpt:
      'Revenue: Grew 25% year over year to $898.2 million. / ARR: Grew 25% year over year to $3,771 million, of which $246 million was net new ARR during the fourth quarter of fiscal 2026.',
    sourceClass: 'FILING',
    interpretation: 'Steady growth at scale for the public SSE/SASE bellwether.',
    limitations: 'Total-company revenue and ARR; not a single-product or single-domain series.',
    conflictingEvidenceIds: [],
    artifactLabel: 'SEC-MARKET-ISSUE-001 / W36-15',
    tags: ['security-vendor', 'sase', 'network'],
    retrievedAt: '2026-09-03',
    retrieval: { finalUrl: 'https://www.sec.gov/Archives/edgar/data/1713683/000171368326000156/zs-07312026_991.htm', sha256: '1d2e6e883821e405ca08482d7e381b7f979a9337ecc564cca19e6ab347519173', fetchedAt: '2026-09-04T16:31:56Z', locator: 'EX-99.1, revenue and ARR bullet points' },
  },
  {
    id: 'W36-16',
    title: 'SentinelOne Announces Second Quarter Fiscal Year 2027 Financial Results',
    organization: 'SentinelOne',
    publicationDate: '2026-08-27',
    economicPeriod: 'Quarter ended 2026-07-31',
    canonicalUrl:
      'https://www.sec.gov/Archives/edgar/data/1583708/000158370826000052/sentineloneq227exhibit991.htm',
    excerpt:
      'Total revenue grew 21% to $292 million, compared to $242 million. / Annualized recurring revenue (ARR) grew 22% to $1,218 million as of July 31, 2026.',
    sourceClass: 'FILING',
    interpretation: 'Steady growth as SentinelOne’s platform consolidation continues.',
    limitations: 'Total-company revenue and ARR; not a single-product or single-domain series.',
    conflictingEvidenceIds: [],
    artifactLabel: 'SEC-MARKET-ISSUE-001 / W36-16',
    tags: ['security-vendor', 'secops', 'public'],
    retrievedAt: '2026-09-03',
    retrieval: { finalUrl: 'https://www.sec.gov/Archives/edgar/data/1583708/000158370826000052/sentineloneq227exhibit991.htm', sha256: 'cf829186ef50df7c177000aabef60335accb235ba439671e93f91ee5292c8293', fetchedAt: '2026-09-04T16:31:56Z', locator: 'EX-99.1, revenue and ARR paragraph' },
  },
  {
    id: 'W36-17',
    title: 'Okta Announces Second Quarter Fiscal Year 2027 Financial Results',
    organization: 'Okta',
    publicationDate: '2026-08-26',
    economicPeriod: 'Quarter ended 2026-07-31',
    canonicalUrl:
      'https://www.sec.gov/Archives/edgar/data/1660134/000166013426000068/okta-7312026_ex991.htm',
    excerpt:
      'Revenue: Total revenue was $805 million, an increase of 11% year-over-year. Subscription revenue was $793 million, an increase of 12% year-over-year.',
    sourceClass: 'FILING',
    interpretation: 'Steady, unremarkable growth for the public identity bellwether.',
    limitations: 'Total-company revenue; not a single-product or single-domain series.',
    conflictingEvidenceIds: [],
    artifactLabel: 'SEC-MARKET-ISSUE-001 / W36-17',
    tags: ['security-vendor', 'identity', 'public'],
    retrievedAt: '2026-09-03',
    retrieval: { finalUrl: 'https://www.sec.gov/Archives/edgar/data/1660134/000166013426000068/okta-7312026_ex991.htm', sha256: '5547ef7e7f3aaf24bfa43c8b795b8a9316aea034dd3d9e0af0461e999a6ca067', fetchedAt: '2026-09-04T16:31:56Z', locator: 'EX-99.1, revenue paragraph' },
  },
  {
    id: 'W36-18',
    title: 'Rubrik Reports Second Quarter Fiscal Year 2027 Financial Results',
    organization: 'Rubrik',
    publicationDate: '2026-08-27',
    economicPeriod: 'Quarter ended 2026-07-31',
    canonicalUrl:
      'https://www.sec.gov/Archives/edgar/data/1943896/000194389626000055/rubrikinc-991pressrelease7.htm',
    excerpt:
      'Second quarter subscription ARR grew 33% year-over-year to $1.66 billion. / Second quarter revenue grew 38% year-over-year to $427.3 million.',
    sourceClass: 'FILING',
    interpretation: 'Accelerating growth for the public data-security bellwether.',
    limitations: 'Total-company revenue and ARR; not a single-product or single-domain series.',
    conflictingEvidenceIds: [],
    artifactLabel: 'SEC-MARKET-ISSUE-001 / W36-18',
    tags: ['security-vendor', 'data-security', 'public'],
    retrievedAt: '2026-09-03',
    retrieval: { finalUrl: 'https://www.sec.gov/Archives/edgar/data/1943896/000194389626000055/rubrikinc-991pressrelease7.htm', sha256: 'dde91722cd830efaee460a4e01ad8a76e5f5d7083fafddbb630895fc4c99c9d6', fetchedAt: '2026-09-04T16:31:56Z', locator: 'EX-99.1, headline metrics bullets' },
  },
  {
    id: 'W36-19',
    title: 'Palo Alto Networks Reports Fiscal Fourth Quarter and Fiscal Year 2026 Financial Results',
    organization: 'Palo Alto Networks',
    publicationDate: '2026-09-01',
    economicPeriod: 'Quarter ended 2026-07-31',
    canonicalUrl:
      'https://www.sec.gov/Archives/edgar/data/1327567/000132756726000019/ex991q426earningsrelease.htm',
    excerpt:
      'Total revenue for the fiscal fourth quarter 2026 grew 34% year over year to $3.41 billion. / Next-Generation Security ARR for the fiscal fourth quarter 2026 grew 63% year over year to $9.10 billion.',
    sourceClass: 'FILING',
    interpretation: 'A strong beat with accelerating Next-Gen Security ARR, the fastest growth rate of this window’s prints.',
    limitations: 'Total-company revenue and a company-defined ARR segment; spans multiple domains, not a single-domain series.',
    conflictingEvidenceIds: [],
    artifactLabel: 'SEC-MARKET-ISSUE-001 / W36-19',
    tags: ['security-vendor', 'public'],
    retrievedAt: '2026-09-03',
    retrieval: { finalUrl: 'https://www.sec.gov/Archives/edgar/data/1327567/000132756726000019/ex991q426earningsrelease.htm', sha256: '4743aea7568eeff9b80a62b14f8fafb6018a085e876e77bf198642ab8b4c8aed', fetchedAt: '2026-09-04T16:31:56Z', locator: 'EX-99.1, revenue and Next-Generation Security ARR paragraph' },
  },
  {
    id: 'W36-20',
    title: 'Broadcom Inc. Announces Third Quarter Fiscal Year 2026 Financial Results and Quarterly Dividend',
    organization: 'Broadcom',
    publicationDate: '2026-09-02',
    economicPeriod: 'Quarter ended 2026-08-02',
    canonicalUrl:
      'https://www.sec.gov/Archives/edgar/data/1730168/000173016826000076/avgo-08022026x8kxex99.htm',
    excerpt:
      'Revenue of $29.6 billion for the third quarter, up 86 percent from the prior year period / Q3 AI semiconductor revenue of $16.7 billion grew 221% year-over-year, and 54% quarter-over-quarter, said Hock Tan.',
    sourceClass: 'FILING',
    interpretation: 'AI-semiconductor demand remains the dominant infrastructure impulse this window.',
    limitations: 'Semiconductor and infrastructure supplier, not a security vendor; total-company revenue.',
    conflictingEvidenceIds: [],
    artifactLabel: 'SEC-MARKET-ISSUE-001 / W36-20',
    tags: ['infrastructure', 'supplier', 'semiconductor'],
    retrievedAt: '2026-09-03',
    retrieval: { finalUrl: 'https://www.sec.gov/Archives/edgar/data/1730168/000173016826000076/avgo-08022026x8kxex99.htm', sha256: 'cce08d125724af16210eb7480ea5486a145ffc44ba66f5e25b8311158fa3b07b', fetchedAt: '2026-09-04T16:31:56Z', locator: 'EX-99, CEO Hock Tan quote paragraph' },
  },
  {
    id: 'W36-21',
    title: 'Nutanix Reports Fourth Quarter and Fiscal 2026 Financial Results',
    organization: 'Nutanix',
    publicationDate: '2026-08-26',
    economicPeriod: 'Quarter ended 2026-07-31',
    canonicalUrl: 'https://www.sec.gov/Archives/edgar/data/1618732/000117184326005752/exh_991.htm',
    excerpt:
      'Annual Recurring Revenue (ARR)... $2.55 billion... 16% / Revenue $757.1 million $653.3 million 16%',
    sourceClass: 'FILING',
    interpretation: 'Steady infrastructure-layer growth alongside this window’s security-vendor prints.',
    limitations: 'Infrastructure (HCI) vendor, not a security vendor; total-company revenue.',
    conflictingEvidenceIds: [],
    artifactLabel: 'SEC-MARKET-ISSUE-001 / W36-21',
    tags: ['infrastructure', 'supplier', 'compute'],
    retrievedAt: '2026-09-03',
    retrieval: { finalUrl: 'https://www.sec.gov/Archives/edgar/data/1618732/000117184326005752/exh_991.htm', sha256: '58493df53fa2b319caff903723e73d2146a9cc1455644801bbb48e70e9b607a5', fetchedAt: '2026-09-04T16:31:56Z', locator: 'EX-99.1, headline metrics table' },
  },
  {
    id: 'W36-22',
    title: 'NVIDIA Announces Financial Results for Second Quarter Fiscal 2027',
    organization: 'NVIDIA',
    publicationDate: '2026-08-26',
    economicPeriod: 'Quarter ended 2026-07-26',
    canonicalUrl: 'https://www.sec.gov/Archives/edgar/data/1045810/000104581026000073/q2fy27pr.htm',
    excerpt:
      'Revenue of $96.2 billion, up 106% from a year ago / Data Center revenue of $89.0 billion, up 117% from a year ago',
    sourceClass: 'FILING',
    interpretation: 'Compute demand keeps accelerating; the infrastructure impulse this call is measured against.',
    limitations: 'Data Center includes non-GenAI workloads; not a deployed-workload measure.',
    conflictingEvidenceIds: [],
    artifactLabel: 'SEC-MARKET-ISSUE-001 / W36-22',
    tags: ['infrastructure', 'supplier', 'compute'],
    retrievedAt: '2026-09-03',
    retrieval: { finalUrl: 'https://www.sec.gov/Archives/edgar/data/1045810/000104581026000073/q2fy27pr.htm', sha256: '1809cb206590dcfeb959f3a1a64157f4e5ee42788ec51289b74f3ea299931eb7', fetchedAt: '2026-09-04T16:31:56Z', locator: 'EX-99.1, revenue and Data Center revenue bullets' },
  },
  {
    id: 'W36-23',
    title: 'FY27 Segments and Investor Metrics — September 2026',
    organization: 'Microsoft',
    publicationDate: '2026-09-02',
    economicPeriod: 'FY2027 capex outlook',
    canonicalUrl:
      'https://www.sec.gov/Archives/edgar/data/789019/000119312526380280/d291965dex991.htm',
    excerpt:
      'Capital expenditures Expected to be over $50 billion including the impact of the useful life update',
    sourceClass: 'FILING',
    interpretation: 'A new infrastructure-buildout data point measured against the standing infra-to-security lag call.',
    limitations: 'A single-quarter capex guide, not a security-specific figure.',
    conflictingEvidenceIds: [],
    artifactLabel: 'SEC-MARKET-ISSUE-001 / W36-23',
    tags: ['infrastructure', 'supplier', 'compute'],
    retrievedAt: '2026-09-03',
    retrieval: { finalUrl: 'https://www.sec.gov/Archives/edgar/data/789019/000119312526380280/d291965dex991.htm', sha256: '557161af7ac2f2eed02c2ad77b8d5e1e21acd35173e46519981ad85d28a15be5', fetchedAt: '2026-09-04T16:31:56Z', locator: 'EX-99.1, capital expenditures guidance line' },
  },
{
  "id": "TR-abnormal-1",
  "title": "Abnormal Security Series D Funding",
  "organization": "Abnormal Security",
  "publicationDate": "2024-08-06",
  "economicPeriod": "August 2024",
  "canonicalUrl": "https://abnormal.ai/newsroom/press-releases/series-d-5b-valuation",
  "excerpt": "Series D: $250 million at $5.1 billion post-money valuation, led by Wellington Management.",
  "sourceClass": "IR",
  "interpretation": "",
  "limitations": "",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-abnormal-1",
  "tags": [
    "tracker",
    "email"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-abnormal-2",
  "title": "Abnormal Security ARR and Growth",
  "organization": "Abnormal Security",
  "publicationDate": "2024-08-06",
  "economicPeriod": "August 2024",
  "canonicalUrl": "https://abnormal.ai/newsroom/press-releases/series-d-5b-valuation",
  "excerpt": "Over $200 million ARR with 100%+ YoY growth.",
  "sourceClass": "IR",
  "interpretation": "",
  "limitations": "No later ARR figure found through September 2026.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-abnormal-2",
  "tags": [
    "tracker",
    "email"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-aqua-2",
  "title": "Aqua Security Leadership Transition",
  "organization": "Aqua Security",
  "publicationDate": "2025-11-05",
  "economicPeriod": "November 2025",
  "canonicalUrl": "https://www.aquasec.com/news/aqua-security-announces-leadership-transition-as-company-enters-its-next-phase-of-growth/",
  "excerpt": "Co-founder/CEO Dror Davidoff and co-founder/CTO Amir Jerbi stepped back to strategic advisors. Mike Dube became CEO; Nir Makowski became Chief Product & Technology Officer.",
  "sourceClass": "IR",
  "interpretation": "",
  "limitations": "",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-aqua-2",
  "tags": [
    "tracker",
    "cloud"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-aqua-3",
  "title": "About Us — Aqua Security",
  "organization": "Aqua Security",
  "publicationDate": "2026-09-30",
  "economicPeriod": "N/A (company background)",
  "canonicalUrl": "https://www.aquasec.com/about-us/",
  "excerpt": "Founded in 2015, Aqua is headquartered in Boston and Ramat Gan, Israel, and protects more than 500 of the world's largest enterprises. Investors include Shlomo Kramer (co-founder of Check Point and Imperva), TLV Partners, Lightspeed Venture Partners, Insight Partners, StepStone Group, and ION Crossover Partners.",
  "sourceClass": "OFFICIAL",
  "interpretation": "",
  "limitations": "The page names investors but does not disclose a funding round amount, date, or valuation; see TR-aqua-4 for the dated Series E figure found on PR Newswire.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-aqua-3",
  "tags": [
    "tracker",
    "cloud"
  ],
  "retrievedAt": "2026-09-30"
},
{
  "id": "TR-aqua-4",
  "title": "Aqua Security Announces $135 Million in Series E Funding at a $1 Billion Valuation",
  "organization": "Aqua Security",
  "publicationDate": "2021-03-10",
  "economicPeriod": "N/A (funding announcement)",
  "canonicalUrl": "https://www.prnewswire.com/news-releases/aqua-security-announces-135-million-in-series-e-funding-at-a-1-billion-valuation-301243855.html",
  "excerpt": "Aqua Security...announced today the completion of $135 Million in Series E funding led by ION Crossover Partners, putting Aqua's valuation in excess of $1 Billion.",
  "sourceClass": "IR",
  "interpretation": "",
  "limitations": "AUTO-001 fix pass 4, item 1/8: the tracker previously had no lastRound field for Aqua at all. Checked Aqua's own newsroom (aquasec.com/news/) and its PR Newswire release list; no funding round or ownership change newer than this one was found as of 2026-09-30.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-aqua-4",
  "tags": [
    "tracker",
    "cloud"
  ],
  "retrievedAt": "2026-09-30",
  "retrieval": {
    "finalUrl": "https://www.prnewswire.com/news-releases/aqua-security-announces-135-million-in-series-e-funding-at-a-1-billion-valuation-301243855.html",
    "sha256": "a778adbb87264a3e1a5850a2cea3cd9d66b54d655a64c3a94b2cbc4b5f890231",
    "fetchedAt": "2026-09-30T00:00:00Z",
    "locator": "First paragraph"
  }
},
{
  "id": "TR-armis-1",
  "title": "ServiceNow Announces First Quarter Fiscal 2026 Financial Results",
  "organization": "ServiceNow, Inc.",
  "publicationDate": "2026-04-22",
  "economicPeriod": "Q1 FY2026",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/1373715/000137371526000054/erq1fy26.htm",
  "excerpt": "'ServiceNow closed its acquisition of Armis on April 20, 2026.' Armis is expected to contribute approximately 125 basis points to Q2/FY2026 subscription revenue growth, with integration headwinds of approximately 25 basis points to subscription gross margin, 75 basis points to operating margin, and 200 basis points to free cash flow margin.",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "Company-reported disclosure, filed as an exhibit to an SEC Form 8-K. No standalone Armis dollar revenue figure is disclosed.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-armis-1",
  "tags": [
    "tracker",
    "ot-iot"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-axonius-1",
  "title": "Axonius ARR Milestone",
  "organization": "Axonius, Inc.",
  "publicationDate": "2026-05-19",
  "economicPeriod": "May 2026",
  "canonicalUrl": "https://www.axonius.com/newsroom/press-release/axonius-surpasses-200m-arr-appoints-joe-diamond-ceo",
  "excerpt": "Axonius reported ARR exceeding $200 million in Q1 of fiscal 2027, with company stating 100% growth in the preceding two years.",
  "sourceClass": "OFFICIAL",
  "interpretation": "",
  "limitations": "Single-year growth rate not provided by the company; stated as 100% over two years.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-axonius-1",
  "tags": [
    "tracker",
    "exposure"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-axonius-2",
  "title": "Axonius Names Joe Diamond CEO",
  "organization": "Axonius, Inc.",
  "publicationDate": "2026-05-19",
  "economicPeriod": "May 2026",
  "canonicalUrl": "https://www.axonius.com/newsroom/press-release/axonius-surpasses-200m-arr-appoints-joe-diamond-ceo",
  "excerpt": "Axonius appointed Joe Diamond as permanent CEO following his interim role since February 2026. Co-founder Dean Sysman moved to executive chairman.",
  "sourceClass": "OFFICIAL",
  "interpretation": "",
  "limitations": "",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-axonius-2",
  "tags": [
    "tracker",
    "exposure"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-axonius-3",
  "title": "Axonius Closes $200M Series E Funding Round",
  "organization": "Axonius, Inc.",
  "publicationDate": "2022-03-08",
  "economicPeriod": "N/A (funding announcement)",
  "canonicalUrl": "https://www.axonius.com/newsroom/press-release/axonius-closes-200m-series-e-funding-round",
  "excerpt": "Axonius today announced it has closed $200 million in Series E funding, led by Accel, at a valuation of $2.6 billion.",
  "sourceClass": "OFFICIAL",
  "interpretation": "",
  "limitations": "AUTO-001 fix pass 4, item 1: the tracker previously had no lastRound field for Axonius at all.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-axonius-3",
  "tags": [
    "tracker",
    "exposure"
  ],
  "retrievedAt": "2026-09-30"
},
{
  "id": "TR-barracuda-1",
  "title": "Barracuda KKR Acquisition Completion",
  "organization": "Barracuda Networks, Inc.",
  "publicationDate": "2022-08",
  "economicPeriod": "August 2022",
  "canonicalUrl": "https://www.barracuda.com/company/news",
  "excerpt": "KKR acquired from Thoma Bravo, closed August 2022 at approximately $4 billion.",
  "sourceClass": "IR",
  "interpretation": "",
  "limitations": "",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-barracuda-1",
  "tags": [
    "tracker",
    "email"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-beyondtrust-1",
  "title": "BeyondTrust Completes Transaction with Clearlake Capital and Francisco Partners",
  "organization": "BeyondTrust",
  "publicationDate": "2021-08-17",
  "economicPeriod": "N/A (ownership announcement)",
  "canonicalUrl": "https://www.globenewswire.com/news-release/2021/08/17/2282045/0/en/BeyondTrust-Completes-Transaction-with-Clearlake-Capital-and-Francisco-Partners.html",
  "excerpt": "Clearlake joins existing investor Francisco Partners, a leading global investment firm that specializes in partnering with technology businesses, which acquired BeyondTrust in 2018.",
  "sourceClass": "IR",
  "interpretation": "",
  "limitations": "AUTO-001 fix pass 4, item 8: the tracker previously had no ownership field for BeyondTrust at all.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-beyondtrust-1",
  "tags": [
    "tracker",
    "identity"
  ],
  "retrievedAt": "2026-09-30"
},
{
  "id": "TR-bigid-1",
  "title": "BigID funding and investors summary",
  "organization": "Tracxn",
  "publicationDate": "2024-03-01",
  "economicPeriod": "N/A (funding history aggregator)",
  "canonicalUrl": "https://tracxn.com/d/companies/bigid/__pHSLjAzI2aqF63ud9QosF69usdaBPTT49_kou_rHtgw/funding-and-investors",
  "excerpt": "$60 million growth round led by Riverwood Capital, with Silver Lake Waterman and Advent International participating, at a $1 billion valuation, March 2024.",
  "sourceClass": "INDEPENDENT",
  "interpretation": "",
  "limitations": "Third-party funding aggregator, not a BigID or Riverwood Capital press release directly reached this pass.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-bigid-1",
  "tags": [
    "tracker",
    "data"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-cato-1",
  "title": "Cato Networks Series G Funding Announcement",
  "organization": "Cato Networks",
  "publicationDate": "2025-06-30",
  "economicPeriod": "June 2025",
  "canonicalUrl": "https://www.prnewswire.com/news-releases/cato-networks-raises-359-million-at-a-valuation-of-more-than-4-8-billion-302494283.html",
  "excerpt": "Series G: $359 million initial close led by Vitruvian Partners and ION Crossover Partners, with ~$50 million extension, at valuation over $4.8 billion.",
  "sourceClass": "IR",
  "interpretation": "",
  "limitations": "",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-cato-1",
  "tags": [
    "tracker",
    "network-sase"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-cato-2",
  "title": "Cato Networks FY2025 ARR Milestone",
  "organization": "Cato Networks",
  "publicationDate": "2026-02-24",
  "economicPeriod": "Full year 2025",
  "canonicalUrl": "https://www.prnewswire.com/il/news-releases/cato-networks-surpasses-350-million-arr-with-43-yoy-growth-in-2025-302694952.html",
  "excerpt": "ARR surpassed $350 million, +43% YoY, for full year 2025.",
  "sourceClass": "IR",
  "interpretation": "",
  "limitations": "",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-cato-2",
  "tags": [
    "tracker",
    "network-sase"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-cato-3",
  "title": "Cato Networks Exceeds $415M in ARR Fueled by 42% YoY Growth and Enterprise Demand",
  "organization": "Cato Networks",
  "publicationDate": "2026-07-27",
  "economicPeriod": "ARR milestone as of July 27, 2026",
  "canonicalUrl": "https://www.prnewswire.com/il/news-releases/cato-networks-exceeds-415m-in-arr-fueled-by-42-yoy-growth-and-enterprise-demand-302833667.html",
  "excerpt": "Cato Networks...announced that it has surpassed $415 million in ARR, with 42% year-over-year (YoY) growth.",
  "sourceClass": "IR",
  "interpretation": "",
  "limitations": "Company-stated, not an audited filing. AUTO-001 fix pass 4, item 1: this record previously cited a later company blog restating the same figure because the originating PR Newswire release could not be fetched that session; it is now cited directly, carrying its own July 27, 2026 publication date instead of the blog's August 2026 repost date. Supersedes TR-cato-2's $350M/2025 figure with this more recent company-stated figure.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-cato-3",
  "tags": [
    "tracker",
    "network-sase"
  ],
  "retrievedAt": "2026-09-30"
},
{
  "id": "TR-chainguard-1",
  "title": "Chainguard secures $280M to expand trusted open source software platform",
  "organization": "SiliconANGLE",
  "publicationDate": "2025-10-23",
  "economicPeriod": "N/A (funding announcement)",
  "canonicalUrl": "https://siliconangle.com/2025/10/23/chainguard-secures-280m-expand-trusted-open-source-software-platform/",
  "excerpt": "Chainguard closed $280 million in growth financing led by General Catalyst's Customer Value Fund, bringing total raised to approximately $892 million.",
  "sourceClass": "INDEPENDENT",
  "interpretation": "",
  "limitations": "Trade press report; not confirmed against a direct Chainguard primary-source release.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-chainguard-1",
  "tags": [
    "tracker",
    "appsec"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-chainguard-2",
  "title": "Chainguard Announces $280 Million Growth Financing from General Catalyst to Usher in Next Era of Trusted Open Source Software",
  "organization": "Chainguard, Inc.",
  "publicationDate": "2025-10-23",
  "economicPeriod": "N/A (funding announcement)",
  "canonicalUrl": "https://www.prnewswire.com/news-releases/chainguard-announces-280-million-growth-financing-from-general-catalyst-to-usher-in-next-era-of-trusted-open-source-software-302592279.html",
  "excerpt": "Chainguard...today announced it has raised $280 million in growth financing from General Catalyst's Customer Value Fund (CVF).",
  "sourceClass": "IR",
  "interpretation": "",
  "limitations": "AUTO-001 fix pass 4, item 1: supersedes TR-chainguard-1 (SiliconANGLE, trade press) as the cited source — amount and date unchanged, same round.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-chainguard-2",
  "tags": [
    "tracker",
    "appsec"
  ],
  "retrievedAt": "2026-09-30"
},
{
  "id": "TR-checkpoint-1",
  "title": "Check Point Q2 2026 Earnings Release",
  "organization": "Check Point Software Technologies Ltd.",
  "publicationDate": "2026-07-30",
  "economicPeriod": "Q2 2026, ended 2026-06-30",
  "canonicalUrl": "https://www.checkpoint.com/press-releases/check-point-software-reports-2026-second-quarter-financial-results/",
  "excerpt": "Total revenue $674 million, +1% YoY; Security Subscriptions revenue $333 million, +12% YoY.",
  "sourceClass": "IR",
  "interpretation": "",
  "limitations": "Harmony SASE growth not disclosed separately.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-checkpoint-1",
  "tags": [
    "tracker",
    "network-sase",
    "email"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-checkpoint-2",
  "title": "Check Point Q1 2026 Earnings Release",
  "organization": "Check Point Software Technologies Ltd.",
  "publicationDate": "2026-04-30",
  "economicPeriod": "Q1 2026, ended 2026-03-31",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/0001015922/000117891326002310/a2635159.htm",
  "excerpt": "Total revenue $668 million, +5% YoY; Security Subscriptions revenue $323 million, +11% YoY.",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-checkpoint-2",
  "tags": [
    "tracker",
    "network-sase"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-checkpoint-3",
  "title": "Check Point Chief Revenue Officer Appointment",
  "organization": "Check Point Software Technologies Ltd.",
  "publicationDate": "2026-05-01",
  "economicPeriod": "May 2026",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/0001015922/000117891326002310/a2635159.htm",
  "excerpt": "Sherif Seddik appointed Chief Revenue Officer effective May 1, 2026, succeeding Itai Greenberg.",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-checkpoint-3",
  "tags": [
    "tracker",
    "network-sase"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-checkpoint-4",
  "title": "Check Point Convertible Notes Issuance",
  "organization": "Check Point Software Technologies Ltd.",
  "publicationDate": "2026-07-30",
  "economicPeriod": "Q2 2026",
  "canonicalUrl": "https://www.checkpoint.com/press-releases/check-point-software-reports-2026-second-quarter-financial-results/",
  "excerpt": "$2 billion in convertible senior notes issued during Q2 2026, ~$1.8 billion net proceeds.",
  "sourceClass": "IR",
  "interpretation": "",
  "limitations": "",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-checkpoint-4",
  "tags": [
    "tracker",
    "network-sase"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-checkpoint-email-1",
  "title": "Check Point Email Security (formerly Harmony Email & Collaboration)",
  "organization": "Check Point Software Technologies Ltd.",
  "publicationDate": "2026-07-30",
  "economicPeriod": "Q2 2026",
  "canonicalUrl": "https://www.checkpoint.com/press-releases/check-point-software-reports-2026-second-quarter-financial-results/",
  "excerpt": "Harmony Email originated from Avanan acquisition (~August 30, 2021 at $250-300M). Security Subscriptions revenue $333M, +12% YoY.",
  "sourceClass": "IR",
  "interpretation": "",
  "limitations": "Check Point Email Security growth not separately disclosed.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-checkpoint-email-1",
  "tags": [
    "tracker",
    "email"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-checkpoint-email-2",
  "title": "Introducing Check Point Email Security: A New Name Aligned with Our AI-Driven Strategy",
  "organization": "Check Point Software Technologies Ltd.",
  "publicationDate": "2026-03-25",
  "economicPeriod": "March 2026",
  "canonicalUrl": "https://blog.checkpoint.com/product-updates/introducing-check-point-email-security-a-new-name-aligned-with-our-ai-driven-strategy/",
  "excerpt": "Check Point Email Security is the new name for Harmony Email & Collaboration, reflecting a broader strategic evolution and tighter alignment with Check Point's AI-focused security vision.",
  "sourceClass": "OFFICIAL",
  "interpretation": "",
  "limitations": "Product-naming announcement only; no financial figures.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-FITFIX2 / TR-checkpoint-email-2",
  "tags": [
    "tracker",
    "email"
  ],
  "retrievedAt": "2026-09-26"
},
{
  "id": "TR-claroty-1",
  "title": "Industrial cybersecurity startup Claroty nabs $150M funding round",
  "organization": "SiliconANGLE",
  "publicationDate": "2026-01-22",
  "economicPeriod": "N/A (funding announcement)",
  "canonicalUrl": "https://siliconangle.com/2026/01/22/industrial-cybersecurity-startup-claroty-nabs-150m-funding-round/",
  "excerpt": "Claroty raised $150 million in growth equity led by Golub Growth (Golub Capital's growth-equity arm) at a $3 billion post-money valuation, an approximately 80% increase from its prior valuation; the article states Claroty 'expects to become profitable in the near future' and describes revenue only as 'hundreds of millions of dollars,' with no exact figure given.",
  "sourceClass": "INDEPENDENT",
  "interpretation": "",
  "limitations": "Trade press (SiliconANGLE, citing Calcalist); not confirmed against a direct Claroty or Golub press release.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-claroty-1",
  "tags": [
    "tracker",
    "ot-iot"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-cloudflare-1",
  "title": "Cloudflare Q2 2026 Earnings Release",
  "organization": "Cloudflare, Inc.",
  "publicationDate": "2026-08-06",
  "economicPeriod": "Q2 2026, ended 2026-06-30",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/1477333/000147733326000053/q226exhibit991.htm",
  "excerpt": "Revenue $696.1 million, +36% YoY; Current RPO growth 35% YoY.",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-cloudflare-1",
  "tags": [
    "tracker",
    "network-sase"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-cloudflare-2",
  "title": "Cloudflare Q1 2026 Earnings Release",
  "organization": "Cloudflare, Inc.",
  "publicationDate": "2026-05-07",
  "economicPeriod": "Q1 2026, ended 2026-03-31",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/1477333/000147733326000035/q126exhibit991.htm",
  "excerpt": "Revenue $639.8 million, +34% YoY.",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-cloudflare-2",
  "tags": [
    "tracker",
    "network-sase"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-cloudflare-3",
  "title": "Cloudflare Q1 2026 Restructuring Announcement",
  "organization": "Cloudflare, Inc.",
  "publicationDate": "2026-05-07",
  "economicPeriod": "Q1 2026, ended 2026-03-31",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/1477333/000147733326000035/q126exhibit991.htm",
  "excerpt": "Restructuring charge guided at $140-150 million; approximately 1,100 employees affected as part of agentic AI-first operating-model shift.",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "Majority of charge ($105-110M) is cash.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-cloudflare-3",
  "tags": [
    "tracker",
    "network-sase"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-cloudflare-4",
  "title": "Cloudflare Convertible Notes Issuance",
  "organization": "Cloudflare, Inc.",
  "publicationDate": "2026-08-13",
  "economicPeriod": "August 2026",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/1477333/000095010326012340/dp251721_8k.htm",
  "excerpt": "$2.5 billion aggregate principal of 0% Convertible Senior Notes due 2031 issued; ~$2,462.3 million net proceeds.",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-cloudflare-4",
  "tags": [
    "tracker",
    "network-sase"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-commvault-1",
  "title": "Commvault Announces First Quarter Fiscal 2027 Financial Results",
  "organization": "Commvault Systems, Inc.",
  "publicationDate": "2026-07-28",
  "economicPeriod": "Q1 FY2027 (quarter ended 2026-06-30)",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/1169561/000116956126000020/q1fy27pressrelease.htm",
  "excerpt": "Revenue of $314.1 million, up 11% year-over-year; Subscription ARR of $1,054 million, up 22% year-over-year; additional restructuring charges of $2.4 million recorded in the quarter.",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "Company-reported unaudited quarterly results, filed as an exhibit to an SEC Form 8-K.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-commvault-1",
  "tags": [
    "tracker",
    "data"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-commvault-2",
  "title": "Commvault Announces Fourth Quarter and Fiscal Year 2026 Financial Results",
  "organization": "Commvault Systems, Inc.",
  "publicationDate": "2026-04-28",
  "economicPeriod": "Q4 FY2026 (quarter ended 2026-03-31); FY2026 full year",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/1169561/000116956126000013/q4fy26pressrelease.htm",
  "excerpt": "Revenue of $311.7 million for the quarter (+13% YoY); FY2026 full-year revenue of $1,183.7 million (+19% YoY); Subscription ARR of $989.3 million (+27% YoY); two restructuring plans initiated in fiscal 2026 with total charges of $32.2 million; $900 million in convertible notes issued during fiscal 2026 plus $99.6 million spent on related capped-call purchases.",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "Company-reported unaudited quarterly and full-year results, filed as an exhibit to an SEC Form 8-K.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-commvault-2",
  "tags": [
    "tracker",
    "data"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-crwd-1",
  "title": "CrowdStrike Q2 FY2027 Financial Results",
  "organization": "CrowdStrike Holdings, Inc.",
  "publicationDate": "2026-08-26",
  "economicPeriod": "Quarter ended 2026-07-31",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/0001535527/000153552726000029/crwd-20260826xex991.htm",
  "excerpt": "Revenue of $1.47 billion, up 26% year over year. Subscription revenue of $1.40 billion, up 27%. ARR of $5.84 billion, up 25% year over year.",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-crwd-1",
  "tags": [
    "tracker",
    "endpoint-xdr",
    "exposure"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-crwd-2",
  "title": "CrowdStrike Q1 FY2027 Financial Results",
  "organization": "CrowdStrike Holdings, Inc.",
  "publicationDate": "2026-06-03",
  "economicPeriod": "Quarter ended 2026-04-30",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/0001535527/000153552726000022/crwd-20260603xex991.htm",
  "excerpt": "Revenue of $1.39 billion, up 26% year over year. Net new ARR of $256 million, up 32% year over year.",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-crwd-2",
  "tags": [
    "tracker",
    "endpoint-xdr"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-cyberark-1",
  "title": "CyberArk Acquisition Agreement",
  "organization": "Palo Alto Networks, Inc.",
  "publicationDate": "2025-07-31",
  "economicPeriod": "July 2025",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/1327567/000119312525169870/d804159d8k.htm",
  "excerpt": "Merger agreement with CyberArk announced; consideration 2.2005 PANW shares plus $45.00 cash per share.",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "AUTO-001 fix pass 4, item 9: the prior URL 404'd (wrong accession number). Corrected to PANW's actual 2025-07-31 8-K, verified against EDGAR's own submissions index for CIK 0001327567. Deal value approximately $25B per trade press, not explicitly in 8-K text.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-cyberark-1",
  "tags": [
    "tracker",
    "identity"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-cyberark-2",
  "title": "CyberArk SEC Deregistration",
  "organization": "CyberArk Software Ltd.",
  "publicationDate": "2026-02-23",
  "economicPeriod": "February 2026",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/1598110/000110465926018360/tm266096d1_1512g.htm",
  "excerpt": "CyberArk filed Form 15-12G deregistering from SEC, effective February 23, 2026, following acquisition close on February 11, 2026.",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "AUTO-001 fix pass 4, item 9: the prior URL 404'd (wrong accession number). Corrected to CyberArk's actual Form 15-12G, verified against EDGAR's own submissions index for CIK 0001598110.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-cyberark-2",
  "tags": [
    "tracker",
    "identity"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-cyera-1",
  "title": "Cyera Announces $400 Million Investment from Goldman Sachs to Build the Trust Layer for the Agentic Enterprise",
  "organization": "Cyera",
  "publicationDate": "2026-09-22",
  "economicPeriod": "N/A (funding announcement)",
  "canonicalUrl": "https://www.cyera.com/press-releases/cyera-announces-400-million-investment-from-goldman-sachs-to-build-the-trust-layer-for-the-agentic-enterprise",
  "excerpt": "Cyera announced a $400 million growth-equity investment from Growth Equity at Goldman Sachs Alternatives at a valuation of 'over $12 billion.'",
  "sourceClass": "OFFICIAL",
  "interpretation": "",
  "limitations": "Company press release.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-cyera-1",
  "tags": [
    "tracker",
    "data"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-cyera-2",
  "title": "Cyera Completes Acquisition of Oasis Security",
  "organization": "Cyera",
  "publicationDate": "2026-09-03",
  "economicPeriod": "N/A (acquisition announcement)",
  "canonicalUrl": "https://www.cyera.com/press-releases/cyera-completes-acquisition-of-oasis-security",
  "excerpt": "Cyera completed its acquisition of Oasis Security.",
  "sourceClass": "OFFICIAL",
  "interpretation": "",
  "limitations": "",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-FITFIX2 / TR-cyera-2",
  "tags": [
    "tracker",
    "data"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-cyera-3",
  "title": "Cyera Acquires Ryft to Extend its Agentic AI Security Platform",
  "organization": "Cyera",
  "publicationDate": "2026-04-23",
  "economicPeriod": "N/A (acquisition announcement)",
  "canonicalUrl": "https://www.cyera.com/press-releases/cyera-acquires-ryft-to-extend-its-agentic-ai-security-platform",
  "excerpt": "Cyera completed its acquisition of Ryft.",
  "sourceClass": "OFFICIAL",
  "interpretation": "",
  "limitations": "",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-FITFIX2 / TR-cyera-3",
  "tags": [
    "tracker",
    "data"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-cyera-4",
  "title": "Cyera Raises $600 Million at $12 Billion Valuation to Continue Building the Trust Layer for the AI Era",
  "organization": "Cyera",
  "publicationDate": "2026-06-10",
  "economicPeriod": "N/A (funding announcement)",
  "canonicalUrl": "https://www.cyera.com/press-releases/cyera-raises-600-million-at-12-billion-valuation-to-continue-building-the-trust-layer-for-the-ai-era",
  "excerpt": "Cyera raised $600 million led by Evolution Equity Partners at a $12 billion valuation.",
  "sourceClass": "OFFICIAL",
  "interpretation": "",
  "limitations": "Company press release.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-cyera-4",
  "tags": [
    "tracker",
    "data"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-delinea-3",
  "title": "Delinea Appoints Timothy Regan as Chief Financial Officer",
  "organization": "Delinea",
  "publicationDate": "2026-09-23",
  "economicPeriod": "September 2026",
  "canonicalUrl": "https://www.globenewswire.com/news-release/2026/09/23/3367539/0/en/delinea-appoints-timothy-regan-as-chief-financial-officer.html",
  "excerpt": "Timothy Regan appointed Chief Financial Officer of Delinea. He previously served as CFO at Dropbox from 2020 to 2025.",
  "sourceClass": "IR",
  "interpretation": "",
  "limitations": "Whether this followed a predecessor departure was not confirmed.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-FITFIX2 / TR-delinea-3",
  "tags": [
    "tracker",
    "identity"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-dragos-1",
  "title": "Accenture to acquire Dragos, runZero, NetRise",
  "organization": "Help Net Security",
  "publicationDate": "2026-06-19",
  "economicPeriod": "N/A (acquisition announcement)",
  "canonicalUrl": "https://www.helpnetsecurity.com/2026/06/19/accenture-dragos-runzero-netrise-acquisition/",
  "excerpt": "Accenture agreed to acquire a majority stake in Dragos and all of runZero and NetRise; combined enterprise value reported at approximately $4.1-4.2 billion. The underlying research separately confirms the existence of this agreement in Accenture's own Q3 FY2026 earnings 8-K exhibit (accession 0001467373-26-000031), which states: 'Our agreement to acquire a majority stake in Dragos and all of runZero and NetRise...' — that filing does not disclose the dollar price.",
  "sourceClass": "INDEPENDENT",
  "interpretation": "",
  "limitations": "Trade press report; the deal's existence and June 18, 2026 announcement date are independently corroborated in Accenture's own SEC 8-K exhibit per the underlying research, though a direct filing URL was not captured for citation here. Price and closing-date specifics remain trade-press-sourced only.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-dragos-1",
  "tags": [
    "tracker",
    "ot-iot"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-esentire-1",
  "title": "eSentire Growth Equity Funding",
  "organization": "eSentire, Inc.",
  "publicationDate": "2022-02-22",
  "economicPeriod": "February 2022",
  "canonicalUrl": "https://www.esentire.com/news-releases/global-cybersecurity-leader-esentire-raises-us-325m-and-achieves-unicorn-status",
  "excerpt": "eSentire raised $325 million in growth-equity funding at $1.1 billion valuation, led by Warburg Pincus, with Georgian and CDPQ participating.",
  "sourceClass": "OFFICIAL",
  "interpretation": "",
  "limitations": "Warburg Pincus has held a majority stake since an initial 2017 investment.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-esentire-1",
  "tags": [
    "tracker",
    "managed-security"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-exabeam-1",
  "title": "Exabeam and LogRhythm Merger Completion",
  "organization": "Thoma Bravo",
  "publicationDate": "2024-07-17",
  "economicPeriod": "July 2024",
  "canonicalUrl": "https://www.thomabravo.com/press-releases/exabeam-and-logrhythm-complete-merger-and-announce-new-company-details",
  "excerpt": "Exabeam and LogRhythm completed their merger on July 17, 2024. Thoma Bravo is a named stakeholder in the combined company.",
  "sourceClass": "OFFICIAL",
  "interpretation": "",
  "limitations": "Merger date corrects prior assumption of 2025 closing.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-exabeam-1",
  "tags": [
    "tracker",
    "secops"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-expel-2",
  "title": "Expel Investors Fuel Rapid Growth With Additional Series E Investment, Bringing Total Funding to $288 Million",
  "organization": "Expel, Inc.",
  "publicationDate": "2022-10-03",
  "economicPeriod": "N/A (funding announcement)",
  "canonicalUrl": "https://expel.com/resource/expel-investors-fuel-rapid-growth-with-additional-series-e-investment-bringing-total-funding-to-288-million/",
  "excerpt": "Expel...announced an additional $171.3 million in Series E funding, led by CapitalG and Paladin Capital Group, with participation from existing investors Scale Venture Partners, March Capital, Index Ventures, and Battery Ventures, bringing total funding raised to $288.8 million.",
  "sourceClass": "OFFICIAL",
  "interpretation": "",
  "limitations": "AUTO-001 fix pass 4, item 8: the tracker previously had no ownership field for Expel at all.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-expel-2",
  "tags": [
    "tracker",
    "managed-security"
  ],
  "retrievedAt": "2026-09-30"
},
{
  "id": "TR-forescout-1",
  "title": "Forescout leadership page",
  "organization": "Forescout Technologies, Inc.",
  "publicationDate": "2026-09-25",
  "economicPeriod": "N/A (company background)",
  "canonicalUrl": "https://www.forescout.com/company/leadership/",
  "excerpt": "Forescout is co-owned by Advent International and Crosspoint Capital Partners; CEO Barry Mainz also holds the title of Operating Partner at Crosspoint Capital Partners.",
  "sourceClass": "OFFICIAL",
  "interpretation": "",
  "limitations": "Company leadership page. Advent International's original take-private acquisition closed via tender offer in 2020 per SEC EDGAR SC TO-T/A filings; the exact date Crosspoint joined as co-owner was not independently dated this pass.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-forescout-1",
  "tags": [
    "tracker",
    "ot-iot"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-fortinet-1",
  "title": "Fortinet Q2 2026 Earnings Release",
  "organization": "Fortinet, Inc.",
  "publicationDate": "2026-07-29",
  "economicPeriod": "Q2 2026, ended 2026-06-30",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/0001262039/000126203926000018/ftntq2-2026ex991.htm",
  "excerpt": "Revenue $2.05 billion, +26% YoY; Billings $2.37 billion, +33% YoY.",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "SASE platform-specific ARR not disclosed separately.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-fortinet-1",
  "tags": [
    "tracker",
    "network-sase"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-fortinet-2",
  "title": "Fortinet Q1 2026 Earnings Release",
  "organization": "Fortinet, Inc.",
  "publicationDate": "2026-05-06",
  "economicPeriod": "Q1 2026, ended 2026-03-31",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/0001262039/000126203926000010/ftntq1-2026ex991.htm",
  "excerpt": "Revenue $1.85 billion, +20% YoY; Billings $2.09 billion, +31% YoY.",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-fortinet-2",
  "tags": [
    "tracker",
    "network-sase"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-ghas-1",
  "title": "Goodbye, GitHub",
  "organization": "GitHub, Inc. (subsidiary of Microsoft Corporation)",
  "publicationDate": "2025-08-11",
  "economicPeriod": "N/A (leadership announcement)",
  "canonicalUrl": "https://github.blog/news-insights/company-news/goodbye-github/",
  "excerpt": "GitHub CEO Thomas Dohmke announced he was stepping down to become a founder again; no successor CEO was named, and GitHub's leadership folded further into Microsoft's CoreAI organization.",
  "sourceClass": "OFFICIAL",
  "interpretation": "",
  "limitations": "Company (GitHub) blog post.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-ghas-1",
  "tags": [
    "tracker",
    "appsec"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-google-secops-1",
  "title": "Alphabet Inc. - Google Cloud Security Products",
  "organization": "Alphabet Inc.",
  "publicationDate": "2026-07-22",
  "economicPeriod": "Quarter ended 2026-06-30",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/0001652044/000165204426000066/googexhibit991q22026.htm",
  "excerpt": "Google Cloud revenue of $24.8 billion, up 82% year over year. Google SecOps (Chronicle and Mandiant products) are components within Google Cloud; no separate revenue disclosed.",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "Segment figure. No separate revenue or metrics disclosed for SecOps specifically.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-google-secops-1",
  "tags": [
    "tracker",
    "secops"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-hiddenlayer-1",
  "title": "HiddenLayer Raises $100M in Series B Funding to Advance AI Security",
  "organization": "HiddenLayer, Inc.",
  "publicationDate": "2026-09-02",
  "economicPeriod": "N/A (funding announcement)",
  "canonicalUrl": "https://www.hiddenlayer.com/news/hiddenlayer-100m-series-b-ai-security",
  "excerpt": "HiddenLayer raised a $100 million Series B round led by Delta-v Capital, with Ten Eleven Ventures, Morgan Stanley, M12, and Booz Allen Ventures participating. The company states ARR 'grew more than 10x year-over-year' with 50+ new platform customers signed (unaudited).",
  "sourceClass": "OFFICIAL",
  "interpretation": "",
  "limitations": "",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-FITFIX2 / TR-hiddenlayer-1",
  "tags": [
    "tracker",
    "ai-security"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-ivanti-1",
  "title": "Ivanti Capital Refinancing",
  "organization": "Ivanti, Inc.",
  "publicationDate": "2025-05-02",
  "economicPeriod": "May 2025",
  "canonicalUrl": "https://www.ivanti.com/company/press-releases/2025/ivanti-announces-successful-refinancing-and-new-capital-infusion-to-support-key-strategic-initiatives",
  "excerpt": "Ivanti announced successful refinancing with $350 million in new capital from existing first- and second-lien lenders. Maturities extended to 2029.",
  "sourceClass": "OFFICIAL",
  "interpretation": "",
  "limitations": "Date falls just outside the 12-month event window but is provided for context.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-ivanti-1",
  "tags": [
    "tracker",
    "exposure"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-ivanti-2",
  "title": "Charlesbank Capital Partners Closes Strategic Investment in Ivanti",
  "organization": "Ivanti, Inc.",
  "publicationDate": "2021-05-11",
  "economicPeriod": "May 2021",
  "canonicalUrl": "https://www.ivanti.com/company/press-releases/2021/charlesbank-capital-partners-closes-strategic-investment-in-ivanti",
  "excerpt": "Ivanti...today announced the close of the strategic investment from Charlesbank Capital Partners, LLC...Charlesbank...has joined existing investors Clearlake Capital Group, L.P....and TA Associates...as an institutional shareholder in Ivanti. Terms of the transaction were not disclosed.",
  "sourceClass": "OFFICIAL",
  "interpretation": "",
  "limitations": "AUTO-001 fix pass 4, item 2: the prior ownership citation (TR-ivanti-1) was actually a 2025 refinancing release and named no date for the ownership structure itself; this is Ivanti's own dated release for when Charlesbank joined as the third PE investor.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-ivanti-2",
  "tags": [
    "tracker",
    "exposure"
  ],
  "retrievedAt": "2026-10-01",
  "retrieval": {
    "finalUrl": "https://www.ivanti.com/company/press-releases/2021/charlesbank-capital-partners-closes-strategic-investment-in-ivanti",
    "sha256": "2a6e79069dbf5f7206a5d878d633fd2436b4544e4e184a635de295cfcf8598cb",
    "fetchedAt": "2026-10-01T00:00:00Z",
    "locator": "First paragraph"
  }
},
{
  "id": "TR-jfrog-1",
  "title": "JFrog Announces Second Quarter 2026 Results",
  "organization": "JFrog Ltd.",
  "publicationDate": "2026-08-06",
  "economicPeriod": "Q2 2026 (quarter ended 2026-06-30)",
  "canonicalUrl": "https://investors.jfrog.com/news/news-details/2026/JFrog-Announces-Second-Quarter-2026-Results/default.aspx",
  "excerpt": "Revenue of $163.8 million, up 29% year-over-year; cloud revenue of $87.5 million, up 53% year-over-year and equal to 53% of total revenue, up from 45% a year earlier.",
  "sourceClass": "IR",
  "interpretation": "",
  "limitations": "Company investor-relations press release.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-jfrog-1",
  "tags": [
    "tracker",
    "appsec"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-jfrog-2",
  "title": "JFrog Announces First Quarter 2026 Results",
  "organization": "JFrog Ltd.",
  "publicationDate": "2026-05-07",
  "economicPeriod": "Q1 2026 (quarter ended 2026-03-31)",
  "canonicalUrl": "https://investors.jfrog.com/news/news-details/2026/JFrog-Announces-First-Quarter-2026-Results/default.aspx",
  "excerpt": "Revenue of $154.0 million, up 26% year-over-year; cloud revenue of $78.9 million, up 50% year-over-year.",
  "sourceClass": "IR",
  "interpretation": "",
  "limitations": "Company investor-relations press release.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-jfrog-2",
  "tags": [
    "tracker",
    "appsec"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-lakera-1",
  "title": "Check Point Software Technologies FY2025 earnings release (Form 6-K)",
  "organization": "Check Point Software Technologies Ltd",
  "publicationDate": "2026-01-01",
  "economicPeriod": "FY2025 full year",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/1015922/000117891326000437/zk2634351.htm",
  "excerpt": "'During the fourth quarter of 2025 we completed the acquisition of Lakera AI for approximately $190 million net cash consideration.'",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "Company SEC Form 6-K exhibit. Check Point separately announced the deal on September 16, 2025; no more precise closing day within Q4 2025 was disclosed in the exhibit reviewed.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-lakera-1",
  "tags": [
    "tracker",
    "ai-security"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-mimecast-1",
  "title": "Mimecast Permira Take-Private Completion",
  "organization": "Mimecast Limited",
  "publicationDate": "2022-05",
  "economicPeriod": "May 2022",
  "canonicalUrl": "https://www.mimecast.com/resources/press-releases/",
  "excerpt": "Permira take-private via Magnesium Bidco closed May 2022 at $5.8 billion.",
  "sourceClass": "IR",
  "interpretation": "",
  "limitations": "",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-mimecast-1",
  "tags": [
    "tracker",
    "email"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-mimecast-2",
  "title": "Mimecast CEO Appointment",
  "organization": "Mimecast",
  "publicationDate": "2026-06-25",
  "economicPeriod": "June 2026",
  "canonicalUrl": "https://www.mimecast.com/resources/press-releases/",
  "excerpt": "Ranjan Singh appointed CEO effective June 25, 2026, succeeding Marc van Zadelhoff.",
  "sourceClass": "IR",
  "interpretation": "",
  "limitations": "",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-mimecast-2",
  "tags": [
    "tracker",
    "email"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-msft-1",
  "title": "Microsoft FY2026 10-K Filing",
  "organization": "Microsoft Corporation",
  "publicationDate": "2026-07-29",
  "economicPeriod": "FY2026, ended 2026-06-30",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/789019/000119312526323660/msft-20260630.htm",
  "excerpt": "FY2026 revenue $331.839 billion, +18% YoY. Defender for Endpoint is a product within Microsoft's Security segment and is not separately reported in the filing.",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "AUTO-001 fix pass 4, item 9: this record previously cited a generic investor landing page (microsoft.com/en-us/investor) rather than a document. Points to Microsoft's own 10-K now, the same filing already cited by TR-msft-defender-1 and TR-msft-entra-1. No separate revenue disclosed by the company for Defender for Endpoint.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-msft-1",
  "tags": [
    "tracker",
    "endpoint-xdr"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-msft-defender-1",
  "title": "Microsoft FY2026 10-K Filing",
  "organization": "Microsoft Corporation",
  "publicationDate": "2026-07-29",
  "economicPeriod": "FY2026, ended 2026-06-30",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/789019/000119312526323660/msft-20260630.htm",
  "excerpt": "FY2026 revenue $331.839 billion, +18% YoY. Defender for Office 365 is a product within Microsoft, not separately reported.",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-msft-defender-1",
  "tags": [
    "tracker",
    "email"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-msft-entra-1",
  "title": "Microsoft FY2026 10-K Filing",
  "organization": "Microsoft Corporation",
  "publicationDate": "2026-07-29",
  "economicPeriod": "FY2026, ended 2026-06-30",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/789019/000119312526323660/msft-20260630.htm",
  "excerpt": "FY2026 revenue $331.839 billion, +18% YoY. No discrete Entra ID revenue figure disclosed.",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "Security business revenue not broken out separately since January 2023 disclosure of $20B.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-msft-entra-1",
  "tags": [
    "tracker",
    "identity"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-netskope-1",
  "title": "Netskope Q2 FY2027 Earnings Release",
  "organization": "Netskope, Inc.",
  "publicationDate": "2026-09-02",
  "economicPeriod": "Q2 FY2027, ended 2026-07-31",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/2063196/000119312526380188/ntsk-ex99_1.htm",
  "excerpt": "Revenue $220.5 million, +29% YoY; ARR $899 million, +27% YoY.",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-netskope-1",
  "tags": [
    "tracker",
    "network-sase"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-netskope-2",
  "title": "Netskope Q1 FY2027 Earnings Release",
  "organization": "Netskope, Inc.",
  "publicationDate": "2026-06-03",
  "economicPeriod": "Q1 FY2027, ended 2026-04-30",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/2063196/000119312526255439/ck0002063196-ex99_1.htm",
  "excerpt": "Revenue $201.6 million, +28% YoY; ARR $845 million, +29% YoY.",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-netskope-2",
  "tags": [
    "tracker",
    "network-sase"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-netskope-3",
  "title": "Netskope IPO Prospectus",
  "organization": "Netskope, Inc.",
  "publicationDate": "2025-09-18",
  "economicPeriod": "September 2025",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/2063196/000119312525204285/ck0002063196-20250916.htm",
  "excerpt": "IPO'd on Nasdaq on September 18, 2025: 47.8 million Class A shares at $19.00, implying $7.3B valuation; closed with full over-allotment exercise, net proceeds ~$992.2 million.",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "AUTO-001 fix pass 4, item 9: the prior URL 404'd (wrong accession number). Corrected to Netskope's final S-1/A, filed 2025-09-16, two days before the IPO date this record cites, verified against EDGAR's own submissions index for CIK 0002063196.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-netskope-3",
  "tags": [
    "tracker",
    "network-sase"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-netskope-4",
  "title": "Netskope Q2 FY2027 Restructuring Costs",
  "organization": "Netskope, Inc.",
  "publicationDate": "2026-09-02",
  "economicPeriod": "Q2 FY2027, ended 2026-07-31",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/2063196/000119312526380188/ntsk-ex99_1.htm",
  "excerpt": "$3.5 million in restructuring costs recognized in the quarter ended July 31, 2026.",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-netskope-4",
  "tags": [
    "tracker",
    "network-sase"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-netskope-5",
  "title": "Netskope CFO Retirement Disclosure",
  "organization": "Netskope, Inc.",
  "publicationDate": "2026-06-03",
  "economicPeriod": "Q1 FY2027",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/2063196/000119312526255439/ck0002063196-20260603.htm",
  "excerpt": "CFO Drew Del Matto disclosed intention to retire after 40 years; remains CFO while successor is sought.",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "Successor not yet named.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-netskope-5",
  "tags": [
    "tracker",
    "network-sase"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-nozomi-1",
  "title": "Mitsubishi Electric to Acquire Nozomi Networks to Improve Industrial Cyber Defenses and Power Operational Transformation",
  "organization": "Mitsubishi Electric Corporation / Nozomi Networks, Inc.",
  "publicationDate": "2025-09-09",
  "economicPeriod": "N/A (acquisition announcement)",
  "canonicalUrl": "https://www.prnewswire.com/news-releases/mitsubishi-electric-to-acquire-nozomi-networks-to-improve-industrial-cyber-defenses-and-power-operational-transformation-302550314.html",
  "excerpt": "Mitsubishi Electric Corporation (TOKYO: 6503) signed a definitive agreement to acquire Nozomi Networks.",
  "sourceClass": "OFFICIAL",
  "interpretation": "",
  "limitations": "Announcement of signed agreement, not completion.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-FITFIX2 / TR-nozomi-1",
  "tags": [
    "tracker",
    "ot-iot"
  ],
  "retrievedAt": "2026-09-26"
},
{
  "id": "TR-nozomi-2",
  "title": "Nozomi Networks Enters Next Phase of Growth as Mitsubishi Electric Completes Acquisition",
  "organization": "Mitsubishi Electric Corporation / Nozomi Networks, Inc.",
  "publicationDate": "2026-01-29",
  "economicPeriod": "N/A (acquisition completion)",
  "canonicalUrl": "https://www.prnewswire.com/news-releases/nozomi-networks-enters-next-phase-of-growth-as-mitsubishi-electric-completes-acquisition-302673652.html",
  "excerpt": "Mitsubishi Electric Corporation (TOKYO: 6503) has completed its acquisition of Nozomi Networks. Following completion, Nozomi Networks operates as a wholly owned subsidiary while maintaining independent operations and a vendor-neutral approach.",
  "sourceClass": "OFFICIAL",
  "interpretation": "",
  "limitations": "",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-FITFIX2 / TR-nozomi-2",
  "tags": [
    "tracker",
    "ot-iot"
  ],
  "retrievedAt": "2026-09-26"
},
{
  "id": "TR-okta-1",
  "title": "Okta Q2 FY2027 Earnings Release",
  "organization": "Okta, Inc.",
  "publicationDate": "2026-08-26",
  "economicPeriod": "Quarter ended July 31, 2026",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/1660134/000166013426000069/okta-20260731.htm",
  "excerpt": "Revenue $805 million, +11% YoY; Subscription Revenue $793 million, +12% YoY.",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-okta-1",
  "tags": [
    "tracker",
    "identity"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-okta-2",
  "title": "Okta Q1 FY2027 Earnings Release",
  "organization": "Okta, Inc.",
  "publicationDate": "2026-05-27",
  "economicPeriod": "Quarter ended April 30, 2026",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/1660134/000166013426000051/okta-20260430.htm",
  "excerpt": "Revenue $765 million, +11.2% YoY.",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-okta-2",
  "tags": [
    "tracker",
    "identity"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-optiv-1",
  "title": "Optiv Security - KKR Ownership",
  "organization": "Optiv Security Inc.",
  "publicationDate": "2016-12-06",
  "economicPeriod": "December 2016",
  "canonicalUrl": "https://www.optiv.com/company/press-releases/optiv-security-be-acquired-kkr",
  "excerpt": "KKR announced the acquisition of Optiv Security with Blackstone and management retaining minority stakes. Deal announced 2016-12-06.",
  "sourceClass": "OFFICIAL",
  "interpretation": "",
  "limitations": "",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-optiv-1",
  "tags": [
    "tracker",
    "managed-security"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-optiv-3",
  "title": "Optiv Lender Agreement Amendment",
  "organization": "Optiv Inc.",
  "publicationDate": "2026-05-08",
  "economicPeriod": "May 2026",
  "canonicalUrl": "https://www.optiv.com/company/press-releases/optiv-strengthens-financial-position-lender-agreement-comprehensive",
  "excerpt": "Optiv's lenders agreed to amend and extend the First Lien Credit Agreement to August 2028 and the Second Lien to August 2029, with more than 99% of First Lien and 100% of Second Lien holders participating.",
  "sourceClass": "OFFICIAL",
  "interpretation": "",
  "limitations": "",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-optiv-3",
  "tags": [
    "tracker",
    "managed-security"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-optiv-4",
  "title": "Optiv Sells ACT Business to Vobis Ventures",
  "organization": "Optiv Security Inc.",
  "publicationDate": "2026-06-02",
  "economicPeriod": "June 2026",
  "canonicalUrl": "https://www.optiv.com/company/press-releases/optiv-sells-advisory-consulting-and-transformation-act-business-vobis",
  "excerpt": "Optiv announced the sale of its advisory, consulting and transformation (ACT) project-based services business to Vobis Ventures. The deal officially closed June 1, 2026. Optiv's managed services and staff augmentation will remain in-house.",
  "sourceClass": "OFFICIAL",
  "interpretation": "",
  "limitations": "",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-optiv-4",
  "tags": [
    "tracker",
    "managed-security"
  ],
  "retrievedAt": "2026-09-26",
  "retrieval": {
    "finalUrl": "https://www.optiv.com/company/press-releases/optiv-sells-advisory-consulting-and-transformation-act-business-vobis",
    "sha256": "b3ce593e2c26fdc3f1ace774018e51e7a13a3c309f960706ab3e0e43321ecb43",
    "fetchedAt": "2026-09-26T14:50:00Z",
    "locator": "Press release dated June 02, 2026"
  }
},
{
  "id": "TR-orca-1",
  "title": "Orca Security Company Information",
  "organization": "Orca Security",
  "publicationDate": "2026-09-25",
  "economicPeriod": "September 2026",
  "canonicalUrl": "https://orca.security/resources/press-releases/",
  "excerpt": "VC-backed company with investors including YL Ventures, Willoughby Capital, Temasek, Splunk, SAIC.",
  "sourceClass": "VENDOR-RESEARCH",
  "interpretation": "",
  "limitations": "Revenue/ARR not found in newsroom searched.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-orca-1",
  "tags": [
    "tracker",
    "cloud"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-orca-2",
  "title": "Orca Security Raises $550M in Extended Series C Round",
  "organization": "Orca Security",
  "publicationDate": "2021-10-05",
  "economicPeriod": "N/A (funding announcement)",
  "canonicalUrl": "https://orca.security/resources/press-releases/orca-security-series-c-550-million-announcement/",
  "excerpt": "Orca Security...announced it closed $550 million in its extended Series C fundraising round, led by Temasek...boosting its valuation to $1.8 billion.",
  "sourceClass": "OFFICIAL",
  "interpretation": "",
  "limitations": "AUTO-001 fix pass 4, item 1: the tracker previously had no lastRound field and an un-cited generic ownership line for Orca; no funding or ownership event newer than this October 2021 round was found in Orca's own press-release archive as of 2026-09-30.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-orca-2",
  "tags": [
    "tracker",
    "cloud"
  ],
  "retrievedAt": "2026-09-30"
},
{
  "id": "TR-panw-1",
  "title": "Palo Alto Networks Q4 FY2026 Financial Results",
  "organization": "Palo Alto Networks, Inc.",
  "publicationDate": "2026-09-01",
  "economicPeriod": "Quarter ended 2026-07-31",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/0001327567/000132756726000019/ex991q426earningsrelease.htm",
  "excerpt": "Revenue of $3.41 billion, up 34% year over year. NGS ARR of $9.10 billion, up 63% year over year. RPO of $21.2 billion, up 34% year over year.",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "Growth includes contributions from CyberArk and Chronosphere acquisitions closed during the fiscal year.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-panw-1",
  "tags": [
    "tracker",
    "endpoint-xdr",
    "secops"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-panw-2",
  "title": "Palo Alto Networks Q3 FY2026 Financial Results",
  "organization": "Palo Alto Networks, Inc.",
  "publicationDate": "2026-06-02",
  "economicPeriod": "Quarter ended 2026-04-30",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/0001327567/000132756726000012/ex991q326earningsrelease.htm",
  "excerpt": "Revenue of $3.0 billion, up 31% year over year, including $388 million from CyberArk and Chronosphere acquisitions.",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-panw-2",
  "tags": [
    "tracker",
    "endpoint-xdr",
    "secops"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-panw-3",
  "title": "Palo Alto Networks Closes CyberArk Acquisition",
  "organization": "Palo Alto Networks, Inc.",
  "publicationDate": "2026-02-11",
  "economicPeriod": "February 2026",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/1327567/000119312526045600/d40626d8k.htm",
  "excerpt": "Palo Alto Networks closed its acquisition of CyberArk Software Ltd. for approximately $25 billion in equity value, including $2.3 billion in cash and 112 million shares.",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "AUTO-001 fix pass 4, item 9: the prior URL 404'd (wrong filename). Corrected to PANW's actual 2026-02-11 8-K, verified against EDGAR's own submissions index for CIK 0001327567.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-panw-3",
  "tags": [
    "tracker",
    "endpoint-xdr",
    "secops"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-panw-xsiam-1",
  "title": "Palo Alto Networks, Inc. — Form 10-K, fiscal year ended July 31, 2026",
  "organization": "Palo Alto Networks, Inc.",
  "publicationDate": "2026-09-10",
  "economicPeriod": "FY2026",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/1327567/000132756726000023/panw-20260731.htm",
  "excerpt": "Cortex XSIAM is a product line within Palo Alto Networks; the filing discloses only combined Next-Gen Security ARR, with no XSIAM-specific revenue or metrics stated separately.",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "AUTO-001 fix pass 4, item 9: this record previously cited the filing's index page rather than the document itself. Points to the primary 10-K document (panw-20260731.htm) now. Product line, not a standalone entity — no separate revenue disclosed.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-FITFIX2 / TR-panw-xsiam-1",
  "tags": [
    "tracker",
    "secops"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-ping-1",
  "title": "Ping Identity Surpasses 30% Annual Growth in SaaS Revenue and Approaches $800M ARR as an Enterprise Identity Market Leader",
  "organization": "Ping Identity",
  "publicationDate": "2024-11-14",
  "economicPeriod": "Period ended September 30, 2024",
  "canonicalUrl": "https://press.pingidentity.com/2024-11-14-Ping-Identity-Surpasses-30-Annual-Growth-in-SaaS-Revenue-and-Approaches-800M-ARR-as-an-Enterprise-Identity-Market-Leader",
  "excerpt": "Ping Identity has surpassed key growth milestones as of September 30, 2024, achieving 31% year-over-year Annual Recurring Revenue (ARR) growth of SaaS offerings, 33% year-to-date new bookings growth, while approaching $800M ARR.",
  "sourceClass": "IR",
  "interpretation": "",
  "limitations": "AUTO-001 fix pass 4, item 9: previously cited the bare newsroom index page, which the build's source-legibility gate treats as unusable; replaced with the specific release. No newer figure found; treat as stale relative to September 2026.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-ping-1",
  "tags": [
    "tracker",
    "identity"
  ],
  "retrievedAt": "2026-10-01"
},
{
  "id": "TR-ping-2",
  "title": "Thoma Bravo Completes Acquisition of Ping Identity",
  "organization": "Ping Identity",
  "publicationDate": "2022-10-18",
  "economicPeriod": "October 2022",
  "canonicalUrl": "https://press.pingidentity.com/2022-10-18-Thoma-Bravo-Completes-Acquisition-of-Ping-Identity",
  "excerpt": "Ping Identity announced the completion of its acquisition by Thoma Bravo in an all-cash transaction valued at approximately $2.8 billion. Ping Identity stockholders are entitled to receive $28.50 in cash for each share of common stock they owned.",
  "sourceClass": "IR",
  "interpretation": "",
  "limitations": "AUTO-001 fix pass 4, item 9: previously cited the bare newsroom index page; replaced with the specific release.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-ping-2",
  "tags": [
    "tracker",
    "identity"
  ],
  "retrievedAt": "2026-10-01"
},
{
  "id": "TR-ping-3",
  "title": "Ping Identity Marks Digital Trust Milestone with Zero-Knowledge Biometrics in the Age of AI",
  "organization": "Ping Identity",
  "publicationDate": "2026-01-07",
  "economicPeriod": "N/A (acquisition completion announcement)",
  "canonicalUrl": "https://www.prnewswire.com/news-releases/ping-identity-marks-digital-trust-milestone-with-zero-knowledge-biometrics-in-the-age-of-ai-302654492.html",
  "excerpt": "With the acquisition of Keyless now complete, Ping adds Zero-Knowledge Biometrics to its portfolio. Financial terms of the transaction were not disclosed.",
  "sourceClass": "IR",
  "interpretation": "",
  "limitations": "AUTO-001 fix pass 4, item 3: the tracker previously showed 0 events in the trailing 12 months for Ping Identity; both blind scorers (score3/opus, score3/sol) found this acquisition completion missing.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-ping-3",
  "tags": [
    "tracker",
    "identity"
  ],
  "retrievedAt": "2026-09-30"
},
{
  "id": "TR-proofpoint-1",
  "title": "Proofpoint Thoma Bravo Take-Private Completion",
  "organization": "Proofpoint, Inc.",
  "publicationDate": "2021-08-31",
  "economicPeriod": "August 2021",
  "canonicalUrl": "https://www.proofpoint.com/us/newsroom",
  "excerpt": "Thoma Bravo take-private closed August 31, 2021 at $12.3 billion deal value.",
  "sourceClass": "IR",
  "interpretation": "",
  "limitations": "",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-proofpoint-1",
  "tags": [
    "tracker",
    "email"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-protectai-1",
  "title": "Palo Alto Networks Form 10-K (FY2025)",
  "organization": "Palo Alto Networks, Inc.",
  "publicationDate": "2025-09-01",
  "economicPeriod": "FY2025 (fiscal year ended 2025-07-31)",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/1327567/000132756725000027/panw-20250731.htm",
  "excerpt": "Palo Alto Networks completed its acquisition of Protect AI, Inc. in July 2025 (specifically on or about July 22, 2025 per XBRL tagging), for $700.0 million in cash and replacement awards, subject to adjustment.",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "Company SEC Form 10-K.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-protectai-1",
  "tags": [
    "tracker",
    "ai-security"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-qualys-1",
  "title": "Qualys Inc. Q2 2026 Financial Results",
  "organization": "Qualys, Inc.",
  "publicationDate": "2026-08-04",
  "economicPeriod": "Quarter ended 2026-06-30",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/0001107843/000110784326000034/qlys-20260804xex991.htm",
  "excerpt": "Revenue of $182.2 million, up 11% year over year. GAAP net income of $52.4 million. Q3 2026 guidance: $185.5 million to $187.5 million (+9% to +10%). FY2026 guidance raised to $732.0 million to $738.0 million.",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-qualys-1",
  "tags": [
    "tracker",
    "exposure"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-qualys-2",
  "title": "Qualys Inc. Q1 2026 Financial Results",
  "organization": "Qualys, Inc.",
  "publicationDate": "2026-05-05",
  "economicPeriod": "Quarter ended 2026-03-31",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/1107843/000110784326000013/qlys-20260505xex991.htm",
  "excerpt": "Revenues for the first quarter of 2026 increased by 10% to $175.6 million compared to $159.9 million for the same quarter in 2025.",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "AUTO-001 fix pass 4, item 7: added so the tracker's prior-quarter cell is no longer bare — the tracker previously had no citation for Qualys's Q1 2026 figures at all. Precise YoY growth from these two figures is 9.8%, consistent with the release's own rounded \"10%\" headline; confirmed against the comparative income statement in Qualys's own Q2 2026 10-Q (same $175,638K / $159,899K figures, in thousands).",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-qualys-2",
  "tags": [
    "tracker",
    "exposure"
  ],
  "retrievedAt": "2026-10-01"
},
{
  "id": "TR-rapid7-1",
  "title": "Rapid7 Inc. Q2 2026 Financial Results",
  "organization": "Rapid7, Inc.",
  "publicationDate": "2026-08-10",
  "economicPeriod": "Quarter ended 2026-06-30",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/0001560327/000156032726000043/q22026rapid78-kex991.htm",
  "excerpt": "Revenue of $210.9 million, down 1.5% year over year. ARR of $824.0 million, down 2.0% year over year. Q3 2026 guidance: revenue $208 million to $210 million (-5% to -4% YoY). FY2026 guidance: revenue $837 million to $841 million (-3% to -2% YoY).",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-rapid7-1",
  "tags": [
    "tracker",
    "exposure"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-rapid7-2",
  "title": "Rapid7 Inc. Q1 2026 Financial Results",
  "organization": "Rapid7, Inc.",
  "publicationDate": "2026-05-22",
  "economicPeriod": "Quarter ended 2026-03-31",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/0001560327/000156032726000032/q12026rapid78-kex991.htm",
  "excerpt": "Revenue of $210 million, down 0.3% year over year. ARR of $832 million, down 0.6% year over year.",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-rapid7-2",
  "tags": [
    "tracker",
    "exposure"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-rapid7-3",
  "title": "Rapid7 Appoints Wael Mohamed CEO",
  "organization": "Rapid7, Inc.",
  "publicationDate": "2026-06-01",
  "economicPeriod": "June 2026",
  "canonicalUrl": "https://investors.rapid7.com/news/news-details/2026/Rapid7-Appoints-Wael-Mohamed-Chief-Executive-Officer-Corey-Thomas-to-Become-Executive-Chairman/default.aspx",
  "excerpt": "Rapid7 appointed Wael Mohamed, a board member since April 2025 and former Forescout CEO, as Chief Executive Officer. Corey Thomas, CEO for 13+ years, became executive chairman.",
  "sourceClass": "OFFICIAL",
  "interpretation": "",
  "limitations": "",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-rapid7-3",
  "tags": [
    "tracker",
    "exposure"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-rapid7-4",
  "title": "Rapid7 Workforce Reduction - 8-K Item 2.05",
  "organization": "Rapid7, Inc.",
  "publicationDate": "2026-08-07",
  "economicPeriod": "August 2026",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/0001560327/000156032726000043/rp-20260807.htm",
  "excerpt": "Rapid7 approved a workforce reduction of approximately 12% with estimated charges of $10 million to $11 million, mainly for severance, notice-period pay, and benefits. Most charges expected in Q3 and Q4 2026.",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-rapid7-4",
  "tags": [
    "tracker",
    "exposure"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-rapid7-5",
  "title": "Rapid7, Inc. — Form 8-K, Item 5.02 (director resignations)",
  "organization": "Rapid7, Inc.",
  "publicationDate": "2026-08-31",
  "economicPeriod": "August 2026",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/1560327/000156032726000046/rp-20260827.htm",
  "excerpt": "Four directors — Michael Burns, Benjamin Holzman, Thomas Schodorf, and Reeny Sondhi — notified the board of their resignation from the board and every committee they served on, effective August 27, 2026. The filing states the resignations were not due to any disagreement with the company; the board approved severance arrangements including cash payments through June 2027 and accelerated equity vesting for each departing director.",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "Filed August 31, 2026; the resignations themselves were effective August 27, 2026.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-FITFIX2 / TR-rapid7-5",
  "tags": [
    "tracker",
    "exposure"
  ],
  "retrievedAt": "2026-09-26"
},
{
  "id": "TR-red-canary-1",
  "title": "Zscaler Closes Red Canary Acquisition",
  "organization": "Zscaler, Inc.",
  "publicationDate": "2025-08-01",
  "economicPeriod": "August 2025",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/1713683/000171368325000205/zs-20251031.htm",
  "excerpt": "Zscaler closed its acquisition of Red Canary for $651.4 million in cash plus $20.2 million in restricted stock. Announced 2025-05-27; closed 2025-08-01.",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-red-canary-1",
  "tags": [
    "tracker",
    "managed-security"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-reliaquest-1",
  "title": "ReliaQuest Growth Equity Funding",
  "organization": "ReliaQuest, LLC",
  "publicationDate": "2025-03-31",
  "economicPeriod": "March 2025",
  "canonicalUrl": "https://reliaquest.com/news-and-press/reliaquest-raises-more-than-500-million-in-funding-at-a-valuation-of-3-4-billion/",
  "excerpt": "ReliaQuest raised more than $500 million in funding at a $3.4 billion valuation, led by EQT, KKR, and FTV Capital, with Ten Eleven Ventures and Finback Investment Partners participating. Company states ARR surpassed $300 million, growing more than 30% year over year, and operating profitably.",
  "sourceClass": "OFFICIAL",
  "interpretation": "",
  "limitations": "",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-reliaquest-1",
  "tags": [
    "tracker",
    "managed-security"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-rubrik-1",
  "title": "Rubrik Announces Second Quarter Fiscal 2027 Financial Results",
  "organization": "Rubrik, Inc.",
  "publicationDate": "2026-08-27",
  "economicPeriod": "Q2 FY2027 (quarter ended 2026-07-31)",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/0001943896/000194389626000055/rubrikinc-991pressrelease7.htm",
  "excerpt": "Revenue of $427.3 million, up 38% year-over-year; Subscription ARR of $1.66 billion, up 33% year-over-year.",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "Company-reported unaudited quarterly results, filed as an exhibit to an SEC Form 8-K.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-rubrik-1",
  "tags": [
    "tracker",
    "data"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-rubrik-2",
  "title": "Rubrik Announces First Quarter Fiscal 2027 Financial Results",
  "organization": "Rubrik, Inc.",
  "publicationDate": "2026-04-30",
  "economicPeriod": "Q1 FY2027 (quarter ended 2026-04-30)",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/0001943896/000194389626000047/rbrk-20260430.htm",
  "excerpt": "Revenue of $387.1 million, up 39% year-over-year; Subscription ARR of $1.565 billion, up 32% year-over-year.",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "Company-reported unaudited quarterly results filed as an SEC exhibit; the underlying research did not separately record a release date distinct from the period-end date.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-rubrik-2",
  "tags": [
    "tracker",
    "data"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-rubrik-3",
  "title": "Rubrik Promotes Jesse Green to Chief Revenue Officer",
  "organization": "Rubrik, Inc.",
  "publicationDate": "2026-02-06",
  "economicPeriod": "N/A (leadership announcement)",
  "canonicalUrl": "https://ir.rubrik.com/news-events/press-releases/news-details/2026/Rubrik-Promotes-Jesse-Green-to-Chief-Revenue-Officer/default.aspx",
  "excerpt": "Brian McCarthy, President of Global Sales & Field Operations, resigned effective February 6, 2026; Jesse Green, previously President of Rubrik Americas, was promoted to Chief Revenue Officer.",
  "sourceClass": "IR",
  "interpretation": "",
  "limitations": "Company investor-relations press release, corroborated by a related SEC Form 8-K per the underlying research.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-rubrik-3",
  "tags": [
    "tracker",
    "data"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-s1-1",
  "title": "SentinelOne Q2 FY2027 Financial Results",
  "organization": "SentinelOne, Inc.",
  "publicationDate": "2026-08-27",
  "economicPeriod": "Quarter ended 2026-07-31",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/0001583708/000158370826000052/sentineloneq227exhibit991.htm",
  "excerpt": "Revenue of $292 million, up 21% year over year. ARR of $1.218 billion, up 22% year over year. Net new ARR of $56 million, record for a Q2.",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-s1-1",
  "tags": [
    "tracker",
    "endpoint-xdr"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-s1-2",
  "title": "SentinelOne Q1 FY2027 Financial Results",
  "organization": "SentinelOne, Inc.",
  "publicationDate": "2026-05-28",
  "economicPeriod": "Quarter ended 2026-04-30",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/0001583708/000158370826000039/sentineloneq127exhibit991.htm",
  "excerpt": "Revenue of $277 million, up 21% year over year. ARR of $1,163 million, up 23% year over year.",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-s1-2",
  "tags": [
    "tracker",
    "endpoint-xdr"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-s1-3",
  "title": "SentinelOne Restructuring Charges - 8-K Item 2.05",
  "organization": "SentinelOne, Inc.",
  "publicationDate": "2026-05-28",
  "economicPeriod": "May 2026",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/0001583708/000158370826000039/s-20260528.htm",
  "excerpt": "Workforce reduction of 8% with approximately $25 million in charges, including severance, benefits, and related costs.",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-s1-3",
  "tags": [
    "tracker",
    "endpoint-xdr"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-sailpoint-1",
  "title": "SailPoint Q2 FY2027 Earnings Release",
  "organization": "SailPoint, Inc.",
  "publicationDate": "2026-09-10",
  "economicPeriod": "Quarter ended July 31, 2026",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/2030781/000203078126000021/sail-20260731.htm",
  "excerpt": "Revenue $308.8 million, +16.8% YoY; ARR $1,230.7 million, +25.3% YoY; SaaS ARR $846.9 million, +36.0% YoY.",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-sailpoint-1",
  "tags": [
    "tracker",
    "identity"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-sailpoint-2",
  "title": "SailPoint Q1 FY2027 Earnings Release",
  "organization": "SailPoint, Inc.",
  "publicationDate": "2026-06-12",
  "economicPeriod": "Quarter ended April 30, 2026",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/2030781/000203078126000011/sail-20260430.htm",
  "excerpt": "Total revenue $280,142 thousand (Q1 FY2027) vs $230,468 thousand (Q1 FY2026), a $49,674 thousand / 22% increase per the filing's own MD&A table.",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "AUTO-001 fix pass 4, item 6: the tracker previously rounded this to 21.5%; the precise figure from these same two reported dollar values is 21.6% (49,674 / 230,468), which still rounds to the 22% change SailPoint's own MD&A table states.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-sailpoint-2",
  "tags": [
    "tracker",
    "identity"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-snyk-1",
  "title": "Snyk raises $530M on $8.5B valuation to protect applications",
  "organization": "CRN",
  "publicationDate": "2021-09-09",
  "economicPeriod": "N/A (funding announcement)",
  "canonicalUrl": "https://www.crn.com/news/security/snyk-raises-530m-on-8-5b-valuation-to-protect-applications",
  "excerpt": "Snyk raised a $530 million Series F round at an $8.5 billion valuation.",
  "sourceClass": "INDEPENDENT",
  "interpretation": "",
  "limitations": "Trade press report; not confirmed against a direct Snyk primary-source release. Superseded in part by TR-snyk-2, Snyk's own primary-source announcement of a $75M extension to this same Series F round on 2021-09-30; no funding round after 2021 was found in Snyk's newsroom.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-snyk-1",
  "tags": [
    "tracker",
    "appsec"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-snyk-2",
  "title": "Snyk Secures $75 Million in Additional Funding",
  "organization": "Snyk Ltd.",
  "publicationDate": "2021-09-30",
  "economicPeriod": "N/A (funding announcement, extension of the 2021-09-09 Series F round)",
  "canonicalUrl": "https://www.prnewswire.com/news-releases/snyk-secures-75-million-in-additional-funding-301388357.html",
  "excerpt": "Snyk, the leader in developer security, today announced $75 million of funding from Atlassian Ventures and Salesforce Ventures as part of its recent Series F financing. Total capital raised to date: $850 million.",
  "sourceClass": "IR",
  "interpretation": "",
  "limitations": "Company-stated, primary source. Extends the Series F round announced 2021-09-09 at an updated $8.6 billion valuation; not a new priced round. Checked against Snyk's own newsroom listing on PR Newswire; no funding round after this date was found there.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-snyk-2",
  "tags": [
    "tracker",
    "appsec"
  ],
  "retrievedAt": "2026-09-26"
},
{
  "id": "TR-snyk-3",
  "title": "Snyk Closes $196.5 Million Series G Funding at $7.4 Billion Valuation",
  "organization": "Snyk Ltd.",
  "publicationDate": "2022-12-13",
  "economicPeriod": "N/A (funding announcement)",
  "canonicalUrl": "https://snyk.io/news/snyk-closes-196-5-million-series-g-funding-at-7-4-billion-valuation/",
  "excerpt": "Snyk today announced it has closed $196.5 million in Series G funding at a $7.4 billion valuation, led by Qatar Investment Authority (QIA), with participation from Evolution Equity Partners, G Squared, Irving Investors, boldstart ventures, Sands Capital, and Tiger Global.",
  "sourceClass": "IR",
  "interpretation": "",
  "limitations": "AUTO-001 fix pass 4, item 1: supersedes TR-snyk-1/TR-snyk-2's 2021 Series F figures — this Series G round is Snyk's actual most recent priced round. Two blind scorers (score3/opus, score3/sol) caught the tracker still showing the 2021 Series F as Snyk's last round while Snyk's own newsroom lists this later round.",
  "conflictingEvidenceIds": ["TR-snyk-1", "TR-snyk-2"],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-snyk-3",
  "tags": [
    "tracker",
    "appsec"
  ],
  "retrievedAt": "2026-09-30"
},
{
  "id": "TR-snyk-4",
  "title": "Snyk Secures Strategic Investment from ServiceNow to Accelerate Enterprise DevSecOps Transformation",
  "organization": "Snyk Ltd.",
  "publicationDate": "2023-01-24",
  "economicPeriod": "N/A (strategic investment announcement)",
  "canonicalUrl": "https://snyk.io/news/snyk-secures-strategic-investment-from-servicenow-to-accelerate-enterprise-devsecops-transformation/",
  "excerpt": "This latest development comes on the heels of Snyk's announcement of $196.5 million in Series G investment in late 2022.",
  "sourceClass": "IR",
  "interpretation": "",
  "limitations": "ServiceNow's investment amount was not disclosed in this release. Checked against Snyk's own newsroom archive (pages 1-3 of snyk.io/news/); no funding round or strategic investment after this date was found there as of 2026-09-30.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-snyk-4",
  "tags": [
    "tracker",
    "appsec"
  ],
  "retrievedAt": "2026-09-30"
},
{
  "id": "TR-sonatype-1",
  "title": "Vista Acquires Majority Interest in Sonatype",
  "organization": "Sonatype Inc.",
  "publicationDate": "2019-11-18",
  "economicPeriod": "N/A (ownership announcement)",
  "canonicalUrl": "https://www.sonatype.com/press-releases/vista-acquires-majority-interest-in-sonatype",
  "excerpt": "Vista Equity Partners acquired a majority stake in Sonatype; price not disclosed.",
  "sourceClass": "OFFICIAL",
  "interpretation": "",
  "limitations": "Company press release.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-sonatype-1",
  "tags": [
    "tracker",
    "appsec"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-sonatype-2",
  "title": "Sonatype Strengthens Leadership Team for AI-Driven Growth",
  "organization": "Sonatype Inc.",
  "publicationDate": "2026-06-09",
  "economicPeriod": "N/A (leadership announcement)",
  "canonicalUrl": "https://www.sonatype.com/press-releases/sonatype-strengthens-leadership-team-for-ai-driven-growth",
  "excerpt": "Sonatype named Casey Watson as Chief Revenue Officer, Jason McClelland as Chief Marketing Officer, and Sherri Manning as Chief Human Resources Officer.",
  "sourceClass": "OFFICIAL",
  "interpretation": "",
  "limitations": "Company press release.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-sonatype-2",
  "tags": [
    "tracker",
    "appsec"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-sophos-1",
  "title": "Sophos Announces Completion of Take-Private Acquisition by Thoma Bravo",
  "organization": "Thoma Bravo",
  "publicationDate": "2020-03-02",
  "economicPeriod": "March 2020",
  "canonicalUrl": "https://www.thomabravo.com/press-releases/sophos-announces-completion-of-take-private-acquisition-by-thoma-bravo",
  "excerpt": "Sophos Announces Completion of Take-Private Acquisition by Thoma Bravo. Transaction · March 2, 2020.",
  "sourceClass": "OFFICIAL",
  "interpretation": "",
  "limitations": "AUTO-001 fix pass 4, item 9: the prior canonicalUrl (thomabravo.com/press-releases/sophos) 404s; replaced with the actual release, found via Thoma Bravo's own sitemap.xml. The page is a client-streamed Next.js document whose body text is not reachable in plain HTML, so the excerpt here is limited to the headline and the dateline, both directly confirmed in the page's own data payload.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-COLLECT / TR-sophos-1",
  "tags": [
    "tracker",
    "endpoint-xdr"
  ],
  "retrievedAt": "2026-10-02",
  "retrieval": {
    "finalUrl": "https://www.thomabravo.com/press-releases/sophos-announces-completion-of-take-private-acquisition-by-thoma-bravo",
    "sha256": "97d7411a96e6ad170706b4e3059f5ae2027ae4ebe8c5d5d85aa04db914c6f63f",
    "fetchedAt": "2026-10-02T16:05:00Z",
    "locator": "Page headline and dateline"
  }
},
{
  "id": "TR-sophos-2",
  "title": "S&P Rating Action - Sophos Group",
  "organization": "S&P Global Ratings",
  "publicationDate": "2025-12-01",
  "economicPeriod": "December 2025",
  "canonicalUrl": "https://app.researchpool.com/index.php/provider/s-p-global",
  "excerpt": "S&P affirmed Sophos' B- rating and noted expected need to refinance 2027 maturities.",
  "sourceClass": "INDEPENDENT",
  "interpretation": "",
  "limitations": "Agency rating actions republished through third-party aggregator; original agency pages not directly verified this session.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-sophos-2",
  "tags": [
    "tracker",
    "endpoint-xdr"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-sophos-3",
  "title": "Moody's Rating Action - Sophos Group",
  "organization": "Moody's Investors Service",
  "publicationDate": "2026-03-01",
  "economicPeriod": "March 2026",
  "canonicalUrl": "https://app.researchpool.com/index.php/provider/moodys-investors-service",
  "excerpt": "Moody's downgraded Sophos to B3 from B2, with outlook revised to stable.",
  "sourceClass": "INDEPENDENT",
  "interpretation": "",
  "limitations": "Agency rating actions republished through third-party aggregator; original agency pages not directly verified this session.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-sophos-3",
  "tags": [
    "tracker",
    "endpoint-xdr"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-splunk-1",
  "title": "Splunk - Cisco Acquisition",
  "organization": "Cisco Systems, Inc.",
  "publicationDate": "2024-03-18",
  "economicPeriod": "March 2024",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/858877/000119312524070175/d783088dex991.htm",
  "excerpt": "Cisco completed its acquisition of Splunk for $157 per share cash, approximately $28 billion in equity value as announced, $27 billion as closed.",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-splunk-1",
  "tags": [
    "tracker",
    "secops"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-splunk-2",
  "title": "Cisco Restructuring Charges - 8-K Item 2.05",
  "organization": "Cisco Systems, Inc.",
  "publicationDate": "2026-05-13",
  "economicPeriod": "May 2026",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/858877/000085887726000075/csco-20260513.htm",
  "excerpt": "Cisco disclosed up to $1 billion pre-tax restructuring charges to invest in silicon, optics, security, and artificial intelligence, including $450 million in Q4 FY2026.",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "Cisco company-wide restructuring; not Splunk-specific by name.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-splunk-2",
  "tags": [
    "tracker",
    "secops"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-surepath-1",
  "title": "F5 Form 10-Q (quarter ended June 30, 2026)",
  "organization": "F5, Inc.",
  "publicationDate": "2026-06-15",
  "economicPeriod": "N/A (acquisition disclosure)",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/1048695/000104869526000067/ffiv-20260630.htm",
  "excerpt": "F5 completed its acquisition of SurePath AI, Inc. on June 15, 2026, for $50.1 million, recording $39.1 million of goodwill; F5 states the acquisition's impact on operating results was immaterial.",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "Company SEC Form 10-Q.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-surepath-1",
  "tags": [
    "tracker",
    "ai-security"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-sysdig-1",
  "title": "Sysdig Names Hatem Naguib as CEO to Lead Next Generation of AI-Driven Cloud Security",
  "organization": "Sysdig",
  "publicationDate": "2026-06-16",
  "economicPeriod": "June 2026",
  "canonicalUrl": "https://sysdig.com/press-releases/sysdig-names-hatem-naguib-as-ceo-to-lead-next-generation-of-ai-driven-cloud-security",
  "excerpt": "Founder Loris Degioanni (CTO) confirms Hatem Naguib as CEO. Board member Enrique Salem, a partner at Bain Capital Ventures and former Symantec CEO, is quoted. Confirmed privately held.",
  "sourceClass": "OFFICIAL",
  "interpretation": "",
  "limitations": "This release names one board member (Enrique Salem, Bain Capital Ventures); it does not confirm the previously listed full board (Accel, Premji Invest, Third Point Ventures, Permira), which is dropped for lack of a specific source.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-FITFIX2 / TR-sysdig-1",
  "tags": [
    "tracker",
    "cloud"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-tenable-1",
  "title": "Tenable Holdings Q2 2026 Financial Results",
  "organization": "Tenable Holdings, Inc.",
  "publicationDate": "2026-07-29",
  "economicPeriod": "Quarter ended 2026-06-30",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/0001660280/000166028026000032/q22026financialresults-ear.htm",
  "excerpt": "Revenue of $268.5 million, up 8.6% year over year. Subscription revenue of $248.3 million. Guidance for Q3 2026: $270.0 million to $273.0 million. FY2026 guidance: $1.075 billion to $1.081 billion.",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-tenable-1",
  "tags": [
    "tracker",
    "exposure"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-tenable-2",
  "title": "Tenable Convertible Notes Issuance",
  "organization": "Tenable Holdings, Inc.",
  "publicationDate": "2026-09-15",
  "economicPeriod": "September 2026",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/1660280/000166028026000039/tenb-20260910.htm",
  "excerpt": "Tenable completed the issuance of $800 million of 0.25% convertible senior notes due 2031, upsized from the originally planned $725 million.",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "Capital-markets transaction; not a distress signal.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-tenable-2",
  "tags": [
    "tracker",
    "exposure"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-tenable-3",
  "title": "Tenable Holdings Q1 2026 Financial Results",
  "organization": "Tenable Holdings, Inc.",
  "publicationDate": "2026-04-29",
  "economicPeriod": "Quarter ended 2026-03-31",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/1660280/000166028026000020/q12026financialresults-ear.htm",
  "excerpt": "Revenue of $262.1 million, year-over-year growth of 9.6%.",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "AUTO-001 fix pass 4, item 7: added so the tracker's prior-quarter cell is no longer bare — the tracker previously had no citation for Tenable's Q1 2026 figures at all. The company's own stated 9.6% YoY figure matches the precise computation from its own reported dollar values ($262,058K vs $239,137K, confirmed against the comparative income statement in Tenable's own Q2 2026 10-Q).",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-tenable-3",
  "tags": [
    "tracker",
    "exposure"
  ],
  "retrievedAt": "2026-10-01"
},
{
  "id": "TR-tines-1",
  "title": "Goldman, SoftBank Back AI Startup Tines Valued at $1.13 Billion",
  "organization": "Bloomberg",
  "publicationDate": "2025-02-11",
  "economicPeriod": "February 2025",
  "canonicalUrl": "https://www.bloomberg.com/news/articles/2025-02-11/goldman-softbank-back-ai-startup-tines-valued-at-1-13-billion",
  "excerpt": "Tines raised $125 million in Series C funding at a $1.13 billion valuation, led by Goldman Sachs and SoftBank.",
  "sourceClass": "INDEPENDENT",
  "interpretation": "",
  "limitations": "Company did not publish a dedicated press-release URL for this round; Bloomberg's report is corroborated by the Irish Times, 2026-07-28, and listed on Tines' own newsroom page.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-FITFIX2 / TR-tines-1",
  "tags": [
    "tracker",
    "secops"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-torq-1",
  "title": "Torq Series D Funding",
  "organization": "Torq",
  "publicationDate": "2026-01-09",
  "economicPeriod": "January 2026",
  "canonicalUrl": "https://torq.io/news/torq-seriesd/",
  "excerpt": "Torq raised $140 million in Series D funding at a $1.2 billion valuation, led by Merlin Ventures, with participation from Evolution Equity Partners, Notable Capital, Bessemer Venture Partners, Insight Partners, and Greenfield Partners.",
  "sourceClass": "OFFICIAL",
  "interpretation": "",
  "limitations": "",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-torq-1",
  "tags": [
    "tracker",
    "secops"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-trend-1",
  "title": "Trend Micro Q2 2026 Earnings Results",
  "organization": "Trend Micro Incorporated",
  "publicationDate": "2026-08-13",
  "economicPeriod": "Quarter ended 2026-06-30",
  "canonicalUrl": "https://newsroom.trendmicro.com/2026-08-13-Trend-Micro-Reports-Earnings-Results-for-Q2-2026",
  "excerpt": "ARR exceeded $1.7 billion, up 5% year over year. Total company net sales up 13% YoY; consolidated net sales of 74,739 million yen (US $468 million at 159.47 JPY = 1 USD) for the quarter. FY2026 operating-income guidance cut from ¥56.4 billion to ¥44.4 billion due to rising artificial-intelligence and cloud-computing token costs.",
  "sourceClass": "IR",
  "interpretation": "",
  "limitations": "AUTO-001 fix pass 4, item 7: added the revenue-growth figure (previously bare in the tracker). The release states the 13% YoY net-sales growth as a whole percent and does not give the prior-year yen figure in its own text (only in a financial-supplement table this evidence record does not reach), so the tracker stores the company's own whole-percent figure rather than a fabricated one-decimal value. Company is Tokyo-listed; not an active SEC filer.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-trend-1",
  "tags": [
    "tracker",
    "endpoint-xdr"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-trustwave-1",
  "title": "LevelBlue Completes Trustwave Acquisition",
  "organization": "LevelBlue",
  "publicationDate": "2025-08-19",
  "economicPeriod": "August 2025",
  "canonicalUrl": "https://www.levelblue.com/newsroom/press-releases/levelblue-completes-acquisition-of-trustwave-to-form-the-worlds-largest-managed-security-services-provider",
  "excerpt": "LevelBlue completed its acquisition of Trustwave Holdings, which states combined operations serve over 30,000 customers with annual revenues exceeding $1 billion.",
  "sourceClass": "OFFICIAL",
  "interpretation": "",
  "limitations": "Revenue figure is combined LevelBlue + Trustwave; not broken out for Trustwave alone.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-trustwave-1",
  "tags": [
    "tracker",
    "managed-security"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-upwind-1",
  "title": "Upwind Series B Funding Announcement",
  "organization": "Upwind Security",
  "publicationDate": "2026-01-26",
  "economicPeriod": "January 2026",
  "canonicalUrl": "https://www.upwind.io/feed/building-next-wave-cloud-security-upwind",
  "excerpt": "Series B funding: $250M led by Bessemer Venture Partners, achieving unicorn status (>$1B valuation).",
  "sourceClass": "IR",
  "interpretation": "",
  "limitations": "",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-upwind-1",
  "tags": [
    "tracker",
    "cloud"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-varonis-1",
  "title": "Varonis Reports Second Quarter 2026 Financial Results",
  "organization": "Varonis Systems, Inc.",
  "publicationDate": "2026-07-28",
  "economicPeriod": "Q2 2026 (quarter ended 2026-06-30)",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/0001361113/000117184326004948/exh_991.htm",
  "excerpt": "Revenue of $180.0 million, up 18.3% year-over-year; Total SaaS ARR of $726.0 million, up 52% year-over-year (25% excluding conversions).",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "Company-reported unaudited quarterly results, filed as an exhibit to an SEC Form 8-K.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-varonis-1",
  "tags": [
    "tracker",
    "data"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-varonis-2",
  "title": "Varonis Reports Third Quarter 2025 Financial Results",
  "organization": "Varonis Systems, Inc.",
  "publicationDate": "2025-10-29",
  "economicPeriod": "Q3 2025 (quarter ended 2025-09-30)",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/1361113/000117184325006721/exh_991.htm",
  "excerpt": "Announced a 5% headcount reduction (approximately 120 employees) and disclosed plans to end-of-life the company's self-hosted, on-premises product effective December 31, 2026.",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "Company-reported disclosure filed as an SEC exhibit; the underlying research also cites an earnings-call transcript quoting CEO Yakov Faitelson on the same layoff.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-varonis-2",
  "tags": [
    "tracker",
    "data"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-veeam-1",
  "title": "Veeam (Wikipedia)",
  "organization": "Wikipedia",
  "publicationDate": "2026-09-25",
  "economicPeriod": "N/A (company background)",
  "canonicalUrl": "https://en.wikipedia.org/wiki/Veeam",
  "excerpt": "Insight Partners holds a majority stake in Veeam Software, in a deal reported closed on or about January 9, 2020, for approximately $5 billion.",
  "sourceClass": "INDEPENDENT",
  "interpretation": "",
  "limitations": "Secondary source only; the research notes Veeam's own press release on the Insight Partners deal was not reachable this pass, so deal date and value should be treated as reported rather than confirmed.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-veeam-1",
  "tags": [
    "tracker",
    "data"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-veeam-2",
  "title": "Veeam Acquires Securiti AI",
  "organization": "Veeam Software",
  "publicationDate": "2025-12-11",
  "economicPeriod": "N/A (acquisition announcement)",
  "canonicalUrl": "https://www.veeam.com/news/veeam-acquires-securiti-ai.html",
  "excerpt": "Veeam completed its acquisition of Securiti AI, a data security posture management and AI-governance company, for $1.725 billion; Securiti founder and CEO Rehan Jalil joined Veeam as President of Security and AI, with approximately 600 Securiti employees integrated.",
  "sourceClass": "OFFICIAL",
  "interpretation": "",
  "limitations": "Company press release.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-veeam-2",
  "tags": [
    "tracker",
    "data"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-veeam-4",
  "title": "Veeam, the World's #1 Leader in Data Resilience, Welcomes New Investors with a $15 Billion Valuation",
  "organization": "Veeam Software",
  "publicationDate": "2024-12-04",
  "economicPeriod": "N/A (secondary equity offering announcement)",
  "canonicalUrl": "https://www.veeam.com/company/press-release/veeam-the-worlds-1-leader-in-data-resilience-welcomes-new-investors-with-a-dollar15-billion-valuation.html",
  "excerpt": "Insight Partners owned Veeam expands investor base in a $2 billion secondary equity offering led by TPG with participation from Temasek, Neuberger Berman Capital Solutions, and others...Insight Partners remains the largest shareholder.",
  "sourceClass": "OFFICIAL",
  "interpretation": "",
  "limitations": "AUTO-001 fix pass 4, item 1: supersedes TR-veeam-1 (a Wikipedia secondary source for a reported 2020 deal) with Veeam's own primary release.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-veeam-4",
  "tags": [
    "tracker",
    "data"
  ],
  "retrievedAt": "2026-09-30"
},
{
  "id": "TR-veracode-1",
  "title": "Veracode Receives Major Growth Investment from TA Associates",
  "organization": "Veracode, Inc.",
  "publicationDate": "2022-03-15",
  "economicPeriod": "N/A (ownership announcement)",
  "canonicalUrl": "https://www.veracode.com/press-release/veracode-receives-major-growth-investment-from-ta-associates/",
  "excerpt": "TA Associates signed a definitive agreement for a majority growth-investment stake in Veracode at a $2.5 billion valuation, with Thoma Bravo retaining a minority position; the transaction was expected to close in Q2 2022.",
  "sourceClass": "OFFICIAL",
  "interpretation": "",
  "limitations": "The announcement gives an expected close of Q2 2022; a precise closing date was not independently confirmed.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-FITFIX2 / TR-veracode-1",
  "tags": [
    "tracker",
    "appsec"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-witnessai-1",
  "title": "WitnessAI Raises $58M to Help Enterprises Move Faster with AI Safely",
  "organization": "WitnessAI",
  "publicationDate": "2026-01-13",
  "economicPeriod": "N/A (funding announcement)",
  "canonicalUrl": "https://witness.ai/blog/witnessai-raises-58m-to-help-enterprises-move-faster-with-ai-safely/",
  "excerpt": "WitnessAI raised a $58 million strategic funding round led by Sound Ventures, with Fin Capital, Samsung Ventures, Qualcomm Ventures, Forgepoint Capital Partners, Silver Buckshot Ventures, and existing investors Google Ventures and Ballistic Ventures participating. The release states '500% ARR growth — just in the past 12 months' and headcount up 5x (unaudited).",
  "sourceClass": "OFFICIAL",
  "interpretation": "",
  "limitations": "Company blog/press release.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-witnessai-1",
  "tags": [
    "tracker",
    "ai-security"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-wiz-1",
  "title": "Wiz Acquisition by Google/Alphabet Closing",
  "organization": "Alphabet Inc.",
  "publicationDate": "2026-04-30",
  "economicPeriod": "Q1 2026",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/1652044/000165204426000048/goog-20260331.htm",
  "excerpt": "Wiz acquisition closed March 11, 2026 for $29.5 billion after purchase price adjustments.",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-wiz-1",
  "tags": [
    "tracker",
    "cloud"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-xage-1",
  "title": "Xage Security hits record growth",
  "organization": "Yahoo Finance",
  "publicationDate": "2026-03-18",
  "economicPeriod": "N/A (company update)",
  "canonicalUrl": "https://finance.yahoo.com/news/xage-security-hits-record-growth-120000615.html",
  "excerpt": "Xage Security reported 81% year-over-year revenue growth and 102% year-over-year customer growth, a 50% rise in net-new revenue between Q3 and Q4 2025, and over 100% growth in net-new revenue from Q4 2025 into Q1 2026 (unaudited, no absolute dollar revenue figure disclosed). The company also closed a $15 million equity round led by Piva Capital in December 2025.",
  "sourceClass": "INDEPENDENT",
  "interpretation": "",
  "limitations": "Trade-press relay of company-stated figures; not independently confirmed against a direct Xage or Piva Capital primary release, though an SEC Form D filed the same date (2026-03-18) is consistent with a Reg D raise around this period.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-xage-1",
  "tags": [
    "tracker",
    "ot-iot"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-zenity-1",
  "title": "Zenity Raises $125 Million to Secure the Era of 1 Billion AI Agents",
  "organization": "Zenity",
  "publicationDate": "2026-08-03",
  "economicPeriod": "N/A (funding announcement)",
  "canonicalUrl": "https://zenity.io/company-overview/newsroom/company-news/zenity-raises-125-million-to-secure-the-era-of-1-billion-ai-agents",
  "excerpt": "Zenity raised a $125 million Series C round led by Norwest, with Qumra Capital, SoftBank Vision Fund 2, Hitachi Ventures, LG Technology Ventures, Vertex Ventures, Third Point Ventures, DTCP, and Intel Capital participating. The release states Zenity 'has tripled revenue in each of the past two years and is on track to triple revenue again this year' (unaudited).",
  "sourceClass": "OFFICIAL",
  "interpretation": "",
  "limitations": "Company press release.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-zenity-1",
  "tags": [
    "tracker",
    "ai-security"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-zscaler-1",
  "title": "Zscaler Q4 FY2026 Earnings Release",
  "organization": "Zscaler, Inc.",
  "publicationDate": "2026-09-03",
  "economicPeriod": "Q4 FY2026, ended 2026-07-31",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/1713683/000171368326000156/zs-07312026_991.htm",
  "excerpt": "Revenue $898.2 million, +25% YoY; ARR $3,771 million, +25% YoY (20% excluding Red Canary acquisition).",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "Red Canary acquisition contributed $141M ARR; organic growth rate was 20%.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-zscaler-1",
  "tags": [
    "tracker",
    "network-sase",
    "public-company"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-zscaler-2",
  "title": "Zscaler Q3 FY2026 Earnings Release",
  "organization": "Zscaler, Inc.",
  "publicationDate": "2026-05-26",
  "economicPeriod": "Q3 FY2026, ended 2026-04-30",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/1713683/000171368326000095/zs-04302026_991.htm",
  "excerpt": "Revenue $850.5 million, +25% YoY; ARR $3,525 million, +25% YoY (21% excluding Red Canary).",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-zscaler-2",
  "tags": [
    "tracker",
    "network-sase"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-zscaler-3",
  "title": "Zscaler Q4 FY2026 Non-GAAP Reconciliation",
  "organization": "Zscaler, Inc.",
  "publicationDate": "2026-09-03",
  "economicPeriod": "Q4 FY2026, ended 2026-07-31",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/1713683/000171368326000156/zs-07312026_991.htm",
  "excerpt": "Restructuring and other charges of $5.5 million in Q4 FY2026 and $10.3 million for full FY2026, described as severance and termination benefits.",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-zscaler-3",
  "tags": [
    "tracker",
    "network-sase"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-zscaler-4",
  "title": "Zscaler Executive Leadership Changes",
  "organization": "Zscaler, Inc.",
  "publicationDate": "2026-09-24",
  "economicPeriod": "Quarter ended July 31, 2026",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/1713683/000171368326000193/zs-20260924.htm",
  "excerpt": "CRO Mike Rich stepping down effective October 1, 2026, succeeded by Ross Tackett. EVP Raj Judge resigned board seat effective April 16, 2026, with employment ending July 31, 2026.",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "Changes do not affect CEO or CFO positions.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-zscaler-4",
  "tags": [
    "tracker",
    "network-sase"
  ],
  "retrievedAt": "2026-09-25"
},
{
  "id": "TR-arctic-wolf-1",
  "title": "Arctic Wolf Acquires Exposure Assessment Platform Visionary Sevco Security",
  "organization": "Arctic Wolf Networks, Inc.",
  "publicationDate": "2026-02-23",
  "economicPeriod": "February 2026",
  "canonicalUrl": "https://arcticwolf.com/resources/press-releases/arctic-wolf-acquires-exposure-assessment-platform-visionary-sevco-security/",
  "excerpt": "Arctic Wolf today announced it has acquired Sevco Security, an innovator in exposure assessment platforms. Sevco's cloud-native technology will operate on the Arctic Wolf Aurora Platform.",
  "sourceClass": "IR",
  "interpretation": "",
  "limitations": "The press release does not state a price or closing date.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-arctic-wolf-1",
  "tags": [
    "tracker",
    "managed-security"
  ],
  "retrievedAt": "2026-09-26",
  "retrieval": {
    "finalUrl": "https://arcticwolf.com/resources/press-releases/arctic-wolf-acquires-exposure-assessment-platform-visionary-sevco-security/",
    "sha256": "4c60f7707a035a7da3d677018fc02db189397f59f62d2d06247043bfc9b738b9",
    "fetchedAt": "2026-09-26T17:10:00Z",
    "locator": "Press release, first paragraph"
  }
},
{
  "id": "TR-armis-2",
  "title": "ServiceNow Fourth Quarter and Full Year 2025 Financial Results (Form 8-K EX-99.1)",
  "organization": "ServiceNow, Inc.",
  "publicationDate": "2026-01-28",
  "economicPeriod": "Q4 FY2025",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/1373715/000137371526000005/erq4fy25.htm",
  "excerpt": "ServiceNow announced its intent to acquire Armis to create a unified, end-to-end security exposure and operations stack... The transaction is expected to close in the second half of 2026.",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "The document does not state a price. It does not give the date the deal was announced; the date used is the filing date.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-armis-2",
  "tags": [
    "tracker",
    "ot-iot"
  ],
  "retrievedAt": "2026-09-26",
  "retrieval": {
    "finalUrl": "https://www.sec.gov/Archives/edgar/data/1373715/000137371526000005/erq4fy25.htm",
    "sha256": "bd192340730b12aa6a863b22797214d3c01727733de69a6b436684052f0acd97",
    "fetchedAt": "2026-09-26T17:08:00Z",
    "locator": "EX-99.1, Acquisitions section"
  }
},
{
  "id": "TR-checkpoint-5",
  "title": "Check Point Form 6-K: closing of $2.0 billion convertible senior notes offering",
  "organization": "Check Point Software Technologies Ltd.",
  "publicationDate": "2025-12-08",
  "economicPeriod": "December 2025",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/1015922/000117891325004030/zk2534094.htm",
  "excerpt": "On December 8, 2025, Check Point closed the previously announced offering of $1.75 billion principal amount of 0.00% convertible senior notes due 2030... including $250 million of Additional Convertible Notes... resulting in a total principal amount of $2.0 billion. The net proceeds from the sale of the Convertible Notes were approximately $1.97 billion.",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-checkpoint-5",
  "tags": [
    "tracker",
    "network-sase"
  ],
  "retrievedAt": "2026-09-26",
  "retrieval": {
    "finalUrl": "https://www.sec.gov/Archives/edgar/data/1015922/000117891325004030/zk2534094.htm",
    "sha256": "673de770671cfa08ba8e9bb2e2ae5f9e443e715be850daa6be5de9b9a6fbeb80",
    "fetchedAt": "2026-09-26T17:07:00Z",
    "locator": "Explanatory note and Purchase Agreement sections"
  }
},
{
  "id": "TR-cyera-5",
  "title": "Cyera Raises $400M to Meet Rapidly Growing Demand for AI Security Among Enterprises",
  "organization": "Cyera",
  "publicationDate": "2026-01-08",
  "economicPeriod": "January 2026",
  "canonicalUrl": "https://www.cyera.com/press-releases/cyera-raises-400m-to-meet-rapidly-growing-demand-for-ai-security-among-enterprises",
  "excerpt": "Cyera announced a $400 million Series F funding round, bringing its total funding to over $1.7 billion... triples the company's valuation from a year ago to $9 billion. The round was led by funds managed by Blackstone.",
  "sourceClass": "OFFICIAL",
  "interpretation": "",
  "limitations": "",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-cyera-5",
  "tags": ["tracker"],
  "retrievedAt": "2026-09-26",
  "retrieval": {
    "finalUrl": "https://www.cyera.com/press-releases/cyera-raises-400m-to-meet-rapidly-growing-demand-for-ai-security-among-enterprises",
    "sha256": "9576a4e2104bdd5ba074b6e48a6dd50f0c9e7fc0ab0cecfc386bd344cb95f4cb",
    "fetchedAt": "2026-09-26T17:30:00Z",
    "locator": "Opening paragraphs of the press release"
  }
},
{
  "id": "TR-delinea-4",
  "title": "Delinea and StrongDM to Unite to Redefine Identity Security for the Agentic AI Era",
  "organization": "Delinea",
  "publicationDate": "2026-01-15",
  "economicPeriod": "January 2026",
  "canonicalUrl": "https://delinea.com/news/delinea-strongdm-to-unite-redefine-identity-security-for-the-ai-era",
  "excerpt": "Delinea... today announced it has signed a definitive agreement to acquire StrongDM, the universal access management company purpose-built for modern engineering, DevOps, and AI-driven environments.",
  "sourceClass": "OFFICIAL",
  "interpretation": "",
  "limitations": "",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-delinea-4",
  "tags": ["tracker"],
  "retrievedAt": "2026-09-26",
  "retrieval": {
    "finalUrl": "https://delinea.com/news/delinea-strongdm-to-unite-redefine-identity-security-for-the-ai-era",
    "sha256": "1a75e7f25cee91769438182502d006eebf5cd153029c80c9c05a9885ba67e6e7",
    "fetchedAt": "2026-09-26T17:30:00Z",
    "locator": "Dateline and first paragraph"
  }
},
{
  "id": "TR-delinea-5",
  "title": "Delinea Completes StrongDM Acquisition to Secure AI Agents with Continuous Identity Authorization",
  "organization": "Delinea",
  "publicationDate": "2026-03-05",
  "economicPeriod": "March 2026",
  "canonicalUrl": "https://www.globenewswire.com/news-release/2026/03/05/3250113/0/en/delinea-completes-strongdm-acquisition-to-secure-ai-agents-with-continuous-identity-authorization.html",
  "excerpt": "Delinea... has completed its acquisition of StrongDM, the universal access management company purpose-built for modern engineering, DevOps, and AI-driven environments.",
  "sourceClass": "OFFICIAL",
  "interpretation": "",
  "limitations": "",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-delinea-5",
  "tags": ["tracker"],
  "retrievedAt": "2026-09-26",
  "retrieval": {
    "finalUrl": "https://www.globenewswire.com/news-release/2026/03/05/3250113/0/en/delinea-completes-strongdm-acquisition-to-secure-ai-agents-with-continuous-identity-authorization.html",
    "sha256": "d18b79e5bfb9b2a1c3a1dbf1bf0e7d2001a7487989a68f6dc18067086a5329cc",
    "fetchedAt": "2026-09-26T17:30:00Z",
    "locator": "First paragraph"
  }
},
{
  "id": "TR-dragos-2",
  "title": "Accenture to Strengthen Critical Infrastructure Defense with End-to-End Cybersecurity Platform (release with closing note)",
  "organization": "Accenture plc",
  "publicationDate": "2026-09-16",
  "economicPeriod": "June 2026 announcement; closing note September 2026",
  "canonicalUrl": "https://newsroom.accenture.com/news/2026/accenture-to-strengthen-critical-infrastructure-defense-with-end-to-end-cybersecurity-platform-in-age-of-ai-driven-cyber-threats-and-geopolitical-risk",
  "excerpt": "NOTE: The acquisition of NetRise closed on July 31, 2026, the majority investment in Dragos closed on September 16, 2026 and the acquisition of runZero closed on September 17, 2026. As part of the closing terms, NetRise and runZero have been acquired by Dragos.",
  "sourceClass": "OFFICIAL",
  "interpretation": "",
  "limitations": "",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-dragos-2",
  "tags": ["tracker"],
  "retrievedAt": "2026-09-26",
  "retrieval": {
    "finalUrl": "https://newsroom.accenture.com/news/2026/accenture-to-strengthen-critical-infrastructure-defense-with-end-to-end-cybersecurity-platform-in-age-of-ai-driven-cyber-threats-and-geopolitical-risk",
    "sha256": "91aad377f4cc2f569acb94449e8bd4255e51616a7ddc90966f1bac0d62c740b3",
    "fetchedAt": "2026-09-26T17:30:00Z",
    "locator": "Note at the top of the release"
  }
},
{
  "id": "TR-exabeam-2",
  "title": "Exabeam Appoints Pete Harteveld as CEO",
  "organization": "Exabeam (published by Thoma Bravo)",
  "publicationDate": "2025-10-08",
  "economicPeriod": "October 2025",
  "canonicalUrl": "https://www.thomabravo.com/press-releases/exabeam-appoints-pete-harteveld-as-ceo",
  "excerpt": "Exabeam... today announced Pete Harteveld as Chief Executive Officer. The leadership transition follows the decision by Chris O'Malley to step into retirement after three years of dedicated service.",
  "sourceClass": "OFFICIAL",
  "interpretation": "",
  "limitations": "",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-exabeam-2",
  "tags": ["tracker"],
  "retrievedAt": "2026-09-26",
  "retrieval": {
    "finalUrl": "https://www.thomabravo.com/press-releases/exabeam-appoints-pete-harteveld-as-ceo",
    "sha256": "0581fe913bca27e4edfca54c8f8e399ee412bbc4df02ff3ed20041c9f4999cbd",
    "fetchedAt": "2026-09-26T17:30:00Z",
    "locator": "First two paragraphs"
  }
},
{
  "id": "TR-commvault-3",
  "title": "Commvault Systems Form 8-K, Item 5.02 (CFO resignation)",
  "organization": "Commvault Systems, Inc.",
  "publicationDate": "2025-12-04",
  "economicPeriod": "December 2025",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/1169561/000116956125000094/cvlt-20251130.htm",
  "excerpt": "On November 30, 2025, Jennifer DiRico notified Commvault Systems, Inc. that she will be resigning from her position as Chief Financial Officer of the Company at the end of the calendar year.",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-commvault-3",
  "tags": ["tracker"],
  "retrievedAt": "2026-09-26",
  "retrieval": {
    "finalUrl": "https://www.sec.gov/Archives/edgar/data/1169561/000116956125000094/cvlt-20251130.htm",
    "sha256": "e486c064a7184b058382ed0dc66297aa50f3b0509f5a3c899e60b595811a9828",
    "fetchedAt": "2026-09-26T17:30:00Z",
    "locator": "Item 5.02"
  }
},
{
  "id": "TR-commvault-4",
  "title": "Commvault Systems Form 8-K, Item 5.02 (CFO appointment)",
  "organization": "Commvault Systems, Inc.",
  "publicationDate": "2026-04-13",
  "economicPeriod": "April 2026",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/1169561/000116956126000008/cvlt-20260408.htm",
  "excerpt": "On April 13, 2026, Commvault Systems, Inc. announced the appointment of Mr. Gary Merrill as Chief Financial Officer and principal financial officer. As of the Effective Date, Mr. Merrill will cease to serve as the Company's Chief Commercial Officer.",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-commvault-4",
  "tags": ["tracker"],
  "retrievedAt": "2026-09-26",
  "retrieval": {
    "finalUrl": "https://www.sec.gov/Archives/edgar/data/1169561/000116956126000008/cvlt-20260408.htm",
    "sha256": "71430172f7360cda62b937526cb70b041c512e5f19aa03adb20df45cbd5097c2",
    "fetchedAt": "2026-09-26T17:30:00Z",
    "locator": "Item 5.02"
  }
},
{
  "id": "TR-okta-3",
  "title": "Okta Announces Second Quarter Fiscal Year 2027 Financial Results (Exhibit 99.1)",
  "organization": "Okta, Inc.",
  "publicationDate": "2026-08-26",
  "economicPeriod": "Quarter ended July 31, 2026",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/1660134/000166013426000068/okta-7312026_ex991.htm",
  "excerpt": "cRPO, which represents subscription backlog expected to be recognized over the next 12 months, was $2.585 billion, up 14% compared to the second quarter of fiscal 2026.",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-okta-3",
  "tags": [
    "tracker",
    "identity"
  ],
  "retrievedAt": "2026-09-26",
  "retrieval": {
    "finalUrl": "https://www.sec.gov/Archives/edgar/data/1660134/000166013426000068/okta-7312026_ex991.htm",
    "sha256": "f1280f38f9a28f3461acdb1bbd4955575be2ea13041863d3913d6103d1198c6e",
    "fetchedAt": "2026-09-26T17:40:00Z",
    "locator": "Second Quarter Fiscal 2027 Financial Highlights, RPO bullet"
  }
},
{
  "id": "TR-panw-4",
  "title": "Palo Alto Networks to Acquire Chronosphere (Form 8-K, Exhibit 99.2)",
  "organization": "Palo Alto Networks, Inc.",
  "publicationDate": "2025-11-19",
  "economicPeriod": "November 2025",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/1327567/000132756725000032/ex992pressrelease.htm",
  "excerpt": "Under the terms of the agreement, Palo Alto Networks will acquire Chronosphere for a total consideration of $3.35 billion, to be paid in cash and replacement equity awards, subject to adjustments.",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-panw-4",
  "tags": [
    "tracker",
    "secops"
  ],
  "retrievedAt": "2026-09-26",
  "retrieval": {
    "finalUrl": "https://www.sec.gov/Archives/edgar/data/1327567/000132756725000032/ex992pressrelease.htm",
    "sha256": "e6bd890c0e575a32ecb76c56fe030a26c4fdcf791d3dcc4be8e5c4bd10e1e564",
    "fetchedAt": "2026-09-26T17:40:00Z",
    "locator": "Paragraph 6, terms of the agreement"
  }
},
{
  "id": "TR-panw-5",
  "title": "Palo Alto Networks Completes Chronosphere Acquisition (Form 8-K, Item 7.01, Exhibit 99.1)",
  "organization": "Palo Alto Networks, Inc.",
  "publicationDate": "2026-01-29",
  "economicPeriod": "January 2026",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/1327567/000119312526029489/d884183dex991.htm",
  "excerpt": "Palo Alto Networks (NASDAQ: PANW), the global cybersecurity leader, today announced it has completed its acquisition of Chronosphere.",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-panw-5",
  "tags": [
    "tracker",
    "secops"
  ],
  "retrievedAt": "2026-09-26",
  "retrieval": {
    "finalUrl": "https://www.sec.gov/Archives/edgar/data/1327567/000119312526029489/d884183dex991.htm",
    "sha256": "0a91f9c95ec918e067392b6c2644ea61b5bfdc1372497e568428140ac534dcda",
    "fetchedAt": "2026-09-26T17:40:00Z",
    "locator": "Opening paragraph; Item 7.01 of the 8-K"
  }
},
{
  "id": "TR-proofpoint-2",
  "title": "Proofpoint Acquires Acuvity to Deliver AI Security and Governance Across the Agentic Workspace",
  "organization": "Proofpoint, Inc.",
  "publicationDate": "2026-02-12",
  "economicPeriod": "February 2026",
  "canonicalUrl": "https://www.proofpoint.com/us/newsroom/press-releases/proofpoint-acquires-acuvity-deliver-ai-security-and-governance-across",
  "excerpt": "Proofpoint, Inc. today announced it has acquired Acuvity, a pioneer in AI enterprise security and governance.",
  "sourceClass": "OFFICIAL",
  "interpretation": "",
  "limitations": "",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-proofpoint-2",
  "tags": [
    "tracker",
    "email"
  ],
  "retrievedAt": "2026-09-26",
  "retrieval": {
    "finalUrl": "https://www.proofpoint.com/us/newsroom/press-releases/proofpoint-acquires-acuvity-deliver-ai-security-and-governance-across",
    "sha256": "a721271180cee3681ce94fe3b91b5b0ef198c0351b3cbf95bea484fbf90b77a7",
    "fetchedAt": "2026-09-26T17:40:00Z",
    "locator": "Opening paragraph"
  }
},
{
  "id": "TR-rapid7-6",
  "title": "Rapid7, Inc. — Form 8-K, Items 2.02 and 5.02 (Chief Financial Officer appointment)",
  "organization": "Rapid7, Inc.",
  "publicationDate": "2025-11-04",
  "economicPeriod": "November 2025",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/1560327/000156032725000059/rp-20251104.htm",
  "excerpt": "On November 1, 2025, the Board of Directors of the Company appointed Rafe Brown as the Chief Financial Officer of the Company, effective upon the commencement of Mr. Brown's employment with the Company, which is expected to be on or about December 1, 2025.",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-COLLECT / TR-rapid7-6",
  "tags": [
    "tracker",
    "exposure"
  ],
  "retrievedAt": "2026-09-26",
  "retrieval": {
    "finalUrl": "https://www.sec.gov/Archives/edgar/data/1560327/000156032725000059/rp-20251104.htm",
    "sha256": "b7a6e4c62b750d05e6ef0c0b1df165ff90d9a91b31c2eeeb428b5b0d279bebf0",
    "fetchedAt": "2026-09-26T17:50:00Z",
    "locator": "Item 5.02, Appointment of Chief Financial Officer"
  }
},
{
  "id": "TR-s1-4",
  "title": "SentinelOne, Inc. — Form 8-K, Items 2.02, 5.02, 7.01 (Chief Financial Officer resignation and interim appointment)",
  "organization": "SentinelOne, Inc.",
  "publicationDate": "2025-12-04",
  "economicPeriod": "December 2025",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/1583708/000158370825000157/s-20251204.htm",
  "excerpt": "On December 1, 2025, Barbara Larson notified the Company of her intention to resign from her position as the Chief Financial Officer and principal financial officer of the Company at a future date that is mutually agreeable to the Company and Ms. Larson (currently expected in mid-January 2026). Effective as of the Larson Resignation Date, Barry Padgett, the Company's current Chief Growth Officer, will serve as the interim Chief Financial Officer and principal financial officer of the Company.",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-COLLECT / TR-s1-4",
  "tags": [
    "tracker",
    "endpoint-xdr"
  ],
  "retrievedAt": "2026-09-26",
  "retrieval": {
    "finalUrl": "https://www.sec.gov/Archives/edgar/data/1583708/000158370825000157/s-20251204.htm",
    "sha256": "5488bac66b32ee9ad059a83df56b1437628498d38b0e5a6e79e2703723d9db1d",
    "fetchedAt": "2026-09-26T17:50:00Z",
    "locator": "Item 5.02(b) and (c), Appointment of Barry Padgett as Interim Chief Financial Officer"
  }
},
{
  "id": "TR-s1-5",
  "title": "SentinelOne, Inc. — Form 8-K, Item 5.02 (Chief Financial Officer appointment)",
  "organization": "SentinelOne, Inc.",
  "publicationDate": "2026-03-05",
  "economicPeriod": "March 2026",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/1583708/000158370826000009/s-20260228.htm",
  "excerpt": "On February 28, 2026, the Board of Directors of SentinelOne, Inc. appointed Sonalee Parekh as the Company's Chief Financial Officer and principal financial officer, effective as of the start date, currently set for March 24, 2026.",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "Filed March 5, 2026; the board action is dated February 28, 2026.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-COLLECT / TR-s1-5",
  "tags": [
    "tracker",
    "endpoint-xdr"
  ],
  "retrievedAt": "2026-09-26",
  "retrieval": {
    "finalUrl": "https://www.sec.gov/Archives/edgar/data/1583708/000158370826000009/s-20260228.htm",
    "sha256": "369452916c99643e42339947646454241b0d22831bea79b48d6f7dfb1dabfcc7",
    "fetchedAt": "2026-09-26T17:50:00Z",
    "locator": "Item 5.02(b) and (c)"
  }
},
{
  "id": "TR-sailpoint-3",
  "title": "SailPoint, Inc. — Form 10-Q for the quarter ended July 31, 2026 (Entro acquisition)",
  "organization": "SailPoint, Inc.",
  "publicationDate": "2026-09-10",
  "economicPeriod": "Quarter ended 2026-07-31",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/2030781/000203078126000021/sail-20260731.htm",
  "excerpt": "On June 29, 2026, the Company completed the acquisition of 100% of the outstanding equity interests of Entro Security Ltd. and its wholly owned subsidiary, Entro Security Inc. (collectively, \"Entro\"), for total purchase consideration of approximately $122.6 million in cash.",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "The 10-Q also states the Company committed to issue up to $7.3 million in restricted stock to certain key employees and former shareholders of Entro who became employees.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-COLLECT / TR-sailpoint-3",
  "tags": [
    "tracker",
    "identity"
  ],
  "retrievedAt": "2026-09-26",
  "retrieval": {
    "finalUrl": "https://www.sec.gov/Archives/edgar/data/2030781/000203078126000021/sail-20260731.htm",
    "sha256": "f0f7736fe98833a8577a06884431283e4faf7594fd1867d0c330d1cb1cdcadbe",
    "fetchedAt": "2026-09-26T17:50:00Z",
    "locator": "Note, Business Combinations, Entro"
  }
},
{
  "id": "TR-veeam-3",
  "title": "Veeam to Acquire Securiti AI",
  "organization": "Veeam Software",
  "publicationDate": "2025-10-21",
  "economicPeriod": "N/A (acquisition announcement)",
  "canonicalUrl": "https://www.veeam.com/news/veeam-to-acquire-securiti-ai.html",
  "excerpt": "Veeam \"today announced it has signed a definitive agreement to acquire\" Securiti AI \"for $1.725 billion.\" \"The transaction is expected to close in the fourth quarter and is subject to customary closing conditions and regulatory approvals.\"",
  "sourceClass": "OFFICIAL",
  "interpretation": "",
  "limitations": "Company press release announcing the agreement; the completion is recorded separately under TR-veeam-2.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-COLLECT / TR-veeam-3",
  "tags": [
    "tracker",
    "data"
  ],
  "retrievedAt": "2026-09-26",
  "retrieval": {
    "finalUrl": "https://www.veeam.com/news/veeam-to-acquire-securiti-ai.html",
    "sha256": "f6f33bb13a7e5c0860b3437552a785f77d73bf3e444d3b462df220e94721498b",
    "fetchedAt": "2026-09-26T18:10:00Z",
    "locator": "Press release, dateline and first two paragraphs"
  }
},
{
  "id": "TR-torq-2",
  "title": "Torq Acquires Jit to Unleash the First Enterprise AI SOC Context Graph",
  "organization": "Torq",
  "publicationDate": "2026-05-19",
  "economicPeriod": "May 2026",
  "canonicalUrl": "https://torq.io/news/torq-acquires-jit/",
  "excerpt": "\"Torq, the established agentic security operations leader, today announced the acquisition of Jit, the Boston-based AI Context Graph cybersecurity pioneer.\"",
  "sourceClass": "OFFICIAL",
  "interpretation": "",
  "limitations": "The page shows a display date of May 18, 2026 and a dateline of May 19, 2026; the dateline date is used. The release states no price or closing date.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-COLLECT / TR-torq-2",
  "tags": [
    "tracker",
    "secops"
  ],
  "retrievedAt": "2026-09-26",
  "retrieval": {
    "finalUrl": "https://torq.io/news/torq-acquires-jit/",
    "sha256": "63301efedcccfb33c0082d016689000b35b48124bb50b9524d33d186bc18795b",
    "fetchedAt": "2026-09-26T18:12:00Z",
    "locator": "Press release, dateline paragraph"
  }
},
{
  "id": "TR-upwind-2",
  "title": "Building the Future: Introducing the Upwind AI Security Lab",
  "organization": "Upwind Security",
  "publicationDate": "2026-09-23",
  "economicPeriod": "September 2026",
  "canonicalUrl": "https://www.upwind.io/feed/building-the-future-introducing-the-upwind-ai-security-lab",
  "excerpt": "\"Upwind is acquiring Aegis, and we are launching the Upwind AI Lab.\"",
  "sourceClass": "OFFICIAL",
  "interpretation": "",
  "limitations": "Company blog post; publication date taken from the page's datePublished metadata (2026-09-23). The post states no price or closing date.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-COLLECT / TR-upwind-2",
  "tags": [
    "tracker",
    "cloud"
  ],
  "retrievedAt": "2026-09-26",
  "retrieval": {
    "finalUrl": "https://www.upwind.io/feed/building-the-future-introducing-the-upwind-ai-security-lab",
    "sha256": "c1f435a0736b0a8b76a7dcae584cd5ca6fa2da2b8d092f5091f2fd13cc6270f0",
    "fetchedAt": "2026-09-26T18:14:00Z",
    "locator": "Blog post, first sentence"
  }
},
{
  "id": "TR-zscaler-5",
  "title": "Zscaler Annual Report on Form 10-K for fiscal year ended July 31, 2026 (Note 6, Business Combinations)",
  "organization": "Zscaler, Inc.",
  "publicationDate": "2026-09-03",
  "economicPeriod": "Fiscal year ended 2026-07-31",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/1713683/000171368326000157/zs-20260731.htm",
  "excerpt": "On October 31, 2025, we acquired all outstanding equity of SPLXAI Inc. (\"SPLX\"), an early-stage AI technology company, for cash consideration of $40.6 million. In connection with the acquisition, we also issued $16.6 million in restricted stock subject to post-combination service vesting conditions. On February 5, 2026, we acquired all outstanding equity of SquareX Holdings, Inc. (\"SquareX\"), a browser security company, for cash consideration of $112.8 million. In connection with the acquisition, we issued $37.4 million in restricted stock subject to post-combination service vesting conditions. On May 27, 2026, we acquired all outstanding equity of Symmetry Systems, Inc. (\"Symmetry\"), a technology company, for cash consideration of $152.9 million. In connection with the acquisition, we issued $16.9 million in restricted stock subject to post-combination service vesting conditions.",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "Purchase price allocations are described in the filing as preliminary and subject to adjustment during the measurement period.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-COLLECT / TR-zscaler-5",
  "tags": [
    "tracker",
    "network-sase",
    "public-company"
  ],
  "retrievedAt": "2026-09-26",
  "retrieval": {
    "finalUrl": "https://www.sec.gov/Archives/edgar/data/1713683/000171368326000157/zs-20260731.htm",
    "sha256": "fa8596d6062015c4d3d617ffbd932237cc96146ff72364f92cbbc4a6f8e781ba",
    "fetchedAt": "2026-09-26T17:31:00Z",
    "locator": "Note 6. Business Combinations"
  }
},
{
  "id": "TR-zscaler-6",
  "title": "Zscaler Form 8-K, Item 5.02, filed 2026-04-16",
  "organization": "Zscaler, Inc.",
  "publicationDate": "2026-04-16",
  "economicPeriod": "Event dated 2026-04-15",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/1713683/000171368326000082/zs-20260415.htm",
  "excerpt": "On April 15, 2026, Raj Judge, the EVP of Corporate Strategy of Zscaler, Inc. (the \"Company\") informed the Company of his resignation. Mr. Judge's departure will be effective on July 31, 2026. Mr. Judge resigned as an officer of the Company, effective April 15, 2026. In addition, Mr. Judge resigned as a member of the Board of Directors of the Company, effective April 15, 2026.",
  "sourceClass": "FILING",
  "interpretation": "",
  "limitations": "The 8-K states the Board resignation is not the result of any disagreements with the Company on any matter.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-COLLECT / TR-zscaler-6",
  "tags": [
    "tracker",
    "network-sase",
    "public-company"
  ],
  "retrievedAt": "2026-09-26",
  "retrieval": {
    "finalUrl": "https://www.sec.gov/Archives/edgar/data/1713683/000171368326000082/zs-20260415.htm",
    "sha256": "c0ef7cb530e8b8e13a116dc078b3cea8019b47849cda4cb63e71b26ec401137d",
    "fetchedAt": "2026-09-26T17:31:00Z",
    "locator": "Item 5.02"
  }
},
{
  "id": "TR-expel-1",
  "title": "Expel Raises $140 Million in Series E Funding",
  "organization": "Expel, Inc.",
  "publicationDate": "2021-11-18",
  "economicPeriod": "N/A (funding announcement)",
  "canonicalUrl": "https://expel.com/resource/expel-raises-140-million-in-series-e-funding/",
  "excerpt": "Expel... announced $140.3 million in Series E funding, co-led by CapitalG, Alphabet's independent growth fund, and Paladin Capital Group... a valuation over $1 billion.",
  "sourceClass": "IR",
  "interpretation": "",
  "limitations": "AUTO-001 fix pass 4, item 1/8: the tracker previously had no lastRound/ownership field for Expel at all. Checked Expel's own newsroom through its most recent 2026 releases; no later funding round or ownership change was found there.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-STEP5 / TR-expel-1",
  "tags": [
    "tracker",
    "managed-security"
  ],
  "retrievedAt": "2026-10-01"
},
{
  "id": "TR-reliaquest-2",
  "title": "ReliaQuest Names Krish Venkataraman Chief Financial Officer",
  "organization": "ReliaQuest, LLC",
  "publicationDate": "2026-10-01",
  "economicPeriod": "N/A (leadership announcement)",
  "canonicalUrl": "https://reliaquest.com/news-and-press/reliaquest-names-krish-venkataraman-chief-financial-officer/",
  "excerpt": "ReliaQuest... today announced that Krish Venkataraman will join the company as Chief Financial Officer on October 5. Venkataraman will lead ReliaQuest's global finance and accounting organization... Venkataraman joins ReliaQuest from Solink, an AI technology company, where he serves as CFO. Previously he was President of Dataiku and CFO of Socure.",
  "sourceClass": "OFFICIAL",
  "interpretation": "",
  "limitations": "Company press release; ReliaQuest is privately held with no SEC filer CIK.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-COLLECT / TR-reliaquest-2",
  "tags": [
    "tracker",
    "managed-security"
  ],
  "retrievedAt": "2026-10-02",
  "retrieval": {
    "finalUrl": "https://reliaquest.com/news-and-press/reliaquest-names-krish-venkataraman-chief-financial-officer/",
    "sha256": "f160bda9c0f1d3ccd47db4afc9b3b1fa047532b729ec3d54211d7e56e07f173e",
    "fetchedAt": "2026-10-02T15:10:00Z",
    "locator": "Opening paragraph"
  }
},
{
  "id": "TR-arctic-wolf-2",
  "title": "Arctic Wolf Closes Record-breaking Series F with New and Existing Investors",
  "organization": "Arctic Wolf Networks, Inc.",
  "publicationDate": "2021-07-13",
  "economicPeriod": "N/A (funding announcement)",
  "canonicalUrl": "https://arcticwolf.com/resources/blog/arctic-wolf-closes-record-breaking-series-f-funding/",
  "excerpt": "...backed by top tier investors, including Viking Global Investors, Owl Rock, a division of Blue Owl Capital and others in our Series F funding round of $150 million. Following this round, the company has achieved a valuation of $4.3 billion.",
  "sourceClass": "IR",
  "interpretation": "",
  "limitations": "AUTO-001 fix pass 4, item 8: this is the most recent funding round found on Arctic Wolf's own site after checking its press-releases index, its full post-sitemap for every 'series'/'funding'/'raises'/'valuation' slug, and a GlobeNewswire organization search; no company-issued source for a later round was found. Company is privately held with no SEC filer CIK.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-COLLECT / TR-arctic-wolf-2",
  "tags": [
    "tracker",
    "managed-security"
  ],
  "retrievedAt": "2026-10-02",
  "retrieval": {
    "finalUrl": "https://arcticwolf.com/resources/blog/arctic-wolf-closes-record-breaking-series-f-funding/",
    "sha256": "9e957f78e50ee3a72266382ca364e7cbe8de6fdce135da4a2b43d1ede7c54a5a",
    "fetchedAt": "2026-10-02T15:30:00Z",
    "locator": "Body paragraph naming investors, round amount, and resulting valuation"
  }
},
{
  "id": "TR-cohesity-1",
  "title": "Cohesity Becomes World's Largest Data Protection Software Provider After Completing Combination with Veritas' Enterprise Data Protection Business",
  "organization": "Cohesity, Inc.",
  "publicationDate": "2024-12-10",
  "economicPeriod": "N/A (transaction close announcement)",
  "canonicalUrl": "https://www.cohesity.com/newsroom/press/cohesity-becomes-worlds-largest-data-protection-provider-after-completing-combination-with-veritas-enterprise-data-protection-business/",
  "excerpt": "The transaction values the combined company at over $7 billion. The combined company received support from current marquee investors, including Sequoia Capital, Softbank Vision Fund I, Wing Venture Capital, Premji Invest, and Madrona. The Carlyle Group is now one of the largest shareholders in the combined company. The transaction was funded by a Series H investment round led by Haveli Investments, which provided the majority of equity in the transaction and is now one of Cohesity's largest shareholders. Coatue, Sapphire Ventures, and Dragon Fund were also key investors in the Series H investment round.",
  "sourceClass": "IR",
  "interpretation": "",
  "limitations": "Company's own press release. Company is privately held with no SEC filer CIK.",
  "conflictingEvidenceIds": [],
  "artifactLabel": "SEC-MARKET-AUTO-001-COLLECT / TR-cohesity-1",
  "tags": [
    "tracker",
    "data"
  ],
  "retrievedAt": "2026-10-02",
  "retrieval": {
    "finalUrl": "https://www.cohesity.com/newsroom/press/cohesity-becomes-worlds-largest-data-protection-provider-after-completing-combination-with-veritas-enterprise-data-protection-business/",
    "sha256": "c4af532ff76676eb0416c732b3494f57eebb8fe975b7f17011ae7aaa71e1763e",
    "fetchedAt": "2026-10-02T15:35:00Z",
    "locator": "Transaction Details and Advisors section"
  }
},
]

export const evidenceRecords: EvidenceRecord[] = [
  ...handWrittenEvidenceRecords,
  ...(generatedFilingEvidence as EvidenceRecord[]),
]

export const evidenceById = Object.fromEntries(
  evidenceRecords.map((record) => [record.id, record]),
) as Record<string, EvidenceRecord>

export function getEvidence(ids: string | string[]): EvidenceRecord[] {
  const list = Array.isArray(ids) ? ids : [ids]
  return list.map((id) => evidenceById[id]).filter(Boolean)
}
