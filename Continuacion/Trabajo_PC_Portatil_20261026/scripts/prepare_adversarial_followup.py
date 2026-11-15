import unreal,json,math,traceback
from pathlib import Path
R=Path(__file__).resolve().parent.parent;out=R/'AdversarialQA_20261026';results=[]
for name in ['test_pure_order_acceptance.py','test_pure_phone_map.py']:
 scope=dict(__file__=str(R/'work'/name),__name__='__main__',unreal=unreal,json=json,math=math)
 try:
  exec(compile((R/'work'/name).read_text(encoding='utf-8-sig'),str(R/'work'/name),'exec'),scope);row=dict(test=name,status='PASS',checks=scope.get('checks',[]))
 except Exception:row=dict(test=name,status='FAIL',error=traceback.format_exc(),checks_before_failure=scope.get('checks',[]))
 results.append(row)
(out/'followup.json').write_text(json.dumps(results,indent=2,default=str))
for path in ['/Game/Delivery/BlueprintGameplay/UI/WBP_BlueprintPhone','/Game/Delivery/BlueprintGameplay/Player/BP_BlueprintRider','/Game/World/BlueprintWorld/Traffic/BP_TrafficManager']:
 audit=json.loads(unreal.DeliveryEditorLibrary.audit_blueprint(unreal.load_asset(path)))
 (out/(path.rsplit('/',1)[-1]+'_audit.json')).write_text(json.dumps(audit,indent=2))
p=R/'scripts/cache_phone_layout.py';exec(compile(p.read_text(encoding='utf-8-sig'),str(p),'exec'),{'__file__':str(p),'__name__':'__main__'})
p=R/'work/build_pure_phone_runtime_test.py';exec(compile(p.read_text(encoding='utf-8-sig'),str(p),'exec'),{'__file__':str(p),'__name__':'__main__'})
unreal.log('ADVERSARIAL_FOLLOWUP_READY')
