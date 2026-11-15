import unreal,re,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).parents[1]
report=[]
for name,folder in [('SM_PizzaFront','Shops'),('SM_PizzaInterior','Shops'),('SM_Pizza','HighFidelity')]:
 task=unreal.AssetImportTask();task.filename=str(root/'outputs/DeliveryArt'/folder/(name+'.fbx'));task.destination_path='/Game/Delivery/Review/Pizzeria';task.destination_name=name;task.automated=True;task.replace_existing=True;task.save=False
 options=unreal.FbxImportUI();options.import_mesh=True;options.import_materials=False;options.import_textures=False;options.import_as_skeletal=False;options.automated_import_should_detect_type=False;options.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH;options.static_mesh_import_data.combine_meshes=True;options.static_mesh_import_data.auto_generate_collision=False;task.options=options
 unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
 mesh=unreal.load_asset(task.destination_path+'/'+name);assert mesh,name
 slots=list(mesh.get_editor_property('static_materials'))
 for i,slot in enumerate(slots):
  canonical=re.sub(r'[_\.]\d+$','',str(slot.material_slot_name));mat=unreal.load_asset('/Game/Delivery/Stores/'+canonical);assert mat,canonical;slot.set_editor_property('material_interface',mat);slots[i]=slot
 mesh.set_editor_property('static_materials',slots)
 mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
 assert unreal.EditorAssetLibrary.save_loaded_asset(mesh,only_if_is_dirty=False)
 report.append(mesh.get_path_name())
(root/'work/pizzeria_review_import.json').write_text(json.dumps(report,indent=2))
