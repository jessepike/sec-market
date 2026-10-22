"""Resumable daily execution. Coverage receipts never imply publication."""
import json
import subprocess
import threading
import time
from datetime import timedelta
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from agents import ModelUnavailable
from contracts import canonical, digest, instant, plan_run, require, utcnow
from discovery import Page, discover
from documents import readable_document
from validation import reconcile, verify_statement, mentions_entity


class Pipeline:
    def __init__(self, contract, store, fetcher, agent=None, clock=utcnow, structured=None):
        self.contract, self.store, self.fetcher, self.agent, self.clock = contract, store, fetcher, agent, clock
        self.structured = structured or self._structured
        self.sources = {s["id"]: s for s in contract["sources"]}
        self.suppliers = {s["id"]: s for s in contract["suppliers"]}
        self.model_lock = threading.Lock()
        self.budget_lock = threading.RLock()
        self.model_unavailable = None
        self.deadline = float("inf")
        self.native_budget_exhausted = False

    def _structured(self, source, documents, day):
        result = subprocess.run(["node", "--import", "tsx", str(Path(__file__).with_name("sec-adapter.mjs"))],
                                input=json.dumps({"kind": source["kind"], "supplierId": source["supplierId"], "documents": documents, "windowEnd": day}),
                                capture_output=True, text=True, timeout=90, cwd=Path(__file__).resolve().parents[2])
        require(result.returncode == 0, "Independent SEC validation failed")
        return json.loads(result.stdout)["facts"]

    def run(self, scheduled_at, replay=False):
        self.replay = replay
        self.deadline = time.monotonic() + self.contract["schedule"].get("maxRuntimeSeconds", 7200)
        proposed = plan_run(self.contract, scheduled_at)
        plan_key = f"runs/{proposed['runId']}/plan.json"
        with self.store.lock(f"run-{proposed['runId']}"):
            plan = self.store.read(plan_key) or proposed
            require(plan["contractSha256"] == digest(self.contract), "Resume contract differs")
            self.store.write_once(plan_key, plan)
            self.store.write_once(f"contracts/{plan['contractSha256']}.json", self.contract)
            self.budget_name = f"budget-{plan['scheduledAt'][:10]}"
            counts = self.store.read(f"heads/{self.budget_name}.json") or {}
            self.native_budget_exhausted = bool(getattr(self.agent, "queued_work", False) and
                (counts.get("calls", 0) >= self.contract["model"]["maxCallsPerRun"] or
                 counts.get("documents", 0) >= self.contract["model"]["maxDocumentsPerRun"]))
            if self.agent:
                self.agent.reserve = self._reserve
            with ThreadPoolExecutor(max_workers=self.contract["schedule"]["maxWorkers"]) as pool:
                priority = {"sec_facts": 0, "sec_submissions": 0, "citation": 1, "sec_documents": 2}
                tasks = sorted(plan["tasks"], key=lambda t: priority.get(self.sources.get(t["sourceId"], {}).get("kind"), 3))
                receipts = list(pool.map(lambda task: self._task(plan, task), tasks))
            result = reconcile(plan, receipts, self.contract, self.clock(), self.store)
            result_ref = self.store.put(result)
            previous = self.store.read("heads/latest-run.json")
            self.store.compare_and_swap("latest-run", previous, {"runId": plan["runId"], "receipt": result_ref})
            return result

    def _task(self, plan, task):
        prior_task = self.store.read(f"heads/task-{task['taskId']}.json") if self.replay else None
        if prior_task and prior_task["outcome"] in ("updated", "checked_no_change"):
            age = (instant(self.clock()) - instant(prior_task["completedAt"])).total_seconds()/3600
            if 0 <= age <= self.contract["schedule"]["overdueHours"]:
                return prior_task
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
                run_download = f"runs/{plan['runId']}/downloads/{digest({'source': source['id'], 'url': url})}.json"
                retained = self.store.read(run_download) if self.replay else None
                if retained:
                    old_observation = self.store.read(f"observations/{retained['observationId']}.json")
                    age = (instant(self.clock()) - instant(old_observation["fetchedAt"])).total_seconds()/3600
                    if 0 <= age <= self.contract["schedule"]["overdueHours"]:
                        observations[url] = old_observation
                        receipt["observationIds"].append(old_observation["observationId"])
                        return old_observation, self.store.get(old_observation["body"])
                download_name = f"download-{digest({'source': source['id'], 'url': url})}"
                download_head = self.store.read(f"heads/{download_name}.json")
                old = download_head or previous["observations"].get(url)
                cache_key = f"downloads/{digest({'source': source['id'], 'url': url})}.json"
                cached = self.store.read(cache_key) if source["kind"] == "sec_documents" and url.startswith("https://www.sec.gov/Archives/") else None
                if cached:
                    self.store.get(cached["body"])
                    anchors = [o["observationId"] for o in observations.values() if o["requestedUrl"].startswith("https://data.sec.gov/")]
                    require(bool(anchors), "Cached SEC document has no current index anchor")
                    observation = {**cached, "status": "retained_immutable", "verifiedAt": self.clock(),
                                   "reusesObservationId": cached["observationId"], "anchorObservationIds": anchors}
                else:
                    self._reserve("fetches", self.contract["schedule"].get("maxFetchesPerRun", 5000))
                    observation = self.fetcher.fetch(source, url, old)
                observation["observationId"] = digest({"attempt": attempt_id, "url": url, "at": observation["fetchedAt"]})
                observation["sourceId"] = source["id"]
                self.store.write_once(f"observations/{observation['observationId']}.json", observation)
                if observation["status"] in ("fetched", "not_modified"):
                    self.store.compare_and_swap(download_name, download_head, observation)
                    if self.replay:
                        self.store.write_once(run_download, {"observationId": observation["observationId"]})
                if source["kind"] == "sec_documents" and url.startswith("https://www.sec.gov/Archives/") and observation["status"] == "fetched":
                    self.store.write_once(cache_key, observation)
                observations[url] = observation
                receipt["observationIds"].append(observation["observationId"])
                return observation, self.store.get(observation["body"]) if observation.get("body") else b""

            found = discover(source, request)
            if source["kind"] == "sec_documents" and found["complete"]:
                cutoff = (instant(self.clock()) - timedelta(days=source.get("lookbackDays", 365))).date().isoformat()
                retained = {url for url, date in previous.get("itemDates", {}).items() if date >= cutoff}
                require(retained.issubset(found["items"]), "SEC_INDEX_REMOVED_WITHIN_RETENTION")
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
                pending, pending_errors = [], []
                def process_item(url):
                    observation, body = request(url)
                    require(observation["status"] in ("fetched", "not_modified", "retained_immutable"), "Discovered document fetch failed")
                    if source["kind"] == "sec_documents":
                        # Establish archived primary-document coverage separately from facts.
                        # Reading a filing is not automatic proof of every sentence it contains.
                        text = readable_document(body, observation.get("contentType", ""))
                        receipt.setdefault("documents", []).append({"url": url, "body": observation["body"], "text": self.store.put(text.encode())})
                        return
                    page = Page(body.decode("utf8", errors="replace"))
                    # Re-extract only pages whose newly supported publication
                    # metadata changes the model input; preserve other caches.
                    extractor = 4 if page.published_from_time else 3
                    cache_key = digest({"supplier": source["supplierId"], "body": observation["body"]["sha256"], "contract": plan["contractSha256"], "extractor": extractor})
                    with self.store.lock(f"document-{cache_key}", blocking=True), self.model_lock:
                        cached = self.store.read(f"document-validation/{cache_key}.json")
                        if cached and cached["supplierId"] == source["supplierId"]:
                            receipt["validatedFacts"].extend(cached["factRefs"])
                            receipt.setdefault("heldClaims", []).extend(cached.get("heldClaims", []))
                            receipt.setdefault("documentValidations", []).append({"url": url, "validation": self.store.put(cached)})
                            return
                        if source["family"] in ("investor_acquirer", "release_distribution") and not mentions_entity(page.readable, self.suppliers[source["supplierId"]]):
                            require(len(page.readable) >= 100, "Shared publisher page is unreadable")
                            validation = {"supplierId": source["supplierId"], "body": observation["body"], "contractSha256": plan["contractSha256"],
                                          "candidateHashes": [], "factRefs": [], "heldClaims": [], "exclusionRule": "no-registered-entity-mention-v1", "emptyReview": None}
                            self.store.write_once(f"document-validation/{cache_key}.json", validation)
                            receipt.setdefault("documentValidations", []).append({"url": url, "validation": self.store.put(validation)})
                            return
                        if self.agent is None or self.model_unavailable:
                            pending.append(url)
                            pending_errors.append(self.model_unavailable or "SUBSCRIPTION_WORKER_REQUIRED")
                            return
                        model_text = (f"Source publication date metadata: {page.published}\n" if page.published else "") + page.readable
                        try:
                            extracted = self.store.read(f"document-extractions/{cache_key}.json")
                            if extracted is None:
                                reservation_key = f"document-reservations/{plan['scheduledAt'][:10]}/{cache_key}.json"
                                if not self.store.read(reservation_key):
                                    self._reserve("documents", self.contract["model"]["maxDocumentsPerRun"])
                                    self.store.write_once(reservation_key, {"cacheKey": cache_key})
                                candidates = self.agent.extract(model_text, self.suppliers[source["supplierId"]])
                                extracted = {"candidates": candidates, "body": observation["body"], "policySha256": plan["contractSha256"]}
                                if hasattr(self.agent, "extraction_session"):
                                    extracted["nativeCollectorSession"] = self.agent.extraction_session
                                self.store.write_once(f"document-extractions/{cache_key}.json", extracted)
                            candidates = extracted["candidates"]
                            if hasattr(self.agent, "extraction_session"):
                                self.agent.extraction_session = extracted.get("nativeCollectorSession")
                        except (ModelUnavailable, ValueError) as exc:
                            if isinstance(exc, ModelUnavailable) or "BUDGET_EXHAUSTED" in str(exc):
                                if getattr(self.agent, "queued_work", False):
                                    self.native_budget_exhausted = True
                                else:
                                    self.model_unavailable = str(exc)[:160]
                            pending.append(url)
                            pending_errors.append(str(exc)[:160])
                            return
                        if not candidates:
                            review = self.agent.review_empty(model_text, self.suppliers[source["supplierId"]], observation, plan["contractSha256"])
                            require(review.get("noRelevantFacts") is True and review.get("evidenceSha256") == observation["body"]["sha256"] and review.get("policySha256") == plan["contractSha256"], "EMPTY_EXTRACTION_NOT_INDEPENDENTLY_CONFIRMED")
                            # A clear business signal must not disappear through two empty answers.
                            require(not __import__('re').search(r"\b(funding|raised|acquisition|appointed|restructuring|layoffs|ARR|revenue|debt|shutdown)\b", page.readable, __import__('re').I), "EMPTY_EXTRACTION_WITH_BUSINESS_SIGNAL")
                        document_facts, held_claims = [], []
                        for candidate in candidates:
                            review_key = f"candidate-reviews/{digest({'cache': cache_key, 'candidate': candidate})}.json"
                            saved_review = self.store.read(review_key)
                            if saved_review is None:
                                review = self.agent.review(model_text, candidate, observation, plan["contractSha256"])
                                self.store.write_once(review_key, review)
                            else:
                                review = saved_review
                            try:
                                fact = verify_statement(candidate, observation, self.store, review, self.suppliers[source["supplierId"]], plan["contractSha256"])
                                self._accept(fact, accepted, document_facts)
                            except ValueError as exc:
                                held = {"supplierId": source["supplierId"], "candidate": candidate,
                                        "candidateSha256": digest(candidate), "sourceObservationId": observation["observationId"],
                                        "evidence": observation["body"], "review": self.store.put(review),
                                        "policySha256": plan["contractSha256"], "reason": str(exc)[:160]}
                                held_claims.append(self.store.put(held))
                        receipt["validatedFacts"].extend(document_facts)
                        receipt.setdefault("heldClaims", []).extend(held_claims)
                        validation = {"supplierId": source["supplierId"], "body": observation["body"], "contractSha256": plan["contractSha256"], "candidateHashes": [digest(c) for c in candidates], "factRefs": document_facts, "heldClaims": held_claims, "emptyReview": self.store.put(review) if not candidates else None}
                        self.store.write_once(f"document-validation/{cache_key}.json", validation)
                        receipt.setdefault("documentValidations", []).append({"url": url, "validation": self.store.put(validation)})
                        validated_hashes[url] = cache_key
                ordered = sorted(found["items"], key=lambda u: found.get("itemModified", {}).get(u, ""), reverse=True)
                for index, url in enumerate(ordered):
                    cached_download = f"runs/{plan['runId']}/downloads/{digest({'source': source['id'], 'url': url})}.json"
                    if self.native_budget_exhausted and source["kind"] != "sec_documents" and not self.store.read(cached_download):
                        pending.append(url)
                        pending_errors.append("NATIVE_NEW_WORK_BUDGET_EXHAUSTED")
                        continue
                    if self.model_unavailable and source["kind"] != "sec_documents":
                        pending.extend(ordered[index:])
                        pending_errors.append(self.model_unavailable)
                        break
                    try:
                        process_item(url)
                    except (ValueError, ModelUnavailable, OSError, TimeoutError) as exc:
                        if isinstance(exc, ModelUnavailable):
                            self.model_unavailable = str(exc)[:160]
                        pending.append(url)
                        pending_errors.append(str(exc)[:160] if isinstance(exc, (ValueError, ModelUnavailable)) else type(exc).__name__)
                        receipt.setdefault("heldDocuments", []).append({"url": url, "reason": pending_errors[-1]})
                if pending:
                    receipt.update(outcome="not_checked", errorCode=pending_errors[0], pendingDocuments=len(pending),
                                   pendingManifest=self.store.put({"sourceId": source["id"], "runId": plan["runId"], "items": pending}))
                    return self._finish(receipt)
            # Advance only after all discovered items are either independently validated or explicitly no-fact.
            head = {"observations": observations, "items": found["items"], "itemDates": found.get("itemDates", {}), "validatedHashes": validated_hashes, "manifest": manifest}
            self.store.compare_and_swap(f"source-{digest(source['id'])}", previous_head, head)
            receipt.update(outcome="updated" if accepted else "checked_no_change", newFactIds=accepted)
        except (ValueError, KeyError, OSError, TimeoutError, RuntimeError, subprocess.SubprocessError) as exc:
            # Persist bounded reason codes, never model logs, tokens or response headers.
            receipt.update(outcome="failed", errorCode=str(exc)[:160] if isinstance(exc, (ValueError, ModelUnavailable)) else type(exc).__name__)
        return self._finish(receipt)

    def _reserve(self, kind, limit):
        # Run lock serializes processes; model_lock serializes this run's threads.
        # Reserve before invocation, so crashes/retries cannot reset daily budgets.
        with self.budget_lock:
            require(time.monotonic() < self.deadline, "RUN_TIME_BUDGET_EXHAUSTED")
            with self.store.lock("daily-budget-reservation", blocking=True):
                previous = self.store.read(f"heads/{self.budget_name}.json")
                counts = dict(previous or {"calls": 0, "documents": 0, "fetches": 0})
                require(counts.get(kind, 0) < limit, f"{kind.upper()}_BUDGET_EXHAUSTED")
                counts[kind] = counts.get(kind, 0) + 1
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
        head = "task-" + receipt["taskId"]
        self.store.compare_and_swap(head, self.store.read(f"heads/{head}.json"), receipt)
        return receipt
