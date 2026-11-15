import unreal

mesh = unreal.load_asset('/Game/VoxelExplorer/SK_VoxelExplorer')
unreal.log('CHARACTER_MESH ' + str(mesh))
if mesh:
    for i, slot in enumerate(mesh.get_editor_property('materials')):
        mat = slot.material_interface
        unreal.log('CHARACTER_MATERIAL ' + str(i) + '=' + str(mat) + ' class=' + (mat.get_class().get_name() if mat else 'None'))
        if mat and mat.get_class().get_name() == 'MaterialInstanceConstant':
            try:
                unreal.log('CHARACTER_PARENT ' + str(mat.get_editor_property('parent')))
            except Exception:
                pass
