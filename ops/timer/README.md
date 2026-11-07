# Pipeline timer and outside watchdog (Vercel Cron)

A small Vercel project that does two jobs outside GitHub Actions (D-127):

| Path | Schedule (UTC) | What it does |
|---|---|---|
| `/api/dispatch` | 05:17 daily | Starts the collector workflow with `timer=true` on `main` |
| `/api/watchdog` | every 6 hours at :41 | Alerts the owner when any of these is true: the published data is stale or unreadable, the latest daily collector run failed or never started, or the ChatGPT login has expired |
| `/api/health` | hourly at :11 | Rewrites one issue, "Site health: OK" or "Site health: N failing", with a table of every check (live site, data age, timer, collection time against the job limit, ChatGPT login, runner disk, publisher, collection reaching the site, GitHub Actions running, weekly funding job, open alerts, Actions minutes, live code against main, shipped pages, request box). Edits are silent; it comments, which notifies, only when a check newly goes bad and once on recovery. If a finished release gate has no publisher run after it, it starts one (the split release's fallback). Run it locally without writing: `GITHUB_TOKEN=$(gh auth token) node ops/timer/health-cli.mjs` |
| `/api/request` | on demand (public) | The site's "Want a company tracked?" box (D-136). Adds the name to one private issue, "Company requests from the site", with an issues-only token |

## Company request box

`POST /api/request` with `{ name, website, elapsed }` from an allowed origin (the site and its
preview; override with `REQUEST_ORIGINS`, comma-separated). The hidden `website` field and an
`elapsed` under 1.5 seconds are treated as bots: the answer says ok and nothing is written. Names
are 2 to 60 letters, digits, spaces and `. & ' + -`, with no links. A repeat raises the count
silently; a new name edits the list and comments once, which notifies the assignee. At most 10 new
names a day and 500 in total; past that, requests are dropped quietly. Close the issue to start a
fresh list. Requests never change the site.

The watchdog alerts through one GitHub issue, "Daily pipeline needs attention (outside watchdog)".
The issue is assigned to the owner and opened by the GitHub App, so GitHub emails or pushes it to
the owner. The issue is updated while problems last and closes itself on recovery. Reading GitHub's
API and opening issues still work when Actions is blocked, for example by billing.

The login check reads a `chatgpt-login` annotation on the collection job. The collector workflow
writes it when the model step reports `CHATGPT_SUBSCRIPTION_LOGIN_REQUIRED` or `CHATGPT_SIGN_IN_AGAIN`.

GitHub's own schedule (`17 5` and the `47 9` backup) still runs. Each timer start skips once a timer
collection has already succeeded that UTC day (`ops/ci/schedule_guard.py`), so a late GitHub run
never collects twice.

The code has no dependencies and is shared by any pipeline site. Each site deploys its own Vercel
project from this folder, with its own GitHub App installation and settings. No credential or data
is shared between sites.

## Credential: a GitHub App (preferred)

Create a private GitHub App owned by your account, with no webhook. Give it these repository
permissions: Actions read and write, Checks read, Issues read and write, Metadata read. Install it
on `jessepike/sec-market` only, then generate a private key.

The watchdog uses a GitHub App instead of a personal token because GitHub never notifies you about
issues your own token opens. App tokens also expire after one hour and cover only this repository.
A fine-grained personal token (`GITHUB_TOKEN`) still works for dispatch, but its alerts will not
notify you.

## Settings (Vercel environment variables, Production)

| Name | Security Market Pulse value |
|---|---|
| `GITHUB_APP_ID` | The app's ID, from its settings page |
| `GITHUB_APP_PRIVATE_KEY` | The full private key (`.pem` text) |
| `CRON_SECRET` | A random string of 16 or more characters. Vercel sends it with each cron call |
| `GITHUB_REPO` | `jessepike/sec-market` |
| `WORKFLOW_FILE` | `subscription-collector.yml` |
| `DATA_URL` | `https://securitymarketpulse.com/daily-coverage.json` |
| `MAX_AGE_HOURS` | `30`. Optional; matches `overdueHours` |
| `ALERT_ASSIGNEE` | `jessepike`. Optional; defaults to the repository owner |

## Set up

1. Create and install the GitHub App as described above.
2. In Vercel, add a new project from `jessepike/sec-market`. Set the root directory to `ops/timer`,
   the framework to "Other" and the production branch to `main`. Add the settings above.
3. Crons run only on the production deployment, so nothing fires until `ops/timer` is on `main`.
   `vercel.json` skips builds for other branches and for commits that do not touch this folder, so
   routine pushes use no build minutes.
4. After the first production deployment, run each cron once from the Vercel dashboard (Settings,
   Cron Jobs, Run). Check that the dispatch starts a run named "daily timer collection".

If a dispatch fails, it returns 502 in the Vercel cron log. GitHub's backup schedule and the
watchdog still cover the day.

Test: `npm test` (Node 22, no install needed).
