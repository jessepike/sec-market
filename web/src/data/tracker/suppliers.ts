/**
 * Tracked suppliers — step 5 of the autonomy plan
 * (docs/active/autonomy-coverage-plan.md §4–5, D-76/D-77). One record per
 * declared supplier, sourced from docs/active/auto/step5/research/coverage-g{1,2,3}.md
 * (~80 suppliers across the twelve domains in domains.ts). `id` reuses an
 * existing print id (prints.ts, stripped of "print-") or EDGAR registry id
 * (edgarRegistry.ts) where one already exists, so the data sets join without
 * a remapping table. Every fact-bearing field cites evidence in evidence.ts
 * with a real source URL — see web/scripts/verify-tracker.ts, the build
 * gate that enforces this.
 */

export interface HeadlineMetric {
  label: string
  value: string
  period: string
  evidenceIds: string[]
}

export interface RevenuePeriod {
  value: string
  yoyGrowth: string
  period: string
  periodEnd: string
  evidenceIds: string[]
}

export interface RevenuePeriodLatest extends RevenuePeriod {
  releaseDate: string
}

export interface SupplierRevenue {
  latest: RevenuePeriodLatest
  /** Absent when the research found no comparable prior-quarter figure (e.g. an unbroken-out segment). */
  prior?: RevenuePeriod
}

export interface FundingRound {
  /** Full "YYYY-MM-DD", or "YYYY-MM" when the sourced evidence only gave a month. */
  date: string
  stage: string
  amount: string
  /** Absent when no lead investor was disclosed in the sourced evidence. */
  lead?: string
  valuation?: string
  evidenceIds: string[]
}

export interface Ownership {
  status: string
  acquirer?: string
  announced?: string
  closed?: string
  price?: string
  evidenceIds: string[]
}

export type SupplierKind = 'public' | 'private' | 'pe-owned' | 'segment' | 'acquired'

export interface TrackerSupplier {
  id: string
  name: string
  domainIds: string[]
  kind: SupplierKind
  ticker?: string
  cik?: string
  edgarId?: string
  headlineMetric?: HeadlineMetric
  revenue?: SupplierRevenue
  lastRound?: FundingRound
  ownership?: Ownership
}

