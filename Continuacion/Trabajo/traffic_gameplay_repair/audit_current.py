import unreal,json
from pathlib import Path
P=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/traffic_gameplay_repair')
paths=['/Game/World/BlueprintWorld/Traffic/BP_TrafficVehicle','/Game/Delivery/BlueprintGameplay/Player/BP_BlueprintRider','/Game/Traffic/Services/BP_PoliceRoadPatrol','/Game/Traffic/Services/BP_VoxelRoadVehicle','/Game/Delivery/BlueprintGameplay/UI/WBP_BlueprintPhone']
out={}
for path in paths:
 b=unreal.load_asset(path)
 if not b:continue
 (P/(b.get_name()+'_current.json')).write_text(unreal.DeliveryEditorLibrary.audit_blueprint(b))
 c=unreal.get_default_object(b.generated_class());row={}
 for n in unreal.BlueprintEditorLibrary.list_member_variable_names(b):
  try:
   v=c.get_editor_property(str(n));row[str(n)]=str(v)[:600]
  except:pass
 row['components']=[]
 for x in (c.get_components_by_class(unreal.ActorComponent) if isinstance(c,unreal.Actor) else []):
  z={'name':x.get_name(),'class':x.get_class().get_name()}
  for n in ['relative_location','relative_rotation','relative_scale3d','max_step_height','capsule_half_height','capsule_radius']:
   try:z[n]=str(x.get_editor_property(n))
   except:pass
  row['components'].append(z)
 out[path]=row
(P/'current_defaults.json').write_text(json.dumps(out,indent=2))
unreal.log('CURRENT_AUDIT_DONE')
