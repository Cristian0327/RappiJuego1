import unreal
from pathlib import Path
root=Path(unreal.Paths.project_dir()).parents[1];source=root/'outputs/DeliveryArt/Shops/SM_ComponentsInterior.fbx';t=unreal.AssetImportTask();t.filename=str(source);t.destination_path='/Game/Delivery/Stores';t.destination_name=source.stem;t.automated=True;t.replace_existing=True;t.save=True;o=unreal.FbxImportUI();o.import_mesh=True;o.import_materials=False;o.import_textures=False;o.automated_import_should_detect_type=False;o.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH;o.static_mesh_import_data.combine_meshes=True;o.static_mesh_import_data.auto_generate_collision=False;o.static_mesh_import_data.normal_generation_method=unreal.FBXNormalGenerationMethod.BUILT_IN;t.options=o;unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t]);assert t.imported_object_paths
mesh=unreal.load_asset('/Game/Delivery/Stores/SM_ComponentsInterior');mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
slots=mesh.get_editor_property('static_materials')
for slot in slots:
 name=str(slot.get_editor_property('material_slot_name'));canonical=name.split('_00')[0];mat=unreal.load_asset('/Game/Delivery/Stores/'+canonical)
 if mat:slot.set_editor_property('material_interface',mat)
mesh.set_editor_property('static_materials',slots)
unreal.EditorAssetLibrary.save_loaded_asset(mesh);unreal.log('TECH_CLEARANCE_IMPORTED')

