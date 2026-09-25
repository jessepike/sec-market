# Audit: how complete is full site autonomy?

Read-only audit of `/Users/jessepike/code/projects/sec-market`, run 2026-09-25. No files in the repo
were changed. Every claim below names the file and line (or a live check, such as a `gh run` log)
it came from. Anything not directly verified is marked **inference**.

Bottom line up front: the pipeline from a public document to a *drafted* issue is real and running
weekly. The one step the owner wants gone — his tap of approval before anything reaches the public
site — is deliberately still there, by design, in the spec the owner himself approved five days ago
(D-73, 2026-09-21). Removing it is not a small technical step; it means rewriting the gate logic,
the file-allowlist guard, the data-integrity checks, and the "a named person signs" language baked
into the constraints file and the intent document, and it removes the one safety mechanism the
project's own review process just finished hardening. On top of that, there is one currently broken
mechanical link (the pull-request bot lacks permission to open PRs) and one host outage that has
stopped this week's gather entirely.

---

## 1. The weekly gather

**What runs, where.** `scripts/com.securitymarketpulse.gather.plist` installs a launchd agent on
macbook2014, firing Tuesdays 07:00 local time (plist lines 30-38), which calls
`scripts/gather.sh` (plist line 27). This is **not** what `docs/active/gather-job-spec.md` (v0.2,
2026-09-03) describes — that spec calls for "a Claude Code cloud routine" with no host dependency
(`gather-job-spec.md:22-33`). The cloud routine was tried and abandoned: its egress proxy blocked
every public host the job needs (`docs/active/fable-run/automation-plan.md:18-25`, citing the
2026-09-05 dry run). D-70 (`decisions.md:828-849`) records the switch to macbook2014/launchd as the
actual, current runtime. `gather-job-spec.md` itself is stale and superseded — BACKLOG SEC-049 says
so explicitly (`BACKLOG.md:607-615`: "This supersedes the cloud-routine plan... nothing further is
needed there").

**What `gather.sh` does** (`scripts/gather.sh`, full file read):
- Loads a Claude subscription token from `~/.env.local` if present (lines 62-68), because launchd
  and a non-interactive shell don't inherit a login environment.
- Resets the repo to `origin/preview`, works out which ISO week is due, and exits early
  (`state: nothing-due`) if that issue already exists or its branch is already on the remote
  (lines 70-99).
- Probes the Claude login with a one-token `claude -p "ok"` call; if it's expired, exits
  `blocked-auth` and tells you to run `claude setup-token` (lines 101-113).
- Hands the actual work to `claude -p` with model `claude-sonnet-5` (default, line 22), instructing
  it to read and carry out `docs/active/gather-brief.md` (lines 115-146).
- Runs headless with a **pre-approved, narrow tool allowlist** — curl, shasum, jq, pdftotext,
  specific git subcommands, `npm run`/`npm ci` — and an explicit denylist blocking any push to
  `main`, `preview`, or a force-push (lines 166-228).
- After the model exits, checks that a branch actually reached GitHub, and independently re-checks
  that only the five allowed files were touched (`BLOCKED_PATHS` check, lines 251-278) — this is a
  second, independent copy of the same allowlist check that lives in `publish-issue.sh`
  (comment at lines 260-263 says so explicitly).
- Writes a JSON receipt to `~/gather-logs/receipts/` every run, success or failure (lines 36-52).

**What the brief tells the model to do** (`docs/active/gather-brief.md`, v0.2, full file read): fetch
from a fixed, closed source list (§2, lines 57-70) with `curl` so it holds the actual bytes, hash
every quoted document, date every item from a primary source rather than a roundup, cap eight items
per lane, and write to **exactly five files**: the new issue module, the issues index, the
append-only evidence file, `prints.ts` (scorecard figures only), and `.gather/pr-body.md`
(lines 29-40). It explicitly may never touch `domains.ts`, `hypotheses.ts`, `market.ts`, `meta.ts`,
`printsUnverified.ts`, or any existing issue, and never pushes to `main` or `preview` — one branch
only, `issue/<id>` (lines 33-39). This is **automated** end to end, in the sense that no person
starts it — but see §5 below on whether it actually fires unattended.

**Why the week-38 branch has no pull request.** The gather run did produce a real, fully-gated
draft: `origin/issue/2026-w38` exists, with `.gather/pr-body.md` on it (verified via
`git show origin/issue/2026-w38:.gather/pr-body.md`) reporting all five build gates passing (0/0/0/0,
154 data tests), eight formation items, one absorption item, and a "Scorecard changes: None this
week" line (no in-window prints found). `.github/workflows/gather-pr.yml` is the piece that's
supposed to open the pull request from that pushed branch (triggers on `push: branches: ['issue/**']`,
lines 8-10) — I ran it: `gh run view 35658917857` (2026-09-21T21:44:33Z, `completed failure`). The
log line is exact: **`pull request create failed: GraphQL: GitHub Actions is not permitted to
create or approve pull requests (createPullRequest)`.** This is a GitHub repository setting
("Allow GitHub Actions to create and approve pull requests", under Settings → Actions → General →
Workflow permissions) that is currently off. **This is broken, not by design** — it is a one-checkbox
repo setting, not a code change, and it silently drops every week's draft into a state with no
notification at all. I did not change the setting; it's outside a read-only audit's scope, but it's
the single highest-value fix available today, unrelated to the "should it be autonomous" question.

**Current state of the host.** `status.md` (top of "Current State", read directly): macbook2014 has
been unreachable since partway through 2026-09-21 — it dropped off the network mid-run and hasn't
answered ssh or ping since. No receipt and no confirmed firing exist for the 2026-09-22 07:00
Tuesday schedule. The week-38 branch that does exist was pushed by a **hand-started** run under
Opus, not by the scheduled launchd job under Sonnet (`docs/active/fable-run/automation-plan.md:27-33`
— a real drift from both the runtime and the model-tier rule).

---

## 2. GitHub workflows and the human gate

Four workflows, `scripts/publish-issue.sh` (full file read, 814 lines), and
`docs/active/publish-path-spec.md` v0.2 ("as built") together implement the gate.

| Workflow | Trigger | What it does |
|---|---|---|
| `gather-pr.yml` | push to `issue/**` | Opens the PR from the pushed branch (currently broken — see §1) |
| `publish-issue.yml` | an approving review, or an `issue_comment` whose trimmed body is exactly `publish` or `publish reconfirm`, from the repo owner only | Runs `publish-issue.sh` in three phases and is the entire publish path |
| `freshness.yml` | daily cron 08:00 Pacific | Polls the live site; opens/closes a GitHub issue if the newest published issue is >10 days old |
| `web.yml` | push/PR touching `web/**` | `npm ci && npm run lint && npm test` — ordinary CI, not part of the publish decision |

**The human gate, exactly.** `publish-issue.yml`'s "Resolve the event and check every condition"
step (lines 71-201) requires, in order: the actor equals `github.repository_owner` (line 102); the
event is either `pull_request_review` with `state == approved` (lines 104-114), or an `issue_comment`
on that PR whose lower-cased, trimmed body is exactly `publish` or `publish reconfirm`
(lines 135-139); and the head branch matches `issue/*` with base `preview` (lines 150-167). Nothing
else satisfies it — "request changes," a plain comment, or silence does nothing
(`publish-path-spec.md:36`).

**What the machine does once approved**, run by `scripts/publish-issue.sh` in three phases so the
untrusted issue branch never runs code while holding a push token (doc comment, lines 9-24,
41-78): `guard` (no token) verifies the checked-out commit is the one actually approved
(`approved_sha_matches`, line 274), that the branch didn't change after a `publish` comment was
posted (`branch_changed_after_comment`, line 305), and that only the five allowed files were
touched (`is_allowed_issue_branch_path`, lines 287-297 — the same five paths `gather.sh` also
checks). `build` (still no token) merges `preview`, runs `sign-issue.ts` (turns the draft into a
signed, published issue), appends the lock manifest, runs the full `npm test` suite, and commits
locally. `release` (the only phase with a token) verifies a second, independently-checked-out
"trusted" copy of the publisher script hasn't been tampered with, then pushes `preview`, the issue
branch, and — **only if `preview` already matched `main` outside record-keeping paths** — `main`
(step 8, `publish-issue.sh:415-431`), then polls the live site for up to 15 minutes and comments
the result.

**What would have to change to remove the human gate while keeping the automated checks.** The
`npm run verify:*` gates (`edition`, `panel`, `integrity`, `issue`, `prints`) are separable from the
approval logic — they already run inside `build_phase` (`step4_test`, line 363, via `npm test`)
independent of who or what triggered the run. To go fully autonomous you would need to:

1. Change `publish-issue.yml`'s trigger from `pull_request_review`/`issue_comment` to something that
   fires on its own (a `schedule:` cron, or `push` on the `issue/**` branch itself) — i.e., delete
   the actor/approval condition block at lines 71-201 entirely, or replace it with an
   always-true condition.
2. Remove or repurpose the `APPROVED_SHA` / `COMMENT_CREATED_AT` guards in `guard_phase()`
   (`publish-issue.sh:544-633`), since there is no longer an approval event to check a commit
   against.
3. Change `sign-issue.ts`'s signature semantics: `weThink.signedBy` currently must equal
   `AUTHOR_NAME` (`web/src/data/types.ts:356`, "must equal AUTHOR_NAME in meta.ts when set") and is
   set from the approval event, not from the machine (`publish-path-spec.md:58-59`). An autonomous
   path either signs under the owner's name with no owner action (which is the actual thing the
   "named person signs" rule exists to prevent — see §4), or introduces a second, machine-attributed
   signature type, which is a new judgment-authority concept the project has not designed.
