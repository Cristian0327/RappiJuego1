"""Five timed quality captures, or one tier with -BogotaSingle=1."""
import unreal,json,sys
from pathlib import Path
R=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(R/'Herramientas'));import blueprint_graph as d
E=unreal.BlueprintEditorLibrary;M=d.M;GS='/Script/Engine.GameUserSettings';K='/Script/Engine.KismetSystemLibrary';G='/Script/Engine.GameplayStatics';STR='/Script/Engine.KismetStringLibrary';NAV='/Script/NavigationSystem.NavigationSystemV1';RENDER='/Script/Engine.KismetRenderingLibrary';bp=unreal.load_asset('/Game/QA/BP_OptimizationFrameProbe');assert bp
for name,typ in [('Phase','int'),('PhaseAge','real'),('SingleTier','bool')]:
 if name not in [str(x) for x in E.list_member_variable_names(bp)]:assert E.add_member_variable(bp,name,E.get_basic_type_by_name(typ))
assert E.compile_blueprint(bp);P=bp.generated_class().get_path_name()
def build(g,name,override=False):
 spec=dict(nodes=g.nodes,links=g.links)
 if not override:spec['parameters']=[]
 assert unreal.DeliveryEditorLibrary.build_logic_graph(bp,name,json.dumps(spec)),name
def message(g,id,prefix,previous,source=None,pin='ReturnValue'):
 g.call(id,'PrintString',K,bPrintToScreen='false',InString=prefix)
 if source:
  g.call(id+'Number','Conv_IntToString',STR);g.link(source,pin,id+'Number','InInt');g.call(id+'Label','Concat_StrStr',STR,A=prefix);g.link(id+'Number','ReturnValue',id+'Label','B');g.link(id+'Label','ReturnValue',id,'InString')
 g.exec(previous,id);return id
g=d.Graph();g.get('Preset');g.call('Settings','GetGameUserSettings',GS);g.exec('entry','Settings');g.call('Tier','SetOverallScalabilityLevel',GS);g.link('Settings','ReturnValue','Tier','self');g.link('Preset','Preset','Tier','Value');g.exec('Settings','Tier');g.call('Times','Multiply_IntInt',M,B='15');g.link('Preset','Preset','Times','A');g.call('Plus','Add_IntInt',M,B='55');g.link('Times','ReturnValue','Plus','A');g.call('Clamp','Min',M,B='100');g.link('Plus','ReturnValue','Clamp','A');g.call('Scale','SetResolutionScaleValueEx',GS);g.link('Settings','ReturnValue','Scale','self');g.link('Clamp','ReturnValue','Scale','NewScaleValue');g.exec('Tier','Scale');g.call('Fixed','SetDynamicResolutionEnabled',GS,bEnable='false');g.link('Settings','ReturnValue','Fixed','self');g.exec('Scale','Fixed');g.call('Uncap','SetFrameRateLimit',GS,NewLimit='0');g.link('Settings','ReturnValue','Uncap','self');g.exec('Fixed','Uncap');g.call('Apply','ApplyNonResolutionSettings',GS);g.link('Settings','ReturnValue','Apply','self');g.exec('Uncap','Apply');g.exec('Apply','result');build(g,'ApplyBenchmarkTier')
g=d.Graph();g.call('Command','GetCommandLine',K);g.exec('entry','Command');last='Command'
for name,flag in [('Preset','-BogotaQuality='),('SingleTier','-BogotaSingle=')]:
 g.call(name+'Split','Split',STR,InStr=flag,SearchCase='IgnoreCase',SearchDir='FromStart');g.link('Command','ReturnValue',name+'Split','SourceString');g.call(name+'Integer','Conv_StringToInt',STR);g.link(name+'Split','RightS',name+'Integer','InString')
 if name=='Preset':g.call('Range','Clamp',M,Min='0',Max='4');g.link(name+'Integer','ReturnValue','Range','Value');g.setter('Save'+name,name,'Range')
 else:g.call('Single','Greater_IntInt',M,B='0');g.link(name+'Integer','ReturnValue','Single','A');g.setter('Save'+name,name,'Single')
 g.exec(last,'Save'+name);last='Save'+name