export const trackerSuppliers: TrackerSupplier[] = [
  {
    "id": "abnormal-security",
    "name": "Abnormal Security",
    "domainIds": [
      "email"
    ],
    "kind": "private",
    "lastRound": {
      "date": "2024-08-06",
      "stage": "Series D",
      "amount": "$250 million",
      "lead": "Wellington Management",
      "valuation": "$5.1 billion",
      "evidenceIds": [
        "TR-abnormal-1"
      ]
    },
    "headlineMetric": {
      "label": "ARR",
      "value": "over $200 million",
      "period": "August 6, 2024",
      "evidenceIds": [
        "TR-abnormal-2"
      ]
    },
    "ownership": {
      "status": "Independent, venture-backed. Series D raised $250M at $5.1B valuation on August 6, 2024.",
      "evidenceIds": [
        "TR-abnormal-1"
      ]
    }
  },
  {
    "id": "aqua",
    "name": "Aqua Security",
    "domainIds": [
      "cloud"
    ],
    "kind": "private",
    "lastRound": {
      "date": "2024-01",
      "stage": "Series E extension",
      "amount": "$60 million",
      "valuation": "$1 billion+",
      "evidenceIds": [
        "TR-aqua-1"
      ]
    },
    "ownership": {
      "status": "Independent, venture-backed. Series E extension closed January 2024 at $1B+ valuation.",
      "evidenceIds": [
        "TR-aqua-1"
      ]
    }
  },
  {
    "id": "arctic-wolf",
    "name": "Arctic Wolf Networks, Inc.",
    "domainIds": [
      "managed-security"
    ],
    "kind": "private"
  },
  {
    "id": "armis",
    "name": "Armis Security Ltd.",
    "domainIds": [
      "ot-iot"
    ],
    "kind": "acquired",
    "ownership": {
      "status": "Acquired; ServiceNow closed its acquisition of Armis on April 20, 2026, per ServiceNow's own SEC filing.",
      "acquirer": "ServiceNow, Inc. (NYSE: NOW)",
      "closed": "2026-04-20",
      "evidenceIds": [
        "TR-armis-1"
      ]
    }
  },
  {
    "id": "axonius",
    "name": "Axonius, Inc.",
    "domainIds": [
      "exposure"
    ],
    "kind": "private",
    "headlineMetric": {
      "label": "ARR",
      "value": ">$200 million",
      "period": "Q1 fiscal 2027 (as of 2026-05-19)",
      "evidenceIds": [
        "TR-axonius-1"
      ]
    }
  },
  {
    "id": "barracuda",
    "name": "Barracuda Networks",
    "domainIds": [
      "email"
    ],
    "kind": "pe-owned",
    "cik": "0001348334",
    "ownership": {
      "status": "PE-owned by KKR. Acquired from Thoma Bravo, announced April 2022, closed August 2022 at approximately $4 billion.",
      "evidenceIds": [
        "TR-barracuda-1"
      ]
    }
  },
  {
    "id": "beyondtrust",
    "name": "BeyondTrust",
    "domainIds": [
      "identity"
    ],
    "kind": "pe-owned",
    "ownership": {
      "status": "PE-owned by Clearlake Capital. Strategic investment announced June 1, 2021.",
      "evidenceIds": [
        "TR-beyondtrust-1"
      ]
    }
  },
  {
    "id": "bigid",
    "name": "BigID",
    "domainIds": [
      "data"
    ],
    "kind": "private",
    "lastRound": {
      "date": "2024-03",
      "stage": "Growth round",
      "amount": "$60 million",
      "lead": "Riverwood Capital",
      "valuation": "$1 billion",
      "evidenceIds": [
        "TR-bigid-1"
      ]
    }
  },
  {
    "id": "cato",
    "name": "Cato Networks",
    "domainIds": [
      "network-sase"
    ],
    "kind": "private",
    "lastRound": {
      "date": "2025-06-30",
      "stage": "Series G",
      "amount": "$409 million (initial close $359M plus extension $50M)",
      "lead": "Vitruvian Partners and ION Crossover Partners",
      "valuation": "more than $4.8 billion",
      "evidenceIds": [
        "TR-cato-1"
      ]
    },
    "headlineMetric": {
      "label": "ARR",
      "value": "$415 million, +42% YoY",
      "period": "As of Jul 2026 (company-stated milestone)",
      "evidenceIds": [
        "TR-cato-3"
      ]
    },
    "ownership": {
      "status": "Independent, venture-backed. Series G announced June 30, 2025 at valuation over $4.8B.",
      "evidenceIds": [
        "TR-cato-1"
      ]
    }
  },
  {
    "id": "chainguard",
    "name": "Chainguard",
    "domainIds": [
      "appsec"
    ],
    "kind": "private",
    "lastRound": {
      "date": "2025-10-23",
      "stage": "Growth financing (no series letter disclosed)",
      "amount": "$280 million",
      "lead": "General Catalyst's Customer Value Fund",
      "evidenceIds": [
        "TR-chainguard-1"
      ]
    }
  },
  {
    "id": "checkpoint-email",
    "name": "Check Point",
    "domainIds": [
      "email"
    ],
    "kind": "segment",
    "ticker": "CHKP",
    "cik": "0001015922",
    "ownership": {
      "status": "Segment inside Check Point Software Technologies. Harmony Email originated from Avanan acquisition (~August 30, 2021 at $250-300M).",
      "evidenceIds": [
        "TR-checkpoint-email-1"
      ]
    }
  },
  {
    "id": "checkpoint-sase",
    "name": "Check Point",
    "domainIds": [
      "network-sase",
      "email"
    ],
    "kind": "public",
    "ticker": "CHKP",
    "cik": "0001015922",
    "headlineMetric": {
      "label": "Total Revenue",
      "value": "$674 million",
      "period": "Q2 2026, ended 2026-06-30",
      "evidenceIds": [
        "TR-checkpoint-1"
      ]
    },
    "revenue": {
      "latest": {
        "value": "$674 million",
        "yoyGrowth": "1%",
        "period": "Q2 2026",
        "periodEnd": "2026-06-30",
        "releaseDate": "2026-07-30",
        "evidenceIds": [
          "TR-checkpoint-1"
        ]
      },
      "prior": {
        "value": "$668 million",
        "yoyGrowth": "5%",
        "period": "Q1 2026",
        "periodEnd": "2026-03-31",
        "evidenceIds": [
          "TR-checkpoint-2"
        ]
      }
    },
    "ownership": {
      "status": "Independent, publicly traded as foreign private issuer on Nasdaq.",
      "evidenceIds": [
        "TR-checkpoint-1"
      ]
    }
  },
  {
    "id": "claroty",
    "name": "Claroty Ltd.",
    "domainIds": [
      "ot-iot"
    ],
    "kind": "private",
    "headlineMetric": {
      "label": "Annual revenue (company-stated, exact figure undisclosed)",
      "value": "hundreds of millions of dollars",
      "period": "as of 2026-01-22",
      "evidenceIds": [
        "TR-claroty-1"
      ]
    },
    "lastRound": {
      "date": "2026-01-22",
      "stage": "Growth equity",
      "amount": "$150 million",
      "lead": "Golub Growth (Golub Capital's growth-equity arm)",
      "valuation": "$3 billion",
      "evidenceIds": [
        "TR-claroty-1"
      ]
    }
  },
  {
    "id": "cloudflare",
    "name": "Cloudflare",
    "domainIds": [
      "network-sase"
    ],
    "kind": "public",
    "ticker": "NET",
    "cik": "0001477333",
    "headlineMetric": {
      "label": "Revenue",
      "value": "$696.1 million",
      "period": "Q2 2026, ended 2026-06-30",
      "evidenceIds": [
        "TR-cloudflare-1"
      ]
    },
    "revenue": {
      "latest": {
        "value": "$696.1 million",
        "yoyGrowth": "36%",
        "period": "Q2 2026",
        "periodEnd": "2026-06-30",
        "releaseDate": "2026-08-06",
        "evidenceIds": [
          "TR-cloudflare-1"
        ]
      },
      "prior": {
        "value": "$639.8 million",
        "yoyGrowth": "34%",
        "period": "Q1 2026",
        "periodEnd": "2026-03-31",
        "evidenceIds": [
          "TR-cloudflare-2"
        ]
      }
    },
    "ownership": {
      "status": "Independent, publicly traded since September 2019 IPO.",
      "evidenceIds": [
        "TR-cloudflare-1"
      ]
    }
  },
  {
    "id": "cohesity",
    "name": "Cohesity",
    "domainIds": [
      "data"
    ],
    "kind": "private"
  },
  {
    "id": "commvault",
    "name": "Commvault Systems, Inc.",
    "domainIds": [
      "data"
    ],
    "kind": "public",
    "ticker": "CVLT",
    "cik": "0001169561",
    "headlineMetric": {
      "label": "Subscription ARR",
      "value": "$1,054 million",
      "period": "Q1 FY2027 (ended 2026-06-30)",
      "evidenceIds": [
        "TR-commvault-1"
      ]
    },
    "revenue": {
      "latest": {
        "value": "$314.1 million",
        "yoyGrowth": "+11%",
        "period": "Q1 FY2027",
        "periodEnd": "2026-06-30",
        "releaseDate": "2026-07-28",
        "evidenceIds": [
          "TR-commvault-1"
        ]
      },
      "prior": {
        "value": "$311.7 million",
        "yoyGrowth": "+13%",
        "period": "Q4 FY2026",
        "periodEnd": "2026-03-31",
        "evidenceIds": [
          "TR-commvault-2"
        ]
      }
    },
    "ownership": {
      "status": "Independent, publicly traded (Nasdaq: CVLT).",
      "evidenceIds": [
        "TR-commvault-1"
      ]
    }
  },
  {
    "id": "crwd",
    "name": "CrowdStrike Holdings, Inc.",
    "domainIds": [
      "cloud",
      "endpoint-xdr",
      "exposure"
    ],
    "kind": "public",
    "ticker": "CRWD",
    "cik": "0001535527",
    "edgarId": "crwd",
    "headlineMetric": {
      "label": "ARR",
      "value": "$5.84 billion",
      "period": "Q2 FY2027, ended 2026-07-31",
      "evidenceIds": [
        "TR-crwd-1",
        "TR-crwd-2"
      ]
    },
    "revenue": {
      "latest": {
        "value": "$1.47 billion",
        "yoyGrowth": "+26%",
        "period": "Q2 FY2027",
        "periodEnd": "2026-07-31",
        "releaseDate": "2026-08-26",
        "evidenceIds": [
          "TR-crwd-1"
        ]
      },
      "prior": {
        "value": "$1.39 billion",
        "yoyGrowth": "+26%",
        "period": "Q1 FY2027",
        "periodEnd": "2026-04-30",
        "evidenceIds": [
          "TR-crwd-2"
        ]
      }
    },
    "ownership": {
      "status": "Independent, publicly traded (Nasdaq: CRWD).",
      "evidenceIds": [
        "TR-crwd-1"
      ]
    }
  },
  {
    "id": "crwd-exposure",
    "name": "CrowdStrike Falcon Exposure Management",
    "domainIds": [
      "exposure"
    ],
    "kind": "segment",
    "ticker": "CRWD",
    "cik": "0001535527",
    "ownership": {
      "status": "Product line within CrowdStrike Holdings, Inc. No separate revenue disclosed.",
      "evidenceIds": [
        "TR-crwd-1"
      ]
    }
  },
  {
    "id": "cyberark",
    "name": "CyberArk",
    "domainIds": [
      "identity"
    ],
    "kind": "acquired",
    "ticker": "CYBR (prior to delisting)",
    "cik": "0001598110",
    "ownership": {
      "status": "Acquired by Palo Alto Networks on February 11, 2026 at approximately $25 billion.",
      "acquirer": "Palo Alto Networks",
      "announced": "2025-07-31",
      "closed": "2026-02-11",
      "price": "$25 billion",
      "evidenceIds": [
        "TR-cyberark-1"
      ]
    }
  },
  {
    "id": "cyera",
    "name": "Cyera",
    "domainIds": [
      "data"
    ],
    "kind": "private",
    "lastRound": {
      "date": "2026-09-22",
      "stage": "Growth-equity investment (reported as a Series G extension)",
      "amount": "$400 million",
      "lead": "Growth Equity at Goldman Sachs Alternatives",
      "valuation": "over $12 billion",
      "evidenceIds": [
        "TR-cyera-1"
      ]
    }
  },
  {
    "id": "delinea",
    "name": "Delinea",
    "domainIds": [
      "identity"
    ],
    "kind": "pe-owned",
    "headlineMetric": {
      "label": "ARR",
      "value": "$400 million (nearing)",
      "period": "March 2025",
      "evidenceIds": [
        "TR-delinea-1"
      ]
    },
    "ownership": {
      "status": "PE-owned by TPG Capital. Formed from Thycotic and Centrify merger, rebranded February 2022.",
      "evidenceIds": [
        "TR-delinea-2"
      ]
    }
  },
  {
    "id": "dragos",
    "name": "Dragos, Inc.",
    "domainIds": [
      "ot-iot"
    ],
    "kind": "acquired",
    "ownership": {
      "status": "Accenture plc agreed to acquire a majority stake in Dragos; the agreement is disclosed in Accenture's own SEC 8-K exhibit accompanying its Q3 FY2026 earnings. Reported closing timing (around August/September 2026) was not independently confirmed against a primary source.",
      "acquirer": "Accenture plc (NYSE: ACN)",
      "announced": "2026-06-18",
      "evidenceIds": [
        "TR-dragos-1"
      ]
    }
  },
  {
    "id": "esentire",
    "name": "eSentire, Inc.",
    "domainIds": [
      "managed-security"
    ],
    "kind": "pe-owned",
    "ownership": {
      "status": "Owned by Warburg Pincus (majority since 2017).",
      "evidenceIds": [
        "TR-esentire-1"
      ]
    }
  },
  {
    "id": "exabeam",
    "name": "Exabeam, Inc.",
    "domainIds": [
      "secops"
    ],
    "kind": "private",
    "ownership": {
      "status": "Merged with LogRhythm (Thoma Bravo-owned). Closed 2024-07-17.",
      "acquirer": "LogRhythm (Thoma Bravo)",
      "closed": "2024-07-17",
      "evidenceIds": [
        "TR-exabeam-1"
      ]
    }
  },
  {
    "id": "expel",
    "name": "Expel, Inc.",
    "domainIds": [
      "managed-security"
    ],
    "kind": "private"
  },
  {
    "id": "forescout",
    "name": "Forescout Technologies, Inc.",
    "domainIds": [
      "ot-iot"
    ],
    "kind": "pe-owned",
    "ownership": {
      "status": "PE-owned; co-owned by Advent International and Crosspoint Capital Partners, per Forescout's own leadership page. Advent International's original take-private acquisition closed via tender offer in 2020.",
      "acquirer": "Advent International / Crosspoint Capital Partners",
      "evidenceIds": [
        "TR-forescout-1"
      ]
    }
  },
  {
    "id": "fortinet",
    "name": "Fortinet",
    "domainIds": [
      "network-sase"
    ],
    "kind": "public",
    "ticker": "FTNT",
    "cik": "0001262039",
    "edgarId": "fortinet",
    "headlineMetric": {
      "label": "Billings",
      "value": "$2.37 billion",
      "period": "Q2 2026, ended 2026-06-30",
      "evidenceIds": [
        "TR-fortinet-1"
      ]
    },
    "revenue": {
      "latest": {
        "value": "$2.05 billion",
        "yoyGrowth": "26%",
        "period": "Q2 2026",
        "periodEnd": "2026-06-30",
        "releaseDate": "2026-07-29",
        "evidenceIds": [
          "TR-fortinet-1"
        ]
      },
      "prior": {
        "value": "$1.85 billion",
        "yoyGrowth": "20%",
        "period": "Q1 2026",
        "periodEnd": "2026-03-31",
        "evidenceIds": [
          "TR-fortinet-2"
        ]
      }
    },
    "ownership": {
      "status": "Independent, publicly traded.",
      "evidenceIds": [
        "TR-fortinet-1"
      ]
    }
  },
  {
    "id": "github-advanced-security",
    "name": "GitHub Advanced Security",
    "domainIds": [
      "appsec"
    ],
    "kind": "segment"
  },
  {
    "id": "google-secops",
    "name": "Google SecOps",
    "domainIds": [
      "secops"
    ],
    "kind": "segment",
    "ticker": "GOOGL",
    "cik": "0001652044",
    "ownership": {
      "status": "Segment of Alphabet Inc. (publicly traded, Nasdaq: GOOGL). Product of Chronicle (acquired 2019) and Mandiant (closed September 2022).",
      "evidenceIds": [
        "TR-google-secops-1"
      ]
    }
  },
  {
    "id": "hiddenlayer",
    "name": "HiddenLayer, Inc.",
    "domainIds": [
      "ai-security"
    ],
    "kind": "private",
    "headlineMetric": {
      "label": "ARR growth (company-stated)",
      "value": "more than 10x year-over-year",
      "period": "as of 2026-09-02",
      "evidenceIds": [
        "TR-hiddenlayer-1"
      ]
    },
    "lastRound": {
      "date": "2026-09-02",
      "stage": "Series B",
      "amount": "$100 million",
      "lead": "Delta-v Capital",
      "evidenceIds": [
        "TR-hiddenlayer-1"
      ]
    }
  },
  {
    "id": "ivanti",
    "name": "Ivanti, Inc.",
    "domainIds": [
      "exposure"
    ],
    "kind": "pe-owned",
    "ownership": {
      "status": "Owned by Clearlake Capital Group, Charlesbank Capital Partners, and TA Associates.",
      "evidenceIds": [
        "TR-ivanti-1"
      ]
    }
  },
  {
    "id": "jfrog",
    "name": "JFrog Ltd.",
    "domainIds": [
      "appsec"
    ],
    "kind": "public",
    "ticker": "FROG",
    "cik": "0001800667",
    "headlineMetric": {
      "label": "Cloud revenue",
      "value": "$87.5 million",
      "period": "Q2 2026 (ended 2026-06-30)",
      "evidenceIds": [
        "TR-jfrog-1"
      ]
    },
    "revenue": {
      "latest": {
        "value": "$163.8 million",
        "yoyGrowth": "+29%",
        "period": "Q2 2026",
        "periodEnd": "2026-06-30",
        "releaseDate": "2026-08-06",
        "evidenceIds": [
          "TR-jfrog-1"
        ]
      },
      "prior": {
        "value": "$154.0 million",
        "yoyGrowth": "+26%",
        "period": "Q1 2026",
        "periodEnd": "2026-03-31",
        "evidenceIds": [
          "TR-jfrog-2"
        ]
      }
    },
    "ownership": {
      "status": "Independent, publicly traded (Nasdaq: FROG), IPO 2020.",
      "evidenceIds": [
        "TR-jfrog-1"
      ]
    }
  },
  {
    "id": "lakera",
    "name": "Lakera AI (Lakera)",
    "domainIds": [
      "ai-security"
    ],
    "kind": "acquired",
    "ownership": {
      "status": "Acquired by Check Point Software Technologies; announced September 16, 2025 and completed during the fourth quarter of 2025, per Check Point's own earnings filing, for approximately $190 million in net cash consideration.",
      "acquirer": "Check Point Software Technologies Ltd (CHKP)",
      "announced": "2025-09-16",
      "price": "approximately $190 million net cash consideration",
      "evidenceIds": [
        "TR-lakera-1"
      ]
    }
  },
  {
    "id": "mimecast",
    "name": "Mimecast",
    "domainIds": [
      "email"
    ],
    "kind": "pe-owned",
    "cik": "0001644675",
    "ownership": {
      "status": "PE-owned by Permira via Magnesium Bidco Limited. Take-private announced December 7, 2021, closed May 2022 at $5.8 billion.",
      "evidenceIds": [
        "TR-mimecast-1"
      ]
    }
  },
  {
    "id": "msft-defender",
    "name": "Microsoft Defender for Endpoint",
    "domainIds": [
      "endpoint-xdr"
    ],
    "kind": "segment",
    "ticker": "MSFT",
    "cik": "0000789019",
    "ownership": {
      "status": "Segment of Microsoft Corporation (publicly traded, Nasdaq: MSFT). No separate revenue disclosed.",
      "evidenceIds": [
        "TR-msft-1"
      ]
    }
  },
  {
    "id": "msft-defender-o365",
    "name": "Microsoft Defender for Office 365",
    "domainIds": [
      "email"
    ],
    "kind": "segment",
    "ticker": "MSFT",
    "cik": "0000789019",
    "ownership": {
      "status": "Segment of Microsoft Corporation (publicly traded, Nasdaq: MSFT). No separate revenue disclosed.",
      "evidenceIds": [
        "TR-msft-defender-1"
      ]
    }
  },
  {
    "id": "msft-entra",
    "name": "Microsoft Entra ID",
    "domainIds": [
      "identity"
    ],
    "kind": "segment",
    "ticker": "MSFT",
    "cik": "0000789019",
    "ownership": {
      "status": "Segment of Microsoft Corporation (publicly traded, Nasdaq: MSFT). No separate revenue disclosed.",
      "evidenceIds": [
        "TR-msft-entra-1"
      ]
    }
  },
  {
    "id": "netskope",
    "name": "Netskope",
    "domainIds": [
      "network-sase"
    ],
    "kind": "public",
    "ticker": "NTSK",
    "cik": "0002063196",
    "headlineMetric": {
      "label": "ARR",
      "value": "$899 million",
      "period": "Q2 FY2027, ended 2026-07-31",
      "evidenceIds": [
        "TR-netskope-1"
      ]
    },
    "revenue": {
      "latest": {
        "value": "$220.5 million",
        "yoyGrowth": "29%",
        "period": "Q2 FY2027",
        "periodEnd": "2026-07-31",
        "releaseDate": "2026-09-02",
        "evidenceIds": [
          "TR-netskope-1"
        ]
      },
      "prior": {
        "value": "$201.6 million",
        "yoyGrowth": "28%",
        "period": "Q1 FY2027",
        "periodEnd": "2026-04-30",
        "evidenceIds": [
          "TR-netskope-2"
        ]
      }
    },
    "ownership": {
      "status": "Independent, publicly traded since Nasdaq IPO on September 18, 2025. Raised approximately $992 million at $7.3 billion valuation.",
      "evidenceIds": [
        "TR-netskope-3"
      ]
    }
  },
  {
    "id": "nozomi",
    "name": "Nozomi Networks, Inc.",
    "domainIds": [
      "ot-iot"
    ],
    "kind": "private"
  },
  {
    "id": "okta",
    "name": "Okta",
    "domainIds": [
      "identity"
    ],
    "kind": "public",
    "ticker": "OKTA",
    "cik": "0001660134",
    "edgarId": "okta",
    "headlineMetric": {
      "label": "Revenue",
      "value": "$805 million",
      "period": "Quarter ended July 31, 2026",
      "evidenceIds": [
        "TR-okta-1"
      ]
    },
    "revenue": {
      "latest": {
        "value": "$805 million",
        "yoyGrowth": "11%",
        "period": "Q2 FY2027",
        "periodEnd": "2026-07-31",
        "releaseDate": "2026-08-26",
        "evidenceIds": [
          "TR-okta-1"
        ]
      },
      "prior": {
        "value": "$765 million",
        "yoyGrowth": "11.2%",
        "period": "Q1 FY2027",
        "periodEnd": "2026-04-30",
        "evidenceIds": [
          "TR-okta-2"
        ]
      }
    },
    "ownership": {
      "status": "Independent, publicly traded on Nasdaq.",
      "evidenceIds": [
        "TR-okta-1"
      ]
    }
  },
  {
    "id": "optiv",
    "name": "Optiv Security Inc.",
    "domainIds": [
      "managed-security"
    ],
    "kind": "pe-owned",
    "ownership": {
      "status": "Owned by KKR (majority) with Blackstone and management retaining minority stakes. Announced 2016-12-06.",
      "acquirer": "KKR",
      "announced": "2016-12-06",
      "evidenceIds": [
        "TR-optiv-1"
      ]
    }
  },
  {
    "id": "orca",
    "name": "Orca Security",
    "domainIds": [
      "cloud"
    ],
    "kind": "private",
    "ownership": {
      "status": "Independent, venture-backed private company.",
      "evidenceIds": [
        "TR-orca-1"
      ]
    }
  },
  {
    "id": "panw",
    "name": "Palo Alto Networks, Inc.",
    "domainIds": [
      "ai-security",
      "cloud",
      "endpoint-xdr",
      "network-sase",
      "secops"
    ],
    "kind": "public",
    "ticker": "PANW",
    "cik": "0001327567",
    "edgarId": "panw",
    "headlineMetric": {
      "label": "NGS ARR",
      "value": "$9.10 billion",
      "period": "Q4 FY2026, ended 2026-07-31",
      "evidenceIds": [
        "TR-panw-1"
      ]
    },
    "revenue": {
      "latest": {
        "value": "$3.41 billion",
        "yoyGrowth": "+34%",
        "period": "Q4 FY2026",
        "periodEnd": "2026-07-31",
        "releaseDate": "2026-09-01",
        "evidenceIds": [
          "TR-panw-1"
        ]
      },
      "prior": {
        "value": "$3.0 billion",
        "yoyGrowth": "+31%",
        "period": "Q3 FY2026",
        "periodEnd": "2026-04-30",
        "evidenceIds": [
          "TR-panw-2"
        ]
      }
    },
    "ownership": {
      "status": "Independent, publicly traded (Nasdaq: PANW).",
      "evidenceIds": [
        "TR-panw-1"
      ]
    }
  },
  {
    "id": "panw-xsiam",
    "name": "Palo Alto Networks Cortex XSIAM",
    "domainIds": [
      "secops"
    ],
    "kind": "segment",
    "ticker": "PANW",
    "cik": "0001327567",
    "ownership": {
      "status": "Product line within Palo Alto Networks, Inc. (publicly traded, Nasdaq: PANW). No separate revenue disclosed.",
      "evidenceIds": [
        "TR-panw-xsiam-1"
      ]
    }
  },
  {
    "id": "ping-identity",
    "name": "Ping Identity",
    "domainIds": [
      "identity"
    ],
    "kind": "pe-owned",
    "headlineMetric": {
      "label": "ARR",
      "value": "$800 million (approaching)",
      "period": "November 2024",
      "evidenceIds": [
        "TR-ping-1"
      ]
    },
    "ownership": {
      "status": "PE-owned by Thoma Bravo. Acquisition closed October 18, 2022 at $2.8 billion. ForgeRock merged in, completed August 23, 2023.",
      "evidenceIds": [
        "TR-ping-2"
      ]
    }
  },
  {
    "id": "proofpoint",
    "name": "Proofpoint",
    "domainIds": [
      "email"
    ],
    "kind": "pe-owned",
    "cik": "0001212458",
    "ownership": {
      "status": "PE-owned by Thoma Bravo. Take-private announced April 26, 2021, closed August 31, 2021 at $12.3 billion.",
      "evidenceIds": [
        "TR-proofpoint-1"
      ]
    }
  },
  {
    "id": "protect-ai",
    "name": "Protect AI, Inc.",
    "domainIds": [
      "ai-security"
    ],
    "kind": "acquired",
    "ownership": {
      "status": "Acquired by Palo Alto Networks; the deal was announced April 27, 2025 and closed in July 2025 (specifically on or about July 22, 2025 per PANW's XBRL tagging), for $700.0 million in cash and replacement awards, subject to adjustment.",
      "acquirer": "Palo Alto Networks, Inc. (PANW)",
      "announced": "2025-04-27",
      "closed": "2025-07-22",
      "price": "$700.0 million in cash and replacement awards, subject to adjustment",
      "evidenceIds": [
        "TR-protectai-1"
      ]
    }
  },
  {
    "id": "qualys",
    "name": "Qualys, Inc.",
    "domainIds": [
      "exposure"
    ],
    "kind": "public",
    "ticker": "QLYS",
    "cik": "0001107843",
    "edgarId": "qualys",
    "headlineMetric": {
      "label": "Revenue",
      "value": "$182.2 million",
      "period": "Q2 2026, ended 2026-06-30",
      "evidenceIds": [
        "TR-qualys-1"
      ]
    },
    "revenue": {
      "latest": {
        "value": "$182.2 million",
        "yoyGrowth": "+11%",
        "period": "Q2 2026",
        "periodEnd": "2026-06-30",
        "releaseDate": "2026-08-04",
        "evidenceIds": [
          "TR-qualys-1"
        ]
      }
    },
    "ownership": {
      "status": "Independent, publicly traded (Nasdaq: QLYS).",
      "evidenceIds": [
        "TR-qualys-1"
      ]
    }
  },
  {
    "id": "rapid7",
    "name": "Rapid7, Inc.",
    "domainIds": [
      "exposure"
    ],
    "kind": "public",
    "ticker": "RPD",
    "cik": "0001560327",
    "edgarId": "rapid7",
    "headlineMetric": {
      "label": "ARR",
      "value": "$824.0 million",
      "period": "Q2 2026, ended 2026-06-30",
      "evidenceIds": [
        "TR-rapid7-1"
      ]
    },
    "revenue": {
      "latest": {
        "value": "$210.9 million",
        "yoyGrowth": "-1.5%",
        "period": "Q2 2026",
        "periodEnd": "2026-06-30",
        "releaseDate": "2026-08-10",
        "evidenceIds": [
          "TR-rapid7-1"
        ]
      },
      "prior": {
        "value": "$210 million",
        "yoyGrowth": "-0.3%",
        "period": "Q1 2026",
        "periodEnd": "2026-03-31",
        "evidenceIds": [
          "TR-rapid7-2"
        ]
      }
    },
    "ownership": {
      "status": "Independent, publicly traded (Nasdaq: RPD).",
      "evidenceIds": [
        "TR-rapid7-1"
      ]
    }
  },
  {
    "id": "red-canary",
    "name": "Red Canary, Inc.",
    "domainIds": [
      "managed-security"
    ],
    "kind": "acquired",
    "ownership": {
      "status": "Acquired by Zscaler, Inc. Closed 2025-08-01.",
      "acquirer": "Zscaler, Inc.",
      "announced": "2025-05-27",
      "closed": "2025-08-01",
      "price": "$651.4 million cash plus $20.2 million restricted stock",
      "evidenceIds": [
        "TR-red-canary-1"
      ]
    }
  },
  {
    "id": "reliaquest",
    "name": "ReliaQuest, LLC",
    "domainIds": [
      "managed-security"
    ],
    "kind": "pe-owned",
    "lastRound": {
      "date": "2025-03-31",
      "stage": "Growth equity",
      "amount": "$500 million+",
      "lead": "EQT, KKR, FTV Capital",
      "valuation": "$3.4 billion",
      "evidenceIds": [
        "TR-reliaquest-1"
      ]
    }
  },
  {
    "id": "rubrik",
    "name": "Rubrik, Inc.",
    "domainIds": [
      "data"
    ],
    "kind": "public",
    "ticker": "RBRK",
    "cik": "0001943896",
    "edgarId": "rubrik",
    "headlineMetric": {
      "label": "Subscription ARR",
      "value": "$1.66 billion",
      "period": "Q2 FY2027 (ended 2026-07-31)",
      "evidenceIds": [
        "TR-rubrik-1"
      ]
    },
    "revenue": {
      "latest": {
        "value": "$427.3 million",
        "yoyGrowth": "+38%",
        "period": "Q2 FY2027",
        "periodEnd": "2026-07-31",
        "releaseDate": "2026-08-27",
        "evidenceIds": [
          "TR-rubrik-1"
        ]
      },
      "prior": {
        "value": "$387.1 million",
        "yoyGrowth": "+39%",
        "period": "Q1 FY2027",
        "periodEnd": "2026-04-30",
        "evidenceIds": [
          "TR-rubrik-2"
        ]
      }
    },
    "ownership": {
      "status": "Independent, publicly traded (NYSE: RBRK).",
      "evidenceIds": [
        "TR-rubrik-1"
      ]
    }
  },
  {
    "id": "s1",
    "name": "SentinelOne, Inc.",
    "domainIds": [
      "endpoint-xdr"
    ],
    "kind": "public",
    "ticker": "S",
    "cik": "0001583708",
    "edgarId": "s1",
    "headlineMetric": {
      "label": "ARR",
      "value": "$1.218 billion",
      "period": "Q2 FY2027, ended 2026-07-31",
      "evidenceIds": [
        "TR-s1-1"
      ]
    },
    "revenue": {
      "latest": {
        "value": "$292 million",
        "yoyGrowth": "+21%",
        "period": "Q2 FY2027",
        "periodEnd": "2026-07-31",
        "releaseDate": "2026-08-27",
        "evidenceIds": [
          "TR-s1-1"
        ]
      },
      "prior": {
        "value": "$277 million",
        "yoyGrowth": "+21%",
        "period": "Q1 FY2027",
        "periodEnd": "2026-04-30",
        "evidenceIds": [
          "TR-s1-2"
        ]
      }
    },
    "ownership": {
      "status": "Independent, publicly traded (NYSE: S).",
      "evidenceIds": [
        "TR-s1-1"
      ]
    }
  },
  {
    "id": "sailpoint",
    "name": "SailPoint",
    "domainIds": [
      "identity"
    ],
    "kind": "public",
    "ticker": "SAIL",
    "cik": "0002030781",
    "edgarId": "sailpoint",
    "headlineMetric": {
      "label": "ARR",
      "value": "$1,230.7 million",
      "period": "Quarter ended July 31, 2026",
      "evidenceIds": [
        "TR-sailpoint-1"
      ]
    },
    "revenue": {
      "latest": {
        "value": "$308.8 million",
        "yoyGrowth": "16.8%",
        "period": "Q2 FY2027",
        "periodEnd": "2026-07-31",
        "releaseDate": "2026-09-10",
        "evidenceIds": [
          "TR-sailpoint-1"
        ]
      },
      "prior": {
        "value": "$280.142 million",
        "yoyGrowth": "21.5%",
        "period": "Q1 FY2027",
        "periodEnd": "2026-04-30",
        "evidenceIds": [
          "TR-sailpoint-2"
        ]
      }
    },
    "ownership": {
      "status": "Publicly traded after re-IPO. Taken private by Thoma Bravo, then returned to public markets.",
      "evidenceIds": [
        "TR-sailpoint-1"
      ]
    }
  },
  {
    "id": "snyk",
    "name": "Snyk, Inc.",
    "domainIds": [
      "appsec"
    ],
    "kind": "private",
    "lastRound": {
      "date": "2021-09-30",
      "stage": "Series F (plus extension)",
      "amount": "$605 million (initial close $530M plus extension $75M)",
      "lead": "not disclosed in available sourcing",
      "valuation": "$8.6 billion",
      "evidenceIds": [
        "TR-snyk-1",
        "TR-snyk-2"
      ]
    }
  },
  {
    "id": "sonatype",
    "name": "Sonatype Inc.",
    "domainIds": [
      "appsec"
    ],
    "kind": "pe-owned",
    "ownership": {
      "status": "PE-owned; Vista Equity Partners acquired a majority stake, announced November 18, 2019 (price undisclosed).",
      "acquirer": "Vista Equity Partners",
      "announced": "2019-11-18",
      "evidenceIds": [
        "TR-sonatype-1"
      ]
    }
  },
  {
    "id": "sophos",
    "name": "Sophos Group (Sophos Ltd)",
    "domainIds": [
      "endpoint-xdr"
    ],
    "kind": "pe-owned",
    "ownership": {
      "status": "Owned by Thoma Bravo since March 2020.",
      "acquirer": "Thoma Bravo",
      "announced": "2020-03-01",
      "evidenceIds": [
        "TR-sophos-1"
      ]
    }
  },
  {
    "id": "splunk",
    "name": "Splunk",
    "domainIds": [
      "secops"
    ],
    "kind": "segment",
    "ticker": "CSCO",
    "cik": "0000858877",
    "ownership": {
      "status": "Acquired by Cisco Systems, Inc. Closed 2024-03-18.",
      "acquirer": "Cisco Systems, Inc.",
      "announced": "2023-09-21",
      "closed": "2024-03-18",
      "price": "$157 per share cash; ~$28 billion equity value",
      "evidenceIds": [
        "TR-splunk-1"
      ]
    }
  },
  {
    "id": "surepath",
    "name": "SurePath AI, Inc.",
    "domainIds": [
      "ai-security"
    ],
    "kind": "acquired",
    "ownership": {
      "status": "Acquired by F5; the deal closed June 15, 2026 for $50.1 million, with $39.1 million of goodwill recorded. F5 states the acquisition's impact on its operating results was immaterial.",
      "acquirer": "F5, Inc. (FFIV)",
      "closed": "2026-06-15",
      "price": "$50.1 million",
      "evidenceIds": [
        "TR-surepath-1"
      ]
    }
  },
  {
    "id": "sysdig",
    "name": "Sysdig",
    "domainIds": [
      "cloud"
    ],
    "kind": "private",
    "ownership": {
      "status": "Independent, venture-backed private company. Confirmed not public.",
      "evidenceIds": [
        "TR-sysdig-1"
      ]
    }
  },
  {
    "id": "tenable",
    "name": "Tenable Holdings, Inc.",
    "domainIds": [
      "exposure"
    ],
    "kind": "public",
    "ticker": "TENB",
    "cik": "0001660280",
    "edgarId": "tenable",
    "headlineMetric": {
      "label": "Revenue",
      "value": "$268.5 million",
      "period": "Q2 2026, ended 2026-06-30",
      "evidenceIds": [
        "TR-tenable-1"
      ]
    },
    "revenue": {
      "latest": {
        "value": "$268.5 million",
        "yoyGrowth": "+8.6%",
        "period": "Q2 2026",
        "periodEnd": "2026-06-30",
        "releaseDate": "2026-07-29",
        "evidenceIds": [
          "TR-tenable-1"
        ]
      }
    },
    "ownership": {
      "status": "Independent, publicly traded (Nasdaq: TENB).",
      "evidenceIds": [
        "TR-tenable-1"
      ]
    }
  },
  {
    "id": "tines",
    "name": "Tines",
    "domainIds": [
      "secops"
    ],
    "kind": "private",
    "lastRound": {
      "date": "2025-02-11",
      "stage": "Series C",
      "amount": "$125 million",
      "lead": "Goldman Sachs and SoftBank",
      "valuation": "$1.13 billion",
      "evidenceIds": [
        "TR-tines-1"
      ]
    }
  },
  {
    "id": "torq",
    "name": "Torq",
    "domainIds": [
      "secops"
    ],
    "kind": "private",
    "lastRound": {
      "date": "2026-01-09",
      "stage": "Series D",
      "amount": "$140 million",
      "lead": "Merlin Ventures",
      "valuation": "$1.2 billion",
      "evidenceIds": [
        "TR-torq-1"
      ]
    }
  },
  {
    "id": "trend-micro",
    "name": "Trend Micro Incorporated",
    "domainIds": [
      "endpoint-xdr"
    ],
    "kind": "public",
    "ticker": "4704 (Tokyo Stock Exchange)",
    "cik": "0001089463",
    "headlineMetric": {
      "label": "ARR",
      "value": ">$1.7 billion",
      "period": "Q2 2026, ended 2026-06-30",
      "evidenceIds": [
        "TR-trend-1"
      ]
    },
    "ownership": {
      "status": "Independent, publicly traded on Tokyo Stock Exchange. Not an active SEC filer.",
      "evidenceIds": [
        "TR-trend-1"
      ]
    }
  },
  {
    "id": "trustwave",
    "name": "Trustwave Holdings, Inc.",
    "domainIds": [
      "managed-security"
    ],
    "kind": "acquired",
    "ownership": {
      "status": "Acquired by LevelBlue. Closed 2025-08-19.",
      "acquirer": "LevelBlue",
      "closed": "2025-08-19",
      "evidenceIds": [
        "TR-trustwave-1"
      ]
    }
  },
  {
    "id": "upwind",
    "name": "Upwind",
    "domainIds": [
      "cloud"
    ],
    "kind": "private",
    "lastRound": {
      "date": "2026-01-26",
      "stage": "Series B",
      "amount": "$250 million",
      "lead": "Bessemer Venture Partners",
      "valuation": "Unicorn status (>$1B implied)",
      "evidenceIds": [
        "TR-upwind-1"
      ]
    },
    "ownership": {
      "status": "Independent, venture-backed. Series B raised $250M on January 26, 2026, achieving unicorn status.",
      "evidenceIds": [
        "TR-upwind-1"
      ]
    }
  },
  {
    "id": "varonis",
    "name": "Varonis Systems, Inc.",
    "domainIds": [
      "data"
    ],
    "kind": "public",
    "ticker": "VRNS",
    "cik": "0001361113",
    "edgarId": "varonis",
    "headlineMetric": {
      "label": "Total SaaS ARR",
      "value": "$726.0 million",
      "period": "Q2 2026 (ended 2026-06-30)",
      "evidenceIds": [
        "TR-varonis-1"
      ]
    },
    "revenue": {
      "latest": {
        "value": "$180.0 million",
        "yoyGrowth": "+18.3%",
        "period": "Q2 2026",
        "periodEnd": "2026-06-30",
        "releaseDate": "2026-07-28",
        "evidenceIds": [
          "TR-varonis-1"
        ]
      },
      "prior": {
        "value": "$173.1 million",
        "yoyGrowth": "+27%",
        "period": "Q1 2026",
        "periodEnd": "2026-03-31",
        "evidenceIds": [
          "TR-varonis-1"
        ]
      }
    },
    "ownership": {
      "status": "Independent, publicly traded (Nasdaq: VRNS).",
      "evidenceIds": [
        "TR-varonis-1"
      ]
    }
  },
  {
    "id": "veeam",
    "name": "Veeam Software",
    "domainIds": [
      "data"
    ],
    "kind": "pe-owned",
    "ownership": {
      "status": "PE-owned; Insight Partners holds a majority stake, in a deal reported closed on or about January 9, 2020 for approximately $5 billion.",
      "acquirer": "Insight Partners",
      "evidenceIds": [
        "TR-veeam-1"
      ]
    }
  },
  {
    "id": "veracode",
    "name": "Veracode, Inc.",
    "domainIds": [
      "appsec"
    ],
    "kind": "pe-owned",
    "ownership": {
      "status": "PE-owned (majority stake held by TA Associates), which took a majority growth-investment stake at a $2.5 billion valuation, announced March 15, 2022.",
      "acquirer": "TA Associates",
      "announced": "2022-03-15",
      "evidenceIds": [
        "TR-veracode-1"
      ]
    }
  },
  {
    "id": "witnessai",
    "name": "WitnessAI",
    "domainIds": [
      "ai-security"
    ],
    "kind": "private",
    "headlineMetric": {
      "label": "ARR growth (company-stated)",
      "value": "500% year-over-year",
      "period": "as of 2026-01-13",
      "evidenceIds": [
        "TR-witnessai-1"
      ]
    },
    "lastRound": {
      "date": "2026-01-13",
      "stage": "Strategic funding round",
      "amount": "$58 million",
      "lead": "Sound Ventures",
      "evidenceIds": [
        "TR-witnessai-1"
      ]
    }
  },
  {
    "id": "wiz",
    "name": "Wiz",
    "domainIds": [
      "cloud"
    ],
    "kind": "acquired",
    "ownership": {
      "status": "Acquired by Google/Alphabet. Deal announced March 18, 2025 at $32 billion; closed March 11, 2026 at $29.5 billion.",
      "acquirer": "Google (Alphabet)",
      "announced": "2025-03-18",
      "closed": "2026-03-11",
      "price": "$29.5 billion",
      "evidenceIds": [
        "TR-wiz-1"
      ]
    }
  },
  {
    "id": "xage",
    "name": "Xage Security, Inc.",
    "domainIds": [
      "ot-iot"
    ],
    "kind": "private",
    "headlineMetric": {
      "label": "Year-over-year revenue growth (company-stated)",
      "value": "81%",
      "period": "as of 2026-03-18",
      "evidenceIds": [
        "TR-xage-1"
      ]
    },
    "lastRound": {
      "date": "2025-12",
      "stage": "Equity financing",
      "amount": "$15 million",
      "lead": "Piva Capital",
      "evidenceIds": [
        "TR-xage-1"
      ]
    }
  },
  {
    "id": "zenity",
    "name": "Zenity",
    "domainIds": [
      "ai-security"
    ],
    "kind": "private",
    "headlineMetric": {
      "label": "Revenue growth (company-stated)",
      "value": "tripled year-over-year in each of the past two years; on track to triple again in 2026",
      "period": "as of 2026-08-03",
      "evidenceIds": [
        "TR-zenity-1"
      ]
    },
    "lastRound": {
      "date": "2026-08-03",
      "stage": "Series C",
      "amount": "$125 million",
      "lead": "Norwest",
      "evidenceIds": [
        "TR-zenity-1"
      ]
    }
  },
  {
    "id": "zscaler",
    "name": "Zscaler",
    "domainIds": [
      "network-sase"
    ],
    "kind": "public",
    "ticker": "ZS",
    "cik": "0001713683",
    "edgarId": "zscaler",
    "headlineMetric": {
      "label": "ARR",
      "value": "$3,771 million",
      "period": "Q4 FY2026, ended 2026-07-31",
      "evidenceIds": [
        "TR-zscaler-1"
      ]
    },
    "revenue": {
      "latest": {
        "value": "$898.2 million",
        "yoyGrowth": "25%",
        "period": "Q4 FY2026",
        "periodEnd": "2026-07-31",
        "releaseDate": "2026-09-03",
        "evidenceIds": [
          "TR-zscaler-1"
        ]
      },
      "prior": {
        "value": "$850.5 million",
        "yoyGrowth": "25%",
        "period": "Q3 FY2026",
        "periodEnd": "2026-04-30",
        "evidenceIds": [
          "TR-zscaler-2"
        ]
      }
    },
    "ownership": {
      "status": "Independent, publicly traded on Nasdaq since 2018 IPO.",
      "evidenceIds": [
        "TR-zscaler-1"
      ]
    }
  }
]
