import gzip,hashlib,json,pathlib,re
p=pathlib.Path('/mnt/mac/Users/jessepike/code/projects/sec-market-finish-20261022/docs/active/daily-pipeline/accuracy/receipts/coverage-monitor-preview-2026-10-25')
read=lambda n:json.loads((p/n).read_bytes())
h=lambda b:hashlib.sha256(b).hexdigest()
run=read('github-run.json'); jobs=read('github-jobs.json')['jobs']
assert run['id']==40177951978 and run['event']=='workflow_dispatch' and run['head_branch']=='preview'
assert run['head_sha']=='05965a710f0a1cb84b582e9dc134deecf04535fe' and run['status']=='completed' and run['conclusion']=='failure'
assert {j['name']:j['conclusion'] for j in jobs}=={'probe':'success','daily-pipeline':'failure'}
log=gzip.decompress((p/'daily-pipeline.log.gz').read_bytes()).decode()
plain='\n'.join(re.sub(r'^\d{4}-\d\d-\d\dT\S+ ', '', line) for line in log.splitlines())
start=plain.index('{\n  "healthy":'); result,_=json.JSONDecoder().raw_decode(plain[start:])
assert 'Ran 36 tests in 2.039s\n\nOK' in plain
expected=['SCHEDULED_COLLECTION_RECEIPT_DIFFERS','OVERDUE_OR_INCOMPLETE_COVERAGE','DAILY_INTAKE_INCOMPLETE','PROCESSING_PENDING_10617','PROCESSING_HELD_10','HISTORICAL_REVIEW_PENDING_10616','PUBLIC_DAILY_INTAKE_INCOMPLETE','PUBLIC_PROCESSING_PENDING_10617','PUBLIC_PROCESSING_HELD_10','PUBLIC_HISTORICAL_REVIEW_PENDING_10616','PUBLIC_COVERAGE_INCOMPLETE_OR_OVERDUE','HELD_CLAIMS_37']
assert result['healthy'] is False and result['reasons']==expected
assert result['successfulTasks']==264 and result['requiredTasks']==557
assert result['notification']=={'delivery':'github_issue_updated','url':'https://github.com/jessepike/sec-market/issues/10','number':10,'state':'open','notificationTransport':'GitHub account notification settings'}
issue=read('after-issue10.json'); before=read('before-issue10.json')
assert issue['state']=='open' and issue['updated_at']>before['updated_at'] and result['checkedAt'] in issue['body']
assert all(reason in issue['body'] for reason in expected) and 'INDEPENDENT_PROBE_FAILED' not in issue['body']
assert [x['login'] for x in issue['assignees']]==['jessepike']
assert read('before-archive-ref.json')['object']['sha']==read('after-archive-ref.json')['object']['sha']=='b08469e082606def8ef37d9bfeb1cc9609f48176'
for name in ('app-release.json','deployment-receipt.json'):
 assert (p/('before-'+name)).read_bytes()==(p/('after-'+name)).read_bytes()
body=gzip.decompress((p/'after-daily-coverage.json.gz').read_bytes())
assert body==gzip.decompress((p/'before-daily-coverage.json.gz').read_bytes())
assert len(body)==1337257 and h(body)=='ac8068379c6c79760331711bfb7bb6387fbc639f9ab6f921713502c6982d47fc'
c=json.loads(body); assert c['validUntil']=='2026-10-26T12:45:29.479727+00:00'
assert result['checkedAt']<c['validUntil']
web=read('preview-web-run.json'); deployment=read('preview-deployment.json')['result']['deployment']
preview=read('preview-app-release.json')
assert web['id']==40177941631 and web['head_sha']==run['head_sha'] and web['conclusion']=='success'
assert deployment['id']=='dpl_x8eMjP1csPinhA6R8aj81QhnneVT' and deployment['state']=='READY'
assert deployment['meta']['githubCommitSha']==run['head_sha'] and deployment['meta']['githubCommitRef']=='preview'
assert deployment['target'] is None and preview['appRevision']==run['head_sha']
for name in ('daily-pipeline','legacy-probe'):
 compressed=(p/(name+'.log.gz')).read_bytes(); raw=gzip.decompress(compressed)
 meta={'rawSha256':h(raw),'rawBytes':len(raw),'rawLfCount':raw.count(b'\n'),'gzipSha256':h(compressed),'gzipBytes':len(compressed),'byteExactRoundTrip':gzip.decompress(compressed)==raw}
 (p/(name+'.log-metadata.json')).write_text(json.dumps(meta,indent=2)+'\n')
(p/'actual-monitor-result.json').write_text(json.dumps(result,indent=2)+'\n')
files=[{'path':f.name,'sha256':h(f.read_bytes()),'bytes':f.stat().st_size} for f in sorted(p.iterdir()) if f.is_file() and f.name!='verification.json']
verification={'runId':run['id'],'url':run['html_url'],'event':run['event'],'branch':run['head_branch'],'appRevision':run['head_sha'],'conclusion':run['conclusion'],'checkedAt':result['checkedAt'],'issueUpdatedAt':issue['updated_at'],'guardTestsPassed':36,'coverageBytes':len(body),'coverageRawSha256':h(body),'actualPublicValidUntil':c['validUntil'],'genericProbeFailureAbsent':True,'remainingReasons':expected,'archiveRefUnchanged':read('after-archive-ref.json')['object']['sha'],'publicAppAckAndCoverageBytesUnchanged':True,'qualificationCredit':0,'scheduledRunCredit':False,'productionUpdateCredit':False,'files':files}
(p/'verification.json').write_text(json.dumps(verification,indent=2)+'\n')
print(json.dumps({k:v for k,v in verification.items() if k!='files'},indent=2))
