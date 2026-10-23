# Pending: run in the Blueprint authoring project after access is restored.
import unreal
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent
npc=unreal.load_asset('/Game/Crowd/AN_CrowdWalk_Mixamo')
skel=unreal.load_asset('/Game/VoxelExplorer/SK_VoxelExplorer_Skeleton')
o=unreal.FbxImportUI();o.import_mesh=False;o.import_animations=True;o.skeleton=skel;o.mesh_type_to_import=unreal.FBXImportType.FBXIT_ANIMATION;o.automated_import_should_detect_type=False
o.anim_sequence_import_data.force_front_x_axis=True;o.anim_sequence_import_data.convert_scene=True;o.anim_sequence_import_data.convert_scene_unit=True
t=unreal.AssetImportTask();t.filename=str(r/'outputs/DeliveryArt/AnimationRebuild/Upright/AN_CrowdWalk_Rebuilt.fbx');t.destination_path='/Game/VoxelExplorer';t.destination_name='AN_HeroSharedCrowdWalk';t.automated=True;t.replace_existing=True;t.replace_existing_settings=True;t.save=True;t.options=o
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t]);assert list(t.imported_object_paths)
a=unreal.load_asset('/Game/VoxelExplorer/AN_HeroSharedCrowdWalk');assert a.get_editor_property('skeleton')==skel;assert abs(a.get_play_length()-npc.get_play_length())<.05
a.set_editor_property('rate_scale',npc.get_editor_property('rate_scale'));assert unreal.EditorAssetLibrary.save_loaded_asset(a,only_if_is_dirty=False)
s=(r/'work/migrate_rider_animation_pure_blueprint.py').read_text(encoding='utf-8-sig')
assert "'AN_Idle','AN_MixamoWalk','AN_BikePedal'" in s and "B='390'" in s
s=s.replace("'AN_Idle','AN_MixamoWalk','AN_BikePedal'","'AN_Idle','AN_HeroSharedCrowdWalk','AN_BikePedal'").replace("B='390'","B='140'").replace("Min='.35'","Min='.3'")
exec(compile(s,'SharedHeroWalk','exec'),{'__file__':str(r/'work/migrate_rider_animation_pure_blueprint.py')})
unreal.log('SHARED_HERO_NPC_WALK_COMPILED_REQUIRES_RUNTIME_VALIDATION')
