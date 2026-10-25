"""Inspect supplied primary JSON-LD as data; preserve original transports and actual304 chains."""
from pathlib import Path
from html.parser import HTMLParser
from unittest.mock import patch
import json,hashlib,sys,socket
R=Path('/var/tmp/smp-listing-pagination-actual-40193925490-20261025/extracted');O=R.parent/'proof'
sys.path.insert(0,'/mnt/mac/Users/jessepike/code/projects/sec-market-finish-20261022/web/scripts/pipeline')
from discovery import Page
from storage import LocalStore
rows={x['key']:x for x in json.loads((R/'archive-manifest.json').read_bytes())['files']};seals={}
def read(key):
 p=R/key;b=p.read_bytes();x=rows[key];assert hashlib.sha256(b).hexdigest()==x['sha256'] and len(b)==x['bytes'];s={'sha256':x['sha256'],'bytes':x['bytes'],'mtimeNs':p.stat().st_mtime_ns};assert seals.setdefault(key,s)==s;return b
class DataScripts(HTMLParser):
 def __init__(self,text):
  super().__init__(convert_charrefs=True);self.rows=[];self.active=None;self.feed(text)
 def handle_starttag(self,tag,attrs):
  if tag=='script':
   a=dict(attrs)
   if a.get('type','').strip().lower()=='application/ld+json':self.active={'attrs':attrs,'line':self.getpos()[0],'text':''}
 def handle_data(self,data):
  if self.active is not None:self.active['text']+=data
 def handle_endtag(self,tag):
  if tag=='script'and self.active is not None:self.rows.append(self.active);self.active=None
def fields(v,path=''):
 out=[]
 if isinstance(v,dict):
  for k,x in v.items():
   if k in ('datePublished','dateModified','headline','mainEntityOfPage','publisher','author','@type'):out.append({'pointer':path+'/'+k,'value':x})
   out+=fields(x,path+'/'+k)
 elif isinstance(v,list):
  for i,x in enumerate(v):out+=fields(x,path+'/'+str(i))
 return out
inspection=json.loads((O/'retained-primary-detail-reuse.json').read_bytes());pages=json.loads((O/'listing-card-pagination-inspection.json').read_bytes())['pages'];result=[]
with patch.object(socket.socket,'connect',side_effect=AssertionError('NO_NETWORK')),patch.object(LocalStore,'__init__',side_effect=AssertionError('NO_FROZEN_LOCALSTORE')):
 for item in inspection['latestFull200ShapeResults']:
  obs=json.loads(read(item['key']));body=read('state/'+obs['body']['key']);text=body.decode('utf8');page=Page(text,source_url=obs['requestedUrl']);scripts=[]
  for i,s in enumerate(DataScripts(text).rows):
   data=json.loads(s['text']);scripts.append({'scriptIndex':i,'htmlLine':s['line'],'attrs':s['attrs'],'rawScriptTextSha256':hashlib.sha256(s['text'].encode()).hexdigest(),'suppliedIdentityAndDateFields':fields(data)})
  matching=[m for m in inspection['matches']if m['observation'].get('sourceId')==obs['sourceId'] and m['observation'].get('requestedUrl')==obs['requestedUrl']];latest=max(matching,key=lambda m:m['observation']['fetchedAt']);chain=[];current=json.loads(read(latest['key']));seen=set()
  while True:
   assert current['observationId']not in seen;seen.add(current['observationId']);chain.append(current)
   if current['status']=='fetched':assert current['httpStatus']==200;break
   assert current['status']=='not_modified' and current['httpStatus']==304 and current['reusesObservationId'];prior=json.loads(read('state/observations/'+current['reusesObservationId']+'.json'));assert prior['sourceId']==current['sourceId'] and prior['requestedUrl']==current['requestedUrl'] and prior['body']==current['body'] and prior['fetchedAt']<=current['fetchedAt'];current=prior
  cards=[c for p in pages for c in p['cards']if c['url']==obs['requestedUrl']];days={c['date']['calendarDay']for c in cards};assert len(days)==1 and page.published and page.published[:10]in days and page.publication_ambiguous is False
  result.append({'sourceId':obs['sourceId'],'supplierCandidateIds':item['literalSourceIds'],'requestedUrl':obs['requestedUrl'],'full200ObservationKey':item['key'],'full200Observation':obs,'limitedExistingShapeGuard':item['existingPrimaryShape'],'existingPagePublication':page.published,'existingPageJsonDates':sorted(page.json_dates),'existingPagePublicationAmbiguous':page.publication_ambiguous,'indexCardWrittenDates':[c.get('writtenDateText')or c['date']['written']for c in cards],'writtenCalendarDayJoin':True,'jsonLdScripts':scripts,'latestActualObservationKey':latest['key'],'actual304To200ReuseChain':chain,'noDateRenewal':True})
for key,s in seals.items():p=R/key;b=p.read_bytes();assert hashlib.sha256(b).hexdigest()==s['sha256'] and len(b)==s['bytes'] and p.stat().st_mtime_ns==s['mtimeNs']
output={'schemaVersion':1,'scope':'Supplied exact retained primary identity/date fields; no semantic admission or publication.','rows':result,'inputSeals':seals,'allSealsUnchanged':True,'socketDenied':True,'LocalStoreConstructionDenied':True,'refinement':'The earlier limited primary-shape dateMetadata=[] is not proof of global metadata absence. Existing Page and direct suppliedJSONLD inspection establish the dates shown here; original preflight receipts remain unchanged.','sourceRequests':0,'modelCalls':0,'executedJavaScript':False};(O/'primary-supplied-jsonld-and-reuse.json').write_text(json.dumps(output,indent=2)+'\n');print(json.dumps({'PASS':True,'samples':len(result),'exactWrittenDayJoins':len(result),'archivedInputsSealed':len(seals)}))
