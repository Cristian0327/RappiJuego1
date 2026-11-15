import unreal,json,traceback
from pathlib import Path
root=Path(__file__).resolve().parents[1];out=root/'outputs/DeliveryArt/Crowd';dest='/Game/Crowd';report={}
try:
 tools=unreal.AssetToolsHelpers.get_asset_tools();mel=unreal.MaterialEditingLibrary
 t=unreal.AssetImportTask();t.filename=str(out/'T_CrowdPixelAtlas.png');t.destination_path=dest;t.automated=True;t.replace_existing=True;t.save=True;tools.import_asset_tasks([t])
 tex=unreal.load_asset(dest+'/T_CrowdPixelAtlas');tex.set_editor_property('filter',unreal.TextureFilter.TF_NEAREST);tex.set_editor_property('mip_gen_settings',unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS);tex.set_editor_property('never_stream',True);unreal.EditorAssetLibrary.save_loaded_asset(tex,only_if_is_dirty=False)
 mat=unreal.load_asset(dest+'/M_CrowdPixel') or tools.create_asset('M_CrowdPixel',dest,unreal.Material,unreal.MaterialFactoryNew())
 mel.delete_all_material_expressions(mat)
 n=mel.create_material_expression(mat,unreal.MaterialExpressionTextureSample,-400,0);n.texture=tex
 assert mel.connect_material_property(n,'RGB',unreal.MaterialProperty.MP_BASE_COLOR)
 rough=mel.create_material_expression(mat,unreal.MaterialExpressionConstant,-200,200);rough.r=.82;mel.connect_material_property(rough,'',unreal.MaterialProperty.MP_ROUGHNESS)
 mult=mel.create_material_expression(mat,unreal.MaterialExpressionMultiply,-200,-200);mult.set_editor_property('const_b',.06);mel.connect_material_expressions(n,'RGB',mult,'A');mel.connect_material_property(mult,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
 mat.set_editor_property('used_with_skeletal_mesh',True);mel.recompile_material(mat);unreal.EditorAssetLibrary.save_loaded_asset(mat,only_if_is_dirty=False)
 # Use one independent skeleton with the exact FBX joint axes of these meshes.
 # The protagonist's native skeleton uses a different local bone basis.
 rig=unreal.load_asset(dest+'/SK_CrowdRig')
 if True:
  o=unreal.FbxImportUI();o.automated_import_should_detect_type=False;o.import_mesh=True;o.import_as_skeletal=True;o.import_animations=False;o.import_materials=False;o.import_textures=False;o.create_physics_asset=False;o.mesh_type_to_import=unreal.FBXImportType.FBXIT_SKELETAL_MESH
  o.skeletal_mesh_import_data.force_front_x_axis=True;o.skeletal_mesh_import_data.convert_scene=True;o.skeletal_mesh_import_data.convert_scene_unit=True
  task=unreal.AssetImportTask();task.filename=str(out/'SK_Citizen06.fbx');task.destination_path=dest;task.destination_name='SK_CrowdRig';task.automated=True;task.replace_existing=True;task.replace_existing_settings=True;task.save=True;task.options=o;tools.import_asset_tasks([task]);rig=unreal.load_asset(dest+'/SK_CrowdRig')
 city=unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.load_class(None,'/Script/BogotaVoxel.BogotaCity'),unreal.Vector())
 skeleton=city.create_crowd_skeleton(rig);unreal.EditorAssetLibrary.save_loaded_asset(skeleton,only_if_is_dirty=False)
 assert skeleton,'Crowd skeleton creation failed'
 for f in sorted(out.glob('SK_*.fbx')):
  o=unreal.FbxImportUI();o.automated_import_should_detect_type=False;o.import_mesh=True;o.import_as_skeletal=True;o.import_animations=False;o.import_materials=False;o.import_textures=False;o.create_physics_asset=False;o.mesh_type_to_import=unreal.FBXImportType.FBXIT_SKELETAL_MESH;o.skeleton=skeleton
  o.skeletal_mesh_import_data.force_front_x_axis=True;o.skeletal_mesh_import_data.convert_scene=True;o.skeletal_mesh_import_data.convert_scene_unit=True
  task=unreal.AssetImportTask();task.filename=str(f);task.destination_path=dest+'/People';task.destination_name=f.stem;task.automated=True;task.replace_existing=True;task.replace_existing_settings=True;task.save=True;task.options=o;tools.import_asset_tasks([task])
  mesh=unreal.load_asset(dest+'/People/'+f.stem);assert mesh,f.stem
  city.bind_crowd_mesh(mesh,skeleton)
  unreal.EditorAssetLibrary.save_loaded_asset(skeleton,only_if_is_dirty=False)
  assert mesh.get_editor_property('skeleton')==skeleton
  mesh.modify();slots=mesh.get_editor_property('materials');assert len(slots)==1
  slot=slots[0];slot.material_interface=mat;slots[0]=slot;mesh.set_editor_property('materials',slots);unreal.EditorAssetLibrary.save_loaded_asset(mesh,only_if_is_dirty=False)
  b=mesh.get_bounds();report[f.stem]={'height_cm':b.box_extent.z*2,'material':str(slots[0].material_interface.get_name()),'shared_skeleton':True}
 assert len(report)==60
 report['status']='PASS'
except Exception:report['status']='FAIL';report['error']=traceback.format_exc();unreal.log_error(report['error'])
(out/'unreal_import.json').write_text(json.dumps(report,indent=2));unreal.log('CROWD_IMPORT '+str(report))








