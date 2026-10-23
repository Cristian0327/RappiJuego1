import unreal,json
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;E=unreal.BlueprintEditorLibrary;lib=unreal.SubobjectDataBlueprintFunctionLibrary;ss=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);out={}
for path in ['/Game/World/BlueprintWorld/BP_WorldPresentation','/Game/World/BlueprintWorld/BP_WorldState','/Game/Traffic/Transit/BP_TransitPassengerVisual','/Game/World/BlueprintWorld/Traffic/BP_TrafficManager','/Game/World/BlueprintWorld/Crowd/BP_CrowdManager']:
 bp=unreal.load_asset(path);c=unreal.get_default_object(bp.generated_class());v={}
 for n in E.list_member_variable_names(bp):
  try:
   val=c.get_editor_property(str(n));v[str(n)]=str(val)[:700]
  except:pass
 out[path]=v
(r/'work/urban_refresh_inventory.json').write_text(json.dumps(out,indent=2));unreal.log('URBAN_REFRESH_INVENTORY_READY')
