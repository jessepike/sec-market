"""Prepare an isolated acknowledged-manifest overlay; never modify the frozen baseline."""
from pathlib import Path, PurePosixPath
import argparse, hashlib, json, os, shutil
def digest(raw): return hashlib.sha256(raw).hexdigest()
def records(raw):
    result = {}
    for row in json.loads(raw)["files"]:
        path = PurePosixPath(row["key"])
        assert path.parts[0] == "state" and ".." not in path.parts and not path.is_absolute()
        assert row["key"] not in result
        result[row["key"]] = row
    return result
def main():
    p = argparse.ArgumentParser()
    p.add_argument("baseline"); p.add_argument("baseline_sha"); p.add_argument("manifest")
    p.add_argument("manifest_sha"); p.add_argument("manifest_blob"); p.add_argument("destination");p.add_argument("needed")
    a = p.parse_args()
    baseline, dest = Path(a.baseline), Path(a.destination)
    previous = (baseline / "archive-manifest.json").read_bytes()
    raw = Path(a.manifest).read_bytes()
    assert digest(previous) == a.baseline_sha and digest(raw) == a.manifest_sha
    assert hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() == a.manifest_blob
    old, new = records(previous), records(raw)
    assert all(key in new for key in old)
    assert all(not path.is_symlink() for path in baseline.rglob("*"))
    assert not dest.exists() and not dest.is_relative_to(baseline)
    shutil.copytree(baseline, dest, copy_function=os.link)
    (dest / "archive-manifest.json").unlink()
    (dest / "archive-manifest.json").write_bytes(raw)
    needed = []
    for key, row in new.items():
        if old.get(key) == row:
            continue
        target = dest / key
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            target.unlink()
        needed.append(row)
    Path(a.needed).write_text(json.dumps(needed, indent=2) + "\n")
    print(json.dumps({"baselineEntries":len(old),"acknowledgedEntries":len(new),
                      "newOrChangedFilesRequired":len(needed),"unchangedFilesReused":len(new)-len(needed),
                      "completeArchiveAuthenticated":False}))
if __name__ == "__main__": main()
