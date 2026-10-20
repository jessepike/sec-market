"""Immutable Vercel Build Output payloads with a detached release receipt.

The payload hash excludes only that receipt, avoiding a self-referential hash.
The transport ZIP has its own independent content address in the evidence store.
"""
import io
import json
import stat
import zipfile
from pathlib import Path, PurePosixPath

from contracts import canonical, digest, require

RECEIPT = "static/deployment-receipt.json"


def inventory(files):
    return [{"path": name, "sha256": digest(body), "bytes": len(body)} for name, body in sorted(files.items()) if name != RECEIPT]


def unpack(body):
    require(len(body) <= 100_000_000, "Build archive exceeds transport budget")
    result, size = {}, 0
    with zipfile.ZipFile(io.BytesIO(body)) as archive:
        for item in archive.infolist():
            path = PurePosixPath(item.filename)
            require(not path.is_absolute() and ".." not in path.parts and "\\" not in item.filename, "Unsafe build archive path")
            require(not stat.S_ISLNK(item.external_attr >> 16), "Build symlinks prohibited")
            require(not item.is_dir() and item.filename not in result, "Duplicate/directory build member")
            require(item.filename == "config.json" or item.filename.startswith("static/"), "Unsupported executable build member")
            size += item.file_size
            require(size <= 200_000_000 and item.file_size <= 50_000_000 and len(result) < 20000, "Expanded build exceeds byte/file budget")
            result[item.filename] = archive.read(item)
    require("config.json" in result and "static/index.html" in result and "static/app-release.json" in result, "Incomplete static build output")
    config = json.loads(result["config.json"])
    require(config.get("version") == 3 and set(config).issubset({"version", "routes", "overrides"}), "Unexpected executable build configuration")
    for route in config.get("routes", []):
        require(set(route).issubset({"src", "headers", "continue", "handle", "status", "dest"}), "Unexpected route capability")
        require(not route.get("dest", "").startswith(("http:", "https:", "//")), "External rewrite prohibited")
    return result


def pack(files):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, body in sorted(files.items()):
            entry = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            entry.external_attr = (stat.S_IFREG | 0o644) << 16
            entry.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(entry, body)
    return buffer.getvalue()


def build_artifact(store, dist, vercel_config):
    dist = Path(dist).resolve()
    files = {}
    for path in sorted(dist.rglob("*")):
        require(not path.is_symlink(), "Build output contains symlink")
        if path.is_file():
            key = "static/" + path.relative_to(dist).as_posix()
            require(key != RECEIPT, "Receipt must be detached after payload testing")
            files[key] = path.read_bytes()
    routes = [{"src": h["source"], "headers": {v["key"]: v["value"] for v in h["headers"]}, "continue": True} for h in vercel_config.get("headers", [])]
    routes.append({"handle": "filesystem"})
    files["config.json"] = canonical({"version": 3, "routes": routes})
    archive = pack(files)
    unpack(archive)
    manifest = inventory(files)
    return {"sha256": digest(manifest), "archive": store.put(archive), "inventory": store.put(manifest)}


def stage_files(store, artifact, receipt):
    files = unpack(store.get(artifact["archive"]))
    manifest = inventory(files)
    require(digest(manifest) == artifact["sha256"] and canonical(manifest) == store.get(artifact["inventory"]), "Build payload differs from tested inventory")
    require(receipt["artifactSha256"] == artifact["sha256"], "Detached receipt differs from tested payload")
    files[RECEIPT] = canonical(receipt)
    return files