g.setter('ResetPhase','Phase',value='0');g.exec(last,'ResetPhase');g.setter('ResetClock','PhaseAge',value='0');g.exec('ResetPhase','ResetClock');g.call('Apply','ApplyBenchmarkTier',P);g.exec('ResetClock','Apply');g.exec('Apply','result');build(g,'ReceiveBeginPlay',True)
g=d.Graph()
for name in ['Preset','Phase','PhaseAge','SingleTier']:g.get(name)
g.call('Next','Add_DoubleDouble',M);g.link('PhaseAge','PhaseAge','Next','A');g.link('entry','DeltaSeconds','Next','B');g.setter('Clock','PhaseAge','Next');g.exec('entry','Clock');g.call('PSOs','NumPrecompilingPSOsRemaining',RENDER);g.exec('Clock','PSOs');last='PSOs';edge='then'
for phase in range(3):
 n='Phase'+str(phase);g.call(n+'Matches','EqualEqual_IntInt',M,B=str(phase));g.link('Phase','Phase',n+'Matches','A');g.branch(n,n+'Matches');g.exec(last,n,edge);g.call(n+'Time','Greater_DoubleDouble',M,B=str([15,60,5][phase]));g.link('PhaseAge','PhaseAge',n+'Time','A');due=n+'Time'
 if phase==0:
  g.call('ShadersReady','EqualEqual_IntInt',M,B='0');g.link('PSOs','ReturnValue','ShadersReady','A');g.call('NavBuilding','IsNavigationBeingBuilt',NAV);g.call('NavReady','Not_PreBool',M);g.link('NavBuilding','ReturnValue','NavReady','A');g.call('Ready','BooleanAND',M);g.link('ShadersReady','ReturnValue','Ready','A');g.link('NavReady','ReturnValue','Ready','B');g.call('Warm','BooleanAND',M);g.link('Ready','ReturnValue','Warm','A');g.link(due,'ReturnValue','Warm','B');due='Warm'
 g.branch(n+'Due',due);g.exec(n,n+'Due');g.exec(n+'Due','result','else');tail=n+'Due'
 if phase==0:
  tail=message(g,'Begin','BENCHMARK_TIER_BEGIN=',tail,'Preset','Preset');g.call('PC','GetPlayerController',G,PlayerIndex='0');g.call('Viewport','GetViewportSize','/Script/Engine.PlayerController');g.link('PC','ReturnValue','Viewport','self');tail=message(g,'Width','BENCHMARK_VIEWPORT_X=',tail,'Viewport','SizeX');tail=message(g,'Height','BENCHMARK_VIEWPORT_Y=',tail,'Viewport','SizeY');g.call('CSVStart','ExecuteConsoleCommand',K,Command='csvprofile start');g.exec(tail,'CSVStart');tail='CSVStart';next_phase=1
 elif phase==1:
  g.call('CSVStop','ExecuteConsoleCommand',K,Command='csvprofile stop');g.exec(tail,'CSVStop');tail=message(g,'End','BENCHMARK_TIER_END=','CSVStop','Preset','Preset');next_phase=2
 else:
  g.call('LastTier','GreaterEqual_IntInt',M,B='4');g.link('Preset','Preset','LastTier','A');g.call('Done','BooleanOR',M);g.link('LastTier','ReturnValue','Done','A');g.link('SingleTier','SingleTier','Done','B');g.branch('Complete','Done');g.exec(tail,'Complete');message(g,'CompleteMessage','BENCHMARK_MATRIX_COMPLETE','Complete');g.call('Quit','QuitGame',K,QuitPreference='Quit',bIgnorePlatformRestrictions='false');g.exec('CompleteMessage','Quit');g.exec('Quit','result');g.call('NextTier','Add_IntInt',M,B='1');g.link('Preset','Preset','NextTier','A');g.setter('RememberTier','Preset','NextTier');g.exec('Complete','RememberTier','else');g.call('ApplyTier','ApplyBenchmarkTier',P);g.exec('RememberTier','ApplyTier');tail='ApplyTier';next_phase=0
 g.setter(n+'Phase','Phase',value=str(next_phase));g.exec(tail,n+'Phase');g.setter(n+'ResetClock','PhaseAge',value='0');g.exec(n+'Phase',n+'ResetClock');g.exec(n+'ResetClock','result');last=n;edge='else'
g.exec(last,'result',edge);build(g,'ReceiveTick',True);assert E.compile_blueprint(bp);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
unreal.log('OPTIMIZATION_MATRIX_READY')
