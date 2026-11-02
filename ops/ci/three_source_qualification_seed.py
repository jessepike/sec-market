"""One exact K inventory seed, composed with the unchanged J package."""
import json
from pathlib import Path
import re

from contracts import canonical, digest, require
import html_qualification_seed as html
import q4_qualification_seed as q4seed
import three_source_qualification_origin as three

KIND = "three_source_qualification_seed"
PACKAGE = {'bytes': 30265,
 'path': 'contracts/three-source-qualification-seeds/6cb053a5954a52f2dddf7773caeca1db436dbe5966e085ea421d911691774a68/seed.json',
 'sha256': '01d8478e12f6ee53b977f144ac18305cac302e05f564710b7a9009fface67dcd'}
ARCHIVE = {"commit": "e5f189981428adf720c783c613685fbd969fd16c",
           "manifestSha256": "d6be094e27da036581b5bdef63b1cf1e7a0574f4cc68fccdac0091e48d35efd6"}


def _payload(repo, pin):
    root = Path(repo).resolve()
    prefix = "contracts/three-source-qualification-seeds/" + three.AUTHORITY["activatedContractSha256"] + "/"
    require(type(pin) is dict and set(pin) == {"path", "sha256", "bytes"} and
            type(pin["path"]) is str and pin["path"].startswith(prefix) and ".." not in pin["path"].split("/") and
            type(pin["bytes"]) is int and 0 < pin["bytes"] <= 32_000_000 and
            isinstance(pin["sha256"], str) and re.fullmatch(r"[a-f0-9]{64}", pin["sha256"]),
            "THREE_SEED_PAYLOAD_PIN_INVALID")
    path = root / pin["path"]
    require(path.resolve().is_relative_to(root) and not any(root.joinpath(*path.relative_to(root).parts[:i]).is_symlink()
            for i in range(1, len(path.relative_to(root).parts) + 1)), "THREE_SEED_PATH_ESCAPES")
    raw = path.read_bytes()
    require(digest(raw) == pin["sha256"] and len(raw) == pin["bytes"], "THREE_SEED_PAYLOAD_BYTES_DIFFER")
    return raw


