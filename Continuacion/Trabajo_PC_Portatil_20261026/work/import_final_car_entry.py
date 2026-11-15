import unreal,json,sys,shutil
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;sys.path.insert(0,str(r/'Herramientas'));import blueprint_graph as d
backup=r/'Recuperacion_Migracion_Blueprints/2026-10-19_car_entry_yield'
for rel in ['Delivery/BlueprintGameplay/Player/BP_RoadInteraction.uasset','World/BlueprintWorld/Traffic/BP_TrafficVehicle.uasset','VoxelExplorer/AN_HeroEnterCar.uasset']:
 p=backup/rel;p.parent.mkdir(parents=True,exist_ok=True)
 if not p.exists():shutil.copy2(r/'RappiJuego1/Content'/rel,p)
# Mixamo entry finishes in the same upright seated coordinate basis as the sitting clip.
o=unreal.FbxImportUI();o.import_mesh=False;o.import_animations=True;o.skeleton=unreal.load_asset('/Game/VoxelExplorer/SK_VoxelExplorer_Skeleton');o.mesh_type_to_import=unreal.FBXImportType.FBXIT_ANIMATION;o.automated_import_should_detect_type=False;o.anim_sequence_import_data.force_front_x_axis=True;o.anim_sequence_import_data.convert_scene=True;o.anim_sequence_import_data.convert_scene_unit=True
t=unreal.AssetImportTask();t.filename=str(r/'outputs/DeliveryArt/AnimationRebuild/CarAligned/AN_HeroEnterCar_Aligned.fbx');t.destination_path='/Game/VoxelExplorer';t.destination_name='AN_HeroEnterCar';t.automated=True;t.replace_existing=True;t.replace_existing_settings=True;t.save=True;t.options=o;unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t]);assert t.imported_object_paths

unreal.log('CAR_ENTRY_FINAL_IMPORT_PASS')
