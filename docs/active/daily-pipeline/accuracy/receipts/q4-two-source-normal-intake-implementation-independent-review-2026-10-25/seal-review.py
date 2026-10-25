from pathlib import Path
import copy,gzip,hashlib,io,json,struct
from urllib.parse import urlsplit
R=Path('/mnt/mac/Users/jessepike/.codex/worktrees/q4-normal-intake/sec-market');O=Path('/var/tmp/smp-q4-exact-j-independent-20261025');D=O/'handback';D.mkdir(exist_ok=True);Q=D/'receipts';Q.mkdir(exist_ok=True)
def sha(b):return hashlib.sha256(b).hexdigest()
def canonical(v):return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def digest(v):return sha(canonical(v))
def need(v,msg):
 if not v:raise AssertionError(msg)
def pin(p):
 b=p.read_bytes();return {'sha256':sha(b),'bytes':len(b),'mtimeNs':p.stat().st_mtime_ns}
def read(p):return json.loads(p.read_bytes())
py=read(O/'python-review.json');js=read(O/'javascript-review.json');edge=read(O/'lease-edge-review.json');need(js['verdict']==edge['verdict']=='PASS' and py['negativeCount']==62 and js['negativeCount']==27 and edge['negativeCount']==17,'ACTUAL_RESULTS')
verification=R/'docs/active/daily-pipeline/accuracy/receipts/q4-two-source-normal-intake-2026-10-25/verification.json';w=read(verification);need(pin(verification)==py['workerVerification']|{'path':str(verification)} if False else pin(verification)['sha256']==py['workerVerification']['sha256'],'WORKER_HANDOFF_CHANGED')
for rel,v in w['files'].items():need(all(pin(R/rel)[k]==v[k] for k in ['sha256','bytes']),'CORE_FILE_CHANGED:'+rel)
for name,v in py['inputSealsBeforeAfter'].items():need(pin(Path(name))==v,'CONSUMED_INPUT_CHANGED:'+name)
# Independently reconstruct the complete two origin objects and inventory refs from accepted proof records.
J=read(R/'contracts/market.json');H=read(R/'contracts/html-qualification-seeds'/py['H']/('contracts__'+py['H']+'.json'));pack=read(R/w['seed']['path']);files={e['key']:(R/e['path']).read_bytes() for e in pack['files']};proofref={'key':'objects/eb82ff6f74ffd0461a74cc6590e3cb1ef52adae2be698f4421b904c79d25d714','sha256':'eb82ff6f74ffd0461a74cc6590e3cb1ef52adae2be698f4421b904c79d25d714','bytes':7571};descriptor={'key':'objects/0223ae2af8878aecf73b5b6a5665d7840d592e7e299470e44bd31cedf7a12c1b','sha256':'0223ae2af8878aecf73b5b6a5665d7840d592e7e299470e44bd31cedf7a12c1b','bytes':6105};proof=json.loads(files[proofref['key']]);expected=copy.deepcopy(H);authority=[]
for n,(i,sid,count) in enumerate([(34,'jfrog:official:1',206),(52,'rapid7:official:1',323)]):
 row=J['sources'][i];adapter={**H['sources'][i],'kind':'q4_press_list','registration':'verified','url':row['url']};stream=proof['streams'][n];initial=files[stream['initialBody']['key']];need(sha(initial)==stream['initialBody']['sha256'] and len(initial)==stream['initialBody']['bytes'],'INITIAL_BODY_PIN');apirows=json.loads(initial)['GetPressReleaseListResult'];urls=sorted('https://'+urlsplit(row['url']).hostname+r['LinkToDetailPage'] for r in apirows);need(len(urls)==len(set(urls))==stream['records']==count and stream['sourceId']==sid,'ACTUAL_FULL_INVENTORY')
 inv={'schemaVersion':1,'kind':'q4_qualification_inventory_manifest','sourceId':sid,'descriptor':descriptor,'proof':proofref,'sourceResultIndex':n,'streamSha256':stream['streamSha256'],'items':urls};invraw=canonical(inv);ref={'key':'objects/'+sha(invraw),'sha256':sha(invraw),'bytes':len(invraw)};need(files[ref['key']]==invraw,'INDEPENDENT_INVENTORY_MANIFEST')
 origin={'schemaVersion':1,'kind':'bounded_q4_press_qualification','originalContract':{'key':'contracts/'+py['H']+'.json','sha256':py['H'],'bytes':len(canonical(H))},'descriptor':descriptor,'proof':proofref,'sourceResultIndex':n,'originalSourceSha256':digest(H['sources'][i]),'adapterSha256':digest(adapter),'inventoryManifest':ref};need(canonical(row)==canonical({**adapter,'qualificationOrigin':origin}),'INDEPENDENT_COMPLETE_ORIGIN');expected['sources'][i]={**adapter,'qualificationOrigin':origin};authority.append({'sourceId':sid,'sourceIndex':i,'originalSourceSha256':digest(H['sources'][i]),'adapterSha256':digest(adapter),'inventoryManifest':ref,'documents':count})
