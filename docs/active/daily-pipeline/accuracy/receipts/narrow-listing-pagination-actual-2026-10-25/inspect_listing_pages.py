"""Cold inspection of actual retained listing bytes. Never execute publisher JavaScript."""
import json,re,sys,hashlib
from pathlib import Path
from datetime import datetime,date,timedelta
from urllib.parse import urljoin,urlsplit,parse_qs
REPO=Path('/mnt/mac/Users/jessepike/code/projects/sec-market-finish-20261022')
ROOT=Path('/var/tmp/smp-listing-pagination-actual-40193925490-20261025/extracted')
OUT=ROOT.parent/'proof';sys.path.insert(0,str(REPO/'web/scripts/pipeline'))
from discovery import IndexMarkup,Page
audit=json.loads((OUT/'actual-diagnostic-audit.json').read_bytes())
old=json.loads((ROOT/'state/ci/source-probe-runs/40190857026-1.json').read_bytes())['diagnostic']['qualification']['targets']
new=json.loads((ROOT/'state/ci/source-probe-runs/40193925490-1.json').read_bytes())['diagnostic']['qualification']['targets']
def read(ref):
 b=(ROOT/'state'/ref['key']).read_bytes();assert len(b)==ref['bytes'] and hashlib.sha256(b).hexdigest()==ref['sha256'];return b
def observed(row):return json.loads(read(row['observation']))
def day(text):
 m=re.search(r'\b((?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2},?\s+\d{4})\b',text)
 if not m:return {'written':None,'calendarDay':None}
 written=m.group(1)
 for fmt in ('%b %d %Y','%B %d %Y'):
  try:return {'written':written,'calendarDay':datetime.strptime(written.replace(',',''),fmt).date().isoformat()}
  except ValueError:pass
 return {'written':written,'calendarDay':None,'invalidCalendar':True}
def window(d):
 if not d:return 'unknown_date'
 if d in ('2026-09-25','2026-10-25'):return 'boundary_day_undetermined_timezone'
 if '2026-09-25'<d<'2026-10-25':return 'inside_calendar_window'
 if d<'2026-09-25':return 'older_calendar_day'
 return 'future_calendar_day_anomaly'
