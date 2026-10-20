"""Offline, adversarial and recovery tests for the daily pipeline's real code."""
import copy
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import unittest
import hashlib
import io
import zipfile
from urllib.parse import urlsplit
from types import SimpleNamespace
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts/pipeline"
sys.path.insert(0, str(SCRIPTS))
from contracts import ContractError, canonical, digest, plan_run, validate_contract
from discovery import discover, xml_links
from engine import Pipeline
from fetcher import safe_url
from publication import health, prepare_release, publish, verify_acknowledgement
from storage import ConflictError, LocalStore
from validation import REVIEW_CHECKS, reconcile, verify_statement, eligible_fact_references
from reporting import inventory
from provenance import GitHubAuthority
from agents import ModelUnavailable, SubscriptionAgent

T = "2026-10-19T16:00:00Z"
QUOTE = "Fixture Vendor raised approximately $10 million on 2026-10-19."
URL = "https://example.invalid/releases/one"


def contract():
    return {"schemaVersion": 1, "version": "test-v1", "schedule": {"intervalHours": 24, "overdueHours": 30, "reconcileEveryRun": True, "maxWorkers": 1},
            "model": {"provider": "codex_subscription", "allowApiBilling": False, "maxDocumentsPerRun": 10, "maxCallsPerRun": 20, "maxDocumentChars": 30000, "timeoutSeconds": 5},
            "publication": {"enabled": False, "allowDegradedCoverage": True},
            "suppliers": [{"id": "fixture", "name": "Fixture Vendor", "kind": "private", "aliases": [], "sourceIds": ["official"], "requiredCategories": ["funding_valuation"], "requiredFamilies": ["official_announcements"]}],
            "sources": [{"id": "official", "supplierId": "fixture", "family": "official_announcements", "kind": "rss", "url": "https://example.invalid/feed.xml", "allowedHosts": ["example.invalid"], "registration": "verified", "required": True, "maxPages": 5, "scopePrefixes": ["/releases/"]}]}


def candidate():
    return {"supplierId": "fixture", "predicate": "funding", "valueText": QUOTE, "quote": QUOTE,
            "effectiveDate": "2026-10-19", "amount": "10000000", "currency": "USD", "qualifier": "approximately", "eventStatus": "reported", "scope": "company"}


def review(c, obs, policy):
    return {"result": "accepted", "candidateSha256": digest(c), "evidenceSha256": obs["body"]["sha256"], "policySha256": policy, "checks": {k: "pass" for k in REVIEW_CHECKS}}


class FakeFetcher:
    def __init__(self, store, pages=None):
        self.store = store
        self.pages = pages or {"https://example.invalid/feed.xml": b'<rss><channel><item><link>https://example.invalid/releases/one</link></item></channel></rss>', URL: f"<html><body>{QUOTE}</body></html>".encode()}

    def fetch(self, source, url, previous=None):
        body = self.pages[url]
        if isinstance(body, int):
            return {"requestedUrl": url, "fetchedAt": T, "status": "blocked", "httpStatus": body, "errorCode": f"HTTP_{body}"}
        return {"requestedUrl": url, "finalUrl": url, "fetchedAt": T, "status": "fetched", "httpStatus": 200, "body": self.store.put(body), "contentType": "text/html" if b"<html" in body else "application/xml"}


