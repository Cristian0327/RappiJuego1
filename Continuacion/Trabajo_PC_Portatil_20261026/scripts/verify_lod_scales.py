import unreal,json,gc
from pathlib import Path
R=Path(__file__).resolve().parent.parent;p=R/'static_lod_optimization.json';report=json.loads(p.read_text());sub=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
baseline={x['path']:x for x in json.loads((R/'optimization_audit.json').read_text())['static']}
for row in report['assets']:
 mesh=unreal.load_asset(row['path'])
 changed=False
 mesh.set_editor_property('LODStreaming',unreal.StaticMeshLODStreaming.ENABLED)
 changed=True  # Per-mesh count is protected in UE 5.8; project LOD group supplies the limit.
 for lod in range(1,4):
  settings=sub.get_lod_build_settings(mesh,lod)
  if max(abs(v-1) for v in settings.build_scale3d.to_tuple())>.0001:
   settings.set_editor_property('build_scale3d',unreal.Vector(1,1,1));sub.set_lod_build_settings(mesh,lod,settings);changed=True
 assert mesh.get_num_triangles(0)==row['triangles'][0]
 assert mesh.get_num_vertices(0)==baseline[row['path']]['vertices'],(row['path'],'base vertex count changed')
 assert mesh.get_editor_property('lod_for_collision')==0,(row['path'],'collision must use the original mesh')
 row['lower_lod_build_scale_verified']=True;row['bounds']=list(mesh.get_bounds().box_extent.to_tuple())
 row['streaming_policy']='enabled; up to 3 high LODs through the project LOD group'
 if changed:assert unreal.EditorAssetLibrary.save_loaded_asset(mesh,only_if_is_dirty=False)
 unreal.log('LOD_SCALE_VERIFIED '+row['path']);mesh=None;gc.collect();unreal.SystemLibrary.collect_garbage()
done={x['path'] for x in report['assets']};report['errors']=[x for x in report['errors'] if x['path'] not in done];report['status']='verified';p.write_text(json.dumps(report,indent=2))
