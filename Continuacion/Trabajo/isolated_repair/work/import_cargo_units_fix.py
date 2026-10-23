import unreal,json,ast
from pathlib import Path
root=Path(unreal.Paths.project_dir()).parents[1];project=Path(unreal.Paths.project_dir());art=root/'outputs/DeliveryArt';tools=unreal.AssetToolsHelpers.get_asset_tools()
def import_file(file,dest,options=None):
 t=unreal.AssetImportTask();t.filename=str(file);t.destination_path=dest;t.destination_name=file.stem;t.automated=True;t.replace_existing=True;t.save=True
 if options:t.options=options
 tools.import_asset_tasks([t]);assert t.imported_object_paths,str(file)
 return [unreal.load_asset(p) for p in t.imported_object_paths]
def anim(file,name,skeleton,dest,front=False):
 o=unreal.FbxImportUI();o.import_mesh=False;o.import_animations=True;o.skeleton=skeleton;o.mesh_type_to_import=unreal.FBXImportType.FBXIT_ANIMATION;o.automated_import_should_detect_type=False
 o.anim_sequence_import_data.force_front_x_axis=front;o.anim_sequence_import_data.convert_scene=True;o.anim_sequence_import_data.convert_scene_unit=True
 for a in import_file(file,dest,o):
  if isinstance(a,unreal.AnimSequence):
   if a.get_name()!=name:unreal.EditorAssetLibrary.rename_asset(a.get_path_name(),dest+'/'+name)
   unreal.EditorAssetLibrary.save_loaded_asset(a)

skel=unreal.load_asset('/Game/VoxelExplorer/SK_VoxelExplorer_Skeleton')
for file in (art/'Animation').glob('AN_Mixamo*.fbx'):anim(file,file.stem,skel,'/Game/VoxelExplorer',True)
for file in (art/'Cargo').glob('*.fbx'):
 o=unreal.FbxImportUI();o.import_mesh=True;o.import_materials=True;o.import_textures=False;o.automated_import_should_detect_type=False;o.import_animations=False
 if file.stem.startswith('SK_'):
  o.import_as_skeletal=True;o.skeleton=skel;o.create_physics_asset=False;o.mesh_type_to_import=unreal.FBXImportType.FBXIT_SKELETAL_MESH;o.skeletal_mesh_import_data.force_front_x_axis=True;o.skeletal_mesh_import_data.convert_scene=True;o.skeletal_mesh_import_data.convert_scene_unit=True
 else:o.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH;o.static_mesh_import_data.combine_meshes=True;o.static_mesh_import_data.auto_generate_collision=False
 import_file(file,'/Game/Delivery/Art',o)
for file in (art/'Cargo').glob('T_*.png'):
 for t in import_file(file,'/Game/Delivery/Art'):
  if isinstance(t,unreal.Texture2D):t.set_editor_property('lod_group',unreal.TextureGroup.TEXTUREGROUP_UI);t.set_editor_property('compression_settings',unreal.TextureCompressionSettings.TC_EDITOR_ICON);unreal.EditorAssetLibrary.save_loaded_asset(t)

unreal.log('CORRECTED_BLENDER_RIGS_IMPORTED')
