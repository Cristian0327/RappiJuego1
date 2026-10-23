from pathlib import Path
exec(compile(Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/traffic_gameplay_repair/implement.py').read_text().split('# Recovery never')[0],'helpers','exec'))
assert 'isolated_repair' in root.parts
P=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/map_adaptation_v2');S='/Script/Engine.KismetStringLibrary'
f=unreal.BlueprintFactory();f.set_editor_property('parent_class',unreal.Actor)
b=unreal.load_asset('/Game/QA/BP_AdaptationTrafficProbe') or unreal.AssetToolsHelpers.get_asset_tools().create_asset('BP_AdaptationTrafficProbe','/Game/QA',unreal.Blueprint,f)
addvar(b,'Age',real);E.compile_blueprint(b);g=d.Graph();g.get('Age');op(g,'PlusAge','Add_DoubleDouble',('Age','Age'),('entry','DeltaSeconds'));g.setter('Clock','Age','PlusAge');g.exec('entry','Clock')
g.call('Manager','GetActorOfClass',G,ActorClass=TM);g.node('ManagerCast','cast',type=TM);g.link('Manager','ReturnValue','ManagerCast','Object');field(g,'Cars','Vehicles',('ManagerCast','AsBP Traffic Manager'),TM);g.exec('Clock','Manager');g.node('Each','foreach');g.link('Cars','Vehicles','Each','Array');g.link('Manager','then','Each','Exec')
def line(tag,fields,last):
 prev=None
 for i,(src,pin,kind) in enumerate(fields):
  n=tag+str(i);fn,inp={'real':('Conv_DoubleToString','InDouble'),'int':('Conv_IntToString','InInt'),'vec':('Conv_VectorToString','InVec'),'str':(None,None)}[kind]
  if fn:g.call(n,fn,S);g.link(src,pin,n,inp);value=(n,'ReturnValue')
  else:value=(src,pin)
  g.call(n+'Join','Concat_StrStr',S,A=tag+'|' if prev is None else '');
  if prev:g.link(*prev,n+'Join','A')
  g.link(*value,n+'Join','B');g.call(n+'Sep','Concat_StrStr',S,B='|');g.link(n+'Join','ReturnValue',n+'Sep','A');prev=(n+'Sep','ReturnValue')
 g.call(tag+'Print','PrintString',K,bPrintToScreen='false');g.link(*prev,tag+'Print','InString');g.exec(last,tag+'Print');return tag+'Print'
for n in ['Distance','Speed','NextPosition','NextYaw','HalfLength','HalfWidth','PreviousDistance','PreviousPosition']:
 field(g,n,n,('Each','Array Element'),V)
g.call('ActualName','GetObjectName',K);g.link('Each','Array Element','ActualName','Object');field(g,'ActualLane','Lane',('Each','Array Element'),V);field(g,'ActualGroup','RouteGroup',('ActualLane','Lane'),'/Game/World/BlueprintWorld/Traffic/BP_TrafficLane.BP_TrafficLane_C')
end=line('V2CAR',[('Age','Age','real'),('Each','Array Index','int'),('Distance','Distance','real'),('Speed','Speed','real'),('NextPosition','NextPosition','vec'),('NextYaw','NextYaw','real'),('HalfLength','HalfLength','real'),('HalfWidth','HalfWidth','real'),('PreviousDistance','PreviousDistance','real'),('PreviousPosition','PreviousPosition','vec'),('ActualName','ReturnValue','str'),('ActualGroup','RouteGroup','int')],'Each')
# Foreach loop output uses LoopBody rather than then.
g.links=[([a,'LoopBody',c,p] if a=='Each' and c==end else [a,ap,c,p]) for a,ap,c,p in g.links]
SR='/Game/Traffic/Services/BP_TwoWheelerCitizen.BP_TwoWheelerCitizen_C';g.call('Services','GetAllActorsOfClass',G,ActorClass='/Script/Engine.Character');g.link('Each','Completed','Services','execute');g.node('ServiceEach','foreach');g.link('Services','OutActors','ServiceEach','Array');g.link('Services','then','ServiceEach','Exec');g.call('Name','GetObjectName',K);g.link('ServiceEach','Array Element','Name','Object');g.call('At','K2_GetActorLocation',A);g.link('ServiceEach','Array Element','At','self');g.call('Velocity','GetVelocity',A);g.link('ServiceEach','Array Element','Velocity','self');g.call('Facing','GetActorForwardVector',A);g.link('ServiceEach','Array Element','Facing','self');end=line('V2SERVICE',[('Age','Age','real'),('Name','ReturnValue','str'),('At','ReturnValue','vec'),('Velocity','ReturnValue','vec'),('Facing','ReturnValue','vec')],'ServiceEach');g.links=[([a,'LoopBody',c,p] if a=='ServiceEach' and c==end else [a,ap,c,p]) for a,ap,c,p in g.links]
op(g,'Done','Greater_DoubleDouble',('Age','Age'),B='165');g.branch('QuitWhenDone','Done');g.link('ServiceEach','Completed','QuitWhenDone','execute');g.call('Quit','ExecuteConsoleCommand',K,Command='quit');g.exec('QuitWhenDone','Quit');g.exec('Quit','result');g.exec('QuitWhenDone','result','else');build(b,g,'ReceiveTick');c=unreal.get_default_object(b.generated_class());t=c.get_editor_property('primary_actor_tick');t.set_editor_property('tick_interval',5.);c.set_editor_property('primary_actor_tick',t);save(b)
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/MapaCompleto_Integration');aa=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in aa.get_all_level_actors():
 if a.get_class().get_name()=='BP_AdaptationTrafficProbe_C':aa.destroy_actor(a)
assert unreal.EditorLoadingAndSavingUtils.save_current_level();w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert unreal.EditorLoadingAndSavingUtils.save_map(w,'/Game/QA/AdaptationTraffic');unreal.EditorLoadingAndSavingUtils.load_map('/Game/QA/AdaptationTraffic');aa.spawn_actor_from_class(b.generated_class(),unreal.Vector());assert unreal.EditorLoadingAndSavingUtils.save_current_level();unreal.EditorLoadingAndSavingUtils.new_blank_map(False);unreal.log('V2_TRAFFIC_PROBE_READY')
