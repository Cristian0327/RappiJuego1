import unreal
skeleton=unreal.load_asset('/Game/VoxelExplorer/SK_VoxelExplorer_Skeleton')
clips=[unreal.load_asset('/Game/VoxelExplorer/'+n) for n in ['AN_Idle','AN_MixamoWalk','AN_BikePedal','AN_MotoRide','AN_MixamoJump']]
assert skeleton and all(clips)
bp=unreal.DeliveryEditorLibrary.build_locomotion_blueprint(skeleton,*clips)
assert bp,'Animation Blueprint failed'
unreal.EditorAssetLibrary.save_loaded_asset(bp)
unreal.log('LOCOMOTION_ANIMATION_BLUEPRINT_SAVED')
