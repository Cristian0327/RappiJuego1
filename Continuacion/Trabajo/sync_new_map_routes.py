import unreal,json,sys,shutil
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;sys.path.insert(0,str(r/'Herramientas'));import blueprint_graph as d
exec(Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/finish_new_map_crowd.py').read_text())
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/MapaCompleto_Integration');actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);c=unreal.get_default_object(unreal.load_class(None,'/Game/World/BlueprintWorld/Crowd/BP_CrowdManager.BP_CrowdManager_C'))
for a in list(actors.get_all_level_actors()):
 if a.get_class().get_name()=='BP_CrowdManager_C':actors.destroy_actor(a)
actors.spawn_actor_from_class(c.get_class(),unreal.Vector())
assert unreal.EditorLoadingAndSavingUtils.save_current_level()
task=unreal.AssetExportTask();task.object=unreal.load_asset('/Game/Maps/MapaCompleto/Geometry/SM_Mapa_000');task.filename='C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/new_map_audit/unreal_export.fbx';task.automated=True;task.prompt=False;task.replace_identical=True;task.exporter=unreal.StaticMeshExporterFBX();opt=unreal.FbxExportOption();opt.vertex_color=True;task.options=opt;assert unreal.Exporter.run_asset_export_task(task)
shutil.copy2(Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/new_map_audit/integration_plan.json'),r/'outputs/MapRebuild/integration_plan.json')
exec(Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/build_new_map_runtime_probe.py').read_text());unreal.log('NEW_MAP_INSTANCE_ROUTES_SYNCED')
