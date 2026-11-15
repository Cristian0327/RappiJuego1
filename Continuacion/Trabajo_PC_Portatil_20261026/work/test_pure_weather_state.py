import unreal,json
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;bp=unreal.load_asset('/Game/World/BlueprintWorld/BP_WorldState');assert bp;c=unreal.get_default_object(bp.generated_class());checks=[]
def check(n,v):checks.append({'name':n,'passed':bool(v)});assert v,n
for state in range(4):
 counts={}
 for i in range(1000):
  v=c.call_method('NextWeatherState',(state,(i+.5)/1000));assert 0<=v<=3 and abs(v-state)<=1,(state,v);counts[v]=counts.get(v,0)+1
 check('adjacent_weather_transitions_'+str(state),sum(counts.values())==1000)
c.set_editor_property('WeatherInitialized',True);c.set_editor_property('WeatherRandom',unreal.RandomStream(initial_seed=6401));c.set_editor_property('AutomaticWeatherState',0);c.set_editor_property('WeatherDecisionRemaining',1);c.set_editor_property('DeveloperRainOverride',-1);c.set_editor_property('PreviousWeatherOverride',-1);states=[0,0,0,0]
for minute in range(10080):
 c.call_method('AdvanceDynamicWeather',(60.0,));states[c.get_editor_property('AutomaticWeatherState')]+=1
check('sunny_days_predominate',.65<states[0]/10080<.95);check('all_weather_severities_reached',all(x>0 for x in states))
for mode,expected in [(0,0),(1,.7),(2,.25),(3,1)]:
 c.set_editor_property('DeveloperRainOverride',mode);actual=c.call_method('AdvanceDynamicWeather',(0.0,));check('developer_mode_'+str(mode),abs(actual-expected)<.001)
c.set_editor_property('RainIntensity',0);c.set_editor_property('HailIntensity',0);c.set_editor_property('DeveloperRainOverride',3)
for i in range(24):c.call_method('ReceiveTick',(1.0,))
check('smooth_storm_intensity',abs(c.get_editor_property('RainIntensity')-1)<.001);check('hail_in_storm',abs(c.get_editor_property('HailIntensity')-1)<.001)
for i in range(40):c.call_method('ReceiveTick',(1.0,))
check('lightning_events_generated',c.get_editor_property('LightningEvents')>0);check('delayed_thunder_events_generated',c.get_editor_property('ThunderEvents')>0)
c.set_editor_property('DeveloperRainOverride',1)
for i in range(3):c.call_method('ReceiveTick',(1.0,))
check('hail_stops_outside_storm',c.get_editor_property('HailIntensity')<.001 and c.get_editor_property('LightningFlash')<.001 and c.get_editor_property('ThunderDelay')<0)
c.set_editor_property('DeveloperRainOverride',0)
for i in range(24):c.call_method('ReceiveTick',(1.0,))
check('storm_clears_gradually',c.get_editor_property('RainIntensity')<.001 and c.get_editor_property('HailIntensity')<.001)
(r/'work/pure_weather_state_validation.json').write_text(json.dumps({'status':'PASS','minutes_by_state':states,'sunny_fraction':states[0]/10080,'checks':checks},indent=2));unreal.log('PURE_WEATHER_STATE_VM_PASS checks='+str(len(checks)))