4. Decide what happens to `weThink.summary`, `postureDeltas`, and `noCalls` — currently these are
   drawn from the *approved* `proposed` block, on the theory that his approval is his agreement with
   that specific text (`publish-path-spec.md:56`). Autonomous publishing means the machine's own
   proposal becomes the published judgment with no review — this is the actual site content readers
   see, not a mechanical step.
5. `.claude/rules/constraints.md` (Authorization section) currently still reads "Production
   collectors, database, scheduler, website, digest, and autonomous pipeline are not authorized" —
   this line already lags what's built (the scheduler and signing pipeline exist and are approved
   under D-70/D-73), and `publish-path-spec.md:89-98` flags it as the owner's line to personally
   amend. Full autonomy would need this rule, and the corresponding language in `intent.md`, changed
   again to actually authorize unattended publication — today they authorize a human-approved one.

None of this is large in engineering terms (points 1-2 are maybe an hour of workflow-YAML and
bash editing). Point 3-5 are judgment/governance changes, not code — they're the actual question
the owner is asking, dressed as a completeness question.

---

## 3. What the job updates vs. does not

**Weekly issue content** (`web/src/data/issues/<id>.ts`, `evidence.ts`): fully proposed by the
gather, fully gated by `verify:issue`'s 16 checks (`web/scripts/verify-issue.ts`, full file read —
ordering/uniqueness, non-overlapping windows, four-lane structure, evidence-id resolution and
in-window dates, publish/signature consistency, at-most-one-draft, append-only lock manifest via two
independent anchors, posture-delta consistency, numeral-citation matching (check 12), strict dates,
per-lane bounds, evidence receipts, fiscal-period mismatch, reconfirmation validity, and a real React
render check). **Automated draft, human-gated publish.**

