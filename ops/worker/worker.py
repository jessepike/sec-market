#!/usr/bin/env python3
"""Run the daily collector on an existing ChatGPT-authenticated computer.

No copied subscription tokens, API keys, hosted runner registration or new
service is required. The outside GitHub probe must watch its archived receipts.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path


def execute(config):
    repo = Path(config["repo"]).resolve()
    sys.path.insert(0, str(repo / "web/scripts/pipeline"))
    from contracts import digest, require, utcnow
    from storage import LocalStore
    from archive import GitArchive
    from release import release_daily
    revision = config["reviewedRevision"]
    require(len(revision) == 40 and all(c in "0123456789abcdef" for c in revision), "Pin the reviewed full commit")
    result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True, check=True)
    require(result.stdout.strip() == revision, "Worker checkout changed; review and repin before running")
    changed = subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"], cwd=repo, capture_output=True, text=True, check=True)
    require(not changed.stdout.strip(), "Worker checkout has uncommitted application changes")
    state = LocalStore(config["state"])
    require(not state.root.is_relative_to(repo), "Worker state must survive checkout cleanup")
    with state.lock("daily-worker"):
        command = [sys.executable, str(repo / "web/scripts/pipeline/cli.py"), "--state", str(state.root)]
        log_dir = state.root / "worker-logs"
        log_dir.mkdir(exist_ok=True)
        started = utcnow()
        log_file = log_dir / (started.replace(":", "-") + ".jsonl")
        results = {}
        contract = json.loads((repo / "contracts/market.json").read_text())
        def run(phase, extra):
            # Pipeline output contains public evidence and bounded reason codes only.
            with log_file.open("ab") as output:
                try:
                    r = subprocess.run(command + [phase, *extra], cwd=repo, stdout=output, stderr=output, timeout=3*3600)
                    results[phase] = r.returncode
                except subprocess.TimeoutExpired:
                    # Continue to archive and alert. An execution timeout must not
                    # disappear as an absent receipt on an otherwise healthy host.
                    results[phase] = 124
        latest = state.read("heads/latest-run.json")
        old_coverage = json.loads(state.get(latest["receipt"])) if latest else None
        old_plan = state.read(f"runs/{old_coverage['runId']}/plan.json") if old_coverage else None
        reuse = bool(old_coverage and old_coverage["complete"] and old_coverage["contractSha256"] == digest(contract)
                     and old_plan["scheduledAt"][:10] == started[:10])
        if reuse:
            results["run"] = 0
        else:
            run("run", ["--subscription-worker"])
        run("verify", [])
        run("report", ["--destination", str(state.root / "reports" / started.replace(":", "-"))])
        run("snapshot", ["--destination", str(state.root / "heads/dailySnapshot.json")])
        prior = state.read("heads/worker-heartbeat.json")
        heartbeat = {"startedAt": started, "finishedAt": utcnow(), "appRevision": revision,
                     "phases": results, "reusedCompletedDailyCollection": reuse, "publication": "held_until_release_gate_and_cutover"}
        state.compare_and_swap("worker-heartbeat", prior, heartbeat)
        # Back up even degraded runs: failure evidence is part of the contract.
        archive = GitArchive(config["archiveMirror"], config.get("archiveRemote", "https://github.com/jessepike/sec-market.git"))
        archived = archive.push(state)
        released = release_daily(state, contract, archived, revision, config, checkpoint=lambda: archive.push(state))
        heartbeat["publication"] = released
        current = state.read("heads/worker-heartbeat.json")
        state.compare_and_swap("worker-heartbeat", current, heartbeat)
        final_archive = archive.push(state)
        print(json.dumps({"heartbeat": heartbeat, "archive": final_archive}))
        return 0 if all(v == 0 for v in results.values()) else 2


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    try:
        raise SystemExit(execute(json.loads(Path(args.config).read_text())))
    except (ValueError, OSError, RuntimeError, subprocess.SubprocessError) as error:
        print(json.dumps({"ok": False, "errorType": type(error).__name__, "reason": str(error)[:160]}), file=sys.stderr)
        raise SystemExit(2)
