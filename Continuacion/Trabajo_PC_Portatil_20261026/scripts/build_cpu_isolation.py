"""Diagnostic map only: progressively stop groups to attribute CPU cost."""
import unreal,json,sys
from pathlib import Path
R=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(R/'Herramientas'));import blueprint_graph as d
if not unreal.EditorAssetLibrary.does_asset_exist('/Game/QA/BP_CPUIsolation'):
 factory=unreal.BlueprintFactory();factory.set_editor_property('parent_class',unreal.Actor);assert unreal.AssetToolsHelpers.get_asset_tools().create_asset('BP_CPUIsolation','/Game/QA',unreal.Blueprint,factory)
probe=unreal.load_asset('/Game/QA/BP_CPUIsolation')
if 'Preset' not in [str(x) for x in unreal.BlueprintEditorLibrary.list_member_variable_names(probe)]:assert unreal.BlueprintEditorLibrary.add_member_variable(probe,'Preset',unreal.BlueprintEditorLibrary.get_basic_type_by_name('int'))
assert unreal.BlueprintEditorLibrary.compile_blueprint(probe)
src=(R/'scripts/build_optimization_matrix.py').read_text(encoding='utf-8-sig').replace('BP_OptimizationFrameProbe','BP_CPUIsolation').replace('[15,60,5]','[10,20,3]').replace('BENCHMARK_','CPU_ISOLATION_')
shot='Shot showui filename="'+str(R/'AdversarialQA_20261026/screens/city_cpu.png').replace('\\','/')+'"'
src=src.replace("g.call('CSVStart','ExecuteConsoleCommand',K,Command='csvprofile start');g.exec(tail,'CSVStart')","g.call('CityShot','ExecuteConsoleCommand',K,Command="+repr(shot)+");g.exec(tail,'CityShot');g.call('CSVStart','ExecuteConsoleCommand',K,Command='csvprofile start');g.exec('CityShot','CSVStart')")
scope={'__file__':str(R/'scripts/build_optimization_matrix.py'),'__name__':'__main__'};exec(compile(src,'CPUIsolationMatrix','exec'),scope)
b=scope['bp'];P=b.generated_class().get_path_name();E=unreal.BlueprintEditorLibrary;M=d.M;K='/Script/Engine.KismetSystemLibrary';GS='/Script/Engine.GameUserSettings';G='/Script/Engine.GameplayStatics';A='/Script/Engine.Actor';AC='/Script/Engine.ActorComponent'
g=d.Graph();g.get('Preset');last='entry';edge='then'
groups=[(1,'/Game/World/BlueprintWorld/Traffic/BP_TrafficManager'),(2,'/Game/World/BlueprintWorld/Crowd/BP_StreetCitizen'),(2,'/Game/World/BlueprintWorld/Crowd/BP_CrowdManager'),(2,'/Game/World/BlueprintWorld/Crowd/BP_CrowdFarBudget'),(2,'/Game/World/BlueprintWorld/Crowd/BP_CrowdVisibility'),(3,'/Game/Traffic/Services/BP_VoxelRoadVehicle'),(3,'/Game/Traffic/Services/BP_TwoWheelerCitizen'),(3,'/Game/Traffic/Services/BP_PoliceOfficer'),(3,'/Game/Traffic/Services/BP_ServiceTrafficCache')]
for i,(phase,path) in enumerate(groups):
 n='Group'+str(i);g.call(n+'Due','GreaterEqual_IntInt',M,B=str(phase));g.link('Preset','Preset',n+'Due','A');g.branch(n,n+'Due');g.exec(last,n,edge);g.call(n+'Find','GetAllActorsOfClass',G,ActorClass=path+'.'+path.rsplit('/',1)[-1]+'_C');g.exec(n,n+'Find');g.node(n+'Each','foreach');g.link(n+'Find','OutActors',n+'Each','Array');g.link(n+'Find','then',n+'Each','Exec');g.call(n+'Stop','SetActorTickEnabled',A,bEnabled='false');g.link(n+'Each','Array Element',n+'Stop','self');g.link(n+'Each','LoopBody',n+'Stop','execute');g.call(n+'Components','K2_GetComponentsByClass',A,ComponentClass=AC);g.link(n+'Each','Array Element',n+'Components','self');g.node(n+'EveryComponent','foreach');g.link(n+'Components','ReturnValue',n+'EveryComponent','Array');g.link(n+'Stop','then',n+'EveryComponent','Exec');g.call(n+'StopComponent','SetComponentTickEnabled',AC,bEnabled='false');g.link(n+'EveryComponent','Array Element',n+'StopComponent','self');g.link(n+'EveryComponent','LoopBody',n+'StopComponent','execute')
 # Merge the skipped and completed branches through a small no-op log.
 g.call(n+'Done','PrintString',K,bPrintToScreen='false',InString='CPU isolation checked '+path);g.exec(n,n+'Done','else');g.link(n+'Each','Completed',n+'Done','execute');last=n+'Done';edge='then'
