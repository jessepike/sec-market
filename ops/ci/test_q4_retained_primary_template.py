"""Offline exact retained samples. No requests, frozen writes or source authority."""
import copy
import json
from pathlib import Path
import socket
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "web/scripts/pipeline"), str(ROOT / "ops/ci")]
from contracts import canonical, digest
from storage import LocalStore
import q4_retained_primary_template as operation
from onboarding import _candidate_primary_shape

ARCHIVE = Path("/var/tmp/smp-q4-primary-actual-40188161705-20261025/extracted")
DESCRIPTOR = ROOT / "docs/active/daily-pipeline/accuracy/q4-retained-primary-template-descriptor-2026-10-25.json"


class ReadOnlyActual:
    def __init__(self):
        raw = (ARCHIVE / "archive-manifest.json").read_bytes()
        assert digest(raw) == "bb1c3da1399e89341badf80bba8642d7892f32ce2030bd57fc1d4c165e383e4d"
        self.entries = {r["key"]: r for r in json.loads(raw)["files"]}
        self.touched = {}
    def raw(self, key):
        path = ARCHIVE / "state" / key
        entry = self.entries.get("state/" + key)
        if entry is None:
            assert not path.exists()
            return None
        raw = path.read_bytes()
        assert digest(raw) == entry["sha256"] and len(raw) == entry["bytes"]
        self.touched[str(path)] = (digest(raw), len(raw), path.stat().st_mtime_ns)
        return raw
    def read(self, key):
        raw = self.raw(key)
        return json.loads(raw) if raw is not None else None
    def get(self, ref):
        raw = self.raw(ref["key"])
        assert digest(raw) == ref["sha256"] and len(raw) == ref["bytes"]
        return raw
    def unchanged(self, case):
        for name, before in self.touched.items():
            p = Path(name)
            raw = p.read_bytes()
            case.assertEqual((digest(raw), len(raw), p.stat().st_mtime_ns), before)


class ClosedDescriptorTests(unittest.TestCase):
    def setUp(self):
        self.contract = json.loads((ROOT / "contracts/html-qualification-seeds/8b44bcbec679c178836408c4d98c7230a85572784b0257ef21d21d3b03b445db/contracts__8b44bcbec679c178836408c4d98c7230a85572784b0257ef21d21d3b03b445db.json").read_bytes())
        self.raw = DESCRIPTOR.read_bytes()
        self.descriptor = json.loads(self.raw)
    def test_every_descriptor_field_substitution_rejects_before_any_store_read(self):
        class NoRead:
            def get(self, *_): raise AssertionError("Descriptor rejected before store access")
        def paths(value, path=()):
            if isinstance(value, dict):
                for key, child in value.items():
                    yield from paths(child, (*path, key))
            elif isinstance(value, list):
                for index, child in enumerate(value):
                    yield from paths(child, (*path, index))
            else: yield path
        for path in paths(self.descriptor):
            changed = copy.deepcopy(self.descriptor)
            parent = changed
            for key in path[:-1]: parent = parent[key]
            parent[path[-1]] = "substituted"
            with self.subTest(path=path), self.assertRaises(ValueError):
                operation.derive_report(self.contract, NoRead(), canonical(changed))
    def test_missing_extra_reordered_and_wrong_policy_reject(self):
        changes = []
        for key in self.descriptor:
            changed = copy.deepcopy(self.descriptor); del changed[key]; changes.append(changed)
        changed = copy.deepcopy(self.descriptor); changed["extra"] = 1; changes.append(changed)
        changed = copy.deepcopy(self.descriptor); changed["sources"].reverse(); changes.append(changed)
        for changed in changes:
            with self.subTest(changed=changed), self.assertRaises(ValueError):
                operation.derive_report(self.contract, object(), canonical(changed))
        changed = copy.deepcopy(self.contract); changed["version"] += "-different"
        with self.assertRaises(ValueError): operation.derive_report(changed, object(), self.raw)
    def test_nonstandard_duplicate_empty_and_nonbyte_descriptor_reject(self):
        for raw in (b"{}", b"[]", b"", "not bytes", b"{", b"{\"kind\":NaN}",
                    b"{\"kind\":Infinity}", b"{\"kind\":-Infinity}", b"{\"kind\":1,\"kind\":2}"):
            with self.subTest(raw=raw), self.assertRaises((ValueError, TypeError)):
                operation.derive_report(self.contract, object(), raw)


