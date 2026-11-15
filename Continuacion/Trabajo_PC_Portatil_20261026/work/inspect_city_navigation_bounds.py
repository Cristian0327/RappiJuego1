import unreal,json
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;assert unreal.EditorLoadingAndSavingUtils.load_map('/Game/QA/PureCityCrowd');actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);out=[]
for a in actors.get_all_level_actors():
 if isinstance(a,(unreal.NavMeshBoundsVolume,unreal.NavModifierVolume)):
  o,e=a.get_actor_bounds(False);out.append({'label':a.get_actor_label(),'centre':[o.x,o.y,o.z],'extent':[e.x,e.y,e.z],'area':str(a.get_editor_property('area_class')) if isinstance(a,unreal.NavModifierVolume) else None})
(r/'work/city_navigation_volume_bounds.json').write_text(json.dumps(out,indent=2));unreal.log('NAV_VOLUME_INVENTORY_PASS')
