import unreal,json,sys
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;sys.path.insert(0,str(r/'Herramientas'));import blueprint_graph as d
bp=unreal.load_asset('/Game/Maps/MapaCompleto/BP_MapaCompletoGeometry');ss=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);lib=unreal.SubobjectDataBlueprintFunctionLibrary;kept=[]
for h in ss.k2_gather_subobject_data_for_blueprint(bp):
 o=lib.get_object_for_blueprint(lib.get_data(h),bp)
 if isinstance(o,unreal.HierarchicalInstancedStaticMeshComponent):
  mesh=o.static_mesh;keep=bool(mesh and (mesh.get_name()=='SM_Mapa_081' or 'Road_' in mesh.get_name()));o.set_editor_property('can_ever_affect_navigation',keep)
  if keep:kept.append(mesh.get_name())
assert unreal.BlueprintEditorLibrary.compile_blueprint(bp);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
bp=unreal.load_asset('/Game/World/BlueprintWorld/Crowd/BP_CrowdManager');d.bp=bp;g=d.Graph();g.exec('entry','result');g.build('ReceiveBeginPlay');assert unreal.BlueprintEditorLibrary.compile_blueprint(bp);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
exec(Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/build_new_map_runtime_probe.py').read_text());unreal.log('NEW_MAP_NAVIGATION_SURFACES '+str(kept))
