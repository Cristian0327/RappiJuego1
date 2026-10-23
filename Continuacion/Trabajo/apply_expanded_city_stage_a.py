import unreal,json,sys,math,collections,shutil
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;W=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/new_map_audit');sys.path.insert(0,str(r/'Herramientas'));import blueprint_graph as d
E=unreal.BlueprintEditorLibrary;EL=unreal.EditorAssetLibrary;manifest=json.loads((W/'manifest.json').read_text());plan=json.loads((W/'integration_plan.json').read_text());factor=manifest['spacing_expansion'];T=unreal.AssetToolsHelpers.get_asset_tools();mat=unreal.load_asset('/Game/Maps/MapaCompleto/M_MapaVoxel')
for i in range(3):
 name='SM_Mapa_Road_%d'%i;opt=unreal.FbxImportUI();opt.import_mesh=True;opt.import_as_skeletal=False;opt.import_materials=False;opt.import_textures=False;opt.import_animations=False;opt.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH;opt.automated_import_should_detect_type=False;opt.static_mesh_import_data.combine_meshes=True;opt.static_mesh_import_data.auto_generate_collision=False;opt.static_mesh_import_data.vertex_color_import_option=unreal.VertexColorImportOption.REPLACE;opt.static_mesh_import_data.convert_scene=True;opt.static_mesh_import_data.convert_scene_unit=True;task=unreal.AssetImportTask();task.filename=str(W/'export'/(name+'.fbx'));task.destination_path='/Game/Maps/MapaCompleto/Geometry';task.destination_name=name;task.options=opt;task.automated=True;task.replace_existing=True;task.save=True;T.import_asset_tasks([task]);mesh=unreal.load_asset('/Game/Maps/MapaCompleto/Geometry/'+name);assert mesh;mesh.set_material(0,mat);mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE);assert EL.save_loaded_asset(mesh,only_if_is_dirty=False)
bp=unreal.load_asset('/Game/Maps/MapaCompleto/BP_MapaCompletoGeometry');ss=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);lib=unreal.SubobjectDataBlueprintFunctionLibrary;groups=collections.defaultdict(list)
for item in manifest['instances']:
 x,y,z=item['location'];rx,ry,rz=item['rotation'];groups[item['mesh']].append(unreal.Transform(location=unreal.Vector(x*100,-y*100,z*100),rotation=unreal.Rotator(pitch=-ry,yaw=-rz,roll=rx),scale=unreal.Vector(*item['scale'])))
for h in ss.k2_gather_subobject_data_for_blueprint(bp):
 o=lib.get_object_for_blueprint(lib.get_data(h),bp);n=str(lib.get_variable_name(lib.get_data(h)))
 if isinstance(o,unreal.InstancedStaticMeshComponent):o.set_editor_property('can_ever_affect_navigation',n.startswith('Part'))
assert E.compile_blueprint(bp);c=unreal.get_default_object(bp.generated_class())
for i,transforms in enumerate(groups.values()):c.set_editor_property('Transforms%03d'%i,transforms)
b=plan['building_footprints'];c.set_editor_property('BuildingCenters',[unreal.Vector((v[0]+v[2])/2,(v[1]+v[3])/2,0) for v in b]);c.set_editor_property('BuildingExtents',[unreal.Vector2D((v[2]-v[0])/2,(v[3]-v[1])/2) for v in b]);assert EL.save_loaded_asset(bp,only_if_is_dirty=False)
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/MapaCompleto_Integration');actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in list(actors.get_all_level_actors()):
 if a.get_class().get_name() in ['BP_MapaCompletoGeometry_C','BP_BuildingBoundary_C']:actors.destroy_actor(a)
actors.spawn_actor_from_class(bp.generated_class(),unreal.Vector()).set_actor_label('Mapa Completo - Blender + andenes')
s=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/integrate_new_map_routes.py').read_text();s=s[:s.index('# Polyline pedestrian')];s=s.replace('range(1120)','range(1872)').replace("B='1120'","B='1872'").replace("('Y',60000,39)","('Y',78000,51)").replace("('Y',40)","('Y',52)").replace("B='40'","B='52'");s=s.replace("source=source.replace(\"g.setter('ResetLimit'", "source=source.replace(\"('X',42000,27)\",\"('X',54000,35)\");source=source.replace(\"g.setter('ResetLimit'");exec(compile(s,'ExpandedTrafficRoutes','exec'),{})
exec(Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/finish_new_map_crowd.py').read_text())
for a in list(actors.get_all_level_actors()):
 if a.get_class().get_name() in ['BP_CrowdManager_C','BP_TrafficManager_C']:actors.destroy_actor(a)
for path in ['/Game/World/BlueprintWorld/Crowd/BP_CrowdManager','/Game/World/BlueprintWorld/Traffic/BP_TrafficManager']:actors.spawn_actor_from_class(unreal.load_asset(path).generated_class(),unreal.Vector())
for a in actors.get_all_level_actors():
 if isinstance(a,unreal.PlayerStart):a.set_actor_location(unreal.Vector(*plan['player_start']),False,True)
 if isinstance(a,unreal.NavMeshBoundsVolume):
  a.set_actor_location(unreal.Vector(0,0,120),False,True);o,ex=a.get_actor_bounds(False);sc=a.get_actor_scale3d();a.set_actor_scale3d(unreal.Vector(sc.x*40000*factor/max(ex.x,1),sc.y*50000*factor/max(ex.y,1),sc.z*250/max(ex.z,1)))
 if isinstance(a,unreal.RecastNavMesh):a.set_editor_property('tile_pool_size',16384);a.set_editor_property('max_simultaneous_tile_generation_jobs_count',4)
assert unreal.EditorLoadingAndSavingUtils.save_current_level();D=r/'outputs/MapRebuild'
for name in ['manifest.json','integration_plan.json','Mapa_Completo_Andenes_Ampliado.blend']:shutil.copy2(W/name,D/name)
unreal.log('SAME_MAP_EXPANSION_STAGE_A_READY '+str(factor))
