import unreal

mel = unreal.MaterialEditingLibrary
names = [
    'Asphalt', 'Concrete', 'Brick', 'Ochre', 'Cream', 'White', 'Charcoal',
    'Glass', 'Green', 'Leaf', 'Trunk', 'Red', 'Yellow', 'Teal', 'Orange',
    'Glow', 'Blue', 'Stone', 'Earth', 'Grass', 'Roof', 'Steel'
]
fixed = []
for name in names:
    asset = unreal.load_asset('/Game/World/M_' + name)
    if not asset:
        unreal.log_warning('MATERIAL_USAGE missing M_' + name)
        continue
    parent = asset if isinstance(asset, unreal.Material) else asset.get_editor_property('parent')
    if parent:
        mel.set_material_usage(parent, unreal.MaterialUsage.MATUSAGE_INSTANCED_STATIC_MESHES)
        mel.recompile_material(parent)
        unreal.EditorAssetLibrary.save_asset(parent.get_path_name(), only_if_is_dirty=False)
        if asset != parent:
            unreal.EditorAssetLibrary.save_asset(asset.get_path_name(), only_if_is_dirty=False)
        fixed.append(name)
unreal.EditorAssetLibrary.save_directory('/Game/World', only_if_is_dirty=False, recursive=True)
unreal.log('MATERIAL_USAGE_FIXED ' + ','.join(fixed))