@unittest.skipUnless(ARCHIVE.exists(), "Retained actual archive is available only in the offline evidence VM")
class ActualProofTests(unittest.TestCase):
    def setUp(self):
        self.store = ReadOnlyActual()
        self.raw = DESCRIPTOR.read_bytes()
        self.descriptor = json.loads(self.raw)
        self.contract = json.loads((ROOT / "contracts/html-qualification-seeds/8b44bcbec679c178836408c4d98c7230a85572784b0257ef21d21d3b03b445db/contracts__8b44bcbec679c178836408c4d98c7230a85572784b0257ef21d21d3b03b445db.json").read_bytes())
        self.network = patch.object(socket.socket, "connect", side_effect=AssertionError("NO_NETWORK"))
        self.local = patch.object(LocalStore, "__init__", side_effect=AssertionError("NO_FROZEN_LOCALSTORE"))
        self.network.start(); self.local.start()
        self.addCleanup(self.network.stop); self.addCleanup(self.local.stop)
        self.addCleanup(self.store.unchanged, self)
    def derive(self): return operation.derive_report(self.contract, self.store, self.raw)
    def test_actual_both_samples_replay_original_hold_and_complete_graph_without_credit(self):
        report = self.derive()
        self.assertTrue(operation.verify_report(self.contract, self.store, self.raw, report)["proposalEvidenceComplete"])
        self.assertEqual(report["originalReportAcceptedSamples"], 0)
        self.assertFalse(report["originalReportProposalEvidenceComplete"])
        self.assertEqual([(s["records"], s["currentWindowRecords"]) for s in report["streams"]], [(206, 3), (323, 4)])
        for key in ("qualified", "semanticAdmission", "coverageCredit", "operationalIntake"): self.assertIs(report[key], False)
        for key in ("qualifiedSources", "sourceChecksCredited", "modelCalls"): self.assertEqual(report[key], 0)
        self.assertEqual(report["facts"], [])
    def test_actual_identity_headings_and_supplied_metadata_remain_literal(self):
        shapes = [s["primaryShape"] for s in self.derive()["retainedSamples"]]
        for shape in shapes:
            self.assertIsNone(shape["canonical"])
            self.assertEqual(shape["identityProof"], "source_bound_response_and_og_url")
            self.assertEqual(shape["genericH1"], "News Details")
            self.assertEqual(shape["displayedCalendarDay"], "2026-10-14")
            self.assertEqual(shape["indexDateLiteral"], "10/14/2026 16:05:00")
            self.assertIsNone(shape["indexTimezone"])
            self.assertGreater(shape["readableCharacters"], 100)
        self.assertEqual(shapes[0]["jsonLdIdentity"][0]["datePublished"], "2026-10-14T15:05:00Z")
        self.assertEqual(shapes[0]["jsonLdIdentity"][0]["dateModified"], "2026-10-14T15:05:00Z")
        self.assertEqual(shapes[1]["dateMetadataState"], "unknown")
        self.assertEqual(shapes[1]["dateMetadata"], [])
    def test_generic_primary_helper_and_original_accepted_zero_are_unchanged(self):
        self.derive()
        record = self.store.read(self.descriptor["actualProof"]["record"]["key"])
        self.assertEqual(record["diagnostic"]["acceptedSamples"], 0)
        for row in self.descriptor["sources"]:
            with self.assertRaisesRegex(ValueError, "BOUNDED_CANDIDATE_PRIMARY_CANONICAL_DIFFERS"):
                _candidate_primary_shape(self.store.get(row["body"]), row["url"])
    def test_original_report_replay_is_required_before_template_extraction(self):
        with patch.object(operation.primary, "verify_report", side_effect=ValueError("ORIGINAL_PROOF_FAILED")), \
             patch.object(operation, "_shape", side_effect=AssertionError("Must not extract before original replay")):
            with self.assertRaisesRegex(ValueError, "ORIGINAL_PROOF_FAILED"): self.derive()
    def test_actual_audit_identity_is_required(self):
        with patch.object(operation, "REPO", Path("/nonexistent-retained-audit")):
            with self.assertRaises(FileNotFoundError): self.derive()
    def test_one_source_failure_cannot_return_complete_proposal(self):
        real = operation._shape
        calls = []
        def shape(body, row, target):
            calls.append(row["sourceId"])
            if len(calls) == 2: raise ValueError("SECOND_SAMPLE_HELD")
            return real(body, row, target)
        with patch.object(operation, "_shape", side_effect=shape):
            with self.assertRaisesRegex(ValueError, "SECOND_SAMPLE_HELD"): self.derive()
        self.assertEqual(len(calls), 2)
    def test_every_report_field_and_nested_finding_tampering_rejects(self):
        report = self.derive()
        for key in report:
            changed = copy.deepcopy(report); changed[key] = None
            with self.subTest(field=key), self.assertRaises(ValueError):
                operation.verify_report(self.contract, self.store, self.raw, changed)
        for index in range(2):
            for key in report["retainedSamples"][index]["primaryShape"]:
                changed = copy.deepcopy(report); changed["retainedSamples"][index]["primaryShape"][key] = "forged"
                with self.subTest(index=index, key=key), self.assertRaises(ValueError):
                    operation.verify_report(self.contract, self.store, self.raw, changed)
    def test_all_original_identity_clock_plan_and_html_substitutions_fail_at_pins(self):
        old_get = self.store.get
        keys = [self.descriptor["actualProof"]["record"]["key"], self.descriptor["actualProof"]["plan"]["key"]]
        for row in self.descriptor["sources"]: keys.extend(row[key]["key"] for key in ("observation", "rawObservation", "body"))
        for key in keys:
            def altered(ref, chosen=key):
                raw = old_get(ref)
                return raw + b" " if ref["key"] == chosen else raw
            with self.subTest(key=key), patch.object(self.store, "get", side_effect=altered), self.assertRaises(ValueError):
                self.derive()
    def test_malformed_conflicting_decoy_and_hidden_html_cannot_replace_exact_bodies(self):
        original_get = self.store.get
        for row in self.descriptor["sources"]:
            for fragment in (b"<h3>Decoy</h3>", b"<base href=\"https://foreign.invalid/\">", b"<template/>",
                             b"<script type=\"application/ld+json\">{\"@type\":\"NewsArticle\",\"datePublished\":\"tomorrow\"}</script>",
                             b"<time datetime=\"\"></time>", b"<div hidden>Different headline</div>"):
                def altered(ref, chosen=row["body"]["key"], extra=fragment):
                    raw = original_get(ref)
                    return raw + extra if ref["key"] == chosen else raw
                with self.subTest(source=row["sourceId"], fragment=fragment), patch.object(self.store, "get", side_effect=altered), self.assertRaises(ValueError):
                    self.derive()


if __name__ == "__main__": unittest.main()
