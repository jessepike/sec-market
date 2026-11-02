# Independent service-cost attribution

November 2, 2026. The current-cycle Vercel export reports **$17.3196227705662081732580** for the two Security Market Pulse projects. **$17.26899999999999999 is build CPU usage**, making builds the material cost. The narrower stopped-trial calculation still starts October 30 at 07:00 UTC. Its latest forecast is **$0.370780121391**, above the approved $0.30 stop. No spending or dispatch is authorized by this review.

## Source, calculation and scope

The original owner-account download is `vercel-costs (28).csv`, downloaded **November 2 at 18:41:05 UTC**, 244,988 bytes, SHA-256 **`c40d16b3725c2d8e4b66c6dbb9ecf1af2ed6a2d4bce07de23cf60212f2bddf44`**. Its ignored local path is `/Users/jessepike/.codex/worktrees/market-managed-runtime/sec-market/.ctx/billing-full-period-2026-11-02/billing.csv`. The owner selected the current **October 18–November 18** billing cycle. This is an unfinished cycle with observed day rows through November 2, not a forecast for the rest of the cycle or a settled invoice. No exact provider metered-through timestamp is supplied.

Independently parsed **1,594 source records** and selected exactly **103 records** using only reader project ID `prj_g8sZPXo81XT2Xopa1oLrsbYjTehV` and proof project ID `prj_d2GuxLptHspqQjh2CeT7fW8H8pvd`. Every selected original row, zero charge and numeric string is preserved in `/Users/jessepike/.codex/worktrees/market-managed-runtime/sec-market/docs/active/daily-pipeline/receipts/service-and-cost-inventory-2026-11-02/full-period-attribution.json`. That file includes every metric, day, project/day sum and reported usage quantity. It contains no other projects' names or rows. The raw all-project source remains ignored.

Calculations used Python standard-library `Decimal` at 100-digit precision in the existing OrbStack dev VM, with `sudo unshare -n` and a cleared environment. All selected starts were checked against Pacific local midnight using `zoneinfo`; no duplicate selected day/project/metric keys were found. No package, network, provider, billing, journal, project, deployment or credential action occurred.

## Current-cycle project attribution

| Project | Exact reported USD |
| --- | ---: |
| Public reader / publisher project | **17.1790821405953948844366** |
| Stopped managed-runtime proof project | **0.1405406299708132888214** |
| Combined current-cycle reported usage | **17.3196227705662081732580** |

Reader costs are build CPU **$17.129**, deployment storage **$0.0459016405953948845**, Web Analytics **$0.003449999999999999936**, and additional CDN CPU **$0.0007305000000000000006**. CDN requests and Fast Data Transfer have zero reported charges. These zeros do not mean unlimited future use.

The proof project's build CPU row is raw **$0.13999999999999999** for **40 CPU-minutes**, consistent with the previously reviewed failed Turbo and five Basic builds. Its other reported meters are Function Storage **$0.00038323154792229093**, active CPU **$0.0000664754919739405**, Workflow events **$0.00006**, provisioned memory **$0.00002100264868845591**, Function invocations **$0.0000059951278928136424**, origin transfer **$0.00000100182**, Workflow storage writes **$0.000000296**, Workflow retention **$0.000000227334335797839**, and four Queue meters at **$0.0000006 each**. Proof CDN requests and Fast Data Transfer report zero. Function storage continues after execution is stopped; the total is not just the build row.

The combined build meter reports **4,934 CPU-minutes**. Of these, **4,860 CPU-minutes / $17.010** precede the trial window and belong to the reader. Aggregate CPU-minutes do not identify the number of deployments or the machine class of each historical build; those claims require historical native deployment logs. The already retained actual November 1 log separately establishes that publication's Turbo machine, and the November 2 native logs establish Basic machines.

The reader's October 18–29 usage totals **$17.042242649175606066123**. That historical operating/development cost must appear in a complete service-cost inventory. It must not be silently inserted into, or deducted from, the later bounded trial's source scope. Existing trial receipts deliberately cover the two projects from October 30 onward.

## Reported provider days

These are combined selected-project subtotals. Dates use the provider's original row timestamps.

