import unreal,json,sys
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;sys.path.insert(0,str(r/'Herramientas'));import blueprint_graph as d
E=unreal.BlueprintEditorLibrary;bp=unreal.load_asset('/Game/Maps/MapaCompleto/BP_MapaCompletoGeometry');d.bp=bp;ss=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);lib=unreal.SubobjectDataBlueprintFunctionLibrary;names=[]
for h in ss.k2_gather_subobject_data_for_blueprint(bp):
 o=lib.get_object_for_blueprint(lib.get_data(h),bp);n=str(lib.get_variable_name(lib.get_data(h)))
 if isinstance(o,unreal.InstancedStaticMeshComponent) and not n.startswith('Part'):names.append(n)
def clear_graph(g,last):
 for i,n in enumerate(names):
  g.get(n);g.call('ClearLegacy'+str(i),'ClearInstances','/Script/Engine.InstancedStaticMeshComponent');g.link(n,n,'ClearLegacy'+str(i),'self');g.exec(last,'ClearLegacy'+str(i));last='ClearLegacy'+str(i)
 return last
s=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/integrate_new_map_geometry.py').read_text();a=s.index("assert E.compile_blueprint(bp);c=");b=s.index("unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/Bogota_Blueprint_Integration')",a);part=s[a:b];part=part.replace("g=d.Graph();last='entry'","g=d.Graph();last=clear_graph(g,'entry')")
# Only rebuild the existing construction graph. Reuse stored Part transforms.
groups={}
for h in ss.k2_gather_subobject_data_for_blueprint(bp):
 o=lib.get_object_for_blueprint(lib.get_data(h),bp);n=str(lib.get_variable_name(lib.get_data(h)))
 if isinstance(o,unreal.HierarchicalInstancedStaticMeshComponent) and n.startswith('Part'):groups[int(n[4:])]=o
c=unreal.get_default_object(bp.generated_class());g=d.Graph();last=clear_graph(g,'entry')
for i in sorted(groups):
 n='Part%03d'%i;v='Transforms%03d'%i;g.get(n);g.get(v);g.call('Clear'+n,'ClearInstances','/Script/Engine.InstancedStaticMeshComponent');g.link(n,n,'Clear'+n,'self');g.exec(last,'Clear'+n);g.call('Add'+n,'AddInstances','/Script/Engine.InstancedStaticMeshComponent',bShouldReturnIndices='false',bWorldSpace='false',bUpdateNavigation='true');g.link(n,n,'Add'+n,'self');g.link(v,v,'Add'+n,'InstanceTransforms');g.exec('Clear'+n,'Add'+n);last='Add'+n
g.exec(last,'result');g.build('UserConstructionScript');g=d.Graph();last=clear_graph(g,'entry');g.exec(last,'result');g.build('ReceiveBeginPlay');assert E.compile_blueprint(bp);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/MapaCompleto_Integration');actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in actors.get_all_level_actors():
 if a.get_class().get_name()=='BP_MapaCompletoGeometry_C':a.call_method('UserConstructionScript')
assert unreal.EditorLoadingAndSavingUtils.save_current_level();exec(Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/build_new_map_runtime_probe.py').read_text());unreal.log('NEW_MAP_LEGACY_COLLISION_REMOVED '+str(names))
