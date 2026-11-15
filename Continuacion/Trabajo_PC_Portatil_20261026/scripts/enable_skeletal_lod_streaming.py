import unreal,json,shutil,gc
from pathlib import Path
R=Path(__file__).resolve().parent.parent;backup=Path((R/'optimization_backup_path.txt').read_text());audit=json.loads((R/'optimization_audit.json').read_text());report=[]
legacy=R/'scripts/retain_legacy_station_asset.py';exec(compile(legacy.read_text(),str(legacy),'exec'),{'__file__':str(legacy)})
sub=unreal.get_editor_subsystem(unreal.SkeletalMeshEditorSubsystem)
for row in audit['skeletal']:
 if row['lods']<3:continue
 mesh=unreal.load_asset(row['path']);source=Path(unreal.Paths.project_content_dir())/(row['path'][6:]+'.uasset');dest=backup/'Content'/(row['path'][6:]+'.uasset');dest.parent.mkdir(parents=True,exist_ok=True)
 if not dest.exists():shutil.copy2(source,dest)
 mesh.set_editor_property('bOverrideLODStreamingSettings',True);mesh.set_editor_property('bSupportLODStreaming',unreal.PerPlatformBool(default=True));mesh.set_editor_property('MaxNumStreamedLODs',unreal.PerPlatformInt(default=2))
 assert sub.get_lod_count(mesh)==row['lods']
 assert unreal.EditorAssetLibrary.save_loaded_asset(mesh,only_if_is_dirty=False);report.append(row['path']);mesh=None;gc.collect();unreal.SystemLibrary.collect_garbage()
 (R/'skeletal_lod_streaming.json').write_text(json.dumps(report,indent=2))
unreal.log('SKELETAL_LOD_STREAMING_READY '+str(len(report)))
