from pathlib import Path
import ast,difflib,gzip,hashlib,io,json,sys,tempfile
R=Path('/mnt/mac/Users/jessepike/code/projects/sec-market-finish-20261022');W=Path('/mnt/mac/Users/jessepike/.codex/worktrees/q4-normal-intake/sec-market');O=Path('/var/tmp/smp-q4-normal-intake-test-delta-independent-20261025');P=R/'docs/active/daily-pipeline/accuracy/receipts/q4-two-source-normal-intake-postcopy-2026-10-25';OUT=O/'handback';OUT.mkdir(exist_ok=True);Q=OUT/'receipts';Q.mkdir(exist_ok=True)
sys.path[:0]=[str(R/'web/scripts/pipeline'),str(R/'ops/ci')]
from contracts import canonical,digest
from onboarding import validate_qualification_probe_plan
seals={}
def sha(b):return hashlib.sha256(b).hexdigest()
def need(v,msg):
 if not v:raise AssertionError(msg)
def pin(p):
 b=p.read_bytes();return {'sha256':sha(b),'bytes':len(b),'mtimeNs':p.stat().st_mtime_ns}
def raw(p):
 v=pin(p);need(seals.setdefault(str(p),v)==v,'INPUT_CHANGED');return p.read_bytes()
def read(p):return json.loads(raw(p))
old=raw(P/'original-sealed-test.py');new=raw(R/'ops/ci/test_q4_normal_intake.py');need(sha(old)=='8cd91a00d1bd5a714ec81aa06b4b428edb58bf83a3ac20a7373f1b67ccb832a9' and len(old)==23761,'OLD_TEST_PIN');need(sha(new)=='c6bcd4939a10d4fe38d7bf350a4f30df8e0bd7c288ea2d78c5b7e1b314c197f1' and len(new)==24493 and new==raw(W/'ops/ci/test_q4_normal_intake.py'),'NEW_TEST_PIN_BOTH_WORKTREES')
method='test_H_operational_probe_plan_rejects_under_J_and_disabled_J_is_exact'
def split_method(b):
 t=ast.parse(b);node=next(n for n in ast.walk(t) if isinstance(n,ast.FunctionDef) and n.name==method);lines=b.decode().splitlines(keepends=True);return ''.join(lines[:node.lineno-1]),''.join(lines[node.lineno-1:node.end_lineno]),''.join(lines[node.end_lineno:])
a,b,c=split_method(old);x,y,z=split_method(new);need(a==x and c==z,'NON_METHOD_TEXT_CHANGED');diff=''.join(difflib.unified_diff(old.decode().splitlines(keepends=True),new.decode().splitlines(keepends=True),fromfile='original/ops/ci/test_q4_normal_intake.py',tofile='selected-J/ops/ci/test_q4_normal_intake.py'));need(diff.encode()==raw(P/'test-only.diff'),'TEST_DIFF_DIFFERS')
verification=R/'docs/active/daily-pipeline/accuracy/receipts/q4-two-source-normal-intake-2026-10-25/verification.json';v=read(verification);need(sha(raw(verification))=='79ce23bb08ab202534489f3f5610f744181c54b409cd7c185641e6ee3ac4c156','ORIGINAL_VERIFICATION_REWRITTEN')
for root in [R,W]:
 for rel,p in v['files'].items():
  actual=raw(root/rel);expected={'sha256':sha(new),'bytes':len(new)} if rel=='ops/ci/test_q4_normal_intake.py' else p;need(sha(actual)==expected['sha256'] and len(actual)==expected['bytes'],'83_PIN_SCOPE:'+str(root/rel))
 for ext in ['md','json']:
  rel='docs/active/daily-pipeline/accuracy/q4-two-source-normal-intake-implementation-2026-10-25.'+ext;need(raw(R/rel)==raw(W/rel),'WORKER_REPORTS_DIFFER')
