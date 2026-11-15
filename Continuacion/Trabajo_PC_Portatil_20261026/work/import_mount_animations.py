import unreal,json
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;src=r/'outputs/DeliveryArt/AnimationRebuild';tasks=[];entries=[]
for who in ['Hero','Crowd']:
 for kind in ['MountBike','MountMoto']:
  name='AN_'+who+kind;entries.append((name,'/Game/VoxelExplorer' if who=='Hero' else '/Game/Crowd','/Game/VoxelExplorer/SK_VoxelExplorer_Skeleton' if who=='Hero' else '/Game/Crowd/SKEL_Crowd'))
entries += [('AN_CrowdBikePedal_Rebuilt','/Game/Crowd','/Game/Crowd/SKEL_Crowd'),('AN_HeroEnterCar_Rebuilt','/Game/VoxelExplorer','/Game/VoxelExplorer/SK_VoxelExplorer_Skeleton'),('AN_HeroSitting_Rebuilt','/Game/VoxelExplorer','/Game/VoxelExplorer/SK_VoxelExplorer_Skeleton')]
for name,folder,skeleton in entries:
 o=unreal.FbxImportUI();o.import_mesh=False;o.import_animations=True;o.skeleton=unreal.load_asset(skeleton);o.mesh_type_to_import=unreal.FBXImportType.FBXIT_ANIMATION;o.automated_import_should_detect_type=False;o.anim_sequence_import_data.force_front_x_axis=True;o.anim_sequence_import_data.convert_scene=True;o.anim_sequence_import_data.convert_scene_unit=True
 t=unreal.AssetImportTask();t.filename=str(src/(name+'.fbx'));t.destination_path=folder;t.destination_name=name.replace('_Rebuilt','');t.automated=True;t.replace_existing=True;t.replace_existing_settings=True;t.save=True;t.options=o;tasks.append(t)
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
for t in tasks:
 a=unreal.load_asset(t.destination_path+'/'+t.destination_name);assert a and a.get_play_length()>0,t.destination_name
unreal.log('PLAYER_AND_NPC_MOUNT_ANIMATIONS_IMPORTED_PASS')