need(canonical(expected)==canonical(J) and digest(expected)==py['J']==js['J'],'FULL_INDEPENDENT_J')
# Authenticate lossless worker logs and retained render pairs without any network request.
logs={};worker_receipts=verification.parent
for name,v in w['logs'].items():
 p=worker_receipts/v['gzipFile'];b=p.read_bytes();raw=gzip.decompress(b);need(sha(b)==v['gzipSha256'] and len(b)==v['gzipBytes'] and sha(raw)==v['rawSha256'] and len(raw)==v['rawBytes'],'WORKER_LOG:'+name);logs[name]={'compressed':pin(p),'rawSha256':sha(raw),'rawBytes':len(raw)}
actual_replay=worker_receipts/w['actualReplay']['file'];need(all(pin(actual_replay)[k]==w['actualReplay'][k] for k in ['sha256','bytes']),'WORKER_ACTUAL_REPLAY');renders=[]
for row in w['renderComparison']:
 p=Path('/mnt/mac'+row['path']);prior=Path('/mnt/mac'+row['priorPath']);b=p.read_bytes();old=prior.read_bytes();need(b==old and sha(b)==row['sha256']==row['priorSha256'],'RENDER_PAIR');need(b[:8]==b'\x89PNG\r\n\x1a\n','PNG');dimensions=list(struct.unpack('>II',b[16:24]));need(dimensions==row['dimensions'],'RENDER_DIMENSIONS');renders.append({'kind':row['kind'],'width':row['width'],'path':row['path'],'priorPath':row['priorPath'],'sha256':sha(b),'bytes':len(b),'dimensions':dimensions,'byteIdentical':True,'viewAttribution':'Root separately reported viewing all four new images.'})
# Retain exact tested metadata before the worker applies any later documentation-only command correction.
(Q/'tested-worker-verification.json').write_bytes(verification.read_bytes())
for name in ['review.py','review.mjs','lease-edges.py','seal-review.py','python-review.log','lease-edge.log','javascript-review.json','cross-language-input.json']:(Q/name).write_bytes((O/name).read_bytes())
compressed={}
for name in ['python-review.json','lease-edge-review.json']:
 raw=(O/name).read_bytes();buf=io.BytesIO()
 with gzip.GzipFile(filename='',fileobj=buf,mode='wb',mtime=0,compresslevel=9)as f:f.write(raw)
 b=buf.getvalue();need(gzip.decompress(b)==raw,'GZIP');(Q/(name+'.gz')).write_bytes(b);compressed[name]={'rawSha256':sha(raw),'rawBytes':len(raw),'gzipFile':name+'.gz','gzipSha256':sha(b),'gzipBytes':len(b),'lossless':True}
