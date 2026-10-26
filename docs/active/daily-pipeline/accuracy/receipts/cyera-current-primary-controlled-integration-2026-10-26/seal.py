from pathlib import Path
import gzip,hashlib,json,os,shutil,subprocess
ROOT=Path('/mnt/mac/Users/jessepike/code/projects/sec-market-finish-20261022')
OUT=Path('/var/tmp/smp-cyera-controlled-integration-20261026')
REL=Path('docs/active/daily-pipeline/accuracy/receipts/cyera-current-primary-controlled-integration-2026-10-26')
DEST=ROOT/REL;DEST.mkdir(parents=True,exist_ok=True)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def canonical(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def payload(path):return os.readlink(path).encode() if path.is_symlink() else path.read_bytes()
index=json.loads((OUT/'copy-index.json').read_bytes());before=json.loads(gzip.decompress((OUT/'target-base-before.json.gz').read_bytes()))
assert subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD']).decode().strip()==index['base']
changes=[]
for rel,row in before.items():
 raw=payload(ROOT/rel);current={'path':rel,'sha256':sha(raw),'bytes':len(raw)}
 if current['sha256']!=row['sha256']:
  assert rel in ('ops/ci/collect.py','status.md','BACKLOG.md'),('UNEXPECTED_TARGET_CHANGE',rel)
  changes.append({**current,'baseSha256':row['sha256']})
assert len(changes)==3
for row in index['files']:
 raw=(ROOT/row['path']).read_bytes();assert sha(raw)==row['sha256'] and len(raw)==row['bytes']
for name in ('controlled-copy.py','copy-index.json','target-base-before.json.gz','assembly.json','full-archive-absence-driver.py','full-archive-absent.json'):
 shutil.copyfile(OUT/name,DEST/name)
for name in ('operations-present.log','operations-absent.log','npm-test.log','production-renders.log','local-renders.log'):
 (DEST/(name+'.gz')).write_bytes(gzip.compress((OUT/name).read_bytes(),mtime=0))
shutil.copyfile('/mnt/mac/private/tmp/cyera-controlled-seal.py',DEST/'seal.py')
present=(OUT/'operations-present.log').read_text();assert 'Ran 995 tests' in present and present.rstrip().endswith('OK')
absent=json.loads((OUT/'full-archive-absent.json').read_bytes());assert absent['testsRun']==995 and absent['passed']==935 and len(absent['skipped'])==60 and not absent['frozenReadAttempts'] and len(absent['portableCyeraPassed'])==22
npm=(OUT/'npm-test.log').read_text();assert '# tests 379' in npm and '# pass 379' in npm and 'Ran 115 tests' in npm and '42 passed' in npm and '1 skipped' in npm and '{"complete":true,"required":80,"verified":80,"blockers":0,"drift":0}' in npm
host=Path('/mnt/mac/Users/jessepike/Documents/Codex/2026-10-22/security-market-pulse/renewal-20261024')
old=ROOT/'docs/active/daily-pipeline/accuracy/receipts/cyera-current-primary-build-2026-10-25/images'
rows=[]
for surface,url in [('production','https://securitymarketpulse.com/'),('local','http://127.0.0.1:4489/')]:
 for width in (1440,390):
  path=host/f'cyera-current-primary-{surface}-{width}.png';raw=path.read_bytes();prior=host/f'prn-dated-window-{surface}-{width}.png';initial=old/f'{surface}-{width}.png'
  assert raw==prior.read_bytes()==initial.read_bytes()
  dest=DEST/'images'/f'{surface}-{width}.png';dest.parent.mkdir(exist_ok=True);dest.write_bytes(raw)
  rows.append({'surface':surface,'url':url,'width':width,'actualHostPath':str(path).replace('/mnt/mac','',1),'retainedCapture':str(dest.relative_to(ROOT)),
               'sha256':sha(raw),'bytes':len(raw),'workerViewed':True,'rootViewRequiredBeforePush':True,
               'exactInitialCyeraCapture':str(initial.relative_to(ROOT)),'exactPrNewsBaselineHostPath':str(prior).replace('/mnt/mac','',1),'unchanged':True})
(DEST/'actualcapture-paths.json').write_bytes(canonical({'status':'PASS_FINAL_COMBINED_CAPTURES','assemblyBase':index['base'],'pendingCorrectionGroups':8,'images':rows,'oldSealedRenderJsonModified':False,'visibleChangesFromCorrespondingBaseline':False,'productionLocalFixtureDifference':'Existing and unchanged; no production publication claim.'}))
protected={'status':'PASS','base':index['base'],'trackedBaseFiles':len(before),'protectedUnchanged':len(before)-len(changes),'authorizedExistingDeltas':changes,
           'copiedFilesVerified':len(index['files']),'staleSourceStatusExcluded':True,'currentEightRequestPolicyAndDisabledPlanPreserved':True}
(DEST/'target-protection-after.json').write_bytes(canonical(protected))
summary={'status':'PASS_CONTROLLED_INTEGRATION_READY_FOR_ROOT_REVIEW','base':index['base'],'copiedSealedFiles':69,'protectedTrackedUnchanged':2755,
         'operationalPresent':{'tests':995,'passed':995,'skipped':0},'operationalAbsent':{'tests':995,'passed':935,'explicitRetainedSkips':60,'frozenReadAttempts':0,'portableCyeraPassed':22},
         'application':{'lint':'PASS','dataPassed':379,'pipelinePassed':115,'secRequired':80,'secVerified':80,'secBlockers':0,'secDrift':0,'browserPassed':42,'existingBrowserSkipped':1},
         'renders':{'actualNewCaptures':4,'workerViewed':4,'correspondingBaselineByteMatches':4,'actualPathsReceipt':'actualcapture-paths.json','rootViewRequired':True},
         'pendingCorrectionGroups':8,'activeDisabledPlanRawSha256':sha((ROOT/'contracts/source-qualification-probes.json').read_bytes()),
         'candidatePlanSelected':False,'collector':'Root reported ordinary manual40263678287 in progress; worker makes no admission/publication claim.',
         'sourceRequests':0,'modelCalls':0,'liveReservations':0,'dispatches':0,'commits':0,'pushes':0,'failedCombinedRuns':0}
(DEST/'verification-summary.json').write_bytes(canonical(summary))
report='docs/active/daily-pipeline/accuracy/cyera-current-primary-controlled-integration-2026-10-26.md';documents=[report,'status.md','BACKLOG.md']
receiptrows=[]
for p in sorted(DEST.rglob('*')):
 if p.is_file() and p.name!='receipt-index.json':
  raw=p.read_bytes();receiptrows.append({'path':str(p.relative_to(DEST)),'bytes':len(raw),'sha256':sha(raw)})
(DEST/'receipt-index.json').write_bytes(canonical({'base':index['base'],'files':receiptrows,'documents':[{'path':p,'bytes':len((ROOT/p).read_bytes()),'sha256':sha((ROOT/p).read_bytes())} for p in documents],
                                                'incomingCopyIndexSha256':sha((OUT/'copy-index.json').read_bytes()),'originalSealedBuildIndexSha256':index['sourceBuildIndexSha256'],'independentReviewIndexSha256':index['independentIndexSha256']}))
print(json.dumps({'copiedFiles':len(index['files']),'receiptFiles':len(receiptrows),'receiptIndexSha256':sha((DEST/'receipt-index.json').read_bytes()),'summarySha256':sha((DEST/'verification-summary.json').read_bytes()),'capturesSha256':sha((DEST/'actualcapture-paths.json').read_bytes()),'reportSha256':sha((ROOT/report).read_bytes())}))
