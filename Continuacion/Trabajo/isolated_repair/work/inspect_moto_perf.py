import unreal,json
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent
report={'has_authoring':hasattr(unreal,'DeliveryEditorLibrary')}
for name in ['SkeletalMeshEditorSubsystem','StaticMeshEditorSubsystem','SkeletalMeshLODSettings','EditorScriptingMeshReductionOptions','EditorScriptingMeshReductionSettings']:
 c=getattr(unreal,name,None);report[name]=str(c.__doc__)[:4500] if c else None
 if c:
  report[name+'_methods']=[n for n in dir(c) if any(s in n for s in ['lod','reduc','screen'])]
for p in ['/Game/Traffic/Services/BP_TwoWheelerCitizen','/Game/Traffic/Services/BP_NpcFacingCoordinator','/Game/Traffic/Services/BP_VoxelRoadVehicle']:
 b=unreal.load_asset(p);report[p]=json.loads(unreal.DeliveryEditorLibrary.audit_blueprint(b)) if b else None
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/Bogota_Blueprint_Integration');actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors();report['actors']=[{'label':a.get_actor_label(),'class':a.get_class().get_path_name()} for a in actors]
(r/'work/moto_perf_inspection.json').write_text(json.dumps(report,indent=2));unreal.log('MOTO_PERF_INSPECTION_READY')
