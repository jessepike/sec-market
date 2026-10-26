from pathlib import Path
import sys,json,hashlib,concurrent.futures,urllib.request
from urllib.parse import quote
APP=Path('/var/tmp/smp-oct26-ordinary-40263678287/application');sys.path.insert(0,str(APP/'web/scripts/pipeline'))
from artifacts import unpack
from contracts import canonical
root=Path(__file__).parent;state=Path('/var/tmp/smp-oct26-publish-40266519925/capture/extracted/state');head=json.loads((state/'heads/production.json').read_bytes());record=json.loads((state/('releases/'+head['releaseId']+'.json')).read_bytes())
files=unpack((state/record['manifest']['artifact']['archive']['key']).read_bytes());files['static/deployment-receipt.json']=canonical(record['acknowledgement'])
old=json.loads(Path('/var/tmp/smp-oct26-publish-40266519925/old-public-vercel-ready.json').read_bytes())
host='https://'+old['url'];hosts=[host,'https://securitymarketpulse.com']
def check(row):
 host,name,expected=row;url=host+'/'+quote(name.removeprefix('static/'),safe='/')
 with urllib.request.urlopen(urllib.request.Request(url,headers={'Cache-Control':'no-cache','Accept-Encoding':'identity'}),timeout=40) as response:
  body=response.read(len(expected)+1);assert response.status==200 and response.url==url and body==expected,url
  return {'host':host,'path':'/'+name.removeprefix('static/'),'bytes':len(body),'sha256':hashlib.sha256(body).hexdigest(),'httpStatus':response.status}
rows=[(host,name,body) for host in hosts for name,body in sorted(files.items()) if name.startswith('static/')]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(check,rows))
assert len(results)==106
(root/'public-static-verification.json').write_text(json.dumps({'status':'PASS','releaseId':head['releaseId'],'sequence':head['sequence'],'allBytesExact':True,'verifiedRequests':len(results),'files':results},indent=2)+'\n')
print(json.dumps({'status':'PASS','releaseId':head['releaseId'],'sequence':head['sequence'],'verifiedRequests':len(results)}))
