import unreal,re,json
from pathlib import Path
project=Path(unreal.Paths.project_dir());root=project.parents[1]
rows=json.loads((root/'work/commercial_catalog.json').read_text(encoding='utf-8'))
for row in [r for r in rows if r['label']=='Pharmacy']:
 name='SM_'+row['label']+'Interior'
 task=unreal.AssetImportTask();task.filename=str(root/'outputs/DeliveryArt/Shops'/(name+'.fbx'));task.destination_path='/Game/Delivery/Stores';task.destination_name=name;task.automated=True;task.replace_existing=True;task.save=False
 options=unreal.FbxImportUI();options.import_mesh=True;options.reset_to_fbx_on_material_conflict=True;options.static_mesh_import_data.reorder_material_to_fbx_order=True;options.import_materials=False;options.import_textures=False;options.import_as_skeletal=False;options.automated_import_should_detect_type=False;options.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH;options.static_mesh_import_data.combine_meshes=True;options.static_mesh_import_data.auto_generate_collision=False;task.options=options
 unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
 mesh=unreal.load_asset(task.destination_path+'/'+name);assert mesh,name
 slots=list(mesh.get_editor_property('static_materials'))
 for i,slot in enumerate(slots):
  canonical=re.sub(r'[_\.]\d+$','',str(slot.material_slot_name));mat=unreal.load_asset('/Game/Delivery/Stores/'+canonical);assert mat,canonical;slot.set_editor_property('material_interface',mat);slots[i]=slot
 mesh.set_editor_property('static_materials',slots);mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
 assert unreal.EditorAssetLibrary.save_loaded_asset(mesh,only_if_is_dirty=False)
table=unreal.load_asset('/Game/Delivery/Data/DT_StoreThemes')
assert unreal.DataTableFunctionLibrary.fill_data_table_from_json_file(table,str(project/'DeliveryData/StoreThemes.json'))
assert unreal.EditorAssetLibrary.save_loaded_asset(table,only_if_is_dirty=False)
unreal.log('INTERIOR_COUNTERS_UPDATED '+str(len(rows)))

mesh=unreal.load_asset("/Game/Delivery/Stores/SM_PharmacyInterior")
(root/"work/pharmacy_reset_slots.json").write_text(json.dumps([str(s.material_slot_name) for s in mesh.get_editor_property("static_materials")],indent=2))
