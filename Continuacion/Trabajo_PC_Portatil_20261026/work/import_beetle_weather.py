import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).parent
# Only replace the corrected mesh; preserve the existing paint material graph.
o=unreal.FbxImportUI();o.automated_import_should_detect_type=False;o.import_mesh=True;o.import_as_skeletal=True;o.import_animations=False;o.import_materials=False;o.import_textures=False;o.create_physics_asset=False;o.mesh_type_to_import=unreal.FBXImportType.FBXIT_SKELETAL_MESH
o.skeletal_mesh_import_data.convert_scene=True;o.skeletal_mesh_import_data.convert_scene_unit=True;o.skeletal_mesh_import_data.vertex_color_import_option=unreal.VertexColorImportOption.REPLACE
o.skeleton=unreal.load_asset('/Game/Traffic/Detailed/SK_PrivateBeetle_Skeleton')
t=unreal.AssetImportTask();t.filename=str(root/'outputs/DeliveryArt/TrafficDetailed/SK_PrivateBeetle.fbx');t.destination_path='/Game/Traffic/Detailed';t.destination_name='SK_PrivateBeetle';t.automated=True;t.replace_existing=True;t.save=True;t.options=o;unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t])
mesh=unreal.load_asset('/Game/Traffic/Detailed/SK_PrivateBeetle');slots=mesh.get_editor_property('materials');slots[0].material_interface=unreal.load_asset('/Game/Traffic/Detailed/M_TrafficVoxelVertex');mesh.set_editor_property('materials',slots);unreal.EditorAssetLibrary.save_loaded_asset(mesh,only_if_is_dirty=False)
# White hail cubes share the instanced mesh rendering path used for rain.
m=unreal.load_asset('/Game/World/M_Hail') or unreal.AssetToolsHelpers.get_asset_tools().create_asset('M_Hail','/Game/World',unreal.Material,unreal.MaterialFactoryNew());m.set_editor_property('shading_model',unreal.MaterialShadingModel.MSM_UNLIT);unreal.MaterialEditingLibrary.delete_all_material_expressions(m);c=unreal.MaterialEditingLibrary.create_material_expression(m,unreal.MaterialExpressionConstant3Vector);c.set_editor_property('constant',unreal.LinearColor(.8,.9,1,1));unreal.MaterialEditingLibrary.connect_material_property(c,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR);unreal.MaterialEditingLibrary.set_material_usage(m,unreal.MaterialUsage.MATUSAGE_INSTANCED_STATIC_MESHES);unreal.MaterialEditingLibrary.recompile_material(m);unreal.EditorAssetLibrary.save_loaded_asset(m,only_if_is_dirty=False)
t=unreal.AssetImportTask();t.filename=str(root/'outputs/Weather/Thunder.wav');t.destination_path='/Game/World/Audio';t.destination_name='S_Thunder';t.automated=True;t.replace_existing=True;t.save=True;unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t]);assert unreal.load_asset('/Game/World/Audio/S_Thunder')
exec(compile((root/'work/configure_rain.py').read_text(encoding='utf-8'),str(root/'work/configure_rain.py'),'exec'))
unreal.log('BEETLE_AND_WEATHER_ASSETS_PASS')
