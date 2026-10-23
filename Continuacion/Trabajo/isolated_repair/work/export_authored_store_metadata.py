import unreal,json
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;assert unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/Bogota');actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);out=[]
for a in actors.get_all_level_actors():
 if not isinstance(a,unreal.DeliveryPoint):continue
 t=a.get_actor_transform();v=t.translation;q=t.rotation.rotator();props={}
 for n in ['ThemeID','PointID']:
  props[n]=str(a.get_editor_property(n))
 out.append({'position':[v.x,v.y,v.z],'rotation':[q.pitch,q.yaw,q.roll],'properties':props})
assert len(out)>0;(r/'work/authored_store_metadata.json').write_text(json.dumps(out,indent=2));unreal.log('AUTHORED_STORE_METADATA_EXPORTED count='+str(len(out)))
