import unreal,json,re
from pathlib import Path
root=Path(unreal.Paths.project_dir()).parents[1]
manifest=json.loads((root/'work/pickup_shelves_manifest.json').read_text())
for row in manifest:
 name=row['asset'];t=unreal.AssetImportTask();t.filename=str(root/'outputs/DeliveryArt/Shops'/(name+'.fbx'));t.destination_path='/Game/Delivery/Stores';t.destination_name=name;t.automated=True;t.replace_existing=True;t.save=True
 o=unreal.FbxImportUI();o.import_mesh=True;o.import_materials=False;o.import_textures=False;o.import_as_skeletal=False;o.automated_import_should_detect_type=False;o.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH;o.static_mesh_import_data.combine_meshes=True;o.static_mesh_import_data.auto_generate_collision=False;t.options=o
 unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t]);assert t.imported_object_paths,name
 mesh=unreal.load_asset('/Game/Delivery/Stores/'+name)
 mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
 slots=list(mesh.get_editor_property('static_materials'));expected=[]
 for index,slot in enumerate(slots):
  material_name=re.sub(r'_\d+$','',str(slot.material_slot_name))
  material=unreal.load_asset('/Game/Delivery/Stores/'+material_name)
  assert material,material_name
  expected.append(material.get_path_name())
  slot.set_editor_property('material_interface',material)
  slots[index]=slot
 mesh.set_editor_property('static_materials',slots)
 unreal.EditorAssetLibrary.save_loaded_asset(mesh)
 check=mesh.get_editor_property('static_materials')
 actual=[s.material_interface.get_path_name() if s.material_interface else None for s in check]
 assert actual==expected,(name,actual,expected)
 unreal.log('SHELF_IMPORTED '+name)
unreal.log('PICKUP_SHELVES_IMPORTED')
