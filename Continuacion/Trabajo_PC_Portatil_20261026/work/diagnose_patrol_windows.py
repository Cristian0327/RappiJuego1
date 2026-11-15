import unreal,json
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;mesh=unreal.load_asset('/Game/Traffic/Services/SK_PolicePatrol');data={'slots':[{'slot':str(s.material_slot_name),'material':s.material_interface.get_path_name() if s.material_interface else None} for s in mesh.get_editor_property('materials')],'child_defaults':{}}
for n in ['BP_VoxelRoadVehicle','BP_PoliceRoadPatrol']:
 c=unreal.get_default_object(unreal.load_asset('/Game/Traffic/Services/'+n).generated_class());data['child_defaults'][n]={k:str(c.get_editor_property(k)) for k in ['RiderModel','RiderAnimation','RiderMaterial']}
w=unreal.load_asset('/Game/Traffic/Services/M_ServiceWindow');data['window_blend']=str(w.get_editor_property('blend_mode'));(r/'work/patrol_window_driver_diagnostic.json').write_text(json.dumps(data,indent=2));unreal.log('WINDOW_DRIVER_DIAGNOSTIC '+json.dumps(data))
