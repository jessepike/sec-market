# November 2 GitHub account readback

The existing signed-in account's Billing Usage page shows November 1–30, 2026, with November 1 gross USD 0.60 and billed USD 0, and November 2 gross USD 0.43 and billed USD 0. These are current reported values, not a settled monthly bill.

The Billing Overview identifies GitHub Free at USD 0/month. Its initially loaded header showed gross USD 1.03 and included usage USD 1.01, which did not reconcile to the Usage page's rounded billed zero. After selecting and loading the Actions panel, its authoritative detailed readback reports:

- Billable usage after discounts: USD 0.
- Consumed usage: USD 1.03; discounts: USD 1.04.
- Compute: USD 1.00 used of USD 12.00 included.
- Actions storage: 0 GB used of 0.5 GB included, a coarse rounded view.
- Included usage reset: 29 days.

The account-wide display changed while data loaded. Preserve the initial discrepancy and the later actual Actions detail; neither supports exact independent cent reconciliation or precise accrued storage. No plan, paid-overage budget, account setting or notification was changed. The unchanged paid-overage budget was last independently verified at zero on November 1, not freshly changed or inferred from today's zero billable amount. Today's observations do not establish sufficient capacity for a month or for other repositories.

Source pages: `https://github.com/settings/billing/usage` and `https://github.com/settings/billing`, inspected in the existing owner browser on November 2 at approximately 16:40–16:45 UTC. Actual runner/step timing is separately retained by the runner reduction spec. Included discounts are account-wide and do not make runner usage unlimited.
