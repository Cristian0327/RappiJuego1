import unreal,sys,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).parent
sys.path.insert(0,str(root/'Herramientas'))
import blueprint_graph as d
d.bp=unreal.load_asset('/Game/World/BP_BogotaCity');M=d.M;A='/Script/Engine.KismetArrayLibrary'
reports=[]
def graph():return d.Graph()
def get(g,v):
 if not any(n['id']==v for n in g.nodes):g.get(v)
 return v
def link(g,a,ap,b,bp):g.link(a,ap,b,bp)
def call(g,n,fn,**kw):return g.call(n,fn,M,**kw)
def state_select(name,input_name,input_pin,thresholds,values,fn):
 g=graph();last=None
 for i,limit in reversed(list(enumerate(thresholds))):
  c=call(g,'Compare'+str(i),'Less_DoubleDouble',B=str(limit));link(g,input_name,input_pin,c,'A')
  n=call(g,'Select'+str(i),fn,A=str(values[i]),**({'B':str(values[-1])} if last is None else {}));link(g,c,'ReturnValue',n,'bPickA')
  if last:link(g,last,'ReturnValue',n,'B')
  last=n
 link(g,last,'ReturnValue','result','ReturnValue');g.exec('entry','result');reports.append(g.build(name))
state_select('WeatherStateForIntensity','entry','Intensity',[.05,.45,.85],[0,1,2,3],'SelectInt')
state_select('WeatherIntensityForState','entry','State',[1,2,3],[0,.25,.7,1],'SelectFloat')
g=graph()
for v in ['AutomaticWeatherState','DryWeatherHold','WetWeatherHold','WeatherRandom']:get(g,v)
call(g,'Dry','EqualEqual_IntInt',B='0');link(g,'AutomaticWeatherState','AutomaticWeatherState','Dry','A');g.branch('Choose','Dry');g.exec('entry','Choose')
for name,var,execpin in [('DryHold','DryWeatherHold','then'),('WetHold','WetWeatherHold','else')]:
 call(g,name+'Range','BreakVector2D');link(g,var,var,name+'Range','InVec')
 call(g,name+'Min','FMax',B='30');link(g,name+'Range','X',name+'Min','A')
 call(g,name+'Max','FMax');link(g,name+'Min','ReturnValue',name+'Max','A');link(g,name+'Range','Y',name+'Max','B')
 call(g,name,'RandomFloatInRangeFromStream');link(g,'WeatherRandom','WeatherRandom',name,'Stream');link(g,name+'Min','ReturnValue',name,'Min');link(g,name+'Max','ReturnValue',name,'Max')
 g.node(name+'Return','return');link(g,name,'ReturnValue',name+'Return','ReturnValue');g.exec('Choose',name+'Return',execpin)
