import unreal,json,math,sys,shutil,collections
from pathlib import Path
U=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/urban_refresh');r=Path(unreal.Paths.project_dir()).parent
exec(compile((U/'integrate_connected_city.py').read_text(),'FinalConnectedIntegration','exec'),{})
E=unreal.BlueprintEditorLibrary;EL=unreal.EditorAssetLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();folder='/Game/World/BogotaUrban';ss=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);lib=unreal.SubobjectDataBlueprintFunctionLibrary;actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);city=json.loads((U.parent/'new_map_audit/integration_plan.json').read_text());plan=json.loads((U/'placement_plan.json').read_text());stplan=json.loads((U/'station_expansion_plan.json').read_text())
# Import the Blender-modeled physical station access connections.
name='SM_Bogota_AccesosEstaciones';opt=unreal.FbxImportUI();opt.import_mesh=True;opt.import_as_skeletal=False;opt.import_materials=False;opt.import_textures=False;opt.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH;opt.automated_import_should_detect_type=False;opt.static_mesh_import_data.combine_meshes=True;opt.static_mesh_import_data.auto_generate_collision=False;opt.static_mesh_import_data.vertex_color_import_option=unreal.VertexColorImportOption.REPLACE;opt.static_mesh_import_data.convert_scene=True;opt.static_mesh_import_data.convert_scene_unit=True;task=unreal.AssetImportTask();task.filename=str(U/'export'/(name+'.fbx'));task.destination_path=folder+'/Geometry';task.destination_name=name;task.options=opt;task.automated=True;task.replace_existing=True;task.save=True;T.import_asset_tasks([task]);mesh=unreal.load_asset(task.destination_path+'/'+name)
for i in range(len(mesh.static_materials)):mesh.set_material(i,unreal.load_asset(folder+'/M_BogotaUrban'))
mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE);assert EL.save_loaded_asset(mesh,only_if_is_dirty=False)
bp=unreal.load_asset(folder+'/BP_CallesSecundarias');hs=ss.k2_gather_subobject_data_for_blueprint(bp);h=next((h for h in hs if str(lib.get_variable_name(lib.get_data(h)))=='StationAccess'),None)
if not h:h,reason=ss.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=hs[0],new_class=unreal.StaticMeshComponent,blueprint_context=bp));assert not str(reason);ss.rename_subobject(h,unreal.Text('StationAccess'))
o=lib.get_object_for_blueprint(lib.get_data(h),bp);o.set_static_mesh(mesh);o.set_collision_profile_name('BlockAll');o.set_editor_property('can_ever_affect_navigation',True);o.set_editor_property('mobility',unreal.ComponentMobility.STATIC);assert E.compile_blueprint(bp);assert EL.save_loaded_asset(bp,only_if_is_dirty=False)
for a in list(actors.get_all_level_actors()):
 if a.get_class().get_name()=='BP_CallesSecundarias_C':actors.destroy_actor(a)
actors.spawn_actor_from_class(bp.generated_class(),unreal.Vector()).set_actor_label('Calles secundarias y accesos a siete estaciones')
# Visible foot traffic approaches the platforms on protected crossings and their actual ramps.
models=json.loads((r/'work/pure_crowd_models.json').read_text());C=unreal.load_class(None,'/Game/World/BlueprintWorld/Crowd/BP_CrosswalkCitizen.BP_CrosswalkCitizen_C');abp=unreal.load_class(None,'/Game/Delivery/Animation/ABP_StreetCitizen.ABP_StreetCitizen_C')
for i,(st,cr) in enumerate(zip(city['stations'],stplan['crossings'])):
 ang=math.radians(st['yaw']);t=unreal.Vector(math.cos(ang),math.sin(ang),0);rr=unreal.Vector(-t.y,t.x,0);q=unreal.Vector(st['position'][0],st['position'][1],0);at=unreal.Vector(*cr['position']);median=q+t*((at-q).dot(t));curb=at+rr*(cr['halfwidth']-120);points=[curb-t*250+unreal.Vector(0,0,20),median-t*250+unreal.Vector(0,0,4),q-t*2400+unreal.Vector(0,0,4),q-t*1350+unreal.Vector(0,0,90),median+t*250+unreal.Vector(0,0,4),curb+t*250+unreal.Vector(0,0,20),curb+t*450+unreal.Vector(0,0,20),curb-t*450+unreal.Vector(0,0,20)]
 for side in [0,4]:
  a=actors.spawn_actor_from_class(C,points[side]+unreal.Vector(0,0,88));a.set_actor_label('Acceso peatonal estación '+str(i+1));a.set_editor_property('Route',points);a.set_editor_property('RouteIndex',side+1);src=unreal.get_default_object(unreal.load_asset(models[(i*3+side+2)%len(models)]['asset']).generated_class()).get_editor_property('mesh');mc=a.get_component_by_class(unreal.SkeletalMeshComponent);mc.set_skinned_asset_and_update(src.get_skinned_asset(),True);mc.set_anim_instance_class(abp)
  for k,mat in enumerate(src.get_materials()):mc.set_material(k,mat)
assert unreal.EditorLoadingAndSavingUtils.save_current_level()
exec(compile((U/'night_windows.py').read_text(),'NightWindowSelection','exec'),{})
# Rebuild isolated test maps from the final playable level, retaining physical walking and warm lights.
exec(compile((U/'final_scene_snapshots.py').read_text(),'FinalCityQASnapshots','exec'),{})
D=r/'outputs/BogotaUrban';D.mkdir(parents=True,exist_ok=True)
for name in ['Mapa_Bogota_Ambientado.blend','Mobiliario_Bogota_Voxel.blend','placement_plan.json','secondary_road_plan.json','secondary_ground_report.json','station_expansion_plan.json']:shutil.copy2(U/name,D/name)
(D/'integration.json').write_text(json.dumps(dict(secondary_streets=14,connected_secondary_endpoints=28,stations=7,station_passengers=28,additional_buildings=24,crossings=len(plan['crossings']),signals=2*len(plan['crossings']),ordinary_pedestrians=len(city['pedestrians']),traffic_vehicles=150,furniture=dict(collections.Counter(v['type'] for v in plan['furniture'])),runtime='Blueprints'),indent=2));unreal.log('CONNECTED_CITY_FINAL_QA_READY')
