import unreal,json,sys,shutil,collections
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;W=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/new_map_audit');sys.path.insert(0,str(r/'Herramientas'));import blueprint_graph as d
E=unreal.BlueprintEditorLibrary;A=unreal.EditorAssetLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();M=d.M;SC='/Script/Engine.SceneComponent';ISM='/Script/Engine.InstancedStaticMeshComponent';HISM='/Script/Engine.HierarchicalInstancedStaticMeshComponent';actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
backup=r/'Recuperacion_Migracion_Blueprints/2026-10-20_new_map';backup.mkdir(parents=True,exist_ok=True)
for path in ['Maps/Bogota_Blueprint_Integration.umap','World/BlueprintWorld/Traffic/BP_TrafficManager.uasset','World/BlueprintWorld/Crowd/BP_CrowdManager.uasset','World/BlueprintWorld/Traffic/BP_TrafficVehicle.uasset']+['World/BlueprintWorld/Traffic/BP_TrafficLane_%d.uasset'%i for i in range(7)]:
 dst=backup/path;dst.parent.mkdir(parents=True,exist_ok=True)
 if not dst.exists():shutil.copy2(r/'RappiJuego1/Content'/path,dst)
manifest=json.loads((W/'manifest.json').read_text());plan=json.loads((W/'integration_plan.json').read_text());shutil.copy2(W/'integration_plan.json',r/'outputs/MapRebuild/integration_plan.json')
folder='/Game/Maps/MapaCompleto';f=unreal.BlueprintFactory();f.set_editor_property('parent_class',unreal.Actor);bp=unreal.load_asset(folder+'/BP_MapaCompletoGeometry') or T.create_asset('BP_MapaCompletoGeometry',folder,unreal.Blueprint,f);d.bp=bp
ss=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem);lib=unreal.SubobjectDataBlueprintFunctionLibrary;root=ss.k2_gather_subobject_data_for_blueprint(bp)[0];known=[str(n) for n in E.list_member_variable_names(bp)];tt=E.get_array_type(E.get_struct_type(unreal.load_object(None,'/Script/CoreUObject.Transform')))
groups=collections.defaultdict(list)
for item in manifest['instances']:
 x,y,z=item['location'];rx,ry,rz=item['rotation'];groups[item['mesh']].append(unreal.Transform(location=unreal.Vector(x*100,-y*100,z*100),rotation=unreal.Rotator(pitch=-ry,yaw=-rz,roll=rx),scale=unreal.Vector(*item['scale'])))
for i,(mesh,instances) in enumerate(groups.items()):
 name='Part%03d'%i;hn=next((h for h in ss.k2_gather_subobject_data_for_blueprint(bp) if str(lib.get_variable_name(lib.get_data(h)))==name),None)
 if not hn:
  hn,reason=ss.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=root,new_class=unreal.HierarchicalInstancedStaticMeshComponent,blueprint_context=bp));assert not str(reason);assert ss.rename_subobject(hn,unreal.Text(name))
 comp=lib.get_object_for_blueprint(lib.get_data(hn),bp);comp.set_static_mesh(unreal.load_asset(folder+'/Geometry/'+mesh));comp.set_collision_profile_name('BlockAll');comp.set_editor_property('mobility',unreal.ComponentMobility.STATIC);comp.set_editor_property('can_ever_affect_navigation',True);comp.set_cull_distances(40000,60000)
 v='Transforms%03d'%i
 if v not in known:assert E.add_member_variable(bp,v,tt)
assert E.compile_blueprint(bp);c=unreal.get_default_object(bp.generated_class());g=d.Graph();last='entry'
for i,(mesh,instances) in enumerate(groups.items()):
 v='Transforms%03d'%i;n='Part%03d'%i;c.set_editor_property(v,instances);g.get(v);g.get(n);g.call('Clear'+n,'ClearInstances',ISM);g.link(n,n,'Clear'+n,'self');g.exec(last,'Clear'+n);g.call('Add'+n,'AddInstances',ISM,bShouldReturnIndices='false',bWorldSpace='false',bUpdateNavigation='true');g.link(n,n,'Add'+n,'self');g.link(v,v,'Add'+n,'InstanceTransforms');g.exec('Clear'+n,'Add'+n);last='Add'+n
g.exec(last,'result');g.build('UserConstructionScript');assert E.compile_blueprint(bp);assert A.save_loaded_asset(bp,only_if_is_dirty=False)
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/Bogota_Blueprint_Integration');world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert unreal.EditorLoadingAndSavingUtils.save_map(world,'/Game/Maps/MapaCompleto_Integration');unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/MapaCompleto_Integration')
for actor in actors.get_all_level_actors():
 if actor.get_class().get_name() in ['BP_CityGeometry_C','NavModifierVolume']:actors.destroy_actor(actor)
 elif isinstance(actor,unreal.PlayerStart):actor.set_actor_location(unreal.Vector(*plan['player_start']),False,True)
 elif isinstance(actor,unreal.NavMeshBoundsVolume):actor.set_actor_location(unreal.Vector(0,0,1000),False,True);actor.set_actor_scale3d(unreal.Vector(120,140,12))
geom=actors.spawn_actor_from_class(bp.generated_class(),unreal.Vector());geom.set_actor_label('Mapa Completo - Blender + andenes');assert unreal.EditorLoadingAndSavingUtils.save_current_level()
unreal.log('NEW_MAP_GEOMETRY_READY '+str(len(groups))+' groups '+str(len(manifest['instances']))+' instances')
exec(compile(Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/audit_new_map_integration.py').read_text(encoding='utf-8-sig'),'IntegrationAudit','exec'))
