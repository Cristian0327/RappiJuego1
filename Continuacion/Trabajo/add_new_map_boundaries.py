import unreal,json,sys
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;sys.path.insert(0,str(r/'Herramientas'));import blueprint_graph as d
E=unreal.BlueprintEditorLibrary;EL=unreal.EditorAssetLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();folder='/Game/Maps/MapaCompleto';f=unreal.BlueprintFactory();f.set_editor_property('parent_class',unreal.Actor);bp=unreal.load_asset(folder+'/BP_BuildingBoundary') or T.create_asset('BP_BuildingBoundary',folder,unreal.Blueprint,f);ss=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);lib=unreal.SubobjectDataBlueprintFunctionLibrary;handles=ss.k2_gather_subobject_data_for_blueprint(bp);h=next((h for h in handles if str(lib.get_variable_name(lib.get_data(h)))=='Boundary'),None)
if not h:
 h,reason=ss.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=handles[0],new_class=unreal.BoxComponent,blueprint_context=bp));assert not str(reason);ss.rename_subobject(h,unreal.Text('Boundary'))
o=lib.get_object_for_blueprint(lib.get_data(h),bp);o.set_box_extent(unreal.Vector(100,100,300));o.set_collision_profile_name('BlockAll');o.set_editor_property('mobility',unreal.ComponentMobility.STATIC);o.set_editor_property('dynamic_obstacle',True);o.set_editor_property('area_class_override',unreal.load_class(None,'/Script/NavigationSystem.NavArea_Null'));o.set_editor_property('can_ever_affect_navigation',True);o.set_editor_property('hidden_in_game',True);assert E.compile_blueprint(bp);EL.save_loaded_asset(bp,only_if_is_dirty=False)
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/MapaCompleto_Integration');actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in list(actors.get_all_level_actors()):
 if a.get_class().get_name()=='BP_BuildingBoundary_C':actors.destroy_actor(a)
plan=json.loads(Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/new_map_audit/integration_plan.json').read_text());count=0
for v in plan['building_footprints']:
 a=actors.spawn_actor_from_class(bp.generated_class(),unreal.Vector((v[0]+v[2])/2,(v[1]+v[3])/2,250));a.set_actor_scale3d(unreal.Vector((v[2]-v[0])/200,(v[3]-v[1])/200,1));count+=1
assert unreal.EditorLoadingAndSavingUtils.save_current_level();unreal.log('NEW_MAP_BUILDING_BOUNDARIES '+str(count))


