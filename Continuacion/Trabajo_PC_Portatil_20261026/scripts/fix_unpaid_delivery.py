import unreal,json,shutil
from pathlib import Path
R=Path(__file__).resolve().parent.parent;out=R/'AdversarialQA_20261026';backup=out/'before';backup.mkdir(exist_ok=True)
for rel in ['Delivery/BlueprintGameplay/BPC_DeliveryDataCore.uasset','Delivery/BlueprintGameplay/People/BP_DeliveryRecipient.uasset']:
 p=Path(unreal.Paths.project_content_dir())/rel
 if not (backup/p.name).exists():shutil.copy2(p,backup/p.name)
p=R/'work/extend_pure_order_lifecycle.py';source=p.read_text(encoding='utf-8-sig');scope={'__file__':str(p),'__name__':'__main__'};exec(compile(source[:source.index('# Circular order completion')],str(p),'exec'),scope)
Base=scope['Graph'];M=scope['M'];CORE=scope['CORE'];core=scope['core'];recipient=scope['recipient']
class GuardGraph(Base):
 def build(self,name,*args,**kwargs):
  if name=='CompleteOrder':
   self.get('OrderPaid');self.call('PaidAndValid','BooleanAND',M);self.link('CanDeliver','ReturnValue','PaidAndValid','A');self.link('OrderPaid','OrderPaid','PaidAndValid','B');self.links.remove(['CanDeliver','ReturnValue','Validate','Condition']);self.link('PaidAndValid','ReturnValue','Validate','Condition')
  elif name=='CanDeliver':
   self.node('Paid','getfield',owner=CORE,var='OrderPaid');self.link('Delivery','Delivery','Paid','self');self.call('PaidAndValid','BooleanAND',M);old=next(x for x in self.links if x[2:] == ['result','ReturnValue']);self.links.remove(old);self.link(old[0],old[1],'PaidAndValid','A');self.link('Paid','OrderPaid','PaidAndValid','B');self.link('PaidAndValid','ReturnValue','result','ReturnValue')
  else:return {'skipped':name}
  return super().build(name,*args,**kwargs)
p=R/'work/migrate_delivery_blueprints.py';body=p.read_text(encoding='utf-8-sig');body=body[body.index('reports=[]')+len('reports=[]'):body.index('unreal.EditorAssetLibrary.save_loaded_asset')]
exec(compile(body,'GuardedOrderCompletion','exec'),dict(scope,Graph=GuardGraph,bp=core,G=scope['d'].G,T=scope['TXT'],A=scope['AL'],reports=[]))
start=source.index('# Recipient authorization');end=source.index("g=Graph();g.get('Delivery');g.call('Allowed','CanDeliver'",start)
exec(compile(source[start:end],'GuardedRecipientAuthorization','exec'),dict(scope,Graph=GuardGraph))
for b in [core,recipient]:
 assert unreal.BlueprintEditorLibrary.compile_blueprint(b);assert unreal.EditorAssetLibrary.save_loaded_asset(b,only_if_is_dirty=False)
p=R/'scripts/probe_delivery_invariants.py';exec(compile(p.read_text(encoding='utf-8-sig'),str(p),'exec'),{'__file__':str(p),'__name__':'__main__'})
assert all(x['status']=='PASS' for x in json.loads((out/'delivery_invariants.json').read_text()))
unreal.log('UNPAID_DELIVERY_FIX_VERIFIED')
