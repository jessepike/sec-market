import copy,json,socket,unittest,sys
from pathlib import Path
from unittest.mock import patch
R=Path("/mnt/mac/Users/jessepike/code/projects/sec-market-finish-20261022")
sys.path[:0]=[str(R/"web/scripts/pipeline"),str(R/"ops/ci")]
from contracts import canonical,digest
import q4_primary_qualification as q
from q4_press_list import parse_press_list
from test_q4_press_list import ReadOnlyD660,BODIES,AS_OF,row,encoded
from test_q4_primary_qualification import CaptureTests,ResponseFetcher,synthetic_html,PLAN,NOW
from storage import LocalStore
class Independent(unittest.TestCase):
 def setUp(self):
  self.f=CaptureTests();self.f.setUp();self.addCleanup(self.f.doCleanups)
 def sample(self,metadata="",change=None):
  f=self.f
  class F(ResponseFetcher):
   def fetch(this,source,url):
    this.body=synthetic_html(f,url,metadata)
    return super().fetch(source,url)
  r=f.capture(F(f,changes=change));f.replay(r);return r
 def test_absent_metadata_unknown(self):
  r=self.sample();self.assertTrue(r["proposalEvidenceComplete"]);self.assertEqual(r["results"][0]["primaryShape"]["dateMetadataState"],"unknown")
 def test_offset_calendar_unchanged(self):
  r=self.sample('<meta property="article:published_time" content="2026-10-14T23:30:00-12:00">');self.assertTrue(r["proposalEvidenceComplete"]);self.assertEqual(r["results"][0]["primaryShape"]["dateMetadata"][0]["value"],"2026-10-14T23:30:00-12:00")
 def test_invalid_supplied_jsonld_dates_hold(self):
  for v in ["tomorrow","",None,7,True,[],{}]:
   with self.subTest(v=v):
    r=self.sample('<script type="application/ld+json">'+json.dumps({"@type":"NewsArticle","datePublished":v})+'</script>');self.assertFalse(r["proposalEvidenceComplete"]);self.assertIsNotNone(r["results"][0]["body"])
 def test_empty_present_meta_time_hold(self):
  for m in ['<meta property="article:published_time" content="">','<time datetime=""></time>']:
   with self.subTest(m=m):self.assertFalse(self.sample(m)["proposalEvidenceComplete"])
 def test_conflicting_jsonld_hold(self):
  r=self.sample('<meta property="article:published_time" content="2026-10-14"><script type="application/ld+json">{"@type":"NewsArticle","datePublished":"2026-10-15"}</script>');self.assertFalse(r["proposalEvidenceComplete"])
 def test_report_tamper(self):
  r=self.sample()
  for mut in [lambda z:z.update(qualified=True),lambda z:z.update(sourceChecksCredited=1),lambda z:z.update(proposalEvidenceComplete=False),lambda z:z["streams"][0].update(asOf="2026-10-26T10:19:17Z")]:
   z=copy.deepcopy(r);mut(z)
   with self.assertRaises((ValueError,KeyError,TypeError)):self.f.replay(z)
 def test_response_mutations_hold(self):
  for c in [{"httpStatus":304},{"finalUrl":"https://investors.jfrog.com/x"},{"contentType":"application/json"},{"redirectDiagnostics":{"responses":[{"status":301}]}}]:
   with self.subTest(c=c):self.assertFalse(self.sample(change=c)["proposalEvidenceComplete"])
 def test_partial_not_complete(self):
  f=self.f
  def cb(x):
   if len(x.calls)==2:x.changes["httpStatus"]=403
  r=f.capture(ResponseFetcher(f,callback=cb));f.replay(r);self.assertEqual(r["acceptedSamples"],1);self.assertFalse(r["proposalEvidenceComplete"])
 def test_duplicate_mime_and_selfclosing_publication_markup_hold(self):
  for m in ['<script type="application/ld+json">{"@type":"NewsArticle","datePublished":"2026-10-15","datePublished":"2026-10-14"}</script>','<script type=" application/ld+json ">{"@type":"NewsArticle","datePublished":"2026-10-15"}</script>','<template/><meta property="article:published_time" content="2026-10-14">','<script type="application/ld+json"/>']:
   with self.subTest(m=m):self.assertFalse(self.sample(m)["proposalEvidenceComplete"])
 def test_nested_graph_valid_date_retained(self):
  m='<script type="application/ld+json">{"@graph":[{"@type":["NewsArticle"],"datePublished":"2026-10-14T16:05:00+05:30"}]}</script>'
  r=self.sample(m);self.assertTrue(r["proposalEvidenceComplete"]);self.assertEqual(r["results"][0]["primaryShape"]["dateMetadata"][0]["value"],"2026-10-14T16:05:00+05:30")
