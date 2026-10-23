import unreal,json,sys,math,collections,shutil
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;U=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/urban_refresh');W=U.parent/'new_map_audit';sys.path.insert(0,str(r/'Herramientas'));import blueprint_graph as d
E=unreal.BlueprintEditorLibrary;EL=unreal.EditorAssetLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();ss=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);lib=unreal.SubobjectDataBlueprintFunctionLibrary;folder='/Game/World/BogotaUrban';city=json.loads((W/'integration_plan.json').read_text());manifest=json.loads((W/'manifest.json').read_text());oldcity=json.loads((U/'before_connected_integration_plan.json').read_text())
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/MapaCompleto_Integration');actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
# Import the connected secondary road mesh and the original roads with open junction mouths.
for name in ['SM_Bogota_CallesSecundarias','SM_Mapa_Road_0','SM_Mapa_Road_1','SM_Mapa_Road_2']:
 dest=folder+'/Geometry' if name.startswith('SM_Bogota') else '/Game/Maps/MapaCompleto/Geometry';opt=unreal.FbxImportUI();opt.import_mesh=True;opt.import_as_skeletal=False;opt.import_materials=False;opt.import_textures=False;opt.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH;opt.automated_import_should_detect_type=False;opt.static_mesh_import_data.combine_meshes=True;opt.static_mesh_import_data.auto_generate_collision=False;opt.static_mesh_import_data.vertex_color_import_option=unreal.VertexColorImportOption.REPLACE;opt.static_mesh_import_data.convert_scene=True;opt.static_mesh_import_data.convert_scene_unit=True;task=unreal.AssetImportTask();task.filename=str(U/'export'/(name+'.fbx'));task.destination_path=dest;task.destination_name=name;task.options=opt;task.automated=True;task.replace_existing=True;task.save=True;T.import_asset_tasks([task]);mesh=unreal.load_asset(dest+'/'+name)
 for i in range(len(mesh.static_materials)):mesh.set_material(i,unreal.load_asset(folder+'/M_BogotaUrban'))
 mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE);assert EL.save_loaded_asset(mesh,only_if_is_dirty=False)
# Add exact existing building models without changing the legacy-clearing construction graphs.
bp=unreal.load_asset('/Game/Maps/MapaCompleto/BP_MapaCompletoGeometry');groups=collections.defaultdict(list)
for v in manifest['instances']:
 x,y,z=v['location'];rx,ry,rz=v['rotation'];groups[v['mesh']].append(unreal.Transform(location=unreal.Vector(x*100,-y*100,z*100),rotation=unreal.Rotator(pitch=-ry,yaw=-rz,roll=rx),scale=unreal.Vector(*v['scale'])))
c=unreal.get_default_object(bp.generated_class())
for i,transforms in enumerate(groups.values()):c.set_editor_property('Transforms%03d'%i,transforms)
assert EL.save_loaded_asset(bp,only_if_is_dirty=False)
for a in list(actors.get_all_level_actors()):
 if a.get_class().get_name()=='BP_MapaCompletoGeometry_C':actors.destroy_actor(a)
actors.spawn_actor_from_class(bp.generated_class(),unreal.Vector()).set_actor_label('Mapa completo - barrios y relleno urbano')
# Re-place the instanced Blender furniture, seven stations and protected pedestrian crossings.
s=(U/'place_urban_refresh.py').read_text();s=s[:s.index('# Increase the ordinary city population')];s=s.replace("for x in [-1050,1050]:actors.spawn_actor_from_class", "for x in [-1050,1050]:actors.spawn_actor_from_class").replace("*x,20))","*x,-80))")
exec(compile(s,'ConnectedUrbanDressing','exec'),{})
geom=unreal.load_asset('/Game/Maps/MapaCompleto/BP_MapaCompletoGeometry')
for actor in list(actors.get_all_level_actors()):
 if actor.get_class().get_name()=='BP_MapaCompletoGeometry_C':actors.destroy_actor(actor)
