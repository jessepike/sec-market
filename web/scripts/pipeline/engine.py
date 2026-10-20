"""Resumable daily execution. Coverage receipts never imply publication."""
import json
import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from agents import ModelUnavailable
from contracts import canonical, digest, plan_run, require, utcnow
from discovery import Page, discover
from validation import reconcile, verify_statement


class Pipeline:
    def __init__(self, contract, store, fetcher, agent=None, clock=utcnow, structured=None):
        self.contract, self.store, self.fetcher, self.agent, self.clock = contract, store, fetcher, agent, clock
        self.structured = structured or self._structured
        self.sources = {s["id"]: s for s in contract["sources"]}
        self.suppliers = {s["id"]: s for s in contract["suppliers"]}
        self.model_lock = threading.Lock()

    def _structured(self, source, documents, day):
        result = subprocess.run(["node", "--import", "tsx", str(Path(__file__).with_name("sec-adapter.mjs"))],
                                input=json.dumps({"kind": source["kind"], "supplierId": source["supplierId"], "documents": documents, "windowEnd": day}),
                                capture_output=True, text=True, timeout=90, cwd=Path(__file__).resolve().parents[2])
        require(result.returncode == 0, "Independent SEC validation failed")
        return json.loads(result.stdout)["facts"]

    def run(self, scheduled_at):
        proposed = plan_run(self.contract, scheduled_at)
        plan_key = f"runs/{proposed['runId']}/plan.json"
        with self.store.lock(f"run-{proposed['runId']}"):
            plan = self.store.read(plan_key) or proposed
            require(plan["contractSha256"] == digest(self.contract), "Resume contract differs")
            self.store.write_once(plan_key, plan)
            self.budget_name = f"budget-{plan['runId']}"
            if self.agent:
                self.agent.reserve = self._reserve
            with ThreadPoolExecutor(max_workers=self.contract["schedule"]["maxWorkers"]) as pool:
                receipts = list(pool.map(lambda task: self._task(plan, task), plan["tasks"]))
            result = reconcile(plan, receipts, self.contract, self.clock(), self.store)
            result_ref = self.store.put(result)
            previous = self.store.read("heads/latest-run.json")
            self.store.compare_and_swap("latest-run", previous, {"runId": plan["runId"], "receipt": result_ref})
            return result

    def _task(self, plan, task):
        attempt_id = digest({"task": task["taskId"], "at": self.clock(), "nonce": __import__('uuid').uuid4().hex})
        receipt = {"taskId": task["taskId"], "sourceId": task["sourceId"], "supplierId": task["supplierId"],
                   "runId": plan["runId"], "attemptId": attempt_id, "startedAt": self.clock(), "completedAt": None,
                   "outcome": "failed", "discoveryComplete": False, "observationIds": [], "newFactIds": [], "validatedFacts": [], "errorCode": None}
        try:
            if task["kind"] == "missing_discovery":
                receipt.update(outcome="not_checked", errorCode="NO_REGISTERED_DISCOVERY_SOURCE")
                return self._finish(receipt)
            source = self.sources[task["sourceId"]]
            previous_head = self.store.read(f"heads/source-{digest(source['id'])}.json")
            previous = previous_head or {"observations": {}, "items": [], "validatedHashes": {}}
            observations = {}

            def request(url):
                old = previous["observations"].get(url)
                observation = self.fetcher.fetch(source, url, old)
                observation["observationId"] = digest({"attempt": attempt_id, "url": url, "at": observation["fetchedAt"]})
                observation["sourceId"] = source["id"]
                self.store.write_once(f"observations/{observation['observationId']}.json", observation)
                observations[url] = observation
                receipt["observationIds"].append(observation["observationId"])
                return observation, self.store.get(observation["body"]) if observation.get("body") else b""

            found = discover(source, request)
            receipt["discoveryComplete"] = found["complete"]
            manifest = self.store.put({"sourceId": source["id"], "items": found["items"], "observations": receipt["observationIds"]})
            receipt["itemManifest"] = manifest
            if not found["complete"]:
                receipt.update(outcome="blocked" if any(o.get("status") == "blocked" for o in found["observations"]) else "not_checked", errorCode=found["reason"])
                return self._finish(receipt)
            accepted = []
            validated_hashes = dict(previous.get("validatedHashes", {}))
            if source["kind"] in ("sec_facts", "sec_submissions"):
                documents = [json.loads(self.store.get(o["body"])) for o in found["observations"]]
                facts = self.structured(source, documents, plan["scheduledAt"][:10])
                for fact in facts:
                    fact.update(evidence=[o["body"] for o in found["observations"]], contractSha256=plan["contractSha256"])
                    self._accept(fact, accepted, receipt["validatedFacts"])
            else:
                # Item inventory is persisted before extraction: interrupted work stays queued.
                for url in found["items"]:
                    observation, body = request(url)
                    require(observation["status"] in ("fetched", "not_modified"), "Discovered document fetch failed")
                    cache_key = digest({"supplier": source["supplierId"], "body": observation["body"]["sha256"], "contract": plan["contractSha256"], "extractor": 2})
                    with self.store.lock(f"document-{cache_key}", blocking=True), self.model_lock:
                        cached = self.store.read(f"document-validation/{cache_key}.json")
                        if cached and cached["supplierId"] == source["supplierId"]:
                            receipt["validatedFacts"].extend(cached["factRefs"])
                            continue
                        page = Page(body.decode("utf8", errors="replace"))
                        model_text = (f"Source publication date metadata: {page.published}\n" if page.published else "") + page.readable
                        require(self.agent is not None, "SUBSCRIPTION_WORKER_REQUIRED")
                        self._reserve("documents", self.contract["model"]["maxDocumentsPerRun"])
                        candidates = self.agent.extract(model_text, self.suppliers[source["supplierId"]])
                        if not candidates:
                            review = self.agent.review_empty(model_text, self.suppliers[source["supplierId"]], observation, plan["contractSha256"])
                            require(review.get("noRelevantFacts") is True and review.get("evidenceSha256") == observation["body"]["sha256"] and review.get("policySha256") == plan["contractSha256"], "EMPTY_EXTRACTION_NOT_INDEPENDENTLY_CONFIRMED")
                            # A clear business signal must not disappear through two empty answers.
                            require(not __import__('re').search(r"\b(funding|raised|acquisition|appointed|restructuring|layoffs|ARR|revenue|debt|shutdown)\b", page.readable, __import__('re').I), "EMPTY_EXTRACTION_WITH_BUSINESS_SIGNAL")
                        document_facts = []
                        for candidate in candidates:
                            review = self.agent.review(page.readable, candidate, observation, plan["contractSha256"])
                            fact = verify_statement(candidate, observation, self.store, review, self.suppliers[source["supplierId"]], plan["contractSha256"])
                            self._accept(fact, accepted, document_facts)
                        receipt["validatedFacts"].extend(document_facts)
                        self.store.write_once(f"document-validation/{cache_key}.json", {"supplierId": source["supplierId"], "body": observation["body"], "contractSha256": plan["contractSha256"], "candidateHashes": [digest(c) for c in candidates], "factRefs": document_facts, "emptyReview": self.store.put(review) if not candidates else None})
                        validated_hashes[url] = cache_key
            # Advance only after all discovered items are either independently validated or explicitly no-fact.
            head = {"observations": observations, "items": found["items"], "validatedHashes": validated_hashes, "manifest": manifest}
            self.store.compare_and_swap(f"source-{digest(source['id'])}", previous_head, head)
            receipt.update(outcome="updated" if accepted else "checked_no_change", newFactIds=accepted)
        except (ValueError, KeyError, OSError, TimeoutError, RuntimeError, subprocess.SubprocessError) as exc:
            # Persist bounded reason codes, never model logs, tokens or response headers.
            receipt.update(outcome="failed", errorCode=str(exc)[:160] if isinstance(exc, (ValueError, ModelUnavailable)) else type(exc).__name__)
        return self._finish(receipt)

    def _reserve(self, kind, limit):
        # Run lock serializes processes; model_lock serializes this run's threads.
        # Reserve before invocation, so crashes/retries cannot reset daily budgets.
        previous = self.store.read(f"heads/{self.budget_name}.json")
        counts = dict(previous or {"calls": 0, "documents": 0})
        require(counts[kind] < limit, f"{kind.upper()}_BUDGET_EXHAUSTED")
        counts[kind] += 1
        self.store.compare_and_swap(self.budget_name, previous, counts)

    def _accept(self, fact, accepted, validated):
        key = f"facts/{fact['factId']}.json"
        with self.store.lock(f"fact-{fact['factId']}", blocking=True):
            previous = self.store.read(key)
            if previous is None:
                self.store.write_once(key, fact)
                accepted.append(fact["factId"])
            else:
                # Same assertion from another source adds provenance, not another market event.
                self.store.write_once(f"fact-observations/{fact['factId']}/{digest(fact)}.json", fact)
        validated.append(self.store.put(fact))

    def _finish(self, receipt):
        receipt["completedAt"] = self.clock()
        self.store.write_once(f"runs/{receipt['runId']}/attempts/{receipt['attemptId']}.json", receipt)
        return receipt
