import unreal,json,sys,math,shutil
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;U=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/urban_refresh');sys.path.insert(0,str(r/'Herramientas'));import blueprint_graph as d
E=unreal.BlueprintEditorLibrary;EL=unreal.EditorAssetLibrary;T=unreal.AssetToolsHelpers.get_asset_tools();M=d.M;K='/Script/Engine.KismetSystemLibrary';G='/Script/Engine.GameplayStatics';A='/Script/Engine.Actor';W='/Game/World/BlueprintWorld/BP_WorldState.BP_WorldState_C';TM='/Game/World/BlueprintWorld/Traffic/BP_TrafficManager.BP_TrafficManager_C';V='/Game/World/BlueprintWorld/Traffic/BP_TrafficVehicle.BP_TrafficVehicle_C';folder='/Game/World/BogotaUrban'
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/MapaCompleto_Integration');actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);services=[];speeds=[]
for a in list(actors.get_all_level_actors()):
 if a.get_class().get_name()=='BP_BogotaServiceSignals_C':actors.destroy_actor(a)
 if a.get_class().get_name() in ['BP_CivilMotorcycle_C','BP_PoliceMotorcycle_C','BP_PoliceRoadPatrol_C']:services.append(a);speeds.append(float(a.get_editor_property('RoadSpeed')))
a=actors.spawn_actor_from_class(unreal.load_asset(folder+'/BP_BogotaServiceSignals').generated_class(),unreal.Vector());a.set_editor_property('RoadActors',services);a.set_editor_property('RoadSpeeds',speeds);assert unreal.EditorLoadingAndSavingUtils.save_current_level();unreal.log('SERVICE_SIGNAL_ACTORS '+str(len(services)))
# A view of actual populated city assets under daylight, rain, storm and night.
f=unreal.BlueprintFactory();f.set_editor_property('parent_class',unreal.Actor);bp=unreal.load_asset('/Game/QA/BP_UrbanRefreshProbe') or T.create_asset('BP_UrbanRefreshProbe','/Game/QA',unreal.Blueprint,f)
for n,t in [('WorldState',E.get_object_reference_type(unreal.load_class(None,W))),('Manager',E.get_object_reference_type(unreal.load_class(None,TM))),('Visitor',E.get_object_reference_type(unreal.load_class(None,V)))]+[(n,E.get_object_reference_type(unreal.Actor)) for n in ['StreetCamera','StationCamera','BenchCamera']]:
 if n not in [str(v) for v in E.list_member_variable_names(bp)]:assert E.add_member_variable(bp,n,t)
 E.set_blueprint_variable_instance_editable(bp,n,True)
assert E.compile_blueprint(bp);d.bp=bp;g=d.Graph();g.variables=[{'name':'Age','default':'0'},{'name':'Stage','default':'0'}]
for n in ['Age','Stage','WorldState','Manager','Visitor','StreetCamera','StationCamera','BenchCamera']:g.get(n)
g.call('Clock','Add_DoubleDouble',M);g.link('Age','Age','Clock','A');g.link('entry','DeltaSeconds','Clock','B');g.setter('Now','Age','Clock');g.exec('entry','Now');g.call('PC','GetPlayerController',G,PlayerIndex='0');last='Now';edge='then'
p=json.loads((U/'placement_plan.json').read_text());c=p['crossings'][0];fwd=c['forward'];position=[c['position'][i]-fwd[i]*2500 for i in range(3)];position[2]=14
steps=[(1,'StreetCamera'),(4,'day'),(5,'green_test'),(6,'BenchCamera'),(8,'bench'),(10,'rain'),(11,'StreetCamera'),(24,'rain_view'),(26,'storm'),(27,'StationCamera'),(43,'storm_view'),(46,'night'),(47,'StreetCamera'),(70,'night_view'),(71,'StationCamera'),(73,'station_night'),(85,'red_test'),(115,'done')]
for i,(time,action) in enumerate(steps):
 tag='S'+str(i);g.call(tag+'Time','Greater_DoubleDouble',M,B=str(time));g.link('Age','Age',tag+'Time','A');g.call(tag+'Stage','NearlyEqual_FloatFloat',M,B=str(i),ErrorTolerance='.01');g.link('Stage','Stage',tag+'Stage','A');g.call(tag+'Due','BooleanAND',M);g.link(tag+'Time','ReturnValue',tag+'Due','A');g.link(tag+'Stage','ReturnValue',tag+'Due','B');g.branch(tag,tag+'Due');g.exec(last,tag,edge);end=tag
 if action.endswith('Camera'):
  g.call(tag+'View','SetViewTargetWithBlend','/Script/Engine.PlayerController',BlendTime='.1');g.link('PC','ReturnValue',tag+'View','self');g.link(action,action,tag+'View','NewViewTarget');g.exec(tag,tag+'View');end=tag+'View'
 elif action in ['rain','storm','night']:
  g.node(tag+'Weather','setfield',owner=W,var='DeveloperRainOverride',defaults={'DeveloperRainOverride':'2' if action=='rain' else '3' if action=='storm' else '0'});g.link('WorldState','WorldState',tag+'Weather','self');g.exec(tag,tag+'Weather');end=tag+'Weather'
  if action=='night':g.node(tag+'Night','setfield',owner=W,var='CycleSeconds',defaults={'CycleSeconds':'1100'});g.link('WorldState','WorldState',tag+'Night','self');g.exec(end,tag+'Night');end=tag+'Night'
 elif action in ['green_test','red_test']:
  for n,val in [('NextPosition','(X=%s,Y=%s,Z=14)'%(position[0],position[1])),('NextYaw',str(c['yaw']))]:
   g.node(tag+n,'setfield',owner=V,var=n,defaults={n:val});g.link('Visitor','Visitor',tag+n,'self');g.exec(end,tag+n);end=tag+n
  g.call(tag+'Limit','JunctionClearance',TM);g.link('Manager','Manager',tag+'Limit','self');g.link('Visitor','Visitor',tag+'Limit','Visitor');g.exec(end,tag+'Limit');g.call(tag+'Value','Conv_DoubleToString','/Script/Engine.KismetStringLibrary');g.link(tag+'Limit','ReturnValue',tag+'Value','InDouble');g.call(tag+'Msg','Concat_StrStr','/Script/Engine.KismetStringLibrary',A='URBAN_SIGNAL_'+action+'=');g.link(tag+'Value','ReturnValue',tag+'Msg','B');g.call(tag+'Print','PrintString',K,bPrintToScreen='false');g.link(tag+'Msg','ReturnValue',tag+'Print','InString');g.exec(tag+'Limit',tag+'Print');end=tag+'Print'
 elif action=='done':g.call(tag+'Quit','ExecuteConsoleCommand',K,Command='quit');g.exec(tag,tag+'Quit');end=tag+'Quit'
 else:
  g.call(tag+'Shot','ExecuteConsoleCommand',K,Command='HighResShot 1600x900 filename="'+str(r/'outputs/BogotaUrban'/('urban_'+action+'.png')).replace('\\','/')+'"');g.exec(tag,tag+'Shot');end=tag+'Shot'
 g.setter(tag+'Next','Stage',value=str(i+1));g.exec(end,tag+'Next');g.exec(tag+'Next','result');last=tag;edge='else'