**Vendor scorecard** (`web/src/data/prints.ts`): **Partly automated, and this directly answers the
"does earnings automatically refresh a scorecard figure" question — no.** SEC-044 and SEC-045
(`BACKLOG.md:548-575`) record this as "built" as of 2026-09-21: the brief instructs the gather to
update the matching `prints.ts` entry for any supplier whose print fell inside *that week's* gather
window (`gather-brief.md:114-122`, §3 step 5), gated by a new check, `verify:prints`
(`web/scripts/verify-prints.ts`, referenced in `publish-path-spec.md:161-163`) that confirms company,
metric, period, and units together, not just that a number appears. But this update only happens
**as a side effect of the weekly gather cycle**, only for issuers whose fiscal period closed inside
that specific week's window, and it is still bundled into the same pull request the owner has to
approve — there is no separate, immediate trigger tied to an earnings release landing on some other
day. The week-38 PR body I read confirms the mechanism works but found nothing to update that week
("Scorecard changes: None this week... EDGAR sweep... found no in-window 8-K/10-Q results" —
`.gather/pr-body.md` on `origin/issue/2026-w38`). Prints that fail the new check aren't deleted or
silently exempted — they go on a dated, shrink-only exceptions list, `printsUnverified.ts`
(`publish-path-spec.md:164-167`), which the gather is explicitly forbidden to edit.

