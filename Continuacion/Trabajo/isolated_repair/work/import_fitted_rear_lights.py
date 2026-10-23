import unreal,json
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;tools=unreal.AssetToolsHelpers.get_asset_tools()
for row in json.loads((r/'outputs/DeliveryArt/TrafficDetailed/rear_lights_fitted.json').read_text()):
 name=row['model'];path='/Game/Traffic/Detailed/'+name;o=unreal.FbxImportUI();o.automated_import_should_detect_type=False;o.import_mesh=True;o.import_as_skeletal=True;o.import_animations=False;o.import_materials=False;o.import_textures=False;o.create_physics_asset=False;o.mesh_type_to_import=unreal.FBXImportType.FBXIT_SKELETAL_MESH;o.skeletal_mesh_import_data.convert_scene=True;o.skeletal_mesh_import_data.convert_scene_unit=True;o.skeletal_mesh_import_data.vertex_color_import_option=unreal.VertexColorImportOption.REPLACE;o.skeleton=unreal.load_asset(path+'_Skeleton');t=unreal.AssetImportTask();t.filename=str(r/'outputs/DeliveryArt/TrafficDetailed'/(name+'.fbx'));t.destination_path='/Game/Traffic/Detailed';t.destination_name=name;t.automated=True;t.replace_existing=True;t.save=True;t.options=o;tools.import_asset_tasks([t]);m=unreal.load_asset(path);slots=m.get_editor_property('materials')
 for i,slot in enumerate(slots):slot.material_interface=unreal.load_asset('/Game/Traffic/Detailed/M_TrafficVoxelVertex');slots[i]=slot
 m.set_editor_property('materials',slots);assert unreal.EditorAssetLibrary.save_loaded_asset(m,only_if_is_dirty=False)

unreal.log('FITTED_REAR_LIGHTS_IMPORT_PASS models=7')
