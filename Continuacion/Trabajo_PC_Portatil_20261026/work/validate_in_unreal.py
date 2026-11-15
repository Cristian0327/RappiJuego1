import unreal, json, traceback
from pathlib import Path
OUT=Path(r'C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto/outputs/unreal_v2')
report={'engine_version':unreal.SystemLibrary.get_engine_version(),'status':'RUNNING'}
def log(x):unreal.log('VOXEL_VALIDATION '+str(x))
def task_for(file,name,options=None):
 t=unreal.AssetImportTask();t.filename=str(OUT/file);t.destination_path='/Game/VoxelExplorer';t.destination_name=name
 t.automated=True;t.replace_existing=True;t.save=True
 if options:t.options=options
 return t
def options(animations=False,skeleton=None):
 o=unreal.FbxImportUI();o.automated_import_should_detect_type=False
 o.import_mesh=not animations;o.import_as_skeletal=True;o.import_animations=animations
 o.mesh_type_to_import=unreal.FBXImportType.FBXIT_ANIMATION if animations else unreal.FBXImportType.FBXIT_SKELETAL_MESH
 o.import_materials=False;o.import_textures=False;o.create_physics_asset=not animations
 if skeleton:o.skeleton=skeleton
 d=o.anim_sequence_import_data if animations else o.skeletal_mesh_import_data
 d.import_uniform_scale=1.;d.convert_scene=True;d.convert_scene_unit=True;d.force_front_x_axis=True
 if not animations:
  d.normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS
 return o
try:
 tools=unreal.AssetToolsHelpers.get_asset_tools()
 task=task_for('SK_VoxelExplorer.fbx','SK_VoxelExplorer',options())
 tools.import_asset_tasks([task]);log(task.imported_object_paths)
 assets=[unreal.load_asset(p) for p in task.imported_object_paths]
 mesh=next(a for a in assets if isinstance(a,unreal.SkeletalMesh))
 skeleton=mesh.get_editor_property('skeleton')
 report['skeletal_mesh']=mesh.get_path_name();report['skeleton']=skeleton.get_path_name()
 report['physics_asset']=mesh.get_editor_property('physics_asset').get_path_name()
 comp=unreal.new_object(unreal.SkeletalMeshComponent)
 comp.set_skeletal_mesh_asset(mesh)
 names=[str(comp.get_bone_name(i)) for i in range(comp.get_num_bones())]
 report['bones']=names
 report['parents']={n:str(comp.get_parent_bone(n)) for n in names}
 report['roots']=[n for n in names if report['parents'][n]=='None']
 report['bounds']=str(mesh.get_bounds())
 assert report['roots']==['root'], report['roots']
 assert len(names)==23,len(names)
 assert report['parents']['lowerarm_l']=='upperarm_l'
 assert report['parents']['calf_l']=='thigh_l'
 report['material_slots']=len(mesh.get_editor_property('materials'))
 assert report['material_slots']==1
 tex_task=task_for('T_VoxelExplorer_BaseColor.png','T_VoxelExplorer_BaseColor')
 tools.import_asset_tasks([tex_task]);tex=unreal.load_asset(tex_task.imported_object_paths[0]);tex.filter=unreal.TextureFilter.TF_NEAREST
 tex.srgb=True
 mat=unreal.load_asset('/Game/VoxelExplorer/M_VoxelExplorer')
 if not mat:mat=tools.create_asset('M_VoxelExplorer','/Game/VoxelExplorer',unreal.Material,unreal.MaterialFactoryNew())
 mel=unreal.MaterialEditingLibrary
 mel.delete_all_material_expressions(mat)
 sample=mel.create_material_expression(mat,unreal.MaterialExpressionTextureSample,-400,0);sample.texture=tex
 mel.connect_material_property(sample,'RGB',unreal.MaterialProperty.MP_BASE_COLOR)
 rough=mel.create_material_expression(mat,unreal.MaterialExpressionConstant,-400,200);rough.r=.87
 mel.connect_material_property(rough,'',unreal.MaterialProperty.MP_ROUGHNESS)
 mel.recompile_material(mat)
 slots=mesh.get_editor_property('materials');slots[0].material_interface=mat;mesh.set_editor_property('materials',slots)
 report['animations']={}
 for name in ['Idle','Walk_InPlace','Rig_Test']:
  at=task_for('AN_'+name+'.fbx','AN_'+name,options(True,skeleton));tools.import_asset_tasks([at])
  anim=next(unreal.load_asset(p) for p in at.imported_object_paths if isinstance(unreal.load_asset(p),unreal.AnimSequence))
  report['animations'][name]={'path':anim.get_path_name(),'length_seconds':anim.get_play_length()}
  assert anim.get_play_length()>0
 log('Creating IK rig')
 ik=unreal.load_asset('/Game/VoxelExplorer/IK_VoxelExplorer')
 if not ik:ik=tools.create_asset('IK_VoxelExplorer','/Game/VoxelExplorer',unreal.IKRigDefinition,unreal.IKRigDefinitionFactory())
 controller=unreal.IKRigController.get_controller(ik)
 controller.set_skeletal_mesh(mesh);controller.set_retarget_root('pelvis')
 chains=[('Spine','spine_01','spine_03'),('Head','neck_01','head'),('LeftArm','upperarm_l','hand_l'),('RightArm','upperarm_r','hand_r'),('LeftLeg','thigh_l','ball_l'),('RightLeg','thigh_r','ball_r')]
 for name,start,end in chains:controller.add_retarget_chain(name,start,end,'')
 report['ik_rig']=ik.get_path_name();report['retarget_chains']=chains
 unreal.EditorAssetLibrary.save_directory('/Game/VoxelExplorer',only_if_is_dirty=False,recursive=True)
 report['status']='PASS'
except Exception:
 report['status']='FAIL';report['error']=traceback.format_exc();unreal.log_error(report['error'])
finally:
 (OUT/'unreal_validation.json').write_text(json.dumps(report,indent=2),encoding='utf8')
 log(report)
