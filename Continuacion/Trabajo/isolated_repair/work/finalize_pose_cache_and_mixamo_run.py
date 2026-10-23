import unreal,json
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent
# Rebuild only the coordinator's callable function, preserving all imported clips and animation rates.
s=(r/'work/fix_requested_animations.py').read_text(encoding='utf-8-sig');prefix=s[:s.index('# Import only')];body=s[s.index('# Post-animation coordinator'):];body=body.replace("g.build('ReceiveTick');save(bp)","E.remove_function_graph(bp,'ReceiveTick');assert unreal.DeliveryEditorLibrary.build_logic_graph(bp,'CorrectPose',json.dumps({'nodes':g.nodes,'links':g.links,'parameters':[]}));save(bp)");exec(compile(prefix+body,'CacheNeutralMeshBasis','exec'),{})
# Give the already-retargeted Mixamo Unarmed Run Forward clip a clear asset name.
run=unreal.load_asset('/Game/VoxelExplorer/AN_Run_Mixamo') or unreal.EditorAssetLibrary.duplicate_asset('/Game/VoxelExplorer/AN_MixamoWalk','/Game/VoxelExplorer/AN_Run_Mixamo');assert run;assert unreal.EditorAssetLibrary.save_loaded_asset(run,only_if_is_dirty=False)
clips=[unreal.load_asset('/Game/VoxelExplorer/'+n) for n in ['AN_Idle','AN_Run_Mixamo','AN_BikePedal','AN_MotoRide','AN_MixamoJump']];assert unreal.DeliveryEditorLibrary.build_character_animation_blueprint('ABP_DeliveryRiderRun',clips[0].get_editor_property('skeleton'),*clips)
exec(compile((r/'work/connect_npc_camera_collision_to_player.py').read_text(encoding='utf-8-sig'),'DirectNpcCamera','exec'),{})
exec(compile((r/'work/build_requested_fixes_qa.py').read_text(encoding='utf-8-sig'),'FinalRequestedQA','exec'),{})
unreal.log('CACHED_NEUTRAL_AND_NAMED_MIXAMO_RUN_PASS')
