import unreal,json,sys,shutil,math
from pathlib import Path
P=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/urban_safety');root=Path(unreal.Paths.project_dir()).parent;sys.path.insert(0,str(root/'Herramientas'));import blueprint_graph as d
E=unreal.BlueprintEditorLibrary;EL=unreal.EditorAssetLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();ME=unreal.MaterialEditingLibrary;ss=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);lib=unreal.SubobjectDataBlueprintFunctionLibrary;AS=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);folder='/Game/World/BogotaUrban';backup=P/'asset_backup';backup.mkdir(exist_ok=True)
def backup_asset(path):
 rel=path.replace('/Game/','')+('.umap' if path.endswith('MapaCompleto_Integration') else '.uasset');src=root/'RappiJuego1/Content'/rel;dst=backup/rel
 if src.exists() and not dst.exists():dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
for path in ['/Game/Maps/MapaCompleto_Integration','/Game/Maps/MapaCompleto/BP_MapaCompletoGeometry',folder+'/BP_BogotaUrbanDressing','/Game/Delivery/BlueprintGameplay/Player/BP_BlueprintRider','/Game/Traffic/Detailed/M_TrafficOpaqueSafe_20261021']:backup_asset(path)
# The previous material's ComponentMask input was unconnected: replace it with the actual UV1 value.
mat=unreal.load_asset('/Game/Traffic/Detailed/M_TrafficOpaqueSafe_20261021');nodes=[v for v in unreal.ObjectIterator(unreal.MaterialExpression) if v.get_outer()==mat];uv=next(v for v in nodes if isinstance(v,unreal.MaterialExpressionTextureCoordinate));customs=[v for v in nodes if isinstance(v,unreal.MaterialExpressionCustom)]
for n in customs:
 n.set_editor_property('code',n.get_editor_property('code').replace('saturate(Mask)','saturate(Mask.x)'));assert ME.connect_material_expressions(uv,'',n,'Mask')
for n in nodes:
 if isinstance(n,unreal.MaterialExpressionComponentMask):ME.delete_material_expression(mat,n)
ME.recompile_material(mat);assert EL.save_loaded_asset(mat,only_if_is_dirty=False)
# Reimport the Blender models with their plinths removed; original materials/vertex colors remain opaque.
imports=[(v,'/Game/Maps/MapaCompleto/Geometry') for v in sorted((P/'export').glob('SM_Mapa_*.fbx'))]+[(P/'export/SM_Bogota_UrbanSolidFloor.fbx',folder+'/Geometry')]
for file,dest in imports:
 path=dest+'/'+file.stem;backup_asset(path);old=unreal.load_asset(path);mats=[v.material_interface for v in old.static_materials] if old else [unreal.load_asset(folder+'/M_BogotaUrban')];opt=unreal.FbxImportUI();opt.import_mesh=True;opt.import_as_skeletal=False;opt.import_materials=False;opt.import_textures=False;opt.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH;opt.automated_import_should_detect_type=False;im=opt.static_mesh_import_data;im.combine_meshes=True;im.auto_generate_collision=False;im.vertex_color_import_option=unreal.VertexColorImportOption.REPLACE;im.convert_scene=True;im.convert_scene_unit=True;task=unreal.AssetImportTask();task.filename=str(file);task.destination_path=dest;task.destination_name=file.stem;task.options=opt;task.automated=True;task.replace_existing=True;task.save=True;T.import_asset_tasks([task]);mesh=unreal.load_asset(path);assert mesh
 for i in range(len(mesh.static_materials)):mesh.set_material(i,mats[min(i,len(mats)-1)])
 body=mesh.get_editor_property('body_setup');body.set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE);body.set_editor_property('double_sided_geometry',True);assert EL.save_loaded_asset(mesh,only_if_is_dirty=False)
 unreal.log('FLUSH_ARCHITECTURE_IMPORTED '+file.stem)
# Every urban plot now has its local floor at zero and is placed at the common 20cm pavement datum.
bp=unreal.load_asset('/Game/Maps/MapaCompleto/BP_MapaCompletoGeometry');cdo=unreal.get_default_object(bp.generated_class());changed=0
for h in ss.k2_gather_subobject_data_for_blueprint(bp):
 co=lib.get_object_for_blueprint(lib.get_data(h),bp);n=str(lib.get_variable_name(lib.get_data(h)))
 if not isinstance(co,unreal.InstancedStaticMeshComponent) or not n.startswith('Part'):continue
 mesh=co.get_editor_property('static_mesh')
 if not mesh or not (P/'export'/(mesh.get_name()+'.fbx')).exists():continue
 key='Transforms'+n[4:];trans=list(cdo.get_editor_property(key))
 for tr in trans:
  p=tr.translation;p.z=20;tr.translation=p;changed+=1
 cdo.set_editor_property(key,trans)
