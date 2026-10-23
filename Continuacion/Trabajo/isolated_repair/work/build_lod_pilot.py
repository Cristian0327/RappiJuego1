import unreal,json
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;m=unreal.load_asset('/Game/Crowd/People/SK_Citizen00');sub=unreal.get_editor_subsystem(unreal.SkeletalMeshEditorSubsystem);report={'before':sub.get_lod_count(m),'mesh_methods':[n for n in dir(m) if 'lod' in n]}
try:
 info=list(m.get_editor_property('lod_info'));report['old_info']=str(info)
 for ratio,size in [(.5,.12),(.22,.055)]:
  lod=unreal.SkeletalMeshLODInfo();red=lod.get_editor_property('reduction_settings');red.set_editor_property('num_of_triangles_percentage',ratio);red.set_editor_property('recalc_normals',False);red.set_editor_property('enforce_bone_boundaries',True);lod.set_editor_property('reduction_settings',red);lod.set_editor_property('screen_size',unreal.PerPlatformFloat(default=size));info.append(lod)
 m.set_editor_property('lod_info',info[:3]);report['success']=sub.regenerate_lod(m,3,False,False);report['after']=sub.get_lod_count(m);assert unreal.EditorAssetLibrary.save_loaded_asset(m,only_if_is_dirty=False)
except Exception as e:report['error']=str(e)
(r/'work/lod_pilot_result.json').write_text(json.dumps(report,indent=2));unreal.log('LOD_PILOT_RESULT '+str(report))