class FakeAgent:
    def __init__(self, empty=False):
        self.calls = 0
        self.empty = empty

    def extract(self, text, supplier):
        self.calls += 1
        return [] if self.empty else [candidate()]

    def review(self, text, c, obs, policy):
        self.calls += 1
        return review(c, obs, policy)

    def review_empty(self, text, supplier, obs, policy):
        self.calls += 1
        return {"noRelevantFacts": True, "evidenceSha256": obs["body"]["sha256"], "policySha256": policy}


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = LocalStore(self.temp.name)
        self.c = contract()

    def run_pipeline(self, c=None, agent=None, pages=None):
        return Pipeline(c or self.c, self.store, FakeFetcher(self.store, pages), agent or FakeAgent(), clock=lambda: T).run(T)

    def source_observation(self, text=QUOTE):
        body = self.store.put(text.encode())
        return {"observationId": "source-one", "sourceId": "official", "requestedUrl": URL, "body": body, "status": "fetched", "fetchedAt": T}

    def assert_bad_candidate(self, mutate, text=QUOTE):
        c = candidate(); mutate(c)
        obs = self.source_observation(text)
        with self.assertRaises(ContractError):
            verify_statement(c, obs, self.store, review(c, obs, digest(self.c)), self.c["suppliers"][0], digest(self.c))

    def test_canonical_hash_has_no_key_order_dependency(self):
        self.assertEqual(digest({"b": 2, "a": 1}), digest({"a": 1, "b": 2}))

    def test_daily_identity_uses_utc_even_when_input_has_an_offset(self):
        a=plan_run(self.c,'2026-10-20T00:30:00Z');b=plan_run(self.c,'2026-10-19T17:30:00-07:00')
        self.assertEqual(a['runId'],b['runId']);self.assertEqual(a['scheduledAt'],b['scheduledAt'])

    def test_expansion_has_no_hardcoded_supplier_limit(self):
        c = contract()
        for i in range(250):
            s = copy.deepcopy(c["suppliers"][0]); s.update(id=f"more-{i}", sourceIds=[]); c["suppliers"].append(s)
        validate_contract(c)
        self.assertEqual(len(plan_run(c, T)["supplierIds"]), 251)

    def test_paid_api_fallback_is_rejected(self):
        self.c["model"]["allowApiBilling"] = True
        with self.assertRaises(ContractError): validate_contract(self.c)

    def test_missing_family_stays_in_denominator(self):
        self.c["suppliers"][0]["requiredFamilies"].append("independent_reporting")
        result = self.run_pipeline()
        self.assertFalse(result["complete"])
        self.assertEqual((result["requiredTasks"], result["successfulTasks"]), (2, 1))

    def test_weekly_reconciliation_cannot_replace_daily(self):
        self.c["schedule"]["reconcileEveryRun"] = False
        with self.assertRaises(ContractError): validate_contract(self.c)

    def test_duplicate_supplier_is_rejected(self):
        self.c["suppliers"].append(copy.deepcopy(self.c["suppliers"][0]))
        with self.assertRaises(ContractError): validate_contract(self.c)

    def test_immutable_object_overwrite_is_rejected(self):
        self.store.write_once("receipts/one.json", {"a": 1})
        with self.assertRaises(ContractError): self.store.write_once("receipts/one.json", {"a": 2})

    def test_object_tamper_is_detected_on_read(self):
        ref = self.store.put(b"original")
        (self.store.root / ref["key"]).write_bytes(b"tampered")
        with self.assertRaises(ContractError): self.store.get(ref)

    def test_state_path_cannot_escape_store(self):
        with self.assertRaises(ContractError): self.store.write_once("../outside", b"x")

    def test_stale_release_cas_rejected(self):
        self.store.compare_and_swap("production", None, {"sequence": 1})
        with self.assertRaises(ConflictError): self.store.compare_and_swap("production", None, {"sequence": 2})

    def test_restore_is_independent_of_original_workspace(self):
        result = self.run_pipeline()
        # Keep the backup outside the traversed archive root.
        with tempfile.TemporaryDirectory() as dst:
            exported = self.store.export(dst)
            LocalStore.verify_export(dst, exported['manifestSha256'])
            restored = LocalStore(dst)
            head = restored.read("heads/latest-run.json")
            self.assertEqual(json.loads(restored.get(head["receipt"])), result)

    def test_backup_root_must_match_independent_receipt(self):
        self.store.put(b'evidence')
        with tempfile.TemporaryDirectory() as dst:
            self.store.export(dst)
            with self.assertRaises(ContractError): LocalStore.verify_export(dst,'0'*64)

    def test_lock_releases_after_worker_process_crash(self):
        code = "import sys,os;sys.path.insert(0,sys.argv[1]);from storage import LocalStore\nwith LocalStore(sys.argv[2]).lock('crash'):os._exit(0)"
        result = subprocess.run([sys.executable,'-c',code,str(SCRIPTS),self.temp.name],capture_output=True,timeout=5)
        self.assertEqual(result.returncode,0,result.stderr.decode())
        with self.store.lock('crash'): pass

    def test_kernel_lock_prevents_concurrent_publishers(self):
        with self.store.lock("production-publisher"):
            with self.assertRaises(ConflictError):
                with LocalStore(self.temp.name).lock("production-publisher"): pass

    def test_valid_source_fact_is_accepted(self):
        obs = self.source_observation()
        fact = verify_statement(candidate(), obs, self.store, review(candidate(), obs, digest(self.c)), self.c["suppliers"][0], digest(self.c))
        self.assertEqual(fact["assurance"], "source_statement_matched")

    def test_value_not_in_source_is_rejected(self):
        self.assert_bad_candidate(lambda c:c.update(amount="20000000"))

    def test_dropped_qualifier_is_rejected(self):
        self.assert_bad_candidate(lambda c:c.update(qualifier="exact"))

    def test_at_least_qualifier_cannot_be_dropped(self):
        text=QUOTE.replace("approximately", "at least")
        self.assert_bad_candidate(lambda c:c.update(quote=text,valueText=text,qualifier="exact"),text)

    def test_qualifier_changes_produce_distinct_assertions(self):
        c=candidate();obs=self.source_observation()
        a=verify_statement(c,obs,self.store,review(c,obs,digest(self.c)),self.c['suppliers'][0],digest(self.c))
        text=QUOTE.replace('approximately','at least');c.update(quote=text,valueText=text,qualifier='at_least');obs=self.source_observation(text)
        b=verify_statement(c,obs,self.store,review(c,obs,digest(self.c)),self.c['suppliers'][0],digest(self.c))
        self.assertNotEqual(a['factId'],b['factId'])

    def test_currency_mismatch_is_rejected(self):
        self.assert_bad_candidate(lambda c:c.update(currency="EUR"))

    def test_arr_cannot_become_revenue(self):
        self.assert_bad_candidate(lambda c:c.update(predicate="revenue", quote="Fixture Vendor reported approximately $10 million ARR on 2026-10-19.", valueText="Fixture Vendor reported approximately $10 million ARR on 2026-10-19."), "Fixture Vendor reported approximately $10 million ARR on 2026-10-19.")

    def test_future_acquisition_cannot_be_closed(self):
        text="Fixture Vendor plans to acquire a company on 2026-10-19."
        self.assert_bad_candidate(lambda c:c.update(predicate="acquisition", eventStatus="closed", quote=text, valueText=text, amount=None, currency=None), text)

    def test_unmatched_entity_is_rejected(self):
        self.assert_bad_candidate(lambda c:c.update(supplierId="another"))

    def test_missing_date_is_held(self):
        self.assert_bad_candidate(lambda c:c.update(effectiveDate=None))

    def test_unsupported_opinion_is_rejected(self):
        self.assert_bad_candidate(lambda c:c.update(predicate="financially_healthy"))

    def test_fabricated_quote_is_rejected(self):
        self.assert_bad_candidate(lambda c:c.update(quote="Invented statement about Fixture Vendor."))

    def test_stale_review_of_changed_value_is_rejected(self):
        obs=self.source_observation(); c=candidate(); proof=review(c,obs,digest(self.c)); c["eventStatus"]="announced"
        with self.assertRaises(ContractError): verify_statement(c,obs,self.store,proof,self.c["suppliers"][0],digest(self.c))

    def test_independent_reviewer_disagreement_is_held(self):
        obs=self.source_observation(); proof=review(candidate(),obs,digest(self.c));proof["checks"]["entity"]="unknown"
        with self.assertRaises(ContractError): verify_statement(candidate(),obs,self.store,proof,self.c["suppliers"][0],digest(self.c))

    def test_duplicate_wire_fact_has_one_identity(self):
        obs=self.source_observation(); a=verify_statement(candidate(),obs,self.store,review(candidate(),obs,digest(self.c)),self.c["suppliers"][0],digest(self.c))
        other={**obs,"observationId":"wire-copy"}
        b=verify_statement(candidate(),other,self.store,review(candidate(),other,digest(self.c)),self.c["suppliers"][0],digest(self.c))
        self.assertEqual(a["factId"],b["factId"])

    def test_concurrent_sources_share_document_validation_without_collisions(self):
        self.c['schedule']['maxWorkers']=2
        extra=copy.deepcopy(self.c['sources'][0]);extra['id']='wire-copy'
        self.c['sources'].append(extra);self.c['suppliers'][0]['sourceIds'].append('wire-copy')
        agent=FakeAgent();result=self.run_pipeline(agent=agent)
        self.assertTrue(result['complete']);self.assertEqual(result['successfulTasks'],2)
        self.assertEqual(agent.calls,2)
        self.assertEqual(len(list((self.store.root/'facts').glob('*.json'))),1)

    def test_full_cycle_is_idempotent_and_cache_saves_model_calls(self):
        first=self.run_pipeline(); self.assertTrue(first["complete"])
        agent=FakeAgent(); second=self.run_pipeline(agent=agent)
        self.assertTrue(second["complete"]); self.assertEqual(agent.calls,0)
        self.assertEqual(second["receipts"][0]["outcome"],"checked_no_change")
        self.assertEqual(len(list((self.store.root/"facts").glob('*.json'))),1)
        self.assertEqual(len(eligible_fact_references(second)),1)

    def test_budget_reservations_survive_restarts(self):
        self.c['model']['maxDocumentsPerRun']=1
        result=self.run_pipeline(agent=FakeAgent(empty=True));self.assertFalse(result['complete'])
        result=self.run_pipeline();self.assertFalse(result['complete'])
        self.assertEqual(result['receipts'][0]['errorCode'],'DOCUMENTS_BUDGET_EXHAUSTED')

    def test_failed_task_facts_remain_ineligible_until_successful_retry(self):
        class DisagreesSecond(FakeAgent):
            def extract(self,text,supplier): return [candidate(),candidate()]
            def review(self,text,c,obs,policy):
                self.calls+=1
                proof=review(c,obs,policy)
                if self.calls==2: proof['result']='rejected'
                return proof
        result=self.run_pipeline(agent=DisagreesSecond())
        self.assertFalse(result['complete']);self.assertEqual(eligible_fact_references(result),[])
        result=self.run_pipeline();self.assertTrue(result['complete'])
        self.assertEqual(len(eligible_fact_references(result)),1)

    def test_stored_review_is_rechecked_during_reconciliation(self):
        result=self.run_pipeline();ref=result['receipts'][0]['validatedFacts'][0]
        fact=json.loads(self.store.get(ref));(self.store.root/fact['review']['key']).write_bytes(b'corrupt')
        with self.assertRaises(ContractError):reconcile(plan_run(self.c,T),result['receipts'],self.c,T,self.store)

    def test_matrix_cannot_borrow_success_from_changed_contract(self):
        result=self.run_pipeline();self.c['version']='new-policy'
        rows=inventory(self.c,T,result)
        self.assertTrue(all(r['outcome']=='not_checked' for r in rows))

    def test_fresh_cli_verifier_reconstructs_a_run_from_durable_receipts(self):
        self.run_pipeline()
        path=self.store.root/'test-contract.json';path.write_bytes(canonical(self.c))
        result=subprocess.run([sys.executable,str(SCRIPTS/'cli.py'),'verify','--contract',str(path),'--state',self.temp.name,'--at',T],capture_output=True,text=True,timeout=5)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertTrue(json.loads(result.stdout)['complete'])
        self.assertEqual(len(list((self.store.root/'verifications').rglob('*.json'))),1)

    def test_cli_status_is_nonzero_for_missing_or_degraded_coverage(self):
        path=self.store.root/'test-contract.json';path.write_bytes(canonical(self.c))
        args=[sys.executable,str(SCRIPTS/'cli.py'),'status','--contract',str(path),'--state',self.temp.name,'--at',T]
        result=subprocess.run(args,capture_output=True,text=True,timeout=5)
        self.assertEqual(result.returncode,2);self.assertFalse(json.loads(result.stdout)['healthy'])
        self.run_pipeline(agent=FakeAgent(empty=True))
        result=subprocess.run(args,capture_output=True,text=True,timeout=5)
        self.assertEqual(result.returncode,2);self.assertFalse(json.loads(result.stdout)['healthy'])

    def test_empty_extraction_cannot_hide_clear_business_signal(self):
        result=self.run_pipeline(agent=FakeAgent(empty=True))
        self.assertFalse(result["complete"])
        self.assertIn("EMPTY_EXTRACTION",result["receipts"][0]["errorCode"])

    def test_explicit_quiet_document_has_no_change_receipt(self):
        pages=FakeFetcher(self.store).pages;pages[URL]=b'<html><body>Fixture Vendor publishes this contact directory for customers and its support team. No business announcement is included.</body></html>'
        result=self.run_pipeline(agent=FakeAgent(empty=True),pages=pages)
        self.assertTrue(result["complete"]);self.assertEqual(result["receipts"][0]["outcome"],"checked_no_change")

    def test_unverified_endpoint_never_earns_coverage(self):
        self.c["sources"][0]["registration"]="candidate"
        result=self.run_pipeline();self.assertFalse(result["complete"]);self.assertEqual(result["successfulTasks"],0)

    def test_blocked_endpoint_has_durable_failure_receipt(self):
        pages={self.c["sources"][0]["url"]:403}
        result=self.run_pipeline(pages=pages)
        self.assertFalse(result["complete"]);self.assertEqual(result["receipts"][0]["outcome"],"blocked")
        self.assertTrue(list((self.store.root/'runs'/result['runId']/'attempts').glob('*.json')))

    def test_missing_receipt_is_rejected(self):
        result=self.run_pipeline();p=plan_run(self.c,T)
        with self.assertRaises(ContractError):reconcile(p,[],self.c,T,self.store)

    def test_duplicate_receipt_is_rejected(self):
        result=self.run_pipeline();p=plan_run(self.c,T);r=result['receipts'][0]
        with self.assertRaises(ContractError):reconcile(p,[r,r],self.c,T,self.store)

    def test_contract_denominator_cannot_change_after_plan(self):
        p=plan_run(self.c,T);result=self.run_pipeline();self.c['version']='changed'
        with self.assertRaises(ContractError):reconcile(p,result['receipts'],self.c,T,self.store)

    def test_fresh_receipt_cannot_reuse_stale_source_check(self):
        result=self.run_pipeline();r=result['receipts'][0];r['completedAt']='2026-10-21T16:00:00Z'
        with self.assertRaises(ContractError):reconcile(plan_run(self.c,T),[r],self.c,'2026-10-21T16:00:00Z',self.store)

    def test_no_change_with_new_facts_is_rejected(self):
        result=self.run_pipeline();r=result['receipts'][0];r['outcome']='checked_no_change'
        with self.assertRaises(ContractError):reconcile(plan_run(self.c,T),[r],self.c,T,self.store)

    def test_pagination_budget_is_not_completeness(self):
        source=self.c['sources'][0];source['maxPages']=1
        first=b'<feed><link rel="next" href="https://example.invalid/feed2.xml"/><entry><link href="https://example.invalid/releases/one"/></entry></feed>'
        pages={source['url']:first}
        result=self.run_pipeline(pages=pages)
        self.assertFalse(result['complete']);self.assertEqual(result['receipts'][0]['errorCode'],'PAGINATION_BUDGET_EXHAUSTED')

    def test_xml_external_entities_are_rejected(self):
        with self.assertRaises(ContractError):xml_links(b'<!DOCTYPE a [<!ENTITY x SYSTEM "file:///etc/passwd">]><rss/>',URL)

    def test_rss_channel_pagination_is_retained(self):
        parsed=xml_links(b'<rss><channel><link rel="next" href="/page2.xml"/></channel></rss>',URL)
        self.assertEqual(parsed['indexes'],['https://example.invalid/page2.xml'])

    def test_private_and_unapproved_targets_are_rejected(self):
        def private(*a,**k):return [(socket.AF_INET,socket.SOCK_STREAM,6,'',('127.0.0.1',443))]
        with self.assertRaises(ContractError):safe_url(URL,['example.invalid'],private)
        with self.assertRaises(ContractError):safe_url('https://evil.invalid/x',['example.invalid'],private)

    def test_missing_or_stale_health_is_not_green(self):
        self.assertFalse(health(None,T)['healthy'])
        result=self.run_pipeline();self.assertFalse(health(result,'2026-10-21T16:00:00Z')['healthy'])

    def test_health_cannot_borrow_another_policys_success_or_ignore_gaps(self):
        result=self.run_pipeline()
        self.assertFalse(health(result,T,expected_contract='0'*64)['healthy'])
        result['gapTaskIds']=['unperformed'];self.assertFalse(health(result,T)['healthy'])

    def test_wrong_deployed_data_receipt_fails(self):
        manifest={'appRevision':'a'*40,'releaseId':'r1','snapshot':{'sha256':'b'*64},'artifact':{'sha256':'c'*64},'contractSha256':'d'*64}
        with self.assertRaises(ContractError):verify_acknowledgement(manifest,{'ready':True,'appRevision':'a'*40,'dataReleaseId':'wrong'})

    def test_automatic_cutover_is_disabled_by_default(self):
        with self.assertRaises(ContractError):publish(self.store,self.c,{},None)

    def test_live_failure_rolls_back_and_retains_last_good_head(self):
        self.c['publication']['enabled']=True
        previous={'releaseId':'old','sequence':1,'deploymentId':'old-deploy'}
        self.store.compare_and_swap('production',None,previous)
        manifest={'releaseId':'new','parentReleaseId':'old','sequence':2,'appRevision':'a'*40,'snapshot':{'sha256':'b'*64},'artifact':{'sha256':'c'*64},'contractSha256':'d'*64}
        class Adapter:
            rolled_back=False
            def production_paths_controlled(self):return True
            def stage(self,m):return 'new-deploy'
            def probe(self,d):return {'ready':True,'appRevision':'a'*40,'dataReleaseId':'new','snapshotSha256':'b'*64,'artifactSha256':'c'*64,'contractSha256':'d'*64}
            def promote(self,d):pass
            def probe_production(self):return {'ready':True,'dataReleaseId':'old' if self.rolled_back else 'wrong'}
            def rollback(self,d):self.rolled_back=True
        adapter=Adapter()
        with self.assertRaises(ContractError):publish(self.store,self.c,manifest,adapter)
        self.assertTrue(adapter.rolled_back);self.assertEqual(self.store.read('heads/production.json'),previous)
        self.assertIsNotNone(self.store.read('rollback-events/new.json'))

    def test_promote_timeout_also_rolls_back(self):
        self.c['publication']['enabled']=True
        self.store.compare_and_swap('production',None,{'releaseId':'old','sequence':1,'deploymentId':'old-deploy'})
        manifest={'releaseId':'new','parentReleaseId':'old','sequence':2,'appRevision':'a'*40,'snapshot':{'sha256':'b'*64},'artifact':{'sha256':'c'*64},'contractSha256':'d'*64}
        class Adapter:
            rolled_back=False
            def production_paths_controlled(self):return True
            def stage(self,m):return 'new-deploy'
            def probe(self,d):return {'ready':True,'appRevision':'a'*40,'dataReleaseId':'new','snapshotSha256':'b'*64,'artifactSha256':'c'*64,'contractSha256':'d'*64}
            def promote(self,d):raise TimeoutError('lost response after alias changed')
            def rollback(self,d):self.rolled_back=True
            def probe_production(self):return {'ready':True,'dataReleaseId':'old'}
        adapter=Adapter()
        with self.assertRaises(TimeoutError):publish(self.store,self.c,manifest,adapter)
        self.assertTrue(adapter.rolled_back)

    def test_subscription_runner_strips_infrastructure_and_api_credentials(self):
        calls=[]
        def runner(args,**kwargs):
            calls.append(args)
            self.assertNotIn('OPENAI_API_KEY',kwargs['env']);self.assertNotIn('VERCEL_TOKEN',kwargs['env']);self.assertNotIn('GITHUB_TOKEN',kwargs['env'])
            if args[1]=='login':return SimpleNamespace(returncode=0,stdout='Logged in using ChatGPT',stderr='')
            self.assertIn('--ignore-user-config',args);self.assertIn('--ignore-rules',args)
            self.assertEqual(args[args.index('--sandbox')+1],'read-only')
            for feature in ['shell_tool','apps','multi_agent','hooks','browser_use']:self.assertIn(feature,args)
            Path(args[args.index('--output-last-message')+1]).write_text('{"facts":[]}')
            return SimpleNamespace(returncode=0,stdout='',stderr='')
        with patch.dict(os.environ,{'OPENAI_API_KEY':'fixture-api','VERCEL_TOKEN':'fixture-vercel','GITHUB_TOKEN':'fixture-git'}):
            agent=SubscriptionAgent(self.c['model'],runner=runner)
            self.assertEqual(agent.extract('Quiet fixture',self.c['suppliers'][0]),[])
        self.assertEqual(len(calls),2)

    def test_api_authenticated_cli_is_not_used_as_subscription(self):
        def runner(*args,**kwargs):return SimpleNamespace(returncode=0,stdout='Logged in using an API key',stderr='')
        with self.assertRaises(ModelUnavailable):SubscriptionAgent(self.c['model'],runner=runner).call('probe',{})

    def test_github_provenance_requires_actual_run_and_exact_artifact(self):
        receipt={'githubRunId':12,'appRevision':'a'*40,'artifactSha256':'b'*64,'result':'pass','executedTests':7}
        archive=io.BytesIO()
        with zipfile.ZipFile(archive,'w') as z:z.writestr('gate-receipt.json',canonical(receipt))
        payload=archive.getvalue()
        run={'status':'completed','conclusion':'success','path':'.github/workflows/market-release-gate.yml','head_branch':'main','head_sha':'a'*40}
        meta={'workflow_run':{'id':12},'expired':False,'name':'daily-market-gate','digest':'sha256:'+hashlib.sha256(payload).hexdigest()}
        def runner(args,**kwargs):
            value=payload if args[-1].endswith('/zip') else canonical(run if 'actions/runs/' in args[-1] else meta)
            return SimpleNamespace(returncode=0,stdout=value,stderr=b'')
        authority=GitHubAuthority(runner=runner);supplied={**receipt,'githubArtifactId':34};artifact={'sha256':'b'*64}
        self.assertTrue(authority.verify_test_receipt(supplied,artifact))
        with self.assertRaises(ContractError):authority.verify_test_receipt({**supplied,'executedTests':9},artifact)
        run['head_branch']='unreviewed'
        with self.assertRaises(ContractError):authority.verify_test_receipt(supplied,artifact)

    def test_release_requires_current_coverage_and_exact_sec_claim_inventory(self):
        coverage=self.run_pipeline()
        self.c['certifiedCohorts']=[{'id':'sec','supplierIds':['fixture'],'claimGroups':['revenue'],'allRequired':True}]
        coverage['contractSha256']=digest(self.c)
        snapshot={'contractSha256':digest(self.c),'sha256':'b'*64,'allChangedClaimsVerified':True,'secCertification':{'required':1,'verified':1,'drift':0,'runId':coverage['runId'],'claimKeys':['fixture.revenue']}}
        artifact={'sha256':'c'*64};receipt={'result':'pass','executedTests':1,'artifactSha256':'c'*64,'appRevision':'a'*40,'snapshotSha256':'b'*64}
        authority=SimpleNamespace(verify_test_receipt=lambda *a:True)
        def prepare():return prepare_release(self.c,coverage,snapshot,'a'*40,artifact,receipt,None,T,authority)
        self.assertEqual(prepare()['sequence'],1)
        snapshot['secCertification']['claimKeys']=['wrong']
        with self.assertRaises(ContractError):prepare()
        snapshot['secCertification']['claimKeys']=['fixture.revenue'];coverage['checkedAt']='2026-10-16T16:00:00Z'
        with self.assertRaises(ContractError):prepare()

    def test_real_roster_has_all_74_and_honest_gaps(self):
        c=validate_contract(json.loads((SCRIPTS.parents[2]/'contracts/market.json').read_text()))
        p=plan_run(c,T)
        self.assertEqual(len(p['supplierIds']),74)
        self.assertTrue(any(t['kind']=='missing_discovery' for t in p['tasks']))

    def test_distribution_and_investor_sites_are_not_company_discovery(self):
        c=json.loads((SCRIPTS.parents[2]/'contracts/market.json').read_text())
        for s in c['sources']:
            if s['kind']=='citation':continue
            host=urlsplit(s['url']).hostname
            if host in {'www.prnewswire.com','www.globenewswire.com'}:self.assertEqual(s['family'],'release_distribution')
            if host in {'www.thomabravo.com','newsroom.accenture.com','www.levelblue.com'}:self.assertEqual(s['family'],'investor_acquirer')


if __name__=='__main__':unittest.main()
