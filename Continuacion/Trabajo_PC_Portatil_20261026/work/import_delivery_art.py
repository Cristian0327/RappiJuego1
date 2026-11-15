import unreal, json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).parents[1]
art=root/'outputs'/'DeliveryArt'
tasks=[]
for name in ['SM_PhoneVoxel','SM_MotorcycleBodyVoxel']:
    task=unreal.AssetImportTask()
    task.set_editor_property('filename',str(art/(name+'.fbx')))
    task.set_editor_property('destination_path','/Game/Delivery/Art')
    task.set_editor_property('destination_name',name)
    task.set_editor_property('automated',True)
    task.set_editor_property('save',True)
    task.set_editor_property('replace_existing',True)
    options=unreal.FbxImportUI()
    options.set_editor_property('import_mesh',True)
    options.set_editor_property('import_as_skeletal',False)
    options.set_editor_property('import_materials',True)
    options.set_editor_property('import_textures',False)
    options.set_editor_property('mesh_type_to_import',unreal.FBXImportType.FBXIT_STATIC_MESH)
    options.set_editor_property('automated_import_should_detect_type',False)
    task.set_editor_property('options',options)
    tasks.append(task)
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
for task in tasks:
    if not task.get_editor_property('imported_object_paths'):
        raise RuntimeError('No se importó '+task.get_editor_property('filename'))
unreal.EditorAssetLibrary.save_directory('/Game/Delivery/Art',only_if_is_dirty=False,recursive=True)
player=unreal.load_asset('/Game/Delivery/Vehicles/BP_DeliveryRider')
if player:
    cdo=unreal.get_default_object(player.generated_class())
    parts=cdo.get_editor_property('motorcycle_parts')
    if parts:
        parts[0].set_static_mesh(unreal.load_asset('/Game/Delivery/Art/SM_MotorcycleBodyVoxel'))
        parts[0].set_material(0,None)
        parts[0].set_relative_location(unreal.Vector(0,0,-90),False,False)
        parts[0].set_relative_scale3d(unreal.Vector(1,1,1))
        cdo.set_editor_property('motorcycle_parts',[parts[0]])
        unreal.EditorAssetLibrary.save_loaded_asset(player,only_if_is_dirty=False)
unreal.log('DELIVERY_ART_IMPORTED')
