import unreal,sys,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).parent
sys.path.insert(0,str(root/'Herramientas'))
import blueprint_graph as d
d.bp=unreal.load_asset('/Game/World/BP_BogotaCity');unreal.BlueprintEditorLibrary.remove_function_graph(d.bp,'RainAmountFor');g=d.Graph();M=d.M
g.get('RainStartChance')
g.call('Start','Less_DoubleDouble',M);g.link('entry','Roll','Start','A');g.link('RainStartChance','RainStartChance','Start','B')
g.call('Clear','SelectInt',M,A='1',B='0');g.link('Start','ReturnValue','Clear','bPickA')
for name,limit in [('DrizzleDown','.55'),('DrizzleHold','.80'),('RainDown','.55'),('RainHold','.80'),('StormDown','.80')]:
 g.call(name,'Less_DoubleDouble',M,B=limit);g.link('entry','Roll',name,'A')
g.call('DrizzleStayOrRise','SelectInt',M,A='1',B='2');g.link('DrizzleHold','ReturnValue','DrizzleStayOrRise','bPickA')
g.call('Drizzle','SelectInt',M,A='0');g.link('DrizzleStayOrRise','ReturnValue','Drizzle','B');g.link('DrizzleDown','ReturnValue','Drizzle','bPickA')
g.call('RainStayOrRise','SelectInt',M,A='2',B='3');g.link('RainHold','ReturnValue','RainStayOrRise','bPickA')
g.call('Rain','SelectInt',M,A='1');g.link('RainStayOrRise','ReturnValue','Rain','B');g.link('RainDown','ReturnValue','Rain','bPickA')
g.call('Storm','SelectInt',M,A='2',B='3');g.link('StormDown','ReturnValue','Storm','bPickA')
for state in range(3):
 g.call('Is'+str(state),'EqualEqual_IntInt',M,B=str(state));g.link('entry','CurrentState','Is'+str(state),'A')
g.call('WetChoice','SelectInt',M);g.link('Rain','ReturnValue','WetChoice','A');g.link('Storm','ReturnValue','WetChoice','B');g.link('Is2','ReturnValue','WetChoice','bPickA')
g.call('RainChoice','SelectInt',M);g.link('Drizzle','ReturnValue','RainChoice','A');g.link('WetChoice','ReturnValue','RainChoice','B');g.link('Is1','ReturnValue','RainChoice','bPickA')
g.call('Choice','SelectInt',M);g.link('Clear','ReturnValue','Choice','A');g.link('RainChoice','ReturnValue','Choice','B');g.link('Is0','ReturnValue','Choice','bPickA');g.link('Choice','ReturnValue','result','ReturnValue');g.exec('entry','result');g.build('NextWeatherState')
cdo=unreal.get_default_object(d.bp.generated_class());cdo.set_editor_property('RainStartChance',.30);cdo.set_editor_property('DryWeatherHold',unreal.Vector2D(120,240));cdo.set_editor_property('WetWeatherHold',unreal.Vector2D(45,75));unreal.EditorAssetLibrary.save_loaded_asset(d.bp,only_if_is_dirty=False)
cdo=unreal.get_default_object(d.bp.generated_class());rows=[]
for state in range(4):
 values=[cdo.call_method('NextWeatherState',(state,(i+.5)/1000)) for i in range(1000)];assert all(abs(v-state)<=1 and 0<=v<=3 for v in values);rows.append({str(v):values.count(v)/1000 for v in set(values)})
assert rows[0]=={'0':.70,'1':.30},rows
report={'status':'PASS','rule':'probabilistic adjacent-state transitions','samples':4000,'transition_probabilities':rows,'dry_hold_seconds':[120,240],'wet_hold_seconds':[45,75]}
(root/'work/weather_validation.json').write_text(json.dumps(report,indent=2))
unreal.log('DYNAMIC_WEATHER_BLUEPRINT_PASS')

# Check actual Blueprint scheduling over a week, with reproducible stream seeds.
cdo.set_editor_property('WeatherInitialized',True);cdo.set_editor_property('WeatherRandom',unreal.RandomStream(initial_seed=6401));cdo.set_editor_property('DeveloperRainOverride',-1);cdo.set_editor_property('PreviousWeatherOverride',-1)
counts=[0,0,0,0]
for minute in range(10080):
 cdo.call_method('AdvanceDynamicWeather',(60.0,));counts[cdo.get_editor_property('AutomaticWeatherState')]+=1
report['scheduled_minutes']=10080;report['clear_weather_fraction']=counts[0]/10080;report['minutes_by_state']=counts
assert .65<report['clear_weather_fraction']<.95,report
(root/'work/weather_validation.json').write_text(json.dumps(report,indent=2))
unreal.EditorLoadingAndSavingUtils.load_map('/Game/Maps/Bogota')
for actor in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
 if isinstance(actor,unreal.BogotaCity):
  actor.set_editor_property('RainStartChance',.30);actor.set_editor_property('DryWeatherHold',unreal.Vector2D(120,240));actor.set_editor_property('WetWeatherHold',unreal.Vector2D(45,75))
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
unreal.log('SUNNY_WEATHER_SCHEDULER_PASS')
