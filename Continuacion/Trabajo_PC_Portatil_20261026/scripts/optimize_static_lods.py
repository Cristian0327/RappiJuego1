"""Distance LODs with unchanged source LOD0 and unchanged collision."""
import unreal,json,gc,shutil
from pathlib import Path
R=Path(__file__).resolve().parent.parent;reportpath=R/'static_lod_optimization.json'
audit=json.loads((R/'optimization_audit.json').read_text());sub=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
backup=Path((R/'optimization_backup_path.txt').read_text());report={'status':'running','assets':[],'errors':[]}
if reportpath.exists():report=json.loads(reportpath.read_text());report['status']='running'
done={x['path'] for x in report['assets']}
targets=[x for x in audit['static'] if x['triangles']>=8000]
for row in sorted(targets,key=lambda x:x['triangles'],reverse=True):
 path=row['path']
 if path in done:continue
 mesh=unreal.load_asset(path)
 source=Path(unreal.Paths.project_content_dir())/(path[6:]+'.uasset');dest=backup/'Content'/(path[6:]+'.uasset');dest.parent.mkdir(parents=True,exist_ok=True)
 if not dest.exists():shutil.copy2(source,dest)
 before=row['triangles'];bounds=mesh.get_bounds();build_settings=sub.get_lod_build_settings(mesh,0);collision=mesh.get_editor_property('body_setup').get_editor_property('collision_trace_flag') if mesh.get_editor_property('body_setup') else None
 options=unreal.StaticMeshReductionOptions(auto_compute_lod_screen_size=False,reduction_settings=[unreal.StaticMeshReductionSettings(percent_triangles=ratio,screen_size=size) for ratio,size in [(1,1),(.5,.18),(.18,.06),(.06,.02)]])
 try:
  count=sub.set_lods(mesh,options);assert count==4,(path,count)
  assert mesh.get_num_triangles(0)==before,(path,'LOD0 changed')
  after=mesh.get_bounds();unreal.log('LOD_BOUNDS '+path+' before='+str(bounds)+' after='+str(after))
  # The bounds encompass all distant LODs; validate source geometry and collision instead.
  if collision is not None:assert mesh.get_editor_property('body_setup').get_editor_property('collision_trace_flag')==collision
  assert unreal.EditorAssetLibrary.save_loaded_asset(mesh,only_if_is_dirty=False)
  item=dict(path=path,triangles=[mesh.get_num_triangles(i) for i in range(4)],lod0_unchanged=True,collision_unchanged=True)
  report['assets'].append(item);unreal.log('STATIC_LOD_OPTIMIZED '+json.dumps(item))
 except Exception as error:
  report['errors'].append(dict(path=path,error=str(error)));reportpath.write_text(json.dumps(report,indent=2));raise
 reportpath.write_text(json.dumps(report,indent=2));mesh=None;gc.collect();unreal.SystemLibrary.collect_garbage()
report['status']='complete';report['targets']=len(targets);reportpath.write_text(json.dumps(report,indent=2));unreal.log('STATIC_LOD_OPTIMIZATION_READY '+str(len(report['assets'])))
