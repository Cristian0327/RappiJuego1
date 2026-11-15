import unreal
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent
p='/Game/Traffic/Services/'
s=unreal.load_asset(p+'SK_BicycleCivil_Skeleton') or unreal.EditorAssetLibrary.duplicate_asset(p+'SK_MotoCivilBlue_Skeleton',p+'SK_BicycleCivil_Skeleton')
for color in ['Blue','Red','Yellow']:
 name='SK_BicycleCivil'+color;o=unreal.FbxImportUI();o.import_mesh=True;o.import_as_skeletal=True;o.import_animations=False;o.import_materials=False;o.import_textures=False;o.create_physics_asset=False;o.skeleton=s;o.mesh_type_to_import=unreal.FBXImportType.FBXIT_SKELETAL_MESH;o.automated_import_should_detect_type=False;o.skeletal_mesh_import_data.convert_scene=True;o.skeletal_mesh_import_data.convert_scene_unit=True
 t=unreal.AssetImportTask();t.filename=str(r/'outputs/DeliveryArt/Services'/(name+'.fbx'));t.destination_path='/Game/Traffic/Bicycles';t.destination_name=name;t.automated=True;t.replace_existing=True;t.save=True;t.options=o;unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t]);m=unreal.load_asset('/Game/Traffic/Bicycles/'+name);assert m.get_editor_property('skeleton');slots=m.get_editor_property('materials')
 for i,slot in enumerate(slots):slot.material_interface=unreal.load_asset(p+'M_ServiceVoxel');slots[i]=slot
 m.set_editor_property('materials',slots);unreal.EditorAssetLibrary.save_loaded_asset(m,only_if_is_dirty=False)
unreal.EditorAssetLibrary.save_loaded_asset(s,only_if_is_dirty=False)
b=unreal.load_asset('/Game/Traffic/Services/BP_TwoWheelerCitizen');unreal.get_default_object(b.generated_class()).set_editor_property('VehicleModel',unreal.load_asset('/Game/Traffic/Bicycles/SK_BicycleCivilBlue'));unreal.EditorAssetLibrary.save_loaded_asset(b,only_if_is_dirty=False)
exec(compile((r/'work/build_two_wheeler_runtime_test.py').read_text(encoding='utf-8-sig'),str(r/'work/build_two_wheeler_runtime_test.py'),'exec'))
