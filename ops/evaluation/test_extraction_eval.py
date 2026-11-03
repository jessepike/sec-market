import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import extraction_eval as ev  # noqa: E402

GOLDEN = Path(__file__).resolve().parent / "golden/extraction"


def pred(case, **over):
    base = {"supplierId": case["supplierId"], "predicate": "funding", "valueText": "x", "quote": "x", "effectiveDate": "2026-06-10",
            "amount": "600000000", "currency": "USD", "qualifier": "exact", "eventStatus": "announced", "scope": "company"}
    base.update(over)
    return base


def make_golden(root):
    cases = {
        "pos": {"id": "pos", "url": "https://example.com/a", "capturedAt": "2026-11-03", "supplierId": "s1", "supplierName": "S1", "kind": "positive", "notes": "",
                "expectedFacts": [{"predicate": "funding", "effectiveDate": "2026-06-10", "amount": "600000000", "currency": "USD", "eventStatus": "announced"}]},
        "neg": {"id": "neg", "url": "https://example.com/b", "capturedAt": "2026-11-03", "supplierId": "s1", "supplierName": "S1", "kind": "negative", "notes": "", "expectedFacts": []},
    }
    for cid, case in cases.items():
        (root / cid).mkdir()
        (root / cid / "case.json").write_text(json.dumps(case))
        (root / cid / "page.html").write_text("<html></html>")
    return cases


class ScorerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.cases = make_golden(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def run_score(self, pos, neg=()):
        return ev.score(self.root, {"cases": {"pos": {"facts": list(pos), "error": None}, "neg": {"facts": list(neg), "error": None}}})

    def test_perfect(self):
        r = self.run_score([pred(self.cases["pos"])])
        o = r["overall"]
        self.assertEqual((o["precision"], o["recall"], o["dateAccuracy"], o["typeAccuracy"]), (1.0, 1.0, 1.0, 1.0))
        self.assertEqual(r["negativePages"]["falsePositiveRate"], 0.0)

    def test_missed_fact(self):
        r = self.run_score([])
        self.assertEqual(r["overall"]["recall"], 0.0)
        self.assertEqual(len(r["cases"]["pos"]["missed"]), 1)

    def test_wrong_date_outside_window_is_miss_and_false_positive(self):
        r = self.run_score([pred(self.cases["pos"], effectiveDate="2026-06-20")])
        self.assertEqual((r["overall"]["truePositives"], r["overall"]["misses"], r["overall"]["falsePositives"]), (0, 1, 1))

    def test_near_date_matches_but_is_not_exact(self):
        r = self.run_score([pred(self.cases["pos"], effectiveDate="2026-06-12")])
        self.assertEqual(r["overall"]["recall"], 1.0)
        self.assertEqual(r["overall"]["dateAccuracy"], 0.0)

    def test_amount_tolerance_and_mismatch(self):
        self.assertEqual(self.run_score([pred(self.cases["pos"], amount="604000000")])["overall"]["recall"], 1.0)
        self.assertEqual(self.run_score([pred(self.cases["pos"], amount="700000000")])["overall"]["recall"], 0.0)

    def test_wrong_status_lowers_type_accuracy(self):
        r = self.run_score([pred(self.cases["pos"], eventStatus="closed")])
        self.assertEqual(r["overall"]["typeAccuracy"], 0.0)

    def test_false_positive_on_negative_page(self):
        r = self.run_score([pred(self.cases["pos"])], [pred(self.cases["neg"])])
        self.assertEqual(r["negativePages"]["falsePositiveRate"], 1.0)
        self.assertEqual(r["overall"]["falsePositives"], 1)

    def test_duplicate_statement_is_not_false_positive(self):
        r = self.run_score([pred(self.cases["pos"]), pred(self.cases["pos"], valueText="again")])
        self.assertEqual(r["overall"]["falsePositives"], 0)
        self.assertEqual(len(r["cases"]["pos"]["duplicates"]), 1)

    def test_errored_case_is_unscored(self):
        r = ev.score(self.root, {"cases": {"pos": {"facts": None, "error": "X"}, "neg": {"facts": [], "error": None}}})
        self.assertEqual([u["id"] for u in r["unscoredCases"]], ["pos"])

    def test_cli_refuses_overwrite_and_writes_both_reports(self):
        preds = self.root.parent / (self.root.name + "-preds.json")
        preds.write_text(json.dumps({"cases": {"pos": {"facts": [pred(self.cases["pos"])], "error": None}, "neg": {"facts": [], "error": None}}}))
        self.addCleanup(preds.unlink)
        with tempfile.TemporaryDirectory() as out:
            target = Path(out) / "report.json"
            self.assertEqual(ev.main(["score", "--golden", str(self.root), "--predictions", str(preds), "--output", str(target)]), 0)
            self.assertTrue(target.exists() and target.with_suffix(".md").exists())
            with self.assertRaises(SystemExit):
                ev.main(["score", "--golden", str(self.root), "--predictions", str(preds), "--output", str(target)])


class GoldenSetTests(unittest.TestCase):
    def test_every_case_is_valid(self):
        cases = ev.load_golden(GOLDEN)
        self.assertGreaterEqual(len(cases), 25)
        ids = [c["id"] for c in cases]
        self.assertEqual(len(ids), len(set(ids)))
        contract = json.loads((ev.REPO / "contracts/market.json").read_text())
        suppliers = {s["id"] for s in contract["suppliers"]}
        for case in cases:
            with self.subTest(case=case["id"]):
                self.assertEqual(case["_dir"].name, case["id"])
                self.assertEqual(ev.validate_case(case), [])
                self.assertIn(case["supplierId"], suppliers)
                self.assertTrue((case["_dir"] / "page.html").stat().st_size > 0)

    def test_validator_rejects_bad_predicate(self):
        bad = {"id": "x", "url": "https://e.com", "capturedAt": "2026-11-03", "supplierId": "s", "supplierName": "S", "kind": "positive", "notes": "",
               "expectedFacts": [{"predicate": "divestiture", "effectiveDate": "2026-01-01", "amount": None, "currency": None, "eventStatus": None}]}
        self.assertTrue(any("FACT_SCHEMA" in p for p in ev.validate_case(bad)))

    def test_mix_of_positive_and_negative(self):
        kinds = [c["kind"] for c in ev.load_golden(GOLDEN)]
        self.assertGreaterEqual(kinds.count("positive"), 15)
        self.assertGreaterEqual(kinds.count("negative"), 8)


if __name__ == "__main__":
    unittest.main()
