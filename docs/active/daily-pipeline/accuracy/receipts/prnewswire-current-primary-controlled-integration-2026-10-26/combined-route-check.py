"""Synthetic caller selection and actual wrong-plan preflight. No durable sink or transport."""
from pathlib import Path
from contextlib import ExitStack
from unittest.mock import patch
import importlib,json,sys,tempfile,hashlib
R=Path('/var/tmp/smp-prn-controlled-integration-20261026/app');O=R.parent
sys.path[:0]=[str(R),str(R/'ops/ci'),str(R/'web/scripts/pipeline')]
import collect
from contracts import canonical
market=json.loads((R/'contracts/market.json').read_bytes())
OPS={'bounded_cyera_primary_capture':'cyera_primary_capture','bounded_prnewswire_primary_capture':'prnewswire_primary_capture','bounded_q4_controller_capture':'q4_controller_capture','bounded_q4_initial_data_capture':'q4_initial_data_capture','bounded_q4_primary_qualification':'q4_primary_qualification','bounded_orca_qualification':'orca_qualification'}
modules={op:importlib.import_module(name)for op,name in OPS.items()}
class Selected(ValueError):pass
class Sink:
 def __init__(self):self.audit=[];self.reads=[]
 def read(self,key):
  self.reads.append(key);assert key=='heads/cloud-lease.json';return None
 def get(self,*a):raise AssertionError('NO_IMMUTABLE_READ_FOR_WRONG_PLAN')
 def put(self,*a):raise AssertionError('NO_OPERATION_WRITE')
 def write_once(self,key,value):
  assert key.startswith('ci/source-probe-failures/');self.audit.append((key,value))
 def __getattr__(self,key):raise AssertionError('NO_DURABLE_METHOD:'+key)
results=[]
with tempfile.TemporaryDirectory(prefix='SYNTHETIC-prn-combined-route-')as temp:
 root=Path(temp);(root/'contracts').mkdir();path=root/'contracts/source-qualification-probes.json'
 for selected,module in modules.items():
  sink=Sink();raw=canonical({'schemaVersion':2,'operation':selected});path.write_bytes(raw)
  with ExitStack()as stack:
   stack.enter_context(patch.object(collect,'REPO',root));stack.enter_context(patch.object(collect.session_runtime,'require_source_probe_context'))
   for attr in ('PersistentProbeBudget','escrow_budgets','Fetcher','probe_sources','validate_qualification_probe_plan'):
    stack.enter_context(patch.object(collect,attr,side_effect=AssertionError('NO_'+attr)))
   validators={}
   for op,mod in modules.items():validators[op]=stack.enter_context(patch.object(mod,'validate_plan',side_effect=Selected(op)if op==selected else AssertionError('CROSS_ACTIVATION:'+op)))
   try:collect.execute_source_probe(root,sink,{'checkpointProfile':'source_probe','sessionId':'SYNTHETIC-CLOSED-ROUTE'},market,1200)
   except Selected as error:assert str(error)==selected
   else:raise AssertionError('EXPECTED_SELECTOR_SENTINEL')
   assert validators[selected].call_count==1 and all(v.call_count==0 for op,v in validators.items()if op!=selected)
  assert len(sink.audit)==1 and sink.reads==['heads/cloud-lease.json']
  results.append({'operation':selected,'exactBranchSelected':True,'crossActivation':False,'budgetEscrowFetchCalls':0,'durableWrites':0,'inMemoryExistingFailureReceipts':len(sink.audit)})
 plans={'bounded_cyera_primary_capture':'cyera-primary-capture-plan-2026-10-25.json','bounded_prnewswire_primary_capture':'prnewswire-primary-capture-plan-2026-10-25.json','bounded_q4_controller_capture':'q4-controller-capture-plan-2026-10-25.json','bounded_q4_initial_data_capture':'q4-initial-data-capture-plan-2026-10-25.json','bounded_q4_primary_qualification':'q4-primary-qualification-plan-2026-10-25.json'}
 for op,name in plans.items():
  value=json.loads((R/'docs/active/daily-pipeline/accuracy'/name).read_bytes());value['maxRequests']=99;raw=canonical(value);path.write_bytes(raw);sink=Sink()
  with patch.object(collect,'REPO',root),patch.object(collect.session_runtime,'require_source_probe_context'),patch.object(collect,'PersistentProbeBudget',side_effect=AssertionError('NO_BUDGET')),patch.object(collect,'escrow_budgets',side_effect=AssertionError('NO_ESCROW')),patch.object(collect,'Fetcher',side_effect=AssertionError('NO_FETCHER')):
   try:collect.execute_source_probe(root,sink,{'checkpointProfile':'source_probe','sessionId':'SYNTHETIC-WRONG-PLAN'},market,1200)
   except (ValueError,KeyError,TypeError):pass
   else:raise AssertionError('WRONG_PLAN_MUST_REJECT')
  assert len(sink.audit)==1 and sink.reads==['heads/cloud-lease.json']
  clean=Sink()
  try:modules[op].validate_plan(market,clean,raw,path)
  except (ValueError,KeyError,TypeError):pass
  else:raise AssertionError('DIRECT_WRONG_PLAN_MUST_REJECT')
  assert clean.audit==[] and clean.reads==[]
  results.append({'operation':op,'actualWrongPlanRejectedBeforeOperationIO':True,'budgetEscrowFetchCalls':0,'durableWrites':0,'directValidatorReads':0,'directValidatorWrites':0,'inMemoryExistingFailureReceipts':1})
 receipt={'verdict':'PASS','cases':results,'mergedCollectSha256':hashlib.sha256((R/'ops/ci/collect.py').read_bytes()).hexdigest(),'sourceRequests':0,'modelRequests':0,'realStateWrites':0,'note':'Caller failure audit receipts went to an in-memory sink only. Direct real wrong-plan validators performed zero reads/writes. Exact branch sentinels are synthetic and grant no capture credit.'}
 (O/'combined-route-check.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'verdict':'PASS','cases':len(results),'mergedCollectSha256':receipt['mergedCollectSha256']}))
