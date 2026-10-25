"""Closed transport mechanics. No fetching, model work, quota or admission writes.

The optional actual-archive tests use only read/get and preserve original clocks.
Run with python3 -B -m unittest discover -s ops/ci -p test_s1_exact_filing_transport.py.
"""
import copy
from datetime import timedelta
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "web/scripts/pipeline"))
from contracts import canonical, digest, instant, require
from historical_correction_fixtures import historical_requests, historical_stamp
from corrections import (S1_TRANSPORT, REVIEW_RULES_VERSION, _index, group_review_policy,
                         load_policy, replay_admission, validate_sources)

FIXTURE = Path(__file__).parent / "fixtures/s1-exact-filing-transport.json"
ARCHIVE = Path(os.environ.get("SMP_S1_TRANSPORT_ARCHIVE", "/var/tmp/smp-seven-source-40131875060-20261024/extracted"))
MANIFEST_SHA = "895213b31bb9f75814acc9484cad9aabd3719e07ddd72c621275a9b2568a1e5c"
ORIGIN = "eafc5bf53cc59e4b0cb49f78039670ce6cff0baff0417b91eb465bf05cc533ab"


def read(path):
    return json.loads(path.read_bytes())


class TransportPolicyTests(unittest.TestCase):
    def setUp(self):
        self.group = read(FIXTURE)
        self.market = read(ROOT / "contracts/market.json")
        self.requests = historical_requests()
        self.baseline = self.requests["baseline"]["sha256"]

    def policy(self, group=None, market=None):
        return group_review_policy(group or self.group, market or self.market, self.baseline)

    def test_closed_tuple_and_policy_basis(self):
        source = self.group["sources"][0]
        self.assertEqual(source["transportAttestation"], S1_TRANSPORT)
        self.assertEqual(REVIEW_RULES_VERSION, "dated-factual-correction-review-1")
        original = next(e for e in read(ROOT / "web/src/data/tracker/originals.json")["evidence"] if e["id"] == "TR-s1-3")
        self.assertEqual(digest(original), S1_TRANSPORT["evidenceSha256"])
        bare = copy.deepcopy(self.group)
        del bare["sources"][0]["transportAttestation"]
        self.assertNotEqual(self.policy(), self.policy(bare))

    def test_all_attestation_fields_are_required_and_closed(self):
        source = self.group["sources"][0]
        for key in S1_TRANSPORT:
            for change in ("missing", "changed"):
                with self.subTest(key=key, change=change):
                    group = copy.deepcopy(self.group)
                    attestation = group["sources"][0]["transportAttestation"]
                    if change == "missing":
                        del attestation[key]
                    else:
                        attestation[key] = "changed"
                    with self.assertRaises(ValueError): self.policy(group)
        for value in (None, [], {}, {**S1_TRANSPORT, "extra": True}, {**S1_TRANSPORT, "schemaVersion": True},
                      {**S1_TRANSPORT, "body": {**source["body"], "extra": True}},
                      {**S1_TRANSPORT, "body": {**source["body"], "bytes": "49404"}}):
            with self.subTest(value=value):
                group = copy.deepcopy(self.group)
                group["sources"][0]["transportAttestation"] = value
                with self.assertRaises(ValueError): self.policy(group)

    def test_source_supplier_registration_and_body_cannot_borrow_rule(self):
        for key, value in (("sourceId", "s1:other"), ("evidenceId", "TR-s1-1"), ("url", S1_TRANSPORT["finalUrl"]),
                           ("observationId", "wrong"), ("fetchedAt", "2026-10-24"), ("extra", True),
                           ("body", {**S1_TRANSPORT["body"], "sha256": "0" * 64})):
            with self.subTest(key=key):
                group = copy.deepcopy(self.group)
                group["sources"][0][key] = value
                with self.assertRaises(ValueError): self.policy(group)
        group = copy.deepcopy(self.group)
        group["supplierId"] = "netskope"
        with self.assertRaises(ValueError): self.policy(group)
        market = copy.deepcopy(self.market)
        next(s for s in market["sources"] if s["id"] == S1_TRANSPORT["sourceId"])["required"] = False
        with self.assertRaises(ValueError): self.policy(market=market)

    def test_load_policy_accepts_optional_shape_only_in_temporary_contract(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            for name in ("contracts/factual-baseline.json", "web/src/data/tracker/originals.json"):
                target = repo / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((ROOT / name).read_bytes())
            requests = copy.deepcopy(self.requests)
            requests["groups"].append(self.group)
            (repo / "contracts/factual-corrections.json").write_bytes(canonical(requests))
            old = historical_stamp()
            stamp = {"schemaVersion": 1,
                     "policySha256": digest({"marketSha256": digest(self.market), "requestsSha256": digest(requests), "baselineSha256": self.baseline}),
                     "groupIds": [g["id"] for g in requests["groups"]],
                     "targetIds": [t["targetId"] for g in requests["groups"] for t in g["targets"]],
                     "sourceEvidenceIds": {g["id"]: [s["evidenceId"] for s in g["sources"]] for g in requests["groups"]},
                     "reviewPolicySha256ByGroup": {g["id"]: self.policy(g) for g in requests["groups"]}}
            (repo / "web/src/data/tracker/factualCorrectionPolicy.json").write_bytes(canonical(stamp))
            result = load_policy(repo, self.market)
            for gid, sha in old["reviewPolicySha256ByGroup"].items():
                self.assertEqual(result["reviewPolicySha256ByGroup"][gid], sha)
            # Recomputing the ordinary baseline cannot launder a changed immutable evidence pin.
            originals = read(repo / "web/src/data/tracker/originals.json")
            evidence = next(e for e in originals["evidence"] if e["id"] == "TR-s1-3")
            evidence["organization"] += " changed"
            baseline = read(repo / "contracts/factual-baseline.json")
            baseline["inventories"]["evidence"][evidence["id"]] = digest(evidence)
            (repo / "web/src/data/tracker/originals.json").write_bytes(canonical(originals))
            (repo / "contracts/factual-baseline.json").write_bytes(canonical(baseline))
            requests["baseline"]["sha256"] = digest(canonical(baseline))
            target = next(t for t in requests["groups"][-1]["targets"] if t["targetId"] == "evidence:TR-s1-3")
            target["original"] = copy.deepcopy(evidence)
            target["originalSha256"] = digest(evidence)
            target["proposedValue"]["organization"] = evidence["organization"]
            (repo / "contracts/factual-corrections.json").write_bytes(canonical(requests))
            with self.assertRaisesRegex(ValueError, "immutable evidence differs"):
                load_policy(repo, self.market)


class ReadOnlyArchive:
    """No LocalStore initialization or write interface; manifest-check every actual read."""
    def __init__(self, root):
        self.root = root
        raw = (root / "archive-manifest.json").read_bytes()
        require(digest(raw) == MANIFEST_SHA, "Actual archive manifest differs")
        self.entries = {e["key"]: e for e in json.loads(raw)["files"]}
        self.touched = {}

    def raw(self, key):
        path = self.root / "state" / key
        entry = self.entries.get("state/" + key)
        if entry is None:
            require(not path.exists(), "Actual archive file absent from manifest")
            return None
        body = path.read_bytes()
        require(digest(body) == entry["sha256"] and len(body) == entry["bytes"], "Actual archive bytes differ")
        self.touched[path] = (digest(body), len(body), path.stat().st_mtime_ns)
        return body

    def read(self, key):
        body = self.raw(key)
        return json.loads(body) if body is not None else None

    def get(self, reference):
        body = self.raw(reference["key"])
        require(body is not None and digest(body) == reference["sha256"] and len(body) == reference["bytes"], "Actual object reference differs")
        return body

    def assert_unchanged(self, test):
        for path, before in self.touched.items():
            body = path.read_bytes()
            test.assertEqual((digest(body), len(body), path.stat().st_mtime_ns), before)


@unittest.skipUnless((ARCHIVE / "archive-manifest.json").exists(), "Requires retained read-only seven-source archive")
class ActualTransportTests(unittest.TestCase):
    def setUp(self):
        TransportPolicyTests.setUp(self)
        self.store = ReadOnlyArchive(ARCHIVE)
        self.addCleanup(self.store.assert_unchanged, self)
        self.at = self.group["sources"][0]["fetchedAt"]

    def validate(self, group=None, store=None, at=None, market=None):
        return validate_sources(group or self.group, store or self.store, market or self.market, at or self.at)

    def overlay(self, **changes):
        original = self.store
        selected = self.group["sources"][0]["observationId"]
        class Overlay:
            get = original.get
            def read(self, key):
                row = original.read(key)
                if key == "observations/" + selected + ".json": row.update(changes)
                return row
        return Overlay()

    def test_authentic_304_and_full_200_keep_original_clocks_and_literal_body(self):
        source = self.group["sources"][0]
        documents = self.validate()
        self.assertEqual(len(documents), 1)
        self.assertIn("SENTINELONE", documents[0]["text"])
        self.assertIn("0001583708", self.store.get(source["body"]).decode())
        self.assertIn("2026-05-28", documents[0]["text"])
        self.assertEqual(len(self.store.touched), 9)  # Eight actual observations plus one body.
        group = copy.deepcopy(self.group)
        origin = self.store.read("observations/" + ORIGIN + ".json")
        group["sources"][0].update(observationId=ORIGIN, fetchedAt=origin["fetchedAt"])
        self.assertEqual(self.validate(group, at=origin["fetchedAt"])[0]["text"], documents[0]["text"])
        self.assertEqual(source["fetchedAt"], "2026-10-24T18:30:00.677520Z")

    def test_missing_attestation_preserves_exact_final_identity(self):
        group = copy.deepcopy(self.group)
        del group["sources"][0]["transportAttestation"]
        with self.assertRaisesRegex(ValueError, "observation URL differs"): self.validate(group)

    def test_neighbor_url_spellings_never_pass(self):
        for key in ("requestedUrl", "finalUrl"):
            base = S1_TRANSPORT[key]
            urls = [base.replace("https:", "http:"), base.replace("www.sec.gov", "sec.gov"),
                    base.replace("www.sec.gov", "www.sec.gov.evil.invalid"), base.replace("www.sec.gov", "www.sec.gov:443"),
                    base.replace("www.sec.gov", "WWW.SEC.GOV"), base.replace("/data/", "/data/../data/"),
                    base.replace("1583708/", "1583709/"), base.replace("26000039/", "26000040/"),
                    base.replace("s-20260528.htm", "s-20260529.htm"), base + "?x=1", base + "#filing",
                    base.replace("s-20260528", "%73-20260528"), S1_TRANSPORT["finalUrl" if key == "requestedUrl" else "requestedUrl"]]
            for url in urls:
                with self.subTest(key=key, url=url):
                    with self.assertRaisesRegex(ValueError, "URL differs"):
                        self.validate(store=self.overlay(**{key: url}))

    def test_observation_body_id_source_time_status_and_reuse_joins(self):
        mutations = [{"observationId": "0" * 64}, {"sourceId": "s1:other"}, {"body": {**S1_TRANSPORT["body"], "bytes": 49403}},
                     {"fetchedAt": "2026-10-24T18:30:01Z"}, {"verifiedAt": "2026-10-25T00:00:00Z"},
                     {"status": "fetched"}, {"httpStatus": 200}, {"transportReused": True},
                     {"reusesObservationId": self.group["sources"][0]["observationId"]},
                     {"reusesObservationId": "0" * 64}, {"reusesObservationId": None}]
        for changes in mutations:
            with self.subTest(changes=changes):
                with self.assertRaises(ValueError): self.validate(store=self.overlay(**changes))
        # An earlier reused record must retain its own exact identity and clock, too.
        original = self.store
        latest = original.read("observations/" + self.group["sources"][0]["observationId"] + ".json")
        for changes in ({"sourceId": "another"}, {"finalUrl": S1_TRANSPORT["requestedUrl"]},
                        {"fetchedAt": "2026-10-25T00:00:00Z"}, {"body": {**S1_TRANSPORT["body"], "bytes": 1}}):
            class Overlay:
                get = original.get
                def read(self, key):
                    row = original.read(key)
                    if key == "observations/" + latest["reusesObservationId"] + ".json": row.update(changes)
                    return row
            with self.subTest(prior=changes):
                with self.assertRaises(ValueError): self.validate(store=Overlay())

    def test_freshness_complete_body_literal_excerpt_and_size_guards_remain(self):
        for delta in (-1, 30 * 3600 + 1):
            at = (instant(self.at) + timedelta(seconds=delta)).isoformat().replace("+00:00", "Z")
            with self.assertRaisesRegex(ValueError, "expired or future"): self.validate(at=at)
        market = copy.deepcopy(self.market)
        market["model"]["maxDocumentChars"] = 100
        with self.assertRaisesRegex(ValueError, "exceeds limit"): self.validate(market=market)
        group = copy.deepcopy(self.group)
        next(t for t in group["targets"] if t["targetId"].startswith("evidence:"))["proposedValue"]["excerpt"] = "Invented excerpt."
        with self.assertRaisesRegex(ValueError, "not literally"): self.validate(group)
        original = self.store
        class CorruptedBody:
            read = original.read
            def get(self, reference): return original.get(reference) + b"x"
        with self.assertRaisesRegex(ValueError, "transport body differs"): self.validate(store=CorruptedBody())

    def test_all_six_actual_admissions_and_policy_hashes_replay_unchanged(self):
        stamp = read(ROOT / "web/src/data/tracker/factualCorrectionPolicy.json")
        self.assertEqual(len(self.requests["groups"]), 6)
        for group in self.requests["groups"]:
            policy = group_review_policy(group, self.market, self.baseline)
            self.assertEqual(policy, stamp["reviewPolicySha256ByGroup"][group["id"]])
            accepted = self.store.read(_index(group, policy))
            self.assertIsNotNone(accepted)
            reference = accepted["admission"]
            before = self.store.get(reference)
            admission = replay_admission(group, reference, self.store, self.market, policy, "2026-10-25T02:00:00Z")
            self.assertEqual(digest(admission), digest(json.loads(before)))
            self.assertEqual(self.store.get(reference), before)


if __name__ == "__main__":
    unittest.main()