actors.spawn_actor_from_class(geom.generated_class(),unreal.Vector()).set_actor_label('Mapa completo - barrios y relleno urbano')
# The secondary street network is a static Blueprint actor with solid complex collision.
f=unreal.BlueprintFactory();f.set_editor_property('parent_class',unreal.Actor);bp=unreal.load_asset(folder+'/BP_CallesSecundarias') or T.create_asset('BP_CallesSecundarias',folder,unreal.Blueprint,f);hs=ss.k2_gather_subobject_data_for_blueprint(bp);h=next((h for h in hs if str(lib.get_variable_name(lib.get_data(h)))=='RoadNetwork'),None)
if not h:h,reason=ss.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=hs[0],new_class=unreal.StaticMeshComponent,blueprint_context=bp));assert not str(reason);ss.rename_subobject(h,unreal.Text('RoadNetwork'))
o=lib.get_object_for_blueprint(lib.get_data(h),bp);o.set_static_mesh(unreal.load_asset(folder+'/Geometry/SM_Bogota_CallesSecundarias'));o.set_collision_profile_name('BlockAll');o.set_editor_property('can_ever_affect_navigation',True);o.set_editor_property('mobility',unreal.ComponentMobility.STATIC);assert E.compile_blueprint(bp);assert EL.save_loaded_asset(bp,only_if_is_dirty=False);actors.spawn_actor_from_class(bp.generated_class(),unreal.Vector()).set_actor_label('14 calles secundarias conectadas con andenes')
# All seven platform IDs are real bus stops, with four visible passengers each.
bp=unreal.load_asset('/Game/World/BlueprintWorld/Traffic/BP_TrafficVehicle');c=unreal.get_default_object(bp.generated_class());c.set_editor_property('TransitStopPositions',[unreal.Vector(s['bus_stop'][0],s['bus_stop'][1],14) for s in city['stations']]);assert EL.save_loaded_asset(bp,only_if_is_dirty=False)
passengers=[a for a in actors.get_all_level_actors() if a.get_class().get_name()=='BP_StationPassenger_C'];P=unreal.load_asset('/Game/Traffic/Transit/BP_StationPassenger').generated_class();models=json.loads((r/'work/pure_crowd_models.json').read_text())
for a in passengers:actors.destroy_actor(a)
for i,s in enumerate(city['stations']):
 ang=math.radians(s['yaw'])
 for slot in range(4):
  x=380+slot*160;pos=unreal.Vector(s['position'][0]+math.cos(ang)*x,s['position'][1]+math.sin(ang)*x,178);a=actors.spawn_actor_from_class(P,pos,unreal.Rotator(pitch=0,yaw=s['yaw'],roll=0));a.set_editor_property('Station',i);a.set_editor_property('PassengerId',i*4+slot);a.set_actor_label('Pasajero estación '+str(i+1)+' - '+str(slot+1));model=unreal.get_default_object(unreal.load_asset(models[(i*7+slot)%len(models)]['asset']).generated_class()).get_editor_property('mesh');a.set_editor_property('Model',model.get_skinned_asset());a.set_editor_property('SkinMaterial',model.get_material(0))
# Update signal admission arrays to exactly match all visual crossings.
bp=unreal.load_asset('/Game/World/BlueprintWorld/Traffic/BP_TrafficManager');c=unreal.get_default_object(bp.generated_class());plan=json.loads((U/'placement_plan.json').read_text());c.set_editor_property('UrbanCrossingCenters',[unreal.Vector(*s['position']) for s in plan['crossings']]);c.set_editor_property('UrbanCrossingForwards',[unreal.Vector(*s['forward']) for s in plan['crossings']]);assert EL.save_loaded_asset(bp,only_if_is_dirty=False)
# Restore wet response for the paving-link material rebuilt by the placement pass.
ME=unreal.MaterialEditingLibrary;mat=unreal.load_asset(folder+'/M_BogotaPavingBorder');param=ME.create_material_expression(mat,unreal.MaterialExpressionCollectionParameter);param.set_editor_property('collection',unreal.load_asset(folder+'/MPC_BogotaWeather'));param.set_editor_property('parameter_name','Rain');lerp=ME.create_material_expression(mat,unreal.MaterialExpressionLinearInterpolate);lerp.set_editor_property('const_a',.88);lerp.set_editor_property('const_b',.34);ME.connect_material_expressions(param,'',lerp,'Alpha');ME.connect_material_property(lerp,'',unreal.MaterialProperty.MP_ROUGHNESS);ME.recompile_material(mat);assert EL.save_loaded_asset(mat,only_if_is_dirty=False)
assert unreal.EditorLoadingAndSavingUtils.save_current_level();unreal.log('CONNECTED_CITY_INTEGRATED 14 roads 7 stations 24 infill 28 passengers')
