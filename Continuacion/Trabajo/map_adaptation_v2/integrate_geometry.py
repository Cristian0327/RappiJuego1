from pathlib import Path
exec(compile(Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/traffic_gameplay_repair/implement.py').read_text().split('# Recovery never')[0],'helpers','exec'))
assert 'isolated_repair' in root.parts
import collections
P=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/map_adaptation_v2');T=unreal.AssetToolsHelpers.get_asset_tools();folder='/Game/World/BogotaUrban';m=json.loads((P/'manifest.json').read_text());variants=json.loads((P/'frontage_variants.json').read_text());by_source={v['source']:v for v in variants};ss=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);lib=unreal.SubobjectDataBlueprintFunctionLibrary
for file in sorted((P/'export').glob('*.fbx')):
 name=file.stem;dest='/Game/Maps/MapaCompleto/Geometry' if name.startswith('SM_Mapa_') else folder+'/StreetFrontages' if name.startswith('SM_StreetFrontage_') else folder+'/Geometry';path=dest+'/'+name;old=unreal.load_asset(path);mats=[s.material_interface for s in old.static_materials] if old else [unreal.load_asset('/Game/Maps/MapaCompleto/M_MapaVoxel') if name.startswith('SM_StreetFrontage_') else unreal.load_asset(folder+'/M_BogotaUrban')]
 opt=unreal.FbxImportUI();opt.import_mesh=True;opt.import_as_skeletal=False;opt.import_materials=False;opt.import_textures=False;opt.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH;opt.automated_import_should_detect_type=False;im=opt.static_mesh_import_data;im.combine_meshes=True;im.auto_generate_collision=False;im.vertex_color_import_option=unreal.VertexColorImportOption.REPLACE;im.convert_scene=True;im.convert_scene_unit=True;task=unreal.AssetImportTask();task.filename=str(file);task.destination_path=dest;task.destination_name=name;task.options=opt;task.automated=True;task.replace_existing=True;task.save=True;T.import_asset_tasks([task]);mesh=unreal.load_asset(path);assert mesh,path
 for i in range(len(mesh.static_materials)):mesh.set_material(i,mats[min(i,len(mats)-1)])
 body=mesh.get_editor_property('body_setup');body.set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE);body.set_editor_property('double_sided_geometry',True);assert EL.save_loaded_asset(mesh,only_if_is_dirty=False);unreal.log('V2_GEOMETRY_IMPORTED '+name)
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/MapaCompleto_Integration');aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in aa.get_all_level_actors():
 if a.get_class().get_name()=='BP_MapaCompletoGeometry_C' or a.get_actor_label().startswith('Calle original - fachada despejada'):aa.destroy_actor(a)
b=unreal.load_asset('/Game/Maps/MapaCompleto/BP_MapaCompletoGeometry');c=unreal.get_default_object(b.generated_class());groups=collections.OrderedDict()
for row in m['instances']:groups.setdefault(row['mesh'],[]).append(row)
def transform(row):
 x,y,z=row['location'];rx,ry,rz=row['rotation'];return unreal.Transform(location=unreal.Vector(x*100,-y*100,z*100),rotation=unreal.Rotator(pitch=-ry,yaw=-rz,roll=rx),scale=unreal.Vector(*row['scale']))
for i,rows in enumerate(groups.values()):c.set_editor_property('Transforms%03d'%i,[transform(v) for v in rows if v['source'] not in by_source])
assert EL.save_loaded_asset(b,only_if_is_dirty=False);aa.spawn_actor_from_class(b.generated_class(),unreal.Vector())
for row in m['instances']:
 variant=by_source.get(row['source'])
 if not variant:continue
 tr=transform(row);a=aa.spawn_actor_from_class(unreal.StaticMeshActor,tr.translation,tr.rotation.rotator());a.set_actor_scale3d(tr.scale3d);mesh=a.static_mesh_component;mesh.set_static_mesh(unreal.load_asset(folder+'/StreetFrontages/'+variant['name']));mesh.set_collision_profile_name('BlockAll');mesh.set_editor_property('can_ever_affect_navigation',False);a.set_actor_label('Calle original - fachada despejada '+variant['name'])
# Preserve every shop identity, theme and interior. Move only the six crossing a street.
shops=json.loads((P/'shops.json').read_text());identity=[]
for a in aa.get_all_level_actors():
 if a.get_class().get_name()!='BP_DeliveryStore_C':continue
 s=next(v for v in shops if v['name']==a.get_name());a.set_actor_location(unreal.Vector(*s['entrance']),False,True);a.set_editor_property('Built',False);identity.append(dict(name=a.get_name(),point_id=str(a.get_editor_property('PointID')),theme=str(a.get_editor_property('ThemeID')),entrance=s['entrance'],yaw=a.get_actor_rotation().yaw))
(P/'actual_shop_identity.json').write_text(json.dumps(identity,indent=2))
assert unreal.EditorLoadingAndSavingUtils.save_current_level();unreal.EditorLoadingAndSavingUtils.new_blank_map(False);unreal.log('V2_GEOMETRY_INTEGRATION_READY frontages='+str(len(variants)))
