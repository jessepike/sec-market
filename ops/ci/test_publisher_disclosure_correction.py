"""Fictional temporary documents and mocked subscription responses, never real admission.

The exact immutable public record is used to exercise the one-record allowlist.
No source request, real model/login, real archive or persistent quota is touched.
"""
import copy
import gzip
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "web/scripts/pipeline"))
import test_correction_admission as fixtures
from agents import (SubscriptionAgent, PUBLISHER_DISCLOSURE_SCOPE, PUBLISHER_DISCLOSURE_CHECKS,
                    PUBLISHER_DISCLOSURE_REVIEW_SCHEMA)
from contracts import canonical, digest
from corrections import (PUBLISHER_OPERATION, PUBLISHER_ORIGINAL_SHA256, PUBLISHER_PROPOSED_SHA256,
                         PUBLISHER_LIMITATIONS, PUBLISHER_QUOTES, group_review_policy, load_policy,
                         process_corrections, project_bundle, replay_admission)
from discovery import Page
from gate import prepare_corrections
from publication import verify_correction_publication
from validation import REVIEW_CHECKS


ROOT = Path(__file__).resolve().parents[2]
DESIGN = ROOT / "docs/active/daily-pipeline/accuracy/source-classification-admission-design-2026-10-23.json"


class PublisherDisclosureCorrectionTests(unittest.TestCase):
    def setUp(self):
        f = self.f = fixtures.CorrectionAdmissionTests()
        f.setUp()
        self.addCleanup(f.doCleanups)
        self.design = json.loads(DESIGN.read_bytes())
        self.original = copy.deepcopy(self.design["records"]["original"])
        self.group = copy.deepcopy(self.design["proposedGroupExample"])
        self.factual_group = f.group
        f.raw["evidence"].append(copy.deepcopy(self.original))
        f.raw["suppliers"].append({"id": "xage", "name": "Xage Security"})
        supplier = copy.deepcopy(self.design["proposedReviewPolicy"]["basis"]["supplier"])
        supplier["sourceIds"] = ["xage:citation:TR-xage-1"]
        f.market["suppliers"].append(supplier)
        f.market["sources"].append(copy.deepcopy(self.design["publisherEvidence"]["configuredSource"]))
        f.requests["groups"] = [self.group]
        self.metadata = {
            "@type": "NewsArticle", "headline": "Fictional publication-role fixture",
            "mainEntityOfPage": {"@id": self.original["canonicalUrl"]},
            "publisher": {"name": "Yahoo! Finance", "alternateName": "Yahoo Finance", "url": "https://finance.yahoo.com/"},
            "provider": {"name": "GlobeNewswire", "url": "https://www.globenewswire.com/"},
            "author": {"name": "Xage Security"}, "creator": {"name": "Xage Security"}}
        self.counter = 0
        self.html = self.document()
        self.set_document(self.html, repin=False)
        f.pins()
        f.runner = Mock(side_effect=self.model_runner)
        f.agent = SubscriptionAgent(f.market["model"], runner=f.runner)

    def document(self):
        return ('<html><head><link rel="canonical" href="' + self.original["canonicalUrl"] + '">'
                '<script type="application/ld+json">' + json.dumps(self.metadata) + '</script></head><body>'
                '<article data-testid="article-content-wrapper"><h1>Fictional publication-role fixture</h1>'
                '<div data-testid="press-release-disclaimer">' + PUBLISHER_QUOTES["publisher_paid_disclosure"] + '</div>'
                '<div class="byline"><div class="byline-attr-author">Xage Security</div>'
                '<time>March 18, 2026</time><span>7 min read</span></div><p>'
                + PUBLISHER_QUOTES["issuer_attributed_dateline"] + '</p>'
                '<p>Fictional test text. This document does not verify any financial claim.</p>'
                '</article></body></html>')

    def set_document(self, html, repin=True, compressed=False):
        f = self.f
        self.counter += 1
        raw = html.encode()
        body = f.store.put(gzip.compress(raw) if compressed else raw)
        source = self.group["sources"][0]
        self.observation = {"sourceId": source["sourceId"], "requestedUrl": source["url"], "finalUrl": source["url"],
                            "body": body, "fetchedAt": "2026-10-23T11:00:00Z", "status": "fetched",
                            "httpStatus": 200, "contentType": "text/html; charset=utf-8"}
        self.observation["observationId"] = digest({"fixture": self.counter, **self.observation})
        f.store.write_once("observations/" + self.observation["observationId"] + ".json", self.observation)
        text = " ".join(" ".join(Page(html, source_url=source["url"]).text).split())
        source.update(body=body, fetchedAt=self.observation["fetchedAt"], observationId=self.observation["observationId"])
        source["visibleText"].update(sha256=digest(text.encode()), chars=len(text))
        for quote in self.group["disclosureQuotes"]:
            start = max(0, text.find(quote["text"]))
            quote.update(normalizedWholePageStart=start, normalizedWholePageEnd=start + len(quote["text"]))
        if repin:
            f.repin()

    def mutate_observation(self, **changes):
        self.observation.update(changes)
        self.f.store._path("observations/" + self.observation["observationId"] + ".json").write_bytes(canonical(self.observation))

    def model_runner(self, args, **kwargs):
        f = self.f
        if args[1:3] == ["login", "status"]:
            return subprocess.CompletedProcess(args, 0, "Logged in using ChatGPT", "")
        f.prompts.append(kwargs["input"])
        if f.fail:
            raise f.fail
        scoped = "UNTRUSTED PUBLISHER DISCLOSURE CORRECTION AND EVIDENCE:\n" in kwargs["input"]
        marker = ("UNTRUSTED PUBLISHER DISCLOSURE CORRECTION AND EVIDENCE:\n" if scoped
                  else "UNTRUSTED CORRECTION AND PRIMARY EVIDENCE:\n")
        payload = json.loads(kwargs["input"].split(marker)[1])
        checks = PUBLISHER_DISCLOSURE_CHECKS if scoped else REVIEW_CHECKS
        response = {key: payload[key] for key in ("candidateSha256", "evidenceSetSha256", "policySha256")}
        response.update(result="accepted", checks={key: "pass" for key in checks})
        if scoped:
            response["reviewScope"] = PUBLISHER_DISCLOSURE_SCOPE
        response = f.response_transform(response)
        Path(args[args.index("--output-last-message") + 1]).write_text(json.dumps(response))
        return subprocess.CompletedProcess(args, 0, "", "")

    def assert_held_before_charge(self, reason=None):
        try:
            result = self.f.process()
        except ValueError as exc:
            if reason:
                self.assertIn(reason, str(exc))
        else:
            self.assertFalse(result["admitted"])
            self.assertTrue(result["pending"])
            if reason:
                self.assertIn(reason, result["pending"][0]["reason"])
        self.assertFalse(self.f.charges)
        self.assertFalse(self.f.prompts)

    def test_exact_scoped_policy_matches_reviewed_basis(self):
        basis = copy.deepcopy(self.design["proposedReviewPolicy"]["basis"])
        basis.update(candidateSha256=digest(self.group), baselineSha256=self.f.requests["baseline"]["sha256"])
        self.assertEqual(group_review_policy(self.group, self.f.market, self.f.requests["baseline"]["sha256"]), digest(basis))
        self.assertEqual(digest(self.original), PUBLISHER_ORIGINAL_SHA256)
        self.assertEqual(digest(self.group["targets"][0]["proposedValue"]), PUBLISHER_PROPOSED_SHA256)

    def test_historical_baseline_and_exact_three_field_amendment_preserve_accepted_groups(self):
        requests = json.loads((ROOT / "contracts/factual-corrections.json").read_bytes())
        market = json.loads((ROOT / "contracts/market.json").read_bytes())
        repair = json.loads((ROOT / "docs/active/daily-pipeline/accuracy/failed-correction-review-repair-spec-2026-10-24.json").read_bytes())
        permitted = {"FC-20261023-checkpoint-sase": {"noteTemplate", "reasonCode"},
                     "FC-20261023-zscaler": {"noteTemplate"}}
        self.assertEqual(set(repair["changedFields"]), {gid + "." + field for gid, fields in permitted.items() for field in fields})
        self.assertEqual(len(repair["changedFields"]), 3)
        self.assertEqual(len(repair["diagnosis"]), 2)
        self.assertEqual({item["groupId"] for item in repair["diagnosis"]}, set(permitted))
        expected = self.design["proposedImplementation"]["inventoryPolicy"]
        groups = {g["id"]: g for g in requests["groups"]}
        historical = copy.deepcopy(requests)
        historical_groups = {g["id"]: g for g in historical["groups"]}
        for item in repair["diagnosis"]:
            gid = item["groupId"]
            self.assertEqual(set(item["proposedChanges"]), permitted[gid])
            self.assertEqual(digest(groups[gid]), item["proposedCandidateSha256"])
            self.assertEqual(group_review_policy(groups[gid], market, requests["baseline"]["sha256"]), item["proposedReviewPolicySha256"])
            self.assertEqual(digest(groups[gid]["sources"]), item["evidenceSetSha256"])
            self.assertEqual(digest(groups[gid]["targets"]), item["targetSetSha256"])
            for field, values in item["proposedChanges"].items():
                self.assertEqual(groups[gid][field], values["new"])
                self.assertNotEqual(values["old"], values["new"])
                historical_groups[gid][field] = values["old"]
        for gid, sha in expected["existingGroupCandidateSha256ById"].items():
            self.assertEqual(digest(historical_groups[gid]), sha)
            self.assertEqual(group_review_policy(historical_groups[gid], market, requests["baseline"]["sha256"]),
                             expected["existingReviewPoliciesUnchanged"][gid])
        self.assertEqual(digest(historical), repair["oldRequestsCanonicalSha256"])
        accepted = repair["preservedAcceptedAdmissions"]
        self.assertEqual({item["groupId"] for item in accepted}, {"FC-20261023-optiv", "FC-20261023-splunk", "FC-20261023-expel", "XAGE-SOURCE-CLASS-20261023"})
        self.assertEqual(len(accepted), 4)
        for item in accepted:
            group = groups[item["groupId"]]
            self.assertEqual(digest(group), item["candidateSha256"])
            self.assertEqual(digest(group["sources"]), item["evidenceSetSha256"])
            self.assertEqual(group_review_policy(group, market, requests["baseline"]["sha256"]), item["reviewPolicySha256"])
        historical_market = json.loads((ROOT / 'docs/active/daily-pipeline/evaluations/2026-10-24/operational-inputs/contract.json').read_text())
        self.assertEqual(digest({'marketSha256': digest(historical_market), 'requestsSha256': digest(requests),
                                 'baselineSha256': requests['baseline']['sha256']}), repair['proposedGlobalPolicySha256'])
        self.assertEqual(load_policy(ROOT, market)['policySha256'], digest({'marketSha256': digest(market),
                         'requestsSha256': digest(requests), 'baselineSha256': requests['baseline']['sha256']}))

    def test_same_gate_seal_publication_date_and_history_flow_carries_the_scope(self):
        f = self.f
        (f.repo / "web/src/data/generated").mkdir(parents=True)
        outcome = f.process()
        collection = {"runId": "fictional-role-run", "checkedAt": f.now, **outcome}
        f.store.compare_and_swap("correction-collection", None,
                                 {"runId": collection["runId"], "outcome": f.store.put(collection)})
        seal = prepare_corrections(f.repo, f.store, f.market, {"runId": collection["runId"]}, now=f.now)
        path = f.repo / "web/src/data/generated/factualCorrections.json"
        first = json.loads(path.read_bytes())
        self.assertEqual(first["groups"][0]["reviewScope"], PUBLISHER_DISCLOSURE_SCOPE)
        self.assertEqual(first["groups"][0]["admission"]["reviewScope"], PUBLISHER_DISCLOSURE_SCOPE)
        self.assertEqual(seal["fileSha256"], digest(path.read_bytes()))
        self.assertEqual(seal["targetIds"], ["evidence:TR-xage-1"])
        self.assertEqual(json.loads(path.with_suffix(".seal.json").read_bytes()), seal)
        with self.assertRaisesRegex(ValueError, "ROLLED_OVER"):
            verify_correction_publication(seal, "2026-10-24T00:00:00Z")
        later = prepare_corrections(f.repo, f.store, f.market, {"runId": collection["runId"]},
                                    previous_bundle=first, now="2026-12-23T12:00:00Z")
        self.assertEqual(later["newGroupIds"], [])
        self.assertEqual(json.loads(path.read_bytes())["groups"], first["groups"])
        self.assertEqual(f.agent.calls, 1)

    def test_scoped_review_prompt_admission_projection_and_zero_call_historical_replay(self):
        f = self.f
        original_raw = copy.deepcopy(f.raw)
        result = f.process()
        self.assertFalse(result["pending"])
        bundle = f.project(result)
        row = bundle["groups"][0]
        self.assertEqual(row["reviewScope"], PUBLISHER_DISCLOSURE_SCOPE)
        self.assertEqual(row["admission"]["reviewScope"], PUBLISHER_DISCLOSURE_SCOPE)
        self.assertEqual(row["targets"][0]["proposedValue"]["sourceClass"], "OFFICIAL")
        self.assertEqual(row["targets"][0]["proposedValue"]["excerpt"], self.original["excerpt"])
        self.assertEqual(f.charges, [("documents", 40), ("calls", 80)])
        self.assertIn("does not verify", f.prompts[0])
        self.assertIn("publication role only", f.prompts[0])
        schema = PUBLISHER_DISCLOSURE_REVIEW_SCHEMA
        self.assertEqual(set(schema["properties"]["checks"]["required"]), PUBLISHER_DISCLOSURE_CHECKS)
        admission = json.loads(f.store.get(result["admitted"][0]["admission"]))
        self.assertEqual(admission["reviewScope"], PUBLISHER_DISCLOSURE_SCOPE)
        later = f.process(now="2026-12-23T12:00:00Z")
        self.assertFalse(later["pending"])
        self.assertFalse(later["attempts"])
        self.assertEqual(f.project(later, bundle, "2026-12-23T12:00:00Z")["groups"], bundle["groups"])
        self.assertEqual(f.charges, [("documents", 40), ("calls", 80)])
        self.assertEqual(f.raw, original_raw)

    def test_group_scope_unknown_missing_and_mixed_targets_fail(self):
        for mode in ["unknown", "missing", "mixed"]:
            with self.subTest(mode=mode):
                saved = copy.deepcopy(self.group)
                if mode == "unknown":
                    self.group["reviewScope"] = "financial_primary"
                elif mode == "missing":
                    self.group.pop("reviewScope")
                else:
                    self.group["targets"].append(copy.deepcopy(self.factual_group["targets"][0]))
                self.f.repin() if mode != "unknown" else self.f.write("contracts/factual-corrections.json", self.f.requests)
                self.assert_held_before_charge()
                self.group.clear(); self.group.update(saved)

    def test_exact_target_and_protected_metadata_cannot_drift(self):
        target = self.group["targets"][0]
        for key, value in [("organization", "Xage Security"), ("canonicalUrl", "https://example.invalid/"),
                           ("excerpt", "New financial claim"), ("retrievedAt", "2026-10-23"),
                           ("id", "TR-other"), ("sourceClass", "IR"), ("limitations", "Financial claims now verified.")]:
            before = copy.deepcopy(target["proposedValue"])
            with self.subTest(key=key):
                target["proposedValue"][key] = value
                self.f.repin()
                self.assert_held_before_charge()
            target["proposedValue"] = before
        target["targetId"] = "evidence:E"
        self.f.repin()
        self.assert_held_before_charge()

    def test_a_rewritten_baseline_cannot_authorize_another_original(self):
        self.f.raw["evidence"][-1]["organization"] = "Some Other Publisher"
        target = self.group["targets"][0]
        target["original"] = copy.deepcopy(self.f.raw["evidence"][-1])
        target["originalSha256"] = digest(target["original"])
        self.f.pins()
        self.assert_held_before_charge("immutable original differs")

    def test_source_requires_exact_verified_supplier_citation_and_proof_scope(self):
        source = self.f.market["sources"][-1]
        for changes in [{"registration": "candidate"}, {"kind": "html_index"}, {"supplierId": "example"},
                        {"family": "independent_reporting"}, {"evidenceId": "E"}]:
            saved = copy.deepcopy(source)
            with self.subTest(changes=changes):
                source.update(changes); self.f.repin(); self.assert_held_before_charge()
            source.clear(); source.update(saved)
        self.group["sources"][0]["proofScope"] = "financial_primary"
        self.f.repin()
        self.assert_held_before_charge()

    def test_notice_byline_and_dateline_must_belong_to_one_article(self):
        paid = '<div data-testid="press-release-disclaimer">' + PUBLISHER_QUOTES["publisher_paid_disclosure"] + '</div>'
        byline = '<div class="byline-attr-author">Xage Security</div>'
        variants = [self.html.replace(paid, "").replace("</article>", "</article><aside>" + paid + "</aside>"),
                    self.html.replace(byline, "").replace("</article>", "</article><aside>" + byline + "</aside>"),
                    self.html.replace(PUBLISHER_QUOTES["issuer_attributed_dateline"], "")
                             .replace("</article>", "</article><aside>" + PUBLISHER_QUOTES["issuer_attributed_dateline"] + "</aside>"),
                    self.html.replace("</body>", '<article data-testid="article-content-wrapper">Other article</article></body>')]
        for html in variants:
            with self.subTest(html=html[-150:]):
                self.set_document(html); self.assert_held_before_charge()

    def test_script_disclosure_and_unclosed_article_do_not_count(self):
        paid = PUBLISHER_QUOTES["publisher_paid_disclosure"]
        for html in [self.html.replace(paid, "<script>" + paid + "</script>"), self.html.replace("</article>", "")]:
            self.set_document(html)
            self.assert_held_before_charge()

    def test_canonical_and_article_metadata_must_match_publisher_issuer_provider(self):
        variants = [self.html.replace('rel="canonical"', 'rel="alternate"'),
                    self.html.replace('https://www.globenewswire.com/', 'https://example.invalid/'),
                    self.html.replace('"alternateName": "Yahoo Finance"', '"alternateName": "Other"'),
                    self.html.replace('"creator": {"name": "Xage Security"}', '"creator": {"name": "Other"}'),
                    self.html.replace('"headline": "Fictional publication-role fixture"', '"headline": "Wrong article"'),
                    self.html.replace('<script type="application/ld+json">', '<script type="application/ld+json">')
                             .replace('</head>', '<script type="application/ld+json">{}</script></head>')]
        for html in variants:
            self.set_document(html)
            self.assert_held_before_charge()

    def test_quote_and_whole_text_hashes_are_replayed_before_charge(self):
        source = self.group["sources"][0]
        for location, key, value in [(source["visibleText"], "sha256", "0" * 64),
                                     (source["visibleText"], "chars", source["visibleText"]["chars"] + 1),
                                     (self.group["disclosureQuotes"][0], "normalizedWholePageStart", 0),
                                     (self.group["disclosureQuotes"][0], "literalInUniqueArticle", False)]:
            old = location[key]
            location[key] = value
            if key == "normalizedWholePageStart":
                self.group["disclosureQuotes"][0]["normalizedWholePageEnd"] = len(PUBLISHER_QUOTES["publisher_paid_disclosure"])
            self.f.repin(); self.assert_held_before_charge(); location[key] = old
            if key == "normalizedWholePageStart":
                self.group["disclosureQuotes"][0]["normalizedWholePageEnd"] = old + len(PUBLISHER_QUOTES["publisher_paid_disclosure"])

    def test_observation_url_body_time_status_and_age_cannot_drift(self):
        good = copy.deepcopy(self.observation)
        for changes in [{"requestedUrl": "https://example.invalid/"}, {"finalUrl": "https://example.invalid/"},
                        {"body": self.f.store.put(b"Other body")}, {"fetchedAt": "2026-10-23T10:59:00Z"},
                        {"sourceId": "other"}, {"httpStatus": 403}, {"verifiedAt": "2026-10-24T00:00:00Z"}]:
            self.observation = copy.deepcopy(good)
            self.mutate_observation(**changes)
            self.assert_held_before_charge()
        self.observation = good; self.mutate_observation()
        outcome = self.f.process(now="2026-10-25T00:00:00Z")
        self.assertIn("expired", outcome["pending"][0]["reason"])
        self.assertFalse(self.f.charges)

    def test_complete_text_cap_and_aggregate_model_cap_precede_reservations(self):
        self.set_document(self.html.replace("</article>", "x" * 30000 + "</article>"))
        self.assert_held_before_charge("limit")
        with self.assertRaisesRegex(ValueError, "document set exceeds"):
            self.f.agent.review_publisher_disclosure([{"text": "x" * 16000}, {"text": "y" * 16000}], self.group, "a" * 64)
        self.f.runner.assert_not_called()

    def test_compressed_body_keeps_exact_original_object_and_complete_decoded_text(self):
        self.set_document(self.html, compressed=True)
        result = self.f.process()
        self.assertFalse(result["pending"])
        admission = json.loads(self.f.store.get(result["admitted"][0]["admission"]))
        self.assertEqual(admission["sources"], self.group["sources"])
        self.assertEqual(self.f.store.get(admission["sources"][0]["body"])[:2], b"\x1f\x8b")

    def test_review_scope_hashes_and_role_checks_cannot_be_substituted(self):
        for key, value in [("reviewScope", "financial_primary"), ("candidateSha256", "0" * 64),
                           ("evidenceSetSha256", "0" * 64), ("policySha256", self.f.policy),
                           ("checks", {key: "pass" for key in REVIEW_CHECKS}), ("result", "ambiguous")]:
            self.f.response_transform = lambda response: {**response, key: value}
            result = self.f.process()
            self.assertFalse(result["admitted"])
            self.assertTrue(result["pending"])
            self.assertIsNotNone(json.loads(self.f.store.get(result["attempts"][0]))["review"])
        self.assertEqual(self.f.charges.count(("documents", 40)), 1)
        self.assertEqual(self.f.charges.count(("calls", 80)), 6)

    def test_missing_scope_and_extra_response_keys_fail_strict_review_schema(self):
        for transform in [lambda r: {k: v for k, v in r.items() if k != "reviewScope"}, lambda r: {**r, "financiallyCertified": True}]:
            self.f.response_transform = transform
            self.assertTrue(self.f.process()["pending"])
        self.assertEqual(self.f.charges.count(("calls", 80)), 2)

    def test_completion_expiry_and_cancellation_preserve_charge_without_cache(self):
        cancelled = [False]
        def respond(value):
            cancelled[0] = True
            return value
        self.f.response_transform = respond
        result = process_corrections(self.f.repo, self.f.store, self.f.market, self.f.agent, self.f.reserve,
                                     self.f.now, cancelled=lambda: cancelled[0], clock=lambda: self.f.now)
        self.assertIn("CANCELLED", result["pending"][0]["reason"])
        self.f.response_transform = lambda value: value
        result = process_corrections(self.f.repo, self.f.store, self.f.market, self.f.agent, self.f.reserve,
                                     self.f.now, clock=lambda: "2026-10-24T17:00:01Z")
        self.assertIn("expired", result["pending"][0]["reason"])
        self.assertEqual(self.f.charges, [("documents", 40), ("calls", 80), ("calls", 80)])
        self.assertFalse(list((self.f.store.root / "correction-admissions").glob("**/*.json")))

    def test_synthetic_or_missing_review_never_admits(self):
        self.f.agent.synthetic = True
        self.assert_held_before_charge("NON_ADMITTING")
        result = process_corrections(self.f.repo, self.f.store, self.f.market, None, self.f.reserve,
                                     self.f.now, clock=lambda: self.f.now)
        self.assertTrue(result["pending"])
        self.assertFalse(self.f.charges)

    def test_forged_flags_missing_index_and_wrong_admission_scope_fail_replay(self):
        forged = {"policySha256": self.f.policy, "pending": [], "admitted": [{"groupId": self.group["id"],
                  "admission": self.f.store.put({"result": "accepted", "reviewScope": PUBLISHER_DISCLOSURE_SCOPE})}]}
        with self.assertRaises(ValueError):
            self.f.project(forged)
        result = self.f.process()
        reference = result["admitted"][0]["admission"]
        admission = json.loads(self.f.store.get(reference))
        admission["reviewScope"] = "financial_primary"
        with self.assertRaisesRegex(ValueError, "scope differs"):
            replay_admission(self.group, self.f.store.put(admission), self.f.store, self.f.market,
                             self.f.review_policies[self.group["id"]], self.f.now)
        index = self.f.store.root / "correction-admissions" / self.f.review_policies[self.group["id"]]
        next(index.glob("*.json")).unlink()
        with self.assertRaisesRegex(ValueError, "accepted index"):
            self.f.project(result)

    def test_projected_official_label_never_grants_financial_source_authority(self):
        outcome = self.f.process()
        self.assertEqual(self.f.project(outcome)["groups"][0]["targets"][0]["proposedValue"]["sourceClass"], "OFFICIAL")
        source = {key: self.group["sources"][0][key] for key in ("evidenceId", "sourceId", "url", "observationId", "body", "fetchedAt")}
        original = self.original
        ordinary = {"id": "FC-financial-authority-forgery", "supplierId": "xage", "reasonCode": "metadata",
                    "noteTemplate": "Correction, {date}.", "sources": [source],
                    "targets": [self.f.target("evidence:TR-xage-1", original, {**original, "title": "New title"})]}
        self.f.requests["groups"] = [ordinary]
        self.f.repin()
        with self.assertRaisesRegex(ValueError, "requires primary organization"):
            load_policy(self.f.repo, self.f.market)
        self.assertEqual(self.f.raw["evidence"][-1]["sourceClass"], "INDEPENDENT")

    def test_ordinary_replace_cannot_change_class_even_for_exact_xage_record(self):
        group = self.group
        group.pop("reviewScope"); group.pop("disclosureQuotes")
        group["sources"] = [{k: v for k, v in group["sources"][0].items() if k not in ("proofScope", "visibleText", "disclosureQuoteIds")}]
        group["targets"][0]["operation"] = "replace"
        self.f.repin()
        self.assert_held_before_charge("Protected evidence metadata")

    def test_disjoint_role_group_addition_preserves_existing_fact_review_and_date(self):
        f = self.f
        f.requests["groups"] = [self.factual_group]
        f.repin()
        old_review_hash = f.review_policies[self.factual_group["id"]]
        before = f.process(); old_bundle = f.project(before)
        f.requests["groups"].append(self.group)
        f.repin()
        self.assertEqual(f.review_policies[self.factual_group["id"]], old_review_hash)
        pending = process_corrections(f.repo, f.store, f.market, None, f.reserve, f.now, clock=lambda: f.now)
        self.assertEqual(len(pending["admitted"]), 1)
        with self.assertRaisesRegex(ValueError, "pending"):
            f.project(pending, old_bundle)
        complete = f.process(); bundle = f.project(complete, old_bundle)
        self.assertEqual(bundle["groups"][0], old_bundle["groups"][0])
        self.assertNotIn("reviewScope", bundle["groups"][0])
        self.assertNotIn("reviewScope", bundle["groups"][0]["admission"])
        self.assertEqual(len(complete["attempts"]), 1)
        self.assertEqual(f.charges.count(("calls", 80)), 2)

    def test_unrelated_policy_edits_retain_role_row_but_relevant_source_cannot_overwrite(self):
        old = self.f.process(); old_bundle = self.f.project(old)
        old_hash = self.f.review_policies[self.group["id"]]
        self.f.market["sources"][0]["unrelatedFixtureChange"] = True
        self.f.repin()
        self.assertEqual(self.f.review_policies[self.group["id"]], old_hash)
        later = self.f.process(now="2026-12-23T12:00:00Z")
        self.assertEqual(self.f.project(later, old_bundle, "2026-12-23T12:00:00Z")["groups"], old_bundle["groups"])
        self.assertEqual(self.f.charges.count(("calls", 80)), 1)
        self.f.market["sources"][-1]["registrationProof"] = {"fixture": "changed"}
        self.f.repin()
        self.assertNotEqual(self.f.review_policies[self.group["id"]], old_hash)
        reviewed = self.f.process()
        with self.assertRaisesRegex(ValueError, "Historical correction changed"):
            self.f.project(reviewed, old_bundle)


if __name__ == "__main__":
    unittest.main()
