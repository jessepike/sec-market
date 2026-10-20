#!/usr/bin/env python3
"""Prepare or install a daily local worker; dry-run is the default.

Run on the existing, regularly awake computer with its own `codex login` and
GitHub Git access. This installer never creates or transfers credentials.
"""
import argparse
import json
import os
import platform
import plistlib
import shutil
import subprocess
import sys
from pathlib import Path


def prepare(repo, directory, system=None):
    repo, directory = Path(repo).resolve(), Path(directory).resolve()
    system = system or platform.system()
    if not (repo / "ops/worker/worker.py").is_file():
        raise ValueError("Use the reviewed daily-pipeline checkout")
    if directory.is_relative_to(repo):
        raise ValueError("Persistent worker state must be outside the checkout")
    for executable in ("node", "codex", "git", "gh", "pdftotext"):
        if not shutil.which(executable):
            raise ValueError(f"Required program missing: {executable}")
    revision = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    config = directory / "worker.json"
    if config.exists():
        raise ValueError("An existing worker configuration needs review before replacement")
    config.write_text(json.dumps({"repo": str(repo), "reviewedRevision": revision,
                                 "state": str(directory / "state"), "archiveMirror": str(directory / "archive-mirror")}, indent=2) + "\n")
    config.chmod(0o600)
    launcher = directory / "launch.py"
    shutil.copyfile(repo / "ops/worker/launch.py", launcher)
    launcher.chmod(0o700)
    args = [sys.executable, str(launcher), "--config", str(config)]
    if system == "Darwin":
        target = directory / "com.securitymarketpulse.daily.plist"
        target.write_bytes(plistlib.dumps({"Label": "com.securitymarketpulse.daily", "ProgramArguments": args,
                                          "WorkingDirectory": str(repo), "EnvironmentVariables": {"PATH": os.environ["PATH"]},
                                          "StartCalendarInterval": {"Hour": 5, "Minute": 17},
                                          "RunAtLoad": True,
                                          "StandardOutPath": str(directory / "scheduler.log"), "StandardErrorPath": str(directory / "scheduler-error.log")}))
        note = "Runs at 05:17 local time; launchd runs a missed calendar job after sleep when the computer wakes."
    elif system == "Linux":
        target = directory / "securitymarketpulse-daily.service"
        # JSON quoting is systemd's quoted argument syntax, never shell code.
        target.write_text("[Unit]\nDescription=Security Market Pulse daily collection\n[Service]\nType=oneshot\n"
                          + "Environment=" + json.dumps("PATH=" + os.environ["PATH"]) + "\n"
                          + "UMask=0077\nWorkingDirectory=" + str(repo) + "\nExecStart=" + " ".join(json.dumps(a) for a in args) + "\n")
        (directory / "securitymarketpulse-daily.timer").write_text("[Unit]\nDescription=Daily market collection timer\n[Timer]\nOnCalendar=*-*-* 12:17:00 UTC\nPersistent=true\n[Install]\nWantedBy=timers.target\n")
        note = "Runs at 12:17 UTC; persistent timer catches up when the computer starts."
    else:
        raise ValueError("Supported persistent hosts: macOS or Linux")
    return {"config": str(config), "schedule": str(target), "system": system, "note": note,
            "oneShot": args, "credentialsCopied": False, "installed": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=str(Path(__file__).resolve().parents[2]))
    parser.add_argument("--directory", default=str(Path.home() / ".local/share/securitymarketpulse"))
    parser.add_argument("--install", action="store_true", help="Activate the prepared user schedule on this computer")
    args = parser.parse_args()
    result = prepare(args.repo, args.directory)
    if args.install:
        login = subprocess.run(["codex", "login", "status"], check=True, capture_output=True, text=True)
        if "using ChatGPT" not in login.stdout + login.stderr:
            raise ValueError("Use the computer's official codex login --device-auth; API-key billing is not allowed")
        subprocess.run(["gh", "auth", "status"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        repo = Path(args.repo).resolve()
        clean = subprocess.run(["git", "-C", str(repo), "status", "--porcelain", "--untracked-files=normal"], check=True, capture_output=True, text=True)
        if clean.stdout.strip():
            raise ValueError("Install from a clean dedicated worker checkout")
        # Restore existing evidence and budgets before any scheduled collection.
        sys.path.insert(0, str(repo / "web/scripts/pipeline"))
        from archive import GitArchive
        from contracts import digest
        config = json.loads(Path(result["config"]).read_text())
        archive = GitArchive(config["archiveMirror"], "https://github.com/jessepike/sec-market.git")
        tip = archive._open()
        if tip:
            manifest = json.loads((archive.root / "archive-manifest.json").read_text())
            result["restoredArchive"] = archive.restore(config["state"], tip, digest(manifest))
        if result["system"] == "Darwin":
            folder = Path.home() / "Library/LaunchAgents"
            folder.mkdir(parents=True, exist_ok=True)
            target = folder / Path(result["schedule"]).name
            if target.exists():
                raise ValueError("An existing schedule needs review before replacement")
            shutil.copyfile(result["schedule"], target)
            subprocess.run(["launchctl", "bootstrap", f"gui/{os.getuid()}", str(target)], check=True)
        else:
            folder = Path.home() / ".config/systemd/user"
            folder.mkdir(parents=True, exist_ok=True)
            for suffix in ("service", "timer"):
                name = "securitymarketpulse-daily." + suffix
                if (folder / name).exists():
                    raise ValueError("An existing schedule needs review before replacement")
                shutil.copyfile(Path(args.directory).expanduser() / name, folder / name)
            subprocess.run(["systemctl", "--user", "daemon-reload"], check=True)
            lingering = subprocess.run(["loginctl", "show-user", str(os.getuid()), "--property=Linger", "--value"], capture_output=True, text=True, check=True)
            if lingering.stdout.strip() != "yes":
                subprocess.run(["loginctl", "enable-linger", str(os.getuid())], check=True)
            subprocess.run(["systemctl", "--user", "enable", "--now", "securitymarketpulse-daily.timer"], check=True)
        result["installed"] = True
    print(json.dumps(result, indent=2))