pages=[]
for row in [old[5],old[6]]+new:
 o=observed(row);b=read(o['body']);assert o['httpStatus']==200 and o['requestedUrl']==o['finalUrl']==row['url'];text=b.decode('utf8');markup=IndexMarkup(text);nodes=list(markup.root.walk());page=Page(text,source_url=row['url']);prn=urlsplit(row['url']).netloc=='www.prnewswire.com';cards=[]
 if prn:
  containers=[n for n in nodes if n.tag=='div' and n.attrs.get('aria-label')=='News Release' and 'card' in n.classes]
  for n in containers:
   anchors=[x for x in n.walk() if x.tag=='a' and 'newsreleaseconsolidatelink' in x.classes];small=[x for x in n.walk() if x.tag=='small'];head=[x for x in n.walk() if x.tag=='h3'];assert len(anchors)==len(small)==len(head)==1
   url=urljoin(row['url'],anchors[0].attrs['href']);s=' '.join(small[0].text.split());d=day(s);cards.append({'url':url,'writtenDateText':s,'date':d,'calendarWindowState':window(d['calendarDay']),'headingIncludingDate':' '.join(head[0].text.split()),'cardText':' '.join(n.text.split()),'scopeProof':'same retained div[role=group][aria-label=News Release].card contains exact link/h3/small'})
  pagers=[n for n in nodes if n.tag=='ul' and 'pagination' in n.classes];assert len(pagers)==1;lis=[n for n in pagers[0].children if hasattr(n,'tag') and n.tag=='li'];active=[n for n in lis if 'active'in n.classes];assert len(active)==1;current=' '.join(active[0].text.split());expected=int(parse_qs(urlsplit(row['url']).query).get('page',['1'])[0]);assert current==str(expected)
  controls=[{'text':' '.join(n.text.split()),'classes':sorted(n.classes),'links':[urljoin(row['url'],x.attrs['href']) for x in n.walk() if x.tag=='a' and x.attrs.get('href')]} for n in lis];next_controls=[x for x in controls if x['text']=='»'];disabled_next=bool(len(next_controls)==1 and 'disabled'in next_controls[0]['classes'] and not next_controls[0]['links'])
 else:
  prefix='/newsroom/press-releases/' if row['sourceId'].startswith('abnormal') else '/press-releases/'
  def detail(n):return urljoin(row['url'],n.attrs.get('href','')) if n.tag=='a' and urlsplit(urljoin(row['url'],n.attrs.get('href',''))).netloc==urlsplit(row['url']).netloc and urlsplit(urljoin(row['url'],n.attrs.get('href',''))).path.startswith(prefix) else None
  for n in nodes:
   url=detail(n)
   if not url:continue
   chosen=n;scope='anchor';parent=n.parent
   if not day(' '.join(n.text.split()))['calendarDay']:
    for _ in range(4):
     if parent is None:break
     urls={detail(x) for x in parent.walk() if detail(x)}
     if urls!={url}:break
     if day(' '.join(parent.text.split()))['calendarDay']:chosen=parent;scope='nearest ancestor with one distinct detail URL and a written calendar date';break
     parent=parent.parent
   txt=' '.join(chosen.text.split());d=day(txt);cards.append({'url':url,'cardText':txt,'date':d,'calendarWindowState':window(d['calendarDay']),'scopeProof':scope,'containerTag':chosen.tag,'containerAttrs':chosen.attrs})
  current=None;controls=[];disabled_next=False
 literal_links=[{'raw':a['url'],'resolved':urljoin(row['url'],a['url']),'relNext':a['next']} for a in page.links]
 continuation=[x for x in literal_links if x['relNext'] or (not x['raw'].startswith('#') and urlsplit(x['raw']).query and urlsplit(x['resolved']).path==urlsplit(row['url']).path and urlsplit(x['resolved']).query and ('page' in urlsplit(x['resolved']).query.lower() or 'offset' in urlsplit(x['resolved']).query.lower()))]
 pages.append({'sourceId':row['sourceId'],'targetId':row['targetId'],'requestedUrl':row['url'],'originalRun':40190857026 if row in old else 40193925490,'observation':row['observation'],'httpStatus':o['httpStatus'],'contentType':o['contentType'],'fetchedAt':o['fetchedAt'],'finalUrl':o['finalUrl'],'body':o['body'],'bodyPath':str(ROOT/'state'/o['body']['key']),'canonicals':page.canonicals,'h1':[' '.join(n.text.split()) for n in nodes if n.tag=='h1'],'cards':cards,'rawCardOccurrences':len(cards),'uniqueDetailUrls':len({x['url'] for x in cards}),'activePaginationNumber':current,'paginationControls':controls,'explicitDisabledNextWithoutHref':disabled_next,'literalContinuationLinks':continuation,'calendarWindowCounts':dict(__import__('collections').Counter(x['calendarWindowState'] for x in cards)),'limits':'Static same-card/date/link inspection. No parser/source registration or semantic credit. Date-only calendar hints do not assert UTC instants.'})
groups={}
for sid in sorted({p['sourceId'] for p in pages}):
 ps=[p for p in pages if p['sourceId']==sid];seen={};overlaps=[];dates=[]
 for p in ps:
  for card in p['cards']:
   if card['url'] in seen:overlaps.append({'url':card['url'],'firstPage':seen[card['url']],'alsoOn':p['requestedUrl']})
   else:seen[card['url']]=p['requestedUrl']
   if card['date']['calendarDay']:dates.append(card['date']['calendarDay'])
 page_numbers=[int(p['activePaginationNumber']) for p in ps if p['activePaginationNumber'] is not None];links={x for p in ps for c in p['paginationControls'] for x in c['links']};known={p['requestedUrl'] for p in ps};unobserved=sorted(links-known);groups[sid]={'pages':len(ps),'pageNumbers':page_numbers,'rawCardOccurrences':sum(len(p['cards'])for p in ps),'uniqueDetailUrls':len(seen),'duplicateOrOverlapOccurrences':overlaps,'writtenDateMinimum':min(dates)if dates else None,'writtenDateMaximum':max(dates)if dates else None,'paginationLinksNotInObservedSet':unobserved,'explicitDisabledNextPages':[p['requestedUrl']for p in ps if p['explicitDisabledNextWithoutHref']],'contiguousObservedNumberedPages':bool(page_numbers and sorted(page_numbers)==list(range(1,max(page_numbers)+1))),'inventoryUrls':sorted(seen),'qualificationCredit':False}
output={'schemaVersion':1,'scope':'Actual two listing pages and five additional wire pages, joined to two retained wire first pages.','archiveCommit':'9e4a9806fdcc1b7cd6f91314b8b4ff4bb4ef2174','pages':pages,'groups':groups,'timezone':'Preserve all literal date labels and ET; no zone/offset inference. Boundary dates held separately.','executedJavaScript':False,'sourceRequests':0,'modelCalls':0,'qualificationCredit':False}
(OUT/'listing-card-pagination-inspection.json').write_text(json.dumps(output,indent=2)+'\n');print(json.dumps(groups,indent=2)[:7000])