reports.append(g.build('ChooseWeatherHold'))
g=graph()
for v in ['WeatherInitialized','WeatherRandom','AutomaticWeatherState','WeatherDecisionRemaining','PreviousWeatherOverride','DeveloperRainOverride','RainIntensity','WeatherTargetIntensity']:get(g,v)
g.branch('Init','WeatherInitialized','WeatherInitialized');g.exec('entry','Init')
call(g,'Seed','RandomIntegerInRange',Min='0',Max='2147483646');call(g,'Stream','MakeRandomStream');link(g,'Seed','ReturnValue','Stream','InitialSeed')
g.setter('SetStream','WeatherRandom','Stream');g.exec('Init','SetStream','else');g.setter('SetInitialized','WeatherInitialized',value='true');g.exec('SetStream','SetInitialized');g.setter('SetClear','AutomaticWeatherState',value='0');g.exec('SetInitialized','SetClear')
g.call('InitialHold','ChooseWeatherHold');g.exec('SetClear','InitialHold');g.setter('SetInitialHold','WeatherDecisionRemaining','InitialHold');g.exec('InitialHold','SetInitialHold');g.setter('SetInitialOverride','PreviousWeatherOverride','DeveloperRainOverride','DeveloperRainOverride');g.exec('SetInitialHold','SetInitialOverride')
call(g,'Automatic','Less_IntInt',B='0');link(g,'DeveloperRainOverride','DeveloperRainOverride','Automatic','A');call(g,'WasManual','GreaterEqual_IntInt',B='0');link(g,'PreviousWeatherOverride','PreviousWeatherOverride','WasManual','A');call(g,'Resuming','BooleanAND');link(g,'Automatic','ReturnValue','Resuming','A');link(g,'WasManual','ReturnValue','Resuming','B');g.branch('Resume','Resuming');g.exec('Init','Resume','then');g.exec('SetInitialOverride','Resume')
g.call('VisibleState','WeatherStateForIntensity');link(g,'RainIntensity','RainIntensity','VisibleState','Intensity');g.setter('SetVisibleState','AutomaticWeatherState','VisibleState');g.exec('Resume','SetVisibleState','then');g.call('ResumeHold','ChooseWeatherHold');g.exec('SetVisibleState','ResumeHold');g.setter('SetResumeHold','WeatherDecisionRemaining','ResumeHold');g.exec('ResumeHold','SetResumeHold')
g.setter('SaveOverride','PreviousWeatherOverride','DeveloperRainOverride','DeveloperRainOverride');g.exec('Resume','SaveOverride','else');g.exec('SetResumeHold','SaveOverride');g.branch('Advance','Automatic');g.exec('SaveOverride','Advance')
call(g,'PositiveDt','FMax',B='0');link(g,'entry','Dt','PositiveDt','A');call(g,'SubtractTime','Subtract_DoubleDouble');link(g,'WeatherDecisionRemaining','WeatherDecisionRemaining','SubtractTime','A');link(g,'PositiveDt','ReturnValue','SubtractTime','B');g.setter('SetTime','WeatherDecisionRemaining','SubtractTime');g.exec('Advance','SetTime','then')
call(g,'Expired','LessEqual_DoubleDouble',B='0');link(g,'WeatherDecisionRemaining','WeatherDecisionRemaining','Expired','A');g.branch('Decide','Expired');g.exec('SetTime','Decide')
call(g,'Roll','RandomFloatFromStream');link(g,'WeatherRandom','WeatherRandom','Roll','Stream');g.call('Next','NextWeatherState');link(g,'AutomaticWeatherState','AutomaticWeatherState','Next','CurrentState');link(g,'Roll','ReturnValue','Next','Roll');g.setter('SetNext','AutomaticWeatherState','Next');g.exec('Decide','SetNext','then');g.call('NextHold','ChooseWeatherHold');g.exec('SetNext','NextHold');call(g,'AddHold','Add_DoubleDouble');link(g,'WeatherDecisionRemaining','WeatherDecisionRemaining','AddHold','A');link(g,'NextHold','ReturnValue','AddHold','B');g.setter('SetNextHold','WeatherDecisionRemaining','AddHold');g.exec('NextHold','SetNextHold');g.exec('SetNextHold','Decide')
g.call('Intensity','WeatherIntensityForState');link(g,'AutomaticWeatherState','AutomaticWeatherState','Intensity','State');g.setter('SetTarget','WeatherTargetIntensity','Intensity');g.exec('Decide','SetTarget','else');g.exec('Advance','SetTarget','else');call(g,'ManualDrizzle','EqualEqual_IntInt',B='2');link(g,'DeveloperRainOverride','DeveloperRainOverride','ManualDrizzle','A');call(g,'ManualRain','EqualEqual_IntInt',B='1');link(g,'DeveloperRainOverride','DeveloperRainOverride','ManualRain','A');call(g,'RainOrOther','SelectInt',A='2');link(g,'DeveloperRainOverride','DeveloperRainOverride','RainOrOther','B');link(g,'ManualRain','ReturnValue','RainOrOther','bPickA');call(g,'ManualState','SelectInt',A='1');link(g,'RainOrOther','ReturnValue','ManualState','B');link(g,'ManualDrizzle','ReturnValue','ManualState','bPickA');g.call('ManualIntensity','WeatherIntensityForState');link(g,'ManualState','ReturnValue','ManualIntensity','State');call(g,'EffectiveTarget','SelectFloat');link(g,'WeatherTargetIntensity','WeatherTargetIntensity','EffectiveTarget','A');link(g,'ManualIntensity','ReturnValue','EffectiveTarget','B');link(g,'Automatic','ReturnValue','EffectiveTarget','bPickA');link(g,'EffectiveTarget','ReturnValue','result','ReturnValue');g.exec('SetTarget','result');reports.append(g.build('AdvanceDynamicWeather'))
g=graph();get(g,'CurbParkingSlots');get(g,'ParkingRandom');call(g,'Stream','MakeRandomStream');link(g,'entry','Seed','Stream','InitialSeed');g.setter('SetStream','ParkingRandom','Stream');g.exec('entry','SetStream');g.call('Clear','Array_Clear',A);link(g,'CurbParkingSlots','CurbParkingSlots','Clear','TargetArray');g.exec('SetStream','Clear');g.call('Count','Array_Length',A);link(g,'CurbParkingSlots','CurbParkingSlots','Count','TargetArray');call(g,'NeedsSlots','Less_IntInt',B='4');link(g,'Count','ReturnValue','NeedsSlots','A');g.branch('Loop','NeedsSlots');g.exec('Clear','Loop');call(g,'Pick','RandomIntegerInRangeFromStream',Min='0',Max='11');link(g,'ParkingRandom','ParkingRandom','Pick','Stream');g.call('Add','Array_AddUnique',A);link(g,'CurbParkingSlots','CurbParkingSlots','Add','TargetArray');link(g,'Pick','ReturnValue','Add','NewItem');g.exec('Loop','Add','then');g.exec('Add','Loop');g.exec('Loop','result','else');reports.append(g.build('InitializeParkingPlan'))
g=graph();get(g,'CurbParkingSlots');get(g,'ParkingRandom');g.call('Curb','Array_Contains',A);link(g,'CurbParkingSlots','CurbParkingSlots','Curb','TargetArray');link(g,'entry','Slot','Curb','ItemToFind');g.branch('Kind','Curb');g.exec('entry','Kind')
# Cache random values in BP variables so each stream draw happens once.
g.variables=[{'name':'ParkingLateralOffset','default':'0'},{'name':'ParkingHeadingJitter','default':'0'}]
g.setter('CurbOffset','ParkingLateralOffset',value='780');g.exec('Kind','CurbOffset','then');call(g,'StreetOffset','RandomFloatInRangeFromStream',Min='590',Max='615');link(g,'ParkingRandom','ParkingRandom','StreetOffset','Stream');g.setter('StreetOffsetSet','ParkingLateralOffset','StreetOffset');g.exec('Kind','StreetOffsetSet','else');call(g,'Jitter','RandomFloatInRangeFromStream',Min='-2.5',Max='2.5');link(g,'ParkingRandom','ParkingRandom','Jitter','Stream');g.setter('SetJitter','ParkingHeadingJitter','Jitter');g.exec('CurbOffset','SetJitter');g.exec('StreetOffsetSet','SetJitter')
call(g,'RightSide','Greater_DoubleDouble',B='0');link(g,'entry','Side','RightSide','A');call(g,'BaseHeading','SelectFloat',A='-90',B='90');link(g,'RightSide','ReturnValue','BaseHeading','bPickA');get(g,'ParkingHeadingJitter');get(g,'ParkingLateralOffset');call(g,'Heading','Add_DoubleDouble');link(g,'BaseHeading','ReturnValue','Heading','A');link(g,'ParkingHeadingJitter','ParkingHeadingJitter','Heading','B');call(g,'CurbFlag','SelectFloat',A='1',B='0');link(g,'Curb','ReturnValue','CurbFlag','bPickA');call(g,'Pose','MakeVector');link(g,'ParkingLateralOffset','ParkingLateralOffset','Pose','X');link(g,'Heading','ReturnValue','Pose','Y');link(g,'CurbFlag','ReturnValue','Pose','Z');link(g,'Pose','ReturnValue','result','ReturnValue');g.exec('SetJitter','result');reports.append(g.build('ParkingPoseFor'))
unreal.EditorAssetLibrary.save_loaded_asset(d.bp,only_if_is_dirty=False)
audit=json.loads(unreal.DeliveryEditorLibrary.audit_blueprint(d.bp));assert audit['compiled'];names={g['name']:g for g in audit['graphs']}
for name in ['AdvanceDynamicWeather','ChooseWeatherHold','WeatherStateForIntensity','WeatherIntensityForState','InitializeParkingPlan','ParkingPoseFor']:
 assert names[name]['bytecode']>0,name
(root/'work/blueprint_weather_parking_graphs.json').write_text(json.dumps({'status':'PASS','graphs':[names[r['function']] for r in reports]},indent=2),encoding='utf-8')
cdo=unreal.get_default_object(d.bp.generated_class())
for seed in range(100):
 cdo.call_method('InitializeParkingPlan',(seed,))
 slots=list(cdo.get_editor_property('CurbParkingSlots'));assert len(slots)==len(set(slots))==4 and all(0<=v<12 for v in slots),(seed,slots)
 poses=[cdo.call_method('ParkingPoseFor',(i,1.0)) for i in range(12)]
 assert sum(p.z>.5 for p in poses)==4
 assert all((p.x==780 if p.z>.5 else 590<=p.x<=615) and -92.5<=p.y<=-87.5 for p in poses)
 cdo.call_method('InitializeParkingPlan',(seed,))
 again=[cdo.call_method('ParkingPoseFor',(i,1.0)) for i in range(12)]
 assert poses==again,seed
(root/'work/blueprint_parking_validation.json').write_text(json.dumps({'status':'PASS','seeds':100,'poses':1200,'unique_curb_slots':4,'reproducible':True},indent=2))
unreal.log('BLUEPRINT_WEATHER_PARKING_PASS')
