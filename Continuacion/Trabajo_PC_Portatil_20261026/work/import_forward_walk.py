exec((__import__('pathlib').Path(__file__).parent/'import_corrected_rigs.py').read_text().split('for file in (art/')[0])
anim(art/'Animation/AN_MixamoWalk.fbx','AN_MixamoWalk',unreal.load_asset('/Game/VoxelExplorer/SK_VoxelExplorer_Skeleton'),'/Game/VoxelExplorer',True)
unreal.log('FORWARD_WALK_IMPORTED')