class Cold(unittest.TestCase):
 def setUp(self):
  self.s=ReadOnlyD660();self.addCleanup(self.s.assert_unchanged,self)
 def test_actual_graph(self):
  with patch.object(socket.socket,"connect",side_effect=AssertionError("socket denied")),patch.object(LocalStore,"__init__",side_effect=AssertionError("frozen constructor denied")):
   p=q.validate_plan(json.loads((R/"contracts/market.json").read_bytes()),self.s,PLAN.read_bytes())
  self.assertEqual([len(s["items"])for s in p["streams"]],[206,323]);self.assertEqual([len(s["currentWindowItems"])for s in p["streams"]],[3,4]);self.assertEqual([t["sample"]["recordSha256"]for t in p["targets"]],["b9a2d2e2000c8d5d8794b49e6b3d0552055ab4051c96c89fe20a027709297949","68f92eeb69a75ed608462310b72798f7efa0c8f9a1118d28712b3cce9716d8f5"]);self.assertGreaterEqual(len(self.s.touched),32)
 def test_quiet_does_not_drop_old_inventory(self):
  b=self.s.raw("objects/"+BODIES[0]);p=parse_press_list(b,"jfrog:official:1","2026-11-25T12:00:00Z");self.assertTrue(p["currentWindowQuiet"]);self.assertEqual(len(p["records"]),206)
 def test_malformed_duplicate_not_dropped(self):
  e=json.loads(self.s.raw("objects/"+BODIES[0]));b=copy.deepcopy(e["GetPressReleaseListResult"][0]);b["PressReleaseDate"]="02/30/2026 00:00:00";e["GetPressReleaseListResult"].append(b)
  with self.assertRaises(ValueError):parse_press_list(canonical(e),"jfrog:official:1",AS_OF)
 def test_future_unzoned_retained_not_quiet(self):
  for d in ["10/26/2026 01:00:00","11/20/2026 01:00:00"]:
   with self.subTest(d=d):
    p=parse_press_list(encoded([row(1,d),row(2,"09/01/2026 01:00:00")]),"jfrog:official:1",AS_OF);self.assertEqual(len(p["records"]),2);self.assertEqual(len(p["undeterminedWindowItems"]),1);self.assertFalse(p["currentWindowQuiet"])
 def test_six_original_admissions(self):
  from corrections import _index,group_review_policy,replay_admission
  c=json.loads((R/"contracts/market.json").read_bytes());gs=json.loads((R/"contracts/factual-corrections.json").read_bytes());st=json.loads((R/"web/src/data/tracker/factualCorrectionPolicy.json").read_bytes())
  with patch.object(socket.socket,"connect",side_effect=AssertionError("socket denied")),patch.object(LocalStore,"__init__",side_effect=AssertionError("frozen constructor denied")):
   for g in gs["groups"]:
    p=group_review_policy(g,c,gs["baseline"]["sha256"]);self.assertEqual(p,st["reviewPolicySha256ByGroup"][g["id"]]);ref=self.s.read(_index(g,p))["admission"];b=self.s.get(ref);replay_admission(g,ref,self.s,c,p,NOW);self.assertEqual(b,self.s.get(ref))
if __name__=="__main__":
 suite=unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromTestCase(Independent),unittest.defaultTestLoader.loadTestsFromTestCase(Cold)])
 result=unittest.TextTestRunner(verbosity=2).run(suite)
 raise SystemExit(not result.wasSuccessful())