**"Going stale" and challenged stances**: automated *detection*, human-gated *action*.
`report:stale` (`web/scripts/stale-report.ts`) lists every judged claim >45 days old and every
scorecard print >150 days old, pasted verbatim into the PR body (`gather-brief.md:123-124`, §3 step
6). The gather may also flag a stance as *challenged* by this week's evidence
(`proposed.challengedClaimIds`, §3 step 7) — but it never rewrites `domains.ts`, `hypotheses.ts`, or
`platformPressure.ts` itself (`gather-brief.md:130-137`), and re-dating a stale-but-unchallenged
claim only happens if the owner's own approval or `publish` comment literally contains the word
"reconfirm" (`publish-path-spec.md:177-200`, "As built" note, T7-4).

**Domain stances/postures, platform pressure, activity, landscape**: **not touched by the job at
all.** These are explicitly on the gather's never-write list (`gather-brief.md:34-37`). SEC-045's own
"still open" note as of 2026-09-21 (`BACKLOG.md:566-575`) and SEC-049's summary
(`BACKLOG.md:622-627`) both confirm: the scorecard write-back is built, but *no other part of the
standing picture* auto-updates — that remains entirely manual, session-driven work.

---

## 4. Where "a named person signs" is enforced in code

- `web/src/data/types.ts:319` — `approvedBy: string // must equal AUTHOR_NAME in meta.ts`
- `web/src/data/types.ts:338` — `by: string // must equal AUTHOR_NAME in meta.ts`
- `web/src/data/types.ts:356-357` — `signedBy: string | null // must equal AUTHOR_NAME in meta.ts
  when set`, `signedOn: string | null`
- `web/src/data/meta.ts:29` — `export const AUTHOR_NAME = 'Jesse Pike'`, the single constant every
  one of the above checks against.
- `web/scripts/verify-issue.ts` check 5 (lines 512-591) — refuses to build if a published issue's
  `signedBy` isn't exactly `AUTHOR_NAME`, or if a draft has any signature/judgment fields set at all.
- `web/scripts/verify-issue.ts` check 17 (lines 856-877) — every reconfirmation record must be
  credited to `AUTHOR_NAME`, dated within bounds, and tied to a real published issue.
- `web/scripts/sign-issue.ts:86` — `computeSignedIssue(draft, { signedOn, authorName: AUTHOR_NAME })`
  is the one place a draft becomes a signed, published issue; it's called only from
  `publish-issue.sh`'s `build_phase` (`step2_sign`, line 350), which only runs after the `guard`
  phase has confirmed a real owner approval event (`publish-issue.yml:71-201`).
- `scripts/publish-issue.sh:379-390` — the release phase's `authed_push` function is the only piece
  of this whole chain that can ever write to a protected ref, and it exists only inside the phase
  gated by the approval check above.

**Every one of these would need to change** to allow unattended publishing: the `signedBy`/`by`/
`approvedBy` constraint would have to accept something other than `Jesse Pike`, or `AUTHOR_NAME`
itself would need to mean "the automated job" — which changes what the site's byline actually claims
to readers, not just a permission setting.

