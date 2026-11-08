"""Git-backed evidence archive, using a dedicated private repository and no database.

Normal fast-forward pushes arbitrate concurrent writers. Every version has an
independently verifiable manifest; restoration needs no original worker disk.
"""
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

from contracts import canonical, digest, require
from storage import LocalStore, ConflictError


# The evidence archive holds full copies of third-party pages, so it lives in a
# private repository of its own while the application repository is public.
# Runners reach it over SSH with a write deploy key scoped to that one repository.
EVIDENCE_REMOTE = "git@github.com:jessepike/sec-market-private.git"


class GitArchive:
    def __init__(self, mirror, remote, branch="data/archive"):
        require(branch == "data/archive", "Evidence must use the dedicated archive ref")
        require(remote == EVIDENCE_REMOTE or Path(remote).is_absolute(), "Unapproved archive remote")
        self.root = Path(mirror).resolve()
        self.remote, self.branch = remote, branch
        # Ordinary application fetches use refs/heads/* and do not download this
        # evidence history. Keep large source bodies out of routine app clones.
        self.remote_ref = "refs/archive/market-evidence"

    def _git(self, *args, check=True):
        result = subprocess.run(["git", "-C", str(self.root), *args], capture_output=True, timeout=180)
        if check:
            require(result.returncode == 0, "GIT_ARCHIVE_OPERATION_FAILED")
        return result

    def _open(self):
        self.root.mkdir(parents=True, exist_ok=True)
        if not (self.root / ".git").exists():
            require(not any(self.root.iterdir()), "Dedicated archive mirror must start empty")
            self._git("init", "--initial-branch=" + self.branch)
            self._git("remote", "add", "origin", self.remote)
            self._git("config", "--local", "smp.evidenceArchive", "true")
        require(self._git("config", "--local", "--get", "smp.evidenceArchive").stdout.decode().strip() == "true", "Not a dedicated evidence mirror")
        require(self._git("config", "--get", "remote.origin.url").stdout.decode().strip() == self.remote, "Archive remote differs")
        self._git("config", "user.name", "Jesse Pike")
        self._git("config", "user.email", "jesse@keatingpike.com")
        refs = self._git("ls-remote", "origin", self.remote_ref).stdout.decode().split()
        if refs:
            expected = refs[0]
            require(re.fullmatch(r"[a-f0-9]{40}", expected), "Invalid remote archive ref")
            self._git("fetch", "--no-tags", "origin", self.remote_ref)
            require(self._git("rev-parse", "FETCH_HEAD").stdout.decode().strip() == expected, "Archive ref changed during fetch; retry")
            self._git("checkout", "-B", self.branch, "FETCH_HEAD")
            return expected
        return None

    def push(self, store, expected_commit=None):
        require(not self.root.is_relative_to(store.root), "Archive mirror must be outside source state")
        with LocalStore(self.root.parent / (self.root.name + "-lock")).lock("git-archive"):
            parent = self._open()
            if expected_commit is not None and parent != expected_commit:
                raise ConflictError("ARCHIVE_CHANGED_SINCE_RESTORE")
            previous = self.root / "archive-manifest.json"
            if previous.exists():
                self.verify(self.root)
            files = []
            for path in sorted(store.root.rglob("*")):
                key = path.relative_to(store.root).as_posix()
                if "locks" in path.relative_to(store.root).parts or path.name.startswith("."):
                    continue
                require(not path.is_symlink(), "Archive state contains symlink")
                if not path.is_file():
                    continue
                body = path.read_bytes()
                require(len(body) <= 50_000_000, "Archive file exceeds Git storage budget")
                if key.startswith("objects/"):
                    require(key == "objects/" + digest(body), "Corrupted source object")
                destination = self.root / "state" / key
                destination.parent.mkdir(parents=True, exist_ok=True)
                existing = destination.read_bytes() if destination.exists() else None
                if existing is not None and not key.startswith("heads/"):
                    require(existing == body, "Immutable remote evidence differs")
                if existing != body:
                    if existing is not None:
                        destination.unlink()  # never write through a link shared with restored state
                    destination.write_bytes(body)
                files.append({"key": "state/" + key, "sha256": digest(body), "bytes": len(body)})
            old_files = json.loads(previous.read_text())["files"] if previous.exists() else []
            # An incomplete local restore must never delete remote evidence.
            keys = {f["key"] for f in files}
            for item in old_files:
                if item["key"] not in keys:
                    require(not item["key"].startswith("state/heads/"), "Restore remote heads before writing archive")
                    files.append(item)
            files.sort(key=lambda f: f["key"])
            manifest = {"schemaVersion": 1, "files": files}
            previous.write_bytes(canonical(manifest))
            # Archive commits contain no app and explicitly disable Git deployments.
            (self.root / "vercel.json").write_bytes(canonical({"git": {"deploymentEnabled": False}}))
            (self.root / "web").mkdir(exist_ok=True)
            (self.root / "web/vercel.json").write_bytes(canonical({"git": {"deploymentEnabled": False}}))
            (self.root / ".gitattributes").write_text("state/objects/* -text\n")
            self._git("add", "--all")
            changed = self._git("diff", "--cached", "--quiet", check=False).returncode
            if changed:
                self._git("commit", "-m", "data(archive): retain evidence " + digest(manifest))
                pushed = self._git("push", "origin", "HEAD:" + self.remote_ref, check=False)
                if pushed.returncode:
                    raise ConflictError("ARCHIVE_PUSH_REJECTED_RETRY_AFTER_RESTORE")
            commit = self._git("rev-parse", "HEAD").stdout.decode().strip()
            return {"commit": commit, "parentCommit": parent, "manifestSha256": digest(manifest), "files": len(files), "ref": self.remote_ref}

    @staticmethod
    def verify(root, expected_manifest=None):
        root = Path(root).resolve()
        manifest = json.loads((root / "archive-manifest.json").read_text())
        if expected_manifest:
            require(digest(manifest) == expected_manifest, "Remote archive root differs")
        for item in manifest["files"]:
            key = item["key"]
            require(key.startswith("state/") and ".." not in Path(key).parts, "Archive path escapes state")
            path = root / key
            require(not path.is_symlink() and path.resolve().is_relative_to(root), "Archive symlink prohibited")
            body = path.read_bytes()
            require(digest(body) == item["sha256"] and len(body) == item["bytes"], "Remote archive integrity mismatch")
            if key.startswith("state/objects/"):
                require(Path(key).name == digest(body), "Remote content address differs")
        return manifest

    def restore(self, destination, expected_commit=None, expected_manifest=None):
        parent = self._open()
        require(parent is not None, "No remote archive exists")
        if expected_commit:
            require(parent == expected_commit, "Remote archive commit differs from pinned receipt")
        manifest = self.verify(self.root, expected_manifest)
        destination = Path(destination).resolve()
        require(not destination.exists() or not any(destination.iterdir()), "Restore destination must be empty")
        # Hard links, not copies: the archive is 2.6 GB and growing, and a second
        # full copy filled the runner's disk on November 5. Every store write
        # makes a new file (temporary file, then link or rename), and push()
        # replaces a changed mirror file instead of writing into it, so the two
        # trees never change each other's bytes.
        def link_or_copy(source, target):
            try:
                os.link(source, target)
            except OSError:
                shutil.copy2(source, target)
            return target
        shutil.copytree(self.root / "state", destination, dirs_exist_ok=True, copy_function=link_or_copy)
        return {"commit": parent, "manifestSha256": digest(manifest), "files": len(manifest["files"])}
