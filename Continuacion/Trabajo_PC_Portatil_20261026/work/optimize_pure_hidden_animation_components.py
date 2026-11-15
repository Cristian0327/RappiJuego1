import unreal,json,sys
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;sys.path.insert(0,str(r/'Herramientas'));import blueprint_graph as d
s=(r/'work/optimize_pure_crowd_active_bubble.py').read_text(encoding='utf-8-sig');s=s[:s.index('# Hidden agents')];exec(compile(s,'SleepFarCitizenMeshes','exec'));assert E.compile_blueprint(bp);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
policy=unreal.VisibilityBasedAnimTickOption.ONLY_TICK_POSE_WHEN_RENDERED
paths=['/Game/World/BlueprintWorld/Crowd/BP_StreetCitizen','/Game/World/BlueprintWorld/Crowd/BP_CrowdPlayerProxy']+[x['asset'] for x in json.loads((r/'work/pure_crowd_models.json').read_text())]
reg=unreal.AssetRegistryHelpers.get_asset_registry();reg.search_all_assets(True)
for item in reg.get_assets_by_path('/Game/Traffic/Services',recursive=True):
 if str(item.asset_class_path.asset_name)=='Blueprint':paths.append(str(item.package_name))
modified=[]
for path in dict.fromkeys(paths):
 b=unreal.load_asset(path)
 if not b or not b.generated_class():continue
 c=unreal.get_default_object(b.generated_class())
 if not isinstance(c,unreal.Character):continue
 mesh=c.get_editor_property('mesh');mesh.set_editor_property('visibility_based_anim_tick_option',policy);mesh.set_editor_property('enable_update_rate_optimizations',False)
 if '/Models/' in path or path.endswith('BP_CrowdPlayerProxy'):
  tick=mesh.get_editor_property('primary_component_tick');tick.set_editor_property('start_with_tick_enabled',False);mesh.set_editor_property('primary_component_tick',tick)
 assert unreal.EditorAssetLibrary.save_loaded_asset(b,only_if_is_dirty=False);modified.append(path)
# Apply the same policy to additional skeletal/poseable visual components.
sub=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);lib=unreal.SubobjectDataBlueprintFunctionLibrary
for path in ['/Game/World/BlueprintWorld/Traffic/BP_TrafficVehicle']+[x for x in paths if x.startswith('/Game/Traffic/Services')]:
 b=unreal.load_asset(path)
 if not b:continue
 changed=False
 for handle in sub.k2_gather_subobject_data_for_blueprint(b):
  obj=lib.get_object_for_blueprint(lib.get_data(handle),b)
  if isinstance(obj,unreal.SkinnedMeshComponent):obj.set_editor_property('visibility_based_anim_tick_option',policy);changed=True
 if changed:assert unreal.EditorAssetLibrary.save_loaded_asset(b,only_if_is_dirty=False)
exec(compile((r/'work/fix_pure_far_traffic_collision.py').read_text(encoding='utf-8-sig'),'SleepFarVehicleMeshes','exec'))
(r/'work/pure_hidden_animation_budget.json').write_text(json.dumps({'status':'COMPILED_PENDING_RUNTIME','character_blueprints':modified,'far_mesh_component_ticks':False,'near_rendered_animation':'Every frame; no update-rate decimation','far_vehicle_poseable_mesh_ticks':False},indent=2));unreal.log('PURE_HIDDEN_ANIMATION_BUDGET_COMPILED '+str(len(modified)))
