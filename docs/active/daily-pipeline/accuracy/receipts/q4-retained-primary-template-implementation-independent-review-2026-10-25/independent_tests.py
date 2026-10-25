import argparse,copy,gzip,hashlib,importlib.util,io,json,re,socket,sys,unittest
from pathlib import Path
from unittest.mock import patch
R=Path("/mnt/mac/Users/jessepike/code/projects/sec-market-finish-20261022")
P=Path("/var/tmp/smp-q4-retained-build-20261025")
O=Path("/var/tmp/smp-q4-retained-template-implementation-independent-review-20261025")
O.mkdir(exist_ok=True)
repo_mode="--repo-mode"in sys.argv
sys.path[:0]=[str(R/"web/scripts/pipeline"),str(R/"ops/ci")]
from contracts import canonical,digest
from storage import LocalStore
from discovery import IndexMarkup,IndexNode
source=R/"web/scripts/pipeline/q4_retained_primary_template.py"if repo_mode else P/"q4_retained_primary_template.py"
descriptor=R/"docs/active/daily-pipeline/accuracy/q4-retained-primary-template-descriptor-2026-10-25.json"if repo_mode else P/"q4-retained-primary-template-descriptor-2026-10-25.json"
spec=importlib.util.spec_from_file_location("q4_retained_independent_target",source);q=importlib.util.module_from_spec(spec);spec.loader.exec_module(q)
if not repo_mode:q.REPO=R
assert q.REPO==R
oldspec=importlib.util.spec_from_file_location("q4_actual_adapter",R/"docs/active/daily-pipeline/accuracy/receipts/q4-primary-qualification-actual-2026-10-25/audit_actual.py")
a=importlib.util.module_from_spec(oldspec);oldspec.loader.exec_module(a)
archive=Path("/var/tmp/smp-q4-primary-actual-40188161705-20261025/extracted")
entries,manifest=a.manifest(archive,"bb1c3da1399e89341badf80bba8642d7892f32ce2030bd57fc1d4c165e383e4d")
store=a.ReadOnlyArchive(archive,entries)
raw=descriptor.read_bytes();d=json.loads(raw);c=json.loads((R/"contracts/market.json").read_bytes())
seals={}
def seal(p):
 b=p.read_bytes();v={"sha256":digest(b),"bytes":len(b),"mtimeNs":p.stat().st_mtime_ns};assert seals.setdefault(str(p),v)==v;return b