g.call('NoUI','GreaterEqual_IntInt',M,B='4');g.link('Preset','Preset','NoUI','A');g.branch('UIPhase','NoUI');g.exec(last,'UIPhase');g.exec('UIPhase','result','else');g.call('Widgets','GetAllWidgetsOfClass','/Script/UMG.WidgetBlueprintLibrary',WidgetClass='/Script/UMG.UserWidget',TopLevelOnly='true');g.exec('UIPhase','Widgets');g.node('EachWidget','foreach');g.link('Widgets','FoundWidgets','EachWidget','Array');g.link('Widgets','then','EachWidget','Exec');g.call('RemoveWidget','RemoveFromParent','/Script/UMG.Widget');g.link('EachWidget','Array Element','RemoveWidget','self');g.link('EachWidget','LoopBody','RemoveWidget','execute');g.link('EachWidget','Completed','result','execute')
assert unreal.DeliveryEditorLibrary.build_logic_graph(b,'ConfigureIsolation',json.dumps(dict(nodes=g.nodes,links=g.links,parameters=[])))
g=d.Graph();g.call('Settings','GetGameUserSettings',GS);g.exec('entry','Settings');last='Settings'
for n,fn,defaults in [('Minimum','SetOverallScalabilityLevel',{'Value':'0'}),('Scale','SetResolutionScaleValueEx',{'NewScaleValue':'55'}),('Dynamic','SetDynamicResolutionEnabled',{'bEnable':'false'}),('Uncap','SetFrameRateLimit',{'NewLimit':'0'}),('Apply','ApplyNonResolutionSettings',{})]:
 g.call(n,fn,GS,**defaults);g.link('Settings','ReturnValue',n,'self');g.exec(last,n);last=n
g.call('Isolate','ConfigureIsolation',P);g.exec(last,'Isolate');g.exec('Isolate','result');assert unreal.DeliveryEditorLibrary.build_logic_graph(b,'ApplyBenchmarkTier',json.dumps(dict(nodes=g.nodes,links=g.links,parameters=[])))
assert E.compile_blueprint(b);assert unreal.EditorAssetLibrary.save_loaded_asset(b,only_if_is_dirty=False)
unreal.EditorLoadingAndSavingUtils.load_map('/Game/QA/OptimizationBenchmark');actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in actors.get_all_level_actors():
 if a.get_class().get_name() in ['BP_OptimizationFrameProbe_C','BP_CPUIsolation_C']:actors.destroy_actor(a)
actors.spawn_actor_from_class(b.generated_class(),unreal.Vector());world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world();assert unreal.EditorLoadingAndSavingUtils.save_map(world,'/Game/QA/CPUIsolation')
# Current phone UI, real engine inputs/functions and screenshots before CPU isolation.
src=(R/'work/build_pure_phone_runtime_test.py').read_text(encoding='utf-8-sig');src=src.replace("r/('work/PurePhoneVisualQA/'+name+'.png')","r/('AdversarialQA_20261026/screens/phone_'+name+'.png')")
src=src.replace("g.call('Quit','QuitGame',K,QuitPreference='Quit',bIgnorePlatformRestrictions='true')","g.call('Quit','ExecuteConsoleCommand',K,Command='open /Game/QA/CPUIsolation')")
(R/'AdversarialQA_20261026/screens').mkdir(exist_ok=True);exec(compile(src,'AdversarialPhoneVisualQA','exec'),{'__file__':str(R/'work/build_pure_phone_runtime_test.py'),'__name__':'__main__'})
unreal.log('CPU_ISOLATION_MAP_READY')
