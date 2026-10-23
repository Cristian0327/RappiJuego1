import unreal,sys,json,shutil
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;sys.path.insert(0,str(r/'Herramientas'));import blueprint_graph as d
E=unreal.BlueprintEditorLibrary;bp=unreal.load_asset('/Game/World/BP_BogotaCity');pure=unreal.load_asset('/Game/World/BlueprintWorld/BP_WorldState');assert bp and pure;P=pure.generated_class().get_path_name();backup=r/'Recuperacion_Migracion_Blueprints/2026-10-17_weather_core_bridge/BP_BogotaCity.uasset';backup.parent.mkdir(parents=True,exist_ok=True)
if not backup.exists():shutil.copy2(r/'RappiJuego1/Content/World/BP_BogotaCity.uasset',backup)
OriginalGraph=d.Graph
class BridgeGraph(OriginalGraph):
 def build(self,name):
  outgoing=[x for x in self.links if x[0]=='entry' and x[1]=='then'];self.links=[x for x in self.links if x not in outgoing];self.get('WorldStateBridge');self.call('BridgeValid','IsValid','/Script/Engine.KismetSystemLibrary');self.link('WorldStateBridge','WorldStateBridge','BridgeValid','Object');self.branch('UsePureWorld','BridgeValid');self.exec('entry','UsePureWorld')
  for old in outgoing:self.link('UsePureWorld','else',old[2],old[3])
  fields={'NextWeatherState':['RainStartChance'],'ChooseWeatherHold':['AutomaticWeatherState','DryWeatherHold','WetWeatherHold','WeatherRandom'],'AdvanceDynamicWeather':['WeatherInitialized','WeatherRandom','AutomaticWeatherState','WeatherDecisionRemaining','PreviousWeatherOverride','DeveloperRainOverride','RainIntensity','WeatherTargetIntensity','RainStartChance','DryWeatherHold','WetWeatherHold']}.get(name,[]);existing={x['id'] for x in self.nodes};last='UsePureWorld'
  for field in fields:
   if field not in existing:self.get(field)
   n='BridgeIn'+field;self.node(n,'setfield',owner=P,var=field);self.link('WorldStateBridge','WorldStateBridge',n,'self');self.link(field,field,n,field);self.exec(last,n);last=n
  self.call('PureWeatherFunction',name,P);self.link('WorldStateBridge','WorldStateBridge','PureWeatherFunction','self')
  for param in {'NextWeatherState':['CurrentState','Roll'],'WeatherStateForIntensity':['Intensity'],'WeatherIntensityForState':['State'],'AdvanceDynamicWeather':['Dt']}.get(name,[]):self.link('entry',param,'PureWeatherFunction',param)
  if name in ['AdvanceDynamicWeather','ChooseWeatherHold']:
   self.exec(last,'PureWeatherFunction');last='PureWeatherFunction'
   output=['WeatherRandom'] if name=='ChooseWeatherHold' else ['WeatherInitialized','WeatherRandom','AutomaticWeatherState','WeatherDecisionRemaining','PreviousWeatherOverride','WeatherTargetIntensity']
   for field in output:
    n='BridgeOut'+field;self.node(n,'getfield',owner=P,var=field);self.link('WorldStateBridge','WorldStateBridge',n,'self');self.setter('Apply'+field,field,n,field);self.exec(last,'Apply'+field);last='Apply'+field
  self.node('PureResult','return');self.link('PureWeatherFunction','ReturnValue','PureResult','ReturnValue');self.exec(last,'PureResult');assert unreal.DeliveryEditorLibrary.build_logic_graph(bp,name,json.dumps({'nodes':self.nodes,'links':self.links,'variables':self.variables})),name;return {'function':name,'active_pure_blueprint':P}
d.Graph=BridgeGraph;d.bp=bp;M=d.M;root=r
try:
 g=BridgeGraph();s=(r/'work/configure_rain.py').read_text(encoding='utf-8-sig');s=s[s.index("g.get('RainStartChance')"):s.index('cdo=')];exec(compile(s,'WeatherNextCoreBridge','exec'))
 s=(r/'work/migrate_weather_parking_blueprints.py').read_text(encoding='utf-8-sig');s=s[s.index('reports=[]'):s.index("g=graph();get(g,'CurbParkingSlots')")];A='/Script/Engine.KismetArrayLibrary';exec(compile(s,'WeatherCoreBridge','exec'))
finally:d.Graph=OriginalGraph
assert E.compile_blueprint(bp);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False);(r/'work/weather_core_bridge_integration.json').write_text(json.dumps({'status':'INTEGRATED_COMPATIBILITY_SHELL_REMAINS','functions':reports},indent=2));unreal.log('WEATHER_CORE_PURE_BLUEPRINT_BRIDGE_INTEGRATED_PASS')