coverage={
'J01':'Independent complete H-to-J reconstruction and inverse, 557 obligations.',
'J02':'Python/JavaScript whole-policy and type/order mutations reject.',
'J03':'Actual accepted descriptor/proof pins and complete original graph replay.',
'J04':'Old three origins and original H resolver outputs are canonical-byte identical under J.',
'J05':'Historical H fixtures remain fixed; operational H plan rejects under J.',
'J06':'Both new origins replay all 529 records as inventory only; original held report stays immutable.',
'J07':'All 55 package payloads hash-check; fixed old H seed replay, existing-byte/path rejection.',
'J08':'Real J context/require_lease/import code; synthetic remote ack, wrong identity/owner/expiry/race reject.',
'J09':'Two unmocked valid imports, idempotence; post-preflight interruption after ten writes retries to 55.',
'J10':'Independent Python/JavaScript full zero-credit baseline reconstruction and whole prior chain.',
'J11':'Honestly resealed forged credit/time/history mutations reject in both languages.',
'J12':'All six actual admissions and group policy hashes replay without model or reservation.',
'J13':'Ordinary Pipeline and real Fetcher full 200 with 206/323 actual arrays; variable-length 205 discovery.',
'J14':'Ordinary conditional requests return genuine synthetic 304 with prior 200 IDs/body and newer check clock.',
'J15':'Status/MIME/body/source/URL failure checks remain incomplete; frozen and origin evidence persists.',
'J16':'Original observation clock wins over a later verifier clock; genuine later 304 has its own new check.',
'J17':'Middle-row malformed, duplicate, order, unsafe/date and extra/continuation envelopes reject; old parser remains exact.',
'J18':'Only valid nonempty older-only data is quiet; empty and future uncertainty do not assert quiet.',
'J19':'Written dates and unknown timezone remain; today/next-day/far-future boundaries/anomalies stay visible.',
'J20':'Normal returned retained inventories contain every Q4 origin row; frozen four refs/38 holds and old dates remain exact.',
'J21':'Real SubscriptionAgent/GuardedRunner at 80 calls/38 docs: two cycles total six fetches, zero model calls, 39 docs.',
'J22':'Real quota/deadline denial and 1 logical/3 physical retry test; generic cancellation/day paths are unchanged and covered by retained full suite.',
'J23':'Eleven protected core modules byte-match base7a1aee7b; stable handback files and frozen archive identities stay exact.',
'J24':'Retained worker full suites/SEC80/render receipts authenticated; live J activation, scheduling and publication remain unexercised.'}
index={'schemaVersion':1,'files':{f.name:{k:v for k,v in pin(f).items() if k!='mtimeNs'} for f in sorted(Q.iterdir()) if f.is_file()}};(Q/'index.json').write_text(json.dumps(index,indent=2)+'\n')
report={'schemaVersion':1,'verdict':'PASS','findings':[],'reviewedWorktree':str(R).removeprefix('/mnt/mac'),'base':w['worktreeBase'],'H':py['H'],'J':py['J'],'completeIndependentSourceOrigins':authority,'seed':{'manifest':w['seed'],'files':55,'payloadBytes':4742948},'independentResults':{'pythonResultGroups':len(py['results']),'pythonRejectionAndGuardChecks':62,'javascriptMutationChecks':27,'additionalLeaseImportRejections':17,'totalRejectionAndGuardChecks':106,'leaseInterruptedImportRetry':edge['interruptedImportSuccessfulRetry'],'normalBudget':py['results'][7]['detail'],'ordinaryRetry':py['results'][-1]['detail'],'globalCorrectionStamp':js['globalCorrectionStamp']},'caseCoverage':coverage,'workerEvidenceAttribution':{'verification':py['workerVerification'],'suiteChecks':w['checks'],'logs':logs,'actualReplay':{'path':str(actual_replay),**pin(actual_replay)},'renderPairs':renders,'fullSuitesRerunByReviewer':False},'protectedCodeUnchanged':py['protectedCodeUnchanged'],'authenticatedArchiveReuse':py['authenticatedArchiveReuse'],'inputSealSummary':{'mainReviewConsultedFiles':len(py['inputSealsBeforeAfter']),'allByteSizeMtimeSealsUnchanged':True,'all48245FrozenFileIdentitiesUnchanged':True,'fullHashReusedFromPreviouslyAuthenticatedReceipt':True},'completeSealReceipts':compressed,'receiptIndex':{k:v for k,v in pin(Q/'index.json').items() if k!='mtimeNs'},'limits':['No actual J collection, import acknowledgement, scheduled run or publication occurred in this review.','Source transport, login status and remote acknowledgement are synthetic fixtures; real parser, Fetcher, ordinary Pipeline task, guards, importer and lease checks execute.','The 985/80/38 ledger is the frozen test fixture, not current activation capacity. Root must use the actual immediate activation ledger and archive.','The six-fetch ceiling is incremental logical work for two sources, not all other obligations or physical retry attempts.','The H operational plan still in the worker base must not land with J. Root must select the reviewed exact disabled-J plan.','Generic engine, Page, model, semantic-context, cancellation and day controls were not modified; their full-suite results are retained worker evidence.','The worker has a queued documentation-only correction of the literal replay command; this review retains the exact tested prior metadata.'], 'reviewerSourceRequests':0,'reviewerModelCalls':0,'reviewerRealArchiveSessionBudgetWrites':0,'reviewerRepoWrites':0,'qualificationCredit':False,'freshnessCredit':False,'publicationCredit':False,'nextDecision':'Accept the implementation for root integration and separately guarded J activation; require actual J ordinary intake and future scheduled/public receipts before granting operational credit.'}
stem='q4-two-source-normal-intake-implementation-independent-review-2026-10-25';(D/(stem+'.json')).write_text(json.dumps(report,indent=2)+'\n')
md=f'''# Independent review of exact-J ordinary Q4 intake

Verdict: **PASS**. No material findings remain. I recommend accepting this implementation for the root's integration and separately guarded activation. Actual J collection and publication still need their own receipts.

The reviewed worktree is `/Users/jessepike/.codex/worktrees/q4-normal-intake/sec-market`, base `{w['worktreeBase']}`. H is `{py['H']}` and the independently reconstructed J is `{py['J']}`. Only the JFrog and Rapid7 source rows change. All 557 obligations remain.

## Independent results

The reviewer reconstructed both complete source-origin objects from the accepted proof records and full 206/323 URL inventories, then reconstructed the whole J object and its inverse. Python and JavaScript reject unlisted policy, field, type, order and authority substitutions. The old Ping, Delinea and Sonatype origins still resolve through the original H validation with exact original output. The new predecessors replay all 529 records and grant inventory authority only. The original accepted-sample count of zero and original held diagnostic remain immutable.

The fixed J package contains 55 immutable payloads totaling 4,742,948 bytes. Full pure preflight runs against retained actual evidence. Two valid importer attempts execute real J repository/context checks and actual lease validation, write only the approved immutable bytes, and require matching synthetic remote acknowledgements. A separate import interrupted after ten writes retries to all 55 files. Wrong role, revision, ref, private-event state, lease owner, expiry, diagnostic scope, H acknowledgement and a lease released during checkpoint all reject. Post-preflight negative import tests explicitly reuse the already validated package; the positive importer tests do not mock preflight.

All six actual correction admissions replay without a model call or reservation. Group policies, evidence/admission references and original dates stay exact. The outer J correction stamp independently recomputes to `{js['globalCorrectionStamp']}`. Both languages independently verify the complete zero-credit baseline and reject honestly resealed forged checks, expiry, intake, processing and superseded-history changes. The new fixture remains 0/557 with no expiry.

The ordinary `Pipeline._task` and real `Fetcher` execute full 200 responses followed by genuine synthetic conditional 304 responses. The new observations retain the original body and link to the prior full 200 while recording the later check clock. They use exact source/URL/MIME/body joins. The actual arrays retain every row and unzoned literal date; a valid 205-row variant also passes. Failed transport, malformed middle rows, duplicates, ordering, unsafe links, impossible dates and extra/continuation envelopes reject. Valid older-only data can be quiet. Empty, boundary and future uncertainty retain their conservative meanings.

The real subscription agent and guarded runner execute with zero remaining model calls and two document slots initially available. Only login-status responses are simulated. Across two ordinary cycles, the fixture moves from 985 fetches / 80 calls / 38 documents to **991 / 80 / 39**, with zero model invocations and all 529 URLs pending. Each cycle stays inside the conservative six additional logical-fetch bound. Real exhausted-quota and deadline checks reject without changing counters. A separate transient-response test makes three physical attempts for one logical fetch reservation.

There are 10 main independent result groups and **106 rejection/guard checks**: 62 Python checks, 27 JavaScript mutations and 17 additional lease/import rejections. The companion JSON maps the prepared 24-case plan to executed checks, direct inspection and unchanged-code/full-suite evidence. Generic cancellation and UTC-day paths were unchanged; this review does not present them as newly exercised live behavior.

## Continuity and test attribution

The archived baseline is acknowledged `9deb0c9ce9fe34999da0cf13bb023dfdfecc15c8`, manifest `8da12977648ce0f6ed62f16de0b52c2257977f41404145adbecb363069e037e1`. Its prior complete 48,245-entry authentication is reused only after all file inode/device/size/mtime identities and the manifest still match. Every consumed reference is hash-checked, and 21,321 main-review input seals remain exact. Four fact references, 38 held rows, original source clocks and old dated evidence remain untouched. Mutable scenarios use isolated test storage or memory overlays. Sockets and frozen-archive `LocalStore` initialization are denied.

Eleven protected core modules, including the engine, model agent, selection, semantic context, old seed loader and old retained-template verifiers, byte-match base `7a1aee7b`. The stable worker handback's code, package, test and asset pins still match.

The retained worker logs independently authenticate **935 operational tests**, **379 data tests**, **115 pipeline tests**, **42 browser tests with one existing skip**, and **80 SEC claims with zero blockers/drift**. These full suites are worker executions; the reviewer ran the separate checks above. Four 1440/390 production/local images are byte-identical to their respective earlier images. The root separately reported viewing them. This change adds no visible improvement.

## Activation boundary

The frozen 985/80/38 ledger is a test fixture. Root must use the actual immediate archive, ledger, lease and day for activation. The historical H operational plan in the worker base must not land with J; root must select the separately reviewed disabled-J plan. The six-fetch ceiling covers the two added sources' logical work, not all 555 other obligations or physical retries.

No actual J collection, source request, model operation, remote acknowledgement, scheduled run or public publication happened in this review. No source clock, account counter, gate allowance or real archive/session state was changed. A later actual J ordinary run, scheduled receipt and accepted public release remain separate acceptance steps. The worker's queued documentation-only replay-command correction can be applied after this sealed review without changing reviewed implementation bytes.
''';(D/(stem+'.md')).write_text(md)
summary={'verdict':'PASS','markdown':{'path':str(D/(stem+'.md')),**pin(D/(stem+'.md'))},'json':{'path':str(D/(stem+'.json')),**pin(D/(stem+'.json'))},'receiptIndex':pin(Q/'index.json'),'receipts':len(index['files']),'allReviewerWritesOutsideCheckout':True,'allWritesStopped':True};(O/'handback.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary))
