import unreal,json
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;exec(compile((r/'work/import_mount_animations.py').read_text(),str(r/'work/import_mount_animations.py'),'exec'));models=json.loads((r/'outputs/DeliveryArt/Services/civil_bicycles.json').read_text())
skeleton=unreal.load_asset('/Game/Traffic/Services/SK_BicycleCivil_Skeleton')
assert skeleton
for row in models:
 name=row['name'];o=unreal.FbxImportUI();o.skeleton=skeleton;o.import_mesh=True;o.import_as_skeletal=True;o.import_animations=False;o.import_materials=False;o.import_textures=False;o.create_physics_asset=False;o.mesh_type_to_import=unreal.FBXImportType.FBXIT_SKELETAL_MESH;o.automated_import_should_detect_type=False;o.skeletal_mesh_import_data.convert_scene=True;o.skeletal_mesh_import_data.convert_scene_unit=True;o.skeletal_mesh_import_data.vertex_color_import_option=unreal.VertexColorImportOption.REPLACE
 t=unreal.AssetImportTask();t.filename=str(r/'outputs/DeliveryArt/Services'/(name+'.fbx'));t.destination_path='/Game/Traffic/Bicycles';t.destination_name=name;t.automated=True;t.replace_existing=True;t.save=True;t.options=o;unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t]);mesh=unreal.load_asset(t.destination_path+'/'+name);assert mesh and mesh.get_editor_property('skeleton');slots=mesh.get_editor_property('materials')
 for i,slot in enumerate(slots):slot.material_interface=unreal.load_asset('/Game/Traffic/Services/M_ServiceVoxel');slots[i]=slot
 mesh.set_editor_property('materials',slots);assert unreal.EditorAssetLibrary.save_loaded_asset(mesh,only_if_is_dirty=False)
unreal.log('CIVIL_BICYCLES_AND_MOUNT_ANIMATIONS_IMPORTED_PASS')
