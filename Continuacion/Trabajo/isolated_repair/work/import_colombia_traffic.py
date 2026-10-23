import unreal,json,traceback
from pathlib import Path
OUT=Path(__file__).resolve().parents[1]/'outputs/DeliveryArt/Traffic'
report={}
try:
 tools=unreal.AssetToolsHelpers.get_asset_tools()
 for f in OUT.glob('SK_*.fbx'):
  o=unreal.FbxImportUI();o.automated_import_should_detect_type=False;o.import_mesh=True;o.import_as_skeletal=True;o.import_animations=False;o.import_materials=True;o.import_textures=False;o.create_physics_asset=False;o.mesh_type_to_import=unreal.FBXImportType.FBXIT_SKELETAL_MESH
  o.skeletal_mesh_import_data.convert_scene=True;o.skeletal_mesh_import_data.convert_scene_unit=True;o.skeletal_mesh_import_data.force_front_x_axis=False
  t=unreal.AssetImportTask();t.filename=str(f);t.destination_path='/Game/Traffic';t.destination_name=f.stem;t.automated=True;t.replace_existing=True;t.save=True;t.options=o;tools.import_asset_tasks([t])
  mesh=unreal.load_asset('/Game/Traffic/'+f.stem);assert isinstance(mesh,unreal.SkeletalMesh),f.stem
  # Use the proven city palette, including correct skeletal shader usage.
  slots=mesh.get_editor_property('materials')
  for s in slots:
   n=str(s.material_slot_name).split('_')[0].split('.')[0];target={'Rubber':'Charcoal','Lamp':'Glow','Tail':'Red'}.get(n,n);mat=unreal.load_asset('/Game/World/M_'+target)
   if mat:
    parent=mat.get_editor_property('parent');unreal.MaterialEditingLibrary.set_material_usage(parent,unreal.MaterialUsage.MATUSAGE_SKELETAL_MESH);unreal.MaterialEditingLibrary.recompile_material(parent);s.material_interface=mat
  mesh.set_editor_property('materials',slots);unreal.EditorAssetLibrary.save_loaded_asset(mesh)
  report[f.stem]={'bounds':str(mesh.get_bounds()),'skeleton':mesh.get_editor_property('skeleton').get_path_name()}
 unreal.EditorAssetLibrary.save_directory('/Game/Traffic',only_if_is_dirty=False);unreal.EditorAssetLibrary.save_directory('/Game/World',only_if_is_dirty=True)
 report['status']='PASS'
except Exception:report['status']='FAIL';report['error']=traceback.format_exc();unreal.log_error(report['error'])
(OUT/'unreal_import.json').write_text(json.dumps(report,indent=2))
unreal.log('TRAFFIC_IMPORT '+str(report))
