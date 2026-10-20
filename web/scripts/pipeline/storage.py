"""Immutable evidence and compare-and-swap heads with integrity on every read."""
import json
import os
import re
import tempfile
import fcntl
from contextlib import contextmanager
from pathlib import Path

from contracts import canonical, digest, require


class ConflictError(RuntimeError):
    pass


class LocalStore:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, key):
        require(isinstance(key, str) and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_./-]*", key), "Invalid archive key")
        require(".." not in key.split("/"), "Archive path traversal")
        result = (self.root / key).resolve()
        require(result.is_relative_to(self.root), "Archive path escapes root")
        return result

    def put(self, body):
        body = body if isinstance(body, bytes) else canonical(body)
        sha = digest(body)
        self.write_once(f"objects/{sha}", body)
        return {"key": f"objects/{sha}", "sha256": sha, "bytes": len(body)}

    def get(self, reference):
        body = self._path(reference["key"]).read_bytes()
        require(digest(body) == reference["sha256"] and len(body) == reference["bytes"], "Archived evidence failed integrity verification")
        return body

    def read(self, key):
        path = self._path(key)
        return json.loads(path.read_text()) if path.exists() else None

    def write_once(self, key, body):
        body = body if isinstance(body, bytes) else canonical(body)
        path = self._path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        # Write+fsync a complete temporary object before atomically linking it.
        fd, temp = tempfile.mkstemp(dir=path.parent, prefix=".incoming-")
        try:
            with os.fdopen(fd, "wb") as out:
                out.write(body)
                out.flush()
                os.fsync(out.fileno())
            try:
                os.link(temp, path)
            except FileExistsError:
                require(path.read_bytes() == body, "Immutable object collision")
            self._sync_directory(path.parent)
        finally:
            os.unlink(temp)

    @staticmethod
    def _sync_directory(path):
        fd = os.open(path, os.O_RDONLY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)

    @contextmanager
    def lock(self, name, blocking=False):
        path = self._path(f"locks/{name}")
        path.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(path, os.O_CREAT | os.O_RDWR, 0o600)
        try:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | (0 if blocking else fcntl.LOCK_NB))
            except BlockingIOError as exc:
                raise ConflictError("Publisher already locked") from exc
            os.ftruncate(fd, 0)
            os.write(fd, str(os.getpid()).encode())
            os.fsync(fd)
            yield
        finally:
            # Kernel locks release on a crash; never unlink a lock another worker opened.
            fcntl.flock(fd, fcntl.LOCK_UN)
            os.close(fd)

    def compare_and_swap(self, name, expected, value):
        with self.lock(name.replace("/", "_")):
            key = f"heads/{name}.json"
            if self.read(key) != expected:
                raise ConflictError("Stale expected release/checkpoint head")
            path = self._path(key)
            path.parent.mkdir(parents=True, exist_ok=True)
            fd, temp = tempfile.mkstemp(dir=path.parent, prefix=".head-")
            try:
                with os.fdopen(fd, "wb") as out:
                    out.write(canonical(value))
                    out.flush()
                    os.fsync(out.fileno())
                os.replace(temp, path)
                self._sync_directory(path.parent)
            finally:
                if os.path.exists(temp):
                    os.unlink(temp)

    def export(self, destination):
        """Copy verified immutable objects and metadata into a portable backup."""
        other = LocalStore(destination)
        require(not other.root.is_relative_to(self.root), "Backup must be outside the source archive")
        manifest = []
        for path in sorted(self.root.rglob("*")):
            if path.is_file() and not path.is_symlink() and "locks" not in path.relative_to(self.root).parts and not path.name.startswith("."):
                key = str(path.relative_to(self.root))
                body = path.read_bytes()
                if key.startswith("objects/"):
                    require(key == f"objects/{digest(body)}", "Corrupted object during backup")
                other.write_once(key, body)
                manifest.append({"key": key, "sha256": digest(body), "bytes": len(body)})
        result = {"schemaVersion": 1, "files": manifest}
        other.write_once("backup-manifest.json", result)
        return {"manifest": result, "manifestSha256": digest(result)}

    @staticmethod
    def verify_export(root, expected_sha256):
        store = LocalStore(root)
        manifest = store.read("backup-manifest.json")
        require(manifest is not None, "Backup manifest missing")
        require(digest(manifest) == expected_sha256, "Backup root differs from independently retained manifest hash")
        for item in manifest["files"]:
            store.get(item)
        return manifest