def validate_seed(repo, store, contract, at):
    require(three.is_successor(contract), "THREE_SEED_EXACT_K_REQUIRED")
    raw = _payload(repo, PACKAGE)
    manifest = json.loads(raw)
    require(canonical(manifest) == raw and set(manifest) == {"schemaVersion", "kind", "activatedContractSha256",
            "transition", "originalJPackage", "files", "actualArchive"} and type(manifest["schemaVersion"]) is int and
            manifest["schemaVersion"] == 1 and manifest["kind"] == KIND and
            manifest["activatedContractSha256"] == digest(contract) and
            manifest["transition"] == three.AUTHORITY["transition"] and
            manifest["originalJPackage"] == q4seed.PACKAGE and manifest["actualArchive"] == ARCHIVE,
            "THREE_SEED_MANIFEST_AUTHORITY_DIFFERS")
    files = {}
    for entry in manifest["files"]:
        require(type(entry) is dict and set(entry) == {"key", "sha256", "bytes", "path"} and
                isinstance(entry["key"], str) and re.fullmatch(
                    r"(?:objects/[a-f0-9]{64}|observations/[a-f0-9]{64}\.json|contracts/[a-f0-9]{64}\.json|ci/source-probe-runs/[0-9]+-[0-9]+\.json|source-qualification-transitions/[a-f0-9]{64}\.json)", entry["key"]) and
                entry["key"] not in files, "THREE_SEED_IMMUTABLE_KEY_INVALID")
        body = _payload(repo, {key: entry[key] for key in ("path", "sha256", "bytes")})
        if entry["key"].startswith("objects/"):
            require(entry["key"] == "objects/" + digest(body), "THREE_SEED_OBJECT_ADDRESS_DIFFERS")
        try:
            require(store.get({key: entry[key] for key in ("key", "sha256", "bytes")}) == body,
                    "THREE_SEED_EXISTING_IMMUTABLE_DIFFERS")
        except FileNotFoundError:
            pass
        files[entry["key"]] = body
    require(list(files) == sorted(files), "THREE_SEED_FILE_ORDER_DIFFERS")
    old_manifest = json.loads(q4seed._payload(repo, q4seed.PACKAGE))
    old_files = {entry['key']: q4seed._payload(repo, {key: entry[key] for key in ('path', 'sha256', 'bytes')})
                 for entry in old_manifest['files']}
    overlay = html._Overlay(store, {**old_files, **files})
    original = three.inverse_policy(contract, overlay)
    old = q4seed.validate_seed(repo, overlay, original, at)
    require(not (set(old["files"]) & set(files)), "THREE_SEED_DUPLICATES_OLD_PACKAGE")
    union = {**old["files"], **files}
    overlay = html._Overlay(store, union)
    inventories = {}
    import source_qualification_origin as origins
    for sid in (*html.SOURCE_IDS, *q4seed.q4.SOURCE_IDS, *three.SOURCE_IDS):
        prior = origins.qualification_predecessors(contract, sid, overlay, at)
        require(len(prior) == 1, "THREE_SEED_ORIGIN_MISSING")
        result = origins.resolve_inventory_origin(prior[0], contract, sid, overlay, at)
        require(result["authority"] == "inventory_only", "THREE_SEED_SEMANTIC_AUTHORITY_FORBIDDEN")
        inventories[sid] = {"documents": len(result["items"]), "itemsSha256": digest(result["items"]),
                            "completedAt": result["completedAt"]}
    # Old preservation validation remains exact under J; unchanged source contexts also bind K.
    from separation import semantic_context
    for source in original["sources"]:
        if source["id"] not in three.SOURCE_IDS:
            require(canonical(semantic_context(original, source["id"])) ==
                    canonical(semantic_context(contract, source["id"])), "THREE_SEED_UNCHANGED_CONTEXT_DIFFERS")
    return {"files": union, "manifestSha256": digest(raw), "contractSha256": digest(contract),
            "preservation": old["preservation"], "qualificationInventory": inventories}


def seed_before_collection(repo, root, store, session, contract, runtime):
    require(Path(runtime.REPO).resolve() == Path(repo).resolve() and
            digest(json.loads((Path(repo) / "contracts/market.json").read_bytes())) == digest(contract),
            "THREE_SEED_RUNTIME_POLICY_OR_REPOSITORY_DIFFERS")
    html._context(root, store, session, runtime, runtime.utcnow())
    checked = validate_seed(repo, store, contract, runtime.utcnow())
    html._context(root, store, session, runtime, runtime.utcnow())
    for key, raw in checked["files"].items():
        store.write_once(key, raw)
    html._context(root, store, session, runtime, runtime.utcnow())
    result = {k: v for k, v in checked.items() if k != "files"}
    result.update(coverageCredit=False, semanticAdmission=False, sourceChecksCredited=0)
    receipt = runtime.checkpoint(root, store, session, "qualification_seeded", result)
    from storage import LocalStore
    archive = receipt.get("archive")
    require(type(archive) is dict and re.fullmatch(r"[a-f0-9]{40}", archive.get("commit", "")) and
            re.fullmatch(r"[a-f0-9]{64}", archive.get("manifestSha256", "")) and
            LocalStore(root).read("heads/remote-archive.json") == archive and
            receipt.get("receipt", {}).get("phase") == "qualification_seeded" and
            receipt["receipt"].get("sessionId") == session["sessionId"] and
            receipt["receipt"].get("appRevision") == session["appRevision"] and
            receipt["receipt"].get("role") == "collector" and receipt["receipt"].get("contractSha256") == digest(contract) and
            receipt["receipt"].get("result") == result, "THREE_SEED_REMOTE_ACK_REQUIRED")
    html._context(root, store, session, runtime, runtime.utcnow())
    return {**result, "archive": archive}