assert EL.save_loaded_asset(bp,only_if_is_dirty=False)
# Correct handedness of physical road and terrain triangles too.
for path in ['/Game/Maps/MapaCompleto/Geometry/SM_Mapa_081']+['/Game/Maps/MapaCompleto/Geometry/SM_Mapa_Road_'+str(i) for i in range(3)]+[folder+'/Geometry/SM_Bogota_CallesSecundarias']:
 backup_asset(path);mesh=unreal.load_asset(path);body=mesh.get_editor_property('body_setup');body.set_editor_property('double_sided_geometry',True);body.set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE);EL.save_loaded_asset(mesh,only_if_is_dirty=False)
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/MapaCompleto_Integration');moves=json.loads((P/'furniture_relocations.json').read_text());bp=unreal.load_asset(folder+'/BP_BogotaUrbanDressing');cdo=unreal.get_default_object(bp.generated_class());groups={}
for row in moves:groups.setdefault(row['component'],[]).append(row)
for name,rows in groups.items():
 transforms=list(cdo.get_editor_property(name+'Transforms'))
 for row in rows:
  tr=transforms[row['index']];tr.translation=unreal.Vector(*row['new']);transforms[row['index']]=tr
 cdo.set_editor_property(name+'Transforms',transforms)
# Light lenses share the relocated street-lamp transforms.
if 'UrbanPart0' in groups:cdo.set_editor_property('UrbanPart1Transforms',cdo.get_editor_property('UrbanPart0Transforms'))
assert EL.save_loaded_asset(bp,only_if_is_dirty=False)
for a in list(AS.get_all_level_actors()):
 cl=a.get_class().get_name()
 if cl in ['BP_MapaCompletoGeometry_C','BP_BogotaUrbanDressing_C','BP_UrbanSolidFloor_C','BP_MapTraversal_C']:AS.destroy_actor(a);continue
 if cl in ['BP_BogotaStreetLight_C','BP_BogotaBenchOccupant_C']:
  at=a.get_actor_location();row=next((r for r in moves if ('Farola' if cl=='BP_BogotaStreetLight_C' else 'Banca') in r['mesh'] and math.hypot(at.x-r['old'][0],at.y-r['old'][1])<30),None)
  if row:a.set_actor_location(unreal.Vector(*row['new']),False,True)
for path in ['/Game/Maps/MapaCompleto/BP_MapaCompletoGeometry',folder+'/BP_BogotaUrbanDressing']:AS.spawn_actor_from_class(unreal.load_asset(path).generated_class(),unreal.Vector())
f=unreal.BlueprintFactory();f.set_editor_property('parent_class',unreal.Actor);bp=unreal.load_asset(folder+'/BP_UrbanSolidFloor') or T.create_asset('BP_UrbanSolidFloor',folder,unreal.Blueprint,f);hs=ss.k2_gather_subobject_data_for_blueprint(bp);h=next((h for h in hs if str(lib.get_variable_name(lib.get_data(h)))=='Ground'),None)
if not h:h,why=ss.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=hs[0],new_class=unreal.StaticMeshComponent,blueprint_context=bp));assert not str(why);ss.rename_subobject(h,unreal.Text('Ground'))
co=lib.get_object_for_blueprint(lib.get_data(h),bp);co.set_static_mesh(unreal.load_asset(folder+'/Geometry/SM_Bogota_UrbanSolidFloor'));co.set_collision_profile_name('BlockAll');co.set_visibility(False,False);co.set_hidden_in_game(True,False);co.set_editor_property('can_ever_affect_navigation',True);co.set_editor_property('mobility',unreal.ComponentMobility.STATIC);assert E.compile_blueprint(bp);EL.save_loaded_asset(bp,only_if_is_dirty=False);AS.spawn_actor_from_class(bp.generated_class(),unreal.Vector()).set_actor_label('Suelo urbano sólido continuo')
# Walking crosses a normal curb directly, while tall walls remain blocking.
bp=unreal.load_asset('/Game/Delivery/BlueprintGameplay/Player/BP_BlueprintRider');cdo=unreal.get_default_object(bp.generated_class());mov=cdo.get_editor_property('character_movement');mov.set_editor_property('max_step_height',45.);mov.set_editor_property('use_flat_base_for_floor_checks',True);mov.set_editor_property('perch_radius_threshold',12.);assert EL.save_loaded_asset(bp,only_if_is_dirty=False)
exec(compile((P/'build_traversal_blueprint.py').read_text(),'BlueprintFlightAndRecovery','exec'),{})
bp=unreal.load_asset(folder+'/BP_MapTraversal');cdo=unreal.get_default_object(bp.generated_class());start=next(a for a in AS.get_all_level_actors() if isinstance(a,unreal.PlayerStart));cdo.set_editor_property('SafeLocation',start.get_actor_location());assert EL.save_loaded_asset(bp,only_if_is_dirty=False);AS.spawn_actor_from_class(bp.generated_class(),unreal.Vector()).set_actor_label('VOLAR / vuelo de desarrollador y recuperación de caídas');world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();world.get_world_settings().set_editor_property('kill_z',-20000.);assert unreal.EditorLoadingAndSavingUtils.save_current_level();shutil.copy2(P/'Mapa_Bogota_Nivelado.blend',root/'outputs/BogotaUrban/Mapa_Bogota_Ambientado.blend');shutil.copy2(P/'leveled_manifest.json',root/'outputs/BogotaUrban/manifest.json');(P/'implementation_report.json').write_text(json.dumps(dict(architecture_meshes=len(imports)-1,leveled_instances=changed,relocated_furniture=len(moves),floor_strips=537,flight='ESOYAM then VOLAR or F8; space up, Ctrl down, Shift fast',blueprint_runtime=True),indent=2));unreal.log('URBAN_SAFETY_TEXTURES_LEVELING_FLIGHT_SAVED')