| Pacific date / UTC row start | Reported USD |
| --- | ---: |
| October 18 / 07:00 | 0.630045583333333333334 |
| October 19 / 07:00 | 0.210760083333333333332 |
| October 20 / 07:00 | 1.050109499999999999995 |
| October 21 / 07:00 | 1.15518449999999999998 |
| October 22 / 07:00 | 2.310171750000000000004 |
| October 23 / 07:00 | 4.5189033092199505 |
| October 24 / 07:00 | 2.52358932170642996615 |
| October 25 / 07:00 | 4.10005133692782463333 |
| October 26 / 07:00 | 0.10982118945679726666 |
| October 27 / 07:00 | 0.424925910051285033336 |
| October 28 / 07:00 | 0.004329457573325999998 |
| October 29 / 07:00 | 0.004350707573326000004 |
| October 30 / 07:00 | 0.1449451104028299979014 |
| October 31 / 07:00 | 0.0046556286466056666466 |
| November 1 / 07:00, closed 25-hour day | **0.109361864982585966667** |
| November 2 / 08:00, incomplete | **0.01841751735858047592** |

November 1 remains above the normal $0.05 condition by **$0.059361864982585966667**. No cheaper later machine, report or day changes that failed result. These source rows are reported usage, not a final invoice or a demonstration that every operational day had the same workload.

## Latest November 2 observation

The new export reports reader **$0.018322299030497185** and proof **$0.00009521832808329092**, totaling **$0.01841751735858047592**. The proof's November 2 Function Storage row has now appeared. It confirms the earlier absence could not support a zero-storage claim.

| November 2 meter | Reported USD |
| --- | ---: |
| Reader build CPU, four CPU-minutes | 0.014 |
| Reader deployment storage | 0.004035549030497185 |
| Reader Web Analytics, nine events | 0.00027 |
| Reader additional CDN CPU | 0.00001675 |
| Proof Function Storage | 0.00009521832808329092 |
| Reader CDN requests and Fast Data Transfer | 0 |
| Combined | **0.01841751735858047592** |

The build row still reports the earlier two Basic builds; this CSV supplies no newly billed third build. It also cannot rule out unreported later activity. Root reports that no later Preview/production build had started when this export was obtained. This review makes no further provider or dispatch check.

The newly reported reader storage amount is lower than the earlier November 2 export. Preserve both original reports and any retained class/report high-water amount; this revised partial row is not a refund or authority to reduce a reservation. The combined bounded trial sum is higher after continuing proof storage appears.

November 2 closes **November 3 at 00:00 Pacific / 08:00 UTC**. A later completed-range export after reporting lag, all retained resources, later builds/traffic and applicable taxes is required before claiming a full-day pass. The difference between today's partial subtotal and five cents is not an approved spendable balance or a guarantee for additional Preview/production builds. No future build is authorized here.

## Unchanged trial source scope and denial

Selecting only rows from the original **October 30 07:00 UTC** start gives **40 records** and exact reported usage **$0.2773801213906021071350**. Sum first and round upward once to picodollars:

`$0.277380121391 + $0.0934 retained net reservations = $0.370780121391`.

That exceeds the approved **$0.30** stop by **$0.070780121391**. Including the unmade corrected copy/storage reservation of $0.0112 would yield **$0.381980121391**. Both deny paid trial work. The $0.0934 remains carried from the existing reviewed accounting; this audit grants no offset, scope change, release, refund or new matching rule. Original failures, storage, transfer buffers and uncertainty remain counted. The earlier higher value of an individual revised row is preserved in its original receipt, while the conservative cumulative baseline remains at least the latest higher combined amount.

## Shared account fees and other services

Root's current owner-account invoice readback reports **one Vercel Pro platform seat at $20/month**, **$55.65 account on-demand charges after $20 usage credit**, and an upcoming **$75.65** account total ending November 18: `$20 + $55.65 = $75.65`. This is an unfinished all-project account bill. The displayed account product amounts, including Build CPU $46.58 and Vercel Agent $28.49, are not Pulse-only attribution. This two-project export contains no Vercel Agent meter for Pulse. Do not assign the whole shared seat, all-project Agent cost, shared usage credits or unspecified tax to these projects, and do not subtract the same credit twice. The source above establishes project resource usage; an agreed shared-cost allocation and final invoice remain separate.

Root also reports a fresh native Cloudflare Workers plan readback of **Free, current $0**, with no $5/month paid trial purchased. It supplies no Cloudflare execution cost for the production pipeline. Existing GitHub-hosted temporary runners execute production; the repository API reports **zero self-hosted runners**. The last retained GitHub account read shows included compute and a $0 paid-overage budget with Usage blocked. Included runner/artifact capacity is shared and finite; this Vercel export does not refresh its consumption or establish future monthly capacity. No additional runner subscription, home-host charge or model API fee is established by this audit.

Those account/service observations are relayed from the owning session; this independent task made no UI, network or provider calls. I would keep Basic capacity, retain the paid-trial hold, and reconcile complete-day and shared-account costs before another cost-fit claim. A new paid synthetic trial would add no evidence needed to explain the already successful scheduled publication.
