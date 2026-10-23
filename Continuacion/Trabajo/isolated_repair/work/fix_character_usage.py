import unreal

path = '/Game/VoxelExplorer/M_VoxelExplorerRuntimeRGB'
mat = unreal.load_asset(path)
if not mat:
    raise RuntimeError('Material not found: ' + path)

mel = unreal.MaterialEditingLibrary
mel.set_material_usage(mat, unreal.MaterialUsage.MATUSAGE_SKELETAL_MESH)
mel.recompile_material(mat)
unreal.EditorAssetLibrary.save_loaded_asset(mat)
unreal.EditorAssetLibrary.save_asset(path, only_if_is_dirty=False)
unreal.log('CHAR_USAGE_FIXED material=' + str(mat))