g.exec(last,'result',edge);g.build('ReceiveTick');assert E.compile_blueprint(bp);assert EL.save_loaded_asset(bp,only_if_is_dirty=False)
# Expose only fields touched by the automated scene test.
for asset,names in [('/Game/World/BlueprintWorld/BP_WorldState',['DeveloperRainOverride','CycleSeconds'])]:
 b=unreal.load_asset(asset)
 for name in names:E.set_blueprint_variable_instance_editable(b,name,True)
 assert E.compile_blueprint(b);assert EL.save_loaded_asset(b,only_if_is_dirty=False)
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/MapaCompleto_Integration');world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert unreal.EditorLoadingAndSavingUtils.save_map(world,'/Game/QA/BogotaUrbanRefresh');unreal.EditorLoadingAndSavingUtils.load_map('/Game/QA/BogotaUrbanRefresh');world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();test=actors.spawn_actor_from_class(bp.generated_class(),unreal.Vector());state=next((a for a in actors.get_all_level_actors() if a.get_class().get_name()=='BP_WorldState_C'),None) or actors.spawn_actor_from_class(unreal.load_class(None,W),unreal.Vector());state.set_editor_property('CycleSeconds',320.);state.set_editor_property('DeveloperRainOverride',0);test.set_editor_property('WorldState',state);test.set_editor_property('Manager',next(a for a in actors.get_all_level_actors() if a.get_class().get_name()=='BP_TrafficManager_C'));model=json.loads((r/'work/pure_traffic_vehicle_foundation.json').read_text())['models'][0];visitor=actors.spawn_actor_from_class(unreal.load_asset(model['asset']).generated_class(),unreal.Vector(0,0,-10000));visitor.set_actor_hidden_in_game(True);test.set_editor_property('Visitor',visitor)
t=unreal.Vector(*c['forward']);rr=unreal.Vector(-t.y,t.x,0);base=unreal.Vector(*c['position']);st=p['stations'][0];ang=math.radians(st['yaw']);stt=unreal.Vector(math.cos(ang),math.sin(ang),0);strr=unreal.Vector(-stt.y,stt.x,0);stbase=unreal.Vector(st['position'][0],st['position'][1],0);bench=next(v for v in p['furniture'] if v['type']=='Banca');ang=math.radians(bench['yaw']+180);bt=unreal.Vector(math.cos(ang),math.sin(ang),0);br=unreal.Vector(-bt.y,bt.x,0);bb=unreal.Vector(*bench['position'])
for name,pos,target in [('StreetCamera',base-t*2200+rr*3100+unreal.Vector(0,0,1400),base+unreal.Vector(0,0,140)),('StationCamera',stbase-stt*2000+strr*1700+unreal.Vector(0,0,1200),stbase+stt*300+unreal.Vector(0,0,150)),('BenchCamera',bb-bt*300+br*600+unreal.Vector(0,0,210),bb+unreal.Vector(0,0,95))]:
 cam=actors.spawn_actor_from_class(unreal.CameraActor,pos,unreal.MathLibrary.find_look_at_rotation(pos,target));test.set_editor_property(name,cam)
assert unreal.EditorLoadingAndSavingUtils.save_current_level();exec(compile((U.parent/'build_new_map_runtime_probe.py').read_text(),'UrbanRegressionProbe','exec'),{});exec(compile((U.parent/'build_new_map_transit_qa.py').read_text(),'UrbanTransitRegression','exec'),{});unreal.log('URBAN_VISUAL_SIGNAL_RAIN_NIGHT_QA_READY')