for p in [source,descriptor,R/"docs/active/daily-pipeline/accuracy/q4-retained-primary-template-build-spec-2026-10-25.md",archive/"archive-manifest.json"]:seal(p)
pins=json.loads((R/"docs/active/daily-pipeline/accuracy/receipts/q4-primary-qualification-actual-2026-10-25/audit-config.json").read_bytes())["expectedCodePins"]
for p,h in pins.items():assert digest(seal(R/p))==h
for p in ["web/scripts/pipeline/source_qualification_origin.py","ops/ci/html_qualification_seed.py","web/scripts/pipeline/onboarding.py","web/scripts/pipeline/discovery.py","contracts/source-qualification-probes.json"]:seal(R/p)
mutations=0
class Cases(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.network=patch.object(socket.socket,"connect",side_effect=AssertionError("NO_NETWORK"));cls.local=patch.object(LocalStore,"__init__",side_effect=AssertionError("NO_FROZEN_LOCALSTORE"))
  cls.network.start();cls.local.start()
 @classmethod
 def tearDownClass(cls):cls.network.stop();cls.local.stop()
 def derive(self):return q.derive_report(c,store,raw)
 def test_actual_both_proposal_original_held_zero_authority(self):
  r=self.derive();v=q.verify_report(c,store,raw,r)
  self.assertTrue(v["proposalEvidenceComplete"]);self.assertEqual(r["originalReportAcceptedSamples"],0);self.assertFalse(r["originalReportProposalEvidenceComplete"])
  self.assertEqual([(s["records"],s["currentWindowRecords"])for s in r["streams"]],[(206,3),(323,4)])
  for k in ["qualified","semanticAdmission","coverageCredit","operationalIntake"]:self.assertIs(r[k],False)
  for k in ["qualifiedSources","sourceChecksCredited","modelCalls"]:self.assertEqual(r[k],0)
  self.assertEqual(r["facts"],[])
 def test_independent_actual_container_and_no_hidden_body_text(self):
  for row in d["sources"]:
   nodes=list(IndexMarkup(store.get(row["body"]).decode()).root.walk());t=row["template"]
   matches=[n for n in nodes if n.attrs.get("id")==t["bodyId"]];self.assertEqual(len(matches),1)
   body=matches[0];item=next(n for n in nodes if n.attrs.get("id")==t["itemId"]);self.assertIs(body.parent,item)
   def full(n):
    yield n
    for x in n.children:
     if isinstance(x,IndexNode):yield from full(x)
   hidden=[n for n in full(body)if n.tag in (q.INERT-{"script","style","template","noscript"}) or "hidden"in n.attrs or n.attrs.get("aria-hidden","").lower()=="true"or re.search(r"display\s*:\s*none|visibility\s*:\s*hidden",n.attrs.get("style",""),re.I)]
   self.assertEqual(hidden,[])
   for n in full(body):
    if n.tag in {"script","style","template","noscript"}:self.assertEqual(n.text,"")
   h=next(n for n in nodes if n.attrs.get("id")==t["headlineId"]);date=next(n for n in nodes if n.attrs.get("id")==t["dateId"])
   self.assertEqual(" ".join(h.text.split()),row["sample"]["title"]);self.assertEqual(" ".join(date.text.split()),"October 14, 2026")
 def test_machine_dates_and_written_dates_preserved(self):
  r=self.derive();jf,r7=[x["primaryShape"]for x in r["retainedSamples"]]
  self.assertEqual(jf["jsonLdIdentity"][0]["headline"],d["sources"][0]["sample"]["title"])
  self.assertEqual(jf["jsonLdIdentity"][0]["mainEntityOfPage"],{"@type":"WebPage","@id":d["sources"][0]["url"]})
  self.assertEqual(jf["jsonLdIdentity"][0]["datePublished"],"2026-10-14T15:05:00Z");self.assertEqual(jf["jsonLdIdentity"][0]["dateModified"],"2026-10-14T15:05:00Z")
  self.assertEqual(r7["dateMetadataState"],"unknown");self.assertEqual(r7["dateMetadata"],[]);self.assertEqual(r7["jsonLdIdentity"],[])
  for x in [jf,r7]:self.assertIsNone(x["canonical"]);self.assertIsNone(x["indexTimezone"]);self.assertEqual(x["indexDateLiteral"],"10/14/2026 16:05:00");self.assertEqual(x["identityProof"],"source_bound_response_and_og_url")
 def test_original_generic_helper_stays_held(self):
  from onboarding import _candidate_primary_shape
  for row in d["sources"]:
   with self.assertRaisesRegex(ValueError,"BOUNDED_CANDIDATE_PRIMARY_CANONICAL_DIFFERS"):_candidate_primary_shape(store.get(row["body"]),row["url"])
  old=json.loads(store.get(d["actualProof"]["record"]));self.assertEqual(old["diagnostic"]["acceptedSamples"],0);self.assertFalse(old["diagnostic"]["proposalEvidenceComplete"])
 def test_all_descriptor_leaf_mutations_reject_before_store(self):
  global mutations
  def paths(v,path=()):
   if isinstance(v,dict):
    for k,x in v.items():yield from paths(x,(*path,k))
   elif isinstance(v,list):
    for k,x in enumerate(v):yield from paths(x,(*path,k))
   else:yield path
  class NoRead:
   def get(self,*args):raise AssertionError("MUTATION_MUST_REJECT_BEFORE_STORE")
  for path in paths(d):
   z=copy.deepcopy(d);p=z
   for k in path[:-1]:p=p[k]
   p[path[-1]]="mutated";mutations+=1
   with self.assertRaises((ValueError,KeyError,TypeError)):q.derive_report(c,NoRead(),canonical(z))
 def test_descriptor_extra_missing_reordered_invalid_types(self):
  values=[]
  for k in d:
   z=copy.deepcopy(d);del z[k];values.append(canonical(z))
  z=copy.deepcopy(d);z["extra"]=1;values.append(canonical(z))
  z=copy.deepcopy(d);z["sources"].reverse();values.append(canonical(z))
  values += [b'{"kind":1,"kind":2}',b'{"kind":NaN}',b'{"kind":Infinity}',b'',b'[]']
  for b in values:
   with self.assertRaises((ValueError,KeyError,TypeError)):q.derive_report(c,object(),b)
 def test_record_plan_wrapper_raw_and_bodies_cannot_be_substituted(self):
  keys=[d["actualProof"][x]["key"]for x in ["record","plan"]]+[row[x]["key"]for row in d["sources"]for x in ["observation","rawObservation","body"]]
  for key in keys:
   class Altered:
    read=store.read
    def get(self,ref):
     b=store.get(ref);return b+b" "if ref["key"]==key else b
   with self.assertRaises(ValueError):q.derive_report(c,Altered(),raw)
 def test_bad_identity_hidden_nested_and_metadata_bytes_reject_at_pin(self):
  snippets=[b'<h3>Other supplier</h3>',b'<base href="https://evil.invalid/">',b'<template/>',b'<div hidden>Decoy title and body</div>',b'<time datetime=""></time>',b'<script type="application/ld+json">{"@type":"NewsArticle","datePublished":"tomorrow"}</script>',b'<script type="application/ld+json">{"@type":"NewsArticle","datePublished":"2026-10-14","datePublished":"2026-10-15"}</script>']
  for row in d["sources"]:
   for fragment in snippets:
    class Altered:
     read=store.read
     def get(self,ref):
      b=store.get(ref);return b+fragment if ref["key"]==row["body"]["key"]else b
    with self.assertRaises(ValueError):q.derive_report(c,Altered(),raw)
 def test_all_derived_report_fields_and_nested_fields_bound(self):
  r=self.derive()
  for key in r:
   z=copy.deepcopy(r);z[key]=None
   with self.assertRaises(ValueError):q.verify_report(c,store,raw,z)
  for index in [0,1]:
   for key in r["retainedSamples"][index]["primaryShape"]:
    z=copy.deepcopy(r);z["retainedSamples"][index]["primaryShape"][key]="changed"
    with self.assertRaises(ValueError):q.verify_report(c,store,raw,z)
  z=copy.deepcopy(r);z["extra"]=True
  with self.assertRaises(ValueError):q.verify_report(c,store,raw,z)
 def test_original_state_and_six_admissions_unchanged(self):
  from corrections import _index,group_review_policy,replay_admission
  gs=json.loads((R/"contracts/factual-corrections.json").read_bytes());stamp=json.loads((R/"web/src/data/tracker/factualCorrectionPolicy.json").read_bytes())
  for g in gs["groups"]:
   p=group_review_policy(g,c,gs["baseline"]["sha256"]);self.assertEqual(p,stamp["reviewPolicySha256ByGroup"][g["id"]]);ref=store.read(_index(g,p))["admission"];before=store.get(ref);replay_admission(g,ref,store,c,p,"2026-10-25T12:00:00Z");self.assertEqual(before,store.get(ref))
  snap=store.read("heads/dailySnapshot.json");self.assertEqual(len(snap["factProvenance"]),4);self.assertEqual(len(snap["reviewQueue"]),38);self.assertEqual(snap["coverage"]["validUntil"],"2026-10-26T15:55:27.307096+00:00")
  self.assertEqual(store.read("heads/budget-2026-10-25.json"),{"calls":80,"documents":38,"fetches":869});self.assertEqual(store.read("heads/gate-budget-2026-10-25.json"),{"attempts":2})
output=io.StringIO();suite=unittest.defaultTestLoader.loadTestsFromTestCase(Cases);result=unittest.TextTestRunner(stream=output,verbosity=2).run(suite)
log=output.getvalue().encode();name="post-copy"if repo_mode else"prototype";z=gzip.compress(log,mtime=0);(O/(name+"-tests.log.gz")).write_bytes(z)
store.unchanged()
for path in list(seals):seal(Path(path))
data={"schemaVersion":1,"phase":name,"verdict":"PASS"if result.wasSuccessful()and not result.skipped else"FAIL","tests":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"skips":len(result.skipped),"descriptorLeafMutationsRejected":mutations,"descriptorRawSha256":digest(raw),"descriptorCanonicalSha256":digest(d),"codeSha256":digest(source.read_bytes()),"placementOverride":"module.REPO only"if not repo_mode else None,"logicPatched":False,"archiveManifest":manifest,"archiveInputSeals":store.touched,"otherFileSeals":seals,"allSealsUnchanged":True,"rawLogSha256":digest(log),"rawLogBytes":len(log),"gzipSha256":digest(z),"gzipBytes":len(z),"byteExactRoundtrip":gzip.decompress(z)==log,"sourceRequests":0,"modelCalls":0,"actualArchiveWrites":0,"qualificationCredit":False}
(O/(name+"-result.json")).write_text(json.dumps(data,indent=2)+"\n")
print(log.decode());print(json.dumps({k:data[k]for k in ["phase","verdict","tests","failures","errors","skips","descriptorLeafMutationsRejected","codeSha256","descriptorRawSha256"]}))
raise SystemExit(not result.wasSuccessful())
