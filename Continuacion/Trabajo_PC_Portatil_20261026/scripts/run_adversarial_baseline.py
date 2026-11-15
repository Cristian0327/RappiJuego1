"""Re-execute current Blueprint functions; historical reports are not results."""
import unreal,json,time,traceback
from pathlib import Path
R=Path(__file__).resolve().parent.parent
out=R/'AdversarialQA_20261026';out.mkdir(exist_ok=True)
results=[]
for name in ['test_pure_delivery_data_core.py','test_pure_delivery_shop_queries.py','test_pure_delivery_marketplace.py','test_pure_delivery_progress.py','test_pure_rider_foundation.py','test_pure_phone_map.py','test_pure_traffic_doors.py','test_pure_traffic_lanes.py','test_pure_traffic_junction_lookup.py']:
 scope={'__file__':str(R/'work'/name),'__name__':'__main__'};started=time.monotonic()
 try:
  source=(R/'work'/name).read_text(encoding='utf-8-sig')
  source=source.replace('c=unreal.get_default_object(bp.generated_class())','c=unreal.new_object(bp.generated_class())')
  exec(compile(source,str(R/'work'/name),'exec'),scope)
  row=dict(test=name,status='PASS',checks=scope.get('checks',[]))
 except Exception:
  row=dict(test=name,status='FAIL',error=traceback.format_exc(),checks_before_failure=scope.get('checks',[]));unreal.log_error(row['error'])
 row['elapsed_seconds']=round(time.monotonic()-started,3);results.append(row)
 (out/'baseline.json').write_text(json.dumps(results,indent=2,default=str),encoding='utf-8')
 unreal.log('ADVERSARIAL_CASE '+name+' '+row['status'])
unreal.log('ADVERSARIAL_BASELINE_COMPLETE')
