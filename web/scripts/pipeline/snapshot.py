"""Materialize only independently rechecked facts into the site's data schema."""
import json
import re
from datetime import timedelta
from decimal import Decimal

from contracts import digest, instant, require, valid_hash
from validation import eligible_fact_references, normalize, reconcile, verified_partial_document_facts, verify_statement
from reporting import inventory

EVENT_TYPES = {"funding": "funding", "valuation": "funding", "revenue": "results", "arr": "results",
               "acquisition": "acquisition", "leadership_change": "exec-change", "restructuring": "restructuring",
               "layoff": "layoff", "debt": "debt", "shutdown": "shutdown", "late_filing": "late-filing"}


def continuity_object(store, sha):
    require(valid_hash(sha), 'CONTINUITY_OBJECT_HASH_REQUIRED')
    raw=store._path('objects/' + sha).read_bytes()
    require(digest(raw) == sha, 'CONTINUITY_OBJECT_HASH_DIFFERS')
    return json.loads(raw)


def document_marker(receipt, url):
    from retained_audit import reference
    ref = reference(receipt)
    return {'kind': 'source_document_revalidation',
            'factId': digest({'sourceId': receipt['sourceId'], 'url': url}), 'supplierId': receipt['supplierId'],
            'reason': 'SOURCE_DOCUMENT_REVALIDATION_REQUIRED', 'sourceId': receipt['sourceId'], 'url': url,
            'receiptSha256': ref['sha256'], 'processingManifest': receipt['processingManifest'],
            'origin': {'runId': receipt['runId'], 'taskId': receipt['taskId'], 'attemptId': receipt['attemptId'], 'receipt': ref}}


def verify_document_marker(item, store):
    from retained_audit import HistoricalStoreView, resolve_origin, verify_receipt, separated_details
    from separation import original_contract
    policy = original_contract(store, item['origin'])
    receipt = resolve_origin(store, item['origin'], policy, item['sourceId'])
    require(receipt.get('retainedAuditVersion') == 2 and item == document_marker(receipt, item['url']),
            'DOCUMENT_REVALIDATION_MARKER_PROVENANCE_DIFFERS')
    source = next(s for s in policy['sources'] if s['id'] == item['sourceId'])
    plan = store.read('runs/' + receipt['runId'] + '/plan.json')
    historical = HistoricalStoreView(store, receipt)
    verify_receipt(receipt, plan, policy, source, receipt['completedAt'], historical)
    details = separated_details(receipt, policy, source, receipt['completedAt'], historical)
    partitions = json.loads(store.get(receipt['processingManifest']))
    require(partitions == {'schemaVersion': 2, 'sourceId': source['id'], 'runId': receipt['runId'], **details['partitions']}
            and item['url'] in partitions['revalidationRequired'], 'DOCUMENT_REVALIDATION_PARTITION_DIFFERS')
    return receipt


def document_resolution(item, receipt, resolved_at, store):
    from retained_audit import HistoricalStoreView, resolve_origin, reference, verify_receipt, separated_details, current_transport, index_for
    from separation import original_contract
    original = verify_document_marker(item, store)
    origin = {'runId': receipt['runId'], 'taskId': receipt['taskId'], 'attemptId': receipt['attemptId'], 'receipt': reference(receipt)}
    policy = original_contract(store, origin)
    require(resolve_origin(store, origin, policy, receipt['sourceId']) == receipt and
            receipt['sourceId'] == item['sourceId'] and receipt['supplierId'] == item['supplierId'],
            'DOCUMENT_REVALIDATION_RESOLUTION_SUBJECT_DIFFERS')
    source = next(s for s in policy['sources'] if s['id'] == receipt['sourceId'])
    plan = store.read('runs/' + receipt['runId'] + '/plan.json')
    view = HistoricalStoreView(store, receipt)
    verify_receipt(receipt, plan, policy, source, resolved_at, view)
    details = separated_details(receipt, policy, source, resolved_at, view)
    partitions = json.loads(store.get(receipt['processingManifest']))
    require(partitions == {'schemaVersion': 2, 'sourceId': source['id'], 'runId': receipt['runId'], **details['partitions']}
            and item['url'] in partitions['processingReviewed'] and item['url'] not in partitions['revalidationRequired'],
            'DOCUMENT_REVALIDATION_CURRENT_REVIEW_REQUIRED')
    current = index_for(view).latest_observation(source['id'], item['url'])
    current_transport(current, {**source, 'overdueHours': policy['schedule']['overdueHours']}, resolved_at, view)
    require(instant(current['fetchedAt']) > instant(original['completedAt']), 'DOCUMENT_REVALIDATION_NEW_PRIMARY_CHECK_REQUIRED')
    record = {'schemaVersion': 1, 'kind': 'source_document_revalidation_resolution', 'marker': item,
              'currentOrigin': origin, 'currentProcessingManifest': receipt['processingManifest'],
              'sourceObservationId': current['observationId'], 'sourceObservationSha256': digest(current),
              'resolvedAt': resolved_at}
    return {**record, 'resolutionSha256': digest(record)}