oldreview=R/'docs/active/daily-pipeline/accuracy/q4-two-source-normal-intake-implementation-independent-review-2026-10-25'
for ext,h in [('md','4ac09668641909ede89dd2f4a04ed823765436025b91b4de7262300243ee3c7d'),('json','292559f18fb0c8e5556f621823395e5634b86ee91bd1d6dd7d280b582446c734')]:need(sha(raw(Path(str(oldreview)+'.'+ext)))==h,'ORIGINAL_REVIEW_REWRITTEN')
oldreceipts=R/'docs/active/daily-pipeline/accuracy/receipts/q4-two-source-normal-intake-implementation-independent-review-2026-10-25';index=read(oldreceipts/'index.json');need(sha(raw(oldreceipts/'index.json'))=='1c2846aefe3505cea4d86275ce2d36470639cc549159a1289179daf991104870','ORIGINAL_REVIEW_INDEX_REWRITTEN')
for name,p in index['files'].items():b0=raw(oldreceipts/name);need(sha(b0)==p['sha256'] and len(b0)==p['bytes'],'ORIGINAL_REVIEW_RECEIPT_REWRITTEN')
historical=raw(R/'docs/active/daily-pipeline/accuracy/receipts/seven-newsroom-disabled-restoration-2026-10-25/disabled-plan.json');need(len(historical)==173 and sha(historical)=='ad1c5cc234fe4fa69cbceb5370ac74825a37dc80b08528ca908d14b1352e53b4','HISTORY_AD1')
active=R/'contracts/source-qualification-probes.json';proposed=R/'docs/active/daily-pipeline/accuracy/q4-normal-intake-disabled-J-plan-2026-10-25.json';need(raw(active)==raw(proposed)==raw(W/'docs/active/daily-pipeline/accuracy/q4-normal-intake-disabled-J-plan-2026-10-25.json') and sha(raw(active))=='ef9ee1bab6cfe6202b62e8d5605393f045d11fd64bd42ea1bcea769de15c8a01','SELECTED_J_PLAN')
J=read(R/'contracts/market.json');need(digest(J)=='47b9f22636f0e6ea79cf830ae90aab844d8f554d44110a5bb08f29f00266593a','POLICY_J')
class NoRead:
 def __init__(self):self.reads=0
 def get(self,*a):self.reads+=1;raise AssertionError('STORE_GET_DURING_PLAN_CHECK')
 def read(self,*a):self.reads+=1;raise AssertionError('STORE_READ_DURING_PLAN_CHECK')
store=NoRead();hpath=O/'historical-ad1-H.json';hpath.write_bytes(historical)
try:validate_qualification_probe_plan(J,store,hpath)
except ValueError as e:historical_reason=str(e)
else:raise AssertionError('H_PLAN_ACCEPTED_UNDER_J')
checked=validate_qualification_probe_plan(J,store,active);need(store.reads==0 and checked['maxRequests']==0 and checked['plan']['sources']==[] and checked['rawSha256']==sha(raw(active)),'BEFORE_READ_REJECTION_OR_J_POSITIVE')
worker=read(P/'postcopy-verification.json');need(sha(raw(P/'postcopy-verification.json'))=='db3fed5ca5fba1e7d6155ce00e14d5a1fef78ac2227ad104c9793b861dc63c66','POSTCOPY_PROOF_PIN')
# Retain exact initial failure and worker/current-configuration logs alongside reviewer runs.
source=Path('/var/tmp/smp-q4-normal-intake-postcopy-20261025');failure=raw(source/'focused-initial.log');need(b'Ran 14 tests' in failure and b'FAILED (failures=1)' in failure and b'AssertionError: ValueError not raised' in failure and method.encode() in failure,'INITIAL_FAILURE_NOT_RETAINED')
full=raw(source/'full-ops-final.log');focused=raw(source/'focused-final.log');js=raw(source/'js.log');own=raw(O/'independent-focused.log');ownjs=raw(O/'independent-js.log');need(b'Ran 935 tests' in full and full.rstrip().endswith(b'OK'),'SELECTED_J_FULL_OPS');need(b'Ran 14 tests' in focused and focused.rstrip().endswith(b'OK') and b'Ran 14 tests' in own and own.rstrip().endswith(b'OK'),'FOCUSED');need(b'# pass 2' in js and b'# fail 0' in js and b'# pass 2' in ownjs and b'# fail 0' in ownjs,'JS')
# The latest-head preservation evidence is separately attributed, never substituted for the old sealed review.
latest=read(P/'latest-actual-preflight.json');head_supplement=read(P/'head-selection-supplement.json')
for name,p in seals.items():need(pin(Path(name))==p,'FINAL_INPUT_SEAL_CHANGED:'+name)
for name,p in [('original-sealed-test.py',P/'original-sealed-test.py'),('test-only.diff',P/'test-only.diff'),('run-focused.py',O/'run-focused.py'),('review-delta.py',O/'review-delta.py')]: (Q/name).write_bytes(p.read_bytes())
logs={}
for name,b0 in [('focused-initial.log',failure),('worker-full-ops-final.log',full),('worker-focused-final.log',focused),('worker-js.log',js),('independent-focused.log',own),('independent-js.log',ownjs)]:
 out=io.BytesIO()
 with gzip.GzipFile(filename='',fileobj=out,mode='wb',mtime=0,compresslevel=9)as f:f.write(b0)
 packed=out.getvalue();need(gzip.decompress(packed)==b0,'LOSSLESS_GZIP');(Q/(name+'.gz')).write_bytes(packed);logs[name]={'rawSha256':sha(b0),'rawBytes':len(b0),'gzipSha256':sha(packed),'gzipBytes':len(packed),'byteExactRoundTrip':True}
