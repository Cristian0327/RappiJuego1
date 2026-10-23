import unreal,json,sys,math
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;U=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/urban_refresh');sys.path.insert(0,str(r/'Herramientas'));import blueprint_graph as d
E=unreal.BlueprintEditorLibrary;EL=unreal.EditorAssetLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();ME=unreal.MaterialEditingLibrary;folder='/Game/World/BogotaUrban';ss=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);lib=unreal.SubobjectDataBlueprintFunctionLibrary;M=d.M;K='/Script/Engine.KismetSystemLibrary';SC='/Script/Engine.SceneComponent'
for name in ['SM_Bogota_SemaforoPeaton','SM_Bogota_SemaforoPeatonRojo']:
 opt=unreal.FbxImportUI();opt.import_mesh=True;opt.import_as_skeletal=False;opt.import_materials=False;opt.import_textures=False;opt.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH;opt.automated_import_should_detect_type=False;opt.static_mesh_import_data.combine_meshes=True;opt.static_mesh_import_data.auto_generate_collision=False;opt.static_mesh_import_data.vertex_color_import_option=unreal.VertexColorImportOption.REPLACE;opt.static_mesh_import_data.convert_scene=True;opt.static_mesh_import_data.convert_scene_unit=True;task=unreal.AssetImportTask();task.filename=str(U/'export'/(name+'.fbx'));task.destination_path=folder+'/Geometry';task.destination_name=name;task.options=opt;task.automated=True;task.replace_existing=True;task.save=True;T.import_asset_tasks([task]);mesh=unreal.load_asset(task.destination_path+'/'+name)
 for i in range(len(mesh.static_materials)):mesh.set_material(i,unreal.load_asset(folder+'/M_BogotaSignalEmission'))
 assert EL.save_loaded_asset(mesh,only_if_is_dirty=False)
bp=unreal.load_asset(folder+'/BP_BogotaSignal');hs=ss.k2_gather_subobject_data_for_blueprint(bp);h=next((h for h in hs if str(lib.get_variable_name(lib.get_data(h)))=='PeatonRojo'),None)
if not h:h,reason=ss.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=hs[0],new_class=unreal.StaticMeshComponent,blueprint_context=bp));assert not str(reason);ss.rename_subobject(h,unreal.Text('PeatonRojo'))
o=lib.get_object_for_blueprint(lib.get_data(h),bp);o.set_static_mesh(unreal.load_asset(folder+'/Geometry/SM_Bogota_SemaforoPeatonRojo'));o.set_collision_profile_name('NoCollision');o.set_editor_property('can_ever_affect_navigation',False);o.set_editor_property('cast_shadow',False);assert E.compile_blueprint(bp);d.bp=bp;g=d.Graph();g.call('Now','GetGameTimeInSeconds',K);g.call('Phase','FMod',M,Divisor='66');g.link('Now','ReturnValue','Phase','Dividend');last='entry'
for name,lo,hi in [('Verde',0,36),('Amarillo',36,40),('Rojo',40,66),('Peaton',46,62),('PeatonRojo',46,62)]:
 g.get(name);g.call(name+'Lower','GreaterEqual_DoubleDouble',M,B=str(lo));g.link('Phase','Remainder',name+'Lower','A');g.call(name+'Upper','Less_DoubleDouble',M,B=str(hi));g.link('Phase','Remainder',name+'Upper','A');g.call(name+'On','BooleanAND',M);g.link(name+'Lower','ReturnValue',name+'On','A');g.link(name+'Upper','ReturnValue',name+'On','B');src=name+'On'
 if name=='PeatonRojo':g.call(name+'Off','Not_PreBool',M);g.link(src,'ReturnValue',name+'Off','A');src=name+'Off'
 g.call(name+'Show','SetVisibility',SC,bPropagateToChildren='true');g.link(name,name,name+'Show','self');g.link(src,'ReturnValue',name+'Show','bNewVisibility');g.exec(last,name+'Show');last=name+'Show'
g.exec(last,'result');g.build('ReceiveTick');assert E.compile_blueprint(bp);assert EL.save_loaded_asset(bp,only_if_is_dirty=False)
# Softer stable shadows remove surface self-shadow speckles on fine voxel faces.
bp=unreal.load_asset('/Game/World/BlueprintWorld/BP_WorldPresentation')
for h in ss.k2_gather_subobject_data_for_blueprint(bp):
 o=lib.get_object_for_blueprint(lib.get_data(h),bp)
 if str(lib.get_variable_name(lib.get_data(h)))=='Sun':o.set_editor_property('shadow_bias',.65);o.set_editor_property('shadow_slope_bias',.8);o.set_editor_property('shadow_sharpen',0.);o.set_editor_property('contact_shadow_length',0.)