def verify_document_resolution(record, store):
    from retained_audit import resolve_origin
    from separation import original_contract
    policy = original_contract(store, record['currentOrigin'])
    receipt = resolve_origin(store, record['currentOrigin'], policy, record['marker']['sourceId'])
    require(document_resolution(record['marker'], receipt, record['resolvedAt'], store) == record,
            'DOCUMENT_REVALIDATION_RESOLUTION_DIFFERS')
    return record


def collector_continuity(collector, contract, coverage, store):
    """Verify saved collector history without conferring publication authority."""
    require(collector.get('enabled') is True and collector.get('contractSha256') == digest(contract)
            and collector.get('runId') == coverage['runId'], 'CONTINUITY_COLLECTOR_RUN_OR_POLICY_DIFFERS')
    require(collector.get('snapshotSha256') == digest({k:v for k,v in collector.items() if k != 'snapshotSha256'}),
            'CONTINUITY_COLLECTOR_HASH_DIFFERS')
    for key in ('runId','contractSha256','inventorySha256','successfulTasks','requiredTasks','complete','gapTaskIds'):
        require(collector.get('coverage',{}).get(key) == coverage.get(key), 'CONTINUITY_SOURCE_COVERAGE_DIFFERS')
    if coverage.get('schemaVersion') == 2:
        for key in ('schemaVersion', 'measure', 'intake', 'processing', 'historicalReview', 'tasks'):
            require(collector.get('coverage', {}).get(key) == coverage.get(key), 'CONTINUITY_SOURCE_MEASURE_DIFFERS')
    suppliers={s['id']:s for s in contract['suppliers']}
    sources={s['id']:s for s in contract['sources']}
    def observation_for(supplier, oid, reference):
        require(valid_hash(oid), 'CONTINUITY_OBSERVATION_ID_REQUIRED')
        observed=store.read('observations/' + oid + '.json')
        require(observed and observed.get('observationId') == oid and observed.get('body') == reference and
                sources.get(observed.get('sourceId'),{}).get('supplierId') == supplier,
                'CONTINUITY_SOURCE_PROVENANCE_DIFFERS')
        store.get(reference)
        return observed
    queue=[]
    def saved_fact(fid):
        ref = collector.get('factProvenance', {}).get(fid)
        fact = json.loads(store.get(ref)) if ref else store.read('facts/' + fid + '.json')
        require(fact and fact.get('factId') == fid, 'CONTINUITY_FACT_PROVENANCE_REQUIRED')
        return fact
    for item in collector.get('reviewQueue',[]):
        if item.get('kind') == 'source_document_revalidation':
            verify_document_marker(item, store)
            queue.append(dict(item))
            continue
        if item.get('reason') == 'ROUND_DETAILS_HELD_EVENT_ONLY' and not item.get('receiptSha256'):
            fact = saved_fact(item.get('factId', ''))
            require(fact.get('predicate') == 'funding' and fact.get('supplierId') == item.get('supplierId') and
                    any(event.get('id') == 'EV-daily-' + fact['factId'] for event in collector.get('events', [])) and
                    not re.search(r'\b(Series [A-Z](?:-\d)?|pre-seed|seed)\b', fact['quote'], re.I),
                    'CONTINUITY_EVENT_DETAIL_HOLD_DIFFERS')
            # The event loop below independently replays this exact accepted fact and evidence.
            queue.append(dict(item))
            continue
        held=continuity_object(store,item.get('receiptSha256'))
        require(held.get('candidateSha256') == item.get('factId') and digest(held.get('candidate')) == item['factId']
                and held.get('supplierId') == item.get('supplierId') and held.get('reason') == item.get('reason'),
                'CONTINUITY_HELD_CLAIM_DIFFERS')
        observation_for(held['supplierId'],held['sourceObservationId'],held['evidence'])
        review=json.loads(store.get(held['review']))
        require(review.get('candidateSha256') == held['candidateSha256']
                and review.get('evidenceSha256') == held['evidence']['sha256']
                and review.get('policySha256') == held['policySha256'], 'CONTINUITY_HELD_REVIEW_PROVENANCE_DIFFERS')
        queue.append(dict(item))
    evidence={e['id']:e for e in collector.get('evidence',[])}
    require(len(evidence) == len(collector.get('evidence',[])), 'CONTINUITY_DUPLICATE_EVIDENCE')
    pending=[]
    for event in collector.get('events',[]):
        fid=event.get('id','').removeprefix('EV-daily-')
        require(valid_hash(fid) and event['id'] == 'EV-daily-' + fid, 'CONTINUITY_EVENT_ID_INVALID')
        fact=saved_fact(fid)
        require(fact and fact.get('factId') == fid and fact.get('assurance') == 'source_statement_matched'
                and fact.get('supplierId') in suppliers and fact.get('predicate') in EVENT_TYPES,
                'CONTINUITY_FACT_PROVENANCE_REQUIRED')
        require(len(fact.get('evidence',[])) == 1, 'CONTINUITY_FACT_EVIDENCE_REQUIRED')
        observed=observation_for(fact['supplierId'],fact['sourceObservationId'],fact['evidence'][0])
        candidate={k:fact[k] for k in ('supplierId','predicate','valueText','quote','effectiveDate','amount',
                                     'currency','qualifier','eventStatus','scope')}
        review=json.loads(store.get(fact['review']))
        reproduced=verify_statement(candidate,observed,store,review,suppliers[fact['supplierId']],fact['policySha256'])
        require(reproduced == fact, 'CONTINUITY_FACT_REPLAY_DIFFERS')
        source=sources[observed['sourceId']]
        rank=1 if source['family'] in ('official_announcements','filing_documents') else 4
        require(event == {'id':'EV-daily-' + fid,'supplierId':fact['supplierId'],'date':fact['effectiveDate'],
                         'type':EVENT_TYPES[fact['predicate']],'text':normalize(fact['valueText']),
                         'evidenceIds':['DAILY-' + fid],'rung':rank}, 'CONTINUITY_EVENT_CONTENT_DIFFERS')
        linked=[]
        for eid in event['evidenceIds']:
            saved=evidence.get(eid)
            require(saved and saved.get('publicationDate') == fact['effectiveDate']
                    and saved.get('excerpt') == normalize(fact['quote'])
                    and saved.get('canonicalUrl') == observed.get('finalUrl',observed['requestedUrl'])
                    and saved.get('interpretation') == '' and saved.get('retrieval',{}).get('sha256') == observed['body']['sha256']
                    and saved['retrieval'].get('fetchedAt') == observed['fetchedAt']
                    and saved['retrieval'].get('locator') == fact['quote'], 'CONTINUITY_EVENT_EVIDENCE_DIFFERS')
            linked.append(saved)
        pending.append({'factId':fid,'supplierId':fact['supplierId'],
                        'reason':'CURRENT_POLICY_REVIEW_REQUIRED' if fact['policySha256'] != digest(contract)
                                 else 'CURRENT_RECEIPT_ADMISSION_REQUIRED',
                        'event':event,'evidence':linked,'fact':fact,'sourceObservation':observed,
                        'sourceSnapshotSha256':collector['snapshotSha256'],
                        'sourceSnapshotCheckedAt':collector['checkedAt']})
    result = {'reviewQueue':queue,'pendingFacts':pending,'sourceSnapshotSha256':collector['snapshotSha256'],
              'sourceCheckedAt':collector['checkedAt']}
    if 'documentReviewResolutions' in collector:
        result['documentReviewResolutions'] = [verify_document_resolution(record, store)
                                               for record in collector['documentReviewResolutions']]
    return result


