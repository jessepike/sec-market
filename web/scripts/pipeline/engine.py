"""Resumable daily execution. Coverage receipts never imply publication."""
import json
import subprocess
import threading
import time
from datetime import timedelta, timezone
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from agents import ModelUnavailable
from contracts import canonical, digest, instant, plan_run, require, utcnow
from discovery import Page, decoded_discovery_body, discover
from documents import article_input, readable_document, verify_article_input
from selection import select_documents
from validation import reconcile, verify_statement, mentions_entity
from retained_audit import (VERSION as AUDIT_VERSION, activate_compatibility, bounded as audit_bounded,
                            index_for, predecessor_inventory, replay_binding, replay_document, verify_receipt)


class Pipeline:
    def __init__(self, contract, store, fetcher, agent=None, clock=utcnow, structured=None, correction_work=None):
        self.contract, self.store, self.fetcher, self.agent, self.clock = contract, store, fetcher, agent, clock
        self.structured = structured or self._structured
        self.correction_work = correction_work
        self.sources = {s["id"]: s for s in contract["sources"]}
        self.suppliers = {s["id"]: s for s in contract["suppliers"]}
        self.model_lock = threading.Lock()
        self.budget_lock = threading.RLock()
        self.model_unavailable = None
        self.deadline = float("inf")
        self.native_budget_exhausted = False
        self.transport_cache = {}
        self.defer_citation_models = False

    def _structured(self, source, documents, day):
        result = subprocess.run(["node", "--import", "tsx", str(Path(__file__).with_name("sec-adapter.mjs"))],
                                input=json.dumps({"kind": source["kind"], "supplierId": source["supplierId"], "documents": documents, "windowEnd": day}),
                                capture_output=True, text=True, timeout=90, cwd=Path(__file__).resolve().parents[2])
        require(result.returncode == 0, "Independent SEC validation failed")
        return json.loads(result.stdout)["facts"]

    def run(self, scheduled_at, replay=False, force_refresh=False):
        self.replay = replay
        self.force_refresh = force_refresh
        self.transport_cache = {}
        self.deadline = time.monotonic() + self.contract["schedule"].get("maxRuntimeSeconds", 7200)
        proposed = plan_run(self.contract, scheduled_at)
        plan_key = f"runs/{proposed['runId']}/plan.json"
        with self.store.lock(f"run-{proposed['runId']}"):
            plan = self.store.read(plan_key) or proposed
            require(plan["contractSha256"] == digest(self.contract), "Resume contract differs")
            self.store.write_once(plan_key, plan)
            self.store.write_once(f"contracts/{plan['contractSha256']}.json", self.contract)
            self.audit_index = index_for(self.store) if self.contract.get('collection') else None
            self.audit_compatibility = (activate_compatibility(self.store, plan, self.contract, self.audit_index)
                                        if self.audit_index is not None else None)
            self.prior_receipts = {}
            prior = self.store.read("heads/latest-run.json")
            if prior and prior.get("runId") == plan["runId"]:
                saved = json.loads(self.store.get(prior["receipt"]))
                require(saved["contractSha256"] == plan["contractSha256"], "Prior receipt policy differs")
                self.prior_receipts = {r["attemptId"]: r for r in saved["receipts"]}
            self.budget_name = f"budget-{plan['scheduledAt'][:10]}"
            counts = self.store.read(f"heads/{self.budget_name}.json") or {}
            self.native_budget_exhausted = bool(getattr(self.agent, "queued_work", False) and
                (counts.get("calls", 0) >= self.contract["model"]["maxCallsPerRun"] or
                 counts.get("documents", 0) >= self.contract["model"]["maxDocumentsPerRun"]))
            if self.agent:
                self.agent.reserve = self._reserve
            with ThreadPoolExecutor(max_workers=self.contract["schedule"]["maxWorkers"]) as pool:
                priority = {"sec_facts": 0, "sec_submissions": 0, "sec_documents": 0, "sec_index": 0, "citation": 1}
                # Rotate the same-priority sources daily so a finite global model
                # budget does not always go to the first suppliers in the roster.
                day = instant(plan["scheduledAt"]).date().toordinal()
                tasks = sorted(plan["tasks"], key=lambda t: (priority.get(self.sources.get(t["sourceId"], {}).get("kind"), 3), digest({"day": day, "task": t["taskId"]})))
                if self.correction_work is None:
                    receipts = list(pool.map(lambda task: self._task(plan, task), tasks))
                else:
                    deterministic = [t for t in tasks if self.sources.get(t["sourceId"], {}).get("kind") in priority]
                    discretionary = [t for t in tasks if self.sources.get(t["sourceId"], {}).get("kind") not in priority]
                    # Citation transport and accepted caches run first, while
                    # uncached citation model work waits for whole-group review.
                    self.defer_citation_models = True
                    try:
                        receipts = list(pool.map(lambda task: self._task(plan, task), deterministic))
                    finally:
                        self.defer_citation_models = False
                    deferred_ids = {r['taskId'] for r in receipts if r.get('citationModelWorkDeferred')}
                    second_phase = [t for t in deterministic if t['taskId'] in deferred_ids] + discretionary
                    try:
                        corrections = self.correction_work(reserve=self._reserve, now=self.clock(),
                                                           cancelled=self._work_cancelled)
                    except (ValueError, RuntimeError, OSError, KeyError, TypeError) as exc:
                        # Invalid correction inputs cannot erase ordinary source
                        # receipts or turn a failed review into an admission.
                        corrections = {"policySha256": None, "admitted": [], "pending": [], "attempts": [],
                                       "error": str(exc)[:160] if isinstance(exc, (ValueError, ModelUnavailable)) else type(exc).__name__}
                    correction_record = {"runId": plan["runId"], "checkedAt": self.clock(), **corrections}
                    correction_ref = self.store.put(correction_record)
                    self.store.write_once(f"runs/{plan['runId']}/correction-collections/{correction_ref['sha256']}.json", correction_record)
                    old = self.store.read("heads/correction-collection.json")
                    self.store.compare_and_swap("correction-collection", old, {"runId": plan["runId"], "outcome": correction_ref})
                    final_receipts = {r['taskId']: r for r in receipts}
                    for receipt in pool.map(lambda task: self._task(plan, task), second_phase):
                        final_receipts[receipt['taskId']] = receipt
                    receipts = [final_receipts[t['taskId']] for t in tasks]
            result = reconcile(plan, receipts, self.contract, self.clock(), self.store)
            result_ref = self.store.put(result)
            previous = self.store.read("heads/latest-run.json")
            self.store.compare_and_swap("latest-run", previous, {"runId": plan["runId"], "receipt": result_ref})
            # Coverage remains exactly replayable by reconcile. Corrections
            # have their own immutable receipt and never alter its denominator.
            return {**result, "corrections": {**corrections, "receipt": correction_ref}} if self.correction_work is not None else result

    def _work_cancelled(self):
        return bool(getattr(self, "cancelled", False) or time.monotonic() >= self.deadline)

    def _task(self, plan, task):
        if not self.force_refresh:
            reusable = self._reusable_receipt(plan, task)
            if reusable is not None:
                return reusable
        attempt_id = digest({"task": task["taskId"], "at": self.clock(), "nonce": __import__('uuid').uuid4().hex})
        receipt = {"taskId": task["taskId"], "sourceId": task["sourceId"], "supplierId": task["supplierId"],
                   "runId": plan["runId"], "attemptId": attempt_id, "startedAt": self.clock(), "completedAt": None,
                   "outcome": "failed", "discoveryComplete": False, "observationIds": [], "newFactIds": [], "validatedFacts": [], "errorCode": None}
        try:
            if task["kind"] == "missing_discovery":
                receipt.update(outcome="not_checked", errorCode="NO_REGISTERED_DISCOVERY_SOURCE")
                return self._finish(receipt)
            source = self.sources[task["sourceId"]]
            if audit_bounded(source, self.contract):
                receipt.update(retainedAuditVersion=AUDIT_VERSION, retainedAuditCompatibility=self.audit_compatibility)
            previous_head = self.store.read(f"heads/source-{digest(source['id'])}.json")
            previous = previous_head or {"observations": {}, "items": [], "validatedHashes": {}}
            observations = {}
            neutral_filings = source['kind'] == 'sec_documents' and 'regulatoryIssuer' in source
            if neutral_filings:
                require(previous.get('validatedHashes', {}) == {} and all(previous.get(key, []) == [] for key in
                        ('validatedFacts', 'factRefs', 'newFactIds', 'documentValidations', 'heldClaims')),
                        'Neutral SEC filing source head contains semantic references')
            index_as_of = self.clock() if source['kind'] == 'sec_index' or neutral_filings else None

            def request(url):
                if neutral_filings:
                    require(instant(index_as_of).astimezone(timezone.utc).date() == instant(self.clock()).astimezone(timezone.utc).date(),
                            'SEC_FILING_WINDOW_CHANGED_DURING_COLLECTION')
                if url in observations:
                    retained_observation = observations[url]
                    return retained_observation, self.store.get(retained_observation['body']) if retained_observation.get('body') else b''
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
                    observation = self._fetch_transport(source, url, old)
                observation["observationId"] = digest({"attempt": attempt_id, "url": url, "at": observation["fetchedAt"]})
                observation["sourceId"] = source["id"]
                self.store.write_once(f"observations/{observation['observationId']}.json", observation)
                if self.audit_index is not None:
                    self.audit_index.register_observation(observation)
                if observation["status"] in ("fetched", "not_modified"):
                    self.store.compare_and_swap(download_name, download_head, observation)
                    if self.replay:
                        self.store.write_once(run_download, {"observationId": observation["observationId"]})
                if source["kind"] == "sec_documents" and url.startswith("https://www.sec.gov/Archives/") and observation["status"] == "fetched":
                    self.store.write_once(cache_key, observation)
                observations[url] = observation
                receipt["observationIds"].append(observation["observationId"])
                return observation, self.store.get(observation["body"]) if observation.get("body") else b""

            found = discover({**source, "checkedAt": index_as_of} if index_as_of else source, request)
            index_checked_at = self.clock() if index_as_of else None
            if index_as_of:
                require(instant(index_as_of).astimezone(timezone.utc).date() == instant(index_checked_at).astimezone(timezone.utc).date(),
                        "SEC_INDEX_WINDOW_CHANGED_DURING_DISCOVERY")
                require(all(instant(o["fetchedAt"]) <= instant(index_checked_at) for o in found["observations"]),
                        "SEC_INDEX_VERIFICATION_PRECEDES_SOURCE_OBSERVATION")
            filing_verification = None
            if neutral_filings and found['complete']:
                from regulatory import verify_filing_index_documents
                index_documents = [{'url': o['requestedUrl'], 'document': json.loads(decoded_discovery_body(self.store.get(o['body'])))}
                                   for o in found['observations']]
                filing_verification = verify_filing_index_documents(source, index_documents, index_checked_at)
                selected = filing_verification['selectedDocuments']
                require(found['items'] == [item['url'] for item in selected] and
                        found.get('itemDates') == {item['url']: item['filingDate'] for item in selected},
                        'Neutral SEC filing discovery selection differs')
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
            validated_hashes = {} if source["kind"] == "sec_index" or neutral_filings else dict(previous.get("validatedHashes", {}))
            if neutral_filings:
                receipt['regulatoryFilingValidation'] = self.store.put({
                    'sourceId': source['id'], 'supplierId': source['supplierId'], 'contractSha256': plan['contractSha256'],
                    'traversalAsOf': index_as_of, 'checkedAt': index_checked_at,
                    'observationIds': list(receipt['observationIds']),
                    'documents': [{'url': o['requestedUrl'], 'observationId': o['observationId'], 'body': o['body']}
                                  for o in found['observations']], 'verification': filing_verification,
                    'selectedDocuments': filing_verification['selectedDocuments']})
            if source["kind"] == "sec_index":
                from regulatory import verify_index_documents
                documents = [{"url": o["requestedUrl"], "document": json.loads(decoded_discovery_body(self.store.get(o["body"])))}
                             for o in found["observations"]]
                verified_index = verify_index_documents(source, documents, index_checked_at)
                require(verified_index.get("facts") == [], "Neutral SEC index cannot emit facts")
                receipt["regulatoryIndexValidation"] = self.store.put({
                    "sourceId": source["id"], "supplierId": source["supplierId"], "contractSha256": plan["contractSha256"],
                    "traversalAsOf": index_as_of, "checkedAt": index_checked_at, "observationIds": list(receipt["observationIds"]),
                    "documents": [{"url": o["requestedUrl"], "observationId": o["observationId"], "body": o["body"]}
                                  for o in found["observations"]], "verification": verified_index})
            elif source["kind"] in ("sec_facts", "sec_submissions"):
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
                        if neutral_filings:
                            require(observation.get('requestedUrl') == url and observation.get('finalUrl', url) == url,
                                    'Neutral SEC primary response URL differs')
                        text = readable_document(body, observation.get("contentType", ""))
                        receipt.setdefault("documents", []).append({"url": url, "body": observation["body"], "text": self.store.put(text.encode())})
                        return
                    input_view = article_input(body, observation)
                    page = input_view['page']
                    input_fields = {'compressedInput': input_view['compressedInput']} if input_view['compressedInput'] is not None else {}
                    # Re-extract only pages whose newly supported publication
                    # metadata changes the model input; preserve other caches.
                    extractor = input_view['extractor']
                    cache_key = digest({"supplier": source["supplierId"], "body": observation["body"]["sha256"], "contract": plan["contractSha256"], "extractor": extractor})
                    with self.store.lock(f"document-{cache_key}", blocking=True), self.model_lock:
                        cached = self.store.read(f"document-validation/{cache_key}.json")
                        if cached and cached["supplierId"] == source["supplierId"]:
                            verify_article_input(cached, body, observation)
                            if audit_bounded(source, self.contract):
                                transient = {**receipt, 'completedAt': self.clock(),
                                             'validatedFacts': cached['factRefs'], 'heldClaims': cached.get('heldClaims', [])}
                                replay_document(transient, {'url': url, 'validation': self.store.put(cached)},
                                                observation, self.contract, source, self.clock(), self.store)
                            receipt["validatedFacts"].extend(cached["factRefs"])
                            receipt.setdefault("heldClaims", []).extend(cached.get("heldClaims", []))
                            receipt.setdefault("documentValidations", []).append({"url": url, "validation": self.store.put(cached)})
                            return
                        if source["family"] in ("investor_acquirer", "release_distribution") and not mentions_entity(page.readable, self.suppliers[source["supplierId"]]):
                            require(len(page.readable) >= 100, "Shared publisher page is unreadable")
                            validation = {"supplierId": source["supplierId"], "body": observation["body"], "contractSha256": plan["contractSha256"],
                                          "candidateHashes": [], "factRefs": [], "heldClaims": [], "exclusionRule": "no-registered-entity-mention-v1", "emptyReview": None, **input_fields}
                            self.store.write_once(f"document-validation/{cache_key}.json", validation)
                            receipt.setdefault("documentValidations", []).append({"url": url, "validation": self.store.put(validation)})
                            return
                        if source['kind'] == 'citation' and self.defer_citation_models:
                            receipt['citationModelWorkDeferred'] = True
                            pending.append(url)
                            pending_errors.append('CITATION_MODEL_WORK_DEFERRED_FOR_CORRECTIONS')
                            return
                        if self.agent is None or self.model_unavailable:
                            pending.append(url)
                            pending_errors.append(self.model_unavailable or "SUBSCRIPTION_WORKER_REQUIRED")
                            return
                        model_text = input_view['modelText']
                        try:
                            extracted = self.store.read(f"document-extractions/{cache_key}.json")
                            if extracted is None:
                                reservation_key = f"document-reservations/{plan['scheduledAt'][:10]}/{cache_key}.json"
                                if not self.store.read(reservation_key):
                                    self._reserve("documents", self.contract["model"]["maxDocumentsPerRun"])
                                    self.store.write_once(reservation_key, {"cacheKey": cache_key})
                                candidates = self.agent.extract(model_text, self.suppliers[source["supplierId"]])
                                extracted = {"candidates": candidates, "body": observation["body"], "policySha256": plan["contractSha256"], **input_fields}
                                if hasattr(self.agent, "extraction_session"):
                                    extracted["nativeCollectorSession"] = self.agent.extraction_session
                                self.store.write_once(f"document-extractions/{cache_key}.json", extracted)
                            verify_article_input(extracted, body, observation)
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
                        validation = {"supplierId": source["supplierId"], "body": observation["body"], "contractSha256": plan["contractSha256"], "candidateHashes": [digest(c) for c in candidates], "factRefs": document_facts, "heldClaims": held_claims, "emptyReview": self.store.put(review) if not candidates else None, **input_fields}
                        self.store.write_once(f"document-validation/{cache_key}.json", validation)
                        receipt.setdefault("documentValidations", []).append({"url": url, "validation": self.store.put(validation)})
                        validated_hashes[url] = cache_key
                ordered = sorted(found["items"], key=lambda u: found.get("itemModified", {}).get(u, ""), reverse=True)
                audit_name = f"audit-{digest(source['id'])}"
                audit_head = self.store.read(f"heads/{audit_name}.json")
                audit_history = dict((audit_head or {}).get("documents", {})) if (audit_head or {}).get("contractSha256") == plan["contractSha256"] else {}
                bounded = audit_bounded(source, self.contract)
                if bounded:
                    # Only affected compressed inputs become due again. Old
                    # ordinary audit entries keep their exact rotation stamps.
                    for url, stamp in list(audit_history.items()):
                        downloaded = self.store.read(f"heads/download-{digest({'source': source['id'], 'url': url})}.json") or previous['observations'].get(url)
                        reference = downloaded.get('body') if downloaded else stamp.get('body')
                        if reference is None:
                            continue
                        raw = self.store.get(reference)
                        if raw.startswith(b'\x1f\x8b'):
                            try:
                                view = article_input(raw, downloaded or {'requestedUrl': url})
                                current_input = stamp.get('body') == reference and stamp.get('compressedInput') == view['compressedInput']
                            except ValueError:
                                current_input = False
                            if not current_input:
                                del audit_history[url]
                    # Feeds can age old URLs out. Preserve previously pending
                    # obligations even when they disappear from today's index.
                    retained_items = set(found["items"])
                    predecessors = self.audit_index.predecessors(source['id'], self.contract, receipt['attemptId'], receipt['startedAt'])
                    anchored_inventory = predecessor_inventory(predecessors, self.contract, source['id'], self.store)
                    retained_items.update(anchored_inventory)
                    prior_receipt = self.store.read(f"heads/task-{task['taskId']}.json")
                    if prior_receipt and prior_receipt.get("pendingManifest"):
                        retained_items.update(json.loads(self.store.get(prior_receipt["pendingManifest"]))["items"])
                    if audit_head and audit_head.get("inventory"):
                        legacy_inventory = set(json.loads(self.store.get(audit_head["inventory"]))["items"])
                        require(legacy_inventory.issubset(retained_items), 'RETAINED_AUDIT_INVENTORY_PREDECESSOR_MISSING')
                    receipt.update(retainedInventoryManifest=self.store.put({'sourceId': source['id'], 'items': sorted(retained_items)}),
                                   retainedInventoryPredecessors=predecessors, retainedAuditBindings=[], retainedAuditUnbound=[])
                    # Expired or superseded transport is genuine due work. The normal
                    # source bound applies; an offline replay cannot renew it.
                    selection_history = dict(audit_history)
                    for url in list(audit_history):
                        try:
                            self.audit_index.binding(source['id'], url, self.contract, self.clock())
                        except (ValueError, KeyError, OSError, TypeError):
                            del selection_history[url]
                    selected_inventory = {**found, "items": sorted(retained_items)}
                    ordered, deferred = select_documents(selected_inventory, selection_history, self.contract["collection"], self.clock(),
                        supplier=self.suppliers[source['supplierId']] if source['family'] in ('investor_acquirer', 'release_distribution') else None)
                    pending.extend(deferred)
                    if deferred:
                        pending_errors.append("HISTORICAL_OR_UNCHANGED_AUDIT_PENDING")
                    receipt["collectionScope"] = {"mode": "delta_with_retained_audit", "selectedDocuments": len(ordered), "deferredDocuments": len(deferred), "currentWindowDays": self.contract["collection"]["currentWindowDays"]}
                    retained_audit = set(selected_inventory["items"]) - set(ordered) - set(deferred)
                    if retained_audit:
                        receipt["retainedAuditDocuments"] = len(retained_audit)
                    for url in sorted(retained_audit):
                        try:
                            binding = self.audit_index.binding(source['id'], url, self.contract, self.clock())
                            original, validation = replay_binding(
                                binding, self.contract, source['id'], self.clock(), self.store, self.audit_index)
                            receipt['retainedAuditBindings'].append(binding)
                            if original['observationId'] not in receipt['observationIds']:
                                receipt['observationIds'].append(original['observationId'])
                            receipt.setdefault('documentValidations', []).append({'url': url, 'validation': binding['validation']})
                            receipt['validatedFacts'].extend(validation['factRefs'])
                            receipt.setdefault('heldClaims', []).extend(validation.get('heldClaims', []))
                        except (ValueError, KeyError, OSError, TypeError) as exc:
                            receipt['retainedAuditUnbound'].append({'url': url, 'reason': str(exc)[:160]})
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
                if bounded:
                    # This is an audit work cursor, never the source's successful
                    # completeness cursor. Failed/pending checks are not advanced.
                    for document in receipt.get("documentValidations", []):
                        url = document["url"]
                        if any(binding['url'] == url for binding in receipt['retainedAuditBindings']):
                            continue
                        audit_history[url] = {"modified": found.get("itemModified", {}).get(url, ""), "checkedAt": self.clock()}
                        validation = json.loads(self.store.get(document['validation']))
                        if 'compressedInput' in validation:
                            audit_history[url].update(body=validation['body'], compressedInput=validation['compressedInput'])
                    retained_manifest = self.store.put({"sourceId": source["id"], "items": selected_inventory["items"]})
                    self.store.compare_and_swap(audit_name, audit_head, {"documents": audit_history, "inventory": retained_manifest, "contractSha256": plan["contractSha256"]})
                if pending:
                    receipt.update(outcome="not_checked", errorCode=pending_errors[0], pendingDocuments=len(pending),
                                   pendingManifest=self.store.put({"sourceId": source["id"], "runId": plan["runId"], "items": pending}))
                    return self._finish(receipt)
                if bounded and receipt.get("retainedAuditUnbound"):
                    # The scheduling cursor is not proof in this receipt. Until
                    # old evidence is independently rebound, keep completeness
                    # held without inventing unresolved document work.
                    receipt.update(outcome="not_checked", errorCode="RETAINED_AUDIT_EVIDENCE_NOT_REBOUND", pendingDocuments=0)
                    return self._finish(receipt)
            # Advance only after all discovered items are either independently validated or explicitly no-fact.
            if audit_bounded(source, self.contract):
                verify_receipt({**receipt, 'completedAt': self.clock(),
                                'outcome': 'updated' if accepted else 'checked_no_change', 'newFactIds': accepted},
                               plan, self.contract, source, self.clock(), self.store)
            if neutral_filings:
                require(instant(index_as_of).astimezone(timezone.utc).date() == instant(self.clock()).astimezone(timezone.utc).date(),
                        'SEC_FILING_WINDOW_CHANGED_DURING_COLLECTION')
            head = {"observations": observations, "items": found["items"], "itemDates": found.get("itemDates", {}), "validatedHashes": validated_hashes, "manifest": manifest}
            self.store.compare_and_swap(f"source-{digest(source['id'])}", previous_head, head)
            receipt.update(outcome="updated" if accepted else "checked_no_change", newFactIds=accepted)
        except (ValueError, KeyError, OSError, TimeoutError, RuntimeError, subprocess.SubprocessError) as exc:
            # Persist bounded reason codes, never model logs, tokens or response headers.
            receipt.update(outcome="failed", errorCode=str(exc)[:160] if isinstance(exc, (ValueError, ModelUnavailable)) else type(exc).__name__)
        return self._finish(receipt)

    def _fetch_transport(self, source, url, previous):
        hosts = sorted(source['allowedHosts'])
        strict_sec = url.startswith('https://data.sec.gov/') and source['kind'] in ('sec_facts', 'sec_submissions', 'sec_documents', 'sec_index')
        if strict_sec:
            # Both SEC index bindings permit this stricter redirect policy.
            # Do not reuse a response obtained through a broader host policy.
            require('data.sec.gov' in hosts, 'SEC transport host not registered')
            hosts = ['data.sec.gov']
        # These public SEC GETs use the same fixed headers and exact data-only
        # redirect policy. Share raw 200 bytes, then validate each subject anew.
        # Ordinary source policies and every conditional chain remain separate.
        key = digest({'url': url, 'hosts': hosts, 'supplier': None if strict_sec else source['supplierId']})
        with self.store.lock('transport-' + key, blocking=True):
            if key in self.transport_cache:
                observation = dict(self.transport_cache[key])
                self.store.get(observation['body'])
                observation['transportReused'] = True
                return observation
            self._reserve('fetches', self.contract['schedule'].get('maxFetchesPerRun', 5000))
            observation = self.fetcher.fetch({**source, 'allowedHosts': hosts}, url, previous)
            observation = {**observation, 'transportReused': False}
            observation.pop('transportId', None)
            # Source-specific 304 provenance must remain source-specific. Only
            # full responses obtained during this invocation are shareable.
            if observation.get('status') == 'fetched' and observation.get('httpStatus') == 200:
                self.store.get(observation['body'])
                observation = {**observation, 'transportReused': False,
                               'transportId': digest({'request': key, 'at': observation['fetchedAt'], 'body': observation['body']})}
                self.transport_cache[key] = dict(observation)
            return observation

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

    def _reusable_receipt(self, plan, task):
        candidates = {r['attemptId']: r for r in self.prior_receipts.values() if r.get('taskId') == task['taskId']}
        # Immutable seals retain successful attempts even after a later forced
        # refresh fails. Unsealed legacy attempts earn no trust from JSON alone.
        directory = self.store.root / 'receipt-integrity' / plan['runId'] / task['taskId']
        for path in directory.glob('*.json'):
            try:
                ref = self.store.read(str(path.relative_to(self.store.root)))
                receipt = json.loads(self.store.get(ref))
                candidates[receipt['attemptId']] = receipt
            except (ValueError, KeyError, OSError):
                continue
        subset = {**plan, 'tasks': [task], 'inventorySha256': digest([task])}
        for receipt in sorted(candidates.values(), key=lambda r: str(r.get('completedAt', '')), reverse=True):
            try:
                if receipt.get('outcome') not in ('updated', 'checked_no_change'):
                    continue
                age = (instant(self.clock()) - instant(receipt['completedAt'])).total_seconds()/3600
                require(0 <= age <= self.contract['schedule']['overdueHours'], 'Prior receipt stale or future')
                require(receipt.get('discoveryComplete') is True and bool(receipt.get('observationIds')), 'Prior discovery incomplete')
                require(receipt['supplierId'] == task['supplierId'], 'Prior receipt entity differs')
                for oid in receipt['observationIds']:
                    observation = self.store.read(f'observations/{oid}.json')
                    require(observation is not None, 'Prior source observation missing')
                    observed_age = (instant(self.clock()) - instant(observation.get('verifiedAt', observation['fetchedAt']))).total_seconds()/3600
                    require(0 <= observed_age <= self.contract['schedule']['overdueHours'], 'Prior observation stale or future')
                    if audit_bounded(self.sources[task['sourceId']], self.contract):
                        require(self.audit_index.latest_observation(task['sourceId'], observation['requestedUrl']) == observation,
                                'Prior receipt superseded by a newer source observation')
                archived = self.store.read(f"runs/{plan['runId']}/attempts/{receipt['attemptId']}.json")
                require(archived == receipt, 'Prior attempt differs from hash-anchored receipt')
                verified = reconcile(subset, [receipt], self.contract, self.clock(), self.store)
                require(verified['successfulTasks'] == int(task['required']), 'Prior source check is stale or incomplete')
                return receipt
            except (ValueError, KeyError, OSError, TypeError):
                continue
        return None

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
        receipt['observationIds'] = list(dict.fromkeys(receipt['observationIds']))
        for key in ('validatedFacts', 'heldClaims'):
            if key in receipt:
                receipt[key] = list({ref['sha256']: ref for ref in receipt[key]}.values())
        receipt["completedAt"] = self.clock()
        self.store.write_once(f"runs/{receipt['runId']}/attempts/{receipt['attemptId']}.json", receipt)
        reference = self.store.put(receipt)
        self.store.write_once(f"receipt-integrity/{receipt['runId']}/{receipt['taskId']}/{receipt['attemptId']}.json", reference)
        if getattr(self, 'audit_index', None) is not None:
            self.audit_index.register(receipt, reference)
        head = "task-" + receipt["taskId"]
        self.store.compare_and_swap(head, self.store.read(f"heads/{head}.json"), receipt)
        return receipt
