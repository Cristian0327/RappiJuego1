import unreal,json,sys,math
from pathlib import Path
U=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/urban_refresh');exec(compile((U/'fix_physical_crossings.py').read_text(),'CrossingAndLampFinal','exec'),{})
r=Path(unreal.Paths.project_dir()).parent;E=unreal.BlueprintEditorLibrary;EL=unreal.EditorAssetLibrary;unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/MapaCompleto_Integration');actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);stations=json.loads((U/'placement_plan.json').read_text())['stations'];models=[v for v in json.loads((r/'work/pure_crowd_models.json').read_text()) if not v['cane']]
for a in actors.get_all_level_actors():
 if a.get_class().get_name()=='BP_BogotaStreetLight_C':
  pos=a.get_actor_location()
  if pos.z==20 and any(abs(math.dist([pos.x,pos.y],st['position'][:2])-1050)<1 for st in stations):a.set_actor_location(unreal.Vector(pos.x,pos.y,-80),False,True)
people=[a for a in actors.get_all_level_actors() if a.get_class().get_name()=='BP_CrosswalkCitizen_C']
for i,a in enumerate(people):
 source=unreal.get_default_object(unreal.load_asset(models[i%len(models)]['asset']).generated_class()).get_editor_property('mesh');mesh=a.get_component_by_class(unreal.SkeletalMeshComponent);mesh.set_skinned_asset_and_update(source.get_skinned_asset(),True)
 for k,mat in enumerate(source.get_materials()):mesh.set_material(k,mat)
 mesh.set_anim_instance_class(unreal.load_class(None,'/Game/Delivery/Animation/ABP_StreetCitizen.ABP_StreetCitizen_C'))
assert unreal.EditorLoadingAndSavingUtils.save_current_level();exec(compile((U/'build_urban_qa.py').read_text(),'FinalSceneSnapshots','exec'),{});exec(compile((U/'add_crossing_completion_probe.py').read_text(),'ProtectedCrossingCounters','exec'),{});unreal.log('URBAN_FINAL_SNAPSHOTS_READY')