def money(fact):
    symbols = {"USD": "$", "EUR": "€", "GBP": "£", "JPY": "¥", "CAD": "C$", "AUD": "A$"}
    amount = Decimal(str(fact["amount"]))
    text = format(amount, ",f").rstrip("0").rstrip(".") if amount % 1 else format(amount, ",.0f")
    prefix = {"exact": "", "approximately": "approximately ", "at_least": "at least ", "more_than": "more than ", "up_to": "up to "}[fact["qualifier"]]
    return prefix + symbols[fact["currency"]] + text


def review_resolution(store, contract, held_sha, fact_ref, policy, resolved_at):
    """Reproduce the exact accepted statement before closing one raw held receipt."""
    instant(resolved_at)
    held = continuity_object(store, held_sha)
    fact = json.loads(store.get(fact_ref))
    require(valid_hash(policy) and fact.get('policySha256') == policy
            and fact.get('candidateSha256') == held.get('candidateSha256') == digest(held.get('candidate'))
            and fact.get('supplierId') == held.get('supplierId')
            and fact.get('evidence') == [held.get('evidence')], 'RESOLUTION_EXACT_CLAIM_REQUIRED')
    observed = store.read('observations/' + fact['sourceObservationId'] + '.json')
    original = store.read('observations/' + held['sourceObservationId'] + '.json')
    sources = {s['id']:s for s in contract['sources']}
    supplier = next(s for s in contract['suppliers'] if s['id'] == fact['supplierId'])
    for observation in (observed, original):
        source = sources.get((observation or {}).get('sourceId'), {})
        require(observation and observation.get('body') == held['evidence']
                and source.get('supplierId') == fact['supplierId']
                and source.get('family') in ('official_announcements','release_distribution','investor_acquirer','filing_documents'),
                'RESOLUTION_SOURCE_PROOF_REQUIRED')
    review = json.loads(store.get(fact['review']))
    reproduced = verify_statement(held['candidate'], observed, store, review, supplier, policy)
    require(reproduced == fact, 'RESOLUTION_ACCEPTED_FACT_DIFFERS')
    original_review = json.loads(store.get(held['review']))
    require(original_review.get('candidateSha256') == held['candidateSha256']
            and original_review.get('evidenceSha256') == held['evidence']['sha256']
            and original_review.get('policySha256') == held['policySha256'], 'RESOLUTION_HELD_REVIEW_DIFFERS')
    record = {'heldReceiptSha256':held_sha, 'candidateSha256':held['candidateSha256'],
              'candidate':held['candidate'], 'supplierId':fact['supplierId'], 'admittedFact':fact_ref,
              'admittedReview':fact['review'], 'evidence':fact['evidence'], 'policySha256':policy,
              'sourceObservationId':fact['sourceObservationId'], 'originalSourceObservationId':held['sourceObservationId'],
              'sourceFetchedAt':observed['fetchedAt'], 'originalSourceFetchedAt':original['fetchedAt'],
              'effectiveDate':held['candidate']['effectiveDate'], 'resolvedAt':resolved_at}
    return {**record, 'resolutionSha256':digest(record)}


