#!/usr/bin/env python3
"""Follow approved main changes while preserving the explicitly installed pin.

A reviewed setup pin may be ahead of main during initial collection testing.
Unrelated preview commits are never pulled into the unattended worker.
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def launch(config_path):
    path = Path(config_path).resolve()
    config = json.loads(path.read_text())
    repo = Path(config["repo"]).resolve()
    sys.path.insert(0, str(repo / "web/scripts/pipeline"))
    from contracts import require
    from storage import LocalStore
    with LocalStore(path.parent).lock("worker-launcher"):
        def git(*args, check=True):
            result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, timeout=180)
            if check:
                require(result.returncode == 0, "APPROVED_WORKER_CHECKOUT_UPDATE_FAILED")
            return result
        current = git("rev-parse", "HEAD").stdout.strip()
        require(current == config["reviewedRevision"], "Worker code differs from installed pin")
        require(not git("status", "--porcelain", "--untracked-files=normal").stdout.strip(), "Worker checkout has local changes")
        git("fetch", "--no-tags", "origin", "refs/heads/main:refs/remotes/origin/main")
        latest = git("rev-parse", "refs/remotes/origin/main").stdout.strip()
        if current != latest:
            if git("merge-base", "--is-ancestor", current, latest, check=False).returncode == 0:
                git("merge", "--ff-only", latest)
                config["reviewedRevision"] = latest
                with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, delete=False) as temporary:
                    json.dump(config, temporary, indent=2)
                    temporary.flush()
                    os.fsync(temporary.fileno())
                    temporary_path = temporary.name
                os.chmod(temporary_path, 0o600)
                os.replace(temporary_path, path)
            else:
                require(git("merge-base", "--is-ancestor", latest, current, check=False).returncode == 0,
                        "Approved main diverged from the installed setup pin; inspect before changing the worker")
        return subprocess.run([sys.executable, str(repo / "ops/worker/worker.py"), "--config", str(path)], cwd=repo).returncode


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    try:
        raise SystemExit(launch(args.config))
    except (ValueError, OSError, RuntimeError, subprocess.SubprocessError) as error:
        print(json.dumps({"ok": False, "reason": str(error)[:160]}), file=sys.stderr)
        raise SystemExit(2)
