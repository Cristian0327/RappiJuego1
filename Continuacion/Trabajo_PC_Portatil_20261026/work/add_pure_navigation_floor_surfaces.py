import unreal,json
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;E=unreal.BlueprintEditorLibrary;bp=unreal.load_asset('/Game/World/BlueprintWorld/BP_CityGeometry');sub=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);lib=unreal.SubobjectDataBlueprintFunctionLibrary;handles=sub.k2_gather_subobject_data_for_blueprint(bp);root=next(h for h in handles if str(lib.get_variable_name(lib.get_data(h)))=='CityRoot');floors=[]
for h in handles:
 c=lib.get_object_for_blueprint(lib.get_data(h),bp)
 if not isinstance(c,unreal.HierarchicalInstancedStaticMeshComponent) or not c.get_editor_property('can_ever_affect_navigation'):continue
 for i in range(c.get_instance_count()):
  t=c.get_instance_transform(i,False)
  if t.translation.z<=35 and t.scale3d.z<=.4 and min(t.scale3d.x,t.scale3d.y)>=3:floors.append((c.get_editor_property('static_mesh'),t))
for i,(mesh,t) in enumerate(floors):
 name='NavigationFloor_'+str(i);existing=next((h for h in sub.k2_gather_subobject_data_for_blueprint(bp) if str(lib.get_variable_name(lib.get_data(h)))==name),None)
 if existing:h=existing
 else:
  h,why=sub.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=root,new_class=unreal.StaticMeshComponent,blueprint_context=bp));assert not str(why);assert sub.rename_subobject(h,unreal.Text(name))
 c=lib.get_object_for_blueprint(lib.get_data(h),bp);c.set_editor_property('mobility',unreal.ComponentMobility.STATIC);c.set_static_mesh(mesh);c.set_editor_property('relative_location',t.translation);c.set_editor_property('relative_rotation',t.rotation.rotator());c.set_editor_property('relative_scale3d',t.scale3d);c.set_editor_property('visible',False);c.set_editor_property('hidden_in_game',True);c.set_collision_profile_name('BlockAll');c.set_editor_property('can_ever_affect_navigation',True);c.set_editor_property('cast_shadow',False)
assert E.compile_blueprint(bp);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False);(r/'work/pure_navigation_floor_surfaces.json').write_text(json.dumps({'exact_existing_floor_surfaces':len(floors),'no_new_surface_heights':True,'status':'AUTHORED_PENDING_RUNTIME'},indent=2));unreal.log('PURE_NAVIGATION_FLOORS_PASS '+str(len(floors)))