def build_snapshot(contract, plan, coverage, store, now, baseline=None, previous=None, continuity=None):
    # Recompute from raw receipts and evidence, not a worker's completion flag.
    verified = reconcile(plan, coverage["receipts"], contract, now, store)
    require(verified["runId"] == coverage["runId"], "Snapshot run differs")
    age = (instant(now) - instant(coverage["checkedAt"])).total_seconds() / 3600
    require(0 <= age <= contract["schedule"]["overdueHours"], "Snapshot coverage is stale/future")
    suppliers = {s["id"]: s for s in contract["suppliers"]}
    baseline = {s["id"]: s for s in (baseline or [])}
    sources = {s["id"]: s for s in contract["sources"]}
    previous = previous if (previous or {}).get("enabled") else {}
    events = {e["id"]: e for e in previous.get("events", [])}
    fact_provenance = dict(previous.get('factProvenance', {}))
    evidence = {e["id"]: e for e in previous.get("evidence", [])}
    updates = dict(previous.get("supplierUpdates", {}))
    update_dates = dict(previous.get("supplierUpdateDates", {}))
    queue, facts_by_id, sec_records = list(previous.get("reviewQueue", [])), {}, {}
    resolutions = {}
    for record in previous.get('resolvedReviews', []):
        reproduced = review_resolution(store, contract, record['heldReceiptSha256'], record['admittedFact'],
                                       record['policySha256'], record['resolvedAt'])
        require(reproduced == record, 'RESOLUTION_RECORD_DIFFERS')
        resolutions[record['heldReceiptSha256']] = record
    pending={p['factId']:p for p in previous.get('pendingFacts',[])}
    if continuity:
        queue.extend(continuity['reviewQueue'])
        for item in continuity['pendingFacts']:
            if item['event']['id'] not in events:
                pending[item['factId']]=item
    document_resolutions = {}
    for record in [*previous.get('documentReviewResolutions', []), *(continuity or {}).get('documentReviewResolutions', [])]:
        verify_document_resolution(record, store)
        document_resolutions[digest(record['marker'])] = record
    for item in queue:
        if item.get('kind') == 'source_document_revalidation':
            verify_document_marker(item, store)
    for receipt in verified["receipts"]:
        for ref in receipt.get("heldClaims", []):
            held = json.loads(store.get(ref))
            queue.append({"factId": held["candidateSha256"], "supplierId": held["supplierId"],
                          "reason": held["reason"], "receiptSha256": ref["sha256"]})
        if receipt.get('retainedAuditVersion') == 2:
            partitions = __import__('json').loads(store.get(receipt['processingManifest']))
            for url in partitions['revalidationRequired']:
                if not any(item.get('kind') == 'source_document_revalidation' and
                           item['sourceId'] == receipt['sourceId'] and item['url'] == url for item in queue):
                    queue.append(document_marker(receipt, url))
    current_receipts = {r.get('sourceId'): r for r in verified['receipts'] if r.get('retainedAuditVersion') == 2}
    for item in queue:
        if item.get('kind') != 'source_document_revalidation' or digest(item) in document_resolutions:
            continue
        receipt = current_receipts.get(item['sourceId'])
        if receipt is not None:
            try:
                document_resolutions[digest(item)] = document_resolution(item, receipt, now, store)
            except (ValueError, KeyError, TypeError):
                pass
    queue = [item for item in queue if item.get('kind') != 'source_document_revalidation' or
             digest(item) not in document_resolutions]
    references = [*eligible_fact_references(verified), *verified_partial_document_facts(plan, verified, contract, now, store)]
    for reference in references:
        fact = json.loads(store.get(reference))
        if fact.get("assurance") == "sec_rederived":
            if fact["predicate"] == "sec_revenue_snapshot":
                sec_records[fact["supplierId"]] = fact["value"]
            continue
        require(fact.get("review") and fact.get("assurance") == "source_statement_matched", "Unreviewed fact in snapshot")
        observation = store.read(f"observations/{fact['sourceObservationId']}.json")
        source = sources[observation["sourceId"]]
        # A single independent-media report cannot establish the published fact.
        if source["family"] not in ("official_announcements", "release_distribution", "investor_acquirer", "filing_documents"):
            queue.append({"factId": fact["factId"], "supplierId": fact["supplierId"], "reason": "PRIMARY_SOURCE_REQUIRED"})
            continue
        require(fact["supplierId"] in suppliers and fact["predicate"] in EVENT_TYPES, "Unknown supplier/predicate")
        require(fact["scope"] == "company" or suppliers[fact["supplierId"]]["kind"] == "segment", "Claim entity scope requires review")
        # Prefer company/filing evidence to a distributed copy for the same assertion.
        rank = 1 if source["family"] in ("official_announcements", "filing_documents") else 4
        old = facts_by_id.get(fact["factId"])
        if old is None or rank < old[0]:
            facts_by_id[fact["factId"]] = (rank, fact, observation, source)
    for rank, fact, observation, source in sorted(facts_by_id.values(), key=lambda x: (x[1]["effectiveDate"], x[1]["factId"])):
        fid, sid, date = fact["factId"], fact["supplierId"], fact["effectiveDate"]
        if contract.get('collection', {}).get('mode') == 'daily_intake_with_separate_history':
            from retained_audit import reference
            fact_provenance[fid] = reference(fact)
        eid = f"DAILY-{fid}"
        evidence[eid] = {"id": eid, "title": f"{suppliers[sid]['name']}: reported {fact['predicate'].replace('_', ' ')}",
                         "organization": suppliers[sid]["name"] if rank == 1 else source["allowedHosts"][0],
                         "publicationDate": date, "economicPeriod": f"Statement dated {date}",
                         "canonicalUrl": observation.get("finalUrl", observation["requestedUrl"]), "excerpt": normalize(fact["quote"]),
                         "sourceClass": "FILING" if source["family"] == "filing_documents" else "OFFICIAL",
                         "interpretation": "", "limitations": "Source statement matched. This does not certify undisclosed information.",
                         "conflictingEvidenceIds": [], "artifactLabel": "Archived source statement", "tags": ["daily", sid],
                         "retrievedAt": observation["fetchedAt"][:10],
                         "retrieval": {"finalUrl": observation.get("finalUrl", observation["requestedUrl"]), "sha256": observation["body"]["sha256"], "fetchedAt": observation["fetchedAt"], "locator": fact["quote"]}}
        events[f"EV-daily-{fid}"] = {"id": f"EV-daily-{fid}", "supplierId": sid, "date": date,
                                           "type": EVENT_TYPES[fact["predicate"]], "text": normalize(fact["valueText"]), "evidenceIds": [eid], "rung": rank}
        pending.pop(fid,None)  # Only current independently validated admission resolves quarantine.
        if fact.get('policySha256') == digest(contract):
            for item in queue:
                sha = item.get('receiptSha256')
                if not sha or sha in resolutions or item.get('factId') != fact.get('candidateSha256'):
                    continue
                held = continuity_object(store, sha)
                # A date, quote, supplier, or archived-body difference keeps the hold open.
                if (held.get('candidateSha256') != fact.get('candidateSha256')
                        or held.get('supplierId') != sid or fact.get('evidence') != [held.get('evidence')]):
                    continue
                resolutions[sha] = review_resolution(store, contract, sha, store.put(fact), digest(contract), now)
        field, value = None, None
        if fact["predicate"] in ("arr", "revenue") and fact["amount"] is not None and suppliers[sid]["kind"] not in ("public", "segment"):
            # Keep reported ARR distinct; never replace certified GAAP quarter fields.
            field = "headlineMetric"
            value = {"label": "ARR" if fact["predicate"] == "arr" else "Reported revenue", "value": money(fact), "period": f"Reported {date}", "evidenceIds": [eid]}
        elif fact["predicate"] == "funding" and fact["amount"] is not None:
            stage = re.search(r"\b(Series [A-Z](?:-\d)?|pre-seed|seed)\b", fact["quote"], re.I)
            existing = updates.get(sid, {}).get("lastRound") or baseline.get(sid, {}).get("lastRound", {})
            if stage and date > existing.get("date", ""):
                field, value = "lastRound", {"date": date, "stage": stage[0], "amount": money(fact), "evidenceIds": [eid]}
            elif not stage:
                queue.append({"factId": fid, "supplierId": sid, "reason": "ROUND_DETAILS_HELD_EVENT_ONLY"})
        if field:
            key = f"{sid}.{field}"
            if date > update_dates.get(key, ""):
                updates[sid] = {**updates.get(sid, {}), field: value}
                update_dates[key] = date
            elif date == update_dates.get(key) and updates[sid].get(field) != value:
                # Two same-date assertions must not silently overwrite each other.
                updates[sid].pop(field, None)
                queue.append({"factId": fid, "supplierId": sid, "reason": "CONFLICTING_SAME_DATE_FIELD"})
    tasks_by_supplier = {}
    for task in plan["tasks"]:
        if task["required"]:
            tasks_by_supplier.setdefault(task["supplierId"], []).append(task["taskId"])
    gaps = set(verified["gapTaskIds"])
    public_coverage = {k: v for k, v in verified.items() if k != "receipts"}
    public_coverage["sources"] = inventory(contract, plan["scheduledAt"], verified)
    public_coverage["automationEnabled"] = contract["publication"]["enabled"]
    public_coverage["overdueHours"] = contract["schedule"]["overdueHours"]
    public_coverage["scheduledAt"] = plan["scheduledAt"]
    public_coverage["lastCollectionAt"] = max(r["completedAt"] for r in verified["receipts"])
    observed_at = []
    for receipt in verified["receipts"]:
        from separation import enabled as separated
        from retained_audit import bounded
        source = sources.get(receipt.get('sourceId'))
        observation_ids = receipt.get('observationIds', [])
        if separated(contract) and bounded(source, contract):
            observation_ids = __import__('json').loads(store.get(receipt['itemManifest']))['observations']
        for oid in observation_ids:
            observed = store.read(f"observations/{oid}.json")
            if observed and observed["status"] in ("fetched", "not_modified", "retained_immutable"):
                observed_at.append(instant(observed.get("verifiedAt", observed["fetchedAt"])))
    public_coverage["validUntil"] = (min(observed_at) + timedelta(hours=contract["schedule"]["overdueHours"])).isoformat() if observed_at else None
    public_coverage["suppliers"] = [{"id": sid, "name": supplier["name"], "required": len(tasks_by_supplier[sid]),
                                      "checked": sum(t not in gaps for t in tasks_by_supplier[sid]),
                                      "complete": not any(t in gaps for t in tasks_by_supplier[sid])}
                                     for sid, supplier in suppliers.items()]
    public_coverage["categories"] = {s["id"]: [{"category": category, "state": "source_checks_complete" if not any(t in gaps for t in tasks_by_supplier[s["id"]]) else "incomplete", "claimAssurance": "displayed facts retain their own source and date"} for category in s["requiredCategories"]] for s in contract["suppliers"]}
    result = {"schemaVersion": 1, "enabled": True, "runId": verified["runId"], "checkedAt": now,
              "contractSha256": digest(contract), "supplierUpdates": updates, "supplierUpdateDates": update_dates,
              "events": sorted(events.values(), key=lambda e: (e["date"], e["id"])), "evidence": list(evidence.values()),
              "coverage": public_coverage, "reviewQueue": list({(q["factId"], q["reason"]): q for q in queue
                  if q.get('receiptSha256') not in resolutions}.values()), "secRecords": sec_records,
              "parentSnapshotSha256": digest(previous) if previous else None}
    if pending or 'pendingFacts' in previous or continuity:
        result['pendingFacts']=sorted(pending.values(),key=lambda p:p['factId'])
    if resolutions or 'resolvedReviews' in previous:
        result['resolvedReviews'] = sorted(resolutions.values(), key=lambda r:r['heldReceiptSha256'])
    if document_resolutions or 'documentReviewResolutions' in previous or (continuity or {}).get('documentReviewResolutions'):
        result['documentReviewResolutions'] = sorted(document_resolutions.values(), key=lambda r:r['resolutionSha256'])
    if fact_provenance:
        result['factProvenance'] = fact_provenance
    return {**result, "snapshotSha256": digest(result)}
