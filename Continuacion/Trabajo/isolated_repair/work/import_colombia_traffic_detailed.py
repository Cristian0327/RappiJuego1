import unreal,json,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/DeliveryArt/TrafficDetailed';report={}
try:
 tools=unreal.AssetToolsHelpers.get_asset_tools();mel=unreal.MaterialEditingLibrary;dest='/Game/Traffic/Detailed'
 if globals().get('IMPORT_ONLY_NAMES') and (OUT/'unreal_import.json').exists():report=json.loads((OUT/'unreal_import.json').read_text())
 materials={}
 exec(compile((ROOT/'work/fix_traffic_material.py').read_text(),str(ROOT/'work/fix_traffic_material.py'),'exec'))
 vertexmaster=unreal.load_asset(dest+'/M_TrafficVoxelVertex');materials['TV_VoxelVertex']=vertexmaster
 for f in OUT.glob('SK_*.fbx'):
  if globals().get('IMPORT_ONLY_NAMES') and f.stem not in IMPORT_ONLY_NAMES:continue
  o=unreal.FbxImportUI();o.automated_import_should_detect_type=False;o.import_mesh=True;o.import_as_skeletal=True;o.import_animations=False;o.import_materials=False;o.import_textures=False;o.create_physics_asset=False;o.mesh_type_to_import=unreal.FBXImportType.FBXIT_SKELETAL_MESH
  o.skeletal_mesh_import_data.convert_scene=True;o.skeletal_mesh_import_data.convert_scene_unit=True;o.skeletal_mesh_import_data.force_front_x_axis=False
  o.skeletal_mesh_import_data.vertex_color_import_option=unreal.VertexColorImportOption.REPLACE
  skel=unreal.load_asset(dest+'/'+f.stem+'_Skeleton')
  if skel:o.skeleton=skel
  t=unreal.AssetImportTask();t.filename=str(f);t.destination_path=dest;t.destination_name=f.stem;t.automated=True;t.replace_existing=True;t.save=True;t.options=o;tools.import_asset_tasks([t])
  mesh=unreal.load_asset(dest+'/'+f.stem);assert isinstance(mesh,unreal.SkeletalMesh),f.stem
  mesh.modify();slots=mesh.get_editor_property('materials')
  for index in range(len(slots)):
   s=slots[index]
   key=str(s.material_slot_name).split('.')[0]
   assert key in materials,key
   s.material_interface=materials[key];slots[index]=s
  mesh.set_editor_property('materials',slots);unreal.EditorAssetLibrary.save_loaded_asset(mesh,only_if_is_dirty=False);bounds=mesh.get_bounds();assert bounds.box_extent.x>bounds.box_extent.y*1.3
  assert len(slots)==1,(f.stem,len(slots))
  report[f.stem]={'bounds_cm':{'x':bounds.box_extent.x,'y':bounds.box_extent.y,'z':bounds.box_extent.z},'materials':len(slots),'vertex_colors':True,'skeleton':mesh.get_editor_property('skeleton').get_path_name()}
 unreal.EditorAssetLibrary.save_directory(dest,only_if_is_dirty=False);report['status']='PASS'
except Exception:report['status']='FAIL';report['error']=traceback.format_exc();unreal.log_error(report['error'])
(OUT/'unreal_import.json').write_text(json.dumps(report,indent=2));unreal.log('DETAILED_TRAFFIC_IMPORT '+str(report))
