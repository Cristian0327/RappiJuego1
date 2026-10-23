import unreal,shutil,json
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;project=Path(unreal.Paths.project_dir());backup=r/'Recuperacion_Migracion_Blueprints/2026-10-16_animaciones_rehechas';backup.mkdir(parents=True,exist_ok=True);tools=unreal.AssetToolsHelpers.get_asset_tools();reports=[]
items=[('HeroWalk','/Game/VoxelExplorer/AN_MixamoWalk'),('HeroIdle','/Game/VoxelExplorer/AN_Idle'),('HeroJump','/Game/VoxelExplorer/AN_MixamoJump'),('CrowdWalk','/Game/Crowd/AN_CrowdWalk_Mixamo'),('CrowdIdle','/Game/Crowd/AN_CrowdIdle')]
for source,path in items:
 asset=unreal.load_asset(path);assert asset,path;file=project/('Content/'+path[6:]+'.uasset');dest=backup/(path[6:]+'.uasset');dest.parent.mkdir(parents=True,exist_ok=True)
 if not dest.exists():shutil.copy2(file,dest)
 skeleton=asset.get_editor_property('skeleton');o=unreal.FbxImportUI();o.import_mesh=False;o.import_animations=True;o.skeleton=skeleton;o.mesh_type_to_import=unreal.FBXImportType.FBXIT_ANIMATION;o.automated_import_should_detect_type=False;o.anim_sequence_import_data.force_front_x_axis=True;o.anim_sequence_import_data.convert_scene=True;o.anim_sequence_import_data.convert_scene_unit=True
 t=unreal.AssetImportTask();t.filename=str(r/'outputs/DeliveryArt/AnimationRebuild'/('AN_'+source+'_Rebuilt.fbx'));t.destination_path=path.rsplit('/',1)[0];t.destination_name=path.rsplit('/',1)[1];t.automated=True;t.replace_existing=True;t.replace_existing_settings=True;t.save=True;t.options=o;tools.import_asset_tasks([t]);asset=unreal.load_asset(path);assert asset.get_editor_property('skeleton')==skeleton;assert unreal.EditorAssetLibrary.save_loaded_asset(asset,only_if_is_dirty=False);reports.append({'asset':path,'skeleton':skeleton.get_path_name(),'source':t.filename})
(r/'work/rebuilt_mixamo_import.json').write_text(json.dumps(reports,indent=2));unreal.log('REBUILT_MIXAMO_IMPORT_PASS')