assert E.compile_blueprint(bp);assert EL.save_loaded_asset(bp,only_if_is_dirty=False)
# Keep the original mountain geometry while restoring a coherent green Andean palette.
mat=unreal.load_asset('/Game/Maps/MapaCompleto/M_AndenesBogota')
for obj in unreal.ObjectIterator(unreal.MaterialExpressionCustom):
 if obj.get_outer()==mat:
  code=obj.get_editor_property('code');code=code.replace('if(P.z > 35 || P.z < -40) return C;','if(P.z > 35) { float shade=saturate(dot(C,float3(.21,.72,.07))*3); return lerp(float3(.035,.09,.025),float3(.16,.29,.055),shade); } if(P.z < -40) return C;');obj.set_editor_property('code',code)
ME.recompile_material(mat);assert EL.save_loaded_asset(mat,only_if_is_dirty=False)
models=json.loads((r/'work/pure_traffic_vehicle_foundation.json').read_text())['models']
for spec in models:
 bp=unreal.load_asset(spec['asset'])
 for h in ss.k2_gather_subobject_data_for_blueprint(bp):
  n=str(lib.get_variable_name(lib.get_data(h)));o=lib.get_object_for_blueprint(lib.get_data(h),bp)
  if n in ['HeadlightLeft','HeadlightRight'] and isinstance(o,unreal.LightComponent):o.set_editor_property('intensity',750.);o.set_editor_property('light_color',unreal.Color(255,245,225));o.set_editor_property('attenuation_radius',2600.)
 assert E.compile_blueprint(bp);assert EL.save_loaded_asset(bp,only_if_is_dirty=False)
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/MapaCompleto_Integration');actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in list(actors.get_all_level_actors()):
 if a.get_actor_label()=='Aspecto cálido Bogotá':actors.destroy_actor(a)
pp=actors.spawn_actor_from_class(unreal.PostProcessVolume,unreal.Vector());pp.set_actor_label('Aspecto cálido Bogotá');pp.set_editor_property('unbound',True);pp.set_editor_property('priority',500.);settings=pp.get_editor_property('settings')
for name,value in [('override_auto_exposure_method',True),('auto_exposure_method',unreal.AutoExposureMethod.AEM_MANUAL),('override_auto_exposure_apply_physical_camera_exposure',True),('auto_exposure_apply_physical_camera_exposure',False),('override_auto_exposure_bias',True),('auto_exposure_bias',0.),('override_bloom_intensity',True),('bloom_intensity',.15),('override_vignette_intensity',True),('vignette_intensity',.12)]:settings.set_editor_property(name,value)
pp.set_editor_property('settings',settings)
# Crossing luminaires stand on the actual sidewalk, even where surrounding terrain drops away.
plan=json.loads((U/'placement_plan.json').read_text());extra=[v for v in plan['furniture'] if v.get('crossing_lamp')];bp=unreal.load_asset(folder+'/BP_BogotaUrbanDressing');c=unreal.get_default_object(bp.generated_class())
for h in ss.k2_gather_subobject_data_for_blueprint(bp):
 o=lib.get_object_for_blueprint(lib.get_data(h),bp);n=str(lib.get_variable_name(lib.get_data(h)))
 if isinstance(o,unreal.InstancedStaticMeshComponent) and o.static_mesh and o.static_mesh.get_name() in ['SM_Bogota_Farola','SM_Bogota_FarolaLuz']:
  transforms=list(c.get_editor_property(n+'Transforms'))
  for item in extra:
   tr=unreal.Transform(location=unreal.Vector(*item['position']),rotation=unreal.Rotator(pitch=0,yaw=item['yaw']+180,roll=0),scale=unreal.Vector(1,1,1))
   if not any((t.translation-tr.translation).length()<1 for t in transforms):transforms.append(tr)
  c.set_editor_property(n+'Transforms',transforms)
assert EL.save_loaded_asset(bp,only_if_is_dirty=False)
for a in list(actors.get_all_level_actors()):
 if a.get_class().get_name()=='BP_BogotaUrbanDressing_C':actors.destroy_actor(a)
actors.spawn_actor_from_class(bp.generated_class(),unreal.Vector())
for item in extra:
 a=actors.spawn_actor_from_class(unreal.load_asset(folder+'/BP_BogotaStreetLight').generated_class(),unreal.Vector(*item['position']));a.set_actor_label('Farola cálida de cruce')
assert unreal.EditorLoadingAndSavingUtils.save_current_level();unreal.log('BOGOTA_FINAL_LIGHTING_SIGNAL_POLISH_READY')
