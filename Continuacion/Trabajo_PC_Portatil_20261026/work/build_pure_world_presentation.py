import unreal,json
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;E=unreal.BlueprintEditorLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();folder='/Game/World/BlueprintWorld';name='BP_WorldPresentation';f=unreal.BlueprintFactory();f.set_editor_property('parent_class',unreal.Actor);bp=unreal.load_asset(folder+'/'+name) or T.create_asset(name,folder,unreal.Blueprint,f);sub=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);lib=unreal.SubobjectDataBlueprintFunctionLibrary;root=sub.k2_gather_subobject_data_for_blueprint(bp)[0]
def add(n,cls):
 for h in sub.k2_gather_subobject_data_for_blueprint(bp):
  o=lib.get_object_for_blueprint(lib.get_data(h),bp)
  if o and (str(lib.get_variable_name(lib.get_data(h)))==n or o.get_name().removesuffix('_GEN_VARIABLE')==n):
   if n!='WorldRoot':assert sub.attach_subobject(root,h)
   return o
 h,reason=sub.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=root,new_class=cls,blueprint_context=bp));assert not str(reason);assert sub.rename_subobject(h,unreal.Text(n));return lib.get_object_for_blueprint(lib.get_data(h),bp)
worldRoot=add('WorldRoot',unreal.SceneComponent);rootActor=root
for h in sub.k2_gather_subobject_data_for_blueprint(bp):
 if lib.get_object_for_blueprint(lib.get_data(h),bp)==worldRoot:root=h;break
assert sub.make_new_scene_root(rootActor,root,bp)
assert E.compile_blueprint(bp)
for h in sub.k2_gather_subobject_data_for_blueprint(bp):
 if str(lib.get_variable_name(lib.get_data(h)))=='WorldRoot':root=h;break
sun=add('Sun',unreal.DirectionalLightComponent);sun.set_editor_property('mobility',unreal.ComponentMobility.MOVABLE);sun.set_editor_property('dynamic_shadow_distance_movable_light',16000);sun.set_editor_property('dynamic_shadow_cascades',4);sun.set_editor_property('shadow_bias',.3);sun.set_editor_property('shadow_sharpen',.25);sun.set_editor_property('light_source_angle',2.)
ambient=add('Ambient',unreal.SkyLightComponent);ambient.set_editor_property('mobility',unreal.ComponentMobility.MOVABLE);ambient.set_editor_property('sky_distance_threshold',50000.);ambient.set_editor_property('lower_hemisphere_is_black',False);ambient.set_editor_property('intensity',2.5)
fog=add('Fog',unreal.ExponentialHeightFogComponent);fog.set_editor_property('relative_location',unreal.Vector(0,0,-200));fog.set_editor_property('fog_density',.00012);fog.set_editor_property('fog_height_falloff',.25);fog.set_editor_property('enable_volumetric_fog',False)
sky=add('Sky',unreal.StaticMeshComponent);sky.set_static_mesh(unreal.load_asset('/Engine/BasicShapes/Sphere'));sky.set_material(0,unreal.load_asset('/Game/World/BlueprintWorld/M_BlueprintSky'));sky.set_editor_property('relative_scale3d',unreal.Vector(2200,2200,2200));sky.set_editor_property('cast_shadow',False);sky.set_collision_profile_name('NoCollision');sky.set_editor_property('mobility',unreal.ComponentMobility.MOVABLE)
flash=add('StormLightning',unreal.DirectionalLightComponent);flash.set_editor_property('mobility',unreal.ComponentMobility.MOVABLE);flash.set_editor_property('relative_rotation',unreal.Rotator(pitch=-65,yaw=35,roll=0));flash.set_editor_property('intensity',0.);flash.set_editor_property('cast_shadows',False)
for n,mat in [('RainMesh','M_Rain'),('HailMesh','M_Hail')]:
 o=add(n,unreal.InstancedStaticMeshComponent);o.set_static_mesh(unreal.load_asset('/Engine/BasicShapes/Cube'));o.set_material(0,unreal.load_asset('/Game/World/'+mat));o.set_collision_profile_name('NoCollision');o.set_editor_property('cast_shadow',False);o.set_editor_property('mobility',unreal.ComponentMobility.MOVABLE);o.set_editor_property('can_ever_affect_navigation',False);o.clear_instances()
 for i in range(1800 if n=='RainMesh' else 200):o.add_instance(unreal.Transform(location=unreal.Vector(),scale=unreal.Vector()),False)
known=[str(x) for x in E.list_member_variable_names(bp)]
for n,t in [('WorldState',E.get_object_reference_type(unreal.load_class(None,'/Game/World/BlueprintWorld/BP_WorldState.BP_WorldState_C'))),('SkyMaterial',E.get_object_reference_type(unreal.MaterialInstanceDynamic)),('LastThunderEvent',E.get_basic_type_by_name('int')),('RainOrigin',E.get_struct_type(unreal.load_object(None,'/Script/CoreUObject.Vector'))),('RainDrops',E.get_array_type(E.get_struct_type(unreal.load_object(None,'/Script/CoreUObject.Vector')))),('HailDrops',E.get_array_type(E.get_struct_type(unreal.load_object(None,'/Script/CoreUObject.Vector')))),('RainFloors',E.get_array_type(E.get_basic_type_by_name('real'))),('HailFloors',E.get_array_type(E.get_basic_type_by_name('real')))]:
 if n not in known:assert E.add_member_variable(bp,n,t)
assert E.compile_blueprint(bp);c=unreal.get_default_object(bp.generated_class())
for prefix,count in [('Rain',1800),('Hail',200)]:
 c.set_editor_property(prefix+'Drops',[unreal.Vector() for i in range(count)]);c.set_editor_property(prefix+'Floors',[0.]*count)
assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False);(r/'work/pure_world_presentation_foundation.json').write_text(json.dumps({'status':'STAGING_COMPONENTS_ONLY','components':['Sun','Ambient','Fog','Sky','StormLightning'],'pending':['Dynamic sky lighting Blueprint functions','World state bootstrap/frame connection','Rain/hail geometry presentation','Thunder playback','Runtime visual testing']},indent=2));unreal.log('PURE_WORLD_PRESENTATION_COMPONENTS_PASS')




