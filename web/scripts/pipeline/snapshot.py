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


def collector_continuity(collector, contract, coverage, store):
    """Verify saved collector history without conferring publication authority."""
    require(collector.get('enabled') is True and collector.get('contractSha256') == digest(contract)
            and collector.get('runId') == coverage['runId'], 'CONTINUITY_COLLECTOR_RUN_OR_POLICY_DIFFERS')
    require(collector.get('snapshotSha256') == digest({k:v for k,v in collector.items() if k != 'snapshotSha256'}),
            'CONTINUITY_COLLECTOR_HASH_DIFFERS')
    for key in ('runId','contractSha256','inventorySha256','successfulTasks','requiredTasks','complete','gapTaskIds'):
        require(collector.get('coverage',{}).get(key) == coverage.get(key), 'CONTINUITY_SOURCE_COVERAGE_DIFFERS')
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
    for item in collector.get('reviewQueue',[]):
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
        fact=store.read('facts/' + fid + '.json')
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
    return {'reviewQueue':queue,'pendingFacts':pending,'sourceSnapshotSha256':collector['snapshotSha256'],
            'sourceCheckedAt':collector['checkedAt']}


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
    for receipt in verified["receipts"]:
        for ref in receipt.get("heldClaims", []):
            held = json.loads(store.get(ref))
            queue.append({"factId": held["candidateSha256"], "supplierId": held["supplierId"],
                          "reason": held["reason"], "receiptSha256": ref["sha256"]})
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
    public_coverage["sources"] = inventory(contract, now, verified)
    public_coverage["automationEnabled"] = contract["publication"]["enabled"]
    public_coverage["overdueHours"] = contract["schedule"]["overdueHours"]
    public_coverage["scheduledAt"] = plan["scheduledAt"]
    public_coverage["lastCollectionAt"] = max(r["completedAt"] for r in verified["receipts"])
    observed_at = []
    for receipt in verified["receipts"]:
        for oid in receipt.get("observationIds", []):
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
    return {**result, "snapshotSha256": digest(result)}
