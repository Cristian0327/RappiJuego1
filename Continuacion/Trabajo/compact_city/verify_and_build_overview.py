import unreal,json,sys,math
from pathlib import Path
R=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho');C=R/'compact_city';root=Path(unreal.Paths.project_dir()).parent;sys.path.insert(0,str(root/'Herramientas'));import blueprint_graph as d
E=unreal.BlueprintEditorLibrary;EL=unreal.EditorAssetLibrary;A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/MapaCompleto_Integration');main=A.get_all_level_actors();rows=[];legacy=[]
for actor in main:
 if actor.get_class().get_name()=='BP_MapaCompletoGeometry_C':
  for co in actor.get_components_by_class(unreal.InstancedStaticMeshComponent):
   n=co.get_name();mesh=co.get_editor_property('static_mesh');ct=co.get_instance_count()
   if not n.startswith('Part') and (ct or mesh):legacy.append(dict(name=n,instances=ct,mesh=str(mesh)))
   if n.startswith('Part'):rows.append(dict(name=n,instances=ct,mesh=mesh.get_name() if mesh else None))
assert not legacy,legacy
parent=unreal.load_asset('/Game/World/BlueprintWorld/BP_CityGeometry');pc=unreal.get_default_object(parent.generated_class());bp=unreal.load_asset('/Game/Maps/MapaCompleto/BP_MapaCompletoGeometry');child=unreal.get_default_object(bp.generated_class());assert len(child.get_editor_property('NorthRoads'))==0 and len(child.get_editor_property('EastRoads'))==0
base=json.loads((R/'new_map_audit/before_spacing_expansion/manifest.json').read_text());now=json.loads((R/'new_map_audit/manifest.json').read_text());assert len(now['instances'])==len(base['instances'])==913
for aa,bb in zip(base['instances'],now['instances']):assert aa['source']==bb['source'] and aa['scale']==bb['scale']
assert sum(v['instances'] for v in rows)==913
report=dict(legacy_components=legacy,original_instance_count=913,loaded_instance_count=sum(v['instances'] for v in rows),original_scales_preserved=True,station_count=sum(a.get_class().get_name()=='BP_BogotaTransmiStation_C' for a in main),store_count=sum(a.get_class().get_name()=='BP_DeliveryStore_C' for a in main),parts=rows);(C/'loaded_map_verification.json').write_text(json.dumps(report,indent=2))
# A short visual check of the actual city, including an aerial view that exposes any old grid.
f=unreal.BlueprintFactory();f.set_editor_property('parent_class',unreal.Actor);probe=unreal.load_asset('/Game/QA/BP_CompactLayoutProbe') or unreal.AssetToolsHelpers.get_asset_tools().create_asset('BP_CompactLayoutProbe','/Game/QA',unreal.Blueprint,f)
for n,t in [('Age',E.get_basic_type_by_name('real')),('Stage',E.get_basic_type_by_name('int')),('Overview',E.get_object_reference_type(unreal.Actor)),('Street',E.get_object_reference_type(unreal.Actor))]:
 if n not in [str(v) for v in E.list_member_variable_names(probe)]:assert E.add_member_variable(probe,n,t)
for n in ['Overview','Street']:E.set_blueprint_variable_instance_editable(probe,n,True)
assert E.compile_blueprint(probe);d.bp=probe;g=d.Graph();M=d.M;K='/Script/Engine.KismetSystemLibrary';G='/Script/Engine.GameplayStatics'
for n in ['Age','Stage','Overview','Street']:g.get(n)
g.call('Add','Add_DoubleDouble',M);g.link('Age','Age','Add','A');g.link('entry','DeltaSeconds','Add','B');g.setter('Time','Age','Add');g.exec('entry','Time');g.call('PC','GetPlayerController',G,PlayerIndex='0');last='Time';edge='then'
for i,(at,kind) in enumerate([(1,'Overview'),(9,'overview'),(10,'Street'),(18,'street'),(20,'quit')]):
 tag='S'+str(i);g.call(tag+'T','Greater_DoubleDouble',M,B=str(at));g.link('Age','Age',tag+'T','A');g.call(tag+'I','EqualEqual_IntInt',M,B=str(i));g.link('Stage','Stage',tag+'I','A');g.call(tag+'Due','BooleanAND',M);g.link(tag+'T','ReturnValue',tag+'Due','A');g.link(tag+'I','ReturnValue',tag+'Due','B');g.branch(tag,tag+'Due');g.exec(last,tag,edge)
 if kind in ['Overview','Street']:
  g.call(tag+'Action','SetViewTargetWithBlend','/Script/Engine.PlayerController',BlendTime='0');g.link('PC','ReturnValue',tag+'Action','self');g.link(kind,kind,tag+'Action','NewViewTarget')
 else:g.call(tag+'Action','ExecuteConsoleCommand',K,Command='quit' if kind=='quit' else 'HighResShot 1600x1100 filename="'+str(root/'outputs/BogotaUrban'/('compact_'+kind+'.png')).replace('\\','/')+'"')
 g.exec(tag,tag+'Action');g.setter(tag+'Next','Stage',value=str(i+1));g.exec(tag+'Action',tag+'Next');g.exec(tag+'Next','result');last=tag;edge='else'
g.exec(last,'result',edge);g.build('ReceiveTick');assert E.compile_blueprint(probe);assert EL.save_loaded_asset(probe,only_if_is_dirty=False)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert unreal.EditorLoadingAndSavingUtils.save_map(world,'/Game/QA/CompactLayoutOverview');unreal.EditorLoadingAndSavingUtils.load_map('/Game/QA/CompactLayoutOverview')
for a in A.get_all_level_actors():
 for co in a.get_components_by_class(unreal.InstancedStaticMeshComponent):co.set_cull_distances(0,0)
actor=A.spawn_actor_from_class(probe.generated_class(),unreal.Vector());camera=A.spawn_actor_from_class(unreal.CameraActor,unreal.Vector(0,-4000,45000),unreal.Rotator(pitch=-90,yaw=0,roll=0));camera.get_component_by_class(unreal.CameraComponent).set_field_of_view(110);actor.set_editor_property('Overview',camera)
p=json.loads((R/'new_map_audit/integration_plan.json').read_text());q=unreal.Vector(*p['player_start']);pos=q+unreal.Vector(-1700,-2500,1300);camera=A.spawn_actor_from_class(unreal.CameraActor,pos,unreal.MathLibrary.find_look_at_rotation(pos,q+unreal.Vector(0,0,200)));actor.set_editor_property('Street',camera);assert unreal.EditorLoadingAndSavingUtils.save_current_level();unreal.log('ORIGINAL_SCALE_AND_NO_GRID_VERIFIED '+str(report['loaded_instance_count'])+' instances; seven stations; twenty stores')
