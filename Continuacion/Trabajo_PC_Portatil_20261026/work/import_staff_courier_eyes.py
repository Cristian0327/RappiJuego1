import unreal,json
from pathlib import Path
root=Path(__file__).resolve().parents[1];out=root/'outputs/DeliveryArt/People';tools=unreal.AssetToolsHelpers.get_asset_tools();report={}
for path in sorted(out.glob('SK_*.fbx')):
 mesh=unreal.load_asset('/Game/Delivery/People/'+path.stem);assert mesh,path.stem;skeleton=mesh.get_editor_property('skeleton')
 o=unreal.FbxImportUI();o.automated_import_should_detect_type=False;o.import_mesh=True;o.import_as_skeletal=True;o.import_animations=False;o.import_materials=False;o.import_textures=False;o.create_physics_asset=False;o.mesh_type_to_import=unreal.FBXImportType.FBXIT_SKELETAL_MESH;o.skeleton=skeleton
 t=unreal.AssetImportTask();t.filename=str(path);t.destination_path='/Game/Delivery/People';t.destination_name=path.stem;t.automated=True;t.replace_existing=True;t.save=True;t.options=o;tools.import_asset_tasks([t])
 mesh=unreal.load_asset('/Game/Delivery/People/'+path.stem);assert mesh.get_editor_property('skeleton')==skeleton
 slots=mesh.get_editor_property('materials')
 for slot in slots:slot.material_interface=unreal.load_asset('/Game/Delivery/People/NPC_Atlas')
 mesh.set_editor_property('materials',slots);unreal.EditorAssetLibrary.save_loaded_asset(mesh,only_if_is_dirty=False);report[path.stem]={'skeleton':skeleton.get_name(),'status':'PASS'}
(root/'work/staff_eyes_unreal.json').write_text(json.dumps(report,indent=2));unreal.log('STAFF_COURIER_EYES_IMPORTED')