receiptindex={'schemaVersion':1,'files':{p.name:{k:v for k,v in pin(p).items() if k!='mtimeNs'} for p in sorted(Q.iterdir())}};(Q/'index.json').write_text(json.dumps(receiptindex,indent=2)+'\n')
report={'schemaVersion':1,'verdict':'PASS','scope':'One test-method fixture correction following the authorized local J-disabled plan selection; prior implementation review remains sealed.','testPath':'ops/ci/test_q4_normal_intake.py','oldTest':{'sha256':sha(old),'bytes':len(old)},'newTest':{'sha256':sha(new),'bytes':len(new)},'diffSha256':sha(diff.encode()),'onlyMethodChanged':method,'other82OriginalPinsExactBothWorktrees':True,'selectedConfigurationUnderTest':'finish checkout only; isolated historical operational plan is excluded from the implementation copy','originalWorkerVerificationSha256':sha(raw(verification)),'originalImplementationReviewUnchanged':True,'originalImplementationReviewReceiptsUnchanged':True,'historicalHPlan':{'sha256':sha(historical),'bytes':len(historical),'rejection':historical_reason},'activeLocalJPlan':{'sha256':sha(raw(active)),'bytes':len(raw(active)),'maxRequests':0,'sources':[]},'directIndependentStoreReads':store.reads,'checks':{'initialSelectedJFocusedFailure':{'tests':14,'failures':1,'reason':'The old test treated the now-correct active J-disabled plan as an H fixture.'},'independentFocused':{'passed':14,'failed':0,'networkDenied':True,'frozenLocalStoreInitializationDenied':True},'independentJavaScript':{'passed':2,'failed':0},'workerSelectedJFullOps':{'passed':935,'failed':0},'workerSelectedJFocused':{'passed':14,'failed':0},'workerSelectedJJavaScript':{'passed':2,'failed':0}},'workerPostcopyReceipt':{'path':str(P/'postcopy-verification.json').removeprefix('/mnt/mac'),**pin(P/'postcopy-verification.json')},'latestPreservationEvidence':{'preflight':{'path':str(P/'latest-actual-preflight.json').removeprefix('/mnt/mac'),**pin(P/'latest-actual-preflight.json')},'headSelectionSupplement':{'path':str(P/'head-selection-supplement.json').removeprefix('/mnt/mac'),**pin(P/'head-selection-supplement.json')},'attribution':'Worker authenticated current retained archive and separately sealed the 8588-prefix subset versus canonical 8605 all-heads-except-budget/lease comparison. This test-only review does not redo that full archive audit.'},'inputSealsBeforeAfter':seals,'allInputSealsUnchanged':True,'logs':logs,'receiptIndex':{k:v for k,v in pin(Q/'index.json').items() if k!='mtimeNs'},'reviewerCoreOrPackageEdits':0,'reviewerSourceRequests':0,'reviewerModelCalls':0,'reviewerRealArchiveSessionBudgetWrites':0,'actualJOperationalCredit':False,'publicationCredit':False}
stem='q4-two-source-normal-intake-test-delta-independent-review-2026-10-25';(OUT/(stem+'.json')).write_text(json.dumps(report,indent=2)+'\n');md=f'''# Independent review of the selected-J test fixture correction

Verdict: **PASS**. I recommend accepting the one-method test correction with the local J-disabled selection. Runtime, policy, package and origin code are unchanged.

The test is `/Users/jessepike/code/projects/sec-market-finish-20261022/ops/ci/test_q4_normal_intake.py`. Its original sealed bytes are `{sha(old)}`, 23,761 bytes; the corrected bytes are `{sha(new)}`, 24,493 bytes. The same corrected bytes exist in the isolated worker checkout. The diff changes only `{method}`. All other 82 original implementation pins match in both checkouts.

The initial selected-J run is retained: 14 tests ran and one failed because the old test expected the active plan to remain H. The corrected test writes the exact 173-byte historical disabled-H fixture to a temporary path and pins SHA-256 `ad1c5cc234fe4fa69cbceb5370ac74825a37dc80b08528ca908d14b1352e53b4`. It still rejects that H plan under J before any store read. Separately, it checks the actual selected plan against the reviewed disabled-J proposal, SHA-256 `ef9ee1bab6cfe6202b62e8d5605393f045d11fd64bd42ea1bcea769de15c8a01`, then validates its zero-request/empty-source operation. A direct reviewer check confirms both outcomes with zero store reads.

The reviewer reran **14 focused Python tests and two JavaScript tests**, all passing in the finish checkout with the actual selected J configuration. Network access and frozen-archive LocalStore initialization were denied for the Python run. The worker's retained selected-J runs also pass **935 operational tests, 14 focused tests and two JavaScript tests**. Full-suite execution is attributed to the worker; the initial failure remains beside the successful receipts.

The original 83-file verification, implementation reports, independent review and all original review receipts remain sealed. This new review records the original-to-corrected test hash separately. The current-head preservation preflight and its later head-selection clarification remain separate worker evidence; no historical archive or review proof was overwritten.

No source/model request, runtime or package edit, real session/archive/budget write, actual J collection or public publication occurred in this review. Local J selection and passing tests grant no operational or freshness credit.
''';(OUT/(stem+'.md')).write_text(md)
print(json.dumps({'verdict':'PASS','markdown':{'path':str(OUT/(stem+'.md')),**pin(OUT/(stem+'.md'))},'json':{'path':str(OUT/(stem+'.json')),**pin(OUT/(stem+'.json'))},'receiptIndex':pin(Q/'index.json'),'allWritesOutsideCheckout':True}))
