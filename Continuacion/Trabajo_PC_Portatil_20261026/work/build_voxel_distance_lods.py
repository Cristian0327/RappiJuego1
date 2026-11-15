import unreal,json,shutil
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;reg=unreal.AssetRegistryHelpers.get_asset_registry();reg.search_all_assets(True);settings=unreal.load_asset('/Game/World/BlueprintWorld/Optimization/DA_VoxelLOD');sub=unreal.get_editor_subsystem(unreal.SkeletalMeshEditorSubsystem);report={'skeletal':[],'static':[],'errors':[]};backup=r/'Recuperacion_Migracion_Blueprints/2026-10-19_performance_lods'
for folder in ['/Game/Crowd/People','/Game/Traffic/Detailed','/Game/Traffic/Services']:
 for a in reg.get_assets_by_path(folder,recursive=True):
  if str(a.asset_class_path.asset_name)!='SkeletalMesh':continue
  m=a.get_asset();path=str(a.package_name);old=sub.get_lod_count(m)
  if old>=3:
   report['skeletal'].append(path);continue
  file=Path(unreal.Paths.project_content_dir())/(path[6:]+'.uasset');dest=backup/'Content'/(path[6:]+'.uasset');dest.parent.mkdir(parents=True,exist_ok=True)
  if not dest.exists():shutil.copy2(file,dest)
  m.set_editor_property('lod_settings',settings);ok=sub.regenerate_lod(m,3,False,False)
  if ok and sub.get_lod_count(m)==3:
   assert unreal.EditorAssetLibrary.save_loaded_asset(m,only_if_is_dirty=False);report['skeletal'].append(path)
  else:report['errors'].append(path)
  unreal.log('DISTANCE_LOD '+path+' '+str(ok));(r/'work/distance_lod_result.json').write_text(json.dumps(report,indent=2))
static=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
for a in (reg.get_assets_by_path('/Game/Delivery/Stores',recursive=True) if static else []):
 if str(a.asset_class_path.asset_name)!='StaticMesh':continue
 m=a.get_asset()
 if static.get_lod_count(m)>1:continue
 path=str(a.package_name);file=Path(unreal.Paths.project_content_dir())/(path[6:]+'.uasset');dest=backup/'Content'/(path[6:]+'.uasset');dest.parent.mkdir(parents=True,exist_ok=True)
 if not dest.exists():shutil.copy2(file,dest)
 opts=unreal.StaticMeshReductionOptions();opts.set_editor_property('auto_compute_lod_screen_size',False);opts.set_editor_property('reduction_settings',[unreal.StaticMeshReductionSettings(percent_triangles=ratio,screen_size=size) for ratio,size in [(1.,1.),(.5,.2),(.2,.05)]]);count=static.set_lods(m,opts)
 if count>=3:assert unreal.EditorAssetLibrary.save_loaded_asset(m,only_if_is_dirty=False);report['static'].append(path)
 else:report['errors'].append(path)
(r/'work/distance_lod_result.json').write_text(json.dumps(report,indent=2));unreal.log('DISTANCE_LODS_COMPLETE skeletal='+str(len(report['skeletal']))+' static='+str(len(report['static']))+' errors='+str(len(report['errors'])))
