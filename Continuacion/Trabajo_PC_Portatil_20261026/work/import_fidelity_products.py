exec((__import__('pathlib').Path(__file__).parent/'import_corrected_rigs.py').read_text().split('for file in (art/')[0])
for name in ['Milk','Rice','Apples','Burger','Headphones','Keyboard','PhoneBox','FirstAid','Medicine','Bouquet']:
 o=unreal.FbxImportUI();o.import_mesh=True;o.import_materials=True;o.import_textures=False;o.automated_import_should_detect_type=False;o.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH;o.static_mesh_import_data.combine_meshes=True;o.static_mesh_import_data.auto_generate_collision=False
 import_file(art/'HighFidelity'/('SM_'+name+'.fbx'),'/Game/Delivery/Stores',o)
exec((root/'work/fix_store_materials.py').read_text(encoding='utf-8'))
