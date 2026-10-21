# Codex cloud scheduling: current research and acceptance

Researched October 20, 2026 (America/Los_Angeles), from the current official OpenAI documentation.
**Cloud-first is the owner's requested route. An always-on local computer is not an established
requirement. No recurring cloud job has been created or verified by this onboarding chat.**

## Verified product capabilities

| Capability | Current official evidence | What it establishes |
|---|---|---|
| Cloud coding execution | [Codex Cloud](https://learn.chatgpt.com/docs/cloud) and [Cloud environments](https://learn.chatgpt.com/docs/environments/cloud-environments) say tasks can continue while the computer sleeps, edit code and run commands in isolated workspaces | Remote execution exists; a published environment supplies repositories, dependencies and access |
| Web schedules | [Scheduled tasks, web](https://learn.chatgpt.com/docs/automations?surface=web) describes recurring tasks, standalone runs and schedules that return to an existing chat | Cloud scheduling is a product capability; it must not be confused with desktop project scheduling |
| Chat-based creation | The same guide says tasks can be created/updated from a ChatGPT or Codex chat, with a schedule that returns to that chat | Prepare the real cloud chat and test the scheduled execution context, rather than assuming a laptop is required |
| Subscription use | [Pricing](https://learn.chatgpt.com/docs/pricing) says ChatGPT Work and Codex share usage; local messages and cloud chats share plan allowance | API-key billing is a separate path. Subscription does not mean unlimited execution; additional credits must not be purchased automatically |
| Desktop/local distinction | [Execution modes](https://learn.chatgpt.com/docs/environments/modes) and the automation guide require the computer/app for tasks using local projects/worktrees | This requirement applies to local execution; it is not evidence that remote scheduled work is unsupported |
| Team Tasks distinction | [Teams](https://learn.chatgpt.com/docs/enterprise/teams) explicitly says Team Tasks use workspace credits | Do not select this as a substitute for the owner's individual subscription workflow without a separate billing decision |
| Durable environment inputs | Current cloud environment docs distinguish published starting files, per-task state, automatic repository refresh and destination-scoped network secrets | A fresh scheduled run must restore operational state; published setup is not the evidence database or a live daemon |

The public documentation was reached through OpenAI's own redirects from developers.openai.com
to learn.chatgpt.com. The new host initially received a cloud proxy CONNECT 403. Its network
allowance subsequently took effect and the current Markdown pages were fetched. No further
network action is currently required to read these sources.

Installed Codex CLI 0.163.0 independently confirms `cloud exec --env ... --branch ...` and a live
ChatGPT-authenticated `cloud list --json` request succeeded. This establishes cloud-service access,
not that a scheduler has been created or that a particular published environment is selected.
The CLI's documented cloud commands do not expose schedule creation; this is not evidence that the
web product lacks it. This onboarding chat's available tools likewise expose no schedule-creation
or schedule-update operation. Do not call that an account-level absence.

## Cloud-first implementation

1. Publish the reviewed reusable environment with Node 22, Python, tools, allowed source/service
   hosts, and start instructions. Exclude personal OAuth/CLI credential files from its snapshot.
2. Start a regular cloud task using **Work in > Cloud** and select that environment. Load the
   reviewed repository revision, not unrelated preview code. Restore the exact latest private
   evidence archive and its budgets/checkpoints before collection.
3. Create a personal recurring task associated with that cloud chat/environment. The intended
   collector cadence is daily at 05:17 America/Los_Angeles. A separate fresh governance context
   follows after the collection window, initially 08:17 America/Los_Angeles. Both must report real
   run IDs, checked/missing counts, pending claims and remote archive acknowledgements.
4. Use the subscription-authenticated execution path. Before unattended activation, prove that a
   fresh cloud run can perform actual model work without reusing a token copied into an image or
   falling back to a billed API. The current nested CLI adapter needs this fresh-run auth test;
   native scheduled-agent execution is an alternative adapter, not an already-completed integration.
5. Keep deterministic reconciliation and the exact-artifact GitHub gate separate from collection.
   Publish at most two factual batches/day, using reviewed app code and independently validated data.
   Vercel management access, exact prebuilt staging and its 32 browser tests are already verified.
6. Keep the outside GitHub watchdog. A scheduled agent must not be the only observer of its own
   missing run. Show incomplete/overdue coverage publicly and notify the owner when a run is absent,
   blocked, exhausted or unresolved.

For durable Vercel authorization, today's interactive OAuth proves this running task's access. It
is not proof that a future scheduled VM inherits it. Choose and test a destination-scoped managed
credential, or a controlled Git-based release publisher using the existing Vercel integration.
The latter can avoid a new Vercel secret, but changing production's release branch/path is a major
cutover requiring a concrete reviewed implementation. No credentials were created or copied to CI.

## Acceptance before enabling recurring production publication

- A native schedule exists in Scheduled with the expected time zone, target cloud chat/environment,
  subscription/default model choice and next-run time. Saving a prompt is not creating the schedule.
- **Run now** starts the actual cloud execution, reports the repo/revision and restores remote state.
  Then a timed canary starts without an active local app/computer. Verify its actual runtime/tools;
  web schedule documentation alone does not prove this account's environment binding works.
- Fresh-run GitHub access and model inference work; Vercel publishing authentication survives a new
  VM through the selected governed path. Neither a local browser sign-in nor a published filesystem
  is used as a credential-transfer mechanism.
- Stop/skip a collector canary and verify the outside monitor detects the missing heartbeat. Restore
  it, verify deduplication/recovery, and prove no-change, amendment, failed source and bad release.
- Complete the still-open source bindings, historical backfill/claim mapping and measured daily
  capacity. Current real coverage remains 252/557; native scheduling alone does not close those gaps.
- Execute the trusted main-branch release gate and real production acknowledgement/rollback after
  the existing major-change review. Agree and complete the outreach burn-in period.

No always-on local host is requested while this native cloud route is being evaluated. The existing
Mac/Linux installer remains an implemented fallback only.