**One structural gap already known and unrelated to the approval gate**: SEC-051
(`BACKLOG.md:650-660`) — the same deploy key macbook2014 uses to push the `issue/<id>` branch has
push rights to any branch including `main`, because this is a free private repo with no branch
protection available. Every guard above is *code* sitting beside that open door, not a hard stop;
GitHub Pro (~$4/month) would close it, and the fix is unbuilt, "the owner's call."

---

## 5. Alternative runtimes already tried

Two were tried; two more were designed and shelved, per `docs/active/fable-run/automation-plan.md`
(full file read) and `decisions.md` D-70:

1. **Claude Code cloud routine.** Originally spec'd runtime (`gather-job-spec.md`). Created, disabled,
   dry-run 2026-09-05: the cloud environment's egress proxy returned 403 on every public host the
   brief needs, including a control host (`automation-plan.md:18-25`). **Status: abandoned**, per
   SEC-049 (`BACKLOG.md:614-615`, "supersedes the cloud-routine plan... nothing further is needed
   there").
2. **macbook2014 under launchd**, calling `claude -p` with the subscription (no API key). **Status:
   the current, live runtime** (D-70), needing no allowlist negotiation because it's on ordinary home
   internet — but see §1: it has been offline since 2026-09-21 and the gather can't fire while it's
   down.
3. **GitHub Actions on a cron trigger, or Vercel Cron**, considered and explicitly **not
   recommended** in `automation-plan.md:141-145`: a GitHub-hosted runner calling Claude would most
   likely need an API key (against the standing no-API-key rule), and the site has no serverless
   functions today, so Vercel Cron would mean adding one for no real benefit.
4. **A cloud routine with a curated egress allowlist** — designed in `durability-spec.md` §3 (not
   independently verified in this pass) with a one-off probe before arming, but superseded once the
   macbook2014 option was proven reachable (D-70) — not pursued further.

`docs/active/durable-signals-job.md` (also requested for this audit) is a much earlier, thinner
control document (`SEC-MARKET-SIG-OPS-001`, status "mapping") that predates and is superseded by the
above — it scopes an operating model, not a runtime choice, and explicitly excludes "building
collectors, scrapers, browsers, or schedulers" from its own remit (lines 27-32).

---

## Summary table

| Component | State | What full automation would take |
|---|---|---|
| Public-source gather (curl, hash, quote) | Automated | Nothing — already unattended when the host is up |
| Gather runtime (macbook2014/launchd) | Automated, but currently down | Fix host reachability; no design change |
| Gather → branch push | Automated | Nothing |
| Branch → pull request (`gather-pr.yml`) | Broken (repo setting blocks Actions PR creation) | Flip "Allow GitHub Actions to create and approve pull requests" in repo Settings — a few minutes, not a design change |
| Data-integrity gates (`verify:*`, `npm test`) | Automated | Nothing — already run unattended in `build_phase` |
| Scorecard figure updates (`prints.ts`) | Partly automated (proposed weekly, gated by `verify:prints`) | Would need a trigger independent of the weekly cycle to react to an earnings release the same day it lands; still bundled into the approval either way |
| Domain stances / platform pressure / hypotheses | Manual | Currently out of scope by design (gather-brief write-block); would need new judgment-automation the project has explicitly not built |
| Approval → sign → publish → promote | Human-gated by design (D-73), enforced in code at multiple points | Remove/replace the actor+approval condition in `publish-issue.yml`; redefine what `signedBy`/`AUTHOR_NAME` means for a machine-originated publish; rewrite `constraints.md` and `intent.md`'s authorization language, which is itself an owner-only edit |
| Freshness monitoring | Automated | Nothing |
| Site host / CI (`web.yml`) | Automated | Nothing |
| Branch-protection on `main` (SEC-051) | Missing | GitHub Pro (~$4/mo) or make repo public — owner call, unbuilt |
