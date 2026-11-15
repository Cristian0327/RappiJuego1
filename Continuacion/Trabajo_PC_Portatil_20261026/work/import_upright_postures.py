import unreal,json
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;src=r/'outputs/DeliveryArt/AnimationRebuild/Upright';rows=json.loads((src/'posture_validation.json').read_text());mapping={'AN_HeroIdle_Rebuilt':'/Game/VoxelExplorer/AN_Idle','AN_HeroWalk_Rebuilt':'/Game/VoxelExplorer/AN_Walk_InPlace','AN_HeroRun_Rebuilt':'/Game/VoxelExplorer/AN_MixamoWalk','AN_CrowdIdle_Rebuilt':'/Game/Crowd/AN_CrowdIdle','AN_CrowdWalk_Rebuilt':'/Game/Crowd/AN_CrowdWalk_Mixamo'};tasks=[];rates={}
for row in rows:
 n=row['clip'];path=mapping.get(n)
 if not path:
  kind='Walk' if 'Walk_' in n else 'Idle';role=n[3:].replace(kind+'_Rebuilt','');path='/Game/Delivery/People/A_'+role+'_'+('Work' if kind=='Idle' else 'Walk')
 asset=unreal.load_asset(path);assert asset,path;rates[path]=asset.get_editor_property('rate_scale');o=unreal.FbxImportUI();o.import_mesh=False;o.import_animations=True;o.skeleton=asset.get_editor_property('skeleton');o.mesh_type_to_import=unreal.FBXImportType.FBXIT_ANIMATION;o.automated_import_should_detect_type=False;o.anim_sequence_import_data.force_front_x_axis=True;o.anim_sequence_import_data.convert_scene=True;o.anim_sequence_import_data.convert_scene_unit=True;t=unreal.AssetImportTask();source_dir=src/'CompatibleRoots' if n not in mapping else src/'Standing' if 'Idle_' in n and (src/'Standing'/(n+'.fbx')).exists() else src;t.filename=str(source_dir/(n+'.fbx'));t.destination_path=path.rsplit('/',1)[0];t.destination_name=path.rsplit('/',1)[1];t.automated=True;t.replace_existing=True;t.replace_existing_settings=True;t.save=True;t.options=o;tasks.append(t)
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
for task in tasks:
 assert list(task.imported_object_paths),('Rejected animation import',task.filename)
for path,rate in rates.items():
 a=unreal.load_asset(path);a.set_editor_property('rate_scale',rate);unreal.EditorAssetLibrary.save_loaded_asset(a,only_if_is_dirty=False)
unreal.log('UPRIGHT_WALK_IDLE_IMPORTED_PASS '+str(len(tasks)))
